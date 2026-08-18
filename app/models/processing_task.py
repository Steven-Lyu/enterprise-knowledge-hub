"""文档处理任务实体。

任务表是 Web 进程与后续独立 worker 之间的持久化协作边界。即使 Redis
不可用或进程重启，任务状态、重试次数和心跳仍以这张表为事实来源。
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ParseStep, TaskStatus, TaskType
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.document_event import DocumentEvent


class ProcessingTask(BaseModel):
    """一次可独立追踪、重试和回收的文档处理任务。"""

    __tablename__ = "processing_tasks"
    __table_args__ = (
        CheckConstraint(
            "progress >= 0 AND progress <= 100",
            name="ck_processing_tasks_progress_range",
        ),
        CheckConstraint(
            "retry_count >= 0",
            name="ck_processing_tasks_retry_count_non_negative",
        ),
        CheckConstraint(
            "max_retries >= 0",
            name="ck_processing_tasks_max_retries_non_negative",
        ),
        CheckConstraint(
            "retry_count <= max_retries",
            name="ck_processing_tasks_retry_count_within_limit",
        ),
        Index(
            "ix_processing_tasks_document_id_status_created_at",
            "document_id",
            "status",
            "created_at",
        ),
        Index(
            "ix_processing_tasks_status_heartbeat_at",
            "status",
            "heartbeat_at",  # Worker 心跳
        ),
        # 条件唯一索引只限制 pending/running，不会阻止同一文档保留历史任务 (success/failed)。
        Index(
            "uq_processing_tasks_one_active_per_document",
            "document_id",
            unique=True,
            postgresql_where=text("status IN ('pending', 'running')"),
            sqlite_where=text("status IN ('pending', 'running')"),
        ),
    )

    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        comment="待处理文档 ID",
    )
    task_type: Mapped[TaskType] = mapped_column(
        Enum(
            TaskType,
            name="task_type",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            values_callable=lambda enum_type: [item.value for item in enum_type],
        ),
        default=TaskType.PARSE_DOCUMENT,
        nullable=False,
        comment="任务类型",
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(
            TaskStatus,
            name="task_status",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            values_callable=lambda enum_type: [item.value for item in enum_type],
        ),
        default=TaskStatus.PENDING,
        nullable=False,
        comment="任务状态",
    )
    progress: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="任务完成百分比，范围 0-100",
    )
    current_step: Mapped[ParseStep | None] = mapped_column(
        Enum(
            ParseStep,
            name="parse_step",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            values_callable=lambda enum_type: [item.value for item in enum_type],
        ),
        nullable=True,
        comment="当前解析步骤；任务尚未开始时可为空",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="最近一次失败原因",
    )
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="已消耗的重试次数",
    )
    max_retries: Mapped[int] = mapped_column(
        Integer,
        default=2,
        nullable=False,
        comment="最大重试次数，第一版固定为 2",
    )
    worker_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="当前持有任务的 worker 标识",
    )
    heartbeat_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),  # 带时区的时间
        nullable=True,
        comment="worker 最近一次心跳时间",
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="任务首次开始时间",
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="任务最终完成或失败时间",
    )

    document: Mapped[Document] = relationship(back_populates="processing_tasks")
    events: Mapped[list[DocumentEvent]] = relationship(
        back_populates="task",
        passive_deletes=True,
    )


__all__ = ["ProcessingTask"]
