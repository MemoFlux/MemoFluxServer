package v1

import "github.com/gogf/gf/v2/frame/g"

type SSEGenerateReq struct {
	g.Meta  `path:"/sse/generate" method:"post" summary:"SSE流式生成" tags:"LLM"`
	Tags    []string `json:"tags" description:"标签"`
	Content string   `json:"content" description:"内容"`
	IsImage int      `json:"isImage" description:"是否为图片，0表示否"`
}

type SSEGenerateRes struct {
}
