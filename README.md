# CyberChipped

![PyPI - Version](https://img.shields.io/pypi/v/cyberchipped)

![CyberChipped Logo](https://cyberchipped.com/375.png)

## Introduction
CyberChipped enables building powerful AI apps fast by providing three core abstractions.

These abstractions are the OpenAI Assistant, AI Function, and AI Model.

The key selling point of this library is to handle the OpenAI Assistant thread run system automatically.

CyberChipped powers the most feature-rich AI Companion - [CometHeart](https://cometheart.com)!

## Install

```bash
pip install cyberchipped
```

## Setup
```python
import cyberchipped

cyberchipped.settings.openai.api_key = "YOUR_OPENAI_API_KEY"
```

## Abstractions

### OpenAI Assistant
```python
from cyberchipped.assistants import Assistant
from cyberchipped.assistants.threads import Thread
from cyberchipped.assistants.formatting import pprint_messages


with Assistant as ai:
    thread = Thread()
    thread.create()
    thread.add("Hello World!")
    thread.run(ai)
    messages = thread.get_messages()
    pprint_messages(messages)
    # prints 
    # USER: Hello World!
    # ASSISTANT: Yes! Good morning planet Earth!
```

### AI Function
```python
from cyberchipped import ai_fn

@ai_fn
def echo(text: str) -> str:
    """You return `text`."""

print(echo("Hello World!"))
# prints "Hello World!"

```

### AI Model
```python
from cyberchipped import ai_model
from pydantic import BaseModel, Field

@ai_model
class Planet(BaseModel):
    """Planet Attributes"""
    name: str = Field(..., description="The name of the planet.")

planet = Planet("Mars is a great place to visit!")
print(planet.name)
# prints "Mars"
```

## Source
This is a hard fork of Marvin pre-release

## Platform Support
Mac and Linux

## Requirements
Python 3.11
