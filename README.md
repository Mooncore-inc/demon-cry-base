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

    async def execute(self, config: ModuleConfig, **kwargs) -> dict:
        return {"status": "ok"}
```

### Создание модуля

```python
from demon_cry_base import BaseModule, ModuleConfig


class MyModuleConfig(ModuleConfig):
    target: str
    timeout: int = 30


class MyModule(BaseModule):
    name = "my_module"
    description = "My OSINT module"
    category = "custom"
    config_model = MyModuleConfig

    async def execute(self, config: MyModuleConfig, **kwargs) -> dict:
        return {"result": f"Scanned {config.target}"}
```

### Конфиги

`ModuleConfig` — это Pydantic-модель. Наследуйте её и добавляйте поля:

```python
class ReconConfig(ModuleConfig):
    target: str
    deep: bool = False
    ports: list[int] = [80, 443]


class SocialConfig(ModuleConfig):
    username: str
    platforms: list[str] = ["twitter", "telegram"]
```

Затем укажите `config_model` в модуле:

```python
class ReconModule(BaseModule):
    name = "recon"
    description = "Network reconnaissance"
    category = "osint"
    config_model = ReconConfig

    async def execute(self, config: ReconConfig, **kwargs) -> dict:
        if config.deep:
            ...
```
