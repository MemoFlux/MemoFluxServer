"""
信息管理核心模块的测试文件
"""

import pytest
from unittest.mock import AsyncMock, patch
from typing import List

from baml_py import Image

from src.information.core import InformationCore
from src.baml_client.types import (
    Information as BamlInformation,
    InfromationItem,
    PostType,
)


@pytest.mark.asyncio
async def test_get_information_from_text():
    """测试使用文本输入获取信息的功能"""
    # 创建模拟的 BAML 返回结果
    mock_baml_information_item = InfromationItem(
        header="Python测试", content="Python是一种编程语言"
    )

    mock_baml_information = BamlInformation(
        title="Python信息",
        information_items=[mock_baml_information_item],
        post_type=PostType.LIFE_POST,
        summary="这是关于Python的信息",
        tags=["编程", "Python"],
    )

    # 创建 InformationCore 实例
    information_core = InformationCore()

    # 使用 patch 来模拟 call_llm 函数
    with patch(
        "src.information.core.call_llm",
        new=AsyncMock(return_value=mock_baml_information),
    ):
        # 调用 get_information_from_text 方法
        tag: List[str] = []
        result = await information_core.get_information_from_text(
            "请告诉我关于Python的信息", tag
        )

        # 验证结果
        assert result.title == "Python信息"
        assert len(result.information_items) == 1
        assert result.information_items[0].header == "Python测试"
        assert result.category == "请告诉我关于Python的信息"
        assert result.post_type == PostType.LIFE_POST


@pytest.mark.asyncio
async def test_get_information_from_image():
    """测试使用图像输入获取信息的功能"""
    # 创建模拟的 BAML 返回结果
    mock_baml_information_item = InfromationItem(
        header="图像识别", content="图像识别是AI的一个重要应用"
    )

    mock_baml_information = BamlInformation(
        title="AI信息",
        information_items=[mock_baml_information_item],
        post_type=PostType.SCENE_POST,
        summary="这是关于AI的信息",
        tags=["AI", "图像处理"],
    )

    # 创建 InformationCore 实例
    information_core = InformationCore()

    # 创建一个模拟的图像对象
    mock_image = Image.from_url("file:///tmp/mock_image.png")

    # 使用 patch 来模拟 call_llm 函数
    with patch(
        "src.information.core.call_llm",
        new=AsyncMock(return_value=mock_baml_information),
    ):
        # 调用 get_information_from_image 方法
        tag: List[str] = []
        result = await information_core.get_information_from_image(mock_image, tag)

        # 验证结果
        assert result.title == "AI信息"
        assert len(result.information_items) == 1
        assert result.information_items[0].header == "图像识别"
        assert result.category == "image_content"
        assert result.post_type == PostType.SCENE_POST


@pytest.mark.asyncio
async def test_get_information_from_content_text():
    """测试使用文本内容获取信息的功能"""
    # 创建模拟的 BAML 返回结果
    mock_baml_information_item = InfromationItem(
        header="文本处理", content="文本处理是自然语言处理的基础"
    )

    mock_baml_information = BamlInformation(
        title="NLP信息",
        information_items=[mock_baml_information_item],
        post_type=PostType.LIFE_POST,
        summary="这是关于NLP的信息",
        tags=["NLP", "文本"],
    )

    # 创建 InformationCore 实例
    information_core = InformationCore()

    # 使用 patch 来模拟 call_llm 函数
    with patch(
        "src.information.core.call_llm",
        new=AsyncMock(return_value=mock_baml_information),
    ):
        # 调用 get_information_from_content 方法，传入文本
        tag: List[str] = []
        result = await information_core.get_information_from_content(
            "请告诉我关于文本处理的信息", tag
        )

        # 验证结果
        assert result.title == "NLP信息"
        assert len(result.information_items) == 1
        assert result.information_items[0].header == "文本处理"
        assert result.category == "请告诉我关于文本处理的信息"
        assert result.post_type == PostType.LIFE_POST


@pytest.mark.asyncio
async def test_get_information_from_content_image():
    """测试使用图像内容获取信息的功能"""
    # 创建模拟的 BAML 返回结果
    mock_baml_information_item = InfromationItem(
        header="图像分析", content="图像分析可以帮助理解图片内容"
    )

    mock_baml_information = BamlInformation(
        title="图像信息",
        information_items=[mock_baml_information_item],
        post_type=PostType.FOOD_POST,
        summary="这是关于图像的信息",
        tags=["图像", "分析"],
    )

    # 创建 InformationCore 实例
    information_core = InformationCore()

    # 创建一个模拟的图像对象
    mock_image = Image.from_url("file:///tmp/mock_image.png")

    # 使用 patch 来模拟 call_llm 函数
    with patch(
        "src.information.core.call_llm",
        new=AsyncMock(return_value=mock_baml_information),
    ):
        # 调用 get_information_from_content 方法，传入图像
        tag: List[str] = []
        result = await information_core.get_information_from_content(mock_image, tag)

        # 验证结果
        assert result.title == "图像信息"
        assert len(result.information_items) == 1
        assert result.information_items[0].header == "图像分析"
        assert result.category == "image_content"
        assert result.post_type == PostType.FOOD_POST


@pytest.mark.asyncio
async def test_convert_baml_to_schema():
    """测试 _convert_baml_to_schema 方法"""
    # 创建模拟的 BAML 返回结果
    mock_baml_information_item = InfromationItem(
        header="转换测试", content="测试BAML到Schema的转换"
    )

    mock_baml_information = BamlInformation(
        title="转换测试信息",
        information_items=[mock_baml_information_item],
        post_type=PostType.OTHER_POST,
        summary="这是关于转换测试的信息",
        tags=["测试", "转换"],
    )

    # 创建 InformationCore 实例
    information_core = InformationCore()

    # 调用 _convert_baml_to_schema 方法
    result = information_core._convert_baml_to_schema(mock_baml_information, "测试分类")

    # 验证结果
    assert result.title == "转换测试信息"
    assert len(result.information_items) == 1
    assert result.information_items[0].header == "转换测试"
    assert result.category == "测试分类"
    assert result.post_type == PostType.OTHER_POST
    assert result.tags == ["测试", "转换"]


@pytest.mark.asyncio
async def test_empty_information():
    """测试处理空信息内容的情况"""
    # 创建空的信息内容
    mock_baml_information = BamlInformation(
        title="",
        information_items=[],
        post_type=PostType.OTHER_POST,
        summary="",
        tags=[],
    )

    # 创建 InformationCore 实例
    information_core = InformationCore()

    # 使用 patch 来模拟 call_llm 函数
    with patch(
        "src.information.core.call_llm",
        new=AsyncMock(return_value=mock_baml_information),
    ):
        # 调用 get_information_from_text 方法
        tag: List[str] = []
        result = await information_core.get_information_from_text(
            "这是一段没有信息内容的文本", tag
        )

        # 验证结果
        assert result.title == ""
        assert len(result.information_items) == 0
        assert result.category == "这是一段没有信息内容的文本"
