package middleware

import (
	"encoding/json"

	"github.com/gogf/gf/v2/frame/g"
	"github.com/gogf/gf/v2/net/ghttp"
)

func FormateMiddleware(r *ghttp.Request) {
	r.Middleware.Next() // 执行后续处理（调用具体接口）

	// 取响应缓存
	body := r.Response.Buffer()

	if len(body) == 0 {
		// 空响应，不做处理
		return
	}

	// 定义一个通用结构，用于解析 code,message,data
	var resp struct {
		Code    interface{}     `json:"code"`
		Message interface{}     `json:"message"`
		Data    json.RawMessage `json:"data"`
	}

	err := json.Unmarshal(body, &resp)
	if err != nil {
		// 如果解析失败，说明不是标准结构，直接返回原内容
		return
	}

	// 如果 data 字段为空，也直接返回原内容
	if len(resp.Data) == 0 || string(resp.Data) == "null" {
		return
	}
	if r.Response.Header().Get("Content-Type") == "image/png" {
		return // 不处理图片响应
	}

	// 清空已有响应内容，写入 data 内容
	r.Response.ClearBuffer()
	r.Response.Write(resp.Data)
	g.Log().Debugf(r.Context(), "Response Data: %s", resp.Data)

}
