client<llm> QWenVL {
  provider openai-generic
  options {
    model "deepseek-ai/DeepSeek-V3"
    api_key env.SILICONFLOW_API_KEY
    base_url "https://api.siliconflow.cn/v1"
  }
}

client<llm> Gemini {
  provider openai
  options {
    model "gemini-2.5-flash"
    base_url "https://ki-llmapi.kispace.cc/v1"
    api_key sk-iRIzMYxmJKJ0jI6BauyK1ZkQb2hcRq9HDEWFcBo4tuP0mjGW
  }
}
// https://docs.boundaryml.com/docs/snippets/clients/retry
retry_policy Constant {
  max_retries 3
  // Strategy is optional
  strategy {
    type constant_delay
    delay_ms 200
  }
}

retry_policy Exponential {
  max_retries 2
  // Strategy is optional
  strategy {
    type exponential_backoff
    delay_ms 300
    multiplier 1.5
    max_delay_ms 10000
  }
}
