# MemoFlux

MemoFlux 是一个智能日程管理工具，可以根据自然语言描述自动生成结构化的日程安排。

## 功能特性

- 自然语言处理：将用户输入的自然语言转换为结构化日程
- 图像识别：支持从图片中提取日程信息
- 多格式输出：提供标准化的 JSON 格式日程数据

## 项目结构

```
├── src/
│   ├── schedules/           # 日程管理模块
│   │   ├── core.py          # 核心实现
│   │   ├── interface.py     # 接口定义
│   │   ├── schemas.py       # 数据模型
│   │   ├── utils.py         # 工具函数
│   │   └── tests/           # 测试文件
│   └── ...
```

## 日程管理模块使用说明

### 核心类和方法

- `ScheduleCore`: 日程管理核心实现类
  - `gen_schedule_from_text(text: str)`: 根据文本生成日程
  - `gen_schedule_from_image(image: Image)`: 根据图像生成日程
  - `gen_schedule(text: str)`: 兼容接口，根据文本生成日程
  - `gen_schedule_from_content(content: Union[str, Image])`: 根据内容（文本或图像）生成日程

### 使用示例

```python
from src.schedules.core import schedule_core

# 从文本生成日程
text = "今天下午两点左右记得去公司开会，差不多两小时吧"
schedule = await schedule_core.gen_schedule(text)

# 从图像生成日程（需要先加载图像）
from baml_py import Image
image = Image.from_url("path/to/image.png")
schedule = await schedule_core.gen_schedule_from_image(image)
```

### 数据结构

生成的 `Schedule` 对象包含以下字段：
- `id`: 唯一标识符
- `title`: 日程标题
- `text`: 原始输入文本
- `tasks`: 任务列表，每个任务包含：
  - `task_id`: 任务ID
  - `start_time`: 开始时间（ISO 8601格式）
  - `end_time`: 结束时间（ISO 8601格式）
  - `people`: 相关人员
  - `theme`: 主题
  - `core_tasks`: 核心任务
  - `position`: 地点
  - `tags`: 标签
  - `category`: 分类
  - `suggested_actions`: 建议行为

## 开发和测试

```bash
# 运行测试
python -m pytest src/schedules/tests/test_core.py -v
```