import gradio as gr
from llama_index.core import SimpleDirectoryReader, ServiceContext, VectorStoreIndex
from pinecone import Pinecone
import asyncio
import os
from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPEN_AI_KEY')
pinecone_key = os.getenv('PINECONE_DB')
pc = Pinecone(api_key = pinecone_key)
index = pc.Index("newsic")
embedding_model = "text-embedding-ada-002"
llm = OpenAI(temperature=0.1, model="gpt-4o")

def chat(message, history):
    messages = [
    ChatMessage(
        role="system", 
        content="You are a emergency services helper who will ask the user if they have a message to send or is there an emergency. If the user replies that they have a message to send. Ask the user for what message do they need to send or if they have an emergency ask them what is the emergency that they are facing. Be helpful and empathetic."
    ),
    ChatMessage(role="user", content=f"{message}"),
]
    resp = OpenAI().chat(messages)
    print(resp)
    return str(resp)


def chatcompletion(message, history):
    documents = SimpleDirectoryReader(input_files=["data/resume.pdf"]).load_data()
    print("DOCUMENTS: ", documents)
    index = VectorStoreIndex.from_documents(documents, embed_mode =embedding_model, llm = llm)
    print("Index : ", index)
    query_engine = index.as_query_engine()
    response = str(query_engine.query(message))
    # print(response)
    return response


function_descriptions_multiple = [
    {
        "name": "get_message",
        "description": "Get the message the user says which will need to be stored",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The message from the user, e.g 'Hello Doctor will you be available tomorrow'",
                }
            },
            "required": ["message"],
        },
    },
    {
        "name": "fetch_emergency",
        "description": "Fetch the immidiate action the user should take when there is an emergency until the doctor arrives",
        "parameters": {
            "type": "object",
            "properties": {
                "emergency": {
                    "type": "string",
                    "description": "The emergency situation that has happened, eg : patient is not breathing",
                },
            },
            "required": ["emergency"],
        },
    },
    {
        "name": "get_location",
        "description": "Get the location of the user to give them an estimated time of arrival",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The location of where the incident happened, e.g Bay Area, San Francisco",
                },
            },
            "required": ["location"],
        },
    },
]

# Create a Gradio interface
gr.ChatInterface(chat).launch()
