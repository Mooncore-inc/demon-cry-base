from abc import ABC, abstractmethod

class BaseModule(ABC):
    """Базовый класс для всех OSINT-модулей demon-cry."""

    name: str
    description: str
    category: str
    parameters: dict

    @abstractmethod
    async def execute(self, config: dict, **kwargs) -> dict:
        """Выполнение модуля.

        Args:
            config: Конфигурация модуля (загружена ядром).
            **kwargs: Параметры из запроса.

        Returns:
            dict с результатом.
        """
        ...