from typing import TYPE_CHECKING, Callable, Optional, Union

from pydantic import BaseModel, Field, field_validator

import cyberchipped.utilities.tools
from cyberchipped.requests import Tool
from cyberchipped.tools.assistants import AssistantTools
from cyberchipped.utilities.asyncio import (
    ExposeSyncMethodsMixin,
    expose_sync_method,
    run_sync,
)
from cyberchipped.utilities.logging import get_logger
from cyberchipped.utilities.openai import get_client

from .threads import Thread

if TYPE_CHECKING:
    from .runs import Run

logger = get_logger("Assistants")


class Assistant(BaseModel, ExposeSyncMethodsMixin):
    id: Optional[str] = None
    name: str = "Assistant"
    model: str = "gpt-3.5-turbo-1106"
    instructions: Optional[str] = Field(None, repr=False)
    tools: list[AssistantTools] = []
    file_ids: list[str] = []
    metadata: dict[str, str] = {}

    def get_tools(self) -> list[AssistantTools]:
        return self.tools

    def get_instructions(self) -> str:
        return self.instructions or ""

    @field_validator("tools", mode="before")
    def format_tools(cls, tools: list[Union[Tool, Callable]]):
        return [
            (
                tool
                if isinstance(tool, Tool)
                else cyberchipped.utilities.tools.tool_from_function(tool)
            )
            for tool in tools
        ]

    def __enter__(self):
        self.create()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.delete()
        # If an exception has occurred, you might want to handle it or pass it through
        # Returning False here will re-raise any exception that occurred in the context
        return False

    @expose_sync_method("create")
    async def create_async(self):
        if self.id is not None:
            raise ValueError("Assistant has already been created.")
        client = get_client()
        response = await client.beta.assistants.create(
            **self.model_dump(
                include={"name", "model", "metadata", "file_ids", "metadata"}
            ),
            tools=[tool.model_dump() for tool in self.get_tools()],
            instructions=self.get_instructions(),
        )
        self.id = response.id

    @expose_sync_method("delete")
    async def delete_async(self):
        if not self.id:
            raise ValueError("Assistant has not been created.")
        client = get_client()
        await client.beta.assistants.delete(assistant_id=self.id)
        self.id = None

    @classmethod
    def load(cls, assistant_id: str):
        return run_sync(cls.load_async(assistant_id))

    @classmethod
    async def load_async(cls, assistant_id: str):
        client = get_client()
        response = await client.beta.assistants.retrieve(assistant_id=assistant_id)
        return cls.model_validate(response)
