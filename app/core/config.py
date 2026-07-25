"""应用配置模块。

把配置集中放在这里，后续各模块就不需要到处硬编码数据库地址、Redis 地址、
存储路径、限制参数或 API 前缀。项目虽然还小，但企业服务要想让环境切换可控，
配置集中管理是基础。
"""

import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class AppSettings(BaseModel):
    """从环境变量加载的运行时配置。"""

    app_name: str = Field(default="Enterprise Knowledge Hub Backend")
    app_env: str = Field(default="local")
    debug: bool = Field(default=False)
    api_v1_prefix: str = Field(default="/api/v1")
    log_level: str = Field(default="INFO")

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/enterprise_knowledge_hub"
    )
    redis_url: str = Field(default="redis://localhost:6379/0")
    storage_root: Path = Field(default=Path("storage_data"))

    max_upload_size_mb: int = Field(default=20, ge=1)
    allowed_file_types: tuple[str, ...] = Field(default=("txt", "md", "pdf"))

    @field_validator("api_v1_prefix")
    @classmethod
    def normalize_api_prefix(cls, value: str) -> str:
        """统一 API 前缀格式，避免是否带前导斜杠导致行为不一致。"""

        value = value.strip()
        if not value:
            return "/api/v1"
        return value if value.startswith("/") else f"/{value}"

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return value.strip().upper() or "INFO"

    @field_validator("allowed_file_types", mode="before")
    @classmethod
    def parse_allowed_file_types(cls, value: object) -> tuple[str, ...]:
        """支持本地通过 ``ALLOWED_FILE_TYPES=txt,md,pdf`` 这样的形式传值。"""

        if isinstance(value, str):
            return tuple(item.strip().lower().lstrip(".") for item in value.split(",") if item.strip())
        if isinstance(value, list | tuple | set):
            return tuple(str(item).strip().lower().lstrip(".") for item in value if str(item).strip())
        return ("txt", "md", "pdf")

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @classmethod
    def from_env(cls) -> "AppSettings":
        """使用明确的环境变量名称构造配置对象。"""

        return cls(
            app_name=os.getenv("APP_NAME", "Enterprise Knowledge Hub Backend"),
            app_env=os.getenv("APP_ENV", "local"),
            debug=os.getenv("DEBUG", "false").lower() in {"1", "true", "yes", "on"},
            api_v1_prefix=os.getenv("API_V1_PREFIX", "/api/v1"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            database_url=os.getenv(
                "DATABASE_URL",
                "postgresql+psycopg://postgres:postgres@localhost:5432/enterprise_knowledge_hub",
            ),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            storage_root=Path(os.getenv("STORAGE_ROOT", "storage_data")),
            max_upload_size_mb=int(os.getenv("MAX_UPLOAD_SIZE_MB", "20")),
            allowed_file_types=os.getenv("ALLOWED_FILE_TYPES", "txt,md,pdf"),
        )


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """返回带缓存的应用配置。

    这样可以避免每次请求都重新解析环境变量，同时测试里仍然可以在覆盖配置后主动清理缓存。
    """

    return AppSettings.from_env()
