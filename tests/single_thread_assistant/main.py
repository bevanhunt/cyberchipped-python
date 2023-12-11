from cyberchipped.assistants import Assistant
from cyberchipped.assistants.formatting import pprint_messages


def main() -> int:
    with Assistant() as ai:
        say = ai.say("Repeat: Hello there! How can I assist you today?")
        pprint_messages(ai.get_default_thread().get_messages())
        ai.get_default_thread().delete()
        return say


if __name__ == "__main__":
    print(main())
