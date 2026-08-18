"""API Schema 共用基础设施与统一响应结构。

Schema 是 HTTP 契约，不是数据库表的复制品。这里统一处理严格字段校验、ORM
属性读取、UTC 时间和分页外壳，让后续 route 不需要重复声明相同规则。
"""

from datetime import UTC, datetime
from typing import Annotated, Any

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator


def _ensure_utc(value: datetime) -> datetime:
    """拒绝无时区时间，并把有时区时间统一转换为 UTC。"""

    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("时间字段必须包含时区信息")
    return value.astimezone(UTC)


UtcDateTime = Annotated[datetime, AfterValidator(_ensure_utc)]


class SchemaModel(BaseModel):
    """项目 API Schema 的共同父类。

    ``from_attributes`` 允许响应模型直接读取 ORM 对象属性；``extra=forbid``
    则让请求中的未知字段尽早失败，避免客户端拼错字段却被服务端静默忽略。
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        populate_by_name=True,
        serialize_by_alias=True,
        str_strip_whitespace=True,
    )


class SuccessResponse[ResponseDataT](SchemaModel):
    """需要统一成功外壳时使用的泛型响应。

    已冻结为其他结构的接口不应强行套用本模型。例如文档列表必须直接返回
    ``items/page/page_size/total``，上传接口也使用自己的明确响应结构。
    """

    data: ResponseDataT
    message: str = "success"
    request_id: str | None = None


class ErrorResponse(SchemaModel):
    """所有非 2xx 业务响应遵守的统一结构。"""

    code: str = Field(min_length=1, max_length=64)
    message: str = Field(min_length=1, max_length=1000)
    request_id: str | None = Field(default=None, max_length=64)
    details: dict[str, Any] = Field(default_factory=dict)


class PageResponse[PageItemT](SchemaModel):
    """列表接口统一使用的分页响应。"""

    items: list[PageItemT]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_page_size(self) -> "PageResponse[PageItemT]":
        """防止 repository 返回数量超过当前页容量却仍生成成功响应。"""

        if len(self.items) > self.page_size:
            raise ValueError("items 数量不能超过 page_size")
        return self


__all__ = [
    "ErrorResponse",
    "PageResponse",
    "SchemaModel",
    "SuccessResponse",
    "UtcDateTime",
]
