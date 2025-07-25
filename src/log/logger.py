import os
from loguru import logger
from src.config import settings

# 确保日志目录存在
log_directory = settings.log_path.strip() if settings.log_path else "./logs/"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# 配置loguru
logger.remove()  # 移除默认的日志配置

# 添加按日期分文件的日志配置
log_file_path = os.path.join(log_directory, "{time:YYYY-MM-DD}.log")
logger.add(
    log_file_path,
    rotation="00:00",  # 每天轮转
    retention="30 days",  # 保留30天的日志
    compression="zip",  # 压缩旧日志
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    level="INFO"
)

# 添加控制台输出
logger.add(
    os.path.join(log_directory, "app.log"),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    level="DEBUG"
)

# 添加错误日志文件
logger.add(
    os.path.join(log_directory, "error.log"),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="10 MB"
)

__all__ = ["logger"]
