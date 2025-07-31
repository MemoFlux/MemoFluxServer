package middleware

import (
	"github.com/gogf/gf/v2/frame/g"
	"github.com/gogf/gf/v2/net/ghttp"
	"time"
)

// MiddlewareTiming 是一个计算接口耗时的中间件
func MiddlewareTiming(r *ghttp.Request) {
	// 记录请求开始时间
	start := time.Now()

	// 执行后续的请求处理逻辑（包括其他中间件和控制器）
	r.Middleware.Next()

	// 计算耗时
	duration := time.Since(start)

	// 在日志中记录接口路径、方法和耗时
	g.Log().Infof(r.Context(), "API Latency: %s %s %s", r.Method, r.URL.Path, duration)
}
