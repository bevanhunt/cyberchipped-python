import base64
from cyberchipped.assistants import Assistant
from cyberchipped import ai_listen, ai_speak, ai_vision, ai_image
import fastapi
from fastapi import File, Form, Response, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import tempfile
import mimetypes
import os

app = fastapi.FastAPI()


class SpeakBody(BaseModel):
    text: str
    user_id: str


@app.post("/speak")
async def speak_to(body: SpeakBody):
    with Assistant() as ai:
        text = ai.say(body.text, user_id=body.user_id)
        ai_message = await ai_speak(text)
        return StreamingResponse(ai_message, media_type="audio/x-aac")


@app.post("/listen")
async def listen_to(file: UploadFile):
    extension = mimetypes.guess_extension(file.content_type, False)
    with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as temp:
        temp.write(file.file.read())
    temp_path = temp.name
    try:
        with open(temp_path, "rb") as temp_file:
            ai_message = await ai_listen(file=temp_file)
            return {"text": ai_message}
    finally:
        os.remove(temp_path)


@app.post("/vision")
async def vision_to(file: UploadFile = File(...), user_prompt: str = Form(...)):
    extension = mimetypes.guess_extension(file.content_type, False)
    with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as temp:
        temp.write(file.file.read())
    temp_path = temp.name
    try:
        with open(temp_path, "rb") as temp_file:
            ai_message = await ai_vision(
                user_prompt=user_prompt,
                mime_type=file.content_type,
                base64_image=base64.b64encode(temp_file.read()).decode("utf-8"),
            )
            return {"text": ai_message}
    finally:
        os.remove(temp_path)


@app.post("/image")
async def image_to(user_prompt: str = "Create an image of a cat."):
    ai_message = await ai_image(user_prompt=user_prompt, response_format="b64_json")
    b64_json = ai_message[0].b64_json
    image = base64.b64decode(b64_json)
    return Response(image, media_type="image/png")
