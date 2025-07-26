from typing import Union, List

from baml_py import Image

from src.baml_client.async_client import b
from src.baml_client.types import Knowledge


async def call_llm(content: Union[str, Image], tag: List[str]) -> Knowledge:
    """
    调用LLM生成知识结构

    Args:
        content: 输入内容（文本或图像）
        tag: 标签列表

    Returns:
        Knowledge: LLM生成的知识结构
    """
    res = await b.KnowledgeStruct(content, tag)
    return Knowledge.model_validate(res)
