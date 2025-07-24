from typing import Union

from baml_py import Image

from src.baml_client.async_client import b
from src.baml_client.types import Knowledge

async def call_llm(content: Union[str, Image],tag:list[str]) -> Knowledge:
    res = await b.KnowledgeStruct(content,tag)
    return Knowledge.model_validate(res)