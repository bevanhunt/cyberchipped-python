from cyberchipped.assistants import Assistant
from cyberchipped.assistants.formatting import pprint_messages


def main(text: str) -> str:
    with Assistant(instructions="You only return the number as an answer.") as ai:
        say = ai.say(text)
        pprint_messages(ai.get_default_thread().get_messages())
        return say


if __name__ == "__main__":
    print(main())
