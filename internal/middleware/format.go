package middleware

import (
	"encoding/json"

	"github.com/gogf/gf/v2/frame/g"
	"github.com/gogf/gf/v2/net/ghttp"
)

// FormateMiddleware 是一个响应格式化中间件。
// 它会拦截标准的 API 响应，如果响应体符合 {"code": xxx, "message": "xxx", "data": ...} 的结构，
// 它将提取 "data" 字段的内容作为最终的响应体返回给客户端。
// 这样可以简化客户端对响应数据的处理。
func FormateMiddleware(r *ghttp.Request) {
	// 执行后续的请求处理逻辑（例如，调用具体的API接口）。
	// 响应内容将在执行后被捕获。
	r.Middleware.Next()

	// 获取响应缓存，即接口返回的原始数据。
	body := r.Response.Buffer()

	// 如果响应体为空，则无需进行任何处理，直接返回。
	if len(body) == 0 {
		return
	}

	// 定义一个通用的响应结构，用于解析 JSON 响应中的 code, message, 和 data 字段。
	// data 字段使用 json.RawMessage 类型，以避免二次编解码带来的性能损耗和类型问题。
	var resp struct {
		Code    interface{}     `json:"code"`
		Message interface{}     `json:"message"`
		Data    json.RawMessage `json:"data"`
	}

	// 尝试将响应体 unmarshal 到定义的结构中。
	err := json.Unmarshal(body, &resp)
	if err != nil {
		// 如果解析失败，说明响应体不是我们预期的标准 JSON 结构。
		// 在这种情况下，我们不进行任何处理，直接返回原始响应内容。
		return
	}

	// 如果 data 字段本身为空或为 "null" 字符串，也直接返回原始响应，不进行包装剥离。
	if len(resp.Data) == 0 || string(resp.Data) == "null" {
		return
	}
	// 如果响应内容是图片等非 JSON 类型，不进行处理。
	if r.Response.Header().Get("Content-Type") == "image/png" {
		return // 不处理图片响应
	}

	// 清空原始的响应缓冲区。
	r.Response.ClearBuffer()
	// 将提取出的 data 内容写入响应体，作为最终返回给客户端的数据。
	r.Response.Write(resp.Data)
	g.Log().Debugf(r.Context(), "Response Data: %s", resp.Data)

}
