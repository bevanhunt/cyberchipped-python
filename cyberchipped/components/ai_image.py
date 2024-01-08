from typing import Literal
from cyberchipped.utilities.openai import get_client


async def ai_image(
    user_prompt: str,
    model: Literal["dall-e-2", "dall-e-3"] = "dall-e-3",
    n: int = 1,
    quality: Literal["hd", "standard"] = "standard",
    response_format: Literal["url", "b64_json"] = "url",
    size: Literal[
        "256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"
    ] = "1024x1024",
    style: Literal["standard", "vivid"] = "vivid",
    user: str = "",
):
    client = get_client()
    response = await client.images.generate(
        prompt=user_prompt,
        model=model,
        n=n,
        quality=quality,
        response_format=response_format,
        size=size,
        style=style,
        user=user,
    )
    return response.data
