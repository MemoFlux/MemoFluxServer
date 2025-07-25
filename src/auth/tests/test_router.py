import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os
from src.db import Base
from src.auth.router import router


@pytest.fixture
def client():
    """创建测试客户端"""
    # 创建临时数据库用于测试
    db_fd, db_path = tempfile.mkstemp()
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    # 创建测试应用
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    # 替换依赖项
    from src.db import get_db

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield client

    # 清理
    os.close(db_fd)
    os.unlink(db_path)
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clear_tokens():
    """自动清理令牌存储"""
    from src.auth.token_manager import tokens

    tokens.clear()
    yield
    tokens.clear()


def test_register_user(client):
    """测试用户注册"""
    response = client.post(
        "/register", json={"username": "testuser", "password": "testpassword"}
    )

    assert response.status_code == 200
    assert response.json() == {"message": "User created successfully"}


def test_register_duplicate_user(client):
    """测试注册重复用户"""
    # 先注册一个用户
    client.post("/register", json={"username": "testuser", "password": "testpassword"})

    # 再次注册同名用户应该失败
    response = client.post(
        "/register", json={"username": "testuser", "password": "testpassword"}
    )

    assert response.status_code == 400
    assert "Username already exists" in response.json()["detail"]


def test_login_user(client):
    """测试用户登录"""
    # 先注册一个用户
    client.post("/register", json={"username": "testuser", "password": "testpassword"})

    # 登录用户
    response = client.post(
        "/login", json={"username": "testuser", "password": "testpassword"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """测试使用无效凭据登录"""
    # 尝试登录不存在的用户
    response = client.post(
        "/login", json={"username": "nonexistent", "password": "testpassword"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"

    # 先注册一个用户
    client.post("/register", json={"username": "testuser", "password": "testpassword"})

    # 使用错误密码登录
    response = client.post(
        "/login", json={"username": "testuser", "password": "wrongpassword"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"


def test_get_current_user(client):
    """测试获取当前用户"""
    # 先注册一个用户
    client.post("/register", json={"username": "testuser", "password": "testpassword"})

    # 登录获取令牌
    login_response = client.post(
        "/login", json={"username": "testuser", "password": "testpassword"}
    )

    token = login_response.json()["access_token"]

    # 使用令牌获取当前用户信息
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {"username": "testuser"}


def test_get_current_user_missing_header(client):
    """测试缺少授权头获取当前用户"""
    response = client.get("/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authorization header missing"


def test_get_current_user_invalid_scheme(client):
    """测试使用无效授权方案获取当前用户"""
    response = client.get("/me", headers={"Authorization": "Basic token"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication scheme"


def test_get_current_user_invalid_token(client):
    """测试使用无效令牌获取当前用户"""
    response = client.get("/me", headers={"Authorization": "Bearer invalid_token"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"
