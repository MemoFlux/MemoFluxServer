package v2

import "github.com/gogf/gf/v2/frame/g"

type CacheDoneReq struct {
	g.Meta  `path:"/cache/done" method:"POST" tags:"LLM" summary:"获取处理结果"`
	Voucher string `json:"voucher" dc:"凭证"`
}

type CacheDoneRes struct {
	g.Meta `mime:"application/json" example:"{}"`
	Done   bool `json:"done" dc:"是否处理完成"`
}
