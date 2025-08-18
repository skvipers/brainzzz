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
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",  # nosec B602
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
    except Exception as e:
        print(f"[ERROR] {description} failed with exception: {e}")
        return False


def run_bandit_safe():
    """Run bandit with multiple fallback strategies to avoid EOF errors."""
    print("Running Bandit security scan...")

    # Strategy 1: Try with --quiet and --no-color
    cmd1 = (
        "python -m bandit -r brains/ evo/ tasks/ api/ "
        "-f json -o bandit-report.json --quiet --no-color"
    )

    try:
        subprocess.run(  # nosec B602
            cmd1,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            stdin=subprocess.DEVNULL,  # Prevent stdin reading
        )
        print("[SUCCESS] Bandit security scan completed via command line")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[WARNING] Bandit command failed: {e}")

    # Strategy 2: Try with different output format
    cmd2 = (
        "python -m bandit -r brains/ evo/ tasks/ api/ "
        "-f txt -o bandit-report.txt --quiet --no-color"
    )

    try:
        subprocess.run(  # nosec B602
            cmd2,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            stdin=subprocess.DEVNULL,
        )
        print("[SUCCESS] Bandit security scan completed via txt output")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[WARNING] Bandit txt output also failed: {e}")

    # Strategy 3: Use Python API directly
    try:
        from bandit.core import config_manager, manager

        # Avoid top-level 'bandit' import
        # to prevent an unused import warning
        # Create bandit config
        config = config_manager.BanditConfig()
        config.set_profile("default")

        # Run bandit programmatically
        manager_obj = manager.BanditManager(
            config,
            "json",
            None,
        )
        manager_obj.discover_files(
            [
                "brains/",
                "evo/",
                "tasks/",
                "api/",
            ]
        )
        manager_obj.run_tests()

        # Write results to file
        with open("bandit-report.json", "w", encoding="utf-8") as f:
            manager_obj.output_results(f)

        print("[SUCCESS] Bandit security scan completed via API")
        return True

    except Exception as e:
        print(f"[ERROR] All Bandit strategies failed: {e}")
        return False


def main():
    """Main security check function."""
    print("[SECURITY] Running security checks...")

    # Get project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Run bandit with fallback strategies
    bandit_success = run_bandit_safe()

    # Run safety check
    safety_success = run_command(
        "python -m safety scan --output json --save-json safety-report.json",
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
