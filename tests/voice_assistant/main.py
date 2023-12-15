from cyberchipped.assistants import Assistant
import fastapi
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = fastapi.FastAPI()


class Body(BaseModel):
    text: str
    user_id: str


def main(text: str, user_id: str) -> str:
    with Assistant() as ai:
        text = ai.say(text, user_id=user_id)
        return ai.speak(text)


@app.post("/")
def post(body: Body):
    ai_message = main(body.text, body.user_id)
    return StreamingResponse(ai_message, media_type="audio/x-aac")
