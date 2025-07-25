from typing import List, Union
import uuid
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

from .embedding import get_embeddings
from .schemas import JinaTextInput, JinaImageInput, VectorSearchResult


KEYS: List[str] = [
  "核心论点", "数据支撑", "反方观点", "文献引用", "案例分析", "图表数据", 
  "研究方法", "章节笔记", "灵感闪念", "美食探店", "景点信息", "活动信息", 
  "优惠券", "门票预订", "行程规划", "路线交通", "营业时间", "购物清单", 
  "健身打卡", "健康食谱", "情绪记录", "冥想放松", "习惯养成", "健康资讯", 
  "运动教程", "身体数据", "学习笔记", "教程资源", "代码片段", "知识概念", 
  "实战项目", "文章收藏", "工具推荐", "学习清单"
]

class VectorDB:
    """
    向量数据库类，用于管理向量数据库的创建和初始化。
    
    Args:
        collection_name: 集合名称
        url: 数据库URL
        api_key: 数据库API密钥
    
    Methods:
        create: 创建向量数据库实例
    """
    def __init__(self, collection_name: str, url: str, api_key: str):
        self.client = AsyncQdrantClient(url=url, api_key=api_key)
        self.collection_name = collection_name
        self.initialized = False
    
    @classmethod
    async def create(cls, collection_name: str, url: str, api_key: str) -> "VectorDB":
        instance = cls(collection_name, url, api_key)
        await instance._initialize()
        instance.initialized = True
        return instance
        
    async def __init_async__(self) -> None:
        await self._initialize()

    async def _initialize(self) -> None:
        """将预定义的关键词嵌入并存储到向量数据库中。"""
        has_collection = await self.client.collection_exists(collection_name=self.collection_name)
        if not has_collection:
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=2048, distance=Distance.COSINE)
            )

        # 检查集合是否已经有数据，避免重复初始化
        collection_info = await self.client.get_collection(collection_name=self.collection_name)
        if collection_info.points_count is not None and collection_info.points_count > 0:
            return

        embeddings_response = await get_embeddings([JinaTextInput(text=key) for key in KEYS])
        
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding_data.embedding,
                payload={"text": key}
            )
            for key, embedding_data in zip(KEYS, embeddings_response.data)
        ]
        
        await self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True
        )

    async def search(self, query_content: List[Union[str, JinaTextInput, JinaImageInput]], limit: int = 5) -> List[VectorSearchResult]:
        """
        在向量数据库中搜索与查询文本相似的向量。

        Args:
            query_content: 查询内容
            limit: 返回结果数量

        Returns:
            搜索结果列表
        """
        if not self.initialized:
            raise RuntimeError("VectorDB is not initialized. Call `create` to initialize.")

        query_embedding_response = await get_embeddings(query_content)
        if not query_embedding_response.data:
            return []

        query_vector = query_embedding_response.data[0].embedding

        hits = await self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
        )

        return [VectorSearchResult.from_scored_point(hit) for hit in hits]
    
    