package llm

import (
	"MemoFluxServer/internal/service"
	"context"
	"encoding/json"
	"fmt"
	"github.com/gogf/gf/v2/frame/g"
	"github.com/sashabaranov/go-openai"
	"log"
	"strings"
	"sync"

	"github.com/gogf/gf/v2/errors/gcode"
	"github.com/gogf/gf/v2/errors/gerror"

	"MemoFluxServer/api/llm/v1"
)

func (c *ControllerV1) General(ctx context.Context, req *v1.GeneralReq) (res *v1.GeneralRes, err error) {

	var wg sync.WaitGroup
	//New LLM Client
	apikey, err := g.Cfg().Get(ctx, "llm.apikey")
	if err != nil {
		return nil, gerror.NewCode(gcode.CodeInvalidParameter, "LLM API Key 未配置: "+err.Error())
	}
	baseurl, err := g.Cfg().Get(ctx, "llm.baseurl")
	if err != nil {
		return nil, gerror.NewCode(gcode.CodeInvalidParameter, "Base Url 未配置: "+err.Error())
	}
	modelName, err := g.Cfg().Get(ctx, "llm.model")
	if err != nil {
		return nil, gerror.NewCode(gcode.CodeInvalidParameter, "Model Name 未配置: "+err.Error())
	}
	client := service.NewLLMClient(apikey.String(), baseurl.String())
	g.Log().Debugf(ctx, "LLM Model: %v", modelName.String())
	//Go struct to JSON
	schedule_str, err := service.GenerateStructSchema(v1.Schedule{})
	knowledge_str, err := service.GenerateStructSchema(v1.Knowledge{})

	//Make chan
	schedule_chan := make(chan string)
	knowledge_chan := make(chan string)
	sort_chan := make(chan string)

	wg.Add(3)
	go Schedule(client, modelName.String(), req.Content, schedule_str, &wg, schedule_chan)
	go Knowledge(client, modelName.String(), req.Content, knowledge_str, &wg, knowledge_chan)
	go Sort(client, modelName.String(), req.Content, &wg, sort_chan)

	schedule_result := <-schedule_chan
	knowledge_result := <-knowledge_chan
	sort_result := <-sort_chan
	g.Log().Debugf(ctx, "清洗结果 Knowledge: %v", knowledge_result)
	g.Log().Debugf(ctx, "清洗结果 Schedule: %v", schedule_result)
	g.Log().Debugf(ctx, "清洗结果 Sort: %v", sort_result)
	if err != nil {
		log.Fatalf("LLM 生成失败: %v", err)
	}
	var schedule_struct v1.Schedule
	var knowledge_struct v1.Knowledge

	err = json.Unmarshal([]byte(schedule_result), &schedule_struct)
	if err != nil {
		// 如果 JSON 格式错误，或者类型不匹配，这里会捕获到错误
		log.Fatalf("日程JSON 解析失败: %v", err)
		g.Log().Debugf(ctx, "Schedule: %v", schedule_result)
	}
	err = json.Unmarshal([]byte(knowledge_result), &knowledge_struct)
	if err != nil {
		// 如果 JSON 格式错误，或者类型不匹配，这里会捕获到错误
		log.Fatalf("知识JSON 解析失败: %v", err)
		g.Log().Debugf(ctx, "Knowledge: %v", schedule_result)
	}

	return &v1.GeneralRes{
		Most_possible_category: sort_result,
		Schedule:               schedule_struct,
		Knowledge:              knowledge_struct,
	}, nil
}

