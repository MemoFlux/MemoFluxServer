"""
Information Streaming 处理器测试
"""

import pytest
from unittest.mock import AsyncMock, patch
from baml_py import Image

from src.information_streaming.processor import InformationProcessor
from src.baml_client.types import Information as BamlInformation, InfromationItem as BamlInformationItem
from src.baml_client.stream_types import StreamingInformation as BamlStreamingInformation


@pytest.fixture
def information_processor():
    """创建 InformationProcessor 实例"""
    return InformationProcessor()


@pytest.fixture
def sample_text():
    """示例文本"""
    return "这是一个测试信息内容，用于结构化处理。"


@pytest.fixture
def sample_tags():
    """示例标签"""
    return ["测试", "信息"]


@pytest.fixture
def sample_baml_result():
    """示例 BAML 结果"""
    return BamlInformation(
        title="测试信息标题",
        information_items=[
            BamlInformationItem(
                header="测试项1",
                content="这是测试项1的内容"
            )
        ],
        post_type="OTHER_POST",
        summary="这是一个测试信息的摘要",
        tags=["测试", "信息"]
    )


@pytest.mark.asyncio
async def test_process_from_text(information_processor, sample_text, sample_tags, sample_baml_result):
    """测试从文本处理信息"""
    # 模拟 BAML 调用
    with patch.object(information_processor, '_call_llm', new=AsyncMock(return_value=sample_baml_result)):
        result = await information_processor.process_from_text(sample_text, tags=sample_tags)
        
        # 验证结果
        assert result.title == "测试信息标题"
        assert len(result.information_items) == 1
        assert result.post_type == "OTHER_POST"
        assert result.summary == "这是一个测试信息的摘要"
        assert result.tags == ["测试", "信息"]
        assert result.category == sample_text


@pytest.mark.asyncio
async def test_process_from_text_stream(information_processor, sample_text, sample_tags):
    """测试从文本流式处理信息"""
    # 创建示例流式结果
    # 由于流式类型较为复杂，我们使用更简单的方式创建测试
    streaming_result = AsyncMock()
    streaming_result.title = "测试信息标题"
    streaming_result.information_items = []
    streaming_result.post_type = "OTHER_POST"
    streaming_result.summary = "这是一个测试信息的摘要"
    streaming_result.tags = ["测试", "信息"]
    
    # 模拟 BAML 流式调用
    with patch.object(information_processor, '_call_llm_stream') as mock_call_llm_stream:
        # 创建异步生成器模拟
        async def mock_stream():
            yield streaming_result
        
        mock_call_llm_stream.return_value = mock_stream()
        
        # 测试流式处理
        count = 0
        async for partial_result in information_processor.process_from_text_stream(sample_text, tags=sample_tags):
            count += 1
            assert hasattr(partial_result, 'title')
            assert hasattr(partial_result, 'summary')
        
        assert count > 0


@pytest.mark.asyncio
async def test_validate_input(information_processor, sample_text, sample_tags):
    """测试输入验证"""
    # 有效输入
    assert information_processor._validate_input(sample_text, tags=sample_tags) == True
    
    # 无效输入（太短）
    assert information_processor._validate_input("短", tags=sample_tags) == False
    
    # 有效图像输入
    mock_image = AsyncMock(spec=Image)
    assert information_processor._validate_input(mock_image, tags=sample_tags) == True


@pytest.mark.asyncio
async def test_preprocess_content(information_processor, sample_text, sample_tags):
    """测试内容预处理"""
    # 文本预处理
    processed_text = information_processor._preprocess_content(sample_text, tags=sample_tags)
    assert isinstance(processed_text, str)
    
    # 图像预处理
    mock_image = AsyncMock(spec=Image)
    processed_image = information_processor._preprocess_content(mock_image, tags=sample_tags)
    assert processed_image == mock_image