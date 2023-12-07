import cyberchipped
from cyberchipped.assistants import Assistant
from dotenv import load_dotenv
import os

load_dotenv()

cyberchipped.settings.openai.api_key = os.getenv("OPENAI_API_KEY")


def main():
    with Assistant() as ai:
        print(ai.say("How many dogs do I have?"))


if __name__ == "__main__":
    main()
