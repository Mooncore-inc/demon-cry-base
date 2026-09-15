from abc import ABC, abstractmethod

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

    @abstractmethod
    async def execute(self, config: PluginConfig, params: PluginParameters) -> dict:
        """Выполнение плагина.

        Args:
            config: Конфигурация плагина (загружена ядром).
            params: Параметры из запроса.

        Returns:
            dict с результатом.
        """
        ...
