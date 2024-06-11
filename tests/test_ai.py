import pytest
from fastapi import UploadFile
from io import BytesIO
from cyberchipped.ai import AI, ToolConfig, SQLiteDatabase
import os
import aiosqlite
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture(scope="session")
def sqlite_db():
    db_path = "test_db.sqlite"
    yield db_path
    os.remove(db_path)

@pytest.fixture
async def ai_instance(sqlite_db):
    database = SQLiteDatabase(sqlite_db)
    async with AI(
        api_key=os.getenv("OPENAI_API_KEY"),
        name="Test AI",
        instructions="You are a test AI.",
        database=database,
    ) as ai:
        yield ai

@pytest.fixture
def audio_file():
    audio_file = BytesIO(open("test.mp3", "rb").read())
    return UploadFile(audio_file, filename="test.mp3")

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
async def test_conversation(ai_instance, sqlite_db, audio_file):
    # Run the conversation method
    response = await ai_instance.conversation("user_123", audio_file)

    # Verify the response
    assert response is not None

    # Verify that the message was saved in the database
    async with aiosqlite.connect(sqlite_db) as db:
        async with db.execute("SELECT * FROM messages WHERE user_id = ?", ("user_123",)) as cursor:
            saved_message = await cursor.fetchone()
            assert saved_message is not None
            assert saved_message[0] == "user_123"
            assert saved_message[1] is not None
            assert saved_message[2] is not None

@pytest.mark.anyio
async def test_add_tool(ai_instance):
    @ai_instance.add_tool(ToolConfig(name="test_tool", description="test description"))
    def test_tool_function(arg1, arg2):
        return arg1 + arg2

    assert len(ai_instance.tools) == 1
    assert ai_instance.tools[0]["name"] == "test_tool"
    assert ai_instance.tools[0]["description"] == "test description"
    assert ai_instance.tools[0]["function"] == test_tool_function
