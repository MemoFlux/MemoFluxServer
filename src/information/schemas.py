from src.baml_client.types import Information, InformationItem


class InformationRes(Information):
    """
    信息响应模型
    
    扩展自Information模型，添加了category字段用于分类
    """
    category: str
    
    
InformationItem.model_rebuild()
Information.model_rebuild()
InformationRes.model_rebuild()
