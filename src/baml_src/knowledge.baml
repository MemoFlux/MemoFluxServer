enum RelationShip {
    PARENT @description(#"
        父节点
    "#)
    CHILD @description(#"
        子节点
    "#)
} 
class Node{
    targert_id int @description(#"
        用来指向相关节点
    "#)
    relationship RelationShip @description(#"
        用来阐述两个节点之间的关系
    "#)
}

class KnowledgeItem{
    id int @description(#"
        知识项的唯一标识符
    "#)
    header string @description(#"
        知识项的标题
    "#)
    content string @description(#"
        知识项的具体内容
    "#)
    node Node @description(#"
        知识项对应的节点信息
    "#)
}

class Knowledge{
    title string @description(#"
        知识的标题
    "#)
    knowledge_items KnowledgeItem[] @description(#"
        知识项列表
    "#)
    related_items  string[] @description(#"
        可能相关的知识名
    "#)
    tags string[] @description(#"
        对这个知识的标签，该标签不能少于1个，不超过3个
    "#)
}

function KnowledgeStruct(input:string | image,tag:string[]) -> Knowledge {
    client Gemini
    prompt #"
        你是一个知识图谱构建专家。这是用户希望结构化的内容：

        {{ input }}
        这是已经存在的tag，{{ tag }}。你需要尽量使用其中已存在的tag，在没有符合的tag时可以提供新的
        请使用中文回复
        Example: {
      "id": 1,
      "header": "嗜好",
      "content": "吴邪抽烟喝酒。",
      "node": null
    },
    {
      "id": 2,
      "header": "身体健康",
      "content": "吴邪因为喝酒身体出现脂肪肝等问题",
      "node": {
        "target_id":"1",
        "relationship":"CHILD"
      }
    },
        {{ ctx.output_format }}
    "#
}

