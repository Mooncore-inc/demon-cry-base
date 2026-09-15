# demon-cry-base

Базовый класс для OSINT-плагинов [demon-cry](https://github.com/fazzyt/demon-cry)

## Установка

```bash
pip install demon-cry-base
```

## Использование

### Плагин без конфига

Для простых Stateless-плагинов можно использовать `PluginConfig` напрямую:

```python
from demon_cry_base import BasePlugin, PluginConfig, PluginParameters


class PingPlugin(BasePlugin):
    name = "ping"
    description = "Check if host is alive"
    category = "utility"
    parameters_model = PluginParameters

    async def execute(self, config: PluginConfig, params: PluginParameters) -> dict:
        return {"status": "ok"}
```

### Создание плагина

```python
from demon_cry_base import BasePlugin, PluginConfig, PluginParameters


class MyPluginParams(PluginParameters):
    target: str
    query: str | None = None


class MyPluginConfig(PluginConfig):
    timeout: int = 30


class MyPlugin(BasePlugin):
    name = "my_plugin"
    description = "My OSINT plugin"
    category = "custom"
    config_model = MyPluginConfig
    parameters_model = MyPluginParams

    async def execute(self, config: MyPluginConfig, params: MyPluginParams) -> dict:
        return {"result": f"Scanned {params.target}"}
```

### Два источника данных

Каждый плагин работает с двумя потоками данных:

| | **Config** | **Parameters** |
|---|---|---|
| Откуда | БД / ядро | Запрос / пользователь |
| Формат | Pydantic-модель (`PluginConfig`) | Pydantic-модель (`PluginParameters`) |
| Зачем | Настройки плагина | Входные данные |
| Передаётся | `config` в `execute()` | `params` в `execute()` |

#### Config — настройки из БД

`PluginConfig` — это Pydantic-модель. Наследуйте её и добавляйте поля:

```python
class ReconConfig(PluginConfig):
    deep: bool = False
    ports: list[int] = [80, 443]


class ApiConfig(PluginConfig):
    api_key: str
    rate_limit: int = 100
    timeout: int = 30
```

Затем укажите `config_model` в плагине. Ядро загрузит конфиг из БД и передаст в `execute()`:

```python
class ReconParams(PluginParameters):
    target: str


class ReconConfig(PluginConfig):
    deep: bool = False
    ports: list[int] = [80, 443]


class ReconPlugin(BasePlugin):
    name = "recon"
    description = "Network reconnaissance"
    category = "osint"
    config_model = ReconConfig
    parameters_model = ReconParams

    async def execute(self, config: ReconConfig, params: ReconParams) -> dict:
        if config.deep:
            ...
```

#### Parameters — входные данные

`PluginParameters` — это Pydantic-модель. Наследуйте её и добавляйте поля:

```python
from typing import Literal
from pydantic import Field
from demon_cry_base import PluginParameters


class SearchParams(PluginParameters):
    query: str
    category: Literal["general", "images", "files", "it", "social media", "news"] = "general"
    time_range: Literal["day", "week", "month", "year", "all"] = "all"
    max_results: int = Field(default=10, ge=1, le=100, description="Max results to return")
```

Затем укажите `parameters_model` в плагине:

```python
class SearchPlugin(BasePlugin):
    name = "search"
    description = "Web search"
    category = "osint"
    parameters_model = SearchParams

    async def execute(self, config: PluginConfig, params: SearchParams) -> dict:
        # params.query — строка
        # params.category — enum
        # params.max_results — int с валидацией
        ...
```

##### Паттерны параметров

| Паттерн | Пример |
|---------|--------|
| Обязательное поле | `target: str` |
| Optional поле | `query: str \| None = None` |
| Дефолт | `timeout: int = 30` |
| Enum-like | `category: Literal["a", "b", "c"] = "a"` |
| Валидация | `max_results: int = Field(default=10, ge=1, le=100)` |
| List поле | `ports: list[int] = [80, 443]` |

#### Полный пример: плагин с обоими источниками

```python
import asyncio
import aiodns
from typing import Literal
from demon_cry_base import BasePlugin, PluginConfig, PluginParameters


class DnsLookupParams(PluginParameters):
    domain: str
    record_type: list[Literal["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "PTR"]] = ["A"]


class DnsLookupConfig(PluginConfig):
    name_servers: list[str] = ["1.1.1.1", "8.8.8.8"]


class DnsLookup(BasePlugin):
    name = "dns_lookup"
    description = "Finds DNS records"
    category = "network"
    config_model = DnsLookupConfig
    parameters_model = DnsLookupParams

    async def execute(self, config: DnsLookupConfig, params: DnsLookupParams) -> dict:
        resolver = aiodns.DNSResolver(nameservers=config.name_servers)
        # config — настройки из БД (name_servers)
        # params.domain — домен из параметров
        # params.record_type — типы записей
        ...

### Подключение к ядру (entry points)

Ядро находит плагины через `importlib.metadata.entry_points(group="demon_cry.plugins")`.

Укажите entry-point в `pyproject.toml` вашего плагина:

```toml
[project.entry-points."demon_cry.plugins"]
my_plugin = "my_package.my_plugin:MyPlugin"
```

- Ключ слева (`my_plugin`) — имя для логов/отладки. Регистрирует ядро по `instance.name`, а не по ключу — держите их одинаковыми, чтобы не путаться.
- Значение справа — `импорт-путь:КлассПлагина` (например `my_package.my_plugin:MyPlugin`). Класс должен наследовать `BasePlugin` и задавать `name`, `description`, `category`.

Как это работает на стороне ядра при `discover()`:

1. `ep.load()` → инстанцирует класс без аргументов, поэтому конструктор должен быть без обязательных аргументов.
2. Кладёт инстанс в реестр по `instance.name`.
3. Берёт дефолты из `instance.config_model().model_dump()` и создаёт запись в БД с `enabled=False`.

Требования к плагину: уникальное `name`, конструктор без аргументов, дефолтный конфиг должен быть валидным без секретов в коде.
```
