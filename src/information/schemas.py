from src.baml_client.types import Information, InfromationItem


class InformationRes(Information):
    category: str
    
    
InfromationItem.model_rebuild()
Information.model_rebuild()
InformationRes.model_rebuild()