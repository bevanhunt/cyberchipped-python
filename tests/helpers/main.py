from cyberchipped import ai_fn, ai_model
from pydantic import BaseModel, Field


@ai_fn
def echo(text: str) -> str:
    """You echo the user's input."""


@ai_model
class Planet(BaseModel):
    """Planet attributes."""

    name: str = Field(..., description="The name of the planet.`.")
    true: bool = Field(..., description="Return `True`.")
    false: bool = Field(..., description="Return `False`.")
    number: int = Field(..., description="Return `1`.")
