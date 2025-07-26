"""
日程管理流式处理器测试
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from baml_py import Image

from src.schedules_streaming.processor import ScheduleProcessor
from src.schedules_streaming.schemas import Schedule, Task
from src.baml_client.types import Schedule as BamlSchedule, Task as BamlTask, StreamingSchedule as BamlStreamingSchedule


@pytest.fixture
def schedule_processor():
    """创建 ScheduleProcessor 实例"""
    return ScheduleProcessor()


@pytest.fixture
def sample_text():
    """示例文本输入"""
    return "明天上午9点开会，下午2点去健身房"


@pytest.fixture
def sample_baml_schedule():
    """示例 BAML Schedule 对象"""
    task1 = BamlTask(
        start_time="2023-01-01T09:00:00+08:00",
        end_time="2023-01-01T10:00:00+08:00",
        people=["张三", "李四"],
        theme="项目讨论",
        core_tasks=["讨论项目进度", "分配任务"],
        position=["会议室A"],
        tags=["会议", "项目"],
        category="工作",
        suggested_actions=["准备会议材料", "提前10分钟到场"]
    )
    
    task2 = BamlTask(
        start_time="2023-01-01T14:00:00+08:00",
        end_time="2023-01-01T15:00:00+08:00",
        people=["自己"],
        theme="健身",
        core_tasks=["跑步", "力量训练"],
        position=["健身房"],
        tags=["健身", "健康"],
        category="个人",
        suggested_actions=["带运动服", "带水壶"]
    )
    
    return BamlSchedule(
        title="明日计划",
        category="日常安排",
        tasks=[task1, task2]
    )


class TestScheduleProcessor:
    """ScheduleProcessor 测试类"""
    
    def test_init(self, schedule_processor):
        """测试初始化"""
        assert isinstance(schedule_processor, ScheduleProcessor)
        assert schedule_processor.logger.name == "ScheduleProcessor"
    
    def test_validate_input_valid_text(self, schedule_processor):
        """测试有效文本输入验证"""
        result = schedule_processor._validate_input("这是一个有效的输入文本")
        assert result is True
    
    def test_validate_input_invalid_text(self, schedule_processor):
        """测试无效文本输入验证"""
        result = schedule_processor._validate_input("短")
        assert result is False
    
    def test_validate_input_empty_text(self, schedule_processor):
        """测试空文本输入验证"""
        result = schedule_processor._validate_input("")
        assert result is False
    
    def test_validate_input_image(self, schedule_processor):
        """测试图像输入验证"""
        image = Image.from_url("https://example.com/image.jpg")
        result = schedule_processor._validate_input(image)
        assert result is True
    
    def test_preprocess_content_text(self, schedule_processor):
        """测试文本预处理"""
        input_text = "  这是   一个  测试文本  "
        expected = "这是 一个 测试文本"
        result = schedule_processor._preprocess_content(input_text)
        assert result == expected
    
    def test_preprocess_content_image(self, schedule_processor):
        """测试图像预处理"""
        image = Image.from_url("https://example.com/image.jpg")
        result = schedule_processor._preprocess_content(image)
        assert result == image
    
    def test_convert_to_schema(self, schedule_processor, sample_baml_schedule):
        """测试 BAML 结果转换为 Schema"""
        original_content = "原始输入内容"
        result = schedule_processor._convert_to_schema(sample_baml_schedule, original_content)
        
        assert isinstance(result, Schedule)
        assert result.title == "明日计划"
        assert result.category == "日常安排"
        assert result.text == original_content
        assert len(result.tasks) == 2
        
        # 检查任务转换
        task1 = result.tasks[0]
        assert isinstance(task1, Task)
        assert task1.id == 0
        assert task1.theme == "项目讨论"
        
        task2 = result.tasks[1]
        assert isinstance(task2, Task)
        assert task2.id == 1
        assert task2.theme == "健身"
    
    @pytest.mark.asyncio
    async def test_call_llm_text(self, schedule_processor, sample_baml_schedule):
        """测试文本 LLM 调用"""
        with patch('src.schedules_streaming.processor.b.ScheduleManager', new=AsyncMock(return_value=sample_baml_schedule)):
            result = await schedule_processor._call_llm("测试文本内容")
            assert isinstance(result, BamlSchedule)
            assert result.title == "明日计划"
    
    @pytest.mark.asyncio
    async def test_call_llm_image(self, schedule_processor, sample_baml_schedule):
        """测试图像 LLM 调用"""
        with patch('src.schedules_streaming.processor.b.ScheduleManager', new=AsyncMock(return_value=sample_baml_schedule)):
            image = Image.from_url("https://example.com/image.jpg")
            result = await schedule_processor._call_llm(image)
            assert isinstance(result, BamlSchedule)
            assert result.title == "明日计划"
    
    @pytest.mark.asyncio
    async def test_call_llm_stream_text(self, schedule_processor, sample_baml_schedule):
        """测试文本流式 LLM 调用"""
        # 创建模拟的流式响应
        async def mock_stream():
            yield sample_baml_schedule
            yield sample_baml_schedule  # 模拟多个块
        
        with patch('src.schedules_streaming.processor.b.stream.ScheduleManagerStream', return_value=mock_stream()):
            chunks = []
            async for chunk in schedule_processor._call_llm_stream("测试文本内容"):
                chunks.append(chunk)
            
            assert len(chunks) > 0
            # 注意：这里实际测试的是 BAML StreamingSchedule 类型
    
    @pytest.mark.asyncio
    async def test_process_from_text(self, schedule_processor, sample_baml_schedule):
        """测试从文本处理"""
        with patch('src.schedules_streaming.processor.b.ScheduleManager', new=AsyncMock(return_value=sample_baml_schedule)):
            result = await schedule_processor.process_from_text("测试文本内容")
            assert isinstance(result, Schedule)
            assert result.title == "明日计划"
    
    @pytest.mark.asyncio
    async def test_process_from_image(self, schedule_processor, sample_baml_schedule):
        """测试从图像处理"""
        with patch('src.schedules_streaming.processor.b.ScheduleManager', new=AsyncMock(return_value=sample_baml_schedule)):
            image = Image.from_url("https://example.com/image.jpg")
            result = await schedule_processor.process_from_image(image)
            assert isinstance(result, Schedule)
            assert result.title == "明日计划"
    
    @pytest.mark.asyncio
    async def test_process_from_text_stream(self, schedule_processor, sample_baml_schedule):
        """测试从文本流式处理"""
        # 创建模拟的流式响应
        async def mock_stream():
            yield sample_baml_schedule
            yield sample_baml_schedule
        
        with patch('src.schedules_streaming.processor.b.stream.ScheduleManagerStream', return_value=mock_stream()):
            chunks = []
            async for chunk in schedule_processor.process_from_text_stream("测试文本内容"):
                chunks.append(chunk)
            
            assert len(chunks) > 0
            # 注意：这里实际测试的是 BAML StreamingSchedule 类型