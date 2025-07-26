"""
日程管理流式处理器

该模块实现了基于 LLMContentProcessor 的日程管理处理器，支持文本和图像输入，
以及流式和非流式处理模式。

公开接口:
- ScheduleProcessor: 继承 LLMContentProcessor 的日程处理器
- schedule_processor: 日程处理器的全局实例

内部方法:
- _call_llm: 调用日程管理的 BAML 函数
- _call_llm_stream: 调用日程流式管理的 BAML 函数
- _convert_to_schema: 将 BAML 结果转换为 Schedule 对象

数据流:
输入内容 -> 日程分析 -> 任务提取 -> 分类识别 -> Schedule 对象
"""

import uuid
from typing import Union, AsyncGenerator, Any
from baml_py import Image

from src.common.streaming_output.base import LLMContentProcessor
from src.baml_client.async_client import b
from src.baml_client.types import Schedule as BamlSchedule, StreamingSchedule as BamlStreamingSchedule
from .schemas import Schedule, Task, PartialStreamingSchedule


class ScheduleProcessor(LLMContentProcessor[Schedule, PartialStreamingSchedule]):
    """
    日程管理处理器
    
    继承自 LLMContentProcessor，实现了日程内容的分析和结构化处理。
    支持从文本和图像中提取日程结构，生成结构化的日程安排。
    """
    
    def __init__(self, logger_name: str = "ScheduleProcessor"):
        """
        初始化日程管理处理器
        
        Args:
            logger_name: 日志器名称
        """
        super().__init__(logger_name)
    
    async def _call_llm(self, content: Union[str, Image], **kwargs) -> BamlSchedule:
        """
        调用日程管理的 BAML 函数
        
        Args:
            content: 输入内容（文本或图像）
            **kwargs: 额外参数
            
        Returns:
            BamlSchedule: BAML 生成的日程对象
        """
        self.logger.info("调用 LLM 进行日程分析")
        
        # 调用 BAML 的 ScheduleManager 函数
        result = await b.ScheduleManager(content=content)
        
        return result
    
    async def _call_llm_stream(self, content: Union[str, Image], **kwargs) -> AsyncGenerator[PartialStreamingSchedule, None]:
        """
        调用日程流式管理的 BAML 函数
        
        Args:
            content: 输入内容（文本或图像）
            **kwargs: 额外参数
            
        Yields:
            PartialStreamingSchedule: 流式日程分析结果
        """
        self.logger.info("开始流式日程分析")
        
        # 调用 BAML 的 ScheduleManagerStream 函数
        stream = b.stream.ScheduleManagerStream(content=content)
        async for partial in stream:
            # 将 BAML 流式结果转换为 PartialStreamingSchedule
            yield PartialStreamingSchedule(**partial.model_dump())
    
    def _convert_to_schema(self, baml_result: BamlSchedule, original_content: str, **kwargs) -> Schedule:
        """
        将 BAML 结果转换为 Schedule Schema
        
        Args:
            baml_result: BAML 返回的日程分析结果
            original_content: 原始输入内容的字符串表示
            **kwargs: 额外参数
            
        Returns:
            Schedule: 转换后的日程对象
        """
        self.logger.info("转换 BAML 结果为 Schedule Schema")
        
        # 转换任务列表，添加 ID
        tasks = []
        for i, baml_task in enumerate(baml_result.tasks):
            task = Task(
                id=i,
                start_time=baml_task.start_time,
                end_time=baml_task.end_time,
                people=baml_task.people,
                theme=baml_task.theme,
                core_tasks=baml_task.core_tasks,
                position=baml_task.position,
                tags=baml_task.tags,
                category=baml_task.category,
                suggested_actions=baml_task.suggested_actions
            )
            tasks.append(task)
        
        # 创建 Schedule 对象
        schedule = Schedule(
            id=str(uuid.uuid4()),
            title=baml_result.title,
            category=baml_result.category,
            tasks=tasks,
            text=original_content
        )
        
        return schedule
    
    def _validate_input(self, content: Union[str, Image], **kwargs) -> bool:
        """
        重写输入验证逻辑
        
        对于日程处理，我们要求文本长度至少为5个字符。
        
        Args:
            content: 输入内容
            **kwargs: 额外参数
            
        Returns:
            bool: 验证是否通过
        """
        if isinstance(content, str):
            return len(content.strip()) >= 5
        return content is not None
    
    def _preprocess_content(self, content: Union[str, Image], **kwargs) -> Union[str, Image]:
        """
        重写内容预处理逻辑
        
        对文本进行基本的清理，去除多余的空白字符。
        
        Args:
            content: 原始输入内容
            **kwargs: 额外参数
            
        Returns:
            Union[str, Image]: 预处理后的内容
        """
        if isinstance(content, str):
            # 清理多余的空白字符
            cleaned = ' '.join(content.split())
            self.logger.debug(f"文本预处理：原长度 {len(content)}, 清理后长度 {len(cleaned)}")
            return cleaned
        return content


# 创建全局实例
schedule_processor = ScheduleProcessor()

__all__ = ["ScheduleProcessor", "schedule_processor"]