#!/usr/bin/env python3
"""
Run frontend build in CI-like mode for pre-push checks.
"""

import subprocess  # nosec B404 - безопасное использование для npm команд
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path | None = None) -> int:
    proc = subprocess.run(cmd, cwd=cwd, text=True)  # nosec B603 - безопасные команды
    return proc.returncode


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    web_dir = root / "web" / "frontend"
    if not web_dir.exists():
        print("frontend directory not found, skipping", file=sys.stderr)
        return 0

    # Install only if node_modules missing to keep it fast locally
    if not (web_dir / "node_modules").exists():
        code = run(["npm", "ci"], cwd=web_dir)
        if code != 0:
            return code

    # Lint, test, build
    for cmd in (["npm", "run", "lint"], ["npm", "test"], ["npm", "run", "build"]):
        code = run(cmd, cwd=web_dir)
        if code != 0:
            return code

    print("Frontend build OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
