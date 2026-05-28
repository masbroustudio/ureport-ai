from fastapi import APIRouter

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/")
async def list_conversations():
    return {"message": "TODO: list conversations"}


@router.post("/")
async def create_conversation():
    return {"message": "TODO: create conversation"}
