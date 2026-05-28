from fastapi import APIRouter

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/")
async def list_files():
    return {"message": "TODO: list files"}


@router.post("/")
async def upload_file():
    return {"message": "TODO: upload file"}
