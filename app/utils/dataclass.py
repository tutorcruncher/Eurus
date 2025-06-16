from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class BaseRequest:
    def to_dict(self) -> Dict[str, Any]:
        def _convert_value(value: Any) -> Any:
            if hasattr(value, 'to_dict'):
                return value.to_dict()
            elif isinstance(value, dict):
                return {k: _convert_value(v) for k, v in value.items() if v is not None}
            elif isinstance(value, (list, tuple)):
                return [_convert_value(item) for item in value]
            return value

        data = asdict(self)
        return {k: _convert_value(v) for k, v in data.items() if v is not None}
