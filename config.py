# config.py
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

class Settings(BaseSettings):
    app_name: str = "MemoFlux"
    app_port: int = 8000
    log_path: str = "/log/"
    postgresql_url: str = "postgresql://user:password@localhost/dbname"
    siliconflow_apikey: str = "your_llm_api_key"
    google_apikey: str = "your_google_api_key"

    class Config:
        env_file = ".env"  # 指定环境变量文件路径
        env_file_encoding = "utf-8"

# 创建一个全局的 settings 实例
settings = Settings() 
