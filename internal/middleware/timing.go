package middleware

import (
	"log/slog"
	"time"

	"github.com/gogf/gf/v2/frame/g"
	"github.com/gogf/gf/v2/net/ghttp"
	slogbetterstack "github.com/samber/slog-betterstack"
)

var bsLogger = slog.New(
	slogbetterstack.Option{
		Token:    "LHHu24KiguxDQX4NgugUmkuR",
		Endpoint: "https://s1490890.eu-nbg-2.betterstackdata.com/",
	}.NewBetterstackHandler(),
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
	g.Log().Info(r.Context(), "Method", r.Method, "Endpoint", r.URL.Path, "duration", duration)

	bsLogger.
		With("method", r.Method).
		With("endpoint", r.URL.Path).
		With("duration", duration.String()).
		Info("Request completed")
}
