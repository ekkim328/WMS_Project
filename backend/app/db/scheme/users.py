from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, timezone
from typing import Annotated


class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: Annotated[str, Field(max_length=72)]


class UserLogin(BaseModel):
    username: str
    password: Annotated[str, Field(max_length=72)]


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    password: Annotated[str, Field(max_length=72)] | None = None


class UserInDB(UserBase):
    user_id: int
    password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        from_attributes = True


class UserRead(UserBase):
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True