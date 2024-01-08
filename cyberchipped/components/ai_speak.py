from typing import Literal
from cyberchipped.utilities.openai import get_client


async def ai_speak(
    input: str,
    model: Literal["tts-1", "tts-1-hd"] = "tts-1",
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "nova",
    response_format: Literal["aac", "opus", "flac"] = "aac",
):
    client = get_client()
    response = await client.audio.speech.create(
        input=input,
        model=model,
        voice=voice,
        response_format=response_format,
    )
    return response.response.iter_bytes()
