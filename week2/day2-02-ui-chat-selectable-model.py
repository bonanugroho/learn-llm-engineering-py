# imports

import os

from dotenv import load_dotenv
from openai import OpenAI
import anthropic
import ollama

import gradio as gr # oh yeah!

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


force_dark_mode = """
function refresh() {
    const url = new URL(window.location);
    if (url.searchParams.get('__theme') !== 'dark') {
        url.searchParams.set('__theme', 'dark');
        window.location.href = url.href;
    }
}
"""

system_message = "You are a helpful assistant that responds in markdown"

def message_gpt(prompt):
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
      ]
    completion = openai.chat.completions.create(
        model='gpt-4o-mini',
        messages=messages,
    )
    return completion.choices[0].message.content

def stream_gpt(prompt):
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
      ]
    stream = openai.chat.completions.create(
        model='gpt-4o-mini',
        messages=messages,
        stream=True
    )
    result = ""
    for chunk in stream:
        result += chunk.choices[0].delta.content or ""
        yield result

def stream_claude(prompt):
    result = claude.messages.stream(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0.7,
        system=system_message,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    response = ""
    with result as stream:
        for text in stream.text_stream:
            response += text or ""
            yield response

def stream_os(prompt,model):
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]
    stream = ollama.chat(
        model=model,
        messages=messages,
        stream=True,
    )
    result = ""
    for chunk in stream:
        result += chunk['message']['content'] or ""
        yield result

def stream_model(prompt, model):
    match model:
        case "GPT":
            result = stream_gpt(prompt)
        case "Claude":
            result = stream_claude(prompt)
        case (model) if model == "llama3.2:3b" or model == "qwen2.5:3b" or model == "deepseek-r1:1.5b" :
            print(f"Using Open Source Model (On local): {model}")
            result = stream_os(prompt, model)
        case _ :
            raise ValueError("Unknown model")

    yield from result


view = gr.Interface(
    fn=stream_model,
    inputs=[gr.Textbox(label="Your message:", lines=6), gr.Dropdown(["GPT", "Claude", "llama3.2:3b", "qwen2.5:3b","deepseek-r1:1.5b"], label="Select model", value="GPT")],
    outputs=[gr.Markdown(label="Response:")],
    flagging_mode="never",
    js=force_dark_mode
)

view.launch(
    share=False,
    inbrowser=False
)