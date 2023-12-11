from cyberchipped.assistants import Assistant
import fastapi
from pydantic import BaseModel

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
