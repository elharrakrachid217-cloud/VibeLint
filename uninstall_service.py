#!/usr/bin/env python3
"""
uninstall_service.py
====================
Remove the VibeGuard background service on Windows, macOS, or Linux.

Usage:
    python uninstall_service.py
"""

import platform
import subprocess
import sys
from pathlib import Path

# ── Same identifiers used by install_service.py ─────────────────────
VIBEGUARD_DIR = Path(__file__).parent.resolve()
TASK_NAME = "VibeGuard"
RUNNER_BAT = VIBEGUARD_DIR / "_service_runner.bat"

PLIST_LABEL = "com.vibeguard.server"
PLIST_PATH = (
    Path.home() / "Library" / "LaunchAgents" / f"{PLIST_LABEL}.plist"
)

SYSTEMD_UNIT = "vibeguard.service"
SYSTEMD_PATH = Path.home() / ".config" / "systemd" / "user" / SYSTEMD_UNIT


def _step(msg: str) -> None:
    print(f"  {msg}")


# ═════════════════════════════════════════════════════════════════════
# Windows
# ═════════════════════════════════════════════════════════════════════

def _uninstall_windows() -> None:
    print("\n🪟  Detected: Windows")
    print("  Removing Task Scheduler entry …\n")

    try:
        check = subprocess.run(
            ["schtasks", "/Query", "/TN", TASK_NAME],
            capture_output=True, text=True,
        )
    except FileNotFoundError:
        _step("✗ 'schtasks' command not found.")
        return

    if check.returncode != 0:
        _step(f"ℹ  Task '{TASK_NAME}' is not registered. Nothing to remove.")
        return

    subprocess.run(
        ["schtasks", "/End", "/TN", TASK_NAME],
        capture_output=True, text=True,
    )
    _step("✓ Stopped running task")

    try:
        result = subprocess.run(
            ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            if "access" in stderr.lower():
                _step("✗ Permission denied. Run this script as Administrator.")
            else:
                _step(f"✗ schtasks /Delete failed: {stderr}")
            return
        _step(f"✓ Task '{TASK_NAME}' removed from Task Scheduler")
    except FileNotFoundError:
        _step("✗ 'schtasks' command not found.")
        return

    if RUNNER_BAT.exists():
        try:
            RUNNER_BAT.unlink()
            _step("✓ Runner script removed")
        except OSError:
            pass


# ═════════════════════════════════════════════════════════════════════
# macOS
# ═════════════════════════════════════════════════════════════════════

def _uninstall_mac() -> None:
    print("\n🍎  Detected: macOS")
    print("  Removing launchd service …\n")

    if not PLIST_PATH.exists():
        _step("ℹ  Service is not installed. Nothing to remove.")
        return

    try:
        subprocess.run(
            ["launchctl", "unload", str(PLIST_PATH)],
            capture_output=True, text=True,
        )
        _step("✓ Service unloaded (stopped)")
    except FileNotFoundError:
        _step("⚠  'launchctl' not found — skipping unload.")

    try:
        PLIST_PATH.unlink()
        _step(f"✓ Plist removed: {PLIST_PATH}")
    except PermissionError:
        _step(f"✗ Permission denied removing {PLIST_PATH}")
        _step(f'  Remove manually: rm "{PLIST_PATH}"')


# ═════════════════════════════════════════════════════════════════════
# Linux
# ═════════════════════════════════════════════════════════════════════

def _uninstall_linux() -> None:
    print("\n🐧  Detected: Linux")
    print("  Removing systemd user service …\n")

    if not SYSTEMD_PATH.exists():
        _step("ℹ  Service is not installed. Nothing to remove.")
        return

    try:
        subprocess.run(
            ["systemctl", "--user", "stop", SYSTEMD_UNIT],
            capture_output=True, text=True,
        )
        _step("✓ Service stopped")
        subprocess.run(
            ["systemctl", "--user", "disable", SYSTEMD_UNIT],
            capture_output=True, text=True,
        )
        _step("✓ Service disabled")
    except FileNotFoundError:
        _step("⚠  'systemctl' not found — skipping stop/disable.")

    try:
        SYSTEMD_PATH.unlink()
        _step(f"✓ Unit file removed: {SYSTEMD_PATH}")
    except PermissionError:
        _step(f"✗ Permission denied removing {SYSTEMD_PATH}")
        _step(f'  Remove manually: rm "{SYSTEMD_PATH}"')

    try:
        subprocess.run(
            ["systemctl", "--user", "daemon-reload"],
            capture_output=True, text=True,
        )
        _step("✓ systemd daemon reloaded")
    except (FileNotFoundError, OSError):
        pass


# ═════════════════════════════════════════════════════════════════════
# Main
# ═════════════════════════════════════════════════════════════════════

def main() -> None:
    print("🛡️  VibeGuard Service Uninstaller")

    os_name = platform.system()

    if os_name == "Windows":
        _uninstall_windows()
    elif os_name == "Darwin":
        _uninstall_mac()
    elif os_name == "Linux":
        _uninstall_linux()
    else:
        print(f"\n  ✗ Unsupported OS: {os_name}")
        sys.exit(1)

    print("\n  Done! VibeGuard background service has been removed.")
    print("  Note: Log files in logs/ were not deleted.")


if __name__ == "__main__":
    main()
