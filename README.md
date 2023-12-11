# CyberChipped

[![PyPI - Version](https://img.shields.io/pypi/v/cyberchipped)](https://pypi.org/project/cyberchipped/)
[![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/bevanhunt/cyberchipped/build.yml)](https://github.com/bevanhunt/cyberchipped/actions)
[![Codecov](https://img.shields.io/codecov/c/github/bevanhunt/cyberchipped)](https://app.codecov.io/gh/bevanhunt/cyberchipped)

![CyberChipped Logo](https://cyberchipped.com/375.png)

## Introduction
CyberChipped enables building powerful AI apps fast by providing three core abstractions.

These abstractions are the OpenAI Assistant, AI Function, and AI Model.

The key selling point of this library is to build an OpenAI Assistant in two lines of code!

CyberChipped powers the most feature-rich AI Companion - [CometHeart](https://cometheart.com)!

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
from cyberchipped.assistants import Assistant


with Assistant() as ai:
    print(ai.say("Hello World!"))
    # prints: "Hello there! How can I assist you today?"
```

### AI Function
```python
from cyberchipped import ai_fn

@ai_fn
def echo(text: str) -> str:
    """You return `text`."""

print(echo("Hello World!"))
# prints: "Hello World!"

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
# prints: "Mars"
```

## Note
CyberChipped will save a sqlite3 database to your working directory in order to persist and manage OpenAI Assistant threads.

## Source
This is a hard fork of [Marvin](https://askmarvin.ai) pre-release

## Platform Support
Mac and Linux

## Requirements
Python >= 3.11
