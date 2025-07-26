class Task {
    start_time string @description(#"
        事项开始时间，以ISO 8601格式表示，地区为东八区
    "#)
    end_time string @description(#"
        事项结束时间，以ISO 8601格式表示，地区为东八区
    "#)
    people string[] @description(#"
        相关人群，人名或称呼
    "#)
    theme string @description(#"
        主题
    "#)
    core_tasks string[] @description(#"
        核心任务/事项
    "#)
    position string[] @description(#"
        执行地点
    "#)
    tags string[] @description(#"
        标签
    "#)
    category string @description(#"
        分类
    "#)
    suggested_actions string[] @description(#"
        建议的行为，建议用户该做些什么
    "#)
}

class Schedule {
    title string @description(#"
        标题，需要具体且简洁，不能以"今日待办"、"今日计划"等模糊的标题
    "#)
    category string @description(#"
        分类
    "#)
    tasks Task[] @description(#"
        事项列表
    "#)
}

// 流式版本的 Schedule 类
class StreamingSchedule {
    title string @stream.with_state @stream.not_null @description(#"
        标题，需要具体且简洁，不能以"今日待办"、"今日计划"等模糊的标题
    "#)
    category string @stream.done @stream.not_null @description(#"
        分类
    "#)
    tasks Task[] @stream.with_state @description(#"
        事项列表
    "#)
}

function ScheduleManager(content:string | image) -> Schedule {
    client Gemini
    prompt #"
        你是一个日程管理专家，请根据用户输入的文本，生成一个日程安排。始终使用和用户输入的文本相同的语言进行回答。
        用户输入的文本是：
        """
        {{ content }}
        """
        {{ctx.output_format}}

        注：如果图片中没有日程相关的安排，请设置title和tasks均为空。category为"未分类"
    "#
}

// 流式版本的日程管理函数
function ScheduleManagerStream(content:string | image) -> StreamingSchedule {
    client Gemini
    prompt #"
        你是一个日程管理专家，请根据用户输入的文本，生成一个日程安排。始终使用和用户输入的文本相同的语言进行回答。

        重要：请按照以下顺序逐步生成结果，每一步都要完整且详细：
        1. 首先生成标题
        2. 然后确定分类
        3. 最后逐个生成事项列表

        用户输入的文本是：
        """
        {{ content }}
        """
        {{ctx.output_format}}

        注：如果图片中没有日程相关的安排，请设置title和tasks均为空。category为"未分类"
    "#
}

test IsScheduleSingleTask1 {
    functions [ScheduleManager]
    args {
        content "今天下午两点左右记得去公司开会，差不多两小时吧"
    }
}

test IsScheduleSingleTask2 {
    functions [ScheduleManager]
    args {
        content "明天早上一定要记得赶八点的飞机！"
    }
}

test IsScheduleMultiTask1 {
    functions [ScheduleManager]
    args {
        content "今天下午两点左右记得去公司开会，差不多两小时吧。然后晚上六点去健身房锻炼，差不多一小时。"
    }
}

test IsScheduleMultiTask2 {
    functions [ScheduleManager]
    args {
        content "明天早上一定要记得赶八点的飞机！然后下飞机后赶紧吃早餐。"
    }
}

test IsScheduleImage1 {
    functions [ScheduleManager]
    args {
        content {
            file "sample/test_img_1.png"
        }
    }
}

test NotScheduleImage1 {
    functions [ScheduleManager]
    args {
        content {
            url "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"
        }
    }
}