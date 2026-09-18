from abc import ABC

from demon_cry_base.plugin.models import PluginConfig, PluginParameters


class BasePlugin(ABC):
    """Базовый класс для всех OSINT-плагинов demon-cry."""

    name: str
    description: str
    category: str
    parameters_model: type[PluginParameters] = PluginParameters
    config_model: type[PluginConfig] = PluginConfig
    execute_func: str
