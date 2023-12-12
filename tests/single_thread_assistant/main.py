from cyberchipped.assistants import Assistant
from cyberchipped.assistants.formatting import pprint_messages


def main() -> int:
    with Assistant(
        instructions="You are a calculator that only returns the number answer."
    ) as ai:
        say = ai.say("1+1")
        pprint_messages(ai.get_default_thread().get_messages())
        ai.get_default_thread().delete()
        return say


if __name__ == "__main__":
    print(main())
