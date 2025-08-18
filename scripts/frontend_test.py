import os
import subprocess
import sys


def main() -> int:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(project_root, "web", "frontend")
    try:
        result = subprocess.run(["npm", "run", "test"], cwd=frontend_dir, check=False)
        return result.returncode
    except FileNotFoundError:
        print(
            "[pre-commit] npm not found in PATH, skipping frontend tests",
            file=sys.stderr,
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())
