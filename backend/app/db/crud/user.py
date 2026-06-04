from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import User
from app.db.scheme.users import UserCreate, UserUpdate


# User 테이블과 관련된 CRUD작업을 모아둔 클래스
# scalar_one_or_none : 결과 1개면 객체반환, 없으면 none반환
class UserCrud:
    @staticmethod
    async def get_by_id(db:AsyncSession, user_id:int) -> User|None:
        result = await db.execute(select(User).filter(User.user_id==user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db:AsyncSession) -> list[User]:
        result = await db.execute(select(User))
        return result.scalars().all()

    @staticmethod
    async def create(db:AsyncSession, user:UserCreate) -> User:
        db_user=User(**user.model_dump())
        db.add(db_user)
        await db.flush()
        return db_user
    
    @staticmethod
    async def update_by_id(db:AsyncSession, user_id:int, user:UserUpdate) -> User|None:
        db_user = await db.get(User, user_id)
        if db_user:
            update_data = user.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_user, key, value)
            await db.flush()
            return db_user
        return None
    
    @staticmethod
    async def delete_by_id(db: AsyncSession, user_id: int) -> User | None:
        db_user = await db.get(User, user_id)
        if db_user:
            await db.delete(db_user)
            await db.flush()
            return db_user
        return None

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> User | None:
        result = await db.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()
    
    
    @staticmethod
    async def update_refresh_token_by_id(
        db:AsyncSession, user_id:int, refresh_token:str):

        db_user = await db.get(User, user_id)
        if db_user:
            db_user.refresh_token = refresh_token
            await db.flush()
        return db_user