from models.ai_model import ask_and_reply

def gradio_chat(message, history):
    response = ask_and_reply(message)
    return response


# history = [user, assistant]