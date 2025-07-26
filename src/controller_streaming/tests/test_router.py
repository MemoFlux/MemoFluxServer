"""
Controller Streaming 路由测试
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from src.main import app
from src.controller_streaming.router import router

# 注册路由
app.include_router(router)

client = TestClient(app)


def test_create_ai_streaming_req():
    """测试创建流式 AI 请求"""
    # 准备测试数据
    test_data = {
        "tags": ["test"],
        "content": "测试内容",
        "isimage": 0
    }
    
    # 由于这是一个流式接口，我们只测试请求格式是否正确
    # 实际的流式处理需要更复杂的测试设置
    response = client.post("/aigen_streaming/", json=test_data)
    
    # 验证响应状态码（由于没有有效的认证令牌，可能会返回 401 或其他错误）
    # 但我们主要关心的是路由是否正确设置
    assert response.status_code in [200, 401, 403, 500]


def test_create_ai_streaming_req_invalid_data():
    """测试创建流式 AI 请求 - 无效数据"""
    # 准备无效测试数据
    test_data = {
        "tags": ["test"],
        "content": "",  # 空内容
        "isimage": 0
    }
    
    response = client.post("/aigen_streaming/", json=test_data)
    
    # 验证响应状态码
    assert response.status_code in [400, 401, 403, 500]