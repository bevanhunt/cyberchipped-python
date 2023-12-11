import cyberchipped
from cyberchipped.components import ai_fn, ai_model
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv()

cyberchipped.settings.openai.api_key = os.getenv("OPENAI_API_KEY")


@ai_fn
def echo(text: str) -> str:
    """You echo the user's input."""
    return "`text`"


@ai_model
class Planet(BaseModel):
    """Planet attributes."""

    name: str = Field(..., description="The name of the planet.`.")
    true: bool = Field(..., description="Return `True`.")
    false: bool = Field(..., description="Return `False`.")
    number: int = Field(..., description="Return `1`.")
