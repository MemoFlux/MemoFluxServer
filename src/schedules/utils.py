from typing import Union

from baml_py import Image

from src.baml_client.async_client import b
from src.baml_client.types import Schedule as BamlSchedule

async def call_llm(content: Union[str, Image]) -> BamlSchedule:
    res = await b.ScheduleManager(content)
    return BamlSchedule.model_validate(res)