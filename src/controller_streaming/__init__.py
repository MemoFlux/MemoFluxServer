"""
流式 AI 控制器模块

该模块提供了流式化的 AI 响应接口，路由为 `/aigen_streaming`。

公开接口:
- router: FastAPI 路由实例

依赖:
- src.schedules_streaming: 流式日程处理模块
- src.information_streaming: 流式信息处理模块
- src.knowledge_streaming: 流式知识处理模块
"""
