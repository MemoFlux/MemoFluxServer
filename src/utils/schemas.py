from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel, Field
from qdrant_client.http import models as rest
from qdrant_client.http.models import ShardKey, OrderValue, VectorStruct


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
    id: Union[str, int]
    version: int
    score: float
    payload: Optional[Dict[str, Any]] = None
    vector: Optional[Union[VectorStruct, rest.VectorStructOutput]] = None
    shard_key: Optional[ShardKey] = None
    order_value: Optional[OrderValue] = None


    @classmethod
    def from_scored_point(cls, scored_point: rest.ScoredPoint) -> "VectorSearchResult":
        return cls(
            id=scored_point.id,
            version=scored_point.version,
            score=scored_point.score,
            payload=scored_point.payload,
            vector=scored_point.vector,
            shard_key=scored_point.shard_key,
            order_value=scored_point.order_value
        )