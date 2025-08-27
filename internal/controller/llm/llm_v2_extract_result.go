package llm

import (
	"context"
	"encoding/json"

	"MemoFluxServer/api/llm/v2"

	"github.com/gogf/gf/v2/errors/gcode"
	"github.com/gogf/gf/v2/errors/gerror"
	"github.com/gogf/gf/v2/frame/g"
)

func (c *ControllerV2) ExtractResult(ctx context.Context, req *v2.ExtractResultReq) (res *v2.ExtractResultRes, err error) {

	value, _ := g.Redis().Get(ctx, req.Voucher)
	var response v2.ExtractResultRes

	err = json.Unmarshal([]byte(value.String()), &response)

	if err != nil {
		return nil, gerror.NewCode(gcode.CodeInternalError, "结果解析失败: "+value.String())
	}
	return &response, nil
}
