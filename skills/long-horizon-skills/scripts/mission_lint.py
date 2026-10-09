#!/usr/bin/env python3
"""Check a mission for structural drift, stale handoffs, broken evidence links,
and file-hygiene violations (merged skill).

Exit 1 on ERROR, 0 otherwise (warnings do not fail).
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED_FILES = [
    "AGENT.md",
    "TASK_ANCHOR.md",
    "state.json",
    "CLAIMS.jsonl",
    "STATE.md",
    "CANDIDATES.md",
    "PLAN.md",
    "REVIEW.md",
    "LESSONS.md",
    "HANDOFF.md",
    "HARDSET.md",
    "METRICS.md",
    "EVENTS.md",
    "INDEX.md",
]
REQUIRED_DIRS = ["evidence", "worklog", "reports", "archive", "scratch", "research", "hard-set"]
PLACEHOLDER_PATTERNS = [
    re.compile(r"\[TODO", re.IGNORECASE),
    re.compile(r"\bTODO\b"),
    re.compile(r"\bTBD\b"),
    re.compile(r"<fill", re.IGNORECASE),
]
HASH_PATTERN = re.compile(r"\b[0-9a-fA-F]{12,64}\b")
RESEARCH_QUOTA = 20  # references/file-hygiene.md: research/ file budget


def lint_mission(mission: Path, allow_placeholders: bool = False) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not mission.is_dir():
        return [f"mission directory not found: {mission}"], []

    for name in REQUIRED_FILES:
        path = mission / name
        if not path.is_file():
            errors.append(f"missing file: {name}")
            continue
        if name.endswith(".jsonl") or name.endswith(".json"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if not allow_placeholders:
            for pattern in PLACEHOLDER_PATTERNS:
                if pattern.search(text):
                    errors.append(f"unresolved placeholder in {name}: {pattern.pattern}")

    state_path = mission / "state.json"
    if state_path.is_file():
        try:
            data = json.loads(state_path.read_text(encoding="utf-8"))
            for key in ("task", "round", "frame", "failure_set"):
                if key not in data:
                    errors.append(f"state.json missing key: {key}")
        except json.JSONDecodeError as exc:
            errors.append(f"state.json is not valid JSON: {exc}")

    for name in REQUIRED_DIRS:
        if not (mission / name).is_dir():
            errors.append(f"missing directory: {name}/")

    state = mission / "STATE.md"
    handoff = mission / "HANDOFF.md"
    if state.is_file() and handoff.is_file():
        if handoff.stat().st_mtime + 1 < state.stat().st_mtime:
            warnings.append("HANDOFF.md is older than STATE.md; refresh the recovery point")
        combined = state.read_text(encoding="utf-8", errors="replace") + handoff.read_text(
            encoding="utf-8", errors="replace"
        )
        if not HASH_PATTERN.search(combined):
            warnings.append("STATE/HANDOFF contain no source or binary hash")

    review = mission / "REVIEW.md"
    if review.is_file():
        text = review.read_text(encoding="utf-8", errors="replace").lower()
        if "pending" in text and "verdict" not in text:
            warnings.append("REVIEW.md still appears to be pending")

    candidates = mission / "CANDIDATES.md"
    closed_ids: set[str] = set()
    if candidates.is_file():
        text = candidates.read_text(encoding="utf-8", errors="replace")
        if "| promoted |" in text and "evidence" not in text.lower():
            warnings.append("promoted candidates exist without evidence references")
        for line in text.splitlines():
            if line.startswith("|"):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) >= 2 and cells[1].lower() in {"closed", "close", "killed"}:
                    closed_ids.add(cells[0])

    # --- File-hygiene checks (references/file-hygiene.md) ---
    scratch = mission / "scratch"
    if scratch.is_dir():
        for child in scratch.iterdir():
            if child.is_dir() and child.name in closed_ids:
                errors.append(
                    f"orphan scratch dir for closed candidate: scratch/{child.name} "
                    "(archive or delete it)"
                )

    research = mission / "research"
    if research.is_dir():
        n = sum(1 for p in research.iterdir() if p.is_file())
        if n > RESEARCH_QUOTA:
            warnings.append(
                f"research/ holds {n} files (quota {RESEARCH_QUOTA}); digest before searching more"
            )

    for stray in mission.glob("*.md"):
        if stray.name not in REQUIRED_FILES:
            warnings.append(f"stray markdown at mission root: {stray.name} (move it or delete it)")

    return errors, warnings


def self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        mission = Path(tmp) / "m"
        # init_mission builds the templates; reuse it
        import subprocess, sys

        here = Path(__file__).resolve().parent
        r = subprocess.run(
            [sys.executable, str(here / "init_mission.py"), "--mission", str(mission),
             "--goal", "t", "--acceptance", "a"],
            capture_output=True, text=True,
        )
        assert r.returncode == 0, r.stderr
        errors, warnings = lint_mission(mission, allow_placeholders=True)
        assert not errors, errors
        # now poison it: orphan scratch dir for a closed candidate
        (mission / "CANDIDATES.md").write_text(
            "| ID | Status |\n|---|---|\n| C-1 | killed |\n", encoding="utf-8")
        (mission / "scratch" / "C-1").mkdir(parents=True)
        errors, _ = lint_mission(mission, allow_placeholders=True)
        assert any("orphan scratch" in e for e in errors), errors
    print("mission_lint --self-test: OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mission", nargs="?")
    parser.add_argument("--allow-placeholders", action="store_true")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self test")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if not args.mission:
        parser.error("mission is required (or use --self-test)")

    errors, warnings = lint_mission(Path(args.mission).expanduser().resolve(),
                                    allow_placeholders=args.allow_placeholders)
    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print(f"Mission structure OK: {args.mission}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
