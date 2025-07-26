"""
测试文档处理示例实现

该文件测试 DocumentProcessor 的具体实现逻辑。
"""

import pytest
from unittest.mock import patch
from baml_py import Image

from src.common.streaming_output.document_example import (
    DocumentProcessor,
    MockBamlDocument,
    MockBamlDocumentSection,
)
from src.common.streaming_output.schemas import (
    Document,
    DocumentSection,
    PartialStreamingDocument,
)


class TestDocumentProcessor:
    """测试 DocumentProcessor 实现类"""

    @pytest.fixture
    def processor(self):
        """创建文档处理器实例"""
        return DocumentProcessor()

    @pytest.mark.asyncio
    async def test_call_llm_with_meeting_content(self, processor):
        """测试会议内容的 LLM 调用"""
        meeting_text = "今天上午9点举行了项目启动会议，参会人员包括张三、李四、王五。会议主要讨论了项目的整体规划。"

        result = await processor._call_llm(meeting_text)

        assert isinstance(result, MockBamlDocument)
        assert result.category == "会议纪要"
        assert result.title == "会议记录分析"
        assert len(result.sections) > 0
        assert "会议" in result.summary

    @pytest.mark.asyncio
    async def test_call_llm_with_report_content(self, processor):
        """测试报告内容的 LLM 调用"""
        report_text = "本报告分析了当前系统的性能瓶颈。通过压力测试发现，数据库查询是主要的性能限制因素。"

        result = await processor._call_llm(report_text)

        assert result.category == "报告文档"
        assert result.title == "报告内容分析"
        assert len(result.sections) > 0

    @pytest.mark.asyncio
    async def test_call_llm_with_plan_content(self, processor):
        """测试计划内容的 LLM 调用"""
        plan_text = "我们计划在下个月启动新项目。第一阶段将专注于需求分析，第二阶段进行设计开发。"

        result = await processor._call_llm(plan_text)

        assert result.category == "计划文档"
        assert result.title == "计划内容分析"

    @pytest.mark.asyncio
    async def test_call_llm_with_generic_content(self, processor):
        """测试普通内容的 LLM 调用"""
        generic_text = (
            "这是一份普通的文档内容，没有特定的类型标识。包含了一些基本信息和描述。"
        )

        result = await processor._call_llm(generic_text)

        assert result.category == "普通文档"
        assert result.title == "文档内容分析"

    @pytest.mark.asyncio
    async def test_call_llm_with_image(self, processor):
        """测试图像输入的 LLM 调用"""
        mock_image = Image.from_url("https://example.com/test.png")

        result = await processor._call_llm(mock_image)

        assert result.category == "图像文档"
        assert result.title == "图像内容分析"
        assert len(result.sections) == 1
        assert result.sections[0].title == "图像描述"

    @pytest.mark.asyncio
    async def test_call_llm_with_language_parameter(self, processor):
        """测试带语言参数的 LLM 调用"""
        text = "Test document content"

        result = await processor._call_llm(text, language="en")

        assert result.language == "en"

    @pytest.mark.asyncio
    async def test_call_llm_stream_flow(self, processor):
        """测试流式 LLM 调用的完整流程"""
        test_text = "这是一个流式处理测试文档"
        chunks = []

        async for chunk in processor._call_llm_stream(test_text):
            chunks.append(chunk)

        # 验证流式处理的数据块数量
        assert len(chunks) == 4

        # 验证第一个数据块（仅包含标题）
        first_chunk = chunks[0]
        assert first_chunk.title is not None
        assert first_chunk.title.value == "文档内容分析"
        assert first_chunk.title.state == "Complete"
        assert first_chunk.category == "文档分析"

        # 验证最后一个数据块（包含完整信息）
        last_chunk = chunks[-1]
        assert last_chunk.title is not None
        assert last_chunk.summary is not None
        assert last_chunk.sections is not None
        assert last_chunk.word_count is not None

    @pytest.mark.asyncio
    async def test_call_llm_stream_with_image(self, processor):
        """测试图像的流式处理"""
        mock_image = Image.from_url("https://example.com/test.png")
        chunks = []

        async for chunk in processor._call_llm_stream(mock_image):
            chunks.append(chunk)

        assert len(chunks) == 4
        last_chunk = chunks[-1]
        assert last_chunk.word_count == 0  # 图像没有字数

    def test_convert_to_schema_success(self, processor):
        """测试成功的结果转换"""
        # 创建模拟的 BAML 结果
        mock_sections = [
            MockBamlDocumentSection("第一部分", "第一部分的内容", 1, ["标签1"]),
            MockBamlDocumentSection(
                "第二部分", "第二部分的内容", 2, ["标签2", "标签3"]
            ),
        ]
        mock_baml_result = MockBamlDocument(
            title="测试文档",
            summary="这是一个测试文档的摘要",
            category="测试类别",
            sections=mock_sections,
            language="zh",
        )

        original_content = "原始测试内容"

        # 执行转换
        result = processor._convert_to_schema(mock_baml_result, original_content)

        # 验证转换结果
        assert isinstance(result, Document)
        assert result.title == "测试文档"
        assert result.summary == "这是一个测试文档的摘要"
        assert result.category == "测试类别"
        assert result.original_content == original_content
        assert result.language == "zh"
        assert result.word_count == len(original_content)
        assert len(result.sections) == 2

        # 验证章节转换
        assert isinstance(result.sections[0], DocumentSection)
        assert result.sections[0].title == "第一部分"
        assert result.sections[0].content == "第一部分的内容"
        assert result.sections[0].level == 1
        assert result.sections[0].tags == ["标签1"]

    def test_convert_to_schema_with_empty_sections(self, processor):
        """测试空章节列表的转换"""
        mock_baml_result = MockBamlDocument(
            title="无章节文档",
            summary="没有章节的文档",
            category="简单文档",
            sections=[],
            language="zh",
        )

        result = processor._convert_to_schema(mock_baml_result, "test content")

        assert len(result.sections) == 0
        assert result.title == "无章节文档"

    def test_validate_input_with_valid_text(self, processor):
        """测试有效文本的输入验证"""
        # 有效长度的文本（>= 10字符）
        valid_text = "这是一个有效的文本输入，长度足够"
        assert processor._validate_input(valid_text) is True

    def test_validate_input_with_invalid_text(self, processor):
        """测试无效文本的输入验证"""
        # 过短的文本（< 10字符）
        short_text = "太短了"
        assert processor._validate_input(short_text) is False

        # 空文本
        empty_text = ""
        assert processor._validate_input(empty_text) is False

        # 仅空格的文本
        whitespace_text = "   "
        assert processor._validate_input(whitespace_text) is False

    def test_validate_input_with_image(self, processor):
        """测试图像的输入验证"""
        mock_image = Image.from_url("https://example.com/test.png")
        assert processor._validate_input(mock_image) is True

        # None 值
        assert processor._validate_input(None) is False

    def test_preprocess_content_with_text(self, processor):
        """测试文本预处理"""
        # 测试空白字符清理
        messy_text = "  这是一个    有很多   空格的    文本  "
        cleaned_text = processor._preprocess_content(messy_text)

        assert cleaned_text == "这是一个 有很多 空格的 文本"
        assert "  " not in cleaned_text  # 确保没有连续空格

    def test_preprocess_content_with_newlines(self, processor):
        """测试包含换行符的文本预处理"""
        text_with_newlines = "第一行\n第二行\n\n第三行"
        cleaned_text = processor._preprocess_content(text_with_newlines)

        assert cleaned_text == "第一行 第二行 第三行"

    def test_preprocess_content_with_image(self, processor):
        """测试图像预处理（应该不变）"""
        mock_image = Image.from_url("https://example.com/test.png")
        processed_image = processor._preprocess_content(mock_image)

        assert processed_image == mock_image

    def test_postprocess_result_adds_default_tags(self, processor):
        """测试结果后处理添加默认标签"""
        # 创建一个包含无标签章节的文档
        sections_without_tags = [
            DocumentSection(title="无标签章节", content="内容", level=1, tags=[]),
            DocumentSection(
                title="有标签章节", content="内容", level=1, tags=["已有标签"]
            ),
        ]

        document = Document(
            title="测试文档",
            summary="测试摘要",
            category="测试",
            sections=sections_without_tags,
            original_content="原始内容",
        )

        # 执行后处理
        processed_document = processor._postprocess_result(document)

        # 验证无标签的章节被添加了默认标签
        assert processed_document.sections[0].tags == ["未分类"]
        # 验证有标签的章节保持不变
        assert processed_document.sections[1].tags == ["已有标签"]

    @pytest.mark.asyncio
    async def test_full_processing_pipeline_text(self, processor):
        """测试完整的文本处理流程"""
        test_text = "这是一个完整的文档处理测试。内容包含了足够的信息来进行分析和处理。"

        result = await processor.process_from_text(test_text, language="zh")

        # 验证最终结果
        assert isinstance(result, Document)
        assert result.title is not None
        assert result.summary is not None
        assert result.category is not None
        assert result.original_content == test_text
        assert result.language == "zh"
        assert result.word_count == len(test_text)
        assert len(result.sections) > 0

        # 验证后处理效果（无标签章节应该有默认标签）
        for section in result.sections:
            assert len(section.tags) > 0

    @pytest.mark.asyncio
    async def test_full_processing_pipeline_image(self, processor):
        """测试完整的图像处理流程"""
        mock_image = Image.from_url("https://example.com/document.png")

        result = await processor.process_from_image(mock_image)

        assert isinstance(result, Document)
        assert result.category == "图像文档"
        assert result.original_content == "image_content"
        assert result.word_count == 0
        assert len(result.sections) == 1
        assert result.sections[0].title == "图像描述"

    @pytest.mark.asyncio
    async def test_full_streaming_pipeline(self, processor):
        """测试完整的流式处理流程"""
        test_text = "这是一个流式处理的完整测试文档内容。"
        chunks = []

        async for chunk in processor.process_from_text_stream(test_text):
            chunks.append(chunk)

        # 验证流式处理结果
        assert len(chunks) == 4

        # 验证流式数据的完整性
        final_chunk = chunks[-1]
        assert final_chunk.title is not None
        assert final_chunk.summary is not None
        assert final_chunk.sections is not None
        assert final_chunk.language == "zh"
        assert final_chunk.word_count == len(test_text)

    @pytest.mark.asyncio
    async def test_error_handling_in_llm_call(self, processor):
        """测试 LLM 调用中的错误处理"""
        # 模拟 _call_llm 中发生异常
        with patch.object(
            processor, "_call_llm", side_effect=RuntimeError("模拟LLM错误")
        ):
            with pytest.raises(RuntimeError, match="模拟LLM错误"):
                await processor.process_from_text(
                    "这是一个足够长的测试内容，用于模拟错误处理"
                )

    @pytest.mark.asyncio
    async def test_error_handling_in_streaming(self, processor):
        """测试流式处理中的错误处理"""

        async def mock_error_stream(*args, **kwargs):
            yield PartialStreamingDocument(title=None)
            raise Exception("流式处理错误")

        with patch.object(processor, "_call_llm_stream", side_effect=mock_error_stream):
            with pytest.raises(Exception, match="流式处理错误"):
                chunks = []
                async for chunk in processor.process_from_text_stream(
                    "这是一个足够长的测试内容，用于模拟流式错误处理"
                ):
                    chunks.append(chunk)

    @pytest.mark.asyncio
    async def test_input_validation_integration(self, processor):
        """测试输入验证的集成"""
        # 有效输入
        valid_text = "这是一个有效的长文本输入，应该能够通过验证。"
        result = await processor.process_from_text(valid_text)
        assert isinstance(result, Document)

        # 无效输入（太短）
        invalid_text = "太短"
        with pytest.raises(ValueError, match="输入验证失败"):
            await processor.process_from_text(invalid_text)

    def test_logger_name(self, processor):
        """测试日志器名称设置"""
        assert processor.logger.name == "DocumentProcessor"

        # 测试自定义日志器名称
        custom_processor = DocumentProcessor(logger_name="CustomDocProcessor")
        assert custom_processor.logger.name == "CustomDocProcessor"
