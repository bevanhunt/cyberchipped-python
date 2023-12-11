from cyberchipped.assistants import Assistant


def main() -> int:
    with Assistant() as ai:
        return ai.say("Repeat: Hello there! How can I assist you today?")


if __name__ == "__main__":
    print(main())
