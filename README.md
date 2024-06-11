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

database = SQLiteDatabase("sqlite.db")

@app.post("/conversation/{user_id}")
async def conversation_endpoint(user_id: str, audio_file: UploadFile = File(...)):
    async with AI(
        api_key=os.getenv("OPENAI_API_KEY"),
        name="CometHeart AI Simple",
        instructions="You are CometHeart an AI voice assistant - you answer questions and help with tasks. You keep your responses brief and tailor them for speech.",
        database=database
    ) as ai:
        audio_generator = await ai.conversation(user_id, audio_file)

        return StreamingResponse(
            content=audio_generator,
            media_type="audio/x-aac",
        )
```

## Database
CyberChipped requires a database to track and manage OpenAI Assistant threads across runs.

You can use MongoDB or SQLite.

## Platform Support
Mac and Linux

## Requirements
Python >= 3.12
