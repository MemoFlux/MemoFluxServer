"""
信息管理模块的核心实现

该模块负责根据用户输入的文本或图像生成结构化的信息。

公开接口:
- InformationCore: 实现 InformationInterface 的核心类，提供 get_information_from_text 和 get_information_from_image 方法

内部方法:
- _convert_baml_to_schema: 将 BAML 的 Information 模型转换为本地 Schema 模型
"""

from typing import Union, List

from baml_py import Image

from src.information.interface import InformationInterface
from src.information.schemas import InformationRes
from src.baml_client.types import Information
from src.information.utils import call_llm



class InformationCore(InformationInterface):
    """信息管理核心实现类"""

    async def get_information_from_text(self, text: str, tag: List[str]) -> InformationRes:
        """
        根据输入文本生成结构化信息
        
        Args:
            text: 用户输入的文本内容
            tag: 信息标签列表
            
        Returns:
            InformationRes: 结构化的信息对象
        """
        # 调用 LLM 生成信息
        knowledge = await call_llm(text, tag)
        
        # 转换为本地 Schema 模型
        knowledgeRes = self._convert_baml_to_schema(knowledge, text)

        return knowledgeRes

    async def get_information_from_image(self, image: Image, tag: List[str]) -> InformationRes:
        """
        根据输入图像生成结构化信息
        
        Args:
            image: 用户输入的图像
            tag: 信息标签列表
            
        Returns:
            InformationRes: 结构化的信息对象
        """
        # 调用 LLM 生成信息
        knowledge = await call_llm(image, tag)
        
        # 转换为本地 Schema 模型
        knowledgeRes = self._convert_baml_to_schema(knowledge, "image_content")
        
        return knowledgeRes

    async def get_information_from_content(self, content: Union[str, Image], tag: List[str]) -> InformationRes:
        """
        根据输入内容（文本或图像）生成结构化信息
        
        Args:
            content: 用户输入的内容（文本或图像）
            tag: 信息标签列表
            
        Returns:
            InformationRes: 结构化的信息对象
        """
        if isinstance(content, str):
            return await self.get_information_from_text(content, tag)
        else:
            return await self.get_information_from_image(content, tag)

    def _convert_baml_to_schema(self, meta: Information, category: str) -> InformationRes:
        """
        将 BAML 的 Information 模型转换为本地 Schema 模型
        
        Args:
            meta: BAML 生成的信息对象
            category: 信息分类
            
        Returns:
            InformationRes: 转换后的本地信息对象
        """
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
