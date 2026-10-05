from typing import Literal

from pydantic import BaseModel, SerializeAsAny


class BaseEntity(BaseModel):
    """Базовый энтити"""

    pass


class ErrorEntity(BaseEntity):
    code: str
    message: str
    details: dict | None = None


class PluginResult(BaseModel):
    status: Literal["ok", "error", "partial"]
    entities: SerializeAsAny[list[BaseEntity]]

    @classmethod
    def ok(cls, entities: list[BaseEntity] = None) -> "PluginResult":
        return cls(status="ok", entities=entities or [])

    @classmethod
    def error(cls, entities: list[BaseEntity] = None) -> "PluginResult":
        return cls(status="error", entities=entities or [])

    @classmethod
    def partial(cls, entities: list[BaseEntity] = None) -> "PluginResult":
        return cls(status="partial", entities=entities or [])
