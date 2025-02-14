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

load_dotenv(override=True)
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
MODEL_LLAMA_32 = "llama3.2:3b"


system_message = "You are a helpful assistant for an Airline called FlightAI. "
system_message += "Give short, courteous answers, no more than 1 sentence. "
system_message += "Always be accurate. If you don't know the answer, say so."

def handle_tool_call_gpt(message):
    tool_call = message.tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)
    city = arguments.get('destination_city')
    price = get_ticket_price(city)
    response = {
        "role": "tool",
        "content": json.dumps({"destination_city": city, "price": price}),
        "tool_call_id": tool_call.id,
    }

    return response, city

def chat_gpt(message, history):
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=MODEL_GPT, messages=messages, tools=tools)

    if response.choices[0].finish_reason == "tool_calls" :
        message = response.choices[0].message
        response, city = handle_tool_call_gpt(message)
        messages.append(message)
        messages.append(response)
        response = openai.chat.completions.create(model=MODEL_GPT, messages=messages)

    return response.choices[0].message.content

def chat_claude(message, history):
    messages = []
    for history_message in history:
        messages.append({"role": history_message['role'], "content": history_message['content']})

    messages.append({"role": "user", "content": message})

    message = claude.messages.create(
        model=MODEL_CLAUDE,
        system=system_message,
        messages=messages,
        max_tokens=500
    )
    return message.content[0].text

def chat_ollama(message, history, model):
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = ollama.chat(model=model, messages=messages)
    return response['message']['content']

# gr.ChatInterface(fn=chat_ollama, type="messages").launch()

def stream_by_model(message, history, model):
    match model:
        case "GPT":
            print(f"Using GPT")
            response = chat_gpt(message, history)
        case "Claude":
            print(f"Using Claude")
            response = chat_claude(message, history)
        case (model) if model == "llama3.2:3b" or model == "qwen2.5:3b" or model == "gemma2:2b" or model == "phi3:3.8b" :
            print(f"Using Ollama Open Source Model (On local): {model}")
            response = chat_ollama(message, history, model)
        case _ :

            response = f"Unknown model: {model}"
            raise ValueError("Unknown model")

    return response

# Let's start by making a useful function
ticket_prices = {"london": "$799", "paris": "$899", "tokyo": "$1400", "berlin": "$499"}

def get_ticket_price(destination_city):
    print(f"Tool get_ticket_price called for {destination_city}")
    city = destination_city.lower()
    return ticket_prices.get(city, "Unknown")


# There's a particular dictionary structure that's required to describe our function:
price_function = {
    "name": "get_ticket_price",
    "description": "Get the price of a return ticket to the destination city. Call this whenever you need to know the ticket price, for example when a customer asks 'How much is a ticket to this city'",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "The city that the customer wants to travel to",
            },
        },
        "required": ["destination_city"],
        "additionalProperties": False
    }
}

# And this is included in a list of tools:
tools = [{"type": "function", "function": price_function}]


with gr.Blocks() as ui:
    select_model = gr.Dropdown(["GPT", "Claude", "llama3.2:3b", "qwen2.5:3b", "gemma2:2b", "phi3:3.8b"], label="Select model", value="GPT")

    gr.ChatInterface(
        fn=stream_by_model,
        type="messages",
        additional_inputs=[select_model],
    )

ui.launch()
