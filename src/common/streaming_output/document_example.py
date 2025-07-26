"""
文档处理模块的示例实现

该模块演示如何使用抽象基类 LLMContentProcessor 来实现具体的文档处理功能。
文档处理模块负责分析输入内容并生成结构化的文档摘要。

公开接口:
- DocumentProcessor: 继承 LLMContentProcessor 的文档处理器
- document_processor: 文档处理器的全局实例

内部方法:
- _call_llm: 调用文档处理的 BAML 函数（模拟实现）
- _call_llm_stream: 调用文档流式处理的 BAML 函数（模拟实现）
- _convert_to_schema: 将 BAML 结果转换为 Document 对象

数据流:
输入内容 -> 文档分析 -> 章节提取 -> 摘要生成 -> 标签分类 -> Document 对象
"""

import uuid
from typing import Union, AsyncGenerator, Optional, List
from baml_py import Image

from .base import LLMContentProcessor
from .schemas import Document, DocumentSection, PartialStreamingDocument, StreamState


# 模拟的 BAML 返回类型
class MockBamlDocument:
    """模拟 BAML 返回的文档对象"""

    def __init__(
        self,
        title: str,
        summary: str,
        category: str,
        sections: list,
        language: str = "zh",
    ):
        self.title = title
        self.summary = summary
        self.category = category
        self.sections = sections
        self.language = language


class MockBamlDocumentSection:
    """模拟 BAML 返回的章节对象"""

    def __init__(
        self, title: str, content: str, level: int = 1, tags: Optional[List[str]] = None
    ):
        self.title = title
        self.content = content
        self.level = level
        self.tags = tags or []


