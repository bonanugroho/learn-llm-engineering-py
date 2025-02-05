import os

import openai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from IPython.display import Markdown, display
from openai import OpenAI

load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

# Check the key
if not api_key:
    print("No API key was found - please head over to the troubleshooting notebook in this folder to identify & fix!")
elif not api_key.startswith("sk-proj-"):
    print("An API key was found, but it doesn't start sk-proj-; please check you're using the right key - see troubleshooting notebook")
elif api_key.strip() != api_key:
    print("An API key was found, but it looks like it might have space or tab characters at the start or end - please remove them - see troubleshooting notebook")
else:
    print("API key found and looks good so far!")

MODEL_OLLAMA = "llama3.2"
MODEL_GPT = "gpt-4o-mini"
MODEL_QWEN_25 = "qwen2.5:3b"
MODEL_DEEPSEEK_R1_1 = "deepseek-r1:1.5b"
MODEL_DEEPSEEK_R1_7 = "deepseek-r1:7b"
BASE_URL_OLLAMA = "http://localhost:11434/v1"

openai = OpenAI(base_url=BASE_URL_OLLAMA, api_key="ollama")
# openai = OpenAI()

# Some websites need you to use proper headers when fetching them:
headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

class Website:
    def __init__(self, url):
        """
        Create this Website object from the given url using the BeautifulSoup library
        """
        self.url = url
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)

# Define our system prompt - you can experiment with this later, changing the last sentence to 'Respond in markdown in Spanish."
system_prompt = "You are an assistant that analyzes the contents of a website \
and provides a short summary, ignoring text that might be navigation related. \
Respond in markdown."

# A function that writes a User Prompt that asks for summaries of websites:
def user_prompt_for(website):
    user_prompt = f"You are looking at a website titled {website.title  }"
    user_prompt += "\nThe contents of this website is as follows; \
please provide a short summary of this website in markdown. \
If it includes news or announcements, then summarize these too.\n\n"
    user_prompt += website.text
    return user_prompt

# See how this function creates exactly the format above
def messages_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(website)}
    ]

# And now: call the OpenAI API. You will get very familiar with this!
def summarize(url, model):
    website = Website(url)
    response = openai.chat.completions.create(
        model = model,
        messages = messages_for(website)
    )
    print(f"Using Model: ", response.model)
    return response.choices[0].message.content

# A function to display this nicely in the Jupyter output, using markdown
def display_summary(url, model):
    summary = summarize(url, model)
    display(Markdown(summary))

# ws = Website("https://edwarddonner.com")
# ws = Website("https://cnn.com")
# print("title:", ws.title)
# print("text:",ws.text)

print(summarize("https://edwarddonner.com", MODEL_DEEPSEEK_R1_1))
# print(summarize("https://cnn.com", MODEL_GPT))
