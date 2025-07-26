#!/usr/bin/env python3
"""
统一抽象基类的使用示例脚本

该脚本演示如何使用 LLMContentProcessor 抽象基类和具体的实现类。
展示了非流式和流式两种处理模式的使用方法。

运行方式:
    python -m src.common.streaming_output.example_usage

或者:
    cd /path/to/MemoFluxServer
    python src/common/streaming_output/example_usage.py
"""

import asyncio
import logging
from typing import Dict, Any

from .document_example import document_processor


def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
        ]
    )


async def demo_non_streaming_processing():
    """演示非流式处理"""
    print("\n" + "="*60)
    print("非流式处理演示")
    print("="*60)
    
    # 测试用例
    test_cases = [
        {
            "name": "会议纪要处理",
            "content": "今天上午9点举行了项目启动会议，参会人员包括张三、李四、王五。会议主要讨论了项目的整体规划和时间安排。决定在下周开始第一阶段的开发工作，预计耗时两个月。",
            "params": {"language": "zh"}
        },
        {
            "name": "技术报告处理", 
            "content": "本报告分析了当前系统的性能瓶颈。通过压力测试发现，数据库查询是主要的性能限制因素。建议优化索引结构，并考虑引入缓存机制来提升响应速度。",
            "params": {"language": "zh"}
        },
        {
            "name": "短文本处理",
            "content": "这是一个简短的测试文本。",
            "params": {}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 40)
        
        try:
            # 使用统一接口处理文本
            result = await document_processor.process_from_text(
                test_case['content'], 
                **test_case['params']
            )
            
            # 输出结果
            print(f"标题: {result.title}")
            print(f"类别: {result.category}")
            print(f"摘要: {result.summary}")
            print(f"语言: {result.language}")
            print(f"字数: {result.word_count}")
            print(f"章节数: {len(result.sections)}")
            
            for j, section in enumerate(result.sections, 1):
                print(f"  章节{j}: {section.title} (标签: {', '.join(section.tags)})")
                
        except Exception as e:
            print(f"处理失败: {str(e)}")


async def demo_streaming_processing():
    """演示流式处理"""
    print("\n" + "="*60)
    print("流式处理演示")
    print("="*60)
    
    test_content = """
    这是一份详细的技术文档，包含了系统架构设计、实现细节和性能优化建议。
    文档分为多个章节，每个章节都有具体的技术说明和代码示例。
    希望通过流式处理能够实时看到文档分析的过程。
    """
    
    print("输入内容:")
    print(test_content.strip())
    print("\n流式处理过程:")
    print("-" * 40)
    
    try:
        chunk_count = 0
        async for chunk in document_processor.process_from_text_stream(test_content):
            chunk_count += 1
            print(f"\n数据块 {chunk_count}:")
            
            # 解析并显示数据块内容
            if chunk.title and chunk.title.value:
                print(f"  标题: {chunk.title.value} (状态: {chunk.title.state})")
            
            if chunk.summary and chunk.summary.value:
                print(f"  摘要: {chunk.summary.value} (状态: {chunk.summary.state})")
            
            if chunk.category:
                print(f"  类别: {chunk.category}")
            
            if chunk.sections and chunk.sections.value:
                print(f"  章节数: {len(chunk.sections.value)} (状态: {chunk.sections.state})")
                for i, section in enumerate(chunk.sections.value):
                    assert section is not None
                    if section.title:
                        print(f"    - {section.title}")
            
            if chunk.language:
                print(f"  语言: {chunk.language}")
            
            if chunk.word_count:
                print(f"  字数: {chunk.word_count}")
        
        print(f"\n流式处理完成，共收到 {chunk_count} 个数据块")
        
    except Exception as e:
        print(f"流式处理失败: {str(e)}")


async def demo_unified_interface():
    """演示统一接口的使用"""
    print("\n" + "="*60)
    print("统一接口演示")
    print("="*60)
    
    test_contents = [
        "这是一个文本输入示例，用于测试统一接口的文本处理功能。",
        # 在实际使用中，这里可以是 Image 对象
        # Image.from_url("https://example.com/document.png")
    ]
    
    for i, content in enumerate(test_contents, 1):
        print(f"\n{i}. 处理内容类型: {type(content).__name__}")
        print("-" * 40)
        
        try:
            # 使用统一的 process_from_content 接口
            result = await document_processor.process_from_content(content)
            
            print(f"处理结果: {result.title}")
            print(f"内容类别: {result.category}")
            print(f"原始长度: {len(result.original_content)}")
            
        except Exception as e:
            print(f"处理失败: {str(e)}")


async def demo_error_handling():
    """演示错误处理"""
    print("\n" + "="*60)
    print("错误处理演示")
    print("="*60)
    
    error_cases = [
        {
            "name": "空文本输入",
            "content": "",
            "expect_error": True
        },
        {
            "name": "过短文本输入",
            "content": "短",
            "expect_error": True  
        },
        {
            "name": "正常文本输入",
            "content": "这是一个正常长度的文本输入，应该能够正常处理。",
            "expect_error": False
        }
    ]
    
    for case in error_cases:
        print(f"\n测试: {case['name']}")
        print(f"输入: '{case['content']}'")
        print(f"预期错误: {case['expect_error']}")
        print("-" * 30)
        
        try:
            result = await document_processor.process_from_text(case['content'])
            if case['expect_error']:
                print("❌ 应该报错但成功了")
            else:
                print(f"✅ 处理成功: {result.title}")
                
        except Exception as e:
            if case['expect_error']:
                print(f"✅ 预期错误: {str(e)}")
            else:
                print(f"❌ 意外错误: {str(e)}")


async def performance_test():
    """简单的性能测试"""
    print("\n" + "="*60)
    print("性能测试演示")
    print("="*60)
    
    import time
    
    test_content = "这是一个用于性能测试的文档内容。" * 20
    test_count = 5
    
    print(f"测试内容长度: {len(test_content)} 字符")
    print(f"测试次数: {test_count}")
    print("-" * 40)
    
    # 非流式处理性能测试
    start_time = time.time()
    for i in range(test_count):
        await document_processor.process_from_text(test_content)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / test_count
    print(f"非流式处理平均耗时: {avg_time:.3f} 秒")
    
    # 流式处理性能测试
    start_time = time.time()
    chunk_count = 0
    for i in range(test_count):
        async for chunk in document_processor.process_from_text_stream(test_content):
            chunk_count += 1
    end_time = time.time()
    
    avg_time = (end_time - start_time) / test_count
    print(f"流式处理平均耗时: {avg_time:.3f} 秒")
    print(f"平均数据块数: {chunk_count}")


async def main():
    """主函数"""
    print("统一抽象基类使用示例")
    print("="*60)
    
    # 设置日志
    setup_logging()
    
    try:
        # 运行各种演示
        await demo_non_streaming_processing()
        await demo_streaming_processing()
        await demo_unified_interface()
        await demo_error_handling()
        await performance_test()
        
        print("\n" + "="*60)
        print("所有演示完成!")
        print("="*60)
        
    except Exception as e:
        print(f"\n运行过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main())