"""
流式 AI 控制器路由

该模块实现了流式 AI 处理接口，提供 `/aigen_streaming` 路由。
"""

import asyncio
import json
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Union, List, AsyncGenerator
from baml_py import Image

from src.schedules_streaming.processor import schedule_processor
from src.knowledge_streaming.processor import knowledge_processor
from src.information_streaming.processor import information_processor
from src.controller_streaming.schemas import (
    AIStreamingReq, 
    AIStreamingRes, 
    StreamingDataType, 
    StreamingStatus
)
from src.utils.img_url import base64_to_URL
from src.log.logger import logger

# 导入认证依赖
from src.auth.router import get_current_user

router = APIRouter(
    prefix="/aigen_streaming",
    tags=["AI Streaming"]
)


class StreamEvent:
    """流式事件包装器"""
    
    def __init__(self, data: AIStreamingRes):
        self.data = data
    
    def encode(self) -> str:
        """编码为 SSE 格式"""
        json_data = self.data.model_dump_json()
        return f"data: {json_data}\n\n"


async def stream_processor(
    content: Union[str, Image],
    tags: List[str]
) -> AsyncGenerator[str, None]:
    """
    流式处理器，协调各个模块的流式处理
    
    Args:
        content: 输入内容（文本或图像）
        tags: 标签列表
        
    Yields:
        str: SSE 格式的流式数据
    """
    logger.debug(f"[CONTROLLER_DEBUG] 开始流式处理，内容类型: {type(content)}, 标签: {tags}")
    
    # 发送开始状态
    start_event = StreamEvent(
        AIStreamingRes(
            type=StreamingDataType.STATUS,
            status=StreamingStatus.START,
            message="开始流式处理",
            data={}
        )
    )
    yield start_event.encode()
    
    # 简单实现：顺序处理每个模块的流式数据
    # 实际项目中可以使用更复杂的并发处理
    
    # 处理日程流
    try:
        async for partial_result in schedule_processor.process_from_content_stream(content):
            event = StreamEvent(
                AIStreamingRes(
                    type=StreamingDataType.SCHEDULE,
                    status=StreamingStatus.PROGRESS,
                    data=partial_result.model_dump() if hasattr(partial_result, 'model_dump') else {},
                    message=None
                )
            )
            print(event.encode())
            yield event.encode()
    except Exception as e:
        error_event = StreamEvent(
            AIStreamingRes(
                type=StreamingDataType.STATUS,
                status=StreamingStatus.ERROR,
                message=f"日程处理出错: {str(e)}",
                data={}
            )
        )
        yield error_event.encode()
    
    # 处理知识流
    try:
        logger.debug(f"[CONTROLLER_DEBUG] 开始调用知识处理器流式处理")
        async for partial_result in knowledge_processor.process_from_content_stream(content, tags=tags):
            logger.debug(f"[CONTROLLER_DEBUG] 知识处理器返回数据块: {type(partial_result)}")
            event = StreamEvent(
                AIStreamingRes(
                    type=StreamingDataType.KNOWLEDGE,
                    status=StreamingStatus.PROGRESS,
                    data=partial_result.model_dump() if hasattr(partial_result, 'model_dump') else {},
                    message=None
                )
            )
            yield event.encode()
        logger.debug(f"[CONTROLLER_DEBUG] 知识处理器流式处理完成")
    except Exception as e:
        logger.error(f"[CONTROLLER_DEBUG] 知识处理器出错: {str(e)}")
        import traceback
        logger.error(f"[CONTROLLER_DEBUG] 知识处理器错误堆栈: {traceback.format_exc()}")
        error_event = StreamEvent(
            AIStreamingRes(
                type=StreamingDataType.STATUS,
                status=StreamingStatus.ERROR,
                message=f"知识处理出错: {str(e)}",
                data={}
            )
        )
        yield error_event.encode()
    
    # 处理信息流
    try:
        logger.debug(f"[CONTROLLER_DEBUG] 开始调用信息处理器流式处理")
        async for partial_result in information_processor.process_from_content_stream(content, tags=tags):
            logger.debug(f"[CONTROLLER_DEBUG] 信息处理器返回数据块: {type(partial_result)}")
            event = StreamEvent(
                AIStreamingRes(
                    type=StreamingDataType.INFORMATION,
                    status=StreamingStatus.PROGRESS,
                    data=partial_result.model_dump() if hasattr(partial_result, 'model_dump') else {},
                    message=None
                )
            )
            yield event.encode()
        logger.debug(f"[CONTROLLER_DEBUG] 信息处理器流式处理完成")
    except Exception as e:
        logger.error(f"[CONTROLLER_DEBUG] 信息处理器出错: {str(e)}")
        import traceback
        logger.error(f"[CONTROLLER_DEBUG] 信息处理器错误堆栈: {traceback.format_exc()}")
        error_event = StreamEvent(
            AIStreamingRes(
                type=StreamingDataType.STATUS,
                status=StreamingStatus.ERROR,
                message=f"信息处理出错: {str(e)}",
                data={}
            )
        )
        yield error_event.encode()
    
    # 发送完成状态
    complete_event = StreamEvent(
        AIStreamingRes(
            type=StreamingDataType.STATUS,
            status=StreamingStatus.COMPLETE,
            message="流式处理完成",
            data={}
        )
    )
    yield complete_event.encode()


@router.post("/")
async def create_ai_streaming_req(
    req: AIStreamingReq,
    _: str = Depends(get_current_user)
) -> StreamingResponse:
    """
    创建流式 AI 请求
    
    Args:
        req: 流式 AI 请求数据
        _: 当前用户（从依赖中获取，用于认证）
        
    Returns:
        StreamingResponse: SSE 流式响应
    """
    try:
        # 处理图像或文本内容
        if req.isimage == 1:
            # 处理图像
            image_url = await base64_to_URL(req.content)
            if image_url is None or image_url == "":
                raise HTTPException(status_code=400, detail="图像上传失败")
            
            logger.debug("图像 URL: %s", image_url)
            content = Image.from_url(image_url)
        else:
            # 处理文本
            content = req.content
        
        # 返回流式响应
        return StreamingResponse(
            stream_processor(content, req.tags),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            }
        )
    except Exception as e:
        logger.error(f"流式处理出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理出错: {str(e)}")


__all__ = ["router"]