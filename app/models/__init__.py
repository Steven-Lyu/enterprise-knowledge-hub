"""ORM 模型聚合入口。

第 2 轮只提供通用模型基类，还没有真正的业务表。
第 3 轮生成文档、chunk、任务和事件模型后，会在这里集中导入并导出。

保持这个入口的意义是：Alembic、测试建表、脚本初始化都只需要依赖一个稳定位置，
而不是到处猜测“哪些模型文件需要被 import 一遍”。
"""

from app.models.base import BaseModel, IdMixin, TimestampMixin, utc_now

__all__ = ["BaseModel", "IdMixin", "TimestampMixin", "utc_now"]
