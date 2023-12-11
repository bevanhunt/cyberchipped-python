import cyberchipped
from cyberchipped.assistants import Assistant
from dotenv import load_dotenv
import os

load_dotenv()

cyberchipped.settings.openai.api_key = os.getenv("OPENAI_API_KEY")


def main():
    with Assistant() as ai:
        print(ai.say("Say: `Hello there! How can I assist you today?`", user_id="123"))


if __name__ == "__main__":
    main()
