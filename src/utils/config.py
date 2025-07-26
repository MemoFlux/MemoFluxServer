from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

from dotenv import load_dotenv

load_dotenv()


class UtilsConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # 忽略.env文件中未在模型中定义的字段
    )

    jina_api_key: str = Field(
        default="", description="Jina API Key", validation_alias="JINA_API_KEY"
    )

    collection_name: str = Field(
        default="memo_flux",
        description="Collection Name",
        validation_alias="COLLECTION_NAME",
    )

    qdrant_url: str = Field(
        default="http://localhost:6333",
        description="Qdrant URL",
        validation_alias="QDRANT_URL",
    )

    qdrant_api_key: str = Field(
        default="", description="Qdrant API Key", validation_alias="QDRANT_API_KEY"
    )


utils_config = UtilsConfig()
