from cyberchipped.utilities.openai import get_client


# 'image/png', 'image/jpeg', 'image/gif', 'image/webp'
async def ai_vision(
    user_prompt: str,
    base64_image: str,
    mime_type: str = "image/png",
):
    client = get_client()
    response = await client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
                    },
                ],
            }
        ],
        max_tokens=300,
    )
    return response.choices[0].message.content
