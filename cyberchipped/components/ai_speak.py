from cyberchipped.utilities.openai import get_client


async def ai_speak(
    input: str,
    model: str = "tts-1",
    voice: str = "nova",
    response_format: str = "aac",
):
    client = get_client()
    response = await client.audio.speech.create(
        input=input,
        model=model,
        voice=voice,
        response_format=response_format,
    )
    return response.response.iter_bytes()
