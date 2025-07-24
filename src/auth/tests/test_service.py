import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.user import Base, User
from auth.service import (
    hash_password,
    create_user,
    get_user,
    verify_password,
    create_access_token,
)


@pytest.fixture
def db_session():
    """创建临时数据库会话"""
    # 创建临时数据库用于测试
    db_fd, db_path = tempfile.mkstemp()
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    # 创建会话
    db = SessionLocal()

    yield db

    # 清理
    db.close()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(autouse=True)
def clear_tokens():
    """自动清理令牌存储"""
    from auth.token_manager import tokens

    tokens.clear()
    yield
    tokens.clear()


def test_hash_password():
    """测试密码哈希"""
    password = "testpassword"
    hashed = hash_password(password)
    assert isinstance(hashed, str)
    assert len(hashed) > 0
    assert hashed != password


def test_verify_password():
    """测试密码验证"""
    password = "testpassword"
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_create_user(db_session):
    """测试创建用户"""
    username = "testuser"
    password = "testpassword"

    # 创建用户
    user = create_user(db_session, username, password)

    # 验证用户已创建
    assert isinstance(user, User)
    assert user.username == username  # type: ignore
    assert user.id is not None
    assert verify_password(password, user.password_hash)  # type: ignore


def test_create_duplicate_user(db_session):
    """测试创建重复用户"""
    username = "testuser"
    password = "testpassword"

    # 创建第一个用户
    create_user(db_session, username, password)

    # 尝试创建同名用户应该抛出异常
    with pytest.raises(ValueError, match="Username already exists"):
        create_user(db_session, username, password)


def test_get_user(db_session):
    """测试获取用户"""
    username = "testuser"
    password = "testpassword"

    # 创建用户
    created_user = create_user(db_session, username, password)

    # 获取用户
    user = get_user(db_session, username)

    # 验证获取的用户与创建的用户一致
    assert user is not None
    assert user.id == created_user.id  # type: ignore
    assert user.username == username  # type: ignore

    # 尝试获取不存在的用户
    non_existent_user = get_user(db_session, "nonexistent")
    assert non_existent_user is None


def test_create_access_token():
    """测试创建访问令牌"""
    username = "testuser"

    # 创建令牌
    token = create_access_token(username)

    # 验证令牌已存储
    from auth.token_manager import tokens

    assert token in tokens
    assert tokens[token]["username"] == username

    # 验证令牌未过期
    from datetime import datetime

    expires = tokens[token]["expires"]
    assert expires > datetime.utcnow()
