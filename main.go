package main

import (
	_ "MemoFluxServer/internal/packed"

	"MemoFluxServer/internal/cmd"

	"github.com/gogf/gf/v2/os/gctx"
	"github.com/gogf/gf/v2/os/glog"

	_ "github.com/gogf/gf/contrib/drivers/pgsql/v2"
	_ "github.com/gogf/gf/contrib/nosql/redis/v2"
)

func main() {

	glog.SetDefaultHandler(glog.HandlerStructure)
	cmd.Main.Run(gctx.GetInitCtx())
}
