import json
import aiohttp
from typing import Dict, Any, List

from .config import utils_config
from .schemas import JinaEmbeddingResponse


async def _make_embedding_request(content: List[str], headers: Dict[str, str]) -> Dict[str, Any]:
    """向 Jina API 发送嵌入请求的内部函数，便于测试。"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.jina.ai/v1/embeddings",
            headers=headers,
            json={"input": content, "model": "jina-embeddings-v4", "task": "text-matching"}
        ) as response:
            result = await response.text()
            return json.loads(result)


async def get_embeddings(content: List[str]) -> JinaEmbeddingResponse:
    """获取文本的嵌入向量。"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {utils_config.jina_api_key}"
    }
    
    if not content:
        raise ValueError("Content is empty")
    
    response_data = await _make_embedding_request(content, headers)
    return JinaEmbeddingResponse.model_validate(response_data)