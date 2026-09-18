from pydantic import BaseModel


class PluginConfig(BaseModel):
    """Базовый конфиг плагина."""

    pass


class PluginParameters(BaseModel):
    """Базовый конфиг параметров"""

    pass
