# Information Streaming 模块实现计划

## 项目概述
基于现有的流式输出架构（`src/common/streaming_output`）创建 `information_streaming` 模块，实现流式信息结构化功能。

## 架构设计

### 1. 目录结构
```
src/information_streaming/
├── __init__.py           # 模块导出
├── schemas.py            # 数据模型定义
├── processor.py          # 主要的 InformationProcessor 实现
├── tests/                # 测试文件
│   ├── __init__.py
│   ├── test_processor.py # 处理器测试
│   └── test_integration.py # 集成测试
└── README.md            # 模块文档
```

### 2. 数据流设计

```mermaid
graph TD
    A[用户输入] --> B{输入类型判断}
    B -->|文本| C[文本处理器]
    B -->|图像| D[图像处理器]
    
    C --> E[InformationProcessor]
    D --> E
    
    E --> F[输入验证]
    F --> G[内容预处理]
    G --> H{处理模式}
    
    H -->|非流式| I[LLM调用<br>InformationStruct]
    H -->|流式| J[流式LLM调用<br>InformationStructStream]
    
    I --> K[结果转换]
    J --> L[实时数据块]
    
    K --> M[结果后处理]
    M --> N[最终Information对象]
    
    L --> O[PartialStreamingInformation]
```

### 3. 核心组件

#### 3.1 数据模型 (schemas.py)
- `Information`: 最终信息对象
- `InformationItem`: 信息项对象
- `PartialStreamingInformation`: 流式数据块类型
- `StreamState`: 流式状态包装器

#### 3.2 处理器 (processor.py)
- `InformationProcessor`: 继承自 `LLMContentProcessor`
  - 实现 `_call_llm()`: 调用 BAML InformationStruct
  - 实现 `_call_llm_stream()`: 调用 BAML InformationStructStream
  - 实现 `_convert_to_schema()`: 转换 BAML 结果为本地 Schema

### 4. 接口设计

#### 4.1 公开接口
```python
# 非流式处理
async def process_from_text(text: str, tags: List[str]) -> Information
async def process_from_image(image: Image) -> Information
async def process_from_content(content: Union[str, Image], tags: List[str]) -> Information

# 流式处理
async def process_from_text_stream(text: str, tags: List[str]) -> AsyncGenerator[PartialStreamingInformation, None]
async def process_from_image_stream(image: Image, tags: List[str]) -> AsyncGenerator[PartialStreamingInformation, None]
async def process_from_content_stream(content: Union[str, Image], tags: List[str]) -> AsyncGenerator[PartialStreamingInformation, None]
```

### 5. 实现步骤
1. 创建基础结构
2. 定义数据模型
3. 实现处理器
4. 集成BAML
5. 添加测试
6. 编写文档

### 6. 与现有模块的关系
- 基于 `src.common.streaming_output.base.LLMContentProcessor`
- 使用 `src.baml_client` 的 BAML 函数
- 替换 `src.controller_streaming.placeholders.information`