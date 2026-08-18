"""数据库连接、Session 工厂和依赖入口。

本项目第一版使用同步 SQLAlchemy Session。原因是当前重点是理解数据库事实来源、
事务边界、Repository 层和 worker 轮询链路；同步 Session 更容易把这些工程边界讲清楚。
后续如果需要切换到异步驱动，只需要集中改这个模块和对应 repository 调用方式。
"""

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def _build_engine_kwargs(database_url: str) -> dict[str, Any]:
    """根据数据库类型生成 engine 参数。

    PostgreSQL 是第一版主目标，所以默认启用 ``pool_pre_ping``，让连接池在取出连接前先做可用性检查，降低数据库重启或空闲连接断开后第一次请求直接失败的概率。

    SQLite 只作为本地开发兜底。它需要 ``check_same_thread=False`` 才能在 FastAPI
    测试或多线程场景下复用连接，否则容易出现线程归属错误。
    """

    kwargs: dict[str, Any] = {"pool_pre_ping": True}
    if database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return kwargs


settings = get_settings()

engine: Engine = create_engine(
    settings.database_url,
    **_build_engine_kwargs(settings.database_url),
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db_session() -> Generator[Session, None, None]:
    """FastAPI 依赖注入使用的数据库 Session。

    route 层后续只需要声明依赖，不应该自己创建连接或手动管理连接池。
    每个请求拿到一个独立 Session，请求结束后统一关闭，这样事务边界、连接释放和测试替换都会更可控。
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_session() -> Session:
    """给 worker、脚本或测试使用的显式 Session 创建函数。

    worker 不走 FastAPI 依赖注入，但也必须使用同一个 Session 工厂。
    这样 Web 进程和 worker 进程不会各自维护一套数据库连接逻辑。
    """

    return SessionLocal()


def dispose_engine() -> None:
    """释放数据库连接池资源，主要用于测试进程或应用关闭时清理。"""

    engine.dispose()


__all__ = ["SessionLocal", "create_session", "dispose_engine", "engine", "get_db_session"]
