# imports

import os
import time

from dotenv import load_dotenv
from openai import OpenAI
import anthropic
import ollama

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')

if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")

if anthropic_api_key:
    print(f"Anthropic API Key exists and begins {anthropic_api_key[:7]}")
else:
    print("Anthropic API Key not set")

openai = OpenAI()
claude = anthropic.Anthropic()

# Let's make a conversation between GPT-4o-mini and Claude-3-haiku
# We're using cheap versions of models so the costs will be minimal

MODEL_OS_LLAMA_32 = "llama3.2:3b"
MODEL_OS_QWEN_25 = "qwen2.5:3b"
MODEL_OS_DEEPSEEK_R1_1 = "deepseek-r1:1.5b"
MODEL_OS_DEEPSEEK_R1_7 = "deepseek-r1:7b"
MODEL_GPT = "gpt-4o-mini"
MODEL_CLAUDE = "claude-3-haiku-20240307"

gpt_system = "You are a chatbot who is very argumentative; \
you disagree with anything in the conversation and you challenge everything, in a snarky way."

os_system = "You are a very polite, courteous chatbot. You try to agree with \
everything the other person says, or find common ground. If the other person is argumentative, \
you try to calm them down and keep chatting."

claude_system = "You are an humorous chatbot that is great at telling jokes. You like to \
tell a light-hearted joke for every comments in conversation to make everyone happy."

def call_gpt():
    messages = [{"role": "system", "content": gpt_system}]
    for gpt_msg, claude_msg, os_msg in zip(gpt_messages, claude_messages, os_messages):
        messages.append({"role": "assistant", "content": gpt_msg})
        messages.append({"role": "user", "content": claude_msg})
        messages.append({"role": "user", "content": os_msg})
    completion = openai.chat.completions.create(
        model=MODEL_GPT,
        messages=messages
    )
    return completion.choices[0].message.content

def call_claude():
    messages = []
    for gpt_msg, claude_msg, os_msg in zip(gpt_messages, claude_messages, os_messages):
        messages.append({"role": "user", "content": gpt_msg})
        messages.append({"role": "assistant", "content": claude_msg})
        messages.append({"role": "user", "content": os_msg})
    message = claude.messages.create(
        model=MODEL_CLAUDE,
        system=claude_system,
        messages=messages,
        max_tokens=500
    )
    return message.content[0].text


def call_os():
    messages = [{"role": "system", "content": os_system}]
    for gpt_msg, claude_msg, os_msg in zip(gpt_messages, claude_messages, os_messages):
        messages.append({"role": "user", "content": gpt_msg})
        messages.append({"role": "user", "content": claude_msg})
        messages.append({"role": "assistant", "content": os_msg})
    response = ollama.chat(
        model= MODEL_OS_LLAMA_32,
        messages=messages
    )
    return response['message']['content']


gpt_messages = ["Hi there"]
claude_messages = ["Hi"]
os_messages = ["Hello, What's up guys"]

# print(call_claude())
# print(call_gpt())
# print(call_os())


print(f"GPT:\n{gpt_messages[0]}\n")
print(f"Claude:\n{claude_messages[0]}\n")
print(f"Ollama:\n{os_messages[0]}\n")

for i in range(5):
    gpt_next = call_gpt()
    print(f"GPT:\n{gpt_next}\n")
    if gpt_next != "":
        gpt_messages.append(gpt_next)
    time.sleep(1)

    claude_next = call_claude()
    print(f"Claude:\n{claude_next}\n")
    if claude_next != "":
        claude_messages.append(claude_next)
    time.sleep(1)

    os_next = call_os()
    print(f"Ollama:\n{os_next}\n")
    if os_next != "" :
        os_messages.append(os_next)
    time.sleep(1)
