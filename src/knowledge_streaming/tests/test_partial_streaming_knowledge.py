"""
PartialStreamingKnowledge 测试
"""

from src.knowledge_streaming.schemas import PartialStreamingKnowledge


def test_partial_streaming_knowledge_with_none_values():
    """测试 PartialStreamingKnowledge 处理 None 值"""
    # 测试 related_items 为 None 的情况
    partial_knowledge = PartialStreamingKnowledge(
        title={"value": "测试标题", "state": "Complete"},
        knowledge_items={"value": [], "state": "Complete"},
        related_items=None,  # None 值
        tags=["测试标签"],
    )

    # 验证 None 值被正确转换为空列表
    assert partial_knowledge.related_items == []
    assert partial_knowledge.tags == ["测试标签"]


def test_partial_streaming_knowledge_with_none_tags():
    """测试 PartialStreamingKnowledge 处理 tags 为 None 的情况"""
    partial_knowledge = PartialStreamingKnowledge(
        title={"value": "测试标题", "state": "Complete"},
        knowledge_items={"value": [], "state": "Complete"},
        related_items=["相关知识"],
        tags=None,  # None 值
    )

    # 验证 None 值被正确转换为空列表
    assert partial_knowledge.related_items == ["相关知识"]
    assert partial_knowledge.tags == []


def test_partial_streaming_knowledge_with_valid_values():
    """测试 PartialStreamingKnowledge 处理有效值"""
    partial_knowledge = PartialStreamingKnowledge(
        title={"value": "测试标题", "state": "Complete"},
        knowledge_items={"value": [], "state": "Complete"},
        related_items=["相关知识1", "相关知识2"],
        tags=["标签1", "标签2"],
    )

    # 验证值保持不变
    assert partial_knowledge.related_items == ["相关知识1", "相关知识2"]
    assert partial_knowledge.tags == ["标签1", "标签2"]
