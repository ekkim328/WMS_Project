from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.db.models import User
from app.db.scheme.users import UserCreate, UserUpdate
from app.db.crud import UserCrud
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.core.jwt_handle import (
    create_access_token,
    get_password_hash, 
    verify_password
)

# crud는 UserCrud에서 처리하고, 비즈니스 규칙(유효성검사, 비밀번호해시, 예외처리 등)을 추가
class UserService:

    @staticmethod
    async def get_user(db:AsyncSession, user_id:int) -> User:
        db_user = await UserCrud.get_by_id(db, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="사용자 찾을 수 없다")
        return db_user
    
    @staticmethod
    async def get_user_by_username(db:AsyncSession, username:str) -> User:
        db_user = await UserCrud.get_by_username(db, username)
        if not db_user:
            raise HTTPException(status_code=404, detail="사용자 찾을 수 없다")
        return db_user

    @staticmethod
    async def signup(db:AsyncSession, user:UserCreate):
        if await UserCrud.get_by_username(db, user.username):
            raise HTTPException(status_code=400, detail="이미 사용중인 사용자 이름이다")
        
        hash_pw=get_password_hash(user.password) #비번 암호화해서 들어감
        user_create=UserCreate(username=user.username, name=user.name, password=hash_pw)

        try:
            db_user=await UserCrud.create(db,user_create)
            await db.commit()
            await db.refresh(db_user)
            return db_user
        
        except IntegrityError as exc:
            await db.rollback()
            raise HTTPException(
                status_code=400,
                detail="이미 사용중인 사용자 이름이다",
            ) from exc

    @staticmethod
    async def login(db:AsyncSession, f_data:OAuth2PasswordRequestForm):
        username = f_data.username
        password = f_data.password

        db_user = await UserCrud.get_by_username(db, username)
        if not db_user or not verify_password(password, db_user.password):
            raise HTTPException(status_code=401, detail="사용자 이름 또는 비밀번호 틀렸다")
        
        access_token = create_access_token(db_user.username)
        
        return {"access_token":access_token, "token_type":"bearer"}
    
    @staticmethod
    async def get_user_all(db:AsyncSession) -> list[User]:
        return await UserCrud.get_all(db)

    @staticmethod
    async def update_user(db:AsyncSession, user_id:int, new_user:UserUpdate) -> User:
        if new_user.password:
            hash_pw=get_password_hash(new_user.password)
            new_user.password = hash_pw

        db_user=await UserCrud.update_by_id(db, user_id, new_user)

        if not db_user:
            raise HTTPException(status_code=404, detail="사용자 찾을 수 없다")
        
        await db.commit()
        await db.refresh(db_user)
        
        return db_user


    @staticmethod
    async def delete_user(db:AsyncSession, user_id:int):
        db_user = await UserCrud.delete_by_id(db, user_id)

        if not db_user:
            raise HTTPException(status_code=404, detail="사용자 찾을 수 없다")
        
        await db.commit()

        return db_user
