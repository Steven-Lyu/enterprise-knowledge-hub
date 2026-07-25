"""健康检查接口。

第 1 轮只暴露最小可用的存活检查。
数据库、Redis 和存储系统检查，等后续基础设施模块补齐后再接入。
"""

from datetime import UTC, datetime

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check() -> dict[str, str]:
    """返回最小健康信号，用于确认 API 进程仍然存活。"""

    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
        "timestamp": datetime.now(UTC).isoformat(),
    }
