#!/usr/bin/env python3
"""
Security check script for local development.
Runs bandit and safety checks without interactive prompts.
"""

import os
import subprocess  # nosec B404
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors gracefully."""
    print(f"Running {description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True  # nosec B602
        )
        print(f"[SUCCESS] {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed with exit code {e.returncode}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main():
    """Main security check function."""
    print("[SECURITY] Running security checks...")

    # Get project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Run bandit
    bandit_success = run_command(
        "python -m bandit -r brains/ evo/ tasks/ api/ -f json -o bandit-report.json",
        "Bandit security scan",
    )

    # Run safety check
    safety_success = run_command(
        "python -m safety check --output json --save-json safety-report.json",
        "Safety dependency vulnerability scan",
    )

    # Summary
    print("\n" + "=" * 50)
    if bandit_success and safety_success:
        print("[SUCCESS] All security checks passed!")
        sys.exit(0)
    else:
        print("[WARNING] Some security checks failed. Check the reports above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
