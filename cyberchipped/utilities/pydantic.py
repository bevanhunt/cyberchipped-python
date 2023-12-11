from typing import Any, Callable, Optional, cast, get_origin

from pydantic import BaseModel, TypeAdapter
from pydantic.v1 import validate_arguments
from typing_extensions import Literal


def cast_callable_to_model(
    function: Callable[..., Any],
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> type[BaseModel]:
    response = validate_arguments(function).model
    for field in ["args", "kwargs", "v__duplicate_kwargs"]:
        fields = cast(dict[str, Any], response.__fields__)
        fields.pop(field, None)
    response.__title__ = name or function.__name__
    response.__name__ = name or function.__name__
    response.__doc__ = description or function.__doc__
    return response


def parse_as(
    type_: Any,
    data: Any,
    mode: Literal["python", "json", "strings"] = "python",
) -> BaseModel:
    """Parse a json string to a Pydantic model."""
    adapter = TypeAdapter(type_)

    if get_origin(type_) is list and isinstance(data, dict):
        data = next(iter(data.values()))

    parser = getattr(adapter, f"validate_{mode}")

    return parser(data)
