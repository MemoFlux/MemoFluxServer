"""
日程管理流式处理模块

该模块基于 LLMContentProcessor 抽象基类，提供了完整的日程管理功能，
支持文本和图像输入，以及流式和非流式处理模式。

公开接口:
- ScheduleProcessor: 日程处理器类
- schedule_processor: 日程处理器实例
"""

from .processor import ScheduleProcessor, schedule_processor

__all__ = ["ScheduleProcessor", "schedule_processor"]
