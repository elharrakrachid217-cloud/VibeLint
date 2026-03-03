#!/usr/bin/env python3
"""
install_mcp.py
==============
One-command installer that registers VibeLint in your IDE's MCP config.

Usage:
    python install_mcp.py              # auto-detect IDE
    python install_mcp.py --ide cursor
    python install_mcp.py --ide claude
    python install_mcp.py --ide windsurf

Solves the three most common MCP setup failures:
  1. IDE ignoring `cwd` and not finding server.py
  2. `python` command not resolving to the right interpreter
  3. Users mis-typing paths when editing JSON by hand
"""

import json
import platform
import sys
from pathlib import Path

VIBELINT_DIR = Path(__file__).parent.resolve()
SERVER_PY = VIBELINT_DIR / "server.py"
PYTHON_EXE = Path(sys.executable).resolve()

IDE_CONFIG_LOCATIONS = {
    "cursor": {
        "Windows": Path.home() / ".cursor" / "mcp.json",
        "Darwin":  Path.home() / ".cursor" / "mcp.json",
        "Linux":   Path.home() / ".cursor" / "mcp.json",
    },
    "windsurf": {
        "Windows": Path.home() / ".codeium" / "windsurf" / "mcp_config.json",
        "Darwin":  Path.home() / ".codeium" / "windsurf" / "mcp_config.json",
        "Linux":   Path.home() / ".codeium" / "windsurf" / "mcp_config.json",
    },
    "claude": {
        "Windows": Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json",
        "Darwin":  Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",
        "Linux":   Path.home() / ".config" / "Claude" / "claude_desktop_config.json",
    },
}

VIBELINT_ENTRY = {
    "command": str(PYTHON_EXE),
    "args": [str(SERVER_PY)],
}


def _step(msg: str) -> None:
    print(f"  {msg}")


def _detect_ides() -> list[str]:
    """Return list of IDE names whose config files exist on this machine."""
    os_name = platform.system()
    found = []
    for ide, paths in IDE_CONFIG_LOCATIONS.items():
        cfg = paths.get(os_name)
        if cfg and (cfg.exists() or cfg.parent.exists()):
            found.append(ide)
    return found


def _get_config_path(ide: str) -> Path:
    os_name = platform.system()
    paths = IDE_CONFIG_LOCATIONS.get(ide, {})
    cfg = paths.get(os_name)
    if not cfg:
        print(f"\n  ✗ No known config path for '{ide}' on {os_name}")
        sys.exit(1)
    return cfg


def _read_config(path: Path) -> dict:
    if not path.exists():
        return {"mcpServers": {}}
    try:
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            return {"mcpServers": {}}
        return json.loads(text)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"\n  ✗ Failed to read {path}: {exc}")
        sys.exit(1)


def _write_config(path: Path, config: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(
            json.dumps(config, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"\n  ✗ Failed to write {path}: {exc}")
        sys.exit(1)


def _install_for_ide(ide: str) -> bool:
    cfg_path = _get_config_path(ide)
    _step(f"Config: {cfg_path}")

    config = _read_config(cfg_path)
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    old_entry = config["mcpServers"].get("vibelint")
    if old_entry == VIBELINT_ENTRY:
        _step("Already installed with correct paths. Nothing to do.")
        return True

    if old_entry:
        _step("Updating existing vibelint entry with correct paths ...")
    else:
        _step("Adding vibelint to MCP config ...")

    config["mcpServers"]["vibelint"] = VIBELINT_ENTRY
    _write_config(cfg_path, config)
    _step(f"Wrote config to {cfg_path}")
    return True


def _verify() -> bool:
    """Quick sanity checks before installing."""
    ok = True

    if not SERVER_PY.exists():
        _step(f"✗ server.py not found at {SERVER_PY}")
        ok = False

    if not PYTHON_EXE.exists():
        _step(f"✗ Python executable not found at {PYTHON_EXE}")
        ok = False

    try:
        import mcp  # noqa: F401
    except ImportError:
        _step("✗ 'mcp' package not installed. Run: pip install -r requirements.txt")
        ok = False

    return ok


def main() -> None:
    print("VibeLint MCP Installer")
    print(f"  Python:    {PYTHON_EXE}")
    print(f"  Server:    {SERVER_PY}")
    print()

    if not _verify():
        print("\n  Fix the issues above and try again.")
        sys.exit(1)

    ide_arg = None
    if "--ide" in sys.argv:
        idx = sys.argv.index("--ide")
        if idx + 1 < len(sys.argv):
            ide_arg = sys.argv[idx + 1].lower()

    if ide_arg:
        targets = [ide_arg]
    else:
        targets = _detect_ides()
        if not targets:
            print("  No supported IDE config found. Use --ide to specify one:")
            print("    python install_mcp.py --ide cursor")
            print("    python install_mcp.py --ide windsurf")
            print("    python install_mcp.py --ide claude")
            sys.exit(1)

    all_ok = True
    for ide in targets:
        print(f"\n  [{ide.title()}]")
        if not _install_for_ide(ide):
            all_ok = False

    if all_ok:
        print("\n  Done! Restart your IDE to activate VibeLint.")
        print("  (In Cursor: Settings > MCP > click restart next to vibelint)")
    else:
        print("\n  ✗ Some installations failed. Review the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
