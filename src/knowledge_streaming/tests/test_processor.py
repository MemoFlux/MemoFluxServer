"""
Knowledge Streaming 处理器测试
"""

import pytest
from unittest.mock import AsyncMock, patch
from baml_py import Image

from src.knowledge_streaming.processor import KnowledgeProcessor
from src.baml_client.types import Knowledge as BamlKnowledge, KnowledgeItem as BamlKnowledgeItem
from src.baml_client.stream_types import StreamingKnowledge as BamlStreamingKnowledge


@pytest.fixture
def knowledge_processor():
    """创建 KnowledgeProcessor 实例"""
    return KnowledgeProcessor()


@pytest.fixture
def sample_text():
    """示例文本"""
    return "这是一个测试知识内容，用于结构化处理。"


@pytest.fixture
def sample_tags():
    """示例标签"""
    return ["测试", "知识"]


@pytest.fixture
def sample_baml_result():
    """示例 BAML 结果"""
    return BamlKnowledge(
        title="测试知识标题",
        knowledge_items=[
            BamlKnowledgeItem(
                id=1,
                header="测试项1",
                content="这是测试项1的内容",
                node=None
            )
        ],
        related_items=["相关知识1", "相关知识2"],
        tags=["测试", "知识"]
    )


@pytest.mark.asyncio
async def test_process_from_text(knowledge_processor, sample_text, sample_tags, sample_baml_result):
    """测试从文本处理知识"""
    # 模拟 BAML 调用
    with patch.object(knowledge_processor, '_call_llm', new=AsyncMock(return_value=sample_baml_result)):
        result = await knowledge_processor.process_from_text(sample_text, tags=sample_tags)
        
        # 验证结果
        assert result.title == "测试知识标题"
        assert len(result.knowledge_items) == 1
        assert result.related_items == ["相关知识1", "相关知识2"]
        assert result.tags == ["测试", "知识"]
        assert result.category == sample_text


@pytest.mark.asyncio
async def test_process_from_text_stream(knowledge_processor, sample_text, sample_tags):
    """测试从文本流式处理知识"""
    # 创建示例流式结果
    # 由于流式类型较为复杂，我们使用更简单的方式创建测试
    streaming_result = AsyncMock()
    streaming_result.title = "测试知识标题"
    streaming_result.knowledge_items = []
    streaming_result.related_items = ["相关知识1", "相关知识2"]
    streaming_result.tags = ["测试", "知识"]
    
    # 模拟 BAML 流式调用
    with patch.object(knowledge_processor, '_call_llm_stream') as mock_call_llm_stream:
        # 创建异步生成器模拟
        async def mock_stream():
            yield streaming_result
        
        mock_call_llm_stream.return_value = mock_stream()
        
        # 测试流式处理
        count = 0
        async for partial_result in knowledge_processor.process_from_text_stream(sample_text, tags=sample_tags):
            count += 1
            assert hasattr(partial_result, 'title')
            assert hasattr(partial_result, 'related_items')
        
        assert count > 0


@pytest.mark.asyncio
async def test_validate_input(knowledge_processor, sample_text, sample_tags):
    """测试输入验证"""
    # 有效输入
    assert knowledge_processor._validate_input(sample_text, tags=sample_tags) == True
    
    # 无效输入（太短）
    assert knowledge_processor._validate_input("短", tags=sample_tags) == False
    
    # 有效图像输入
    mock_image = AsyncMock(spec=Image)
    assert knowledge_processor._validate_input(mock_image, tags=sample_tags) == True


@pytest.mark.asyncio
async def test_preprocess_content(knowledge_processor, sample_text, sample_tags):
    """测试内容预处理"""
    # 文本预处理
    processed_text = knowledge_processor._preprocess_content(sample_text, tags=sample_tags)
    assert isinstance(processed_text, str)
    
    # 图像预处理
    mock_image = AsyncMock(spec=Image)
    processed_image = knowledge_processor._preprocess_content(mock_image, tags=sample_tags)
    assert processed_image == mock_image