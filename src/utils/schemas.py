from typing import List
from pydantic import BaseModel


class JinaEmbeddingData(BaseModel):
    object: str
    index: int
    embedding: list[float]
    
class JinaUsage(BaseModel):
    total_tokens: int
    
class JinaEmbeddingResponse(BaseModel):
    model: str
    object: str
    usage: JinaUsage
    data: List[JinaEmbeddingData]