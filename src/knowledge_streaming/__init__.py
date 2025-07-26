"""
知识管理流式处理模块

该模块基于 LLMContentProcessor 抽象基类，提供了完整的知识结构化功能，
支持文本和图像输入，以及流式和非流式处理模式。

公开接口:
- KnowledgeProcessor: 知识处理器类
- knowledge_processor: 知识处理器实例
"""

from .processor import KnowledgeProcessor, knowledge_processor

__all__ = ["KnowledgeProcessor", "knowledge_processor"]