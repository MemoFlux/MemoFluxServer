package v2

import "github.com/gogf/gf/v2/frame/g"

type GeneralReq struct {
	g.Meta  `path:"/General" method:"post" tags:"LLM" summary:"通用请求"`
	Id      *string  `json:"id" v:"omitempty" description:"唯一标识符"`
	Tags    []string `json:"tags" description:"标签"`
	Content string   `json:"content" description:"<UNK>"`
	Isimage int      `json:"isimage" description:"<UNK>"`
}

type GeneralRes struct {
	g.Meta  `mime:"application/json" example:"{}"`
	Voucher string `json:"voucher" dc:"凭证:用户获取处理结果"`
}
