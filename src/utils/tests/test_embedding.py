"""测试 embedding 工具的测试文件。

该文件包含对 get_embeddings 函数的测试用例，
分为快速测试（使用 mock）和慢速测试（使用真实 API）两类。
"""

import pytest
from unittest.mock import patch
from src.utils.embedding import get_embeddings
from src.utils.schemas import JinaEmbeddingResponse, JinaEmbeddingData, JinaUsage


# 快速测试（使用 mock）
class TestGetEmbeddingsFast:
    """快速测试类，使用 mock 来避免实际的 API 调用。"""

    @pytest.mark.asyncio
    async def test_get_embeddings_success(self):
        """测试成功获取嵌入向量的情况。"""
        # 准备测试数据
        content = ["This is a test content."]
        mock_response_data = {
            "model": "jina-embeddings-v4",
            "object": "list",
            "usage": {"total_tokens": 10},
            "data": [
                {
                    "object": "embedding",
                    "index": 0,
                    "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
                }
            ]
        }
        
        # Mock _make_embedding_request 函数
        with patch('src.utils.embedding._make_embedding_request', return_value=mock_response_data):
            # 调用函数
            result = await get_embeddings(content)
            
            # 验证结果
            assert isinstance(result, JinaEmbeddingResponse)
            assert result.model == "jina-embeddings-v4"
            assert result.object == "list"
            assert isinstance(result.usage, JinaUsage)
            assert result.usage.total_tokens == 10
            assert len(result.data) == 1
            assert isinstance(result.data[0], JinaEmbeddingData)
            assert result.data[0].object == "embedding"
            assert result.data[0].index == 0
            assert result.data[0].embedding == [0.1, 0.2, 0.3, 0.4, 0.5]

    @pytest.mark.asyncio
    async def test_get_embeddings_with_empty_content(self):
        """测试传入空内容的情况。"""
        # 准备测试数据
        content = []
        mock_response_data = {
            "model": "jina-embeddings-v4",
            "object": "list",
            "usage": {"total_tokens": 0},
            "data": []
        }
        
        # Mock _make_embedding_request 函数
        with patch('src.utils.embedding._make_embedding_request', return_value=mock_response_data):
            # 调用函数
            with pytest.raises(ValueError):
                await get_embeddings(content)


# 慢速测试（使用真实 API）
@pytest.mark.slow
class TestGetEmbeddingsSlow:
    """慢速测试类，使用真实的 API 进行测试。需要有效的 JINA_API_KEY。"""

    @pytest.mark.asyncio
    async def test_get_embeddings_real_api(self):
        """使用真实 API 测试获取嵌入向量。"""
        # 准备测试数据
        content = ["This is a test content for real API call.", "This is a test content for real API call.", "This is a test content for real API call."]

        result = await get_embeddings(content)
        # 验证结果
        assert isinstance(result, JinaEmbeddingResponse)
        assert result.model.startswith("jina-embeddings")
        assert result.object == "list"
        assert isinstance(result.usage, JinaUsage)
        assert result.usage.total_tokens > 0
        assert len(result.data) > 0
        assert isinstance(result.data[0], JinaEmbeddingData)
        assert result.data[0].object == "embedding"
        assert result.data[0].index == 0
        assert isinstance(result.data[0].embedding, list)
        assert len(result.data[0].embedding) > 0

    @pytest.mark.asyncio
    async def test_get_embeddings_real_api_empty_content(self):
        """使用真实 API 测试传入空内容。"""
        # 准备测试数据
        content = []

        with pytest.raises(ValueError):
            await get_embeddings(content)

if __name__ == "__main__":
    pytest.main(["-v", __file__])