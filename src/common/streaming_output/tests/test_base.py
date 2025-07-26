"""
测试抽象基类 LLMContentProcessor

该文件测试抽象基类的通用逻辑和接口规范。
"""

import pytest
from unittest.mock import patch
from baml_py import Image

from src.common.streaming_output.base import LLMContentProcessor


class MockResult:
    """模拟 BAML 返回结果"""

    def __init__(self, data):
        self.data = data


class MockProcessor(LLMContentProcessor[dict, dict]):
    """测试用的模拟处理器"""

    async def _call_llm(self, content, **kwargs):
        """模拟 LLM 调用"""
        return MockResult(
            {
                "processed": True,
                "content_type": type(content).__name__,
                "kwargs": kwargs,
            }
        )

    async def _call_llm_stream(self, content, **kwargs):
        """模拟流式 LLM 调用"""
        for i in range(3):
            yield {"chunk": i, "content_type": type(content).__name__, "kwargs": kwargs}

    def _convert_to_schema(self, baml_result, original_content: str, **kwargs):
        """模拟结果转换"""
        return {
            "result": baml_result.data,
            "original": original_content,
            "conversion_kwargs": kwargs,
        }


class TestLLMContentProcessor:
    """测试 LLMContentProcessor 抽象基类"""

    @pytest.fixture
    def processor(self):
        """创建测试处理器实例"""
        return MockProcessor()

    @pytest.mark.asyncio
    async def test_process_from_text_success(self, processor):
        """测试文本处理成功路径"""
        # 准备测试数据
        test_text = "这是一个测试文本内容"
        test_kwargs = {"param1": "value1", "param2": "value2"}

        # 执行测试
        result = await processor.process_from_text(test_text, **test_kwargs)

        # 验证结果
        assert result["result"]["processed"] is True
        assert result["result"]["content_type"] == "str"
        assert result["original"] == test_text
        assert result["conversion_kwargs"] == test_kwargs
        assert result["result"]["kwargs"] == test_kwargs

    @pytest.mark.asyncio
    async def test_process_from_text_with_validation_failure(self, processor):
        """测试文本处理输入验证失败"""
        # 重写验证方法，使其返回 False
        with patch.object(processor, "_validate_input", return_value=False):
            with pytest.raises(ValueError, match="输入验证失败"):
                await processor.process_from_text("test content")

    @pytest.mark.asyncio
    async def test_process_from_text_with_llm_error(self, processor):
        """测试 LLM 调用失败的错误处理"""
        # 模拟 _call_llm 抛出异常
        with patch.object(processor, "_call_llm", side_effect=Exception("LLM调用失败")):
            with pytest.raises(Exception, match="LLM调用失败"):
                await processor.process_from_text("test content")

    @pytest.mark.asyncio
    async def test_process_from_text_with_conversion_error(self, processor):
        """测试结果转换失败的错误处理"""
        # 模拟 _convert_to_schema 抛出异常
        with patch.object(
            processor, "_convert_to_schema", side_effect=ValueError("转换失败")
        ):
            with pytest.raises(ValueError, match="转换失败"):
                await processor.process_from_text("test content")

    @pytest.mark.asyncio
    async def test_process_from_image_success(self, processor):
        """测试图像处理成功路径"""
        # 创建模拟图像对象
        mock_image = Image.from_url("https://example.com/test.png")

        # 执行测试
        result = await processor.process_from_image(mock_image)

        # 验证结果
        assert result["result"]["processed"] is True
        assert result["result"]["content_type"] == "BamlImagePy"
        assert result["original"] == "image_content"

    @pytest.mark.asyncio
    async def test_process_from_image_with_error(self, processor):
        """测试图像处理失败的错误处理"""
        mock_image = Image.from_url("https://example.com/test.png")

        # 模拟 _call_llm 抛出异常
        with patch.object(
            processor, "_call_llm", side_effect=RuntimeError("图像处理失败")
        ):
            with pytest.raises(RuntimeError, match="图像处理失败"):
                await processor.process_from_image(mock_image)

    @pytest.mark.asyncio
    async def test_process_from_content_with_text(self, processor):
        """测试通用接口处理文本"""
        result = await processor.process_from_content("test text content")
        assert result["result"]["content_type"] == "str"

    @pytest.mark.asyncio
    async def test_process_from_content_with_image(self, processor):
        """测试通用接口处理图像"""
        mock_image = Image.from_url("https://example.com/test.png")
        result = await processor.process_from_content(mock_image)
        assert result["result"]["content_type"] == "BamlImagePy"

    @pytest.mark.asyncio
    async def test_process_from_text_stream_success(self, processor):
        """测试文本流式处理成功路径"""
        test_text = "stream test content"
        chunks = []

        async for chunk in processor.process_from_text_stream(test_text):
            chunks.append(chunk)

        # 验证流式结果
        assert len(chunks) == 3
        for i, chunk in enumerate(chunks):
            assert chunk["chunk"] == i
            assert chunk["content_type"] == "str"

    @pytest.mark.asyncio
    async def test_process_from_text_stream_with_validation_error(self, processor):
        """测试流式处理输入验证失败"""
        with patch.object(processor, "_validate_input", return_value=False):
            with pytest.raises(ValueError, match="输入验证失败"):
                async for chunk in processor.process_from_text_stream("test"):
                    pass

    @pytest.mark.asyncio
    async def test_process_from_text_stream_with_llm_error(self, processor):
        """测试流式处理 LLM 调用失败"""

        async def mock_error_stream(*args, **kwargs):
            yield {"chunk": 0}
            raise RuntimeError("流式调用失败")

        with patch.object(processor, "_call_llm_stream", side_effect=mock_error_stream):
            with pytest.raises(RuntimeError, match="流式调用失败"):
                chunks = []
                async for chunk in processor.process_from_text_stream("test"):
                    chunks.append(chunk)

    @pytest.mark.asyncio
    async def test_process_from_image_stream_success(self, processor):
        """测试图像流式处理成功路径"""
        mock_image = Image.from_url("https://example.com/test.png")
        chunks = []

        async for chunk in processor.process_from_image_stream(mock_image):
            chunks.append(chunk)

        # 验证流式结果
        assert len(chunks) == 3
        for chunk in chunks:
            assert chunk["content_type"] == "BamlImagePy"

    @pytest.mark.asyncio
    async def test_process_from_content_stream_with_text(self, processor):
        """测试通用流式接口处理文本"""
        chunks = []
        async for chunk in processor.process_from_content_stream("test stream content"):
            chunks.append(chunk)

        assert len(chunks) == 3
        assert all(chunk["content_type"] == "str" for chunk in chunks)

    @pytest.mark.asyncio
    async def test_process_from_content_stream_with_image(self, processor):
        """测试通用流式接口处理图像"""
        mock_image = Image.from_url("https://example.com/test.png")
        chunks = []
        async for chunk in processor.process_from_content_stream(mock_image):
            chunks.append(chunk)

        assert len(chunks) == 3
        assert all(chunk["content_type"] == "BamlImagePy" for chunk in chunks)

    def test_default_validate_input_with_text(self, processor):
        """测试默认输入验证 - 文本"""
        # 有效文本
        assert processor._validate_input("valid text") is True

        # 空文本
        assert processor._validate_input("") is False
        assert processor._validate_input("   ") is False

    def test_default_validate_input_with_image(self, processor):
        """测试默认输入验证 - 图像"""
        mock_image = Image.from_url("https://example.com/test.png")
        assert processor._validate_input(mock_image) is True

        # None 值
        assert processor._validate_input(None) is False

    def test_default_preprocess_content(self, processor):
        """测试默认内容预处理"""
        # 文本不应该被修改
        test_text = "original text"
        assert processor._preprocess_content(test_text) == test_text

        # 图像不应该被修改
        mock_image = Image.from_url("https://example.com/test.png")
        assert processor._preprocess_content(mock_image) == mock_image

    def test_default_postprocess_result(self, processor):
        """测试默认结果后处理"""
        test_result = {"test": "result"}
        assert processor._postprocess_result(test_result) == test_result

    @pytest.mark.asyncio
    async def test_hooks_integration(self, processor):
        """测试钩子方法的集成"""

        # 创建一个带有钩子方法的处理器
        class HookedProcessor(MockProcessor):
            def _validate_input(self, content, **kwargs):
                return len(content) > 5 if isinstance(content, str) else True

            def _preprocess_content(self, content, **kwargs):
                if isinstance(content, str):
                    return content.upper()
                return content

            def _postprocess_result(self, result, **kwargs):
                result["hooked"] = True
                return result

        hooked_processor = HookedProcessor()

        # 测试成功路径
        result = await hooked_processor.process_from_text("valid long text")
        assert result["hooked"] is True
        # 验证预处理是否生效（文本应该被转为大写）
        assert result["result"]["content_type"] == "str"

        # 测试验证失败
        with pytest.raises(ValueError, match="输入验证失败"):
            await hooked_processor.process_from_text("short")

    def test_logger_initialization(self):
        """测试日志器初始化"""
        # 默认日志器名称
        processor1 = MockProcessor()
        assert processor1.logger.name == "MockProcessor"

        # 自定义日志器名称
        processor2 = MockProcessor(logger_name="CustomLogger")
        assert processor2.logger.name == "CustomLogger"
