from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime, timezone
from typing import Annotated


class UserBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    username: Annotated[str, Field(min_length=1, max_length=40)]
    name: Annotated[str, Field(min_length=1, max_length=100)]

class UserCreate(UserBase):
    password: Annotated[str, Field(min_length=4, max_length=72)]

    @field_validator("password")
    @classmethod
    def validate_password_byte_length(cls, password: str) -> str:
        if len(password.encode("utf-8")) > 72:
            raise ValueError("비밀번호는 UTF-8 기준 72바이트 이하여야 합니다")
        return password


class UserLogin(BaseModel):
    username: str
    password: Annotated[str, Field(max_length=72)]


class UserUpdate(BaseModel):
    username: Annotated[str, Field(min_length=1, max_length=40)] | None = None
    name: Annotated[str, Field(min_length=1, max_length=100)] | None = None
    password: Annotated[str, Field(min_length=4, max_length=72)] | None = None


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
