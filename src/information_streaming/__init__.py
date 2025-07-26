"""
信息管理流式处理模块

该模块基于 LLMContentProcessor 抽象基类，提供了完整的信息结构化功能，
支持文本和图像输入，以及流式和非流式处理模式。

公开接口:
- InformationProcessor: 信息处理器类
- information_processor: 信息处理器实例
"""

from .processor import InformationProcessor, information_processor

__all__ = ["InformationProcessor", "information_processor"]
