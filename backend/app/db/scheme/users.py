from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, timezone
from typing import Annotated


class UserBase(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: Annotated[str, Field(max_length=72)]

class UserLogin(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(max_length=72)]


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    password: str | None = None

# DB내부관리
class UserInDB(UserBase):
    user_id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # sqlalchemy 객체를 pydantic모델로 변환할 때 사용
    class Config:
        from_attributes = True


class UserRead(UserInDB):
    pass