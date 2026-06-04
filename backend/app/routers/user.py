from fastapi import APIRouter, Depends, Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.core.auth import get_current_username
from app.db.scheme.users import UserRead, UserCreate, UserUpdate
from app.db.database import get_db
from app.services import UserService


router = APIRouter(prefix="/users", tags=["User"])

@router.post("/token")
async def login(f_data:OAuth2PasswordRequestForm=Depends(), db:AsyncSession=Depends(get_db)):
    result = await UserService.login(db, f_data)
    return result

@router.post("", response_model=UserRead)
async def signup(user:UserCreate, db:AsyncSession=Depends(get_db)):
    db_user = await UserService.signup(db, user)
    return db_user

@router.get("/me", response_model=UserRead)
async def get_me(db:AsyncSession=Depends(get_db), username:str=Depends(get_current_username)):
    return await UserService.get_user_by_username(db, username)

@router.get("")
async def get_user_all(db:AsyncSession=Depends(get_db), username:str=Depends(get_current_username)):
    return await UserService.get_user_all(db)

@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id:Annotated[int, Path(...)], db:AsyncSession=Depends(get_db), username:str=Depends(get_current_username)):
    return await UserService.get_user(db, user_id)

@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id:Annotated[int, Path(...)], user_data:UserUpdate, db:AsyncSession=Depends(get_db), username:str=Depends(get_current_username)):
    return await UserService.update_user(db, user_id, user_data)

@router.delete("/{user_id}", response_model=UserRead)
async def delete_user(user_id:Annotated[int, Path(...)], db:AsyncSession=Depends(get_db), username:str=Depends(get_current_username)):
    return await UserService.delete_user(db, user_id)