func Schedule(client *openai.Client, modelName string, content string, schema string, wg *sync.WaitGroup, resultchan chan string) {
	defer wg.Done()
	resp, err := client.CreateChatCompletion(
		context.Background(),
		openai.ChatCompletionRequest{
			Model: modelName,
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
								// 确保 MIME 类型正确，例如 image/jpeg 或 image/png
								URL: "data:image/png;base64," + content,
							},
						},
					},
				},
				{
					Role:    openai.ChatMessageRoleSystem,
					Content: "输出结果严格遵从以下 JSON Schema",
				},
				{
					Role:    openai.ChatMessageRoleSystem,
					Content: schema,
				},
				{
					Role:    openai.ChatMessageRoleSystem,
					Content: " 注：如果图片中没有日程相关的安排，将category设置为\"未分类\"",
				},
			},
		},
	)
	if err != nil {
		fmt.Printf("请求出错: %v\n", err)
		resultchan <- fmt.Sprintf("请求出错: %v", err)
	}
	fmt.Println("🧠 Moonshot 回复：", resp.Choices[0].Message.Content)
	s := resp.Choices[0].Message.Content
	s = strings.TrimPrefix(s, "```json")
	// 移除后缀
	s = strings.TrimSuffix(s, "```")
	s = strings.TrimPrefix(s, "[")
	s = strings.TrimSuffix(s, "]")
	resultchan <- s
}

func Knowledge(client *openai.Client, modelName string, content string, schema string, wg *sync.WaitGroup, resultchan chan string) {
	defer wg.Done()
	resp, err := client.CreateChatCompletion(
		context.Background(),
		openai.ChatCompletionRequest{
			Model: modelName,
			Messages: []openai.ChatCompletionMessage{
				{
					Role:    openai.ChatMessageRoleSystem,
					Content: "你是一个知识图谱构建专家。始终使用和用户输入的文本相同的语言进行回答。请使用中文回复。",
				},
				{
					Role: openai.ChatMessageRoleUser,
					MultiContent: []openai.ChatMessagePart{
						{
							Type: openai.ChatMessagePartTypeImageURL,
							ImageURL: &openai.ChatMessageImageURL{
								// 确保 MIME 类型正确，例如 image/jpeg 或 image/png
								URL: "data:image/png;base64," + content,
							},
						},
					},
				},
				{
					Role:    openai.ChatMessageRoleSystem,
					Content: "输出结果严格遵从以下 JSON Schema",
				},
				{
					Role:    openai.ChatMessageRoleSystem,
					Content: schema,
				},
			},
		},
	)
	if err != nil {
		fmt.Printf("请求出错: %v\n", err)
		resultchan <- fmt.Sprintf("<UNK>: %v", err)
	}
	fmt.Println("🧠 Moonshot 回复：", resp.Choices[0].Message.Content)
	s := resp.Choices[0].Message.Content
	s = strings.TrimPrefix(s, "```json")
	// 移除后缀
	s = strings.TrimSuffix(s, "```")
	s = strings.TrimPrefix(s, "[")
	s = strings.TrimSuffix(s, "]")
	resultchan <- s
}

func Sort(client *openai.Client, modelName string, content string, wg *sync.WaitGroup, resultchan chan string) {
	defer wg.Done()
	resp, err := client.CreateChatCompletion(
		context.Background(),
		openai.ChatCompletionRequest{
			Model: modelName,
			Messages: []openai.ChatCompletionMessage{
				{
					Role:    openai.ChatMessageRoleSystem,
					Content: "将下列内容进行场景分类，仅输出分类结果。你只能在KNOWLEDGE,SCHEDULE,OTHER这三个分类中选择一个。",
				},
				{
					Role: openai.ChatMessageRoleUser,
					MultiContent: []openai.ChatMessagePart{
						{
							Type: openai.ChatMessagePartTypeImageURL,
							ImageURL: &openai.ChatMessageImageURL{
								// 确保 MIME 类型正确，例如 image/jpeg 或 image/png
								URL: "data:image/png;base64," + content,
							},
						},
					},
				},
			},
		},
	)
	if err != nil {
		fmt.Printf("请求出错: %v\n", err)
		resultchan <- fmt.Sprintf("<UNK>: %v", err)
	}
	fmt.Println("🧠 Moonshot 回复：", resp.Choices[0].Message.Content)
	s := resp.Choices[0].Message.Content
	s = strings.TrimPrefix(s, "```json")
	// 移除后缀
	s = strings.TrimSuffix(s, "```")
	resultchan <- s
}

func GetStructJson(s interface{}) (string, error) {

	schema, err := service.GenerateStructSchema(s)
	if err != nil {
		return "", gerror.NewCode(gcode.CodeInvalidParameter, "生成结构体 JSON 失败: "+err.Error())
	}
	return schema, nil
}
