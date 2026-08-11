from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_auth.database import get_session
from fastapi_auth.core.responses import APIErrorResponse, APIResponse
from fastapi_auth.services.user import UserService
from fastapi_auth.schemas.user import UserRegisterRequest
from fastapi_auth.exceptions import UserAlreadyExistsError

router = APIRouter(
    prefix="/auth",
    tags=["Users"],
)


@router.post("/register")
async def register(
    payload: UserRegisterRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = UserService(session)

    try:
        user = await service.register(
            email=payload.email,
            password=payload.password,
            username=payload.username,
            first_name=payload.first_name,
            last_name=payload.last_name,
            avatar_url=payload.avatar_url,
        )

    except UserAlreadyExistsError as exc:
        return APIErrorResponse(
            message=str(exc),
            code="USER_ALREADY_EXISTS",
            status_code=409,
        )

    return APIResponse(
        data={
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "avatar_url": user.avatar_url,
            "status": user.status.value,
            "is_verified": user.is_verified,
        },
        message="Registration successful. Please verify your email.",
        status_code=201,
    )
