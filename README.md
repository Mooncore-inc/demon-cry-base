# demon-cry-base

Базовый класс для OSINT-модулей [demon-cry](https://github.com/fazzyt/demon-cry)

## Установка

```bash
pip install demon-cry-base
Использование
from demon_cry_base import BaseModule

class MyModule(BaseModule):
    name = "my_module"
    description = "My OSINT module"
    category = "custom"
    parameters = {"target": {"type": "string", "required": True}}

    async def execute(self, config: dict, target: str, **kwargs) -> dict:
        return {"result": f"Scanned {target}"}