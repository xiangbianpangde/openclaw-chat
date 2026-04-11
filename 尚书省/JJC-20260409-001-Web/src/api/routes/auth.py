"""
认证接口
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt

from src.api.error_codes import unauthorized, bad_request

router = APIRouter()

# JWT 配置
JWT_SECRET = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


# 请求模型
class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


def create_access_token(user_id: str, username: str, role: str = "user") -> str:
    """生成 JWT Token"""
    expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@router.post("/login", response_model=TokenResponse, summary="用户登录")
async def login(request: LoginRequest):
    """
    用户登录接口
    
    - **username**: 用户名
    - **password**: 密码
    
    返回 JWT Token
    """
    # TODO: 验证用户凭据
    # 模拟验证
    if request.username == "admin" and request.password == "admin123":
        access_token = create_access_token("user1", request.username, "admin")
        return TokenResponse(
            access_token=access_token,
            expires_in=TOKEN_EXPIRE_HOURS * 3600
        )
    
    raise HTTPException(status_code=401, detail="Invalid username or password")


@router.post("/refresh", response_model=TokenResponse, summary="刷新 Token")
async def refresh_token(current_user: dict = Depends(lambda: {"user_id": "user1", "username": "admin"})):
    """
    刷新 Token 接口
    
    使用 Refresh Token 获取新的 Access Token
    """
    # TODO: 实现 Refresh Token 机制
    access_token = create_access_token(
        current_user["user_id"],
        current_user["username"]
    )
    
    return TokenResponse(
        access_token=access_token,
        expires_in=TOKEN_EXPIRE_HOURS * 3600
    )
