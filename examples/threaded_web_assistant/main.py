import cyberchipped
from cyberchipped.assistants import Assistant
from cyberchipped.assistants.threads import Thread
from dotenv import load_dotenv
import os
import fastapi
from pydantic import BaseModel

load_dotenv()

cyberchipped.settings.openai.api_key = os.getenv("OPENAI_API_KEY")

app = fastapi.FastAPI()

class Body(BaseModel):
    text: str
    thread_id: str


def echo(text: str) -> str:
    return text


def main(text: str, thread_id: str) -> str:
    with Assistant(tools=[echo], instructions="""You echo the input from `text` using the echo tool.""") as ai:
        thread = Thread(id=thread_id)
        thread.create()
        thread.run(ai)
        messages = thread.get_messages()
        last_message = messages[-1]
        last_message = last_message.content[0].text.value
        return last_message


@app.post("/")
def post(body: Body):
    ai_message = main(body.text, body.thread_id)
    return {"ai_message": ai_message}
