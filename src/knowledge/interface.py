from abc import abstractmethod
from src.baml_client.types import Knowledge
from baml_py import Image


class KnowledgeInterface:
    """
    Schema for knowledge data.
    """
    @abstractmethod
    async def get_knowledge_from_text(self, text: str) -> Knowledge:
        pass
    
    @abstractmethod
    async def get_knowledge_from_image(self, image: Image) -> Knowledge:
        # Implementation of the function to retrieve knowledge
        pass