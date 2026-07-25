"""项目状态和接口契约共用的枚举定义。"""

from enum import StrEnum


class DocumentStatus(StrEnum):
    UPLOADED = "uploaded"
    QUEUED = "queued"
    PROCESSING = "processing"
    PARSED = "parsed"
    FAILED = "failed"
    ARCHIVED = "archived"


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ParseStep(StrEnum):
    SAVE_FILE = "save_file"
    EXTRACT_TEXT = "extract_text"
    CLEAN_TEXT = "clean_text"
    SPLIT_CHUNKS = "split_chunks"
    PERSIST_CHUNKS = "persist_chunks"
    COMPLETE = "complete"


class Visibility(StrEnum):
    INTERNAL = "internal"
    DEPARTMENT = "department"
    PRIVATE = "private"


class TaskType(StrEnum):
    PARSE_DOCUMENT = "parse_document"


class DocumentEventType(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    RETRYING = "retrying"
    SUCCESS = "success"
    FAILED = "failed"
    ARCHIVED = "archived"


class SseEventType(StrEnum):
    CONNECTED = "connected"
    PROGRESS = "progress"
    SUCCESS = "success"
    FAILED = "failed"
    HEARTBEAT = "heartbeat"
