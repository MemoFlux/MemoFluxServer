from typing import Union

from baml_py import Image

from src.baml_client.async_client import b
from src.baml_client.types import Information

async def call_llm(content: Union[str, Image],tag:list[str]) -> Information:
    res = await b.InformationStruct(content,tag)
    return Information.model_validate(res)