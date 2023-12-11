import cyberchipped
from cyberchipped.assistants import Assistant
from dotenv import load_dotenv
import os

load_dotenv()

cyberchipped.settings.openai.api_key = os.getenv("OPENAI_API_KEY")


def main() -> int:
    with Assistant() as ai:
        return ai.say("Repeat: Hello there! How can I assist you today?")


if __name__ == "__main__":
    print(main())
