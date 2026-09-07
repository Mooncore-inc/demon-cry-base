from abc import ABC, abstractmethod
from pydantic import BaseModel

class ModuleConfig(BaseModel):
    """Базовый конфиг модуля."""
    pass

class ModuleParameters(BaseModel):
    """Базовый конфиг параметров"""
    pass

class BaseModule(ABC):
    """Базовый класс для всех OSINT-модулей demon-cry."""

    name: str
    description: str
    category: str
    parameters_model: type[ModuleParameters] = ModuleParameters
    config_model: type[ModuleConfig] = ModuleConfig

    @abstractmethod
    async def execute(self, config: ModuleConfig, **kwargs) -> dict:
        """Выполнение модуля.

        Args:
            config: Конфигурация модуля (загружена ядром).
            **kwargs: Параметры из запроса.

        Returns:
            dict с результатом.
        """
        ...
