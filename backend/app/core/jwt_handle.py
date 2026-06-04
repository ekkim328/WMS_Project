from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta, timezone
from app.core.settings import settings
import uuid


# 해싱방식과 정책관리 (bcrypt 알고리즘 사용)
pwd_crypt = CryptContext(schemes=["bcrypt"])

oauth_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

def get_password_hash(password:str):
    trunc_password = password.encode('utf-8')[:72]
    return pwd_crypt.hash(trunc_password)

# 평문 비번과 해시값 비교해서 같으면 true
def verify_password(plain_pw:str, hashed_pw:str) -> bool:
    trunc_password = plain_pw.encode('utf-8')[:72]
    return pwd_crypt.verify(trunc_password, hashed_pw)

def create_token(username:str, expires_delta:timedelta, **kwargs) -> str:
    to_encode=kwargs.copy() #추가정보를 페이로드에 넣고 싶을 때 
    expire=datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp":expire, "username":username})
    encoded_jwt=jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def create_access_token(username:str)->str:
    return create_token(username=username, expires_delta=settings.access_token_expire)


def decode_token(token:str) -> dict:
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.jwt_algorithm]
    )


def verify_token(token:str)->str:
    payload = decode_token(token)
    return payload.get("username")