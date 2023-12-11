import cyberchipped
from cyberchipped.assistants import Assistant
from dotenv import load_dotenv
import os

load_dotenv()

cyberchipped.settings.openai.api_key = os.getenv("OPENAI_API_KEY")


def main() -> int:
    with Assistant() as ai:
        return ai.say("1+1", user_id="123")


if __name__ == "__main__":
    print(main())
