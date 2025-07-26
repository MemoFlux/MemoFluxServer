# Controller Streaming 模块实现计划

## 项目概述
创建一个新的 `controller_streaming` 模块，用于提供流式化的 AI 响应接口，路由为 `/aigen_streaming`。

## 架构设计

### 1. 目录结构
```
src/controller_streaming/
├── __init__.py           # 模块导出
├── router.py            # 流式路由定义
├── schemas.py           # 数据模型定义
├── placeholders/        # 知识和信息模块的占位符
│   ├── __init__.py
│   ├── knowledge.py     # 知识模块占位符
│   └── information.py   # 信息模块占位符
└── README.md           # 模块文档
```

### 2. 数据流设计

```mermaid
graph TD
    A[客户端请求] --> B[/aigen_streaming 路由]
    B --> C[流式控制器]
    C --> D{输入类型判断}
    D -->|文本| E[文本处理器]
    D -->|图像| F[图像处理器]
    
    E --> G[ScheduleProcessor流式处理]
    F --> G
    
    G --> H[实时返回流式数据]
    H --> I[客户端接收]
    
    J[知识占位符] --> H
    K[信息占位符] --> H
```

### 3. 接口设计

#### 3.1 请求模型
- `AIStreamingReq`: 流式请求数据模型
  - tags: 标签列表
  - content: 文本内容
  - isimage: 是否为图像

#### 3.2 响应模型
- `AIStreamingRes`: 流式响应数据模型
  - type: 数据类型 (schedule/knowledge/information)
  - data: 部分数据
  - state: 处理状态 (start/progress/complete)

#### 3.3 路由接口
- POST `/aigen_streaming`: 流式 AI 处理接口
  - 支持 Server-Sent Events (SSE)
  - 实时返回处理结果

### 4. 实现步骤

1. **创建目录结构**: 建立 controller_streaming 目录
2. **创建占位符类**: 为知识和信息模块创建无实际逻辑的类
3. **实现流式路由**: 创建 router.py 中的流式接口
4. **集成 schedules_streaming**: 使用流式日程处理
5. **添加数据模型**: 创建请求和响应的数据模型
6. **测试接口**: 验证流式接口的正确性

### 5. 技术要点

- 使用 FastAPI 的 StreamingResponse
- 集成 schedules_streaming 的流式处理能力
- 提供占位符的知识和信息处理
- 支持文本和图像输入
- 实时流式响应

### 6. 使用示例

```python
# 客户端使用示例
import requests
import json

# 流式请求
response = requests.post(
    "http://localhost:8000/aigen_streaming",
    json={"content": "明天上午9点开会", "isimage": 0, "tags": []},
    stream=True
)

for line in response.iter_lines():
    if line:
        data = json.loads(line.decode('utf-8'))
        print(f"收到: {data}")