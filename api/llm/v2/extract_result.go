package v2

import (
	v1 "MemoFluxServer/api/llm/v1"

	"github.com/gogf/gf/v2/frame/g"
)

type ExtractResultReq struct {
	g.Meta  `path:"/extract-result" method:"POST" tags:"LLM" summary:"获取处理结果"`
	Voucher string `json:"voucher" dc:"凭证:用户获取处理结果"`
}

type ExtractResultRes struct {
	g.Meta                 `mime:"application/json" example:"{}"`
	Most_possible_category string         `json:"mostPossibleCategory" dc:"最可能的分类"`
	Information            v1.Information `json:"information"          dc:"知识信息"`
	Schedule               v1.Schedule    `json:"schedule"             dc:"日程信息"`
}
