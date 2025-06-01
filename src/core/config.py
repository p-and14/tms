from pathlib import Path
import sys
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).absolute().parent.parent.parent
sys.path.append(str(BASE_DIR))

class EnvDict(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


class PgSettings(EnvDict):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_URL_asyncpg(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL_psycopg(self):
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class RedisSettings(EnvDict):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USER: str
    REDIS_PASS: str
    REDIS_DB: int

    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_USER}:{self.REDIS_PASS}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


class Settings(PgSettings, RedisSettings):
    pass


settings = Settings() #type: ignore
