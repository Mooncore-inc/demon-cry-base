from pydantic import BaseModel, SerializeAsAny


class BaseEntity(BaseModel):
    """Базовый энтити"""

    pass


class PluginResult(BaseModel):
    status: str
    entities: SerializeAsAny[list[BaseEntity]]
