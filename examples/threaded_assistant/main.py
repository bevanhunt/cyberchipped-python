import cyberchipped
from cyberchipped.assistants import Assistant
from cyberchipped.assistants.threads import Thread
from cyberchipped.assistants.formatting import pprint_messages
from dotenv import load_dotenv
import os

load_dotenv()

cyberchipped.settings.openai.api_key = os.getenv("OPENAI_API_KEY")


def echo(text: str) -> str:
    return text


def main(text: str):
    with Assistant(tools=[echo], instructions="""You echo the input from `text` using the echo tool.""") as ai:
        thread = Thread(id="123")
        thread.create()
        thread.run(ai)
        messages = thread.get_messages()
        pprint_messages(messages)


if __name__ == "__main__":
    main("Hello World!")
