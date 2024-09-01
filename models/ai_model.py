from openai import OpenAI
from models.tools import tools
from services.database import store_user_message
from models.emergency import fetch_emergency_action, fetch_user_location
from config.config import OPENAI_API_KEY
import json

client = OpenAI(api_key=OPENAI_API_KEY)

def ask_and_reply(prompt, history):
    """Give LLM a given prompt and get an answer."""

    messages = [{"role": "system", "content": "You are a emergency services helper who will ask the user if they have a message to send or is there an emergency. If the user replies that they have a message to send. Ask the user for what message do they need to send. Once they say the message we need to call the store_user_message function and let the user know their message has been sent to Dr. Adrin. If they have an emergency ask them what is the emergency that they are facing. Be helpful and empathetic. If the user has mentioned an emergency, the model will call the function fetch_emergency_action to provide immediate actions that should be taken during an emergency until professional medical help arrives. Keep them engaged and tell them help is on the way. If they tell anything unrelated to emergency or message, the model will ask them to provide a message or emergency only or answer with I am not aware of that and its unrelated as you are a emergency services assistant. If the user gives an location, call the fetch_user_location function to provide an estimated time of arrival for assistance and tell help is on the way."}]
    for pair in history:
        user_input, bot_response = pair
        messages.append({"role": "user", "content": user_input})
        messages.append({"role": "assistant", "content": bot_response})
    
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

            # print("TOTAL_CALL_ID", tool_call_id)
            # print("TOTAL_FUNCTION_NAME", tool_function_name)
            # print("TOTAL_QUERY_STRING", tool_query_string)
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
            # print("Model_Response: ",model_response_with_function_call)

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
            # print("Model_Response: ",model_response_with_function_call)

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
            # print("Model_Response: ",model_response_with_function_call)
            
        else: 
            print(f"Error: function {tool_function_name} does not exist")
        content = model_response_with_function_call.choices[0].message.content
        return str(content)
    else: 
        # Model did not identify a function to call, result can be returned to the user 
        print(response_message.content) 
        return str(response_message.content)