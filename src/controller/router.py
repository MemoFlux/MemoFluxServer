import asyncio

from fastapi import APIRouter
from fastapi import Depends
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional
from src.schedules.schemas import Schedule
from src.knowledge.schemas import KnowledgeRes
from src.information.schemas import InformationRes
from src.schedules.core import schedule_core
from src.knowledge.core import knowledge_core
from src.information.core import information_core

from src.auth.router import get_current_user

router = APIRouter(
    prefix="/aigen",
    tags=["AI"]
)


class AIReq(BaseModel):
    tags: List[str] = Field(default=[])
    content: Optional[str] = None
    image: Optional[str] = None
    
    @model_validator(mode='after')
    def content_and_image_mutually_exclusive(self):
        # Either content or image must be provided, but not both
        if self.content is None and self.image is None:
            raise ValueError('Either content or image must be provided')
        if self.content is not None and self.image is not None:
            raise ValueError('content and image cannot be provided at the same time')
        return self

class AIRes(BaseModel):
    knowledge: KnowledgeRes
    information: InformationRes
    schedule: Schedule


@router.post("/",responses=AIRes)
async  def create_ai_req(req: AIReq,current_user: str = Depends(get_current_user)) -> AIRes:
    """
    创建AI请求
    - content: 文本内容
    - image: 图像内容
    - tags: 标签列表
    """
    # 这里可以调用AI模型处理逻辑
    # 假设返回的结果是knowledge, information, schedule
    knowledge = knowledge_core.get_knowledge_from_content(req.content,req.tags)
    information = information_core.get_information_from_content(req.content,req.tags)
    schedule = schedule_core.gen_schedule_from_content(req.content)

    knowledge_result, information_result, schedule_result = await asyncio.gather(knowledge, information, schedule)

    return AIRes(
        knowledge=knowledge_result,
        information=information_result,
        schedule=schedule_result
    )