package task

import (
	"MemoFluxServer/internal/dao"
	"MemoFluxServer/internal/model/entity"
	"MemoFluxServer/internal/service"
	"context"
	"log"
	"sync"

	"github.com/gogf/gf/v2/frame/g"
)

func ResetUserPlanCost() {
	ctx := context.Background()
	var users []entity.User
	err := dao.User.Ctx(ctx).Scan(&users)

	if err != nil {
		g.Log().Errorf(ctx, "Reset-Plan:Failed to fetch users: %v", err)
		return
	}

	var wg sync.WaitGroup

	for _, user := range users {

		wg.Go(func() {
			// 处理每个用户的计划设置
			if err := service.PlanSetUser(ctx, user.Uid, user.Plan); err != nil {
				log.Printf("Failed to set plan for user %d: %v", user.Uid, err)
			}
		})
	}

}
