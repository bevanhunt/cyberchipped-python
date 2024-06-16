import pytest
from fastapi import UploadFile
from io import BytesIO
from cyberchipped.ai import AI, SQLiteDatabase
import os
import aiosqlite
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

@pytest.fixture(scope="session")
def sqlite_db():
    db_path = "test_db.sqlite"
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture
async def ai_instance(sqlite_db):
    database = SQLiteDatabase(sqlite_db)
    ai = AI(
        api_key=os.getenv("OPENAI_API_KEY"),
        name="Test AI",
        instructions="You are a test AI that keeps answers to the most brief answers.",
        database=database,
    )

    # Add tools before creating the assistant
    @ai.add_tool
    async def test_function(arg1: int, arg2: int) -> int:
        """A test tool"""
        return arg1 + arg2

    @ai.add_tool
    async def get_current_temperature(location: str, unit: str) -> Dict[str, Any]:
        """Get the current temperature for a specific location"""
        return {"temperature": 22, "unit": unit, "location": location}

    @ai.add_tool
    async def get_rain_probability(location: str) -> Dict[str, Any]:
        """Get the probability of rain for a specific location"""
        return {"probability": 0.2, "location": location}

    async with ai as ai_instance:
        yield ai_instance

@pytest.fixture
def audio_file():
    audio_file = BytesIO(open("test.mp3", "rb").read())
    return UploadFile(file=audio_file, filename="test.mp3")

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.anyio
async def test_create_thread(ai_instance):
    thread_id = await ai_instance.create_thread("user_123")
    assert thread_id is not None

@pytest.mark.anyio
async def test_listen(ai_instance, audio_file):
    transcript = await ai_instance.listen(audio_file)
    assert transcript is not None

@pytest.mark.anyio
async def test_text(ai_instance, sqlite_db):
    response = await ai_instance.text("user_123", "Hello, world!")

    assert response is not None

    async with aiosqlite.connect(sqlite_db) as db:
        async with db.execute("SELECT * FROM messages WHERE user_id = ?", ("user_123",)) as cursor:
            saved_message = await cursor.fetchone()
            assert saved_message is not None
            assert saved_message[0] == "user_123"
            assert saved_message[1] is not None
            assert saved_message[2] is not None

@pytest.mark.anyio
async def test_conversation(ai_instance, sqlite_db, audio_file):
    response = await ai_instance.conversation("user_123", audio_file)
    assert response is not None

    async with aiosqlite.connect(sqlite_db) as db:
        async with db.execute("SELECT * FROM messages WHERE user_id = ?", ("user_123",)) as cursor:
            saved_message = await cursor.fetchone()
            assert saved_message is not None
            assert saved_message[0] == "user_123"
            assert saved_message[1] is not None
            assert saved_message[2] is not None

@pytest.mark.anyio
async def test_tool_decorator(ai_instance):
    assert len(ai_instance.tools) == 3  # Ensure that the tools are added
    tool = ai_instance.tools[0]
    assert tool["function"]["name"] == "test_function"
    assert tool["function"]["description"] == "A test tool"

@pytest.mark.anyio
async def test_get_current_temperature_tool(ai_instance):
    response = await ai_instance.text("user_123", "What is the current temperature in New York, NY in Celsius?")
    assert response is not None

@pytest.mark.anyio
async def test_get_rain_probability_tool(ai_instance):
    response = await ai_instance.text("user_123", "What is the probability of rain in San Francisco, CA?")
    assert response is not None
