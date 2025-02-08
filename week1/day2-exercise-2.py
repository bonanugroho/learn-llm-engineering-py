import ollama

OLLAMA_API = "http://localhost:11434"
MODEL_LLAMA_32 = "llama3.2:3b"
MODEL_QWEN_25 = "qwen2.5:3b"
MODEL_DEEPSEEK_R1_1 = "deepseek-r1:1.5b"
MODEL_DEEPSEEK_R1_7 = "deepseek-r1:7b"

messages = [
    {"role": "user", "content": "Describe some of the business applications of Generative AI"}
]

system_message = "You are an assistant that is great at telling jokes and responds in markdown"
user_prompt = "Tell a light-hearted joke for an audience of Data Scientists"

prompts = [
    {"role": "system", "content": system_message},
    {"role": "user", "content": user_prompt}
  ]

# client = ollama.Client(host=OLLAMA_API)

# response = ollama.chat(model=MODEL_QWEN_25, messages=messages)
# response = client.chat(model=MODEL_LLAMA_32, messages=prompts)

# print(response['message']['content'])


stream = ollama.chat(
    model=MODEL_LLAMA_32,
    messages=prompts,
    stream=True,
)

for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)

# print(f"Using Model: ", stream.model)
