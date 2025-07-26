"""
LLM 内容处理器的抽象基类

该文件定义了统一的抽象基类，为各个模块提供一致的接口规范。

公开接口:
- LLMContentProcessor: 泛型抽象基类，定义了统一的处理方法

内部方法:
- _call_llm: 抽象方法，子类实现具体的 LLM 调用逻辑
- _call_llm_stream: 抽象方法，子类实现具体的流式 LLM 调用逻辑
- _convert_to_schema: 抽象方法，子类实现 BAML 结果转换逻辑
- _validate_input: 可选钩子方法，子类可重写进行输入验证
- _preprocess_content: 可选钩子方法，子类可重写进行内容预处理
- _postprocess_result: 可选钩子方法，子类可重写进行结果后处理

数据流:
1. 非流式: 用户输入 -> 类型检查 -> 预处理 -> LLM调用 -> 结果转换 -> 后处理 -> 返回
2. 流式: 用户输入 -> 类型检查 -> 预处理 -> 流式LLM调用 -> 实时yield数据块
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Union, AsyncGenerator, Any, Optional
from baml_py import Image
import logging
from datetime import datetime

# 泛型类型变量
T = TypeVar('T')  # 最终 Schema 类型
T_Stream = TypeVar('T_Stream')  # 流式数据块类型


class LLMContentProcessor(Generic[T, T_Stream], ABC):
    """
    LLM 内容处理器的抽象基类
    
    该类定义了统一的接口规范，所有继承的子类都必须实现抽象方法。
    提供了文本、图像和通用内容的处理接口，支持流式和非流式两种模式。
    
    类型参数:
        T: 最终返回的 Schema 类型（如 Knowledge, Information, Schedule）
        T_Stream: 流式处理时的数据块类型（如 PartialStreamingKnowledge）
    """
    
    def __init__(self, logger_name: Optional[str] = None):
        """
        初始化处理器
        
        Args:
            logger_name: 日志器名称，默认使用类名
        """
        self.logger = logging.getLogger(logger_name or self.__class__.__name__)
    
    # 公开接口 - 非流式处理
    async def process_from_text(self, text: str, **kwargs) -> T:
        """
        从文本生成结果
        
        Args:
            text: 输入的文本内容
            **kwargs: 额外的参数，会传递给内部方法
            
        Returns:
            T: 转换后的最终 Schema 对象
            
        Raises:
            Exception: 处理过程中的任何异常都会被重新抛出
        """
        try:
            self.logger.info(f"开始处理文本输入，长度: {len(text)}")
            
            # 输入验证
            if not self._validate_input(text, **kwargs):
                raise ValueError("输入验证失败")
            
            # 内容预处理
            processed_text = self._preprocess_content(text, **kwargs)
            
            # 调用 LLM
            result = await self._call_llm(processed_text, **kwargs)
            
            # 转换为 Schema
            converted = self._convert_to_schema(result, text, **kwargs)
            
            # 结果后处理
            final_result = self._postprocess_result(converted, **kwargs)
            
            self.logger.info("文本处理完成")
            return final_result
            
        except Exception as e:
            self.logger.error(f"文本处理失败: {str(e)}")
            raise
    
    async def process_from_image(self, image: Image, **kwargs) -> T:
        """
        从图像生成结果
        
        Args:
            image: 输入的图像对象
            **kwargs: 额外的参数，会传递给内部方法
            
        Returns:
            T: 转换后的最终 Schema 对象
            
        Raises:
            Exception: 处理过程中的任何异常都会被重新抛出
        """
        try:
            self.logger.info("开始处理图像输入")
            
            # 输入验证
            if not self._validate_input(image, **kwargs):
                raise ValueError("输入验证失败")
            
            # 内容预处理
            processed_image = self._preprocess_content(image, **kwargs)
            
            # 调用 LLM
            result = await self._call_llm(processed_image, **kwargs)
            
            # 转换为 Schema
            converted = self._convert_to_schema(result, "image_content", **kwargs)
            
            # 结果后处理
            final_result = self._postprocess_result(converted, **kwargs)
            
            self.logger.info("图像处理完成")
            return final_result
            
        except Exception as e:
            self.logger.error(f"图像处理失败: {str(e)}")
            raise
    
    async def process_from_content(self, content: Union[str, Image], **kwargs) -> T:
        """
        通用内容处理接口
        
        根据输入内容的类型自动选择对应的处理方法。
        
        Args:
            content: 输入内容，可以是文本或图像
            **kwargs: 额外的参数，会传递给具体的处理方法
            
        Returns:
            T: 转换后的最终 Schema 对象
        """
        if isinstance(content, str):
            return await self.process_from_text(content, **kwargs)
        else:
            return await self.process_from_image(content, **kwargs)
    
    # 公开接口 - 流式处理
    async def process_from_text_stream(self, text: str, **kwargs) -> AsyncGenerator[T_Stream, None]:
        """
        流式从文本生成结果
        
        Args:
            text: 输入的文本内容
            **kwargs: 额外的参数，会传递给内部方法
            
        Yields:
            T_Stream: 流式数据块
            
        Raises:
            Exception: 处理过程中的任何异常都会被重新抛出
        """
        try:
            self.logger.info(f"开始流式处理文本，长度: {len(text)}")
            
            # 输入验证
            if not self._validate_input(text, **kwargs):
                raise ValueError("输入验证失败")
            
            # 内容预处理
            processed_text = self._preprocess_content(text, **kwargs)
            
            # 流式调用 LLM
            chunk_index = 0
            async for chunk in self._call_llm_stream(processed_text, **kwargs):
                chunk_index += 1
                
                try:
                    # 尝试验证数据块
                    if hasattr(chunk, 'model_validate') and hasattr(chunk, 'model_dump'):
                        chunk.model_validate(chunk.model_dump())  # type: ignore
                    
                    yield chunk
                    
                except Exception as chunk_error:
                    self.logger.error(f"数据块 {chunk_index} 验证失败: {chunk_error}")
                    self.logger.error(f"数据块内容: {chunk}")
                    self.logger.error(f"数据块字段: {list(chunk.model_fields.keys()) if hasattr(chunk, 'model_fields') else 'No model_fields'}")  # type: ignore
                    
                    # 检查具体的字段值
                    if hasattr(chunk, 'model_fields'):
                        for field_name in getattr(chunk, 'model_fields', {}):
                            if hasattr(chunk, field_name):
                                field_value = getattr(chunk, field_name)
                                self.logger.error(f"字段 {field_name}: {field_value} (类型: {type(field_value)})")
                    
                    # 重新抛出异常，让上层处理
                    raise chunk_error
                
            self.logger.info("流式文本处理完成")
            
        except Exception as e:
            self.logger.error(f"流式文本处理失败: {str(e)}")
            raise
    
    async def process_from_image_stream(self, image: Image, **kwargs) -> AsyncGenerator[T_Stream, None]:
        """
        流式从图像生成结果
        
        Args:
            image: 输入的图像对象
            **kwargs: 额外的参数，会传递给内部方法
            
        Yields:
            T_Stream: 流式数据块
            
        Raises:
            Exception: 处理过程中的任何异常都会被重新抛出
        """
        try:
            self.logger.info("开始流式处理图像")
            
            # 输入验证
            if not self._validate_input(image, **kwargs):
                raise ValueError("输入验证失败")
            
            # 内容预处理
            processed_image = self._preprocess_content(image, **kwargs)
            
            # 流式调用 LLM
            async for chunk in self._call_llm_stream(processed_image, **kwargs):
                yield chunk
                
            self.logger.info("流式图像处理完成")
            
        except Exception as e:
            self.logger.error(f"流式图像处理失败: {str(e)}")
            raise
    
    async def process_from_content_stream(self, content: Union[str, Image], **kwargs) -> AsyncGenerator[T_Stream, None]:
        """
        通用流式内容处理接口
        
        根据输入内容的类型自动选择对应的流式处理方法。
        
        Args:
            content: 输入内容，可以是文本或图像
            **kwargs: 额外的参数，会传递给具体的处理方法
            
        Yields:
            T_Stream: 流式数据块
        """
        if isinstance(content, str):
            async for chunk in self.process_from_text_stream(content, **kwargs):
                yield chunk
        else:
            async for chunk in self.process_from_image_stream(content, **kwargs):
                yield chunk
    
    # 抽象方法 - 子类必须实现
    @abstractmethod
    async def _call_llm(self, content: Union[str, Image], **kwargs) -> Any:
        """
        调用对应的 BAML 函数
        
        这是核心的 LLM 调用方法，子类必须实现具体的调用逻辑。
        
        Args:
            content: 处理后的输入内容
            **kwargs: 额外的参数
            
        Returns:
            Any: BAML 函数的原始返回结果
        """
        pass
    
    @abstractmethod
    async def _call_llm_stream(self, content: Union[str, Image], **kwargs) -> AsyncGenerator[T_Stream, None]:
        """
        调用对应的 BAML 流式函数
        
        这是流式 LLM 调用方法，子类必须实现具体的流式调用逻辑。
        
        Args:
            content: 处理后的输入内容
            **kwargs: 额外的参数
            
        Yields:
            T_Stream: 流式数据块
        """
        raise NotImplementedError("子类必须实现此方法")
        yield  # 永远不会执行，但必须存在以标识这是一个异步生成器
    
    @abstractmethod
    def _convert_to_schema(self, baml_result: Any, original_content: str, **kwargs) -> T:
        """
        将 BAML 结果转换为本地 Schema
        
        子类必须实现具体的转换逻辑，将 BAML 返回的结果转换为应用中使用的 Schema 对象。
        
        Args:
            baml_result: BAML 函数的返回结果
            original_content: 原始输入内容的字符串表示
            **kwargs: 额外的参数
            
        Returns:
            T: 转换后的最终 Schema 对象
        """
        pass
    
    # 可选的钩子方法 - 子类可以重写
    def _validate_input(self, content: Union[str, Image], **kwargs) -> bool:
        """
        输入验证钩子
        
        子类可以重写此方法来实现自定义的输入验证逻辑。
        
        Args:
            content: 输入内容
            **kwargs: 额外的参数
            
        Returns:
            bool: 验证是否通过
        """
        if isinstance(content, str):
            return len(content.strip()) > 0
        return content is not None
    
    def _preprocess_content(self, content: Union[str, Image], **kwargs) -> Union[str, Image]:
        """
        内容预处理钩子
        
        子类可以重写此方法来实现自定义的内容预处理逻辑。
        
        Args:
            content: 原始输入内容
            **kwargs: 额外的参数
            
        Returns:
            Union[str, Image]: 预处理后的内容
        """
        return content
    
    def _postprocess_result(self, result: T, **kwargs) -> T:
        """
        结果后处理钩子
        
        子类可以重写此方法来实现自定义的结果后处理逻辑。
        
        Args:
            result: 转换后的 Schema 对象
            **kwargs: 额外的参数
            
        Returns:
            T: 后处理后的最终结果
        """
        return result