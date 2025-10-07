from fastapi import APIRouter

from src.api.v1.schemas.common import MessageResponseSchema

router = APIRouter(prefix="/profile", tags=["Profile Management"])


@router.get("/", summary="Get user's profile details")
async def get_profile_details(): ...


@router.patch("/", summary="Update user's profile details")
async def update_profile_details(): ...


@router.post("/avatar", summary="Set user's profile avatar")
async def set_profile_avatar() -> MessageResponseSchema: ...


@router.delete("/avatar", summary="Delete user's profile avatar")
async def delete_profile_avatar() -> MessageResponseSchema: ...
