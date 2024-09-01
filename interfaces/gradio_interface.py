import gradio as gr
from interfaces.chat_interface import gradio_chat

def launch_gradio_interface():
    iface = gr.ChatInterface(gradio_chat).launch()