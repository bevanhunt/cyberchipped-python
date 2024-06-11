import mimetypes
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from openai import OpenAI
import openai
import aiosqlite
from fastapi import UploadFile
from openai import AssistantEventHandler
from typing_extensions import override
import sqlite3

# Custom adapter for datetime
def adapt_datetime(ts):
    return ts.isoformat()

# Custom converter for datetime
def convert_datetime(ts):
    return datetime.fromisoformat(ts)

# Register the adapter and converter
sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("timestamp", convert_datetime)


class EventHandler(AssistantEventHandler):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    @override
    def on_event(self, event):
        if event.event == "thread.run.requires_action":
            run_id = event.data.id
            self.handle_requires_action(event.data, run_id)
        else:
            super().on_event(event)

    def handle_requires_action(self, data, run_id):
        tool_outputs = []

        for tool in data.required_action.submit_tool_outputs.tool_calls:
            func_name = tool.function.name
            tool_func = next(
                (t["function"] for t in self.manager.tools if t["name"] == func_name),
                None,
            )
            if tool_func:
                output = tool_func(*tool.function.arguments)
                tool_outputs.append({"tool_call_id": tool.id, "output": output})

        self.submit_tool_outputs(tool_outputs, run_id)

    def submit_tool_outputs(self, tool_outputs, run_id):
        with self.manager.client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.manager.current_thread_id,
            run_id=run_id,
            tool_outputs=tool_outputs,
            event_handler=self,
        ) as stream:
            for text in stream.text_deltas:
                print(text, end="", flush=True)
            print()


class ToolConfig(BaseModel):
    name: str
    description: str


class MongoDatabase:
    def __init__(self, db_url: str, db_name: str):
        self.client = AsyncIOMotorClient(db_url)
        self.db = self.client[db_name]
        self.threads = self.db["threads"]
        self.messages = self.db["messages"]

    async def save_thread_id(self, user_id: str, thread_id: str):
        await self.threads.insert_one({"thread_id": thread_id, "user_id": user_id})

    async def get_thread_id(self, user_id: str) -> Optional[str]:
        document = await self.threads.find_one({"user_id": user_id})
        return document["thread_id"] if document else None

    async def save_message(self, user_id: str, metadata: Dict[str, Any]):
        await self.messages.insert_one(metadata)

    async def delete_thread_id(self, user_id: str):
        document = await self.threads.find_one({"user_id": user_id})
        thread_id = document["thread_id"]
        openai.beta.threads.delete(thread_id)
        await self.messages.delete_many({"user_id": user_id})
        await self.threads.delete_one({"user_id": user_id})


class SQLiteDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS threads (user_id TEXT, thread_id TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS messages (user_id TEXT, message TEXT, response TEXT, timestamp TEXT)")
        conn.commit()
        conn.close()

    async def save_thread_id(self, user_id: str, thread_id: str):
        async with aiosqlite.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as db:
            await db.execute(
                "INSERT INTO threads (user_id, thread_id) VALUES (?, ?)",
                (user_id, thread_id),
            )
            await db.commit()

    async def get_thread_id(self, user_id: str) -> Optional[str]:
        async with aiosqlite.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as db:
            async with db.execute(
                "SELECT thread_id FROM threads WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def save_message(self, user_id: str, metadata: Dict[str, Any]):
        async with aiosqlite.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as db:
            await db.execute(
                "INSERT INTO messages (user_id, message, response, timestamp) VALUES (?, ?, ?, ?)",
                (
                    user_id,
                    metadata["message"],
                    metadata["response"],
                    metadata["timestamp"],
                ),
            )
            await db.commit()

    async def delete_thread_id(self, user_id: str):
        async with aiosqlite.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as db:
            async with db.execute(
                "SELECT thread_id FROM threads WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    thread_id = row[0]
                    openai.beta.threads.delete(thread_id)
                    await db.execute(
                        "DELETE FROM messages WHERE user_id = ?", (user_id,)
                    )
                    await db.execute(
                        "DELETE FROM threads WHERE user_id = ?", (user_id,)
                    )
                    await db.commit()


class AI:
    def __init__(self, api_key: str, name: str, instructions: str, database: Any):
        openai.api_key = api_key
        self.name = name
        self.instructions = instructions
        self.model = "gpt-4o"
        self.tools = []
        self.assistant_id = None
        self.database = database
        self.client = OpenAI()

        assistants = openai.beta.assistants.list()
        for assistant in assistants:
            if assistant.name == self.name:
                self.assistant_id = assistant.id
                break

        if self.assistant_id is None:
            self.assistant_id = openai.beta.assistants.create(
                name=self.name,
                instructions=self.instructions,
                tools=self.tools,
                model=self.model,
            ).id

    async def create_thread(self, user_id: str) -> str:
        thread_id = await self.database.get_thread_id(user_id)

        if thread_id is None:
            thread = openai.beta.threads.create()
            thread_id = thread.id
            await self.database.save_thread_id(user_id, thread_id)

        return thread_id

    async def listen(self, audio_file: UploadFile):
        try:
            extension = mimetypes.guess_extension(audio_file.content_type)
            if extension is None:
                raise Exception("Invalid file type")
        except Exception:
            extension = audio_file.filename.split(".")[-1]
        transcription = self.client.audio.transcriptions.create(
            model="whisper-1", file=(f"file.{extension}", audio_file.file)
        )
        return transcription.text

    async def conversation(self, user_id: str, audio_file: UploadFile):
        thread_id = await self.database.get_thread_id(user_id)

        if thread_id is None:
            thread_id = await self.create_thread(user_id)

        self.current_thread_id = thread_id
        transcript = await self.listen(audio_file)
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=transcript,
        )

        print(self.assistant_id)

        response_text = ""
        with openai.beta.threads.runs.stream(
            thread_id=thread_id,
            assistant_id=self.assistant_id,
            event_handler=EventHandler(self),
        ) as stream:
            for event in stream:
                if hasattr(event.data, "delta") and hasattr(
                    event.data.delta, "content"
                ):
                    for content_block in event.data.delta.content:
                        if content_block.type == "text":
                            response_text += content_block.text.value

        metadata = {
            "user_id": user_id,
            "message": transcript,
            "response": response_text,
            "timestamp": datetime.now(),
        }

        await self.database.save_message(user_id, metadata)

        response = self.client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=response_text,
        )

        return response.response.iter_bytes()

    def add_tool(self, tool_config: ToolConfig):
        def decorator(func: Callable):
            self.tools.append(
                {
                    "type": "function_calling",
                    "name": tool_config.name,
                    "description": tool_config.description,
                    "function": func,
                }
            )
            return func

        return decorator


tool = AI.add_tool
