"""SQLAlchemy Base 聚合入口。

这个文件有两个职责：

1. 定义全项目唯一的 ``Base``，所有 ORM 模型都必须继承它。
2. 提供模型集中导入入口，后续 Alembic 生成迁移脚本时可以从这里拿到完整
   ``Base.metadata``。

企业项目里不要让不同模块各自声明 Declarative Base。否则看起来都能建模型，
但 Alembic、表关系和测试初始化很容易因为拿到的不是同一个 metadata 而失效。
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """所有 SQLAlchemy ORM 模型的统一声明基类。"""


def import_all_models() -> None:
    """集中导入所有 ORM 模型，让 ``Base.metadata`` 能注册完整表结构。

    第 2 轮还没有真正的业务模型，所以这里只导入 ``app.models`` 包入口。
    第 3 轮生成 ``Document``、``DocumentChunk``、``ProcessingTask``、
    ``DocumentEvent`` 后，会在 ``app.models.__init__`` 中继续聚合它们。

    这个函数看起来暂时“不做事”，但它为 Alembic 和测试建表保留了稳定入口。
    """

    import app.models  # noqa: F401


__all__ = ["Base", "import_all_models"]
