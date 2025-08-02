package main

import (
	_ "MemoFluxServer/internal/packed"

	"github.com/gogf/gf/v2/os/gctx"

	"MemoFluxServer/internal/cmd"
)

func main() {
	cmd.Main.Run(gctx.GetInitCtx())
}
