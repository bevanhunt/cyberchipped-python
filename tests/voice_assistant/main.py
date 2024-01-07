from cyberchipped.assistants import Assistant
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


def ai_speak(text: str, user_id: str):
    with Assistant() as ai:
        text = ai.say(text, user_id=user_id)
        return ai.speak(text)


def ai_listen(file: UploadFile):
    with Assistant() as ai:
        extension = mimetypes.guess_extension(file.content_type, False)
        with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as temp:
            temp.write(file.file.read())
        temp_path = temp.name
    try:
        with open(temp_path, "rb") as temp_file:
            return ai.listen(file=temp_file)
    finally:
        os.remove(temp_path)


@app.post("/speak")
def speak(body: SpeakBody):
    ai_message = ai_speak(body.text, body.user_id)
    return StreamingResponse(ai_message, media_type="audio/x-aac")


@app.post("/listen")
def listen(file: UploadFile):
    ai_message = ai_listen(file=file)
    return {"text": ai_message}
