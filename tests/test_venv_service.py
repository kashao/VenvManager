import subprocess
from pathlib import Path

from venv_manager import venv_service
from venv_manager.venv_service import VenvService


def test_get_python_version_skips_non_python_executable(
    monkeypatch,
    tmp_path: Path,
) -> None:
    app_exe = tmp_path / "VenvManager.exe"
    app_exe.write_text("", encoding="utf-8")

    def fail_run(*_args, **_kwargs) -> subprocess.CompletedProcess[str]:
        raise AssertionError("non-Python executable should not be launched")

    monkeypatch.setattr(venv_service.subprocess, "run", fail_run)

    assert VenvService().get_python_version(app_exe) == "未知"


def test_discover_from_path_skips_frozen_app_executable(
    monkeypatch,
    tmp_path: Path,
) -> None:
    app_exe = tmp_path / "VenvManager.exe"
    app_exe.write_text("", encoding="utf-8")
    service = VenvService()

    def fake_run(
        command: list[str],
        **_kwargs,
    ) -> subprocess.CompletedProcess[str]:
        assert command == ["where.exe", "python"]
        return subprocess.CompletedProcess(command, 1, "", "")

    monkeypatch.setattr(venv_service.sys, "platform", "win32")
    monkeypatch.setattr(venv_service.sys, "executable", str(app_exe))
    monkeypatch.setattr(venv_service.sys, "frozen", True, raising=False)
    monkeypatch.setattr(venv_service.subprocess, "run", fake_run)

    assert service._discover_from_path() == []


def test_check_base_python_rejects_non_python_executable(
    monkeypatch,
    tmp_path: Path,
) -> None:
    app_exe = tmp_path / "VenvManager.exe"
    app_exe.write_text("", encoding="utf-8")

    def fail_run(*_args, **_kwargs) -> subprocess.CompletedProcess[str]:
        raise AssertionError("non-Python executable should not be launched")

    monkeypatch.setattr(venv_service.subprocess, "run", fail_run)

    assert not VenvService().check_base_python(str(app_exe))


def test_run_background_hides_windows_console(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_run(
        command: list[str],
        **kwargs,
    ) -> subprocess.CompletedProcess[str]:
        calls.append(kwargs)
        return subprocess.CompletedProcess(command, 0, "Python 3.11.3", "")

    monkeypatch.setattr(venv_service.sys, "platform", "win32")
    monkeypatch.setattr(venv_service.subprocess, "CREATE_NO_WINDOW", 0x08000000)
    monkeypatch.setattr(venv_service.subprocess, "run", fake_run)

    result = VenvService()._run_background(["python", "--version"])

    assert result.returncode == 0
    assert calls[0]["creationflags"] == 0x08000000
