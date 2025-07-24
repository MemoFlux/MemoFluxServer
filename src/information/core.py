"""
日程管理模块的核心实现

该模块负责根据用户输入的文本或图像生成结构化的日程安排。

公开接口:
- ScheduleCore: 实现 ScheduleInterface 的核心类，提供 gen_schedule_from_text 和 gen_schedule_from_image 方法

内部方法:
- _convert_baml_schedule_to_schema: 将 BAML 的 Schedule 模型转换为本地 Schema 模型
"""

import uuid
from typing import Union, List

from baml_py import Image

from src.baml_client.async_client import b
from src.information.interface import InformationInterface
from src.information.schemas import InformationRes
from src.baml_client.types import Information
from src.information.utils import call_llm



class InformationCore(InformationInterface):
    """知识管理核心实现类"""

    async def get_information_from_text(self, text: str,tag:List[str]) -> InformationRes:
        """
        根据输入文本生成日程安排
        
        Args:
            text: 用户输入的文本内容
            
        Returns:
            Schedule: 结构化的日程对象
        """
        # 调用 LLM 生成日程
        knowledge = await call_llm(text,tag)
        
        # 转换为本地 Schema 模型
        knowledgeRes = self._convert_baml_to_schema(knowledge, text)

        return knowledgeRes

    async def get_information_from_image(self, image: Image, tag: List[str]) -> InformationRes:
        """
        根据输入图像生成日程安排
        
        Args:
            image: 用户输入的图像
            
        Returns:
            Schedule: 结构化的日程对象
        """
        # 调用 LLM 生成日程
        knowledge = await call_llm(image,tag)
        
        # 转换为本地 Schema 模型
        knowledgeRes = self._convert_baml_to_schema(knowledge, "image_content")
        
        return knowledgeRes

    async def get_information_from_content(self, content: Union[str, Image],tag:List[str]) -> InformationRes:
        """
        根据输入内容（文本或图像）生成日程安排
        
        Args:
            content: 用户输入的内容（文本或图像）
            
        Returns:
            Schedule: 结构化的日程对象
        """
        if isinstance(content, str):
            return await self.get_information_from_text(content,tag)
        else:
            return await self.get_information_from_image(content,tag)

    def _convert_baml_to_schema(self, meta: Information, category: str) -> InformationRes:
        """
        将 BAML 的 Schedule 模型转换为本地 Schema 模型
        
        Args:
            baml_schedule: BAML 生成的日程对象
            original_text: 原始输入文本
            
        Returns:
            Schedule: 转换后的本地日程对象
        """
        # 转换任务列表

        
        return InformationRes(
           title=meta.title,
           information_items=meta.information_items,
           post_type=meta.post_type,
           category=category,
           tags=meta.tags,
           summary=meta.summary
        )

information_core = InformationCore()

__all__ = ["information_core"]