"""
错误码定义模块
"""

from enum import IntEnum
from typing import Dict


class ErrorCode(IntEnum):
    """错误码枚举"""
    SUCCESS = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500


# 错误码描述
ERROR_MESSAGES: Dict[int, str] = {
    200: "success",
    400: "Invalid request parameter",
    401: "Unauthorized - Invalid or expired token",
    403: "Forbidden - Insufficient permissions",
    404: "Not found - Resource does not exist",
    500: "Internal server error - Please try again later"
}


# 错误响应格式
def error_response(code: int, message: str = None, details: dict = None) -> dict:
    """
    生成错误响应
    
    Args:
        code: 错误码
        message: 错误消息（可选，使用默认消息）
        details: 详细错误信息（可选）
    
    Returns:
        错误响应字典
    """
    return {
        "code": code,
        "message": message or ERROR_MESSAGES.get(code, "Unknown error"),
        "details": details or {},
        "success": False
    }


# 快捷错误响应函数
def bad_request(message: str = "Invalid request parameter", details: dict = None) -> dict:
    """400 错误"""
    return error_response(400, message, details)


def unauthorized(message: str = "Unauthorized", details: dict = None) -> dict:
    """401 错误"""
    return error_response(401, message, details)


def forbidden(message: str = "Forbidden", details: dict = None) -> dict:
    """403 错误"""
    return error_response(403, message, details)


def not_found(message: str = "Not found", details: dict = None) -> dict:
    """404 错误"""
    return error_response(404, message, details)


def internal_error(message: str = "Internal server error", details: dict = None) -> dict:
    """500 错误"""
    return error_response(500, message, details)
