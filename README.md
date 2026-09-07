# demon-cry-base

Базовый класс для OSINT-модулей [demon-cry](https://github.com/fazzyt/demon-cry)

## Установка

```bash
pip install demon-cry-base
```

## Использование

### Модуль без конфига

Для простых Stateless-модулей можно использовать `ModuleConfig` напрямую:

```python
from demon_cry_base import BaseModule, ModuleConfig, ModuleParameters


class PingModule(BaseModule):
    name = "ping"
    description = "Check if host is alive"
    category = "utility"
    parameters_model = ModuleParameters

    async def execute(self, config: ModuleConfig, params: ModuleParameters, **kwargs) -> dict:
        return {"status": "ok"}
```

### Создание модуля

```python
from demon_cry_base import BaseModule, ModuleConfig, ModuleParameters


class MyModuleParams(ModuleParameters):
    target: str
    query: str | None = None


class MyModuleConfig(ModuleConfig):
    timeout: int = 30


class MyModule(BaseModule):
    name = "my_module"
    description = "My OSINT module"
    category = "custom"
    config_model = MyModuleConfig
    parameters_model = MyModuleParams

    async def execute(self, config: MyModuleConfig, params: MyModuleParams, **kwargs) -> dict:
        return {"result": f"Scanned {params.target}"}
```

### Два источника данных

Каждый модуль работает с двумя потоками данных:

| | **Config** | **Parameters** |
|---|---|---|
| Откуда | БД / ядро | Запрос / пользователь |
| Формат | Pydantic-модель (`ModuleConfig`) | Pydantic-модель (`ModuleParameters`) |
| Зачем | Настройки модуля | Входные данные |
| Передаётся | `config` в `execute()` | `params` в `execute()` |

#### Config — настройки из БД

`ModuleConfig` — это Pydantic-модель. Наследуйте её и добавляйте поля:

```python
class ReconConfig(ModuleConfig):
    deep: bool = False
    ports: list[int] = [80, 443]


class ApiConfig(ModuleConfig):
    api_key: str
    rate_limit: int = 100
    timeout: int = 30
```

Затем укажите `config_model` в модуле. Ядро загрузит конфиг из БД и передаст в `execute()`:

```python
class ReconParams(ModuleParameters):
    target: str


class ReconConfig(ModuleConfig):
    deep: bool = False
    ports: list[int] = [80, 443]


class ReconModule(BaseModule):
    name = "recon"
    description = "Network reconnaissance"
    category = "osint"
    config_model = ReconConfig
    parameters_model = ReconParams

    async def execute(self, config: ReconConfig, params: ReconParams, **kwargs) -> dict:
        if config.deep:
            ...
```

#### Parameters — входные данные

`ModuleParameters` — это Pydantic-модель. Наследуйте её и добавляйте поля:

```python
from typing import Literal
from pydantic import Field
from demon_cry_base import ModuleParameters


class SearchParams(ModuleParameters):
    query: str
    category: Literal["general", "images", "files", "it", "social media", "news"] = "general"
    time_range: Literal["day", "week", "month", "year", "all"] = "all"
    max_results: int = Field(default=10, ge=1, le=100, description="Max results to return")
```

Затем укажите `parameters_model` в модуле:

```python
class SearchModule(BaseModule):
    name = "search"
    description = "Web search"
    category = "osint"
    parameters_model = SearchParams

    async def execute(self, config: ModuleConfig, params: SearchParams, **kwargs) -> dict:
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

#### Полный пример: модуль с обоими источниками

```python
import asyncio
import aiodns
from typing import Literal
from demon_cry_base import BaseModule, ModuleConfig, ModuleParameters


class DnsLookupParams(ModuleParameters):
    domain: str
    record_type: list[Literal["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "PTR"]] = ["A"]


class DnsLookupConfig(ModuleConfig):
    name_servers: list[str] = ["1.1.1.1", "8.8.8.8"]


class DnsLookup(BaseModule):
    name = "dns_lookup"
    description = "Finds DNS records"
    category = "network"
    config_model = DnsLookupConfig
    parameters_model = DnsLookupParams

    async def execute(self, config: DnsLookupConfig, params: DnsLookupParams, **kwargs) -> dict:
        resolver = aiodns.DNSResolver(nameservers=config.name_servers)
        # config — настройки из БД (name_servers)
        # params.domain — домен из параметров
        # params.record_type — типы записей
        ...
```
