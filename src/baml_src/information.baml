class InformationItem{
    header string @description(#"
        信息项的标题，你有义务对信息的内容进行高度概括
    "#)
    content string @description(#"
        信息项的具体内容，你有义务返回一个完整语义的内容，不能出现错字或语法错误
        如果信息字符长度超过20，请在该字段头部添加一个跟内容相符的emoji
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
    title string @description(#"
        信息的标题
    "#)
    information_items InformationItem[] @description(#"
        信息项列表
    "#)
    post_type string @description(#"
        信息的类型
    "#)
    summary string @description(#"
        信息的摘要
    "#)
    tags string[] @description(#"
        对这个信息的标签，该标签不能少于1个，不超过3个
    "#)

}

function InformationStruct(input:string | image,tag: string[]) -> Information {
    client Gemini
    prompt #"
        你是一个信息结构化专家。这是用户希望结构化的内容：

        {{ input }}
        这是已经存在的tag，{{ tag }}。你需要尽量使用其中已存在的tag，在没有符合的tag时可以提供新的
        你有义务尽可能的减少新tag的创建。
        请使用中文回复
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