import os
import uuid

from fastapi import UploadFile

from app.settings import Settings


async def save_upload_file(
    file: UploadFile, user_id: uuid.UUID, settings: Settings
) -> tuple[str, int]:
    """Save uploaded file to local storage.

    Returns (relative_storage_path, size_bytes).
    """
    user_dir = os.path.join(settings.FILE_STORAGE_PATH, str(user_id))
    os.makedirs(user_dir, exist_ok=True)

    file_id = uuid.uuid4()
    safe_name = file.filename or "upload"
    storage_name = f"{file_id}_{safe_name}"
    storage_path = os.path.join(str(user_id), storage_name)
    full_path = os.path.join(settings.FILE_STORAGE_PATH, storage_path)

    size = 0
    with open(full_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            f.write(chunk)

    return storage_path, size


def delete_file_storage(storage_path: str, settings: Settings) -> None:
    """Remove file from local storage."""
    full_path = os.path.join(settings.FILE_STORAGE_PATH, storage_path)
    if os.path.exists(full_path):
        os.remove(full_path)


def get_full_path(storage_path: str, settings: Settings) -> str:
    """Get absolute path for a stored file."""
    return os.path.join(settings.FILE_STORAGE_PATH, storage_path)
