"""文档上传、查询和 chunk 输出相关的 API Schema。"""

from typing import Annotated, Any, Literal

from pydantic import AliasChoices, Field, StringConstraints, field_validator

from app.core.enums import DocumentStatus, Visibility
from app.schemas.common import PageResponse, SchemaModel, UtcDateTime

ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
TagText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=64),
]
SupportedFileType = Literal["txt", "md", "pdf"]


class DocumentUploadRequest(SchemaModel):
    """上传文档时随 multipart 表单提交的业务元数据。

    文件流（文件的具体内容）由 route 通过 FastAPI ``UploadFile`` 单独接收。把文件对象放进 Pydantic
    模型会混淆“元数据校验”和“文件资源生命周期”两种职责。
    """

    title: ShortText = Field(max_length=255)
    department: ShortText = Field(max_length=128)
    category: ShortText = Field(max_length=128)
    tags: list[TagText] = Field(default_factory=list, max_length=20)
    visibility: Visibility = Visibility.INTERNAL

    @field_validator("tags")
    @classmethod
    def validate_unique_tags(cls, tags: list[str]) -> list[str]:
        """拒绝忽略大小写后的重复标签，避免过滤条件出现重复语义。"""

        normalized_tags = [tag.casefold() for tag in tags]
        if len(normalized_tags) != len(set(normalized_tags)):
            raise ValueError("tags 不能包含重复值")
        return tags


class DocumentListQuery(SchemaModel):
    """文档列表接口冻结的分页、过滤和关键词参数。"""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=50)
    status: DocumentStatus | None = None
    department: str | None = Field(default=None, min_length=1, max_length=128)
    category: str | None = Field(default=None, min_length=1, max_length=128)
    keyword: str | None = Field(default=None, min_length=1, max_length=200)


class DocumentListItem(SchemaModel):
    """文档列表中的轻量条目，不暴露存储路径和文件哈希。"""

    id: str
    title: str
    filename: str
    file_type: SupportedFileType
    file_size: int = Field(ge=0)
    department: str
    category: str
    tags: list[str]
    visibility: Visibility
    version: int = Field(ge=1)
    status: DocumentStatus
    created_by: str
    created_at: UtcDateTime
    updated_at: UtcDateTime


class DocumentDetailResponse(DocumentListItem):
    """文档详情响应。

    ``storage_path`` 属于存储实现细节，不进入 API；哈希和版本组 ID 可帮助知识库
    维护人员判断重复上传和版本归属，因此只在详情响应中提供。
    """

    file_hash: str = Field(min_length=64, max_length=64)
    version_group_id: str = Field(min_length=36, max_length=36)


class DocumentUploadResponse(SchemaModel):
    """上传文档并创建解析任务后的响应。"""

    document_id: str
    task_id: str
    status: Literal[DocumentStatus.QUEUED]
    message: str


class DocumentChunkQuery(SchemaModel):
    """文档 chunk 查询参数。"""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=100)


class DocumentChunkResponse(SchemaModel):
    """单个文档分段的 API 表达。"""

    id: str
    document_id: str
    chunk_index: int = Field(ge=0)
    page_number: int | None = Field(default=None, ge=1)
    section_title: str | None = None
    heading_path: list[str]
    content: str
    char_count: int = Field(ge=0)
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("chunk_metadata", "metadata"),  # 控制输入时可使用的别名
        serialization_alias="metadata",  # API 输出时使用的名字
    )
    created_at: UtcDateTime


DocumentListResponse = PageResponse[DocumentListItem]
DocumentChunkListResponse = PageResponse[DocumentChunkResponse]


__all__ = [
    "DocumentChunkListResponse",
    "DocumentChunkQuery",
    "DocumentChunkResponse",
    "DocumentDetailResponse",
    "DocumentListItem",
    "DocumentListQuery",
    "DocumentListResponse",
    "DocumentUploadRequest",
    "DocumentUploadResponse",
]
