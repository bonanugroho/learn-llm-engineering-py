import gradio as gr # oh yeah!

# here's a simple function
def shout(text):
    print(f"Shout has been called with input {text}")
    return text.upper()

force_dark_mode = """
function refresh() {
    const url = new URL(window.location);
    if (url.searchParams.get('__theme') !== 'dark') {
        url.searchParams.set('__theme', 'dark');
        window.location.href = url.href;
    }
}
"""

# The simplicty of gradio. This might appear in "light mode" - I'll show you how to make this in dark mode later.
gr.Interface(fn=shout, inputs="textbox", outputs="textbox", flagging_mode="never", js=force_dark_mode).launch(share=False,inbrowser=False)