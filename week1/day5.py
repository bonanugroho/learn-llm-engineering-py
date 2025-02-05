import os

import openai
import requests
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from IPython.display import Markdown, display, update_display
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


MODEL_LLAMA_32 = "llama3.2:3b"
MODEL_GPT_4o_MINI = "gpt-4o-mini"
MODEL_QWEN_25 = "qwen2.5:3b"
MODEL_DEEPSEEK_R1_1 = "deepseek-r1:1.5b"
MODEL_DEEPSEEK_R1_7 = "deepseek-r1:7b"
BASE_URL_OLLAMA = "http://localhost:11434/v1"

# openai = OpenAI(base_url=BASE_URL_OLLAMA, api_key="ollama")
# openai = OpenAI()

def get_openai_api(model):
    if model == MODEL_GPT_4o_MINI:
        api = OpenAI()
    else:
        api = OpenAI(base_url=BASE_URL_OLLAMA, api_key="ollama")

    return api


# Some websites need you to use proper headers when fetching them:
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


# ed = Website("https://edwarddonner.com")
# print(ed.links)

link_system_prompt = "You are provided with a list of links found on a webpage. \
You are able to decide which of the links would be most relevant to include in a brochure about the company, \
such as links to an About page, or a Company page, or Careers/Jobs pages.\n"
link_system_prompt += "You should respond in JSON as in this example:"
link_system_prompt += """
{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page": "url": "https://another.full.url/careers"}
    ]
}
"""
# print(link_system_prompt)


def get_links_user_prompt(website):
    user_prompt = f"Here is the list of links on the website of {website.url} - "
    user_prompt += "please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format. \
Do not include Terms of Service, Privacy, email links.\n"
    user_prompt += "Links (some might be relative links):\n"
    user_prompt += "\n".join(website.links)
    return user_prompt

# print(get_links_user_prompt(Website("https://edwarddonner.com")))
# print(get_links_user_prompt(Website("https://huggingface.co")))


def get_links(url,model):
    website = Website(url)
    api = get_openai_api(model)
    response = api.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": get_links_user_prompt(website)}
      ],
        response_format={"type": "json_object"}
    )
    result = response.choices[0].message.content
    return json.loads(result)

# print(get_links("https://huggingface.co",MODEL_LLAMA_32))
# print(get_links("https://huggingface.co",MODEL_GPT_4o_MINI))
# print(get_links("https://edwarddonner.com",MODEL_LLAMA_32))


def get_all_details(url,model):
    result = "Landing page:\n"
    result += Website(url).get_contents()
    links = get_links(url,model)
    print("Found links:", links)
    for link in links["links"]:
        if link["url"] != "" or "https://" not in link["url"]:
            result += f"\n\n{link['type']}\n"
            result += Website(link["url"]).get_contents()
    return result


# print(get_all_details("https://huggingface.co", MODEL_GPT_4o_MINI))
# print(get_all_details("https://edwarddonner.com",MODEL_LLAMA_32))


system_prompt = "You are an assistant that analyzes the contents of several relevant pages from a company website \
and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown.\
Include details of company culture, customers and careers/jobs if you have the information."

# Or uncomment the lines below for a more humorous brochure - this demonstrates how easy it is to incorporate 'tone':

# system_prompt = "You are an assistant that analyzes the contents of several relevant pages from a company website \
# and creates a short humorous, entertaining, jokey brochure about the company for prospective customers, investors and recruits. Respond in markdown.\
# Include details of company culture, customers and careers/jobs if you have the information."


def get_brochure_user_prompt(company_name, url, model):
    user_prompt = f"You are looking at a company called: {company_name}\n"
    user_prompt += f"Here are the contents of its landing page and other relevant pages; use this information to build a short brochure of the company in markdown.\n"
    user_prompt += get_all_details(url, model)
    user_prompt = user_prompt[:5_000] # Truncate if more than 5,000 characters
    return user_prompt

# print(get_brochure_user_prompt("HuggingFace", "https://huggingface.co",MODEL_GPT_4o_MINI))
# print(get_brochure_user_prompt("Edward Donner", "https://edwarddonner.com", MODEL_GPT_4o_MINI))


def create_brochure(company_name, url, model):
    api = get_openai_api(model)
    response = api.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url, model)}
          ],
    )
    result = response.choices[0].message.content
    # print(Markdown(result))
    # display(Markdown(result))
    return result

# print(create_brochure("HuggingFace", "https://huggingface.com", MODEL_GPT_4o_MINI))
# print(create_brochure("Edward Donner", "https://edwarddonner.com",MODEL_LLAMA_32))


def stream_brochure(company_name, url, model):
    api = get_openai_api(model)
    stream = api.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url, model)}
        ],
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")

stream_brochure("Edward Donner", "https://edwarddonner.com", MODEL_LLAMA_32)
# stream_brochure("HuggingFace", "https://huggingface.co", MODEL_GPT_4o_MINI)