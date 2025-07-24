
from abc import abstractmethod
from src.information.schemas import InformationRes
from baml_py import Image

class InformationInterface:
    """
    信息处理接口
    """
    @abstractmethod
    async def get_information_text(self, text: str, tag: list[str]) -> InformationRes:
        """
        处理文本信息并生成结构化信息
        """
        pass
    
    @abstractmethod
    async def get_information_image(self, image: Image, tag: list[str]) -> InformationRes:
        """
        处理图像信息并生成结构化信息
        """
        pass