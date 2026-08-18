"""文档分段实体，为解析结果和后续 RAG 检索提供稳定边界。"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, CheckConstraint, ForeignKey, Index, Integer, String, Text
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.document import Document


class DocumentChunk(BaseModel):
    """从某个文档版本中解析得到的有序文本分段。"""

    __tablename__ = "document_chunks"
    __table_args__ = (
        CheckConstraint(
            "chunk_index >= 0", name="ck_document_chunks_index_non_negative"
        ),
        CheckConstraint(
            "page_number IS NULL OR page_number >= 1",
            name="ck_document_chunks_page_positive",
        ),
        CheckConstraint(
            "char_count >= 0", name="ck_document_chunks_char_count_non_negative"
        ),
        Index(
            "uq_document_chunks_document_id_chunk_index",
            "document_id",
            "chunk_index",
            unique=True,
        ),
    )

    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),  # 如果数据库中的某个 document 被删除，数据库自动删除所有 document_id 指向它的 chunk
        nullable=False,
        comment="所属文档 ID",
    )
    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="分段在文档内的顺序，从 0 开始",
    )
    page_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="原文页码；非分页文件可为空",
    )
    section_title: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        comment="分段所属章节标题",
    )
    heading_path: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(JSON),
        default=list,
        nullable=False,
        comment="从顶层到当前章节的标题路径",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="分段正文",
    )
    char_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="分段字符数",
    )
    chunk_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",  # 这里由于 ORM 的 Base 已有 metadata 属性，因此使用 chunk_metadata 以防混淆，数据库中列名仍是 metadata
        MutableDict.as_mutable(JSON),
        default=dict,
        nullable=False,
        comment="解析器、来源定位等可扩展元数据",
    )

    document: Mapped[Document] = relationship(back_populates="chunks")


__all__ = ["DocumentChunk"]
