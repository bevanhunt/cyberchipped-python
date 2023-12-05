# CyberChipped

![PyPI - Version](https://img.shields.io/pypi/v/cyberchipped)

![CyberChipped Logo](https://cyberchipped.com/375.png)

## Intro
CyberChipped enables building powerful AI apps fast by providing four core abstractions.

These abstractions are the Assistant and 3 helpers: Function, Model, and Classifier.

Building an OpenAI Assistant with multiple tools and helpers is doable in minimal lines of code.

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

## Four Core Abstractions

### Assistant
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
    # ASSISTANT: Yes! Good morning planet Earth!)
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

### AI Classifier
```python
from cyberchipped import ai_classifier
from enum import Enum

@ai_classifier
class WhichGalaxy(Enum):
    """Picks the name of the galaxy a planet is located in."""

    MILKY_WAY = "MILKY WAY"
    ANDROMEDA = "ANDROMEDA"
    PINWHEEL = "PINWHEEL"
    OTHER = "OTHER"
    NONE = "NONE"

WhichGalaxy("Earth")
# WhichGalaxy.MILKY_WAY
```

## Source
This is a hard fork of Marvin pre-release

## Platform Support
Mac and Linux

## Requirements
Python 3.11
