from openai import OpenAI
from models.tools import tools
from services.database import store_user_message
from models.emergency import fetch_emergency_action, fetch_user_location
from config.config import OPENAI_API_KEY
import json

MESSAGES_HISTORY = [{"role": "system", "content": "You are a emergency services helper who will ask the user if they have a message to send or is there an emergency. If the user replies that they have a message to send. Ask the user for what message do they need to send. Once they say the message we need to call the store_user_message function and let the user know their message has been sent to Dr. Adrin. If they have an emergency ask them what is the emergency that they are facing. Be helpful and empathetic. If the user has mentioned an emergency, the model will call the function fetch_emergency_action to provide immediate actions that should be taken during an emergency until professional medical help arrives. Keep them engaged and tell them help is on the way.If the user gives a location or locality or place, call the fetch_user_location function to provide an estimated time of arrival for assistance and tell help is on the way. If they tell anything unrelated to emergency or message, the model will ask them to provide a message or emergency only or answer with I am not aware of that and its unrelated as you are a emergency services assistant. "}] 

client = OpenAI(api_key=OPENAI_API_KEY)

def ask_and_reply(prompt):
    """Give LLM a given prompt and get an answer."""
    
    MESSAGES_HISTORY.append({"role": "user", "content": prompt})

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=MESSAGES_HISTORY,
        tools=tools,
        tool_choice="auto",  # specify the function call
    )   

    response_message = completion.choices[0].message


    MESSAGES_HISTORY.append(completion.choices[0].to_dict()['message'])

    tool_calls = response_message.tool_calls
    if tool_calls:
        for tool in tool_calls:
            tool_name = tool.function.name
            # print("TOOL NAME", tool_name)
            if tool_name == 'fetch_emergency_action':
                tool_call_id = tool.id
                tool_query_string = json.loads(tool.function.arguments)['emergency']
                results = fetch_emergency_action(emergency=tool_query_string)
                MESSAGES_HISTORY.append({
                    "role":"tool", 
                    "tool_call_id":tool_call_id, 
                    "name": tool_name, 
                    "content":results
                })
            if tool_name == 'store_user_message':
                tool_call_id = tool.id
                tool_query_string = json.loads(tool.function.arguments)['message']
                MESSAGES_HISTORY.append({
                    "role":"tool", 
                    "tool_call_id":tool_call_id, 
                    "name": tool_name, 
                    "content":store_user_message(tool_query_string)
                })           

                # print("MESSAGES", MESSAGES_HISTORY)
            if tool_name == 'fetch_user_location':
                tool_call_id = tool.id
                tool_query_string = json.loads(tool.function.arguments)['location']

                MESSAGES_HISTORY.append({
                    "role":"tool", 
                    "tool_call_id":tool_call_id, 
                    "name": tool_name, 
                    "content":fetch_user_location(tool_query_string)
                })  

            print("MESSAGES", MESSAGES_HISTORY)                 
        model_response_with_function_call = client.chat.completions.create(
        model="gpt-4o",
        messages=MESSAGES_HISTORY,
    )   
        content = model_response_with_function_call.choices[0].message.content
        return str(content)
    else: 
        # Model did not identify a function to call, result can be returned to the user 
        print(response_message.content) 
        return str(response_message.content)