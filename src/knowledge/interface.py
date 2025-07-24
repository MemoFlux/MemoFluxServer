from abc import abstractmethod
from baml_client.types import Knowledge
from baml_client.types import Image


class KnowledgeBase:
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