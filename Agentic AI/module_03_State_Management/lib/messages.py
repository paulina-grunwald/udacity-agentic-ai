from pydantic import BaseModel
from typing import Optional, Union, List, Dict, Literal

from lib.tooling import ToolCall


class BaseMessage(BaseModel):
    role: str
    content: Optional[str] = ""

    def dict(self) -> Dict:
        return dict(self)


class SystemMessage(BaseMessage):
    role: Literal["system"] = "system"


class UserMessage(BaseMessage):
    role: Literal["user"] = "user"


class ToolMessage(BaseMessage):
    role: Literal["tool"] = "tool"
    tool_call_id: str
    name: str
    content: str = ""


class AIMessage(BaseMessage):
    role: Literal["assistant"] = "assistant"
    content: Optional[str] = ""
    tool_calls: Optional[List[ToolCall]] = None


AnyMessage = Union[
    SystemMessage,
    UserMessage,
    AIMessage,
    ToolMessage,
]
