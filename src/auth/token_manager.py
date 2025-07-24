import secrets
from datetime import datetime, timedelta
from typing import Optional
import asyncio

# 内存中的令牌存储
tokens = {}


def generate_token() -> str:
    """生成令牌"""
    return secrets.token_urlsafe(32)


def store_token(token: str, username: str):
    """存储令牌"""
    tokens[token] = {
        "username": username,
        "expires": datetime.utcnow() + timedelta(hours=1),  # 令牌有效期1小时
    }


def verify_token(token: str) -> Optional[str]:
    """验证令牌"""
    token_data = tokens.get(token)
    if not token_data:
        return None
    if datetime.utcnow() > token_data["expires"]:
        del tokens[token]  # 删除过期令牌
        return None
    return token_data["username"]


async def cleanup_expired_tokens():
    """清理过期令牌"""
    now = datetime.utcnow()
    expired_tokens = [token for token, data in tokens.items() if now > data["expires"]]
    for token in expired_tokens:
        del tokens[token]


async def start_token_cleanup_task():
    """启动令牌清理任务"""
    while True:
        await asyncio.sleep(60)  # 每分钟检查一次
        await cleanup_expired_tokens()
