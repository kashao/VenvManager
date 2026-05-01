from __future__ import annotations

import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

BASE_PYTHON_ERROR = (
    "找不到可用的 Base Python，請先安裝 Python，或在設定中指定 python.exe 路徑。"
)


@dataclass(frozen=True, slots=True)
class PythonInstallation:
    label: str
    command: str
    path: Path | None = None
    version: str = ""


@dataclass(frozen=True, slots=True)
class VenvInfo:
    name: str
    path: Path
    python_executable: Path
    activate_script: Path
    python_version: str


class VenvService:
    def list_venvs(self, root: Path) -> list[VenvInfo]:
        root.mkdir(parents=True, exist_ok=True)
        venvs: list[VenvInfo] = []
        for child in sorted(root.iterdir(), key=lambda item: item.name.lower()):
            if child.is_dir() and self.is_venv(child):
                venvs.append(self.get_venv_info(child))
        return venvs

    def is_venv(self, path: Path) -> bool:
        return (path / "pyvenv.cfg").exists()

    def create_venv(self, root: Path, name: str, base_python: str) -> Path:
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("請輸入虛擬環境名稱。")
        if any(separator in clean_name for separator in ("\\", "/")):
            raise ValueError("虛擬環境名稱不能包含路徑分隔符號。")

        root.mkdir(parents=True, exist_ok=True)
        target = root / clean_name
        if target.exists():
            raise FileExistsError(f"虛擬環境已存在：{clean_name}")

        if not self.check_base_python(base_python):
            raise RuntimeError(BASE_PYTHON_ERROR)

        command = [*self._split_base_python(base_python), "-m", "venv", str(target)]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            details = (result.stderr or result.stdout).strip()
            raise RuntimeError(details or f"建立虛擬環境失敗：{clean_name}")
        return target

    def delete_venv(self, path: Path) -> None:
        if not self.is_venv(path):
            raise ValueError(f"不是有效的虛擬環境：{path}")
        shutil.rmtree(path)

    def install_package(self, venv_path: Path, package_spec: str) -> None:
        package = package_spec.strip()
        if not package:
            raise ValueError("請輸入套件名稱。")
        self._run_pip(venv_path, ["install", package])

    def install_requirements_file(self, venv_path: Path, requirements_file: Path) -> None:
        if not requirements_file.exists():
            raise FileNotFoundError(f"找不到 requirements 檔案：{requirements_file}")
        self._run_pip(venv_path, ["install", "-r", str(requirements_file)])

    def get_installed_packages(self, venv_path: Path) -> list[str]:
        python = self.get_python_executable(venv_path)
        if not python.exists():
            raise FileNotFoundError(f"找不到 venv Python：{python}")
        result = subprocess.run(
            [str(python), "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            details = (result.stderr or result.stdout).strip()
            raise RuntimeError(details or "讀取已安裝套件失敗。")
        return [line for line in result.stdout.splitlines() if line.strip()]

    def check_base_python(self, base_python: str) -> bool:
        try:
            command = [*self._split_base_python(base_python), "--version"]
            result = subprocess.run(command, capture_output=True, text=True, check=False)
        except (OSError, ValueError):
            return False
        return result.returncode == 0

    def discover_base_pythons(self) -> list[PythonInstallation]:
        """Find Python installations that can be used to create venvs."""
        installs: dict[str, PythonInstallation] = {}

        for install in self._discover_from_py_launcher():
            installs[install.command] = install

        for install in self._discover_from_path():
            installs.setdefault(install.command, install)

        return sorted(installs.values(), key=lambda item: item.label.lower())

    def get_venv_info(self, path: Path) -> VenvInfo:
        python_executable = self.get_python_executable(path)
        activate_script = path / "Scripts" / "Activate.ps1"
        return VenvInfo(
            name=path.name,
            path=path,
            python_executable=python_executable,
            activate_script=activate_script,
            python_version=self.get_python_version(python_executable),
        )

    def get_python_executable(self, path: Path) -> Path:
        if sys.platform == "win32":
            return path / "Scripts" / "python.exe"
        return path / "bin" / "python"

    def get_python_version(self, python_executable: Path) -> str:
        if not python_executable.exists():
            return "未知"
        result = subprocess.run(
            [str(python_executable), "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return "未知"
        return (result.stdout or result.stderr).strip() or "未知"

    def get_activation_command(self, venv_path: Path) -> str:
        activate_script = venv_path / "Scripts" / "Activate.ps1"
        return f"& '{activate_script}'"

    def open_activated_shell(self, venv_path: Path, workdir: Path | None = None) -> None:
        target_dir = workdir if workdir and workdir.exists() else venv_path
        if sys.platform == "win32":
            activate_script = venv_path / "Scripts" / "Activate.ps1"
            if not activate_script.exists():
                raise FileNotFoundError(f"找不到啟用腳本：{activate_script}")
            command = (
                f"Set-Location -LiteralPath {self._ps_quote(target_dir)}; "
                f". {self._ps_quote(activate_script)}"
            )
            subprocess.Popen(
                [
                    "cmd",
                    "/c",
                    "start",
                    "",
                    "powershell.exe",
                    "-NoExit",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    command,
                ],
                cwd=str(target_dir),
            )
            return

        activate_script = venv_path / "bin" / "activate"
        if not activate_script.exists():
            raise FileNotFoundError(f"找不到啟用腳本：{activate_script}")
        shell_command = (
            f"cd {shlex.quote(str(target_dir))}; "
            f"source {shlex.quote(str(activate_script))}; exec bash"
        )
        subprocess.Popen(
            [self._terminal_command(), "-e", f"bash -lc {shlex.quote(shell_command)}"],
            cwd=str(target_dir),
        )

    def _run_pip(self, venv_path: Path, pip_args: list[str]) -> None:
        python = self.get_python_executable(venv_path)
        if not python.exists():
            raise FileNotFoundError(f"找不到 venv Python：{python}")
        result = subprocess.run(
            [str(python), "-m", "pip", *pip_args],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            details = (result.stderr or result.stdout).strip()
            raise RuntimeError(details or "pip 執行失敗。")

    def _discover_from_py_launcher(self) -> list[PythonInstallation]:
        if sys.platform != "win32":
            return []
        try:
            result = subprocess.run(["py", "-0p"], capture_output=True, text=True, check=False)
        except OSError:
            return []
        if result.returncode != 0:
            return []

        installs: list[PythonInstallation] = []
        for line in result.stdout.splitlines():
            match = re.search(
                r"-(?:V:)?(\d+(?:\.\d+)*)(?:[^\s]*)?\s+\*?\s*(.+python\.exe)$",
                line.strip(),
                re.I,
            )
            if not match:
                continue
            version, executable = match.groups()
            command = f"py -{version}"
            path = Path(executable.strip())
            label = f"Python {version} ({command})"
            if path.exists():
                label = f"{label} - {path}"
            installs.append(
                PythonInstallation(label=label, command=command, path=path, version=version)
            )
        return installs

    def _discover_from_path(self) -> list[PythonInstallation]:
        candidates: list[str] = []
        command = ["where.exe", "python"] if sys.platform == "win32" else ["which", "-a", "python3"]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=False)
        except OSError:
            result = subprocess.CompletedProcess(command, 1, "", "")

        if result.returncode == 0:
            candidates.extend(line.strip() for line in result.stdout.splitlines() if line.strip())
        candidates.append(sys.executable)

        installs: list[PythonInstallation] = []
        seen: set[str] = set()
        for candidate in candidates:
            path = Path(candidate)
            if not path.exists():
                continue
            normalized = str(path).lower()
            if normalized in seen or "windowsapps" in normalized:
                continue
            seen.add(normalized)
            version = self.get_python_version(path)
            if version == "未知":
                continue
            installs.append(
                PythonInstallation(
                    label=f"{version} - {path}",
                    command=str(path),
                    path=path,
                    version=version.replace("Python ", ""),
                )
            )
        return installs

    def _split_base_python(self, base_python: str) -> list[str]:
        command = base_python.strip()
        if command.lower().endswith(".exe") and Path(command).exists():
            return [command]
        if command.startswith('"'):
            end_quote = command.find('"', 1)
            if end_quote > 1:
                executable = command[1:end_quote]
                rest = command[end_quote + 1 :].strip()
                return [executable, *shlex.split(rest, posix=False)] if rest else [executable]
        parts = shlex.split(command, posix=False)
        if not parts:
            raise ValueError(BASE_PYTHON_ERROR)
        return parts

    def _ps_quote(self, path: Path) -> str:
        return "'" + str(path).replace("'", "''") + "'"

    def _terminal_command(self) -> str:
        for command in ("x-terminal-emulator", "gnome-terminal", "konsole"):
            if shutil.which(command):
                return command
        return "xterm"
