# Schedules Streaming 模块

## 模块概述

基于 `LLMContentProcessor` 抽象基类实现的日程管理模块，提供完整的日程生成功能，支持文本和图像输入，以及流式和非流式处理模式。

该模块是 `src/schedules` 模块的流式增强版本，提供了更完整的架构设计和扩展性。

## 公开接口

### 类

- `ScheduleProcessor`: 日程处理器类，继承自 `LLMContentProcessor`
- `schedule_processor`: 日程处理器的全局实例

### 数据模型

- `Task`: 日程任务数据模型
- `Schedule`: 日程数据模型
- `PartialStreamingTask`: 流式任务数据模型
- `PartialStreamingSchedule`: 流式日程数据模型

## 内部方法

- `_call_llm`: 调用日程管理的 BAML 函数 `ScheduleManager`
- `_call_llm_stream`: 调用日程流式管理的 BAML 函数 `ScheduleManagerStream`
- `_convert_to_schema`: 将 BAML 结果转换为本地 Schedule 对象
- `_validate_input`: 输入验证钩子
- `_preprocess_content`: 内容预处理钩子
- `_postprocess_result`: 结果后处理钩子（可选）

## 数据流

```
输入内容 -> 日程分析 -> 任务提取 -> 分类识别 -> Schedule 对象
     ↓
流式处理 -> 实时返回部分结果 -> 完整 Schedule 对象
```

## 用法示例

### 非流式处理

```python
from src.schedules_streaming import schedule_processor

# 从文本生成日程
schedule = await schedule_processor.process_from_text("明天上午9点开会，下午2点去健身房")

# 从图像生成日程
from baml_py import Image
image = Image.from_url("https://example.com/schedule.jpg")
schedule = await schedule_processor.process_from_image(image)

# 通用内容处理（自动识别文本或图像）
schedule = await schedule_processor.process_from_content("明天上午9点开会")
```

### 流式处理

```python
from src.schedules_streaming import schedule_processor

# 流式从文本生成日程
async for partial_schedule in schedule_processor.process_from_text_stream("明天上午9点开会，下午2点去健身房"):
    if partial_schedule.title:
        print(f"标题: {partial_schedule.title}")
    
    if partial_schedule.tasks:
        print(f"任务数: {len(partial_schedule.tasks)}")
        for task in partial_schedule.tasks:
            if task:
                print(f"  - {task.theme}")

# 流式从图像生成日程
from baml_py import Image
image = Image.from_url("https://example.com/schedule.jpg")
async for partial_schedule in schedule_processor.process_from_image_stream(image):
    # 处理流式数据
    pass
```

## 架构特点

### 1. 统一接口设计
- 提供一致的 API 接口，支持文本和图像输入
- 同时支持流式和非流式处理模式
- 自动类型识别和路由

### 2. 扩展性强
- 基于抽象基类的设计，易于扩展
- 提供钩子方法支持自定义逻辑
- 模块化解耦，便于维护

### 3. 完整的处理流程
- 输入验证：确保输入内容符合要求
- 内容预处理：标准化输入内容
- LLM 调用：与 BAML 集成
- 结果转换：将 BAML 结果转换为本地模型
- 结果后处理：可选的后处理逻辑

### 4. 流式处理支持
- 实时返回处理结果
- 支持部分结果的增量更新
- 与非流式接口保持一致的使用体验

## 与原 schedules 模块的区别

| 特性 | 原 schedules 模块 | schedules_streaming 模块 |
|------|------------------|-------------------------|
| 架构 | 直接调用 BAML | 基于抽象基类 |
| 流式支持 | 基础流式 | 完整流式架构 |
| 扩展性 | 有限 | 高度可扩展 |
| 错误处理 | 基础 | 完整的钩子系统 |
| 预处理 | 无 | 支持内容预处理 |
| 后处理 | 无 | 支持结果后处理 |

## 测试

模块包含完整的测试套件：

```bash
# 运行单元测试
python -m pytest src/schedules_streaming/tests/test_processor.py

# 运行集成测试
python -m pytest src/schedules_streaming/tests/test_integration.py

# 运行所有测试
python -m pytest src/schedules_streaming/tests/
```

## 依赖

- `src.common.streaming_output`: 抽象基类和流式处理框架
- `src.baml_client`: BAML 生成的客户端代码
- `pydantic`: 数据模型定义
- `baml-py`: BAML Python SDK