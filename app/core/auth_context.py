"""从上游请求头中提取身份上下文。

本项目第一阶段不自建登录系统。
在企业环境里，身份通常来自内部网关、SSO 或服务网格；本地开发时用请求头模拟这条边界。
"""

from dataclasses import dataclass
from uuid import uuid4  # 随机生成一个通用唯一标识符，常用于 request_id task_id

from fastapi import Header

from app.core.exceptions import UnauthorizedError


@dataclass(frozen=True, slots=True)
class AuthContext:
    """供 service 层和审计日志使用的结构化身份信息。"""

    user_id: str
    user_name: str
    request_id: str
    user_department: str | None = None


async def get_auth_context(
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    x_user_name: str | None = Header(default=None, alias="X-User-Name"),
    x_user_department: str | None = Header(default=None, alias="X-User-Department"),
    x_request_id: str | None = Header(default=None, alias="X-Request-Id"),
) -> AuthContext:
    """构造业务接口使用的身份对象。

    健康检查接口不会依赖这个函数。
    后续业务 API 应统一通过它获取结构化身份信息，而不是在 route 里直接读取原始请求头。
    """

    if not x_user_id or not x_user_name:
        raise UnauthorizedError(
            message="missing required identity headers: X-User-Id and X-User-Name",
            details={
                "required_headers": ["X-User-Id", "X-User-Name"],
                "optional_headers": ["X-User-Department", "X-Request-Id"],
            },
        )

    return AuthContext(
        user_id=x_user_id,
        user_name=x_user_name,
        user_department=x_user_department,
        request_id=x_request_id or f"req_{uuid4().hex}",
    )
