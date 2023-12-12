from cyberchipped.assistants import Assistant


def add(a: int, b: int) -> int:
    return a + b


def main() -> str:
    with Assistant(
        tools=[add],
        instructions="You are a calculator and always use the add tool and only output the number answer.",
    ) as ai:
        result = ai.say("you add 1 and 1 together.", user_id="123")
        return result


if __name__ == "__main__":
    print(main())
