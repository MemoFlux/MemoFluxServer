client<llm> Gemini {
  provider openai
  options {
    model "gemini-2.5-flash"
    base_url "https://ki-llmapi.kispace.cc/v1"
    api_key env.OPENAI_API_KEY
  }
}