from datetime import timedelta
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from pydantic import Field
from pydantic_settings import BaseSettings


ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    database_url: str | None = Field(None, alias="DATABASE_URL")

    db_user: str | None = Field(None, alias="DB_USER")
    db_password: str | None = Field(None, alias="DB_PASSWORD")
    db_host: str | None = Field(None, alias="DB_HOST")
    db_port: str | None = Field(None, alias="DB_PORT")
    db_name: str | None = Field(None, alias="DB_NAME")

    secret_key: str = Field(..., alias="SECRET_KEY")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
    access_token_expire_seconds: int = Field(0, alias="ACCESS_TOKEN_EXPIRE")
    refresh_token_expire_seconds: int = Field(604800, alias="REFRESH_TOKEN_EXPIRE")

    class Config:
        env_file = ENV_FILE
        case_sensitive = True
        extra = "allow"
        populate_by_name = True

    @property
    def tmp_db(self) -> str:
        required = {
            "DB_USER": self.db_user,
            "DB_PASSWORD": self.db_password,
            "DB_HOST": self.db_host,
            "DB_PORT": self.db_port,
            "DB_NAME": self.db_name,
        }
        missing = [key for key, value in required.items() if value is None]
        if missing:
            raise ValueError(
                "DATABASE_URL or all legacy DB_* settings are required. "
                f"Missing: {', '.join(missing)}"
            )

        return (
            f"{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def raw_database_url(self) -> str:
        return self.database_url or f"mysql://{self.tmp_db}"

    @staticmethod
    def _with_driver(url: str, async_driver: bool) -> str:
        parsed = urlsplit(url)
        scheme = parsed.scheme

        if scheme == "postgres":
            scheme = "postgresql"

        if "+" not in scheme:
            if scheme == "postgresql":
                scheme = "postgresql+asyncpg" if async_driver else "postgresql+psycopg2"
            elif scheme == "mysql":
                scheme = "mysql+asyncmy" if async_driver else "mysql+pymysql"

        return urlunsplit((scheme, parsed.netloc, parsed.path, parsed.query, parsed.fragment))

    @property
    def db_url(self) -> str:
        return self._with_driver(self.raw_database_url, async_driver=True)

    @property
    def sync_db_url(self) -> str:
        return self._with_driver(self.raw_database_url, async_driver=False)

    @property
    def access_token_expire(self) -> timedelta | None:
        if self.access_token_expire_seconds <= 0:
            return None
        return timedelta(seconds=self.access_token_expire_seconds)

    @property
    def refresh_token_expire(self) -> timedelta:
        return timedelta(seconds=self.refresh_token_expire_seconds)


settings = Settings()
