
client<llm> Gemini {
  provider openai
  options {
    model "gemini-2.5-flash"
    base_url "https://ki-llmapi.kispace.cc/v1"
    api_key env.GEMINI_API_KEY
  }
}

client<llm> QWen {
  provider openai
  options {
    model "gemini-2.5-flash"
    base_url "https://api-inference.modelscope.cn/v1/"
    api_key ms-a63a2622-76d8-41a0-8d72-8b7d715ab4ed
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
