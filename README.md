# CyberChipped

[![PyPI - Version](https://img.shields.io/pypi/v/cyberchipped)](https://pypi.org/project/cyberchipped/)
[![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/bevanhunt/cyberchipped/build.yml)](https://github.com/bevanhunt/cyberchipped/actions)
[![Codecov](https://img.shields.io/codecov/c/github/bevanhunt/cyberchipped)](https://app.codecov.io/gh/bevanhunt/cyberchipped)

![CyberChipped Logo](https://cyberchipped.com/375.png)

## Introduction

CyberChipped powers the best AI Companion - [CometHeart](https://cometheart.com)!

In a few lines of code build a conversational AI Assistant!

## Install

```bash
pip install cyberchipped
```

## OpenAI Assistant

```python
from cyberchipped.ai import SQLiteDatabase, AI
from fastapi import UploadFile, File
from fastapi.responses import StreamingResponse
import os

database = SQLiteDatabase("sqlite.db")

@app.post("/conversation/{user_id}")
async def conversation_endpoint(user_id: str, audio_file: UploadFile = File(...)):
    ai = AI(
        api_key=os.getenv("OPENAI_API_KEY"),
        name="CometHeart AI Simple",
        instructions="You are CometHeart an AI voice assistant - you answer questions and help with tasks. You keep your responses brief and tailor them for speech.",
        database=database
    )
    
    @ai.add_tool
    def get_current_temperature(location: str, unit: str) -> str:
        """Get the current temperature for a specific location"""
        return f"The current temperature in {location} is 20 degrees {unit}"

    async with ai as ai_instance:
        audio_generator = await ai_instance.conversation(user_id, audio_file)

        return StreamingResponse(
            content=audio_generator,
            media_type="audio/x-aac",
        )
```

## Run Tests

```bash
poetry run pytest
```