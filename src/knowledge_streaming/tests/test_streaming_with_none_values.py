"""
Knowledge Streaming 处理器测试 - 测试 None 值处理
"""

import pytest
from unittest.mock import AsyncMock, patch
from baml_py import Image

from src.knowledge_streaming.processor import KnowledgeProcessor
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


@pytest.mark.asyncio
async def test_process_from_text_stream_with_none_values(knowledge_processor, sample_text, sample_tags):
    """测试从文本流式处理知识 - 包含 None 值的情况"""
    # 创建示例流式结果，包含 None 值
    # 我们直接测试 PartialStreamingKnowledge 类的初始化
    from src.knowledge_streaming.schemas import PartialStreamingKnowledge
    
    streaming_result = PartialStreamingKnowledge(
        title={"value": "测试知识标题", "state": "Complete"},
        knowledge_items={"value": [], "state": "Complete"},
        related_items=None,  # 这里是 None 值
        tags=None  # 这里也是 None 值
    )
    
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
            assert hasattr(partial_result, 'tags')
            
            # 验证 None 值已被正确处理为默认列表
            assert partial_result.related_items == []
            assert partial_result.tags == []
        
        assert count > 0


@pytest.mark.asyncio
async def test_process_from_text_stream_with_empty_lists(knowledge_processor, sample_text, sample_tags):
    """测试从文本流式处理知识 - 包含空列表的情况"""
    # 创建示例流式结果，包含空列表
    streaming_result = BamlStreamingKnowledge(
        title={"value": "测试知识标题", "state": "Complete"},
        knowledge_items={"value": [], "state": "Complete"},
        related_items=[],  # 空列表
        tags=[]  # 空列表
    )
    
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
            assert hasattr(partial_result, 'tags')
            
            # 验证空列表保持不变
            assert partial_result.related_items == []
            assert partial_result.tags == []
        
        assert count > 0