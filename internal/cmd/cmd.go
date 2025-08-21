package cmd

import (
	"MemoFluxServer/internal/controller/llm"
	"MemoFluxServer/internal/controller/user"
	"MemoFluxServer/internal/middleware"
	"context"

	"github.com/gogf/gf/v2/frame/g"
	"github.com/gogf/gf/v2/net/ghttp"
	"github.com/gogf/gf/v2/os/gcmd"

	"MemoFluxServer/internal/controller/hello"
)

var (
	Main = gcmd.Command{
		Name:  "main",
		Usage: "main",
		Brief: "start http server",
		Func: func(ctx context.Context, parser *gcmd.Parser) (err error) {
			s := g.Server()
			s.SetPort(8000)
			s.SetSwaggerPath("/swagger/")
			s.SetOpenApiPath("/openapi/")
			s.Use(middleware.FormateMiddleware)
			s.Use(middleware.MiddlewareTiming)
			s.Group("/", func(group *ghttp.RouterGroup) {
				group.Middleware(ghttp.MiddlewareHandlerResponse)
				group.Bind(
					hello.NewV1(),
					llm.NewV1(),
					user.NewV1(),
				)
			})
			s.Run()
			return nil
		},
	}
)
