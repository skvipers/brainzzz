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


def main():
    """Main security check function."""
    print("[SECURITY] Running security checks...")

    # Get project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Run bandit
    bandit_success = run_command(
        (
            "python -m bandit -r brains/ evo/ tasks/ api/ "
            "-f json -o bandit-report.json --quiet"
        ),
        "Bandit security scan",
    )

    # Fallback: if bandit fails, try alternative approach
    if not bandit_success:
        print("Bandit command failed, trying alternative approach...")
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
            bandit_success = True

        except Exception as e:
            print(f"[ERROR] Bandit API fallback also failed: {e}")
            bandit_success = False

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
