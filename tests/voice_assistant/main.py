from cyberchipped.assistants import Assistant
from cyberchipped import ai_listen, ai_speak
import fastapi
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import tempfile
import mimetypes
import os

app = fastapi.FastAPI()


class SpeakBody(BaseModel):
    text: str
    user_id: str


async def listening(file: UploadFile):
    extension = mimetypes.guess_extension(file.content_type, False)
    with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as temp:
        temp.write(file.file.read())
    temp_path = temp.name
    try:
        with open(temp_path, "rb") as temp_file:
            return await ai_listen(file=temp_file)
    finally:
        os.remove(temp_path)


@app.post("/speak")
async def speak_to(body: SpeakBody):
    with Assistant() as ai:
        text = ai.say(body.text, user_id=body.user_id)
        ai_message = await ai_speak(text)
        return StreamingResponse(ai_message, media_type="audio/x-aac")


@app.post("/listen")
async def listen_to(file: UploadFile):
    ai_message = await listening(file=file)
    return {"text": ai_message}
