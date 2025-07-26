enum MostImpossbileScene{
    KNOWLEDGE @description(#"
        知识类内容，通常是一些常识、科普、百科等信息
    "#)
    INFORMATION @description(#"
        信息类内容，通常是一些新闻、公告、通知、天气等信息,有时会具有明显的时效性
    "#)
    SCHEDULE @description(#"
        日程类内容，通常是一些会议、活动、安排等信息
    "#)
}


function SortScene(input:string | image) -> MostImpossbileScene{
    client Gemini
    prompt #"
        将上述文本或图片内容进行分类，判断其是否属于以下场景之一：
        文本或者图片是：
        """
        {{ input }}
        """
        {{ctx.output_format}}
    "#
}


test SortSceneKnowledge1 {
    functions [SortScene]
    args {
        input "今天的天气预报显示，明天会有大雨，请大家出门时注意携带雨具。"
    }
}