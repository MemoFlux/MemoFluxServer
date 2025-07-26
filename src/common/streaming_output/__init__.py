"""
统一的流式输出处理模块

该模块提供了统一的抽象基类，用于标准化不同模块的 LLM 内容处理接口。
支持流式和非流式处理，提供一致的错误处理和日志记录。

公开接口:
- LLMContentProcessor: 抽象基类，定义了统一的处理接口
"""

from .base import LLMContentProcessor

__all__ = ["LLMContentProcessor"]