from cyberchipped.assistants import Assistant
from cyberchipped import ai_listen
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


def speaking(text: str, user_id: str):
    with Assistant() as ai:
        text = ai.say(text, user_id=user_id)
        return ai.speak(text)


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
def speak_to(body: SpeakBody):
    ai_message = speaking(body.text, body.user_id)
    return StreamingResponse(ai_message, media_type="audio/x-aac")


@app.post("/listen")
async def listen_to(file: UploadFile):
    ai_message = await listening(file=file)
    return {"text": ai_message}
