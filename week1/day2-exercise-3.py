from openai import OpenAI

OPENAI_OLLAMA_API = "http://localhost:11434/v1"
MODEL_LLAMA_32 = "llama3.2:3b"
MODEL_QWEN_25 = "qwen2.5:3b"
MODEL_DEEPSEEK_R1_1 = "deepseek-r1:1.5b"
MODEL_DEEPSEEK_R1_7 = "deepseek-r1:7b"

messages = [
    {"role": "user", "content": "Describe some of the business applications of Generative AI"}
]

ollama_via_openai = OpenAI(base_url=OPENAI_OLLAMA_API, api_key='ollama')

response = ollama_via_openai.chat.completions.create(
    model=MODEL_QWEN_25,
    messages=messages
)

print(response.choices[0].message.content)
print(f"Using Model: ",response.model)
