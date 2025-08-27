// =================================================================================
// Code generated and maintained by GoFrame CLI tool. DO NOT EDIT.
// =================================================================================

package llm

import (
	"context"

	"MemoFluxServer/api/llm/v1"
	"MemoFluxServer/api/llm/v2"
)

type ILlmV1 interface {
	General(ctx context.Context, req *v1.GeneralReq) (res *v1.GeneralRes, err error)
	SSEGenerate(ctx context.Context, req *v1.SSEGenerateReq) (res *v1.SSEGenerateRes, err error)
}

type ILlmV2 interface {
	CacheDone(ctx context.Context, req *v2.CacheDoneReq) (res *v2.CacheDoneRes, err error)
	General(ctx context.Context, req *v2.GeneralReq) (res *v2.GeneralRes, err error)
	ExtractResult(ctx context.Context, req *v2.ExtractResultReq) (res *v2.ExtractResultRes, err error)
}
