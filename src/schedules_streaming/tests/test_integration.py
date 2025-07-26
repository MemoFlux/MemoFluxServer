"""
日程管理流式处理器集成测试
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from baml_py import Image

from src.schedules_streaming import schedule_processor
from src.schedules_streaming.schemas import Schedule
from src.baml_client.types import StreamingSchedule


class TestScheduleProcessorIntegration:
    """ScheduleProcessor 集成测试类"""
    
    @pytest.mark.asyncio
    async def test_process_from_text_integration(self):
        """集成测试：从文本处理"""
        # 模拟 BAML 响应
        from src.baml_client.types import Schedule as BamlSchedule, Task as BamlTask
        
        mock_task = BamlTask(
            start_time="2023-01-01T09:00:00+08:00",
            end_time="2023-01-01T10:00:00+08:00",
            people=["张三"],
            theme="会议",
            core_tasks=["讨论项目"],
            position=["会议室"],
            tags=["工作"],
            category="工作",
            suggested_actions=["准备材料"]
        )
        
        mock_schedule = BamlSchedule(
            title="测试日程",
            category="测试",
            tasks=[mock_task]
        )
        
        with patch('src.schedules_streaming.processor.b.ScheduleManager', new=AsyncMock(return_value=mock_schedule)):
            result = await schedule_processor.process_from_text("测试文本内容")
            
            assert isinstance(result, Schedule)
            assert result.title == "测试日程"
            assert result.category == "测试"
            assert len(result.tasks) == 1
            assert result.tasks[0].theme == "会议"
    
    @pytest.mark.asyncio
    async def test_process_from_text_stream_integration(self):
        """集成测试：从文本流式处理"""
        # 模拟 BAML 流式响应
        from src.baml_client.types import StreamingSchedule as BamlStreamingSchedule, Task as BamlTask
        
        mock_task = BamlTask(
            start_time="2023-01-01T09:00:00+08:00",
            end_time="2023-01-01T10:00:00+08:00",
            people=["张三"],
            theme="会议",
            core_tasks=["讨论项目"],
            position=["会议室"],
            tags=["工作"],
            category="工作",
            suggested_actions=["准备材料"]
        )
        
        mock_streaming_schedule = BamlStreamingSchedule(
            title="测试日程",
            category="测试",
            tasks=[mock_task]
        )
        
        # 创建模拟的流式响应
        async def mock_stream():
            yield mock_streaming_schedule
            yield mock_streaming_schedule  # 模拟多个块
        
        with patch('src.schedules_streaming.processor.b.stream.ScheduleManagerStream', return_value=mock_stream()):
            chunks = []
            async for chunk in schedule_processor.process_from_text_stream("测试文本内容"):
                chunks.append(chunk)
            
            assert len(chunks) > 0
            assert isinstance(chunks[0], StreamingSchedule)
    
    @pytest.mark.asyncio
    async def test_process_from_image_integration(self):
        """集成测试：从图像处理"""
        # 模拟 BAML 响应
        from src.baml_client.types import Schedule as BamlSchedule, Task as BamlTask
        
        mock_task = BamlTask(
            start_time="2023-01-01T09:00:00+08:00",
            end_time="2023-01-01T10:00:00+08:00",
            people=["张三"],
            theme="会议",
            core_tasks=["讨论项目"],
            position=["会议室"],
            tags=["工作"],
            category="工作",
            suggested_actions=["准备材料"]
        )
        
        mock_schedule = BamlSchedule(
            title="图像日程",
            category="测试",
            tasks=[mock_task]
        )
        
        with patch('src.schedules_streaming.processor.b.ScheduleManager', new=AsyncMock(return_value=mock_schedule)):
            image = Image.from_url("https://example.com/schedule.jpg")
            result = await schedule_processor.process_from_image(image)
            
            assert isinstance(result, Schedule)
            assert result.title == "图像日程"
            assert result.category == "测试"
    
    def test_input_validation_integration(self):
        """集成测试：输入验证"""
        # 测试有效输入
        assert schedule_processor._validate_input("这是一个有效的长文本输入") is True
        
        # 测试无效输入
        assert schedule_processor._validate_input("短") is False
        assert schedule_processor._validate_input("") is False
    
    def test_preprocessing_integration(self):
        """集成测试：内容预处理"""
        # 测试文本预处理
        input_text = "  这是   一个  测试文本  "
        expected = "这是 一个 测试文本"
        result = schedule_processor._preprocess_content(input_text)
        assert result == expected