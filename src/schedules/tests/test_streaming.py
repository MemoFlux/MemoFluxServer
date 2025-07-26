"""
日程管理流式功能的测试文件
"""

import pytest
from unittest.mock import patch

from baml_py import Image

from src.schedules.core import ScheduleCore


@pytest.mark.asyncio
async def test_gen_schedule_from_text_stream():
    """测试流式文本日程生成"""

    # 模拟流式数据 - 现在使用实际的 BAML 对象
    class MockStreamState:
        def __init__(self, value, state):
            self.value = value
            self.state = state

    class MockTask:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class MockStreamingSchedule:
        def __init__(self, title, category, tasks):
            self.title = title
            self.category = category
            self.tasks = tasks

    async def mock_stream_data():
        # 第一个流式块：标题开始生成
        yield MockStreamingSchedule(
            title=MockStreamState("下午工作", "Incomplete"),
            category=None,
            tasks=MockStreamState(None, "Pending"),
        )

        # 第二个流式块：标题完成，分类出现
        yield MockStreamingSchedule(
            title=MockStreamState("下午工作安排", "Complete"),
            category="工作",
            tasks=MockStreamState(None, "Pending"),
        )

        # 第三个流式块：任务开始生成
        yield MockStreamingSchedule(
            title=MockStreamState("下午工作安排", "Complete"),
            category="工作",
            tasks=MockStreamState([MockTask(theme="开会")], "Incomplete"),
        )

        # 第四个流式块：任务完成
        complete_task = MockTask(
            start_time="2025-01-24T14:00:00+08:00",
            end_time="2025-01-24T16:00:00+08:00",
            people=["同事"],
            theme="工作会议",
            core_tasks=["讨论项目进展"],
            position=["会议室"],
            tags=["工作"],
            category="工作",
            suggested_actions=["准备会议材料"],
        )
        yield MockStreamingSchedule(
            title=MockStreamState("下午工作安排", "Complete"),
            category="工作",
            tasks=MockStreamState([complete_task], "Complete"),
        )

    # 创建 ScheduleCore 实例
    schedule_core = ScheduleCore()

    # 使用 patch 来模拟流式调用
    with patch("src.schedules.core.call_llm_stream", return_value=mock_stream_data()):
        # 收集所有流式数据
        stream_results = []
        async for partial_data in schedule_core.gen_schedule_from_text_stream(
            "今天下午两点开会"
        ):
            stream_results.append(partial_data)

        # 验证流式数据的正确性
        assert len(stream_results) == 4

        # 验证第一个流式块
        first_chunk = stream_results[0]
        assert first_chunk.title.value == "下午工作"
        assert first_chunk.title.state == "Incomplete"
        assert first_chunk.category is None

        # 验证最后一个流式块
        last_chunk = stream_results[-1]
        assert last_chunk.title.value == "下午工作安排"
        assert last_chunk.title.state == "Complete"
        assert last_chunk.category == "工作"
        assert last_chunk.tasks.state == "Complete"
        assert len(last_chunk.tasks.value) == 1


@pytest.mark.asyncio
async def test_gen_schedule_from_image_stream():
    """测试流式图像日程生成"""

    # 模拟图像对象
    mock_image = Image.from_url("https://example.com/schedule.png")

    # 模拟空日程的流式数据
    class MockStreamState:
        def __init__(self, value, state):
            self.value = value
            self.state = state

    class MockStreamingSchedule:
        def __init__(self, title, category, tasks):
            self.title = title
            self.category = category
            self.tasks = tasks

    async def mock_empty_stream_data():
        yield MockStreamingSchedule(
            title=MockStreamState("", "Complete"),
            category="未分类",
            tasks=MockStreamState([], "Complete"),
        )

    schedule_core = ScheduleCore()

    with patch(
        "src.schedules.core.call_llm_stream", return_value=mock_empty_stream_data()
    ):
        stream_results = []
        async for partial_data in schedule_core.gen_schedule_from_image_stream(
            mock_image
        ):
            stream_results.append(partial_data)

        assert len(stream_results) == 1
        result = stream_results[0]
        assert result.title.value == ""
        assert result.category == "未分类"
        assert result.tasks.value == []


@pytest.mark.asyncio
async def test_gen_schedule_from_content_stream_with_text():
    """测试通用流式接口（文本输入）"""

    class MockStreamState:
        def __init__(self, value, state):
            self.value = value
            self.state = state

    class MockStreamingSchedule:
        def __init__(self, title, category, tasks):
            self.title = title
            self.category = category
            self.tasks = tasks

    async def mock_stream_data():
        yield MockStreamingSchedule(
            title=MockStreamState("测试标题", "Complete"),
            category="测试",
            tasks=MockStreamState([], "Complete"),
        )

    schedule_core = ScheduleCore()

    with patch("src.schedules.core.call_llm_stream", return_value=mock_stream_data()):
        stream_results = []
        async for partial_data in schedule_core.gen_schedule_from_content_stream(
            "测试文本"
        ):
            stream_results.append(partial_data)

        assert len(stream_results) == 1
        assert stream_results[0].title.value == "测试标题"


@pytest.mark.asyncio
async def test_gen_schedule_from_content_stream_with_image():
    """测试通用流式接口（图像输入）"""

    mock_image = Image.from_url("https://example.com/test.png")

    class MockStreamState:
        def __init__(self, value, state):
            self.value = value
            self.state = state

    class MockStreamingSchedule:
        def __init__(self, title, category, tasks):
            self.title = title
            self.category = category
            self.tasks = tasks

    async def mock_stream_data():
        yield MockStreamingSchedule(
            title=MockStreamState("图像标题", "Complete"),
            category="图像",
            tasks=MockStreamState([], "Complete"),
        )

    schedule_core = ScheduleCore()

    with patch("src.schedules.core.call_llm_stream", return_value=mock_stream_data()):
        stream_results = []
        async for partial_data in schedule_core.gen_schedule_from_content_stream(
            mock_image
        ):
            stream_results.append(partial_data)

        assert len(stream_results) == 1
        assert stream_results[0].title.value == "图像标题"


@pytest.mark.asyncio
async def test_stream_error_handling():
    """测试流式错误处理"""

    # 对于错误情况，我们简单地模拟异常
    async def mock_error_stream(*args, **kwargs):
        raise Exception("模拟错误")
        # 添加一个 yield 语句使其成为异步生成器
        yield

    schedule_core = ScheduleCore()

    with patch("src.schedules.core.call_llm_stream", side_effect=mock_error_stream):
        with pytest.raises(Exception, match="模拟错误"):
            async for partial_data in schedule_core.gen_schedule_from_text_stream(
                "错误测试"
            ):
                pass
