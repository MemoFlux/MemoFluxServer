package user

import (
	"MemoFluxServer/internal/dao"
	"MemoFluxServer/internal/model/do"
	"context"
	"fmt"

	"github.com/gogf/gf/v2/errors/gcode"
	"github.com/gogf/gf/v2/errors/gerror"
	"github.com/gogf/gf/v2/frame/g"

	"MemoFluxServer/api/user/v1"
)

func (c *ControllerV1) CreateUser(ctx context.Context, req *v1.CreateUserReq) (res *v1.CreateUserRes, err error) {
	// 仅指定需要的列，避免将 uid 写入（适配 GENERATED ALWAYS/自增主键）
	userId, err := dao.User.Ctx(ctx).InsertAndGetId(do.User{Username: req.Username, Plan: 0})
	if err != nil {
		err = gerror.NewCode(gcode.CodeDbOperationError, "用户创建失败")
		return
	}
	res = &v1.CreateUserRes{
		UserId: fmt.Sprintf("%d", userId),
		Plan:   0,
	}
	// 正确的格式化输出：打印 uid、plan 与 username
	g.Log().Infof(ctx, "User created: uid=%d plan=%d username=%s", userId, 0, req.Username)
	return
}
