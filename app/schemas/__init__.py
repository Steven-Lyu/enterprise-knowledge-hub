"""Pydantic Schema 聚合入口。

API、service 和测试可以从这里导入稳定的请求响应类型；具体定义仍按业务域拆分，
避免所有 Schema 堆进一个文件后互相耦合。
"""

from app.schemas.common import (
    ErrorResponse,
    PageResponse,
    SchemaModel,
    SuccessResponse,
    UtcDateTime,
)
from app.schemas.document import (
    DocumentChunkListResponse,
    DocumentChunkQuery,
    DocumentChunkResponse,
    DocumentDetailResponse,
    DocumentListItem,
    DocumentListQuery,
    DocumentListResponse,
    DocumentUploadRequest,
    DocumentUploadResponse,
)
from app.schemas.task import (
    TaskDetailResponse,
    TaskEventListQuery,
    TaskEventListResponse,
    TaskEventResponse,
    TaskSseData,
    TaskSseEvent,
    TaskStatusResponse,
)

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
    "ErrorResponse",
    "PageResponse",
    "SchemaModel",
    "SuccessResponse",
    "TaskDetailResponse",
    "TaskEventListQuery",
    "TaskEventListResponse",
    "TaskEventResponse",
    "TaskSseData",
    "TaskSseEvent",
    "TaskStatusResponse",
    "UtcDateTime",
]
