from abc import abstractmethod
from src.baml_client.types import Knowledge
from baml_py import Image
from typing import List


class KnowledgeInterface:
    """
    知识管理模块的接口定义

    定义了知识管理模块的核心接口，包括从文本和图像中提取知识的方法。
    """

    @abstractmethod
    async def get_knowledge_from_text(self, text: str, tag: List[str]) -> Knowledge:
        """
        从文本中提取知识的抽象方法

        Args:
            text: 输入的文本内容
            tag: 标签列表

        Returns:
            Knowledge: 提取的知识结构
        """
        pass

    @abstractmethod
    async def get_knowledge_from_image(self, image: Image, tag: List[str]) -> Knowledge:
        """
        从图像中提取知识的抽象方法

        Args:
            image: 输入的图像
            tag: 标签列表

        Returns:
            Knowledge: 提取的知识结构
        """
        pass
