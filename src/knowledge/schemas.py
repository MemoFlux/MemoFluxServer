from src.baml_client.types import Knowledge, KnowledgeItem


class KnowledgeRes(Knowledge):
    """
    知识响应模型

    扩展自BAML的Knowledge模型，增加了category字段用于标识知识分类。
    """

    category: str


# 重建模型以解决Pydantic的延迟引用问题
Knowledge.model_rebuild()
KnowledgeItem.model_rebuild()
KnowledgeRes.model_rebuild()
