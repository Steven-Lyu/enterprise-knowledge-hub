"""任务详情、事件时间线和 SSE 数据载体相关的 API Schema。"""

from typing import Any

from pydantic import AliasChoices, Field, model_validator

from app.core.enums import (
    DocumentEventType,
    ParseStep,
    SseEventType,
    TaskStatus,
    TaskType,
)
from app.schemas.common import PageResponse, SchemaModel, UtcDateTime


class TaskDetailResponse(SchemaModel):
    """任务查询接口返回的完整持久化状态。"""

    id: str
    document_id: str
    task_type: TaskType
    status: TaskStatus
    progress: int = Field(ge=0, le=100)
    current_step: ParseStep | None = None
    error_message: str | None = None
    retry_count: int = Field(ge=0)
    max_retries: int = Field(ge=0)
    worker_id: str | None = None
    heartbeat_at: UtcDateTime | None = None
    started_at: UtcDateTime | None = None
    finished_at: UtcDateTime | None = None
    created_at: UtcDateTime
    updated_at: UtcDateTime


class TaskStatusResponse(SchemaModel):
    """缓存和实时反馈可以复用的轻量任务状态快照。"""

    task_id: str
    status: TaskStatus
    progress: int = Field(ge=0, le=100)
    current_step: ParseStep | None = None
    message: str | None = None
    request_id: str | None = Field(default=None, max_length=64)
    timestamp: UtcDateTime


class TaskEventListQuery(SchemaModel):
    """任务事件时间线的分页参数，排序固定为创建时间升序。"""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class TaskEventResponse(SchemaModel):
    """任务时间线中的单条事件。"""

    id: str
    document_id: str
    task_id: str | None = None
    event_type: DocumentEventType
    message: str
    request_id: str | None = None
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("event_metadata", "metadata"),
        serialization_alias="metadata",
    )
    created_at: UtcDateTime


class TaskSseData(TaskStatusResponse):
    """SSE ``data`` 字段的冻结结构。"""


class TaskSseEvent(SchemaModel):
    """应用内部用于组装一条 SSE 消息的结构化载体。

    真正传输时，``event`` 写入 SSE 的 event 行，``data`` 序列化后写入 data 行。
    """

    event: SseEventType
    data: TaskSseData

    @model_validator(mode="after")
    def validate_event_status_consistency(self) -> "TaskSseEvent":
        """拒绝事件类型与任务快照互相矛盾的 SSE 消息。"""

        if self.event is SseEventType.SUCCESS:
            if self.data.status is not TaskStatus.SUCCESS or self.data.progress != 100:
                raise ValueError("success 事件要求 status=success 且 progress=100")
        elif (
            self.event is SseEventType.FAILED
            and self.data.status is not TaskStatus.FAILED
        ):
            raise ValueError("failed 事件要求 status=failed")
        return self


TaskEventListResponse = PageResponse[TaskEventResponse]


__all__ = [
    "TaskDetailResponse",
    "TaskEventListQuery",
    "TaskEventListResponse",
    "TaskEventResponse",
    "TaskSseData",
    "TaskSseEvent",
    "TaskStatusResponse",
]
