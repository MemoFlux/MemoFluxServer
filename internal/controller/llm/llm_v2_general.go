package llm

import (
	v1 "MemoFluxServer/api/llm/v1"
	"MemoFluxServer/internal/service"
	"context"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"sync"
	"time"

	"MemoFluxServer/api/llm/v2"

	"github.com/gogf/gf/v2/frame/g"
	"github.com/sashabaranov/go-openai"
)

type CallChan struct {
	Id      string
	Content string
	Err     error
}

func (c *ControllerV2) General(ctx context.Context, req *v2.GeneralReq) (res *v2.GeneralRes, err error) {
	var data string
	if req.Id == nil {
		data = fmt.Sprintf("%s-%d", "0", time.Now().UnixNano())
	} else {
		data = fmt.Sprintf("%s-%d", *req.Id, time.Now().UnixNano())
	}

	hash := sha256.Sum256([]byte(data))
	voucher := fmt.Sprintf("%x", hash) //转换为16进制字符串
	//兜底用户ID

	go func() {
		apikey, err := g.Cfg().Get(ctx, "llm.apikey")
		if err != nil {
			g.Log().Errorf(ctx, fmt.Sprintf("LLM API Key 未配置: %v", err))
		}
		baseurl, err := g.Cfg().Get(ctx, "llm.baseurl")
		if err != nil {
			g.Log().Errorf(ctx, fmt.Sprintf("Base Url 未配置: %v", err))
		}
		modelName, err := g.Cfg().Get(ctx, "llm.model")
		if err != nil {
			g.Log().Errorf(ctx, fmt.Sprintf("Model Name 未配置: %v", err))
		}
		config := openai.DefaultConfig(apikey.String())
		config.BaseURL = baseurl.String()
		client := openai.NewClientWithConfig(config)

		var wg sync.WaitGroup
		dataChan := make(chan CallChan, 3)

		knowledgeSchema, _ := service.StructToJSONSchema(&v1.Information{})
		scheduleSchema, _ := service.StructToJSONSchema(&v1.Schedule{})

		requests := map[string]openai.ChatCompletionRequest{
			"information": { // ID 1: 知识库搜索
				Model: modelName.String(),
				Messages: []openai.ChatCompletionMessage{
					{
						Role:    openai.ChatMessageRoleSystem,
						Content: "你是一个知识图谱构建专家。如果存在内容是外语，你有义务进行严谨的翻译。始终使用中文文本进行回答。",
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
						Content: "你是一个日程管理专家，请根据用户输入的文本，生成一个日程安排，如果存在内容是外语，你有义务进行严谨的翻译。始终使用中文文本进行回答。",
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
			},
		}
		routine_ctx := context.TODO()
		for id, llmReq := range requests {
			wg.Go(func() {
				callAndNonStreamLLM(routine_ctx, client, id, llmReq, dataChan)
			})
		}
		wg.Wait()
		close(dataChan)

		var response v1.GeneralRes
		for chunk := range dataChan {
			switch chunk.Id {
			case "most_possible_sort":
				if chunk.Err != nil {
					g.Log().Errorf(routine_ctx, "分类调用失败: %v", chunk.Err)
					break
				}
				response.Most_possible_category = chunk.Content
			case "schedule":
				if chunk.Err != nil {
					g.Log().Errorf(routine_ctx, "日程调用失败: %v", chunk.Err)
					break
				}
				err := json.Unmarshal([]byte(chunk.Content), &response.Schedule)
				if err != nil {
					g.Log().Errorf(routine_ctx, "日程JSON 解析失败: %v", err)
					break
				}
			case "information":
				if chunk.Err != nil {
					g.Log().Errorf(routine_ctx, "知识调用失败: %v", chunk.Err)
					break
				}
				err := json.Unmarshal([]byte(chunk.Content), &response.Information)
				if err != nil {
					g.Log().Errorf(routine_ctx, "知识JSON 解析失败: %v", err)
					break
				}
			}
		}

		if response.Most_possible_category == "" || len(response.Schedule.Tasks) == 0 || len(response.Information.InformationItems) == 0 {
			g.Log().Error(routine_ctx, "存在调用失败或未返回有效内容")
			_, _ = g.Redis().Do(routine_ctx, "SET", voucher, "处理失败")
			return
		}

		_, err = g.Redis().Do(routine_ctx, "SET", voucher, response, "EX", 3600*24)
		if err != nil {
			g.Log().Errorf(routine_ctx, "缓存处理结果失败: %v", err)
			_, _ = g.Redis().Do(routine_ctx, "SET", voucher, "缓存错误")
			return
		}
	}()

	return &v2.GeneralRes{
		Voucher: voucher,
	}, nil
}

func callAndNonStreamLLM(
	ctx context.Context,
	client *openai.Client,
	id string,
	req openai.ChatCompletionRequest,
	dataChan chan CallChan, // 注意是只写 channel
) {
	// defer 确保在函数退出时，无论正常结束还是异常退出，都会通知 WaitGroup

	resp, err := client.CreateChatCompletion(ctx, req)
	if err != nil {
		// 如果请求失败，发送错误到 channel
		dataChan <- CallChan{Id: id, Content: "", Err: err}
		return
	}

	// 处理响应，提取内容并通过 channel 发送
	if len(resp.Choices) > 0 {
		content := resp.Choices[0].Message.Content
		if content != "" {
			// 将获取到的完整内容发送到 channel
			g.Log().Debugf(ctx, "LLM 调用 '%s' 成功: %s", id, content)
			dataChan <- CallChan{Id: id, Content: content, Err: nil}
		}
	}
}
