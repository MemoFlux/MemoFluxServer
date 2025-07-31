package llm

import (
	"MemoFluxServer/internal/service"
	"context"
	"encoding/json"
	"fmt"
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
	client := service.NewLLMClient("ms-a63a2622-76d8-41a0-8d72-8b7d715ab4ed", "https://api-inference.modelscope.cn/v1/")

	//Go struct to JSON
	schedule_str, err := service.GenerateStructSchema(v1.Schedule{})
	knowledge_str, err := service.GenerateStructSchema(v1.Knowledge{})

	//Make chan
	schedule_chan := make(chan string)
	knowledge_chan := make(chan string)
	sort_chan := make(chan string)

	wg.Add(3)
	go Schedule(client, req.Content, schedule_str, &wg, schedule_chan)
	go Knowledge(client, req.Content, knowledge_str, &wg, knowledge_chan)
	go Sort(client, req.Content, &wg, sort_chan)

	schedule_result := <-schedule_chan
	knowledge_result := <-knowledge_chan
	sort_result := <-sort_chan

	if err != nil {
		log.Fatalf("LLM 生成失败: %v", err)
	}
	var schedule_struct v1.Schedule
	var knowledge_struct v1.Knowledge

	err = json.Unmarshal([]byte(schedule_result), &schedule_struct)
	if err != nil {
		// 如果 JSON 格式错误，或者类型不匹配，这里会捕获到错误
		log.Fatalf("日程JSON 解析失败: %v", err)
	}
	err = json.Unmarshal([]byte(knowledge_result), &knowledge_struct)
	if err != nil {
		// 如果 JSON 格式错误，或者类型不匹配，这里会捕获到错误
		log.Fatalf("知识JSON 解析失败: %v", err)
	}

	return &v1.GeneralRes{
		Most_possible_category: sort_result,
		Schedule:               schedule_struct,
		Knowledge:              knowledge_struct,
	}, nil
}

func Schedule(client *openai.Client, content string, schema string, wg *sync.WaitGroup, resultchan chan string) {
	defer wg.Done()
	resp, err := client.CreateChatCompletion(
		context.Background(),
		openai.ChatCompletionRequest{
			Model: "Qwen/Qwen2.5-VL-72B-Instruct",
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
					Content: "Answer in JSON using this schema",
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
	resultchan <- s
}

func Knowledge(client *openai.Client, content string, schema string, wg *sync.WaitGroup, resultchan chan string) {
	defer wg.Done()
	resp, err := client.CreateChatCompletion(
		context.Background(),
		openai.ChatCompletionRequest{
			Model: "Qwen/Qwen3-235B-A22B-Instruct-2507",
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
								URL: "data:image/jpeg;base64," + content,
							},
						},
					},
				},
				{
					Role:    openai.ChatMessageRoleSystem,
					Content: "Answer in JSON using this schema",
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
	resultchan <- s
}

func Sort(client *openai.Client, content string, wg *sync.WaitGroup, resultchan chan string) {
	defer wg.Done()
	resp, err := client.CreateChatCompletion(
		context.Background(),
		openai.ChatCompletionRequest{
			Model: "Qwen/Qwen3-235B-A22B-Instruct-2507",
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
								URL: "data:image/jpeg;base64," + content,
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
