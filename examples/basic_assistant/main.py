import cyberchipped
from cyberchipped.assistants import Assistant
from cyberchipped.assistants.threads import Thread
from cyberchipped.assistants.formatting import pprint_messages
from dotenv import load_dotenv
import os

load_dotenv()

cyberchipped.settings.openai.api_key = os.getenv("OPENAI_API_KEY")

def main():
    with Assistant() as ai:
        thread = Thread()
        thread.create()
        thread.add("Hello World!")
        thread.run(ai)
        messages = thread.get_messages()
        pprint_messages(messages)

if __name__ == "__main__":
    main()