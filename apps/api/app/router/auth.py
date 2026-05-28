from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
async def signup():
    return {"message": "TODO: implement signup"}


@router.post("/signin")
async def signin():
    return {"message": "TODO: implement signin"}


@router.get("/me")
async def me():
    return {"message": "TODO: implement get current user"}
