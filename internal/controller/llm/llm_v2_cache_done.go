package llm

import (
	"context"

	"github.com/gogf/gf/v2/errors/gcode"
	"github.com/gogf/gf/v2/errors/gerror"

	"MemoFluxServer/api/llm/v2"
)

func (c *ControllerV2) CacheDone(ctx context.Context, req *v2.CacheDoneReq) (res *v2.CacheDoneRes, err error) {
	return nil, gerror.NewCode(gcode.CodeNotImplemented)
}
