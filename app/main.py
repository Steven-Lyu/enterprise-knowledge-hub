"""FastAPI 应用入口。"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    unhandled_exception_handler,
)
from app.core.logging import get_logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """应用生命周期钩子。

    第 1 轮只记录启动和关闭日志。
    后续等数据库、Redis、存储模块具备后，再把就绪检查挂到这里。
    """

    logger = get_logger(__name__)
    logger.info("application startup")
    yield
    logger.info("application shutdown")


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用。"""

    settings = get_settings()
    setup_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.include_router(api_router, prefix=settings.api_v1_prefix)
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    return app


app = create_app()
