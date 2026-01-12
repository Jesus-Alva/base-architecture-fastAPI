import secrets
import logging
from typing import Any, Dict, List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, EmailStr, HttpUrl, PostgresDsn, validator, ConfigDict

logging.basicConfig(level=logging.INFO)

PROJECT_NAME = ''#SWAGER-NAME

class AsyncPostgresDsn(PostgresDsn):
    allowed_schemes = {"postgres+asyncpg", "postgresql+asyncpg"}

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    # GAFSACOMM IP
    API_DOMAIN_SSO: str = "http://:8002" ##ADD-YOUR-IP
    API_DOMAIN: str = "http://:8000"#ADD-YOUR-IP
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # ! CREAR NUEVA EXPIRACIÓN PARA QUE SEA CORTA
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8
    JOB_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1
    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl = ""#ADD-YOUR-IP
    BACKEND_CORS_ORIGINS: List[Union[AnyHttpUrl, str]] = []
    TEST_MODE: bool = False
    PROFILE_QUERY_MODE: bool = False
    ARBITRARY_TYPES_ALLOWED: bool = True
    CODE_SYSTEM: str = "32182a9a-2873-405d-b8b8-719b2d8bfd51"
    
    @validator("BACKEND_CORS_ORIGINS", pre=False)
    def assemble_cors_origins(cls, v: Union[str, List[Union[AnyHttpUrl, str]]]) -> List[Union[AnyHttpUrl, str]]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = PROJECT_NAME
    SENTRY_DSN: Optional[HttpUrl] = None

    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
        if len(v) == 0:
            return None
        return v

    POSTGRES_SERVER: str 
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    SQLALCHEMY_DATABASE_URI_ASYNC: Optional[str] = None

    @validator("POSTGRES_DB", pre=True)
    def assemble_db_name(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if values.get("TEST_MODE"):
            return "postgres"
        if isinstance(v, str):
            return v
        return v

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        port = values.get("POSTGRES_PORT", "5435")
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}:{port}/{values.get('POSTGRES_DB')}"

    @validator("SQLALCHEMY_DATABASE_URI_ASYNC", pre=True)
    def assemble_async_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        port = values.get("POSTGRES_PORT", "5435")
        return f"postgresql+asyncpg://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}:{port}/{values.get('POSTGRES_DB')}"

    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values.get("PROJECT_NAME", "rcd")
        return v

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 8
    EMAIL_TEMPLATES_DIR: str = "app/email-templates/build"
    EMAILS_ENABLED: bool = True

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool, values: Dict[str, Any]) -> bool:
        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )

    EMAIL_TEST_USER: EmailStr = "no-reply@gafsacomm.com"  # type: ignore
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_NICKNAME: str
    FIRST_SUPERUSER_PASSWORD: str
    USERS_OPEN_REGISTRATION: bool = True

    # Configuración para Pydantic v2
    model_config = ConfigDict(
        case_sensitive=True,
        arbitrary_types_allowed=True
    )

settings = Settings()