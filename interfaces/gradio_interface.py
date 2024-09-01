import gradio as gr
from interfaces.chat_interface import gradio_chat

def launch_gradio_interface():
    iface = gr.ChatInterface(fn=gradio_chat, chatbot=gr.Chatbot(value=[(None, "Welcome 👋. I am AI receptionist, let me now if you want to send a message or if you have an emergency I can help you with.")],),).launch(share=True)