import gradio as gr
import time

def echo(message, history, system_prompt, tokens):
    response = f"System prompt: {system_prompt}\n Message: {message}."
    for i in range(min(len(response), int(tokens))):
        time.sleep(0.05)
        yield response[: i+1]

def stream_by_model(message, history, model):
    response = ""
    match model:
        case "GPT":
            response = f"Using GPT for {message}"
        case "Claude":
            response = f"Using Claude for {message}"
        case (model) if model == "llama3.2:3b" or model == "qwen2.5:3b" or model == "deepseek-r1:1.5b" :
            print(f"Using Open Source Model (On local): {model}")
            response = f"Using Ollama Open Source Model (On local) - {model} for {message}"
        case _ :
            response = f"Unknown model: {model}"
            raise ValueError("Unknown model")

    yield response



with gr.Blocks() as ui:
    # system_prompt = gr.Textbox("You are helpful AI.", label="System Prompt")
    # slider = gr.Slider(10, 100, render=False)
    select_model = gr.Dropdown(["GPT", "Claude", "llama3.2:3b", "qwen2.5:3b","deepseek-r1:1.5b"], label="Select model", value="GPT")

    gr.ChatInterface(
        fn=stream_by_model,
        type="messages",
        additional_inputs=[select_model],
    )

ui.launch()