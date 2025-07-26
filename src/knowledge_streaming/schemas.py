"""
知识管理模块的数据模型

该文件定义了知识管理模块使用的 Pydantic 数据模型，包括最终的 Knowledge 和 KnowledgeItem 类型，
以及流式处理中使用的 PartialStreamingKnowledge 类型。

公开接口:
- KnowledgeItem: 知识项数据模型
- Knowledge: 知识数据模型
- PartialStreamingKnowledge: 流式知识数据模型
- StreamState: 流式状态包装器
"""

import uuid
from typing import List, Optional, Literal, Generic, TypeVar
from pydantic import BaseModel, Field

# 从 BAML 导入原始类型
from src.baml_client.types import Knowledge as BamlKnowledge, KnowledgeItem as BamlKnowledgeItem
from src.baml_client.stream_types import StreamingKnowledge as BamlStreamingKnowledge

# 重建 BAML 模型以解决依赖关系
BamlKnowledgeItem.model_rebuild()
BamlKnowledge.model_rebuild()

# 定义泛型类型变量
T_co = TypeVar('T_co', covariant=True)


class StreamState(BaseModel, Generic[T_co]):
    """
    包裹流式字段的状态机，用于模拟 BAML 的流式状态
    """
    value: T_co
    state: Literal["Pending", "Incomplete", "Complete", "Error"]


class KnowledgeItem(BamlKnowledgeItem):
    """知识项数据模型"""
    pass


class Knowledge(BamlKnowledge):
    """
    知识数据模型
    
    这是经过完整处理和验证后，应用逻辑中使用的对象。
    """
    category: str = Field(default="", description="知识分类")


# 重建模型以解决依赖关系
KnowledgeItem.model_rebuild()
BamlKnowledge.model_rebuild()
Knowledge.model_rebuild()


# 以下是流式处理中使用的部分类型（由 BAML 自动生成）
class PartialStreamingKnowledge(BamlStreamingKnowledge):
    """
    流式知识处理的部分类型
    
    这是在流式处理过程中，每个数据块的实际类型。
    直接继承 BAML 自动生成的 StreamingKnowledge 类型，保持完全兼容。
    """
    
    def __init__(self, **kwargs):
        """
        自定义初始化方法，处理可能为 None 的字段
        
        BAML 流式处理中，某些标记为 @stream.done 的数组字段可能在中间状态时为 None。
        我们在这里将 None 值转换为空列表，以符合最终的数据模型期望。
        """
        # 处理 related_items 字段
        if 'related_items' in kwargs and kwargs['related_items'] is None:
            kwargs['related_items'] = []
        
        # 处理 tags 字段
        if 'tags' in kwargs and kwargs['tags'] is None:
            kwargs['tags'] = []
            
        # 调用父类的初始化方法
        super().__init__(**kwargs)
    
    @classmethod
    def model_validate(cls, obj, **kwargs):
        """
        重写模型验证方法，在验证前处理 None 值
        """
        if isinstance(obj, dict):
            # 处理字典形式的输入
            obj = obj.copy()  # 避免修改原始对象
            if obj.get('related_items') is None:
                obj['related_items'] = []
            if obj.get('tags') is None:
                obj['tags'] = []
        
        return super().model_validate(obj, **kwargs)


# 重建流式模型
PartialStreamingKnowledge.model_rebuild()