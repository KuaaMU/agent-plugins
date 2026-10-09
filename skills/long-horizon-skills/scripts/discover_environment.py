#!/usr/bin/env python3
"""Read-only discovery of compilers, tooling, devices, and versions.

v2: tool list is profile-driven. Base list is generic; a domain profile
(references/profiles/<name>.tools.json) may add extra tools and env keys.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path


BASE_TOOLS = [
    ("git", ["--version"]),
    ("cmake", ["--version"]),
    ("ninja", ["--version"]),
    ("make", ["--version"]),
    ("g++", ["--version"]),
    ("clang++", ["--version"]),
    ("python3", ["--version"]),
    ("nvidia-smi", ["--version"]),
    ("rocminfo", ["--version"]),
]
BASE_ENV_KEYS = ["PATH", "HOME"]


def command_output(command: list[str], timeout: int) -> dict[str, object]:
    try:
        result = subprocess.run(
            command, check=False, capture_output=True, text=True, timeout=timeout
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"found": False, "error": str(exc)}
    out = (result.stdout or result.stderr or "").strip().splitlines()
    return {
        "found": result.returncode == 0,
        "version": out[0] if out else "",
        "path": shutil.which(command[0]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        default="",
        help="Domain profile name; loads references/profiles/<name>.tools.json if present",
    )
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self test")
    args = parser.parse_args()

    if args.self_test:
        info = command_output(["git", "--version"], 5)
        assert isinstance(info, dict) and "found" in info
        print("discover_environment --self-test: OK")
        return 0

    tools = list(BASE_TOOLS)
    env_keys = list(BASE_ENV_KEYS)
    if args.profile:
        skill_root = Path(__file__).resolve().parent.parent
        profile_tools = skill_root / "references" / "profiles" / f"{args.profile}.tools.json"
        if profile_tools.is_file():
            data = json.loads(profile_tools.read_text(encoding="utf-8"))
            tools.extend((t["bin"], t.get("args", ["--version"])) for t in data.get("tools", []))
            env_keys.extend(data.get("env_keys", []))
        else:
            print(f"note: no tools file for profile '{args.profile}'; using base list")

    report: dict[str, object] = {
        "platform": platform.platform(),
        "tools": {name: command_output([name, *cargs], args.timeout) for name, cargs in tools},
        "env": {key: os.environ.get(key, "") for key in env_keys},
    }
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"platform: {report['platform']}")
        for name, info in report["tools"].items():  # type: ignore[union-attr]
            status = "OK " if info["found"] else "MISS"
            print(f"[{status}] {name}: {info.get('version') or info.get('path') or '-'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
