import os
from dotenv import load_dotenv

import requests
import json
from bs4 import BeautifulSoup

from openai import OpenAI
import anthropic
import ollama

import gradio as gr

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

headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

class Website:
    """
    A utility class to represent a Website that we have scraped, now with links
    """
    def __init__(self, url):
        self.url = url
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"

        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)
        else:
            self.text = ""

        links = [link.get('href') for link in soup.find_all('a')]
        self.links = [link for link in links if link]


    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"

force_dark_mode = """
function refresh() {
    const url = new URL(window.location);
    if (url.searchParams.get('__theme') !== 'dark') {
        url.searchParams.set('__theme', 'dark');
        window.location.href = url.href;
    }
}
"""

system_message = "You are an assistant that analyzes the contents of a company website landing page \
and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown."

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

def stream_brochure(company_name, url, model):
    prompt = f"Please generate a company brochure for {company_name}. Here is their landing page:\n"
    prompt += Website(url).get_contents()
    match model:
        case "GPT":
            result = stream_gpt(prompt)
        case "Claude":
            result = stream_claude(prompt)
        case (model) if model == "llama3.2:3b" or model == "qwen2.5:3b" or model == "gemma2:2b" or model == "phi3:3.8b" :
            print(f"Using Open Source Model (On local): {model}")
            result = stream_os(prompt, model)
        case _ :
            raise ValueError("Unknown model")

    yield from result

view = gr.Interface(
    fn=stream_brochure,
    inputs=[
        gr.Textbox(label="Company Name:"),
        gr.Textbox(label="Landing page URL, including http:// or https://"),
        gr.Dropdown(["GPT", "Claude", "llama3.2:3b", "qwen2.5:3b", "gemma2:2b", "phi3:3.8b"], label="Select model", value="GPT")],
    outputs=[gr.Markdown(label="Response:")],
    flagging_mode="never",
    js=force_dark_mode
)

view.launch(
    share=False,
    inbrowser=False
)