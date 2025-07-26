"""
流式控制器数据模型

该模块定义了流式控制器使用的数据模型。
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

# 从 schedules_streaming 导入相关的数据模型
from src.schedules_streaming.schemas import Schedule, PartialStreamingSchedule


class AIStreamingReq(BaseModel):
    """流式 AI 请求数据模型"""

    tags: List[str] = Field(default=[], description="标签列表")
    content: str = Field(..., description="文本内容")
    isimage: int = Field(..., description="是否为图像，0表示文本，1表示图像")


class StreamingDataType(str, Enum):
    """流式数据类型枚举"""

    SCHEDULE = "schedule"
    KNOWLEDGE = "knowledge"
    INFORMATION = "information"
    STATUS = "status"


class StreamingStatus(str, Enum):
    """流式处理状态枚举"""

    START = "start"
    PROGRESS = "progress"
    COMPLETE = "complete"
    ERROR = "error"


class AIStreamingRes(BaseModel):
    """流式 AI 响应数据模型"""

    type: StreamingDataType = Field(..., description="数据类型")
    status: StreamingStatus = Field(..., description="处理状态")
    data: Optional[Dict[str, Any]] = Field(None, description="数据内容")
    message: Optional[str] = Field(None, description="状态消息")


__all__ = [
    "AIStreamingReq",
    "AIStreamingRes",
    "StreamingDataType",
    "StreamingStatus",
    "Schedule",
    "PartialStreamingSchedule",
]
