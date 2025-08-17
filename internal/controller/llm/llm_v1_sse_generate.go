package llm

import (
	v1 "MemoFluxServer/api/llm/v1"
	"MemoFluxServer/internal/service"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"sync" // 【新增】导入 sync 包，用于并发控制

	"github.com/gogf/gf/v2/frame/g"
	"github.com/sashabaranov/go-openai"
)

// StreamedChunk 是一个自定义结构体，用于在 channel 中传递来自不同 LLM 流的数据。
// 它包含一个 ID 用来区分数据源，以及一个 error 字段用于错误传递。
type StreamedChunk struct {
	ID      string // 流的唯一标识符 (例如: "knowledge-base", "creative-writing")
	Content string // 从 LLM 返回的实际数据块
	Err     error  // 如果此流中发生错误，则记录错误信息
}

// MultiplexSSE 会并发调用三个 LLM 流，并将它们的结果合并到单个 SSE 响应中。
func (c *ControllerV1) SSEGenerate(ctx context.Context, req *v1.SSEGenerateReq) (res *v1.SSEGenerateRes, err error) {
	r := g.RequestFromCtx(ctx)
	writer := r.Response.Writer
	flusher, ok := writer.ResponseWriter.(http.Flusher)
	if !ok {
		// 如果ResponseWriter不支持Flusher，则无法进行流式传输，直接返回错误。
		return nil, fmt.Errorf("流式传输不受支持：ResponseWriter 未实现 http.Flusher 接口")
	}

	// --- 1. 配置加载 (与你的示例相同) ---
	apikey, err := g.Cfg().Get(ctx, "llm.apikey")
	if err != nil {
		return nil, fmt.Errorf("LLM API Key 未配置: %v", err)
	}
	baseurl, err := g.Cfg().Get(ctx, "llm.baseurl")
	if err != nil {
		return nil, fmt.Errorf("Base Url 未配置: %v", err)
	}
	modelName, err := g.Cfg().Get(ctx, "llm.model")
	if err != nil {
		return nil, fmt.Errorf("Model Name 未配置: %v", err)
	}
	config := openai.DefaultConfig(apikey.String())
	config.BaseURL = baseurl.String()
	client := openai.NewClientWithConfig(config)

	// --- 2. 设置 SSE 响应头 ---
	// 这是启动SSE流的必要步骤
	writer.Header().Set("Content-Type", "text/event-stream")
	writer.Header().Set("Cache-Control", "no-cache")
	writer.Header().Set("Connection", "keep-alive")
	writer.Header().Set("Access-Control-Allow-Origin", "*") // 方便前端跨域调试

	// --- 3. 并发控制设置 ---
	var wg sync.WaitGroup
	// 创建一个带缓冲的 channel，用于从所有 goroutine 接收数据块。
	dataChan := make(chan StreamedChunk, 3)

	knowledgeSchema, err := service.StructToJSONSchema(&v1.Knowledge{})
	if err != nil {
		return nil, fmt.Errorf("生成 Knowledge Schema 失败: %v", err)
	}
	scheduleSchema, err := service.StructToJSONSchema(&v1.Schedule{})
	if err != nil {
		return nil, fmt.Errorf("生成 Schedule Schema 失败: %v", err)
	}

	// --- 4. 定义三个不同的 LLM 请求 ---
	// 在真实应用中，这些请求的内容应该基于前端传入的 `req` 动态生成。
	requests := map[string]openai.ChatCompletionRequest{
		"knowledge": { // ID 1: 知识库搜索
			Model: modelName.String(),
			Messages: []openai.ChatCompletionMessage{
				{
					Role:    openai.ChatMessageRoleSystem,
					Content: "你是一个知识图谱构建专家。始终使用和用户输入的文本相同的语言进行回答。请使用中文回复。",
				},
				{
					Role: openai.ChatMessageRoleUser,
					MultiContent: []openai.ChatMessagePart{
						{
							Type:     openai.ChatMessagePartTypeImageURL,
							ImageURL: &openai.ChatMessageImageURL{URL: "data:image/png;base64," + req.Content},
						},
					},
				},
			},
			Stream: true,
			ResponseFormat: &openai.ChatCompletionResponseFormat{
				Type: "json_schema",
				JSONSchema: &openai.ChatCompletionResponseFormatJSONSchema{
					Name:   "knowledge",
					Strict: true,
					Schema: knowledgeSchema, // 使用预定义的 JSON Schema
				},
			},
		},
		"schedule": { // ID 2: 创意写作
			Model: modelName.String(),
			Messages: []openai.ChatCompletionMessage{
				{
					Role:    openai.ChatMessageRoleSystem,
					Content: "你是一个日程管理专家，请根据用户输入的文本，生成一个日程安排。始终使用和用户输入的文本相同的语言进行回答。",
				},
				{
					Role: openai.ChatMessageRoleUser,
					MultiContent: []openai.ChatMessagePart{
						{
							Type: openai.ChatMessagePartTypeImageURL,
							ImageURL: &openai.ChatMessageImageURL{
								URL: "data:image/png;base64," + req.Content,
							},
						},
					},
				},
				{
					Role:    openai.ChatMessageRoleSystem,
					Content: " 注：如果图片中没有日程相关的安排，将category设置为\"未分类\"",
				},
			},
			Stream: true,
			ResponseFormat: &openai.ChatCompletionResponseFormat{
				Type: "json_schema",
				JSONSchema: &openai.ChatCompletionResponseFormatJSONSchema{
					Name:   "schedule",
					Strict: true,
					Schema: scheduleSchema, // 使用预定义的 JSON Schema
				},
			},
		},
		"most_possible_sort": { // ID 3: 代码生成
			Model: modelName.String(),
			Messages: []openai.ChatCompletionMessage{
				{
					Role:    openai.ChatMessageRoleSystem,
					Content: "将下列内容进行场景分类，仅输出分类结果。你只能在INFORMATION,SCHEDULE,OTHER这三个分类中选择一个。",
				},
				{
					Role: openai.ChatMessageRoleUser,
					MultiContent: []openai.ChatMessagePart{
						{
							Type:     openai.ChatMessagePartTypeImageURL,
							ImageURL: &openai.ChatMessageImageURL{URL: "data:image/png;base64," + req.Content},
						},
					},
				},
			},
			Stream: true,
		},
	}

	// --- 5. 为每个 LLM 调用启动一个 Goroutine ---
	for id, llmReq := range requests {
		wg.Add(1) // 每启动一个 goroutine，WaitGroup 的计数器加 1
		go c.callAndStreamLLM(ctx, client, id, llmReq, dataChan, &wg)
	}

	// --- 6. 启动一个 Goroutine，用于在所有流结束后关闭 channel ---
	// 这是一个标准模式：当所有工作 goroutine 完成后（wg.Wait()解除阻塞），关闭 channel。
	// 关闭 channel 会让下面的 for...range 循环自动结束。
	go func() {
		wg.Wait()
		close(dataChan)
	}()

	// 发送一个初始的 'open' 事件，告知客户端连接已建立
	fmt.Fprintf(writer, "event: open\n")
	fmt.Fprintf(writer, "data: %s\n\n", `{"status":"流式传输已开始"}`)
	flusher.Flush()

	// 这个循环会一直读取 channel，直到 channel 被关闭
	for chunk := range dataChan {
		// 如果客户端断开连接，及时中止
		if r.Context().Err() != nil {
			g.Log().Info(ctx, "客户端已断开连接，停止推流。")
			break
		}

		var eventData g.Map
		eventType := "chunk" // 默认事件类型为 "chunk"

		if chunk.Err != nil {
			// 如果 chunk 包含了错误信息
			eventType = "error"
			eventData = g.Map{
				"id":      chunk.ID, // 标明是哪个流出错了
				"error":   true,
				"message": chunk.Err.Error(),
			}
			g.Log().Errorf(ctx, "流 '%s' 发生错误: %v", chunk.ID, chunk.Err)
		} else {
			// 如果是正常的数据块
			eventData = g.Map{
				"id":    chunk.ID, // 标明这个数据块来自哪个流
				"chunk": chunk.Content,
			}
		}

		jsonData, err := json.Marshal(eventData)
		if err != nil {
			// 这是服务器端的序列化错误，记录日志后跳过
			g.Log().Errorf(ctx, "序列化 SSE 数据失败: %v", err)
			continue
		}

		// 按照 SSE 格式将事件写入响应
		fmt.Fprintf(writer, "event: %s\n", eventType)
		fmt.Fprintf(writer, "data: %s\n\n", jsonData)
		flusher.Flush() // 立刻将数据发送给客户端
	}

	// 循环结束后，说明所有流都已完成。发送最终的 'done' 事件。
	fmt.Fprintf(writer, "event: done\n")
	fmt.Fprintf(writer, "data: %s\n\n", `{"done":true}`)
	flusher.Flush()

	// 因为响应已经通过 ResponseWriter 手动写入，所以这里返回 (nil, nil)
	return nil, nil
}

