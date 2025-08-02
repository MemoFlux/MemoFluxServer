package service

import (
	"github.com/sashabaranov/go-openai"
)

func NewLLMClient(apikey string, baseurl string) *openai.Client {
	config := openai.DefaultConfig(apikey)
	config.BaseURL = baseurl
	client := openai.NewClientWithConfig(config)
	return client
}
