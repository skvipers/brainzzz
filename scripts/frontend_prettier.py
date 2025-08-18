import os
import subprocess
import sys


def main() -> int:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(project_root, "web", "frontend")
    try:
        result = subprocess.run(
            ["npx", "prettier", "--write", "."], cwd=frontend_dir, check=False
        )
        return result.returncode
    except FileNotFoundError:
        print("[pre-commit] npx not found in PATH, skipping Prettier", file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
