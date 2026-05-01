from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from venv_manager.paths import get_config_path, get_default_venv_root

DEFAULT_BASE_PYTHON = "py -3.11"
DEFAULT_THEME = "flatly"
DARK_THEME = "darkly"


@dataclass(slots=True)
class AppConfig:
    venv_root: str
    base_python: str = DEFAULT_BASE_PYTHON
    theme: str = DEFAULT_THEME
    venv_workdirs: dict[str, str] = field(default_factory=dict)
    last_open_dir: str = ""


def get_default_config() -> AppConfig:
    return AppConfig(venv_root=str(get_default_venv_root()))


class ConfigStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or get_config_path()

    def load(self) -> AppConfig:
        if not self.path.exists():
            config = get_default_config()
            self._try_save_default(config)
            return config

        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            config = get_default_config()
            self._try_save_default(config)
            return config

        return self._normalize(data)

    def save(self, config: AppConfig) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(asdict(config), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _normalize(self, data: dict[str, Any]) -> AppConfig:
        default = get_default_config()
        workdirs = data.get("venv_workdirs")
        return AppConfig(
            venv_root=str(data.get("venv_root") or default.venv_root),
            base_python=str(data.get("base_python") or default.base_python),
            theme=str(data.get("theme") or default.theme),
            venv_workdirs={
                str(key): str(value)
                for key, value in (workdirs if isinstance(workdirs, dict) else {}).items()
                if value
            },
            last_open_dir=str(data.get("last_open_dir") or ""),
        )

    def _try_save_default(self, config: AppConfig) -> None:
        # First launch should still work when the config directory cannot be written yet.
        try:
            self.save(config)
        except OSError:
            return
