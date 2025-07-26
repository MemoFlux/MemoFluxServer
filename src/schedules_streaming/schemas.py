"""
日程管理模块的数据模型

该文件定义了日程管理模块使用的 Pydantic 数据模型，包括最终的 Schedule 和 Task 类型，
以及流式处理中使用的 PartialStreamingSchedule 和 PartialStreamingTask 类型。

公开接口:
- Task: 日程任务数据模型
- Schedule: 日程数据模型
- PartialStreamingTask: 流式任务数据模型
- PartialStreamingSchedule: 流式日程数据模型
- StreamState: 流式状态包装器
"""

import uuid
from typing import List, Optional, Literal, Generic, TypeVar
from pydantic import BaseModel, Field

# 从 BAML 导入原始类型
from src.baml_client.types import Task as BamlTask, Schedule as BamlSchedule
from src.baml_client.stream_types import StreamingSchedule as BamlStreamingSchedule

# 定义泛型类型变量
T_co = TypeVar("T_co", covariant=True)


class StreamState(BaseModel, Generic[T_co]):
    """
    包裹流式字段的状态机，用于模拟 BAML 的流式状态
    """

    value: T_co
    state: Literal["Pending", "Incomplete", "Complete", "Error"]


class Task(BamlTask):
    """日程任务数据模型"""

    id: int = Field(default=0, description="任务ID")


class Schedule(BamlSchedule):
    """
    日程数据模型

    这是经过完整处理和验证后，应用逻辑中使用的对象。
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="日程ID")
    text: str = Field(default="", description="原始输入内容")


# 以下是流式处理中使用的部分类型（由 BAML 自动生成）
class PartialStreamingTask(BaseModel):
    """流式处理中的部分任务类型"""

    start_time: Optional[str] = None
    end_time: Optional[str] = None
    people: Optional[List[Optional[str]]] = None
    theme: Optional[str] = None
    core_tasks: Optional[List[Optional[str]]] = None
    position: Optional[List[Optional[str]]] = None
    tags: Optional[List[Optional[str]]] = None
    category: Optional[str] = None
    suggested_actions: Optional[List[Optional[str]]] = None


class PartialStreamingSchedule(BamlStreamingSchedule):
    """
    流式日程处理的部分类型

    这是在流式处理过程中，每个数据块的实际类型。
    直接继承 BAML 自动生成的 StreamingSchedule 类型，保持完全兼容。
    """

    pass
