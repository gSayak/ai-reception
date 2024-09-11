from typing import List
import asyncio
import random
from enum import Enum


class FetchState(Enum):
    FETCHING = "fetching"
    FETCHED = "fetched"
    NOT_FETCHED = "not_fetched"


class AIAssistant:
    def __init__(self, name, model, tools):
        self.fetch_state = FetchState.NOT_FETCHED
        self.fetched_response: str = None
        self.prompt: str = """You are..."""
        self.tools: List = list()  # dict of tools
        self.messages: List = list()  # messages buffer

    def make_openai_call(self):
        # code for openai API call
        pass

    def get_response(self, user_message: str) -> str:
        # add user message to messages buffer
        if self.fetch_state == FetchState.FETCHING:
            response = "Sorry for delaying, fetching from the db"
            self.messages.append({"role": "user", "content": user_message})
            self.messages.append({"role": "assistant", "content": response})
            return response
        elif self.fetch_state == FetchState.FETCHED:
            response = (
                "Sorry for delaying, here is the response: " + self.fetched_response
            )
            self.messages.append({"role": "user", "content": user_message})
            self.messages.append({"role": "assistant", "content": response})
            return response

        self.messages.append({"role": "user", "content": user_message})

        # make the completion call: this would have a tool response as well
        response = self.make_openai_call()
        # make a completion call to handle the tool call and reply with a reponse
        return self.handle_response(response)

    def handle_response(self, response):
        if response.tool_call:
            self.handle_tool_call(response.tool_call)
        else:
            return response.choices[0].message.content

    def handle_tool_call(self, tool_call):
        for tool in tool_call:
            location = tool.function.arguments["location"]
            if tool.function.name == "get_user_location":
                eta = self.get_eta_on_location(location)
                response = f"Please hold on for a while, dr adrin will be there in {eta} minutes"
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_id": "same as get_user_location id",
                        "content": response,
                    }
                )
                return response

            if tool.function.name == "fetch_emergency_action":
                # Fetch emergency action asynchronously
                self.FETCHING = True
                asyncio.create_task(
                    self.fetch_emergency_action(
                        emergency=tool.function.arguments["emergency"]
                    )
                )
                # Append to messages buffer
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_id": "same as fetch_emergency_action id",
                        "content": "Success 200",
                    }
                )
                # add the static response to the messages buffer
                response = "Please tell me the location of the emergency"
                self.messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )
                return response
                # [system, user, assistant: [tool_call: fetch_emergency_action], tool_call: [fetch_emergency_action: success]]
            if tool.function.name == "store_user_message":
                # store the message in the database
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_id": "same as store_user_message id",
                        "content": "Success 400",
                    }
                )
                return self.make_openai_call()

    def get_eta_on_location(self, location: str):
        return random.randint(5, 20)

    async def fetch_emergency_action(self, emergency: str):
        # delay for 15 secs
        await asyncio.sleep(15)
        # Suppose response is fetched from the vector database
        self.FETCHING = False
        response = (
            "Emergency action fetched: Stay calm and apply pressure to stop bleeding."
        )
        self.messages.append(
            {
                "role": "system",
                "content": f"For the emergency: {emergency}, the action is: {response}",
            }
        )
        return self.make_openai_call()


if __name__ == "__main__":
    assistant = AIAssistant()
    assistant.get_response("Hello my friend lost his arm")
