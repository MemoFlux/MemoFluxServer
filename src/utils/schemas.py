from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel
from qdrant_client.http import models as rest


class JinaTextInput(BaseModel):
    text: str


class JinaImageInput(BaseModel):
    image: str


JinaEmbeddingInput = Union[str, JinaTextInput, JinaImageInput]


class JinaEmbeddingData(BaseModel):
    object: str
    embedding: List[float]
    index: int


class JinaEmbeddingUsage(BaseModel):
    total_tokens: int


class JinaEmbeddingResponse(BaseModel):
    object: str
    data: List[JinaEmbeddingData]
    model: str
    usage: JinaEmbeddingUsage


class VectorSearchResult(BaseModel):
    score: float
    payload: Optional[Dict[str, Any]] = None

    @classmethod
    def from_scored_point(cls, scored_point: rest.ScoredPoint) -> "VectorSearchResult":
        return cls(
            score=scored_point.score,
            payload=scored_point.payload,
        )
