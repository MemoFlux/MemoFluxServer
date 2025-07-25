
from abc import abstractmethod
from typing import List
from src.information.schemas import InformationRes
from baml_py import Image

class InformationInterface:
    """
    信息处理接口
    
    定义了信息处理模块的公共接口，包括文本信息处理和图像信息处理
    """
    
    @abstractmethod
    async def get_information_from_text(self, text: str, tag: List[str]) -> InformationRes:
        """
        处理文本信息并生成结构化信息
        
        Args:
            text: 输入的文本内容
            tag: 信息标签列表
            
        Returns:
            InformationRes: 结构化的信息对象
        """
        pass
    
    @abstractmethod
    async def get_information_from_image(self, image: Image, tag: List[str]) -> InformationRes:
        """
        处理图像信息并生成结构化信息
        
        Args:
            image: 输入的图像对象
            tag: 信息标签列表
            
        Returns:
            InformationRes: 结构化的信息对象
        """
        pass
