from abc import ABC

from pydantic import BaseModel


class PluginConfig(BaseModel):
    """Базовый конфиг плагина."""

    pass


class PluginParameters(BaseModel):
    """Базовый конфиг параметров"""

    pass


class BaseEntity(BaseModel):
    """Базовый энтити"""

    pass


class BasePlugin(ABC):
    """Базовый класс для всех OSINT-плагинов demon-cry."""

    name: str
    description: str
    category: str
    parameters_model: type[PluginParameters] = PluginParameters
    config_model: type[PluginConfig] = PluginConfig
    execute_func: str
