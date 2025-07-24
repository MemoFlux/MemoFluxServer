"""
日程管理核心模块的测试文件
"""

import pytest
from unittest.mock import AsyncMock, patch
import os

from baml_py import Image

from src.schedules.core import ScheduleCore
from src.baml_client.types import Schedule as BamlSchedule, Task as BamlTask


@pytest.mark.asyncio
async def test_gen_schedule():
    # 创建模拟的 BAML 返回结果
    mock_baml_task = BamlTask(
        start_time="2025-07-24T14:00:00+08:00",
        end_time="2025-07-24T16:00:00+08:00",
        people=["同事"],
        theme="工作会议",
        core_tasks=["讨论项目进展", "确定下一步计划"],
        position=["公司会议室"],
        tags=["工作", "会议"],
        category="工作",
        suggested_actions=["准备会议材料", "提前10分钟到达会议室"]
    )
    
    mock_baml_schedule = BamlSchedule(
        title="下午工作安排",
        tasks=[mock_baml_task]
    )
    
    # 创建 ScheduleCore 实例
    schedule_core = ScheduleCore()
    
    # 使用 patch 来模拟 call_llm 函数
    with patch('src.schedules.core.call_llm', new=AsyncMock(return_value=mock_baml_schedule)):
        # 调用 gen_schedule 方法
        result = await schedule_core.gen_schedule("今天下午两点左右记得去公司开会，差不多两小时吧")
        
        # 验证结果
        assert result.title == "下午工作安排"
        assert len(result.tasks) == 1
        assert result.tasks[0].theme == "工作会议"
        assert result.tasks[0].category == "工作"


@pytest.mark.asyncio
async def test_gen_schedule_empty():
    # 创建空的日程安排
    mock_baml_schedule = BamlSchedule(
        title="",
        tasks=[]
    )
    
    # 创建 ScheduleCore 实例
    schedule_core = ScheduleCore()
    
    # 使用 patch 来模拟 call_llm 函数
    with patch('src.schedules.core.call_llm', new=AsyncMock(return_value=mock_baml_schedule)):
        # 调用 gen_schedule 方法
        result = await schedule_core.gen_schedule("这是一段没有日程安排的文本")
        
        # 验证结果
        assert result.title == ""
        assert len(result.tasks) == 0


@pytest.mark.asyncio
async def test_gen_schedule_from_image():
    # 创建模拟的 BAML 返回结果
    mock_baml_task = BamlTask(
        start_time="2025-07-25T08:00:00+08:00",
        end_time="2025-07-25T09:00:00+08:00",
        people=["家人"],
        theme="早餐时间",
        core_tasks=["准备早餐", "一起用餐"],
        position=["家里"],
        tags=["生活", "饮食"],
        category="生活",
        suggested_actions=["提前购买食材", "准备餐具"]
    )
    
    mock_baml_schedule = BamlSchedule(
        title="明日早晨安排",
        tasks=[mock_baml_task]
    )
    
    # 创建 ScheduleCore 实例
    schedule_core = ScheduleCore()
    
    # 创建一个模拟的图像对象
    image_path = "src/schedules/tests/sample/test_img_1.png"
    # 检查文件是否存在
    if os.path.exists(image_path):
        mock_image = Image.from_url(f"file://{os.path.abspath(image_path)}")
    else:
        # 如果文件不存在，使用一个模拟对象
        mock_image = Image.from_url("file:///tmp/mock_image.png")
    
    # 使用 patch 来模拟 call_llm 函数
    with patch('src.schedules.core.call_llm', new=AsyncMock(return_value=mock_baml_schedule)):
        # 调用 gen_schedule_from_content 方法
        result = await schedule_core.gen_schedule_from_content(mock_image)
        
        # 验证结果
        assert result.title == "明日早晨安排"
        assert len(result.tasks) == 1
        assert result.tasks[0].theme == "早餐时间"
        assert result.tasks[0].category == "生活"
        # 验证文本字段包含"image_content"
        assert "image_content" in result.text