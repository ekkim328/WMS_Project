from fastapi import APIRouter, Depends, Path, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.core.auth import get_current_user
from app.db.models import User
from app.db.scheme.users import UserRead, UserCreate, UserUpdate
from app.db.database import get_db
from app.services import UserService


router = APIRouter(prefix="/users", tags=["User"])

@router.post("/token")
async def login(
    f_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    return await UserService.login(db, f_data)


@router.post("", response_model=UserRead)
async def signup(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    return await UserService.signup(db, user)


@router.get("/me", response_model=UserRead)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="본인 계정만 수정할 수 있습니다")

    return await UserService.update_user(db, user_id, user_data)

@router.delete("/{user_id}", response_model=UserRead)
async def delete_user(
    user_id: Annotated[int, Path(...)],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="본인 계정만 삭제할 수 있습니다")

    return await UserService.delete_user(db, user_id)