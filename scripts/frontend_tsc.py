import os
import subprocess  # nosec B404 - безопасное использование для запуска npx
import sys


def main() -> int:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(project_root, "web", "frontend")
    try:
        result = subprocess.run(  # nosec B607,B603 - безопасные команды npx
            ["/usr/bin/npx", "tsc", "--noEmit"], cwd=frontend_dir, check=False
        )
        return result.returncode
    except FileNotFoundError:
        print(
            "[pre-commit] npx not found in PATH, skipping TypeScript check",
            file=sys.stderr,
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())
