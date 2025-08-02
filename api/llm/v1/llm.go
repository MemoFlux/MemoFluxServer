package v1

import "github.com/gogf/gf/v2/frame/g"

type GeneralReq struct {
	g.Meta  `path:"/GeneralReq" method:"post" tags:"LLM" summary:"通用请求"`
	Tags    []string `json:"tags" description:"标签"`
	Content string   `json:"content" description:"<UNK>"`
	Isimage int      `json:"isimage" description:"<UNK>"`
}

// RelationShip 表示节点关系
type RelationShip string

// Node 表示一个知识图谱节点
type Node struct {
	TargetID     int          `json:"targetId"     dc:"用来指向相关节点"`
	Relationship RelationShip `json:"relationship"  dc:"用来阐述两个节点之间的关系,只能从PARENT、CHILD两个值中选择"`
}

// KnowledgeItem 表示一个具体的知识项
type KnowledgeItem struct {
	ID      int    `json:"id"      dc:"知识项的唯一标识符"`
	Header  string `json:"header"  dc:"知识项的标题"`
	Content string `json:"content" dc:"知识项的具体内容，你有义务返回一个完整语义的内容，不能出现错字或语法错误；如果信息字符长度超过20，请在该字段头部添加一个跟内容相符的emoji"`
	Node    *Node  `json:"node"    dc:"知识项对应的节点信息"` // 指针表示可以为 null
}

// Knowledge 表示一个完整的知识结构
type Knowledge struct {
	Title          string          `json:"title"           dc:"知识的标题"`
	KnowledgeItems []KnowledgeItem `json:"knowledgeItems" dc:"知识项列表"`
	RelatedItems   []string        `json:"relatedItems"   dc:"可能相关的知识名"`
	Tags           []string        `json:"tags"            dc:"对这个知识的标签，该标签不能少于1个，不超过3个"`
}

// Task 表示单个事项
type Task struct {
	StartTime        string   `json:"startTime" dc:"事项开始时间，以ISO 8601格式表示，地区为东八区"`
	EndTime          string   `json:"endTime" dc:"事项结束时间，以ISO 8601格式表示，地区为东八区"`
	People           []string `json:"people" dc:"相关人群，人名或称呼"`
	Theme            string   `json:"theme" dc:"主题"`
	CoreTasks        []string `json:"coreTasks" dc:"核心任务/事项"`
	Position         []string `json:"position" dc:"执行地点"`
	Tags             []string `json:"tags" dc:"标签"`
	Category         string   `json:"category" dc:"分类"`
	SuggestedActions []string `json:"suggestedActions" dc:"建议的行为，建议用户该做些什么"`
}

// Schedule 表示一个日程安排
type Schedule struct {
	Title    string `json:"title" dc:"标题，需要具体且简洁，不能以“今日待办”、“今日计划”等模糊的标题"`
	Category string `json:"category" dc:"分类"`
	Tasks    []Task `json:"tasks" dc:"事项列表"`
}

type GeneralRes struct {
	g.Meta                 `mime:"application/json" example:"{}"`
	Most_possible_category string    `json:"mostPossibleCategory" dc:"最可能的分类"`
	Schedule               Schedule  `json:"schedule" dc:"日程安排"`
	Knowledge              Knowledge `json:"knowledge" dc:"<UNK>"`
}
