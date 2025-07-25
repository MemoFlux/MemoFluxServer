"""文本分割工具模块的初始化文件。

该模块提供了文本分割功能，主要用于将长文本按照标点符号进行智能分割。

公开接口:
- greedy_text_splitter: 使用贪婪算法进行文本分割的函数
"""

from .text_splitter import greedy_text_splitter

__all__ = ["greedy_text_splitter"]