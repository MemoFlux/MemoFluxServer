"""
知识管理流式处理器

该模块实现了基于 LLMContentProcessor 的知识管理处理器，支持文本和图像输入，
以及流式和非流式处理模式。

公开接口:
- KnowledgeProcessor: 继承 LLMContentProcessor 的知识处理器
- knowledge_processor: 知识处理器的全局实例

内部方法:
- _call_llm: 调用知识结构化的 BAML 函数
- _call_llm_stream: 调用知识流式结构化的 BAML 函数
- _convert_to_schema: 将 BAML 结果转换为 Knowledge 对象

数据流:
输入内容 -> 知识分析 -> 结构化提取 -> Knowledge 对象
"""

from typing import Union, AsyncGenerator, List, Any
from baml_py import Image

from src.common.streaming_output.base import LLMContentProcessor
from src.baml_client.async_client import b
from src.baml_client.types import Knowledge as BamlKnowledge, RelationShip
from src.baml_client.stream_types import StreamingKnowledge as BamlStreamingKnowledge
from .schemas import Knowledge


class KnowledgeProcessor(LLMContentProcessor[Knowledge, BamlStreamingKnowledge]):
    """
    知识管理处理器
    
    继承自 LLMContentProcessor，实现了知识内容的分析和结构化处理。
    支持从文本和图像中提取知识结构，生成结构化的知识内容。
    """
    
    def __init__(self, logger_name: str = "KnowledgeProcessor"):
        """
        初始化知识管理处理器
        
        Args:
            logger_name: 日志器名称
        """
        super().__init__(logger_name)
    
    async def _call_llm(self, content: Union[str, Image], tags: List[str] = [], **kwargs) -> BamlKnowledge:
        """
        调用知识结构化的 BAML 函数
        
        Args:
            content: 输入内容（文本或图像）
            tags: 标签列表
            **kwargs: 额外参数
            
        Returns:
            BamlKnowledge: BAML 生成的知识对象
        """
        self.logger.info("调用 LLM 进行知识分析")
        
        # 调用 BAML 的 KnowledgeStruct 函数
        result = await b.KnowledgeStruct(input=content, tag=tags)
        
        return result
    
    async def _call_llm_stream(self, content: Union[str, Image], tags: List[str] = [], **kwargs) -> AsyncGenerator[BamlStreamingKnowledge, None]:
        """
        调用知识流式结构化的 BAML 函数
        
        Args:
            content: 输入内容（文本或图像）
            tags: 标签列表
            **kwargs: 额外参数
            
        Yields:
            PartialStreamingKnowledge: 流式知识分析结果
        """
        self.logger.info("开始流式知识分析")
        
        # 调用 BAML 的 KnowledgeStructStream 函数
        stream = b.stream.KnowledgeStructStream(input=content, tag=tags)
        chunk_count = 0
        async for partial in stream:
            chunk_count += 1
            self.logger.debug(f"[DEBUG] 处理第 {chunk_count} 个数据块")
            
            # 详细记录原始 partial 的状态
            self.logger.debug(f"[DEBUG] 原始 partial 类型: {type(partial)}")
            
            # 检查关键字段的值
            if hasattr(partial, 'related_items'):
                self.logger.debug(f"[DEBUG] related_items 值: {partial.related_items} (类型: {type(partial.related_items)})")
            if hasattr(partial, 'tags'):
                self.logger.debug(f"[DEBUG] tags 值: {partial.tags} (类型: {type(partial.tags)})")
            
            # 直接修复 None 值，简单有效
            if hasattr(partial, 'related_items') and partial.related_items is None:
                partial.related_items = []
                self.logger.debug(f"[DEBUG] 修复 related_items None -> []")
                
            if hasattr(partial, 'tags') and partial.tags is None:
                partial.tags = []
                self.logger.debug(f"[DEBUG] 修复 tags None -> []")
            
            # 处理 knowledge_items 中的 None 字段
            if hasattr(partial, 'knowledge_items') and partial.knowledge_items is not None:
                # 检查是否有 value 属性（流式状态包装）
                items_to_check = None
                if hasattr(partial.knowledge_items, 'value'):
                    items_to_check = partial.knowledge_items.value
                elif isinstance(partial.knowledge_items, list):
                    items_to_check = partial.knowledge_items
                
                if items_to_check:
                    for i, item in enumerate(items_to_check):
                        if item is not None:
                            # 修复 id 字段
                            if hasattr(item, 'id') and item.id is None:
                                item.id = i + 1  # 使用基于1的索引作为默认ID
                                self.logger.debug(f"[DEBUG] 修复 knowledge_items[{i}].id None -> {item.id}")
                            
                            # 修复 header 字段
                            if hasattr(item, 'header') and item.header is None:
                                item.header = ""
                                self.logger.debug(f"[DEBUG] 修复 knowledge_items[{i}].header None -> ''")
                            
                            # 修复 content 字段
                            if hasattr(item, 'content') and item.content is None:
                                item.content = ""
                                self.logger.debug(f"[DEBUG] 修复 knowledge_items[{i}].content None -> ''")
                            
                            # 修复 node 字段中的 None 值
                            if hasattr(item, 'node') and item.node is not None:
                                # 修复 target_id 字段
                                if hasattr(item.node, 'target_id') and item.node.target_id is None:
                                    item.node.target_id = 1  # 默认指向第一个节点
                                    self.logger.debug(f"[DEBUG] 修复 knowledge_items[{i}].node.target_id None -> 1")
                                
                                # 修复 relationship 字段
                                if hasattr(item.node, 'relationship') and item.node.relationship is None:
                                    item.node.relationship = RelationShip.CHILD  # 默认关系为子节点
                                    self.logger.debug(f"[DEBUG] 修复 knowledge_items[{i}].node.relationship None -> 'CHILD'")
            
            self.logger.debug(f"[DEBUG] 修复后，返回数据块")
            yield partial
    
    def _convert_to_schema(self, baml_result: BamlKnowledge, original_content: str, tags: List[str] = [], **kwargs) -> Knowledge:
        """
        将 BAML 结果转换为 Knowledge Schema
        
        Args:
            baml_result: BAML 返回的知识分析结果
            original_content: 原始输入内容的字符串表示
            tags: 标签列表
            **kwargs: 额外参数
            
        Returns:
            Knowledge: 转换后的知识对象
        """
        self.logger.info("转换 BAML 结果为 Knowledge Schema")
        
        # 创建 Knowledge 对象
        knowledge = Knowledge(
            title=baml_result.title,
            knowledge_items=baml_result.knowledge_items,
            related_items=baml_result.related_items,
            tags=baml_result.tags,
            category=original_content[:50] if len(original_content) <= 50 else original_content[:47] + "..."  # 使用前50个字符作为分类
        )
        
        return knowledge
    
    def _validate_input(self, content: Union[str, Image], tags: List[str] = [], **kwargs) -> bool:
        """
        重写输入验证逻辑
        
        对于知识处理，我们要求文本长度至少为5个字符。
        
        Args:
            content: 输入内容
            tags: 标签列表
            **kwargs: 额外参数
            
        Returns:
            bool: 验证是否通过
        """
        if isinstance(content, str):
            return len(content.strip()) >= 5
        return content is not None
    
    def _preprocess_content(self, content: Union[str, Image], tags: List[str] = [], **kwargs) -> Union[str, Image]:
        """
        重写内容预处理逻辑
        
        对文本进行基本的清理，去除多余的空白字符。
        
        Args:
            content: 原始输入内容
            tags: 标签列表
            **kwargs: 额外参数
            
        Returns:
            Union[str, Image]: 预处理后的内容
        """
        if isinstance(content, str):
            # 清理多余的空白字符
            cleaned = ' '.join(content.split())
            self.logger.debug(f"文本预处理：原长度 {len(content)}, 清理后长度 {len(cleaned)}")
            return cleaned
        return content


# 创建全局实例
knowledge_processor = KnowledgeProcessor()

__all__ = ["KnowledgeProcessor", "knowledge_processor"]