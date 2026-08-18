"""文档处理事件流水实体，用于时间线查询、审计和故障排查。"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Enum, ForeignKey, Index, String, Text
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import DocumentEventType
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.processing_task import ProcessingTask


class DocumentEvent(BaseModel):
    """文档处理链路中的一条不可变业务事件。"""

    __tablename__ = "document_events"
    __table_args__ = (
        Index("ix_document_events_task_id_created_at", "task_id", "created_at"),
    )

    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        comment="事件所属文档 ID",
    )
    task_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("processing_tasks.id", ondelete="SET NULL"),  # 当 task 被删除时，不删除 event，而是把 task_id 设为 NULL
        nullable=True,
        comment="关联任务 ID；归档等非任务事件可为空",
    )
    event_type: Mapped[DocumentEventType] = mapped_column(
        Enum(
            DocumentEventType,
            name="document_event_type",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            values_callable=lambda enum_type: [item.value for item in enum_type],
        ),
        nullable=False,
        comment="事件类型",
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="面向排障和时间线展示的事件描述",
    )
    request_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="触发事件的请求链路 ID",
    )
    event_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        MutableDict.as_mutable(JSON),
        default=dict,
        nullable=False,
        comment="重试原因、进度等可扩展事件上下文",
    )

    document: Mapped[Document] = relationship(back_populates="events")
    task: Mapped[ProcessingTask | None] = relationship(back_populates="events")


__all__ = ["DocumentEvent"]
