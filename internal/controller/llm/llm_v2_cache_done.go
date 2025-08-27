package llm

import (
	"context"

	"github.com/gogf/gf/v2/errors/gcode"
	"github.com/gogf/gf/v2/errors/gerror"
	"github.com/gogf/gf/v2/frame/g"

	"MemoFluxServer/api/llm/v2"
)

func (c *ControllerV2) CacheDone(ctx context.Context, req *v2.CacheDoneReq) (res *v2.CacheDoneRes, err error) {

	_, err = g.Redis().Do(ctx, "DEL", req.Voucher)
	if err != nil {
		return nil, gerror.NewCode(gcode.CodeInternalError, err.Error())
	}
	return &v2.CacheDoneRes{Done: true}, nil
}
