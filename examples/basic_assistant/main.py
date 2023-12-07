import cyberchipped
from cyberchipped.assistants import Assistant
from cyberchipped.assistants.formatting import pprint_messages
from dotenv import load_dotenv
import os

load_dotenv()

cyberchipped.settings.openai.api_key = os.getenv("OPENAI_API_KEY")

def main():
    with Assistant() as ai:
        pprint_messages(ai.say("Hello World!"))

if __name__ == "__main__":
    main()