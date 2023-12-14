from cyberchipped.assistants import Assistant


def add(a: int, b: int) -> int:
    return a + b


def main(text: str) -> str:
    with Assistant(
        tools=[add],
        instructions="You only return the answer as a number.",
    ) as ai:
        result = ai.say(text, user_id="123")
        return result


if __name__ == "__main__":
    print(main())
