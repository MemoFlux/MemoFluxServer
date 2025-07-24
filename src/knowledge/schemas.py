from src.baml_client.types import Knowledge, KnowledgeItem

class KnowledgeRes(Knowledge):
    category: str

# 重建模型以解决Pydantic的延迟引用问题
Knowledge.model_rebuild()
KnowledgeItem.model_rebuild()
KnowledgeRes.model_rebuild()
