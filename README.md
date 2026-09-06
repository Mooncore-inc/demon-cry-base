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
from demon_cry_base import BaseModule, ModuleConfig


class PingModule(BaseModule):
    name = "ping"
    description = "Check if host is alive"
    category = "utility"
    parameters = {}

    async def execute(self, config: ModuleConfig, **kwargs) -> dict:
        return {"status": "ok"}
```

### Создание модуля

```python
from demon_cry_base import BaseModule, ModuleConfig


class MyModuleConfig(ModuleConfig):
    timeout: int = 30


class MyModule(BaseModule):
    name = "my_module"
    description = "My OSINT module"
    category = "custom"
    config_model = MyModuleConfig
    parameters = {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "Target to scan"},
            "query": {"type": "string", "description": "Search query"}
        },
        "required": ["target"]
    }

    async def execute(self, config: MyModuleConfig, target: str, query: str, **kwargs) -> dict:
        return {"result": f"Scanned {target}"}
```

### Два источника данных

Каждый модуль работает с двумя потоками данных:

| | **Config** | **Parameters** |
|---|---|---|
| Откуда | БД / ядро | Запрос / пользователь |
| Формат | Pydantic-модель (`ModuleConfig`) | JSON Schema (`dict`) |
| Зачем | Настройки модуля | Входные данные |
| Передаётся | `config` в `execute()` | `**kwargs` в `execute()` |

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
class ReconModule(BaseModule):
    name = "recon"
    description = "Network reconnaissance"
    category = "osint"
    config_model = ReconConfig
    parameters = {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "Target to scan"}
        },
        "required": ["target"]
    }

    async def execute(self, config: ReconConfig, target: str, **kwargs) -> dict:
        if config.deep:
            ...
```

#### Parameters — входные данные

`parameters` — JSON Schema, описывает что модуль принимает от пользователя:

```python
parameters = {
    "type": "object",
    "properties": {
        "domain": {"type": "string", "description": "Domain to lookup"},
        "record_type": {
            "type": "array",
            "items": {"type": "string", "enum": ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "PTR"]},
            "default": ["A"],
            "description": "Record types to query"
        }
    },
    "required": ["domain"]
}
```

#### Полный пример: модуль с обоими источниками

```python
import asyncio
import aiodns
from demon_cry_base import BaseModule, ModuleConfig


class DnsLookupConfig(ModuleConfig):
    name_servers: list[str] = ["1.1.1.1", "8.8.8.8"]


class DnsLookup(BaseModule):
    name = "dns_lookup"
    description = "Finds DNS records"
    category = "network"
    config_model = DnsLookupConfig
    parameters = {
        "type": "object",
        "properties": {
            "domain": {"type": "string", "description": "Domain to lookup"},
            "record_type": {
                "type": "array",
                "items": {"type": "string", "enum": ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "PTR"]},
                "default": ["A"],
                "description": "Record types to query"
            }
        },
        "required": ["domain"]
    }

    async def execute(self, config: DnsLookupConfig, domain: str, record_type: list[str] | None = None) -> dict:
        resolver = aiodns.DNSResolver(nameservers=config.name_servers)
        # config — настройки из БД (name_servers)
        # domain, record_type — входные данные из параметров
        ...
```
