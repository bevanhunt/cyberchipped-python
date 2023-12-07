import cyberchipped
from cyberchipped.assistants import Assistant
from dotenv import load_dotenv
import os
import fastapi
from pydantic import BaseModel

load_dotenv()

cyberchipped.settings.openai.api_key = os.getenv("OPENAI_API_KEY")

app = fastapi.FastAPI()


class Body(BaseModel):
    text: str
    user_id: str


def main(text: str, user_id: str) -> str:
    with Assistant() as ai:
        return ai.say(text, user_id=user_id)


@app.post("/")
def post(body: Body):
    ai_message = main(body.text, body.user_id)
    return {"ai_message": ai_message}
