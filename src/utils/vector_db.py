import asyncio
from typing import List, Union
import uuid
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

from .embedding import get_embeddings
from .schemas import JinaTextInput, JinaImageInput, VectorSearchResult
from .config import utils_config


KEYS: List[str] = [
    "核心论点",
    "数据支撑",
    "反方观点",
    "文献引用",
    "案例分析",
    "图表数据",
    "研究方法",
    "章节笔记",
    "灵感闪念",
    "美食探店",
    "景点信息",
    "活动信息",
    "优惠券",
    "门票预订",
    "行程规划",
    "路线交通",
    "营业时间",
    "购物清单",
    "健身打卡",
    "健康食谱",
    "情绪记录",
    "冥想放松",
    "习惯养成",
    "健康资讯",
    "运动教程",
    "身体数据",
    "学习笔记",
    "教程资源",
    "代码片段",
    "知识概念",
    "实战项目",
    "文章收藏",
    "工具推荐",
    "学习清单",
]


class VectorDB:
    _instance = None
    _lock = asyncio.Lock()

    def __init__(self, collection_name: str, url: str, api_key: str):
        """
        私有构造函数，请使用 get_instance() 获取实例。
        """
        self.client = AsyncQdrantClient(url=url, api_key=api_key)
        self.collection_name = collection_name
        self.initialized = False

    @classmethod
    async def get_instance(cls) -> "VectorDB":
        """
        获取 VectorDB 的单例实例。
        如果实例不存在，则会异步创建并初始化它。
        """
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    instance = VectorDB(
                        collection_name=utils_config.collection_name,
                        url=utils_config.qdrant_url,
                        api_key=utils_config.qdrant_api_key,
                    )
                    await instance._initialize()
                    cls._instance = instance
        return cls._instance

    @classmethod
    def _cleanup_instance(cls):
        """清理单例实例，主要用于测试或脚本。"""
        cls._instance = None

    async def _initialize(self) -> None:
        """将预定义的关键词嵌入并存储到向量数据库中。"""
        has_collection = await self.client.collection_exists(
            collection_name=self.collection_name
        )
        if not has_collection:
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=2048, distance=Distance.COSINE),
            )

        # 检查集合是否已经有数据，避免重复初始化
        collection_info = await self.client.get_collection(
            collection_name=self.collection_name
        )
        if collection_info.points_count is None or collection_info.points_count == 0:
            try:
                embeddings_response = await get_embeddings(
                    [JinaTextInput(text=key) for key in KEYS]
                )

                points = [
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding_data.embedding,
                        payload={"text": key},
                    )
                    for key, embedding_data in zip(KEYS, embeddings_response.data)
                ]

                await self.client.upsert(
                    collection_name=self.collection_name, points=points, wait=True
                )
            except Exception as e:
                print(f"Failed to initialize vector database: {e}")
                raise

        self.initialized = True

    async def search(
        self, query_content: Union[str, JinaTextInput, JinaImageInput], limit: int = 5
    ) -> List[VectorSearchResult]:
        """
        在向量数据库中搜索与查询文本相似的向量。

        Args:
            query_content: 查询内容
            limit: 返回结果数量

        Returns:
            搜索结果列表
        """
        if not self.initialized:
            raise RuntimeError(
                "VectorDB is not initialized. Call `get_instance` to initialize."
            )

        try:
            query_embedding_response = await get_embeddings([query_content])
            if not query_embedding_response.data:
                return []

            query_vector = query_embedding_response.data[0].embedding

            hits = await self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
            )

            return [VectorSearchResult.from_scored_point(hit) for hit in hits]
        except Exception as e:
            print(f"Failed to search in vector database: {e}")
            # 返回空列表而不是抛出异常，以避免整个请求失败
            return []

    async def delete_collection(self):
        """删除向量数据库中的集合。"""
        result = await self.client.delete_collection(
            collection_name=self.collection_name
        )
        if result:
            print(f"集合 '{self.collection_name}' 已被成功删除。")
            # 重置实例状态
            self.initialized = False
            VectorDB._cleanup_instance()
        else:
            print(f"删除集合 '{self.collection_name}' 失败。")
        return result
