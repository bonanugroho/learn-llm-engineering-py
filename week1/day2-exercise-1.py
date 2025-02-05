import requests

OLLAMA_API = "http://localhost:11434/api/chat"
OPENAI_OLLAMA_API = "http://localhost:11434/v1"
MODEL_LLAMA_32 = "llama3.2"
MODEL_QWEN_25 = "qwen2.5:3b"
MODEL_DEEPSEEK_R1_1 = "deepseek-r1:1.5b"
MODEL_DEEPSEEK_R1_7 = "deepseek-r1:7b"
HEADERS = {"Content-Type": "application/json"}

messages = [
    {"role": "user", "content": "Describe some of the business applications of Generative AI"}
]

payload = {
        "model": MODEL_QWEN_25,
        "messages": messages,
        "stream": False
    }

response = requests.post(OLLAMA_API, json=payload, headers=HEADERS)

print(response.json()['message']['content'])
print(f"Using Model: ",response.json()['model'])
