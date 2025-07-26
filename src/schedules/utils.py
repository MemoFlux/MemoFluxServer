from typing import Union, AsyncGenerator

from baml_py import Image

from src.baml_client.async_client import b
from src.baml_client.types import Schedule as BamlSchedule

async def call_llm(content: Union[str, Image]) -> BamlSchedule:
    res = await b.ScheduleManager(content)
    return BamlSchedule.model_validate(res)

async def call_llm_stream(content: Union[str, Image]):
    """
    流式调用 LLM 生成日程安排
    
    Args:
        content: 用户输入的内容（文本或图像）
        
    Yields:
        StreamingSchedule: BAML 生成的流式日程对象，包含：
        - title: StreamState[str] - 标题的流式状态
        - category: str | None - 分类
        - tasks: StreamState[List[Task]] - 任务列表的流式状态
    """
    # 使用 BAML 的流式接口，直接返回生成的对象
    stream = b.stream.ScheduleManagerStream(content)
    
    async for partial_result in stream:
        yield partial_result