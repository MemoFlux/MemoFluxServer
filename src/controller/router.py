import asyncio
import json
from fastapi import APIRouter
from fastapi import Depends
from pydantic import BaseModel, Field
from typing import List
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
    try:
        # 这里可以调用AI模型处理逻辑
        # 假设返回的结果是knowledge, information, schedule
        rag_client = await vector_db.VectorDB.get_instance()
        logger.debug("rag_client created")
        if (req.isimage == 1):
            image = Image.from_base64("image/png",req.content)
            result = await rag_client.search(req.content)
            logger.debug("start rag")
            for i in result:
                assert i.payload is not None
                req.tags.append(i.payload.get("text")) # type: ignore
            logger.debug("req.tags: %s", req.tags)
            logger.debug("start llm")
            knowledge = knowledge_core.get_knowledge_from_content(image,req.tags)
            information = information_core.get_information_from_content(image,req.tags)
            schedule = schedule_core.gen_schedule_from_content(image)
        else:
            spilitted_str = greedy_text_splitter(req.content,max_length=30)
            logger.debug("start rag")
            
            sem = asyncio.Semaphore(10)
            
            async def concurrent_search(text: str):
                async with sem:
                    return await rag_client.search(text)

            tasks = [concurrent_search(s) for s in spilitted_str]
            results = await asyncio.gather(*tasks)
            
            rag_dict = {}
            for original_str, result_list in zip(spilitted_str, results):
                # 检查结果列表是否为空
                if not result_list:
                    continue
                assert result_list[0].payload is not None
                rag_dict[original_str] = result_list[0].payload.get("text")
                
            logger.debug(f"rag_dict: {rag_dict}")
            rag_str = json.dumps(rag_dict, ensure_ascii=False)
            logger.debug("start llm")
            knowledge = knowledge_core.get_knowledge_from_content(rag_str,req.tags)
            information = information_core.get_information_from_content(rag_str,req.tags)
            schedule = schedule_core.gen_schedule_from_content(rag_str)

        knowledge_result, information_result, schedule_result = await asyncio.gather(knowledge, information, schedule)

        return AIRes(
            knowledge=knowledge_result,
            information=information_result,
            schedule=schedule_result
        )
    except Exception as e:
        logger.error(f"Error in create_ai_req: {e}", exc_info=True)
        # 返回一个默认响应而不是让服务器崩溃
        from src.knowledge.schemas import KnowledgeRes
        from src.information.schemas import InformationRes
        from src.schedules.schemas import Schedule, Task
        
        return AIRes(
            knowledge=KnowledgeRes(
                title="",
                knowledge_items=[],
                related_items=[],
                tags=[],
                category=""
            ),
            information=InformationRes(
                title="",
                information_items=[],
                post_type="",
                summary="",
                tags=[],
                category=""
            ),
            schedule=Schedule(
                title="",
                category="",
                tasks=[],
                id="",
                text=""
            )
        )
