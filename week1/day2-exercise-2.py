import ollama

OLLAMA_API = "http://localhost:11434/api/chat"
OPENAI_OLLAMA_API = "http://localhost:11434/v1"
MODEL_LLAMA_32 = "llama3.2"
HEADERS = {"Content-Type": "application/json"}

messages = [
    {"role": "user", "content": "Describe some of the business applications of Generative AI"}
]



response = ollama.chat(model=MODEL_LLAMA_32, messages=messages)
print(response['message']['content'])