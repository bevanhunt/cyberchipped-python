import cyberchipped
from cyberchipped.assistants import Assistant
from dotenv import load_dotenv
import os

load_dotenv()

cyberchipped.settings.openai.api_key = os.getenv("OPENAI_API_KEY")


def main():
    with Assistant() as ai:
        print(ai.say("Repeat: `Hello there! How can I assist you today?`"))


if __name__ == "__main__":
    main()
