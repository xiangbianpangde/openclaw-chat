"""
认证与授权接口
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from config.settings import settings

router = APIRouter()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


def create_access_token(user_id: str, role: str) -> str:
    """生成 JWT Token"""
    expire = datetime.utcnow() + timedelta(hours=settings.TOKEN_EXPIRE_HOURS)
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': expire,
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


@router.post("/login", response_model=TokenResponse)
async def login(request: TokenRequest):
    """用户登录"""
    # TODO: 实际应从数据库验证用户
    # 这里仅做示例
    if request.username == "admin" and request.password == "admin123":
        access_token = create_access_token(user_id="admin", role="admin")
        return TokenResponse(
            access_token=access_token,
            expires_in=settings.TOKEN_EXPIRE_HOURS * 3600
        )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="用户名或密码错误"
    )


@router.get("/me")
async def get_current_user_info():
    """获取当前用户信息"""
    # TODO: 从 token 解析用户信息
    return {
        "user_id": "admin",
        "username": "admin",
        "role": "admin",
        "is_active": True
    }
