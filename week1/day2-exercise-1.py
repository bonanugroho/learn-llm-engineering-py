import requests

OLLAMA_API = "http://localhost:11434/api/chat"
OPENAI_OLLAMA_API = "http://localhost:11434/v1"
MODEL_LLAMA_32 = "llama3.2"
HEADERS = {"Content-Type": "application/json"}

messages = [
    {"role": "user", "content": "Describe some of the business applications of Generative AI"}
]

payload = {
        "model": MODEL_LLAMA_32,
        "messages": messages,
        "stream": False
    }


response = requests.post(OLLAMA_API, json=payload, headers=HEADERS)
print(response.json()['message']['content'])