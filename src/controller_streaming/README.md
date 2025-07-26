# Controller Streaming 模块

## 模块概述

该模块提供了流式化的 AI 响应接口，路由为 `/aigen_streaming`。它基于现有的 `schedules_streaming` 模块，实现了完整的流式处理能力，支持文本和图像输入。

## 公开接口

### 路由
- `POST /aigen_streaming`: 流式 AI 处理接口

### 类
- `router`: FastAPI 路由实例

## 内部方法

- `stream_processor`: 流式处理器，协调各个模块的流式处理
- `StreamEvent`: 流式事件包装器

## 数据流

```
客户端请求 -> /aigen_streaming 路由 -> 流式控制器 ->
多个处理器流式处理 -> 实时返回流式数据 -> 客户端接收
```

## 用法示例

### 后端使用

```python
from src.controller_streaming import router

# 在 FastAPI 应用中注册路由
app.include_router(router)
```

### 前端使用

```javascript
// 流式请求示例
const response = await fetch('/aigen_streaming', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-token'
  },
  body: JSON.stringify({
    content: "明天上午9点开会",
    isimage: 0,
    tags: []
  })
});

// 处理流式响应
const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  // 处理 SSE 数据
  if (chunk.startsWith('data: ')) {
    const data = JSON.parse(chunk.slice(6));
    console.log('收到数据:', data);
  }
}
```

## 架构特点

### 1. 流式处理
- 基于 Server-Sent Events (SSE) 实现实时数据传输
- 支持并发处理多个模块的流式数据
- 提供完整的错误处理机制

### 2. 模块化设计
- 与 `schedules_streaming` 模块无缝集成
- 与 `information_streaming` 和 `knowledge_streaming` 模块无缝集成
- 易于扩展和维护

### 3. 统一接口
- 提供与非流式接口一致的使用体验
- 支持文本和图像输入
- 统一的错误处理和状态报告

## 与 controller 模块的区别

| 特性 | controller 模块 | controller_streaming 模块 |
|------|----------------|--------------------------|
| 处理模式 | 非流式 | 流式 |
| 响应方式 | 一次性返回完整结果 | 实时返回部分结果 |
| 用户体验 | 等待时间长 | 实时反馈 |
| 技术实现 | 同步处理 | 异步流式处理 |

## 测试

模块包含完整的测试套件：

```bash
# 运行测试
python -m pytest src/controller_streaming/tests/
```

## 依赖

- `src.schedules_streaming`: 流式日程处理模块
- `src.information_streaming`: 流式信息处理模块
- `src.knowledge_streaming`: 流式知识处理模块
- `fastapi`: Web 框架
- `pydantic`: 数据模型定义