// callAndStreamLLM 是一个辅助函数，负责执行单次 LLM 流式调用。
// 它会在独立的 goroutine 中运行，并将结果或错误通过 channel 发送回去。
func (c *ControllerV1) callAndStreamLLM(
	ctx context.Context,
	client *openai.Client,
	id string,
	req openai.ChatCompletionRequest,
	dataChan chan<- StreamedChunk, // 注意是只写 channel
	wg *sync.WaitGroup,
) {
	// defer 确保在函数退出时，无论正常结束还是异常退出，都会通知 WaitGroup
	defer wg.Done()

	stream, err := client.CreateChatCompletionStream(ctx, req)
	if err != nil {
		// 如果创建流就失败了，直接将错误发送到 channel
		dataChan <- StreamedChunk{ID: id, Err: fmt.Errorf("创建流失败: %w", err)}
		return
	}
	defer stream.Close()

	for {
		resp, recvErr := stream.Recv()

		// 检查上下文是否被取消（例如客户端断开连接）
		if errors.Is(recvErr, context.Canceled) {
			g.Log().Infof(ctx, "流 '%s' 的上下文被取消，关闭。", id)
			return // 正常退出
		}

		if recvErr != nil {
			// 如果接收到 EOF 错误，说明流正常结束
			if errors.Is(recvErr, io.EOF) {
				return // 正常退出
			}
			// 其他任何错误都是真实问题，需要上报
			dataChan <- StreamedChunk{ID: id, Err: fmt.Errorf("流接收错误: %w", recvErr)}
			return
		}

		if len(resp.Choices) > 0 {
			content := resp.Choices[0].Delta.Content
			if content != "" {
				// 将获取到的数据块连同其 ID 发送到 channel
				dataChan <- StreamedChunk{ID: id, Content: content}
			}
		}
	}
}
