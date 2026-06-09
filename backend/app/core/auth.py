from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.jwt_handle import oauth_scheme, verify_token
from app.db.database import get_db
from app.db.crud.user import UserCrud

# app/core/auth.py

async def get_current_user(
    token: str = Depends(oauth_scheme),
    db: AsyncSession = Depends(get_db)
):
    username = verify_token(token)
    user = await UserCrud.get_by_username(db, username)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user

async def get_current_username(
        current_user = Depends(get_current_user)
):
    return current_user.username