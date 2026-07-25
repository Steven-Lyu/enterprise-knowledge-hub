"""应用日志配置。"""

from __future__ import annotations

import logging
from logging.config import dictConfig


def setup_logging(log_level: str = "INFO") -> None:
    """为 API 和 worker 进程配置统一日志格式。

    后续轮次可以继续补 request_id、task_id、document_id、user_id 等字段。
    第 1 轮先保证所有进程至少使用同一套基础格式和日志级别。
    """

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "root": {
                "handlers": ["console"],
                "level": log_level,
            },
        }
    )


def get_logger(name: str) -> logging.Logger:
    """通过统一入口返回模块级 logger。"""

    return logging.getLogger(name)
