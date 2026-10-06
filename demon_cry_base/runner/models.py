from typing import Any, Literal

from pydantic import BaseModel, SerializeAsAny, computed_field


class BaseEntity(BaseModel):
    """Базовый энтити"""

    pass


class ErrorEntity(BaseEntity):
    code: str
    message: str
    details: dict[str, Any] | None = None


class PluginResult(BaseModel):
    entities: SerializeAsAny[list[BaseEntity]]
    errors: list[ErrorEntity] = []

    @computed_field
    @property
    def status(self) -> Literal["ok", "error", "partial"]:
        has_data = bool(self.entities)
        has_errors = bool(self.errors)

        if not has_data and has_errors:
            return "error"
        if has_data and has_errors:
            return "partial"
        return "ok"

    @classmethod
    def build(
        cls,
        entities: list[BaseEntity] | None = None,
        errors: list[ErrorEntity] | None = None,
    ) -> "PluginResult":
        return cls(entities=entities or [], errors=errors or [])
