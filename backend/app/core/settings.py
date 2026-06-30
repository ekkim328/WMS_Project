from pydantic_settings import BaseSettings
from pydantic import Field
from datetime import timedelta
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

# BaseSettings 환경변수 기반 설정 관리 클래스(DB, API키, 환경관련설정)
# alias로 환경변수값이 있는지 확인 -> 해당 값으로 필드 채움
class Settings(BaseSettings):
    db_user:str=Field(..., alias="DB_USER")
    db_password:str=Field(..., alias="DB_PASSWORD")
    db_host:str=Field(..., alias="DB_HOST")
    db_port:str=Field(..., alias="DB_PORT")
    db_name:str=Field(..., alias="DB_NAME")

    secret_key:str=Field(..., alias="SECRET_KEY")
    jwt_algorithm:str=Field(..., alias="JWT_ALGORITHM")
    access_token_expire_seconds:int=Field(900, alias="ACCESS_TOKEN_EXPIRE")
    refresh_token_expire_seconds:int=Field(604800, alias="REFRESH_TOKEN_EXPIRE")

    class Config:
        env_file=ENV_FILE
        case_sensitive=True # 환경변수 이름 대소문자를 구분
        extra="allow"   # 모델에 정의되지 않은 추가 필드도 허용
        populate_by_name=True   # 필드 이름과 alias로 값을 채울 수 있음

    # 동적 프로퍼티
    # @property 데코레이터를 사용하면 메서드를 프로퍼티(속성)처럼 접근할 수 있다.
    # ex) settings.db_url
    @property
    def tmp_db(self) -> str:    #"root:1234@localhost:3306/fastapi"
        return f"{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property   # 비동기 DB URL
    def db_url(self) -> str:
        return f"mysql+asyncmy://{self.tmp_db}"
    
    @property   # 동기 DB URL
    def sync_db_url(self) -> str:
        return f"mysql+pymysql://{self.tmp_db}"
    
    @property
    def access_token_expire(self) -> timedelta:
        return timedelta(seconds=self.access_token_expire_seconds)
    # 초단위 -> timedelta 객체로 변환

    @property
    def refresh_token_expire(self) -> timedelta:
        return timedelta(seconds=self.refresh_token_expire_seconds)
    
settings=Settings()
