package service

import (
	"context"
	"fmt"
	"strconv"
	"time"

	"github.com/gogf/gf/v2/frame/g"
)

func PlanSetUser(ctx context.Context, user_id int64, plan int) error {

	key := getRedisKey(user_id, plan)

	// 计算距离北京时间下一次 00:00 的剩余秒数，并在写入时设置过期时间，确保每天 24:00 重置
	ttl := timeUntilBeijingMidnight()
	cost := getPlanCost(plan)

	// 使用通用指令设置过期（EX 秒）以保证跨版本兼容
	_, err := g.Redis().Do(ctx, "SET", key, cost, "EX", int64(ttl.Seconds()))
	if err != nil {
		return err
	}
	return nil
}

func PlanCostDecrease(ctx context.Context, userId int64, leavePlan int, cost int) (int, error) {
	key := getRedisKey(userId, leavePlan)
	currentCost, err := getCurrentCost(ctx, userId, leavePlan)
	if err != nil {
		return 0, err
	}
	if currentCost >= cost {
		_, err := g.Redis().Do(ctx, "DECRBY", key, cost)
		if err != nil {
			g.Log().Errorf(ctx, "Redis DECRBY error: %v", err)
			return 0, err
		}
		g.Log().Infof(ctx, "用户消耗 %d 点数，当前剩余点数：%d", cost, currentCost-cost)
	}
	currentCost, err = getCurrentCost(ctx, userId, leavePlan)
	if err != nil {
		g.Log().Errorf(ctx, "点数写成功，获取当前点数失败: %v", err)
		return 0, err
	}
	return currentCost, nil
}

func getRedisKey(userId int64, leavePlan int) string {
	return fmt.Sprintf("user:%d:leave_plan:%d", userId, leavePlan)
}

func getCurrentCost(ctx context.Context, userId int64, leavePlan int) (int, error) {
	key := getRedisKey(userId, leavePlan)
	currentCostStr, err := g.Redis().Do(ctx, "GET", key)
	if err != nil {
		return 0, err
	}
	currentCost, err := strconv.Atoi(fmt.Sprintf("%v", currentCostStr))
	if err != nil {
		return 0, err
	}
	return currentCost, nil
}

// 计算距离北京时间下一次 00:00 的持续时间
func timeUntilBeijingMidnight() time.Duration {
	loc, err := time.LoadLocation("Asia/Shanghai")
	if err != nil {
		// 退化到本地时区，避免因时区加载失败导致零 TTL
		loc = time.Local
	}
	now := time.Now().In(loc)
	y, m, d := now.Date()
	nextMidnight := time.Date(y, m, d+1, 0, 0, 0, 0, loc)
	return nextMidnight.Sub(now)
}

func getPlanCost(plan int) int {
	switch plan {
	case 0:
		return 10
	case 1:
		return 50
	case 2:
		return 100
	case 3:
		return 200
	default:
		return 10
	}
}
