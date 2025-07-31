// =================================================================================
// Code generated and maintained by GoFrame CLI tool. DO NOT EDIT.
// =================================================================================

package llm

import (
	"context"

	"MemoFluxServer/api/llm/v1"
)

type ILlmV1 interface {
	General(ctx context.Context, req *v1.GeneralReq) (res *v1.GeneralRes, err error)
}