class DocumentProcessor(LLMContentProcessor[Document, PartialStreamingDocument]):
    """
    文档处理器实现类

    继承自 LLMContentProcessor，实现了文档内容的分析和结构化处理。
    支持从文本和图像中提取文档结构，生成摘要和章节划分。
    """

    def __init__(self, logger_name: str = "DocumentProcessor"):
        """
        初始化文档处理器

        Args:
            logger_name: 日志器名称
        """
        super().__init__(logger_name)

    async def _call_llm(self, content: Union[str, Image], **kwargs) -> MockBamlDocument:
        """
        调用文档处理的 BAML 函数（模拟实现）

        在实际项目中，这里应该调用类似：
        from src.baml_client.async_client import b
        return await b.DocumentAnalyzer(content, **kwargs)

        Args:
            content: 输入内容
            **kwargs: 额外参数，可能包括 'language', 'detail_level' 等

        Returns:
            MockBamlDocument: 模拟的 BAML 文档分析结果
        """
        self.logger.info("调用 LLM 进行文档分析")

        # 模拟异步处理时间
        import asyncio

        await asyncio.sleep(0.1)

        # 根据输入类型生成不同的模拟结果
        if isinstance(content, str):
            # 简单的文本分析逻辑
            content_length = len(content)

            if "会议" in content or "meeting" in content.lower():
                category = "会议纪要"
                title = "会议记录分析"
            elif "报告" in content or "report" in content.lower():
                category = "报告文档"
                title = "报告内容分析"
            elif "计划" in content or "plan" in content.lower():
                category = "计划文档"
                title = "计划内容分析"
            else:
                category = "普通文档"
                title = "文档内容分析"

            # 模拟章节划分
            sentences = content.split("。")[:3]  # 取前3句作为章节
            sections = []
            for i, sentence in enumerate(sentences):
                if sentence.strip():
                    section = MockBamlDocumentSection(
                        title=f"第{i + 1}部分",
                        content=sentence.strip() + "。",
                        level=1,
                        tags=["自动生成"],
                    )
                    sections.append(section)

            summary = f"这是一份{category}，共包含{len(sections)}个主要部分，总长度{content_length}字符。"

        else:  # Image
            category = "图像文档"
            title = "图像内容分析"
            summary = "这是一份从图像中提取的文档内容。"
            sections = [
                MockBamlDocumentSection(
                    title="图像描述",
                    content="图像内容的文字描述。",
                    level=1,
                    tags=["图像分析"],
                )
            ]

        language = kwargs.get("language", "zh")

        return MockBamlDocument(
            title=title,
            summary=summary,
            category=category,
            sections=sections,
            language=language,
        )

    async def _call_llm_stream(
        self, content: Union[str, Image], **kwargs
    ) -> AsyncGenerator[PartialStreamingDocument, None]:
        """
        调用文档流式处理的 BAML 函数（模拟实现）

        在实际项目中，这里应该调用类似：
        from src.baml_client.async_client import b
        stream = b.stream.DocumentAnalyzerStream(content, **kwargs)
        async for partial in stream:
            yield partial

        Args:
            content: 输入内容
            **kwargs: 额外参数

        Yields:
            PartialStreamingDocument: 流式文档分析结果
        """
        self.logger.info("开始流式文档分析")

        import asyncio

        # 模拟流式返回过程
        # 1. 首先返回标题
        yield PartialStreamingDocument(
            title=StreamState(value="文档内容分析", state="Complete"),
            category="文档分析",
        )

        await asyncio.sleep(0.1)

        # 2. 然后返回摘要
        yield PartialStreamingDocument(
            title=StreamState(value="文档内容分析", state="Complete"),
            summary=StreamState(value="正在分析文档内容结构...", state="Incomplete"),
            category="文档分析",
        )

        await asyncio.sleep(0.1)

        # 3. 返回完整摘要
        final_summary = "文档分析完成，已识别主要结构和内容要点。"
        yield PartialStreamingDocument(
            title=StreamState(value="文档内容分析", state="Complete"),
            summary=StreamState(value=final_summary, state="Complete"),
            category="文档分析",
            language="zh",
        )

        await asyncio.sleep(0.1)

        # 4. 最后返回章节信息
        from .schemas import PartialDocumentSection

        sections: List[Optional[PartialDocumentSection]] = [
            PartialDocumentSection(
                title="主要内容",
                content="文档的核心内容描述。",
                level=1,
                tags=["核心内容"],
            )
        ]

        yield PartialStreamingDocument(
            title=StreamState(value="文档内容分析", state="Complete"),
            summary=StreamState(value=final_summary, state="Complete"),
            category="文档分析",
            sections=StreamState(value=sections, state="Complete"),
            language="zh",
            word_count=len(content) if isinstance(content, str) else 0,
        )

    def _convert_to_schema(
        self, baml_result: MockBamlDocument, original_content: str, **kwargs
    ) -> Document:
        """
        将 BAML 结果转换为 Document Schema

        Args:
            baml_result: BAML 返回的文档分析结果
            original_content: 原始输入内容的字符串表示
            **kwargs: 额外参数

        Returns:
            Document: 转换后的文档对象
        """
        self.logger.info("转换 BAML 结果为 Document Schema")

        # 转换章节列表
        sections = []
        for baml_section in baml_result.sections:
            section = DocumentSection(
                title=baml_section.title,
                content=baml_section.content,
                level=baml_section.level,
                tags=baml_section.tags,
            )
            sections.append(section)

        # 计算字数 - 如果是图像内容，字数为0
        word_count = 0 if original_content == "image_content" else len(original_content)

        # 创建 Document 对象
        document = Document(
            id=str(uuid.uuid4()),
            title=baml_result.title,
            summary=baml_result.summary,
            category=baml_result.category,
            sections=sections,
            original_content=original_content,
            language=baml_result.language,
            word_count=word_count,
        )

        return document

    def _validate_input(self, content: Union[str, Image], **kwargs) -> bool:
        """
        重写输入验证逻辑

        对于文档处理，我们要求文本长度至少为10个字符。

        Args:
            content: 输入内容
            **kwargs: 额外参数

        Returns:
            bool: 验证是否通过
        """
        if isinstance(content, str):
            return len(content.strip()) >= 10
        return content is not None

    def _preprocess_content(
        self, content: Union[str, Image], **kwargs
    ) -> Union[str, Image]:
        """
        重写内容预处理逻辑

        对文本进行基本的清理，去除多余的空白字符。

        Args:
            content: 原始输入内容
            **kwargs: 额外参数

        Returns:
            Union[str, Image]: 预处理后的内容
        """
        if isinstance(content, str):
            # 清理多余的空白字符
            cleaned = " ".join(content.split())
            return cleaned
        return content

    def _postprocess_result(self, result: Document, **kwargs) -> Document:
        """
        重写结果后处理逻辑

        为文档添加一些额外的元数据。

        Args:
            result: 转换后的文档对象
            **kwargs: 额外参数

        Returns:
            Document: 后处理后的文档对象
        """
        # 可以在这里添加一些元数据处理逻辑
        # 例如：自动为空章节添加默认标签
        for section in result.sections:
            if not section.tags:
                section.tags = ["未分类"]

        self.logger.info(
            f"文档后处理完成，标题：{result.title}，章节数：{len(result.sections)}"
        )
        return result


# 创建全局实例
document_processor = DocumentProcessor()

__all__ = ["DocumentProcessor", "document_processor"]
