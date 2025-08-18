#!/usr/bin/env python3
"""
Run frontend build in CI-like mode for pre-push checks.
"""

import os
import subprocess  # nosec B404 - безопасное использование для npm команд
import sys
from pathlib import Path


def find_npm() -> str:
    """Находит npm в PATH или возвращает 'npm'."""
    # Проверяем, есть ли npm в PATH
    if os.name == "nt":  # Windows
        npm_paths = [
            r"C:\Program Files\nodejs\npm.cmd",
            r"C:\Program Files\nodejs\npm.exe",
            "npm.cmd",
            "npm",
        ]
    else:  # Unix/Linux
        npm_paths = ["npm"]

    for npm_path in npm_paths:
        try:
            result = subprocess.run(
                [npm_path, "--version"], capture_output=True, text=True
            )  # nosec B603 - безопасные команды
            if result.returncode == 0:
                return npm_path
        except (FileNotFoundError, OSError):
            continue

    return "npm"  # fallback


def run(cmd: list[str], cwd: Path | None = None) -> int:
    proc = subprocess.run(cmd, cwd=cwd, text=True)  # nosec B603 - безопасные команды
    return proc.returncode


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    web_dir = root / "web" / "frontend"
    if not web_dir.exists():
        print("frontend directory not found, skipping", file=sys.stderr)
        return 0

    npm_cmd = find_npm()
    print(f"Using npm: {npm_cmd}")

    # Install only if node_modules missing to keep it fast locally
    if not (web_dir / "node_modules").exists():
        code = run([npm_cmd, "ci"], cwd=web_dir)
        if code != 0:
            return code

    # Lint, test, build
    for cmd in ([npm_cmd, "run", "lint"], [npm_cmd, "test"], [npm_cmd, "run", "build"]):
        code = run(cmd, cwd=web_dir)
        if code != 0:
            return code

    print("Frontend build OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
