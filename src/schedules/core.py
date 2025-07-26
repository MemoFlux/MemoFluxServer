"""
日程管理模块的核心实现

该模块负责根据用户输入的文本或图像生成结构化的日程安排。

公开接口:
- ScheduleCore: 实现 ScheduleInterface 的核心类，提供 gen_schedule_from_text 和 gen_schedule_from_image 方法
- gen_schedule_from_text_stream: 流式生成日程安排（文本输入）
- gen_schedule_from_image_stream: 流式生成日程安排（图像输入）

内部方法:
- _convert_baml_schedule_to_schema: 将 BAML 的 Schedule 模型转换为本地 Schema 模型
"""

import uuid
from typing import Union

from baml_py import Image

from src.schedules.interface import ScheduleInterface
from src.schedules.schemas import Schedule, Task
from src.schedules.utils import call_llm, call_llm_stream
from src.baml_client.types import Schedule as BamlSchedule


class ScheduleCore(ScheduleInterface):
    """日程管理核心实现类"""

    async def gen_schedule_from_text(self, text: str) -> Schedule:
        """
        根据输入文本生成日程安排

        Args:
            text: 用户输入的文本内容

        Returns:
            Schedule: 结构化的日程对象
        """
        # 调用 LLM 生成日程
        baml_schedule = await call_llm(text)

        # 转换为本地 Schema 模型
        schedule = self._convert_baml_schedule_to_schema(baml_schedule, text)

        return schedule

    async def gen_schedule_from_image(self, image: Image) -> Schedule:
        """
        根据输入图像生成日程安排

        Args:
            image: 用户输入的图像

        Returns:
            Schedule: 结构化的日程对象
        """
        # 调用 LLM 生成日程
        baml_schedule = await call_llm(image)

        # 转换为本地 Schema 模型
        schedule = self._convert_baml_schedule_to_schema(baml_schedule, "image_content")

        return schedule

    async def gen_schedule_from_text_stream(self, text: str):
        """
        流式根据输入文本生成日程安排

        Args:
            text: 用户输入的文本内容

        Yields:
            StreamingSchedule: BAML 生成的流式日程对象
        """
        async for partial_data in call_llm_stream(text):
            yield partial_data

    async def gen_schedule_from_image_stream(self, image: Image):
        """
        流式根据输入图像生成日程安排

        Args:
            image: 用户输入的图像

        Yields:
            StreamingSchedule: BAML 生成的流式日程对象
        """
        async for partial_data in call_llm_stream(image):
            yield partial_data

    async def gen_schedule_from_content_stream(self, content: Union[str, Image]):
        """
        流式根据输入内容（文本或图像）生成日程安排

        Args:
            content: 用户输入的内容（文本或图像）

        Yields:
            StreamingSchedule: BAML 生成的流式日程对象
        """
        if isinstance(content, str):
            async for partial_data in self.gen_schedule_from_text_stream(content):
                yield partial_data
        else:
            async for partial_data in self.gen_schedule_from_image_stream(content):
                yield partial_data

    async def gen_schedule(self, text: str) -> Schedule:
        """
        根据输入文本生成日程安排（接口兼容方法）

        Args:
            text: 用户输入的文本内容

        Returns:
            Schedule: 结构化的日程对象
        """
        return await self.gen_schedule_from_text(text)

    async def gen_schedule_from_content(self, content: Union[str, Image]) -> Schedule:
        """
        根据输入内容（文本或图像）生成日程安排

        Args:
            content: 用户输入的内容（文本或图像）

        Returns:
            Schedule: 结构化的日程对象
        """
        if isinstance(content, str):
            return await self.gen_schedule_from_text(content)
        else:
            return await self.gen_schedule_from_image(content)

    def _convert_baml_schedule_to_schema(
        self, baml_schedule: BamlSchedule, original_content: str
    ) -> Schedule:
        """
        将 BAML 的 Schedule 模型转换为本地 Schema 模型

        Args:
            baml_schedule: BAML 生成的 Schedule 对象
            original_content: 原始输入内容

        Returns:
            Schedule: 转换后的本地 Schedule 对象
        """
        # 转换任务列表
        tasks = []
        for i, baml_task in enumerate(baml_schedule.tasks):
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
                suggested_actions=baml_task.suggested_actions,
            )
            tasks.append(task)

        # 创建 Schedule 对象
        schedule = Schedule(
            id=str(uuid.uuid4()),
            title=baml_schedule.title,
            category=baml_schedule.category,
            tasks=tasks,
            text=original_content,
        )

        return schedule


schedule_core = ScheduleCore()

__all__ = ["schedule_core"]
