import gradio as gr
import os
import json
import openai
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, ChatMessage
from openai import OpenAI
from dotenv import load_dotenv
from pinecone import Pinecone
from pymongo import MongoClient
import random

load_dotenv() 

client = OpenAI(
    api_key=os.environ.get("OPEN_AI_KEY"),
)

load_dotenv()
OPENAI_API_KEY = os.environ.get("OPEN_AI_KEY")
pinecone_key = os.getenv('PINECONE_DB')
pc = Pinecone(api_key = pinecone_key)
index = pc.Index("emergency-db")
MONGO_DB_URI = os.getenv('MONGO_DB_URI')
client_db = MongoClient(MONGO_DB_URI)
db = client_db.get_database('asclepius')
records = db.reception 
messages = db.messages




tools = [
    {
        "type": "function",
        "function": {
            "name": "store_user_message",
            "description": "Capture and store the message provided by the user for later retrieval or action.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message content provided by the user, e.g., 'Hello Doctor, will you be available tomorrow?'"
                    }
                },
                "required": ["message"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_emergency_action",
            "description": "Provide immediate actions that should be taken during an emergency until professional medical help arrives.",
            "parameters": {
                "type": "object",
                "properties": {
                    "emergency": {
                        "type": "string",
                        "description": "A brief description of the current emergency situation, e.g., 'patient is not breathing', 'severe bleeding', 'choking incident'."
                    },
                    "cause": {
                        "type": "string",
                        "description": "The underlying cause or event that triggered the emergency, e.g., 'patient fell down the stairs', 'ingested a toxic substance'."
                    }
                },
                "required": ["emergency"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_user_location",
            "description": "Obtain the user's location to provide an estimated time of arrival for assistance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The specific location where the incident occurred, e.g., 'park in the Bay Area, San Francisco'."
                    }
                },
                "required": ["location"],
                "additionalProperties": False
            }
        }
    }
]



def fetch_emergency_action(emergency, cause=None):
    reason = f"The emergency : {emergency}, \n The cause : {cause}"
    searchFix = client.embeddings.create(
      input = reason,
      model = "text-embedding-ada-002"
  )

    doc = index.query(
        vector=searchFix.data[0].embedding,
        top_k = 1
  )
    for match in doc['matches']:
        match_id = match['id']
        match_score = match['score']

    action = records.find_one({'emergency_type': match_id})["action"]
    return action

def store_user_message(message):
    messages.insert_one({"message": message})
    print("Message stored: ", message)
    return "Your message has been sent to Dr. Adrin successfully."

def fetch_user_location(location):
    time = random.randint(5, 20)
    return f"Dr. Adrin is on the way. Estimated time of arrival is {time} minutes. Please continue the steps mentioned before until doctor arrives."



