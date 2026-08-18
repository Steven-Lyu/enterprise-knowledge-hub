"""文档主实体。

``Document`` 保存一份已上传文件的业务身份、存储定位、版本信息和处理状态。
文件正文不直接放在这张表中：原文件由存储层管理，可检索文本由
``DocumentChunk`` 管理，这样文档列表查询不会反复读取大文本字段。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    Enum,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import DocumentStatus, Visibility
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.document_chunk import DocumentChunk
    from app.models.document_event import DocumentEvent
    from app.models.processing_task import ProcessingTask


class Document(BaseModel):
    """企业知识库中的文档及其单个版本。"""

    __tablename__ = "documents"
    __table_args__ = (
        UniqueConstraint(
            "file_hash",
            "department",
            "category",
            name="uq_documents_file_hash_business_scope",
        ),
        CheckConstraint("file_size >= 0", name="ck_documents_file_size_non_negative"),
        CheckConstraint("version >= 1", name="ck_documents_version_positive"),
        Index(
            "ix_documents_status_department_category_created_at",
            "status",   # 写在前面的最先筛选，这里优先按状态筛选
            "department",
            "category",
            "created_at",
        ),
        Index(
            "ix_documents_version_group_id_version",
            "version_group_id",
            "version",
        ),
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="文档标题",
    )
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="上传时的原始文件名",
    )
    file_type: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        comment="文件类型，例如 txt、md、pdf",
    )
    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="文件字节数",
    )
    file_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="文件内容 SHA-256，用于重复上传判断",
    )
    version_group_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        comment="同一逻辑文档各版本共享的版本组 ID",
    )
    storage_path: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
        comment="原文件在存储服务中的定位路径",
    )
    department: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        comment="文档所属部门",
    )
    category: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        comment="文档业务分类",
    )
    # 这里不能用普通 JSON，因为普通 JSON 内部的 append / pop / 字典键赋值
    # 不会触发 ORM 属性赋值事件。
    tags: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(JSON),
        default=list,
        nullable=False,
        comment="文档标签列表",
    )
    visibility: Mapped[Visibility] = mapped_column(
        Enum(
            Visibility,
            name="visibility",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            values_callable=lambda enum_type: [item.value for item in enum_type],
        ),
        default=Visibility.INTERNAL,
        nullable=False,
        comment="文档可见范围",
    )
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="文档版本号，从 1 开始递增",
    )
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(
            DocumentStatus,
            name="document_status",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            values_callable=lambda enum_type: [item.value for item in enum_type],
        ),
        default=DocumentStatus.UPLOADED,
        nullable=False,
        comment="文档处理状态",
    )
    created_by: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        comment="上传人的上游用户 ID",
    )
    # relationship 让对象之间可以互相访问。all 会传播保存、合并、删除和
    # Session 移除等操作；delete-orphan 表示 chunk 从所属 document 中移除且
    # 没有其他父对象接管时，该 chunk 会被删除。
    chunks: Mapped[list[DocumentChunk]] = relationship(
        back_populates="document",  # document 和 chunk 的双向关系
        cascade="all, delete-orphan",
        passive_deletes=True,  # 将一部分删除工作交给外键级联机制，而不必先查询所有 chunk
    )
    processing_tasks: Mapped[list[ProcessingTask]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    events: Mapped[list[DocumentEvent]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


__all__ = ["Document"]
