# CyberChipped

[![PyPI - Version](https://img.shields.io/pypi/v/cyberchipped)](https://pypi.org/project/cyberchipped/)

![CyberChipped Logo](https://cyberchipped.com/375.png)

CyberChipped is a Python library that provides an AI-powered conversation interface using OpenAI's Assistant API. It supports both text and audio-based interactions, with features like thread management, message persistence, and custom tool integration.

## Features

- Streaming text-based conversations with AI
- Audio transcription and streaming text-to-speech conversion
- Thread management for maintaining conversation context
- Message persistence using SQLite or MongoDB
- Custom tool integration for extending AI capabilities

## Installation

You can install CyberChipped using pip:

```bash
pip install cyberchipped
```

## Usage

Here's a basic example of how to use CyberChipped:

```python
from cyberchipped import AI, SQLiteDatabase

async def main():
    database = SQLiteDatabase("conversations.db")
    async with AI("your_openai_api_key", "AI Assistant", "Your instructions here", database) as ai:
        user_id = "user123"
        response = await ai.text(user_id, "Hello, AI!")
        async for chunk in response:
            print(chunk, end="", flush=True)
        print()

# Run the async main function
import asyncio
asyncio.run(main())
```

## Contributing

Contributions to CyberChipped are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