def ask_and_reply(prompt, history):
    """Give LLM a given prompt and get an answer."""

    # messages=[
    #     {
    #     "role":"system", "content": "You are a emergency services helper who will ask the user if they have a message to send or is there an emergency. If the user replies that they have a message to send. Ask the user for what message do they need to send. Once they say the message we need to call the store_user_message function and let the user know their message has been sent to Dr. Adrin. If they have an emergency ask them what is the emergency that they are facing. Be helpful and empathetic. If the user has mentioned an emergency, the model will call the function fetch_emergency_action to provide immediate actions that should be taken during an emergency until professional medical help arrives. Keep them engaged and tell them help is on the way. If they tell anything unrelated to emergency or message, the model will ask them to provide a message or emergency only or answer with I am not aware of that and its unrelated as you are a emergency services assistant. If the user gives an location, call the fetch_user_location function to provide an estimated time of arrival for assistance and tell help is on the way."},
        
    #     {"role": "user", "content": prompt
    #     }
    #     ]
    messages = [{"role": "system", "content": "You are a emergency services helper who will ask the user if they have a message to send or is there an emergency. If the user replies that they have a message to send. Ask the user for what message do they need to send. Once they say the message we need to call the store_user_message function and let the user know their message has been sent to Dr. Adrin. If they have an emergency ask them what is the emergency that they are facing. Be helpful and empathetic. If the user has mentioned an emergency, the model will call the function fetch_emergency_action to provide immediate actions that should be taken during an emergency until professional medical help arrives. Keep them engaged and tell them help is on the way. If they tell anything unrelated to emergency or message, the model will ask them to provide a message or emergency only or answer with I am not aware of that and its unrelated as you are a emergency services assistant. If the user gives an location, call the fetch_user_location function to provide an estimated time of arrival for assistance and tell help is on the way."}]
    for pair in history:
        user_input, bot_response = pair
        messages.append({"role": "user", "content": user_input})
        messages.append({"role": "assistant", "content": bot_response})
    
    
    
    # Add the user's new message
    messages.append({"role": "user", "content": prompt})

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # specify the function call
    )   

    response_message = completion.choices[0].message
    messages.append(response_message)
    # print("MESSAGES", messages)


    tool_calls = response_message.tool_calls
    if tool_calls:
        # If true the model will return the name of the tool / function to call and the argument(s)  
        tool_function_name = tool_calls[0].function.name
        if tool_function_name == 'fetch_emergency_action':
            tool_call_id = tool_calls[0].id
            tool_query_string = json.loads(tool_calls[0].function.arguments)['emergency']

            print("TOTAL_CALL_ID", tool_call_id)
            print("TOTAL_FUNCTION_NAME", tool_function_name)
            print("TOTAL_QUERY_STRING", tool_query_string)
            results = fetch_emergency_action(emergency=tool_query_string)
            messages.append({
                "role":"tool", 
                "tool_call_id":tool_call_id, 
                "name": tool_function_name, 
                "content":results
            })           
            model_response_with_function_call = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
            )  # get a new response from the model where it can see the function response
            print("Model_Response: ",model_response_with_function_call)

        elif tool_function_name == 'store_user_message':
            tool_call_id = tool_calls[0].id
            tool_query_string = json.loads(tool_calls[0].function.arguments)['message']
            print("TOTAL_CALL_ID", tool_call_id)
            print("TOTAL_FUNCTION_NAME", tool_function_name)
            print("TOTAL_QUERY_STRING", tool_query_string)
            messages.append({
                "role":"tool", 
                "tool_call_id":tool_call_id, 
                "name": tool_function_name, 
                "content":store_user_message(tool_query_string)
            })           
            model_response_with_function_call = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
            )
            print("Model_Response: ",model_response_with_function_call)

        elif tool_function_name == 'fetch_user_location':
            tool_call_id = tool_calls[0].id
            tool_query_string = json.loads(tool_calls[0].function.arguments)['location']
            print("TOTAL_CALL_ID", tool_call_id)
            print("TOTAL_FUNCTION_NAME", tool_function_name)
            print("TOTAL_QUERY_STRING", tool_query_string)
            messages.append({
                "role":"tool", 
                "tool_call_id":tool_call_id, 
                "name": tool_function_name, 
                "content":fetch_user_location(tool_query_string)
            })           
            model_response_with_function_call = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
            )
            print("Model_Response: ",model_response_with_function_call)
            
        else: 
            print(f"Error: function {tool_function_name} does not exist")
        content = model_response_with_function_call.choices[0].message.content
        return str(content)
    else: 
        # Model did not identify a function to call, result can be returned to the user 
        print(response_message.content) 
        return str(response_message.content)
    
    


# Output the extracted content



# user_prompt = "I have an emergency, my friend just got hit by a truck and is bleeding profusely. What should I do?"
# user_prompt = "I have an message to send, I want to ask from Dr Adrin if doctor has some medication for fever?"
# user_prompt = "we are at the park in Howrah"
# ask_and_reply(user_prompt)

def gradio_chat(message, history):
    # response = str(ask_and_reply(str(message)))
    response = ask_and_reply(message, history)
    history.append([message, response])
    return response

iface = gr.ChatInterface(gradio_chat).launch()
