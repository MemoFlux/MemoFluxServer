import json
import aiohttp
from typing import Dict, Any, List

from .config import utils_config
from .schemas import JinaEmbeddingResponse, JinaEmbeddingInput


async def _make_embedding_request(content: List[JinaEmbeddingInput], headers: Dict[str, str]) -> Dict[str, Any]:
    """向 Jina API 发送嵌入请求的内部函数，便于测试。"""
    async with aiohttp.ClientSession() as session:
        # Pydantic模型需要被序列化为字典
        json_payload = {
            "input": [item.model_dump() if not isinstance(item, str) else item for item in content],
            "model": "jina-embeddings-v4",
            "task": "text-matching"
        }
        async with session.post(
            "https://api.jina.ai/v1/embeddings",
            headers=headers,
            json=json_payload
        ) as response:
            # 检查响应状态码
            if response.status != 200:
                error_text = await response.text()
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=f"Jina API error: {error_text}"
                )
            result = await response.text()
            return json.loads(result)


async def get_embeddings(content: List[JinaEmbeddingInput]) -> JinaEmbeddingResponse:
    """获取文本的嵌入向量。"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {utils_config.jina_api_key}"
    }
    
    if not content:
        raise ValueError("Content is empty")
    
    try:
        response_data = await _make_embedding_request(content, headers)
        # 检查响应数据是否包含错误信息
        if "detail" in response_data:
            raise ValueError(f"Jina API returned an error: {response_data['detail']}")
        return JinaEmbeddingResponse.model_validate(response_data)
    except aiohttp.ClientResponseError as e:
        raise ValueError(f"Failed to get embeddings from Jina API: {e.message}") from e
    except Exception as e:
        raise ValueError(f"Failed to parse Jina API response: {str(e)}") from e
