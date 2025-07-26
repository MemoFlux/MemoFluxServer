"""
PartialStreamingInformation 测试
"""

import pytest

from src.information_streaming.schemas import PartialStreamingInformation


def test_partial_streaming_information_with_none_tags():
    """测试 PartialStreamingInformation 处理 tags 为 None 的情况"""
    partial_information = PartialStreamingInformation(
        title={"value": "测试标题", "state": "Complete"},
        information_items={"value": [], "state": "Complete"},
        post_type="OTHER_POST",
        summary={"value": "测试摘要", "state": "Complete"},
        tags=None  # None 值
    )
    
    # 验证 None 值被正确转换为空列表
    assert partial_information.tags == []


def test_partial_streaming_information_with_valid_tags():
    """测试 PartialStreamingInformation 处理有效 tags 值"""
    partial_information = PartialStreamingInformation(
        title={"value": "测试标题", "state": "Complete"},
        information_items={"value": [], "state": "Complete"},
        post_type="OTHER_POST",
        summary={"value": "测试摘要", "state": "Complete"},
        tags=["标签1", "标签2"]
    )
    
    # 验证值保持不变
    assert partial_information.tags == ["标签1", "标签2"]