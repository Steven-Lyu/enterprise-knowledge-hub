"""ORM 模型聚合入口。

Alembic、测试建表和脚本初始化只需要导入这个包，就能把全部业务模型注册到
同一个 ``Base.metadata``。新增模型时必须同步加入这里，否则模型代码虽然存在，
迁移工具却无法发现对应表。
"""

from app.models.base import BaseModel, IdMixin, TimestampMixin, utc_now
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.document_event import DocumentEvent
from app.models.processing_task import ProcessingTask

__all__ = [
    "BaseModel",
    "Document",
    "DocumentChunk",
    "DocumentEvent",
    "IdMixin",
    "ProcessingTask",
    "TimestampMixin",
    "utc_now",
]
