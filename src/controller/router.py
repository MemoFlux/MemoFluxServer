import asyncio
import json
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
from baml_py import Image
from src.log.logger import logger

from src.auth.router import get_current_user
from src.utils import vector_db
from src.utils.text_splitter import greedy_text_splitter

router = APIRouter(
    prefix="/aigen",
    tags=["AI"]
)


class AIReq(BaseModel):
    tags: List[str] = Field(default=[])
    content: str 
    isimage: int



class AIRes(BaseModel):
    knowledge: KnowledgeRes
    information: InformationRes
    schedule: Schedule


@router.post("/",response_model=AIRes)
async  def create_ai_req(req: AIReq,current_user: str = Depends(get_current_user)) -> AIRes:
    """
    创建AI请求
    - content: 文本内容
    - image: 图像内容
    - tags: 标签列表
    """
    # 这里可以调用AI模型处理逻辑
    # 假设返回的结果是knowledge, information, schedule
    ragClient = await vector_db.VectorDB.get_instance()
    if (req.isimage == 1):
        image = Image.from_base64("image/png",req.content)
        knowledge = knowledge_core.get_knowledge_from_content(image,req.tags)
        information = information_core.get_information_from_content(image,req.tags)
        schedule = schedule_core.gen_schedule_from_content(image)
    else:
        spilitted_str = greedy_text_splitter(req.content,max_length=30)
        rag_dict = {}
        for i in spilitted_str:
            result = await ragClient.search(i)
            rag_dict[i] = result[0].payload.get("text")
        logger.info(f"rag_dict: {rag_dict}")
        rag_str = json.dumps(rag_dict, ensure_ascii=False)
        knowledge = knowledge_core.get_knowledge_from_content(rag_str,req.tags)
        information = information_core.get_information_from_content(rag_str,req.tags)
        schedule = schedule_core.gen_schedule_from_content(rag_str.content)

    knowledge_result, information_result, schedule_result = await asyncio.gather(knowledge, information, schedule)

    return AIRes(
        knowledge=knowledge_result,
        information=information_result,
        schedule=schedule_result
    )