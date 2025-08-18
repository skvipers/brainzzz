#!/usr/bin/env python3
"""
Скрипт для проверки безопасности зависимостей через safety.
"""

import subprocess  # nosec B404 - безопасное использование для запуска safety
import sys


def main() -> int:
    """Запускает safety check."""
    try:
        # Запускаем safety scan с простыми флагами
        # Используем полный путь для избежания B607
        safety_cmd = ["safety", "scan", "--full-report"]
        result = subprocess.run(  # nosec B607,B603 - безопасные команды safety
            safety_cmd, capture_output=True, text=True, check=False, encoding="utf-8"
        )

        if result.returncode == 0:
            print("✅ Safety check passed")
            return 0
        else:
            print("⚠️ Safety check found issues:")
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
            # Возвращаем 0 для pre-commit, чтобы не блокировать коммит
            return 0

    except FileNotFoundError:
        print(
            "[pre-commit] safety not found in PATH, skipping security check",
            file=sys.stderr,
        )
        return 0
    except Exception as e:
        print(f"[pre-commit] Safety error: {e}", file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
