"""
知识管理模块的核心实现

该模块负责根据用户输入的文本或图像生成结构化的知识内容。

公开接口:
- KnowledgeCore: 实现 KnowledgeInterface 的核心类，提供 get_knowledge_from_text 和 get_knowledge_from_image 方法

内部方法:
- _convert_baml_to_schema: 将 BAML 的 Knowledge 模型转换为本地 Schema 模型
"""

from typing import Union, List

from baml_py import Image

from src.knowledge.interface import KnowledgeInterface
from src.knowledge.schemas import KnowledgeRes
from src.baml_client.types import Knowledge
from src.knowledge.utils import call_llm



class KnowledgeCore(KnowledgeInterface):
    """知识管理核心实现类"""

    async def get_knowledge_from_text(self, text: str,tag:List[str]) -> KnowledgeRes:
        """
        根据输入文本生成知识内容
        
        Args:
            text: 用户输入的文本内容
            tag: 标签列表
            
        Returns:
            KnowledgeRes: 结构化的知识对象
        """
        # 调用 LLM 生成日程
        knowledge = await call_llm(text,tag)
        
        # 转换为本地 Schema 模型
        knowledgeRes = self._convert_baml_to_schema(knowledge, text)

        return knowledgeRes

    async def get_knowledge_from_image(self, image: Image, tag: List[str]) -> KnowledgeRes:
        """
        根据输入图像生成知识内容
        
        Args:
            image: 用户输入的图像
            tag: 标签列表
            
        Returns:
            KnowledgeRes: 结构化的知识对象
        """
        # 调用 LLM 生成日程
        knowledge = await call_llm(image,tag)
        
        # 转换为本地 Schema 模型
        knowledgeRes = self._convert_baml_to_schema(knowledge, "知识")
        
        return knowledgeRes

    async def get_knowledge_from_content(self, content: Union[str, Image],tag:List[str]) -> KnowledgeRes:
        """
        根据输入内容（文本或图像）生成知识内容
        
        Args:
            content: 用户输入的内容（文本或图像）
            tag: 标签列表
            
        Returns:
            KnowledgeRes: 结构化的知识对象
        """
        if isinstance(content, str):
            return await self.get_knowledge_from_text(content,tag)
        else:
            return await self.get_knowledge_from_image(content,tag)

    def _convert_baml_to_schema(self, meta: Knowledge, category: str) -> KnowledgeRes:
        """
        将 BAML 的 Knowledge 模型转换为本地 Schema 模型
        
        Args:
            meta: BAML 生成的知识对象
            category: 知识分类
            
        Returns:
            KnowledgeRes: 转换后的本地知识对象
        """
        # 转换任务列表

        
        return KnowledgeRes(
            title=meta.title,
            knowledge_items=meta.knowledge_items,
            category=category,
            tags=meta.tags,
            related_items=meta.related_items
        )

knowledge_core = KnowledgeCore()

__all__ = ["knowledge_core"]
