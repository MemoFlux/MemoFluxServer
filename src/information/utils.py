from typing import Union, List

from baml_py import Image

from src.baml_client.async_client import b
from src.baml_client.types import Information


async def call_llm(content: Union[str, Image], tag: List[str]) -> Information:
    """
    调用LLM生成结构化信息

    Args:
        content: 输入内容，可以是文本字符串或图像对象
        tag: 信息标签列表

    Returns:
        Information: BAML生成的结构化信息对象
    """
    res = await b.InformationStruct(content, tag)
    return Information.model_validate(res)
