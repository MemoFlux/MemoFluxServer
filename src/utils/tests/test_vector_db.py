import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.utils.vector_db import VectorDB, KEYS
from src.utils.schemas import (
    JinaEmbeddingResponse, 
    JinaEmbeddingData, 
    JinaEmbeddingUsage, 
    VectorSearchResult, 
    JinaTextInput
)
from qdrant_client.http import models as rest

pytestmark = pytest.mark.asyncio

MOCK_URL = "http://localhost:6333"
MOCK_API_KEY = "test-key"
MOCK_COLLECTION_NAME = "test-collection"


@pytest.fixture(autouse=True)
def reset_singleton():
    """在每个测试用例运行后重置 VectorDB 单例。"""
    VectorDB._instance = None
    yield
    VectorDB._instance = None


@pytest.fixture
def mock_keys_embedding_response():
    """为 KEYS 列表模拟一个 Jina API 响应。"""
    embeddings = [[i / 100.0] * 2048 for i in range(len(KEYS))]
    data = [
        JinaEmbeddingData(object="embedding", embedding=emb, index=i)
        for i, emb in enumerate(embeddings)
    ]
    usage = JinaEmbeddingUsage(total_tokens=1000)
    return JinaEmbeddingResponse(
        object="list", data=data, model="jina-embeddings-v4", usage=usage
    )

@pytest.fixture
def mock_qdrant_client():
    """模拟一个 AsyncQdrantClient 实例。"""
    client = AsyncMock()
    client.collection_exists = AsyncMock(return_value=False)
    client.create_collection = AsyncMock()
    
    empty_collection_info = MagicMock()
    empty_collection_info.points_count = 0
    client.get_collection = AsyncMock(return_value=empty_collection_info)
    
    client.upsert = AsyncMock()
    
    mock_search_hits = [
        rest.ScoredPoint(id=str(i), version=1, score=0.9 - i * 0.1, payload={"text": f"hit_{i}"})
        for i in range(3)
    ]
    client.search = AsyncMock(return_value=mock_search_hits)
    
    return client

@patch("src.utils.vector_db.get_embeddings")
@patch("src.utils.vector_db.utils_config")
@patch("src.utils.vector_db.AsyncQdrantClient")
async def test_create_and_initialize_new_collection(
    mock_qdrant_constructor, mock_utils_config, mock_get_embeddings, mock_qdrant_client, mock_keys_embedding_response
):
    """测试在一个新集合上成功创建和初始化 VectorDB。"""
    mock_qdrant_constructor.return_value = mock_qdrant_client
    mock_get_embeddings.return_value = mock_keys_embedding_response
    mock_utils_config.collection_name = MOCK_COLLECTION_NAME
    mock_utils_config.qdrant_url = MOCK_URL
    mock_utils_config.qdrant_api_key = MOCK_API_KEY
    
    db = await VectorDB.get_instance()

    assert db.initialized is True
    assert db.collection_name == MOCK_COLLECTION_NAME
    mock_qdrant_client.collection_exists.assert_awaited_once_with(collection_name=MOCK_COLLECTION_NAME)
    mock_qdrant_client.create_collection.assert_awaited_once()
    mock_get_embeddings.assert_awaited_once()
    
    # 验证 get_embeddings 是用 JinaTextInput 对象列表调用的
    embedding_call_args = mock_get_embeddings.call_args[0][0]
    assert all(isinstance(arg, JinaTextInput) for arg in embedding_call_args)
    assert [arg.text for arg in embedding_call_args] == KEYS

    mock_qdrant_client.upsert.assert_awaited_once()
    upserted_points = mock_qdrant_client.upsert.call_args.kwargs['points']
    assert len(upserted_points) == len(KEYS)

@patch("src.utils.vector_db.get_embeddings")
@patch("src.utils.vector_db.utils_config")
@patch("src.utils.vector_db.AsyncQdrantClient")
async def test_initialize_with_existing_populated_collection(
    mock_qdrant_constructor, mock_utils_config, mock_get_embeddings, mock_qdrant_client
):
    """测试当集合已存在且有数据时，初始化应跳过嵌入和上传步骤。"""
    mock_qdrant_constructor.return_value = mock_qdrant_client
    mock_qdrant_client.collection_exists.return_value = True
    mock_utils_config.collection_name = MOCK_COLLECTION_NAME
    mock_utils_config.qdrant_url = MOCK_URL
    mock_utils_config.qdrant_api_key = MOCK_API_KEY
    
    populated_collection_info = MagicMock()
    populated_collection_info.points_count = len(KEYS)
    mock_qdrant_client.get_collection.return_value = populated_collection_info
    
    db = await VectorDB.get_instance()

    assert db.initialized is True
    mock_qdrant_client.collection_exists.assert_awaited_once_with(collection_name=MOCK_COLLECTION_NAME)
    mock_qdrant_client.create_collection.assert_not_awaited()
    mock_qdrant_client.get_collection.assert_awaited_once_with(collection_name=MOCK_COLLECTION_NAME)
    mock_get_embeddings.assert_not_awaited()
    mock_qdrant_client.upsert.assert_not_awaited()

@patch("src.utils.vector_db.get_embeddings")
@patch("src.utils.vector_db.utils_config")
@patch("src.utils.vector_db.AsyncQdrantClient")
async def test_search_successfully(
    mock_qdrant_constructor, mock_utils_config, mock_get_embeddings, mock_qdrant_client
):
    """测试 search 方法能否成功执行并返回正确格式的结果。"""
    # 初始化 Mock
    mock_qdrant_constructor.return_value = mock_qdrant_client
    mock_qdrant_client.collection_exists.return_value = True
    mock_utils_config.collection_name = MOCK_COLLECTION_NAME
    mock_utils_config.qdrant_url = MOCK_URL
    mock_utils_config.qdrant_api_key = MOCK_API_KEY

    populated_collection_info = MagicMock()
    populated_collection_info.points_count = len(KEYS)
    mock_qdrant_client.get_collection.return_value = populated_collection_info

    # 搜索查询的 Mock 响应
    query_text = "test query"
    query_embedding = [0.5] * 2048
    search_response_data = JinaEmbeddingData(object="embedding", embedding=query_embedding, index=0)
    search_response = JinaEmbeddingResponse(
        object="list", data=[search_response_data], model="jina-embeddings-v4", usage=JinaEmbeddingUsage(total_tokens=5)
    )
    mock_get_embeddings.return_value = search_response
    
    db = await VectorDB.get_instance()
    
    results = await db.search(query_text, limit=3)
    
    mock_get_embeddings.assert_awaited_with([query_text])
    mock_qdrant_client.search.assert_awaited_once_with(
        collection_name=MOCK_COLLECTION_NAME,
        query_vector=query_embedding,
        limit=3
    )
    
    assert len(results) == 3
    assert all(isinstance(r, VectorSearchResult) for r in results)
    assert results[0].score == 0.9

async def test_search_on_uninitialized_db_raises_error():
    """测试在未初始化的 VectorDB 实例上调用 search 会抛出 RuntimeError。"""
    # 为了测试未初始化状态，我们直接实例化而不通过 get_instance
    db = VectorDB(MOCK_COLLECTION_NAME, MOCK_URL, MOCK_API_KEY)
    with pytest.raises(RuntimeError, match="VectorDB is not initialized"):
        await db.search("test query") 