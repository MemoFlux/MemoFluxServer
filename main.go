package main

import (
	_ "MemoFluxServer/internal/packed"

	"github.com/gogf/gf/v2/os/gctx"

	"MemoFluxServer/internal/cmd"

	_ "github.com/gogf/gf/contrib/drivers/pgsql/v2"
	_ "github.com/gogf/gf/contrib/nosql/redis/v2"
)

func main() {
	cmd.Main.Run(gctx.GetInitCtx())
}
