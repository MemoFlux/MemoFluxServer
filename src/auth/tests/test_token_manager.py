import pytest
from datetime import datetime, timedelta
from src.auth.token_manager import (
    generate_token,
    store_token,
    verify_token,
    cleanup_expired_tokens,
)


@pytest.fixture(autouse=True)
def clear_tokens():
    """自动清理令牌存储"""
    from src.auth.token_manager import tokens

    tokens.clear()
    yield
    tokens.clear()


def test_generate_token():
    """测试令牌生成"""
    token = generate_token()
    assert isinstance(token, str)
    assert len(token) > 0


def test_store_and_verify_token():
    """测试存储和验证令牌"""
    token = generate_token()
    username = "testuser"

    # 存储令牌
    store_token(token, username)

    # 验证令牌
    verified_username = verify_token(token)
    assert verified_username == username


def test_verify_nonexistent_token():
    """测试验证不存在的令牌"""
    token = "nonexistent_token"
    verified_username = verify_token(token)
    assert verified_username is None


def test_expired_token():
    """测试过期令牌"""
    from src.auth.token_manager import tokens

    token = generate_token()
    username = "testuser"

    # 手动设置一个过期的令牌
    tokens[token] = {
        "username": username,
        "expires": datetime.utcnow() - timedelta(hours=1),  # 1小时前过期
    }

    # 验证令牌应该返回None
    verified_username = verify_token(token)
    assert verified_username is None

    # 过期令牌应该被自动删除
    assert token not in tokens


@pytest.mark.asyncio
async def test_cleanup_expired_tokens():
    """测试清理过期令牌"""
    from src.auth.token_manager import tokens

    # 添加一个有效的令牌
    valid_token = generate_token()
    store_token(valid_token, "valid_user")

    # 添加一个过期的令牌
    expired_token = generate_token()
    tokens[expired_token] = {
        "username": "expired_user",
        "expires": datetime.utcnow() - timedelta(hours=1),  # 1小时前过期
    }

    # 确保两个令牌都在存储中
    assert valid_token in tokens
    assert expired_token in tokens

    # 清理过期令牌
    await cleanup_expired_tokens()

    # 有效的令牌应该还在，过期的令牌应该被删除
    assert valid_token in tokens
    assert expired_token not in tokens
