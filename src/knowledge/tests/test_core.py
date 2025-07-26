"""
知识管理核心模块的测试文件
"""

import pytest
from unittest.mock import AsyncMock, patch
from typing import List

from baml_py import Image

from src.knowledge.core import KnowledgeCore
from src.baml_client.types import (
    Knowledge as BamlKnowledge,
    KnowledgeItem,
    Node,
    RelationShip,
)


@pytest.mark.asyncio
async def test_get_knowledge_from_text():
    """测试使用文本输入获取知识的功能"""
    # 创建模拟的 BAML 返回结果
    mock_node = Node(targert_id=1, relationship=RelationShip.PARENT)

    mock_baml_knowledge_item = KnowledgeItem(
        id=1, header="Python测试", content="Python是一种编程语言", node=mock_node
    )

    mock_baml_knowledge = BamlKnowledge(
        title="Python知识",
        knowledge_items=[mock_baml_knowledge_item],
        tags=["编程", "Python"],
        related_items=[],
    )

    # 创建 KnowledgeCore 实例
    knowledge_core = KnowledgeCore()

    # 使用 patch 来模拟 call_llm 函数
    with patch(
        "src.knowledge.core.call_llm", new=AsyncMock(return_value=mock_baml_knowledge)
    ):
        # 调用 get_knowledge_from_text 方法
        tag: List[str] = []
        result = await knowledge_core.get_knowledge_from_text(
            "请告诉我关于Python的知识", tag
        )

        # 验证结果
        assert result.title == "Python知识"
        assert len(result.knowledge_items) == 1
        assert result.knowledge_items[0].header == "Python测试"
        assert result.category == "请告诉我关于Python的知识"


@pytest.mark.asyncio
async def test_get_knowledge_from_image():
    """测试使用图像输入获取知识的功能"""
    # 创建模拟的 BAML 返回结果
    mock_node = Node(targert_id=2, relationship=RelationShip.CHILD)

    mock_baml_knowledge_item = KnowledgeItem(
        id=2, header="图像识别", content="图像识别是AI的一个重要应用", node=mock_node
    )

    mock_baml_knowledge = BamlKnowledge(
        title="AI知识",
        knowledge_items=[mock_baml_knowledge_item],
        tags=["AI", "图像处理"],
        related_items=[],
    )

    # 创建 KnowledgeCore 实例
    knowledge_core = KnowledgeCore()

    # 创建一个模拟的图像对象
    mock_image = Image.from_url("file:///tmp/mock_image.png")

    # 使用 patch 来模拟 call_llm 函数
    with patch(
        "src.knowledge.core.call_llm", new=AsyncMock(return_value=mock_baml_knowledge)
    ):
        # 调用 get_knowledge_from_image 方法
        tag: List[str] = []
        result = await knowledge_core.get_knowledge_from_image(mock_image, tag)

        # 验证结果
        assert result.title == "AI知识"
        assert len(result.knowledge_items) == 1
        assert result.knowledge_items[0].header == "图像识别"
        assert result.category == "image_content"


@pytest.mark.asyncio
async def test_get_knowledge_from_content_text():
    """测试使用文本内容获取知识的功能"""
    # 创建模拟的 BAML 返回结果
    mock_node = Node(targert_id=3, relationship=RelationShip.PARENT)

    mock_baml_knowledge_item = KnowledgeItem(
        id=3, header="文本处理", content="文本处理是自然语言处理的基础", node=mock_node
    )

    mock_baml_knowledge = BamlKnowledge(
        title="NLP知识",
        knowledge_items=[mock_baml_knowledge_item],
        tags=["NLP", "文本"],
        related_items=[],
    )

    # 创建 KnowledgeCore 实例
    knowledge_core = KnowledgeCore()

    # 使用 patch 来模拟 call_llm 函数
    with patch(
        "src.knowledge.core.call_llm", new=AsyncMock(return_value=mock_baml_knowledge)
    ):
        # 调用 get_knowledge_from_content 方法，传入文本
        tag: List[str] = []
        result = await knowledge_core.get_knowledge_from_content(
            "请告诉我关于文本处理的知识", tag
        )

        # 验证结果
        assert result.title == "NLP知识"
        assert len(result.knowledge_items) == 1
        assert result.knowledge_items[0].header == "文本处理"
        assert result.category == "请告诉我关于文本处理的知识"


@pytest.mark.asyncio
async def test_get_knowledge_from_content_image():
    """测试使用图像内容获取知识的功能"""
    # 创建模拟的 BAML 返回结果
    mock_node = Node(targert_id=4, relationship=RelationShip.CHILD)

    mock_baml_knowledge_item = KnowledgeItem(
        id=4, header="图像分析", content="图像分析可以帮助理解图片内容", node=mock_node
    )

    mock_baml_knowledge = BamlKnowledge(
        title="图像知识",
        knowledge_items=[mock_baml_knowledge_item],
        tags=["图像", "分析"],
        related_items=[],
    )

    # 创建 KnowledgeCore 实例
    knowledge_core = KnowledgeCore()

    # 创建一个模拟的图像对象
    mock_image = Image.from_url("file:///tmp/mock_image.png")

    # 使用 patch 来模拟 call_llm 函数
    with patch(
        "src.knowledge.core.call_llm", new=AsyncMock(return_value=mock_baml_knowledge)
    ):
        # 调用 get_knowledge_from_content 方法，传入图像
        tag: List[str] = []
        result = await knowledge_core.get_knowledge_from_content(mock_image, tag)

        # 验证结果
        assert result.title == "图像知识"
        assert len(result.knowledge_items) == 1
        assert result.knowledge_items[0].header == "图像分析"
        assert result.category == "image_content"


@pytest.mark.asyncio
async def test_convert_baml_to_schema():
    """测试 _convert_baml_to_schema 方法"""
    # 创建模拟的 BAML 返回结果
    mock_node = Node(targert_id=5, relationship=RelationShip.PARENT)

    mock_baml_knowledge_item = KnowledgeItem(
        id=5, header="转换测试", content="测试BAML到Schema的转换", node=mock_node
    )

    mock_baml_knowledge = BamlKnowledge(
        title="转换测试知识",
        knowledge_items=[mock_baml_knowledge_item],
        tags=["测试", "转换"],
        related_items=[],
    )

    # 创建 KnowledgeCore 实例
    knowledge_core = KnowledgeCore()

    # 调用 _convert_baml_to_schema 方法
    result = knowledge_core._convert_baml_to_schema(mock_baml_knowledge, "测试分类")

    # 验证结果
    assert result.title == "转换测试知识"
    assert len(result.knowledge_items) == 1
    assert result.knowledge_items[0].header == "转换测试"
    assert result.category == "测试分类"
    assert result.tags == ["测试", "转换"]


@pytest.mark.asyncio
async def test_empty_knowledge():
    """测试处理空知识内容的情况"""
    # 创建空的知识内容
    mock_baml_knowledge = BamlKnowledge(
        title="", knowledge_items=[], tags=[], related_items=[]
    )

    # 创建 KnowledgeCore 实例
    knowledge_core = KnowledgeCore()

    # 使用 patch 来模拟 call_llm 函数
    with patch(
        "src.knowledge.core.call_llm", new=AsyncMock(return_value=mock_baml_knowledge)
    ):
        # 调用 get_knowledge_from_text 方法
        tag: List[str] = []
        result = await knowledge_core.get_knowledge_from_text(
            "这是一段没有知识内容的文本", tag
        )

        # 验证结果
        assert result.title == ""
        assert len(result.knowledge_items) == 0
