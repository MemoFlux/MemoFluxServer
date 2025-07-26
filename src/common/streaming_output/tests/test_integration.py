"""
集成测试

该文件测试整个 streaming_output 模块的集成功能。
"""

import pytest
import asyncio
import time
from unittest.mock import patch
from baml_py import Image

from src.common.streaming_output import LLMContentProcessor
from src.common.streaming_output.document_example import (
    document_processor,
    DocumentProcessor,
)
from src.common.streaming_output.schemas import Document


class TestStreamingOutputIntegration:
    """测试 streaming_output 模块的集成功能"""

    @pytest.mark.asyncio
    async def test_unified_interface_consistency(self):
        """测试统一接口的一致性"""
        test_content = (
            "这是一个用于测试统一接口一致性的文档内容，包含足够的信息来进行完整的处理。"
        )

        # 通过不同的入口点调用相同的功能
        result1 = await document_processor.process_from_text(test_content)
        result2 = await document_processor.process_from_content(test_content)

        # 验证结果的一致性
        assert result1.title == result2.title
        assert result1.category == result2.category
        assert result1.summary == result2.summary
        assert result1.original_content == result2.original_content

    @pytest.mark.asyncio
    async def test_streaming_vs_non_streaming_consistency(self):
        """测试流式和非流式处理结果的一致性"""
        test_content = "这是一个测试文档，用于验证流式和非流式处理的结果一致性。内容需要足够长以便进行有效的比较。"

        # 非流式处理
        non_streaming_result = await document_processor.process_from_text(test_content)

        # 流式处理 - 收集所有块
        streaming_chunks = []
        async for chunk in document_processor.process_from_text_stream(test_content):
            streaming_chunks.append(chunk)

        # 验证流式处理有数据返回
        assert len(streaming_chunks) > 0

        # 获取最后一个流式块
        final_chunk = streaming_chunks[-1]

        # 验证关键信息的一致性
        if final_chunk.title and final_chunk.title.value:
            assert final_chunk.title.value == non_streaming_result.title

        if final_chunk.word_count is not None:
            assert final_chunk.word_count == non_streaming_result.word_count

    @pytest.mark.asyncio
    async def test_multiple_processors_isolation(self):
        """测试多个处理器实例的隔离性"""
        # 创建多个处理器实例
        processor1 = DocumentProcessor(logger_name="Processor1")
        processor2 = DocumentProcessor(logger_name="Processor2")

        test_content = "测试多处理器隔离的文档内容，确保各处理器实例之间不会相互干扰。"

        # 并发处理
        results = await asyncio.gather(
            processor1.process_from_text(test_content),
            processor2.process_from_text(test_content),
        )

        # 验证结果
        assert len(results) == 2
        assert all(isinstance(result, Document) for result in results)

        # 验证处理器隔离（日志器名称不同）
        assert processor1.logger.name == "Processor1"
        assert processor2.logger.name == "Processor2"

    @pytest.mark.asyncio
    async def test_concurrent_processing_performance(self):
        """测试并发处理性能"""
        test_contents = [
            f"这是第{i}个测试文档，用于验证并发处理能力。内容包含足够的信息进行分析。"
            for i in range(5)
        ]

        # 测量并发处理时间
        start_time = time.time()

        # 并发处理所有内容
        tasks = [
            document_processor.process_from_text(content) for content in test_contents
        ]
        results = await asyncio.gather(*tasks)

        end_time = time.time()
        processing_time = end_time - start_time

        # 验证结果
        assert len(results) == len(test_contents)
        assert all(isinstance(result, Document) for result in results)

        # 验证性能（应该在合理时间内完成）
        assert processing_time < 10.0  # 5个任务应在10秒内完成

        # 验证每个结果的唯一性
        # 虽然内容相似，但每个文档都应该有自己的ID
        ids = [result.id for result in results]
        assert len(set(ids)) == len(ids)  # 所有ID应该唯一

    @pytest.mark.asyncio
    async def test_streaming_performance_and_ordering(self):
        """测试流式处理的性能和顺序"""
        test_content = "这是一个用于测试流式处理性能和数据块顺序的文档内容。"

        chunks = []
        chunk_timestamps = []

        start_time = time.time()

        async for chunk in document_processor.process_from_text_stream(test_content):
            chunks.append(chunk)
            chunk_timestamps.append(time.time() - start_time)

        # 验证基本要求
        assert len(chunks) > 0
        assert len(chunk_timestamps) == len(chunks)

        # 验证流式数据的时间顺序
        for i in range(1, len(chunk_timestamps)):
            assert chunk_timestamps[i] >= chunk_timestamps[i - 1]

        # 验证流式处理的响应性（第一个块应该快速到达）
        if len(chunk_timestamps) > 0:
            assert chunk_timestamps[0] < 2.0  # 第一个块应在2秒内到达

    @pytest.mark.asyncio
    async def test_error_propagation_and_recovery(self):
        """测试错误传播和恢复"""
        # 测试处理错误的传播
        with patch.object(
            document_processor, "_call_llm", side_effect=RuntimeError("模拟处理错误")
        ):
            with pytest.raises(RuntimeError, match="模拟处理错误"):
                await document_processor.process_from_text(
                    "这是一个足够长的测试内容，用于触发错误处理机制。"
                )

        # 验证错误后处理器仍然能正常工作
        normal_content = (
            "错误恢复测试：这是一个正常的文档内容，用于验证处理器在错误后仍能正常工作。"
        )
        result = await document_processor.process_from_text(normal_content)

        assert isinstance(result, Document)
        assert result.title is not None

    @pytest.mark.asyncio
    async def test_input_validation_across_interfaces(self):
        """测试跨接口的输入验证一致性"""
        # 测试所有接口对无效输入的处理
        invalid_inputs = [
            "",  # 空字符串
            "短",  # 太短的文本（< 10字符）
            "   ",  # 仅空格
        ]

        for invalid_input in invalid_inputs:
            # 测试非流式接口
            with pytest.raises(ValueError, match="输入验证失败"):
                await document_processor.process_from_text(invalid_input)

            with pytest.raises(ValueError, match="输入验证失败"):
                await document_processor.process_from_content(invalid_input)

            # 测试流式接口
            with pytest.raises(ValueError, match="输入验证失败"):
                async for chunk in document_processor.process_from_text_stream(
                    invalid_input
                ):
                    pass

            with pytest.raises(ValueError, match="输入验证失败"):
                async for chunk in document_processor.process_from_content_stream(
                    invalid_input
                ):
                    pass

    @pytest.mark.asyncio
    async def test_image_processing_integration(self):
        """测试图像处理的集成功能"""
        mock_image = Image.from_url("https://example.com/test-document.png")

        # 测试非流式图像处理
        result = await document_processor.process_from_image(mock_image)

        assert isinstance(result, Document)
        assert result.category == "图像文档"
        assert result.original_content == "image_content"
        assert result.word_count == 0

        # 测试流式图像处理
        chunks = []
        async for chunk in document_processor.process_from_image_stream(mock_image):
            chunks.append(chunk)

        assert len(chunks) > 0

        # 测试通用接口的图像处理
        result2 = await document_processor.process_from_content(mock_image)
        assert result2.category == result.category

    @pytest.mark.asyncio
    async def test_preprocessing_and_postprocessing_integration(self):
        """测试预处理和后处理的集成效果"""
        # 使用包含多余空白字符的文本
        messy_text = "  这是一个   包含很多    空白字符的    测试文档内容。  "

        result = await document_processor.process_from_text(messy_text)

        # 验证预处理效果（原始内容应该保持不变，但处理过程中会被清理）
        assert result.original_content == messy_text

        # 验证后处理效果（无标签的章节应该有默认标签）
        for section in result.sections:
            assert len(section.tags) > 0
            if not any(tag != "未分类" for tag in section.tags):
                # 如果只有默认标签，说明后处理生效了
                assert "未分类" in section.tags

    @pytest.mark.asyncio
    async def test_comprehensive_workflow(self):
        """测试完整工作流程"""
        # 准备测试数据
        test_scenarios = [
            {
                "name": "会议纪要",
                "content": "今天下午2点举行了季度总结会议，参与人员包括各部门负责人。会议回顾了本季度的工作成果，讨论了下季度的工作计划。",
                "expected_category": "会议纪要",
            },
            {
                "name": "技术报告",
                "content": "系统性能分析报告：经过一周的监控，发现API响应时间平均为200ms。建议优化数据库查询语句，预计可提升30%性能。",
                "expected_category": "报告文档",
            },
            {
                "name": "项目计划",
                "content": "新产品开发计划：第一阶段进行市场调研，预计2个月完成。第二阶段产品设计，预计3个月。第三阶段开发实施。",
                "expected_category": "计划文档",
            },
        ]

        for scenario in test_scenarios:
            # 非流式处理
            result = await document_processor.process_from_text(scenario["content"])

            # 验证基本结果
            assert isinstance(result, Document)
            assert result.category == scenario["expected_category"]
            assert result.original_content == scenario["content"]
            assert len(result.sections) > 0

            # 流式处理
            chunks = []
            async for chunk in document_processor.process_from_text_stream(
                scenario["content"]
            ):
                chunks.append(chunk)

            # 验证流式结果
            assert len(chunks) > 0
            final_chunk = chunks[-1]

            # 验证流式和非流式的一致性
            if final_chunk.word_count is not None:
                assert final_chunk.word_count == result.word_count

    def test_module_exports(self):
        """测试模块导出的一致性"""
        # 验证主模块的导出
        assert LLMContentProcessor is not None

        # 验证示例模块的导出
        from src.common.streaming_output.document_example import (
            document_processor,
            DocumentProcessor,
        )

        assert document_processor is not None
        assert DocumentProcessor is not None
        assert isinstance(document_processor, DocumentProcessor)

    @pytest.mark.asyncio
    async def test_memory_and_resource_management(self):
        """测试内存和资源管理"""
        import gc

        # 记录初始状态
        initial_objects = len(gc.get_objects())

        # 处理多个文档
        for i in range(10):
            content = f"这是第{i}个测试文档，用于验证内存管理。内容足够长以进行有效的处理和分析。"

            # 非流式处理
            result = await document_processor.process_from_text(content)
            assert isinstance(result, Document)

            # 流式处理
            chunk_count = 0
            async for chunk in document_processor.process_from_text_stream(content):
                chunk_count += 1
            assert chunk_count > 0

        # 强制垃圾回收
        gc.collect()

        # 检查内存泄漏（允许一定的内存增长）
        final_objects = len(gc.get_objects())
        growth_ratio = (final_objects - initial_objects) / initial_objects

        # 内存增长应该在合理范围内（允许50%的增长）
        assert growth_ratio < 0.5, f"内存增长过多: {growth_ratio:.2%}"
