# imports

import os
from dotenv import load_dotenv
import json

from openai import OpenAI
import anthropic
import ollama

import gradio as gr

# Load environment variables in a file called .env
# Print the key prefixes to help with any debugging

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

MODEL_GPT = "gpt-4o-mini"
MODEL_CLAUDE = "claude-3-haiku-20240307"
MODEL_OLLAMA_LLAMA32 = "llama3.2:3b"
MODEL_OLLAMA_QWEN25 = "qwen2.5:3b"
MODEL_OLLAMA_GEMMA2 = "gemma2:2b"
MODEL_OLLAMA_PHI3 = "phi3:3.8b"
MODEL_OLLAMA_DEEPSEEK_R1 = "deepseek-r1:1.5b"

# system_message = "You are a helpful assistant"
system_message = "You are a helpful assistant in a clothes store. You should try to gently encourage \
the customer to try items that are on sale. Hats are 60% off, and most other items are 50% off. \
For example, if the customer says 'I'm looking to buy a hat', \
you could reply something like, 'Wonderful - we have lots of hats - including several that are part of our sales evemt.'\
Encourage the customer to buy hats if they are unsure what to get."


# Simpler than in my video - we can easily create this function that calls OpenAI
# It's now just 1 line of code to prepare the input to OpenAI!

def prepare_messages(message, history):
    relevant_system_messages = prepare_system_messages(message)

    messages = [{"role": "system", "content": relevant_system_messages}] + history + [{"role": "user", "content": message}]

    print("History is:")
    print(history)
    print("And messages is:")
    print(messages)

    return messages

def prepare_system_messages(message):
    relevant_system_messages = system_message
    if 'belt' in message:
        relevant_system_messages += " The store does not sell belts; if you are asked for belts, be sure to point out other items on sale."

    return relevant_system_messages

def chat_ollama(message, history):
    messages, _ = prepare_messages(message, history)

    stream = ollama.chat(
        model=MODEL_OLLAMA_LLAMA32,
        messages=messages,
        stream=True
    )

    response = ""
    for chunk in stream:
        response += chunk['message']['content'] or ''
        yield response

def chat_gpt(message, history):
    messages = prepare_messages(message, history)

    stream = openai.chat.completions.create(
        model=MODEL_GPT,
        messages=messages,
        stream=True)

    response = ""
    for chunk in stream:
        response += chunk.choices[0].delta.content or ''
        yield response

def chat_claude(message, history):
    relevant_system_messages = prepare_system_messages(message)

    print("History is:")
    print(history)

    messages = []
    for history_message in history:
        messages.append({"role": history_message['role'], "content": history_message['content']})

    messages.append({"role": "user", "content": message})

    print("And messages is:")
    print(messages)

    result = claude.messages.stream(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0.7,
        system=relevant_system_messages,
        messages= messages,
    )
    response = ""
    with result as stream:
        for text in stream.text_stream:
            response += text or ""
            yield response

system_message += "\nIf the customer asks for shoes, you should respond that shoes are not on sale today, \
but remind the customer to look at hats!"

gr.ChatInterface(fn=chat_claude, type="messages").launch()