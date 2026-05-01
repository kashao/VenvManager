from pathlib import Path

from venv_manager.config import AppConfig, ConfigStore, DEFAULT_BASE_PYTHON, DEFAULT_THEME


def test_load_creates_default_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    store = ConfigStore(config_path)

    config = store.load()

    assert config_path.exists()
    assert config.venv_root
    assert config.base_python == DEFAULT_BASE_PYTHON
    assert config.theme == DEFAULT_THEME
    assert config.venv_workdirs == {}


def test_save_and_load_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    store = ConfigStore(config_path)
    expected = AppConfig(
        venv_root=str(tmp_path / "venvs"),
        base_python="py -3.11",
        theme="darkly",
        venv_workdirs={str(tmp_path / "venvs" / "demo"): str(tmp_path / "projects" / "demo")},
        last_open_dir=str(tmp_path / "projects"),
    )

    store.save(expected)

    assert store.load() == expected


def test_invalid_config_falls_back_to_default(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("{broken", encoding="utf-8")
    store = ConfigStore(config_path)

    config = store.load()

    assert config.base_python == DEFAULT_BASE_PYTHON
    assert config.theme == DEFAULT_THEME


def test_load_merges_new_path_settings_from_old_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        '{"venv_root": "C:/venvs", "base_python": "py -3.12"}',
        encoding="utf-8",
    )
    store = ConfigStore(config_path)

    config = store.load()

    assert config.venv_root == "C:/venvs"
    assert config.base_python == "py -3.12"
    assert config.venv_workdirs == {}
    assert config.last_open_dir == ""
