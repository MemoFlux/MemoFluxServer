class InfromationItem{
    header string | null @description(#"
        信息项的标题
    "#)
    content string | null @description(#"
        信息项的具体内容
    "#)
}

enum PostType{
    FOOD_POST @description(#"
        食物相关的帖子
    "#)
    SCENE_POST @description(#"
        场景相关的帖子
    "#)
    LIFE_POST @description(#"
        生活相关的帖子
    "#)
    OTHER_POST @description(#"
        其他类型的帖子
    "#)
}

class Information{
    title string | null @description(#"
        信息的标题
    "#)
    information_items InfromationItem[] | null @description(#"
        信息项列表
    "#)
    post_type string | null @description(#"
        信息的类型
    "#)
    summary string | null @description(#"
        信息的摘要
    "#)
    tags string[] | null @description(#"
        对这个信息的标签，该标签不能少于1个，不超过3个
    "#)
}

// 流式版本的 Information 类
class StreamingInformation{
    title string @stream.with_state @stream.not_null @description(#"
        信息的标题
    "#)
    information_items InfromationItem[] @stream.with_state @description(#"
        信息项列表
    "#)
    post_type string @stream.done @stream.not_null @description(#"
        信息的类型
    "#)
    summary string @stream.with_state @stream.not_null @description(#"
        信息的摘要
    "#)
    tags string[] | null @stream.done @description(#"
        对这个信息的标签，该标签不能少于1个，不超过3个
    "#)
}

function InformationStruct(input:string | image,tag: string[]) -> Information {
    client Gemini
    prompt #"
        你是一个信息结构化专家。这是用户希望结构化的内容：

        {{ input }}
        这是已经存在的tag，{{ tag }}。你需要尽量使用其中已存在的tag，在没有符合的tag时可以提供新的
        请使用中文回复
        {{ctx.output_format}}
    "#
}

// 流式版本的信息结构化函数
function InformationStructStream(input:string | image,tag: string[]) -> StreamingInformation {
    client Gemini
    prompt #"
        你是一个信息结构化专家。请根据用户输入的内容，生成结构化的信息。始终使用中文进行回答。

        重要：请按照以下顺序逐步生成结果，每一步都要完整且详细：
        1. 首先生成标题
        2. 然后逐个生成信息项列表
        3. 接着生成摘要
        4. 最后确定帖子类型和标签

        这是用户希望结构化的内容：
        {{ input }}

        这是已经存在的tag，{{ tag }}。你需要尽量使用其中已存在的tag，在没有符合的tag时可以提供新的
        
        {{ctx.output_format}}
    "#
}

test Text{
    functions [InformationStruct]
    args {
        input #"
            LIVE
1/9
福福板鸭
关注 啊啊啊镇江开了开了，我的新妻子
镇江也有了，之前在南京就超爱
抹茶分1—5号不同浓度！5号是很难得吃到的浓九十葉
郁苦抹
不能吃苦的可以试试1号抹茶茉莉，微甜，很清香~
每种都可以试吃，其他口味坠爱柚子的！酸酸的好适合夏天！！！！
荔枝香水 挂茶1号1 採茶1号
九十叶·抹茶（镇江·苏宁广场店）
#九十叶#九十叶抹茶#九十叶冰淇淋#九十叶gelato#九十叶镇江#镇江美食#镇江
抹茶5号 抹茶3号
抹茶4号
昨天09：53江苏 九十票
共7条评论
啦啦啦啦啦啦啦啦啦
哈哈哈哈凭实力刷到自己打的冰淇淋昨天23：24江苏
赞回复 

            "#
        
        tag ["编程","硬件编程"]
    }
}

test Image{
    functions [InformationStruct]
    args {
        input {
            file "../test.png"
        }
        tag ["编程","美食"]
    }
}

test StreamingText{
    functions [InformationStructStream]
    args {
        input #"
            LIVE
1/9
福福板鸭
关注 啊啊啊镇江开了开了，我的新妻子
镇江也有了，之前在南京就超爱
抹茶分1—5号不同浓度！5号是很难得吃到的浓九十葉
郁苦抹
不能吃苦的可以试试1号抹茶茉莉，微甜，很清香~
每种都可以试吃，其他口味坠爱柚子的！酸酸的好适合夏天！！！！
荔枝香水 挂茶1号1 採茶1号
九十叶·抹茶（镇江·苏宁广场店）
#九十叶#九十叶抹茶#九十叶冰淇淋#九十叶gelato#九十叶镇江#镇江美食#镇江
抹茶5号 抹茶3号
抹茶4号
昨天09：53江苏 九十票
共7条评论
啦啦啦啦啦啦啦啦啦
哈哈哈哈凭实力刷到自己打的冰淇淋昨天23：24江苏
赞回复 

            "#
        
        tag ["编程","硬件编程"]
    }
}

test StreamingImage{
    functions [InformationStructStream]
    args {
        input {
            file "../test.png"
        }
        tag ["编程","美食"]
    }
}