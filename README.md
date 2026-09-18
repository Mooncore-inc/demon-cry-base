# demon-cry-base

Базовые контракты для OSINT-плагинов [demon-cry](https://github.com/fazzyt/demon-cry)

## Установка

```bash
pip install demon-cry-base
```

## Использование

> **Правило импортов:** импортируйте только из корней контекстов —
> `demon_cry_base.plugin` (всё для плагина) и `demon_cry_base.runner` (всё для раннера).
> Глубокие пути (например `demon_cry_base.plugin.models`) — приватные, не полагайтесь на них.

### Плагин без конфига

Для простых Stateless-плагинов можно использовать `PluginConfig` напрямую:

```python
from demon_cry_base.plugin import BasePlugin, PluginConfig, PluginParameters
from demon_cry_base.runner import PluginResult


async def ping_run(config: PluginConfig, params: PluginParameters) -> PluginResult:
    return PluginResult(status="ok", entities=[])


class PingPlugin(BasePlugin):
    name = "ping"
    description = "Check if host is alive"
    category = "utility"
    parameters_model = PluginParameters
    execute_func = "my_package.ping:ping_run"
```

`execute_func` — путь к раннеру в формате `путь.до.модуля:имя_функции`.
Раннер — отдельная `async`-функция `(config, params) -> PluginResult`, ядро импортирует её через `importlib`.

### Создание плагина

```python
from demon_cry_base.plugin import BasePlugin, PluginConfig, PluginParameters
from demon_cry_base.runner import PluginResult


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
    execute_func = "my_package.my_plugin:my_plugin_run"


async def my_plugin_run(config: MyPluginConfig, params: MyPluginParams) -> PluginResult:
    return PluginResult(status="ok", entities=[])
```

### Два источника данных

Каждый плагин работает с двумя потоками данных:

| | **Config** | **Parameters** |
|---|---|---|
| Откуда | БД / ядро | Запрос / пользователь |
| Формат | Pydantic-модель (`PluginConfig`) | Pydantic-модель (`PluginParameters`) |
| Зачем | Настройки плагина | Входные данные |
| Передаётся | `config` в функцию из `execute_func` | `params` в функцию из `execute_func` |

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

Затем укажите `config_model` в плагине. Ядро загрузит конфиг из БД и передаст в функцию из `execute_func`:

```python
from demon_cry_base.runner import PluginResult


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
    execute_func = "my_package.recon:recon_run"


async def recon_run(config: ReconConfig, params: ReconParams) -> PluginResult:
    if config.deep:
        ...
```

#### Parameters — входные данные

`PluginParameters` — это Pydantic-модель. Наследуйте её и добавляйте поля:

```python
from typing import Literal
from pydantic import Field
from demon_cry_base.plugin import PluginParameters


class SearchParams(PluginParameters):
    query: str
    category: Literal["general", "images", "files", "it", "social media", "news"] = (
        "general"
    )
    time_range: Literal["day", "week", "month", "year", "all"] = "all"
    max_results: int = Field(
        default=10, ge=1, le=100, description="Max results to return"
    )
```

Затем укажите `parameters_model` в плагине:

```python
from demon_cry_base.plugin import BasePlugin, PluginConfig
from demon_cry_base.runner import PluginResult


class SearchPlugin(BasePlugin):
    name = "search"
    description = "Web search"
    category = "osint"
    parameters_model = SearchParams
    execute_func = "my_package.search:search_run"


async def search_run(config: PluginConfig, params: SearchParams) -> PluginResult:
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

### Выход плагина: entities

Раннер возвращает не `dict`, строку или число, а типизированный `PluginResult`:

```python
from demon_cry_base.runner import BaseEntity, PluginResult


class SearchHit(BaseEntity):
    title: str
    url: str
    snippet: str


async def search_run(config: SearchConfig, params: SearchParams) -> PluginResult:
    ...
    return PluginResult(
        status="ok",
        entities=[
            SearchHit(title="...", url="...", snippet="..."),
            SearchHit(title="...", url="...", snippet="..."),
        ],
    )
```

- `BaseEntity` — базовый класс сущности. Наследуйтесь и описывайте поля, которые плагин возвращает: `qtype`/`value`, `title`/`url`/`snippet` — чем угодно.
- `PluginResult.status` — статус выполнения (например `"ok"`).
- `PluginResult.entities` — список сущностей. Один запуск обычно возвращает их пачкой (2+), пустой список — валидный результат «ничего не найдено».

#### Полный пример: плагин с обоими источниками

```python
import aiodns
from typing import Literal
from demon_cry_base.plugin import BasePlugin, PluginConfig, PluginParameters
from demon_cry_base.runner import BaseEntity, PluginResult


class DnsLookupParams(PluginParameters):
    domain: str
    record_type: list[
        Literal["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "PTR"]
    ] = ["A"]


class DnsLookupConfig(PluginConfig):
    name_servers: list[str] = ["1.1.1.1", "8.8.8.8"]


class DnsRecord(BaseEntity):
    qtype: str
    value: str


class DnsLookup(BasePlugin):
    name = "dns_lookup"
    description = "Finds DNS records"
    category = "network"
    config_model = DnsLookupConfig
    parameters_model = DnsLookupParams
    execute_func = "my_package.dns:dns_lookup_run"


async def dns_lookup_run(
    config: DnsLookupConfig, params: DnsLookupParams
) -> PluginResult:
    resolver = aiodns.DNSResolver(nameservers=config.name_servers)
    # config — настройки из БД (name_servers)
    # params.domain — домен из параметров
    # params.record_type — типы записей
    ...
    return PluginResult(
        status="ok",
        entities=[
            DnsRecord(qtype="A", value="93.184.216.34"),
            DnsRecord(qtype="AAAA", value="2606:2800:220:1:248:1893:25c8:1946"),
        ],
    )
```

### Подключение к ядру (entry points)

Ядро находит плагины через `importlib.metadata.entry_points(group="demon_cry.plugins")`.

Укажите entry-point в `pyproject.toml` вашего плагина:

```toml
[project.entry-points."demon_cry.plugins"]
my_plugin = "my_package.my_plugin:MyPlugin"
```

- Ключ слева (`my_plugin`) — имя для логов/отладки. Регистрирует ядро по `instance.name`, а не по ключу — держите их одинаковыми, чтобы не путаться.
- Значение справа — `импорт-путь:КлассПлагина` (например `my_package.my_plugin:MyPlugin`). Класс должен наследовать `BasePlugin` и задавать `name`, `description`, `category`, `execute_func`.

Не путайте два похожих формата `модуль:объект`:

- entry-point (`my_package.my_plugin:MyPlugin`) — указывает на **класс** плагина;
- `execute_func` (`my_package.my_plugin:my_plugin_run`) — указывает на **async-функцию-раннер** `(config, params) -> PluginResult`.

Как это работает на стороне ядра при `discover()`:

1. `ep.load()` → инстанцирует класс без аргументов, поэтому конструктор должен быть без обязательных аргументов.
2. Кладёт инстанс в реестр по `instance.name`.
3. Берёт дефолты из `instance.config_model().model_dump()` и создаёт запись в БД с `enabled=False`.

Требования к плагину: уникальное `name`, конструктор без аргументов, дефолтный конфиг должен быть валидным без секретов в коде.
