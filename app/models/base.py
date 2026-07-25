"""ORM 通用基础模型。

这个模块只放所有业务模型都会复用的基础字段和工具函数。
真正的业务字段，例如文档标题、任务状态、chunk 内容，会在第 3 轮各自的模型文件中定义。
"""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utc_now() -> datetime:
    """返回带 UTC 时区信息的当前时间。

    企业系统里的时间字段要尽量避免使用本地时区时间。后续接口响应再统一转成
    ISO 8601 字符串，可以减少跨环境部署、日志排查和任务超时判断时的歧义。
    """

    return datetime.now(UTC)


class IdMixin:
    """通用字符串主键字段。

    第一版使用 UUID 字符串，便于 API、日志和事件表直接透传。
    后续如果企业内部有统一 ID 服务，也可以只替换这里的生成策略。
    """

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        comment="主键 ID",
    )


class TimestampMixin:
    """通用创建时间和更新时间字段。"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
        comment="更新时间",
    )


class BaseModel(Base, IdMixin, TimestampMixin):
    """业务 ORM 模型的共同父类。

    这里只提供公共字段，不自动生成 ``__tablename__``。
    后续每个业务模型都应该显式声明表名，例如 ``documents``、``processing_tasks``。
    这样表名不会被隐式规则影响，也更符合企业项目里迁移脚本需要稳定命名的要求。
    """

    __abstract__ = True


__all__ = ["BaseModel", "IdMixin", "TimestampMixin", "utc_now"]
