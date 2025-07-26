"""
流式输出模块的数据模型

该文件定义了示例模块使用的 Pydantic 数据模型。

公开接口:
- Document: 文档处理结果的数据模型
- DocumentSection: 文档章节的数据模型
- PartialStreamingDocument: 流式文档数据块的模拟类型（实际应由 BAML 生成）
"""

import uuid
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Generic, TypeVar


class DocumentSection(BaseModel):
    """文档章节数据模型"""
    title: str
    content: str
    level: int = Field(default=1, description="章节层级，1为顶级章节")
    tags: List[str] = Field(default=[], description="章节标签")


class Document(BaseModel):
    """
    文档处理结果的最终数据模型
    
    这是经过完整处理和验证后，应用逻辑中使用的对象。
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    summary: str
    category: str
    sections: List[DocumentSection]
    original_content: str
    language: str = Field(default="zh", description="文档语言")
    word_count: int = Field(default=0, description="总字数")


# 以下是模拟的流式类型（实际使用中应由 BAML 自动生成）
T_co = TypeVar('T_co', covariant=True)


class StreamState(BaseModel, Generic[T_co]):
    """
    包裹流式字段的状态机，用于模拟 BAML 的流式状态
    """
    value: T_co
    state: Literal["Pending", "Incomplete", "Complete", "Error"]


class PartialDocumentSection(BaseModel):
    """流式处理中的部分章节类型"""
    title: Optional[str] = None
    content: Optional[str] = None
    level: Optional[int] = None
    tags: Optional[List[Optional[str]]] = None


class PartialStreamingDocument(BaseModel):
    """
    流式文档处理的部分类型
    
    这是在流式处理过程中，每个数据块的实际类型。
    在实际项目中，这个类型应该由 BAML 根据 .baml 文件自动生成。
    """
    title: Optional[StreamState[Optional[str]]] = None
    summary: Optional[StreamState[Optional[str]]] = None
    category: Optional[str] = None  # 假设使用 @stream.done，所以没有 StreamState
    sections: Optional[StreamState[Optional[List[Optional[PartialDocumentSection]]]]] = None
    language: Optional[str] = None
    word_count: Optional[int] = None