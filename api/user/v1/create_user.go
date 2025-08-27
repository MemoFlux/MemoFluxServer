package v1

import "github.com/gogf/gf/v2/frame/g"

type CreateUserReq struct {
	g.Meta   `path:"/user/create" method:"post" tag:"user" summary:"create a user"`
	Username string `json:"username" v:"required#用户名不能为空"`
}

type CreateUserRes struct {
	UserId string `json:"user_id"`
	Plan   int    `json:"plan" desc:"用户计划类型，0:免费版, 1:专业版, 2:企业版"`
}
