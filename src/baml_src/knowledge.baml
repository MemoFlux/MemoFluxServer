enum RelationShip {
    PARENT @description(#"
        父节点
    "#)
    CHILD @description(#"
        子节点
    "#)
} 
class Node{
    target_id int @description(#"
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
    node Node | null @description(#"
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

// 流式版本的 Knowledge 类
class StreamingKnowledge{
    title string @stream.with_state @stream.not_null @description(#"
        知识的标题
    "#)
    knowledge_items KnowledgeItem[] @stream.with_state @description(#"
        知识项列表
    "#)
    related_items  string[] @stream.done @description(#"
        可能相关的知识名
    "#)
    tags string[] @stream.done @description(#"
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

// 流式版本的知识结构化函数
function KnowledgeStructStream(input:string | image,tag:string[]) -> StreamingKnowledge {
    client Gemini
    prompt #"
        你是一个知识图谱构建专家。请根据用户输入的内容，生成结构化的知识。始终使用中文进行回答。

        重要：请按照以下顺序逐步生成结果，每一步都要完整且详细：
        1. 首先生成知识标题
        2. 然后逐个生成知识项列表，包含节点关系信息
        3. 接着分析相关的知识名
        4. 最后确定标签

        这是用户希望结构化的内容：
        {{ input }}

        这是已经存在的tag，{{ tag }}。你需要尽量使用其中已存在的tag，在没有符合的tag时可以提供新的
        
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

// Test case 1: Basic knowledge structure with text input
test BasicKnowledgeStructure {
    functions [KnowledgeStruct]
    args {
        input #"
            人工智能是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
        "#
        tag ["科技", "计算机科学"]
    }
}

// Test case 2: Knowledge structure with relationship between items
test KnowledgeStructureWithRelationships {
    functions [KnowledgeStruct]
    args {
        input #"
            员buff 在身无法选中，法考新素材看到一个六月重庆的警情通报，全员buff在身每未成年
        "#
        tag ["健康", "生活习惯"]
    }
}

// Test case 3: Knowledge structure with new tags
test KnowledgeStructureWithNewTags {
    functions [KnowledgeStruct]
    args {
        input #"
            Python是一种广泛使用的解释型、高级编程、通用型编程语言。
        "#
        tag ["编程语言"]
    }
}

// 流式测试用例
test StreamingBasicKnowledge {
    functions [KnowledgeStructStream]
    args {
        input #"
            人工智能是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
        "#
        tag ["科技", "计算机科学"]
    }
}

test StreamingKnowledgeWithRelationships {
    functions [KnowledgeStructStream]
    args {
        input #"
            员buff 在身无法选中，法考新素材看到一个六月重庆的警情通报，全员buff在身每未成年
        "#
        tag ["健康", "生活习惯"]
    }
}

test StreamingKnowledgeImage {
    functions [KnowledgeStructStream]
    args {
        input {
            file "../test.png"
        }
        tag ["编程", "技术"]
    }
}
