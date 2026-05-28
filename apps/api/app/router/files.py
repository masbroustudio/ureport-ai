import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.profiler import auto_profile
from app.deps import get_current_user, get_db
from app.model.file import File
from app.model.user import User
from app.schema.file import FilePreviewResponse, FileResponse
from app.service.files import delete_file_storage, get_full_path, save_upload_file
from app.settings import settings

router = APIRouter(prefix="/files", tags=["files"])

ALLOWED_MIMES = {
    "text/csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
}


@router.post("/", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile,
    conversation_id: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Validate mime type
    mime = file.content_type or ""
    if mime not in ALLOWED_MIMES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {mime}. Allowed: CSV, XLSX, XLS.",
        )

    # Save file to storage
    storage_path, size_bytes = await save_upload_file(file, current_user.id, settings)

    # Check size limit
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        delete_file_storage(storage_path, settings)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB} MB.",
        )

    # Run auto-profile
    full_path = get_full_path(storage_path, settings)
    try:
        profile = auto_profile(full_path, mime)
    except Exception:
        profile = None

    # Create DB record
    conv_id = uuid.UUID(conversation_id) if conversation_id else None
    file_record = File(
        user_id=current_user.id,
        conversation_id=conv_id,
        name=file.filename or "upload",
        mime=mime,
        size_bytes=size_bytes,
        storage_path=storage_path,
        kind="data",
        profile_json=profile,
        status="ready",
    )
    db.add(file_record)
    await db.commit()
    await db.refresh(file_record)

    return FileResponse.model_validate(file_record)


@router.get("/", response_model=list[FileResponse])
async def list_files(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(File)
        .where(File.user_id == current_user.id)
        .order_by(File.created_at.desc())
    )
    files = result.scalars().all()
    return [FileResponse.model_validate(f) for f in files]


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(File).where(
            File.id == file_id,
            File.user_id == current_user.id,
        )
    )
    file_record = result.scalar_one_or_none()
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    return FileResponse.model_validate(file_record)


@router.get("/{file_id}/preview", response_model=FilePreviewResponse)
async def get_file_preview(
    file_id: uuid.UUID,
    rows: int = Query(20, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(File).where(
            File.id == file_id,
            File.user_id == current_user.id,
        )
    )
    file_record = result.scalar_one_or_none()
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    profile = file_record.profile_json
    if not profile or "head_preview" not in profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File profile not available",
        )

    head_preview = profile["head_preview"][:rows]
    columns = [col["name"] for col in profile.get("columns", [])]

    return FilePreviewResponse(
        columns=columns,
        rows=head_preview,
        total_rows=profile.get("n_rows", 0),
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(File).where(
            File.id == file_id,
            File.user_id == current_user.id,
        )
    )
    file_record = result.scalar_one_or_none()
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    # Delete from storage
    delete_file_storage(file_record.storage_path, settings)

    # Delete DB record
    await db.delete(file_record)
    await db.commit()
