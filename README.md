# CyberChipped

[![PyPI - Version](https://img.shields.io/pypi/v/cyberchipped)](https://pypi.org/project/cyberchipped/)
[![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/bevanhunt/cyberchipped/build.yml)](https://github.com/bevanhunt/cyberchipped/actions)
[![Codecov](https://img.shields.io/codecov/c/github/bevanhunt/cyberchipped)](https://app.codecov.io/gh/bevanhunt/cyberchipped)

![CyberChipped Logo](https://cyberchipped.com/375.png)

## Introduction

CyberChipped powers the best AI Companion - [CometHeart](https://cometheart.com)!

In a few lines of code built a conversational AI Assistant!

## Install

```bash
pip install cyberchipped
```

## Setup
Create a .env file in your project root with this key in it:
```bash
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
```

## Abstractions

### OpenAI Assistant
```python
from cyberchipped.ai import SQLiteDatabase, AI

database = SQLiteDatabase(sqlite_db)
with AI(
    api_key="YOUR_OPENAI_API_KEY",
    name="AI Assistant",
    instructions="You are a friendly AI.",
    database=database,
) as ai:
    audio_file = UploadFile # from FastAPI
    ai.conversation("user_123", audio_file)
```

## Database
CyberChipped requires a database to track and manage OpenAI Assistant threads across runs.

You can use MongoDB or SQLite.

## Platform Support
Mac and Linux

## Requirements
Python >= 3.12
