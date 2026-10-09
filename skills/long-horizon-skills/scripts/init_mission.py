#!/usr/bin/env python3
"""Initialize a long-horizon tackling mission from reusable templates.

Merged skill: machine track (state.json, CLAIMS.jsonl) + human track
(TASK_ANCHOR, CANDIDATES, PLAN, STATE, REVIEW, METRICS, HANDOFF, HARDSET,
LESSONS, EVENTS, INDEX, AGENT). Optional domain profile (--profile).
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def fill(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


TEMPLATES: dict[str, str] = {
    "TASK_ANCHOR.md": """# TASK_ANCHOR — {{GOAL}}

> §1 任务锚定。逐字抄验收条件；继承的框架是假设（§1.1）。

## 1. 目标原文（逐字）

{{ACCEPTANCE}}

## 2. 验收判据

- 判定式/阈值：
- 谁有权改：我没有。改判据 = 升级给用户（§9.2）。

## 3. 起始点

- commit：
- 产物 hash：
- 失败集合（逐例列名）：

## 4. 当前框架（假设还是已验证？证伪实验是什么？）

## 5. 未验证假设（每条绑定证伪实验 + 排期，§1.4）
""",
    "STATE.md": """# STATE — 当前快照（人读视图；机器读 state.json）

> §10 状态机制。同一事实只允许一处权威（§2.5.3）。

- 目标：{{GOAL}}
- 当前轮次：
- 当前框架 / 状态：
- 失败集合摘要：
- 缺口 / 趋势：
- 阻塞：
""",
    "CANDIDATES.md": """# Candidates — 候选台账

| ID | Status | Owner | Baseline | Hypothesis | Single Variable | Prediction | Kill Criterion | Evidence | Decision | Reopen Condition |
|---|---|---|---|---|---|---|---|---|---|---|
""",
    "PLAN.md": """# PLAN — 检查点（3–5 个）

每个检查点：目的 / 最小实验 / 通过条件 / kill 线 / 证据路径。
赛马处决周期 N=5（§12.2，可覆盖）。
""",
    "REVIEW.md": """# REVIEW — 独立评审结论（§8）

> 主攻手不得自审。评审者只读原始数据，不读总结；必须报告自己撤回了什么。
""",
    "METRICS.md": """# METRICS — 记分牌

跟踪 3–5 个指标看趋势（通过数/缺口/候选存活数/证据返工），不为填表而填表。
""",
    "HANDOFF.md": """# HANDOFF — 最短恢复路径

- 权威 hash（源码/构建/测试）：
- 下一条可执行命令：
- 必须避开的失败家族：
- 新 agent 第一纪律：验证而不是相信（复算 hash，重跑最小 smoke）。
""",
    "HARDSET.md": """# HARDSET — 困难集（§14）

准入：≥2 种结构路线试过仍不过、常规优化只有个位数改善、失效机制与众不同。
不参与日常评分；爆破只允许结构级实验。
""",
    "LESSONS.md": """# LESSONS — 提炼的失败模式

只记可复用的模式，不抄聊天记录。实例去 references/failure-catalog.md。
""",
    "EVENTS.md": """# EVENTS — 增量日志

每轮追加：轮次 / 做了什么 / 状态补丁摘要 / 台账条目 id。
""",
    "INDEX.md": """# INDEX — 任务目录导航

- TASK_ANCHOR.md — 锚定（§1）
- state.json — 机器真相源，每轮必读（§10）
- CLAIMS.jsonl — 证据台账（§2）
- CANDIDATES.md / PLAN.md / STATE.md / REVIEW.md / METRICS.md
- HANDOFF.md / HARDSET.md / LESSONS.md / EVENTS.md
- evidence/ — 原始证据；scratch/ — 实验产物；research/ — 外部资料；hard-set/ — 困难集工作区
""",
    "AGENT.md": """# AGENT — 任务内阅读顺序

1. 本 skill SKILL.md §0（三层路径按需）
2. TASK_ANCHOR.md（§1）→ state.json（§10，每轮）
3. 撞门禁/评审时读 references/ 对应章节（编号主键 §N.M）
""",
}

STATE_JSON_TEMPLATE = {
    "schema_version": 1,
    "task": "{{GOAL}}",
    "acceptance": "{{ACCEPTANCE}}",
    "round": 0,
    "frame": {"name": "", "status": "假设", "falsifier": "", "next_if_falsified": ""},
    "failure_set": [],
    "gap_now_pct": None,
    "gap_history": [],
    "budget_rounds": None,
    "excluded_paths": [],
    "claims_ref": "CLAIMS.jsonl",
    "candidates_summary": "",
    "hard_set_ref": "HARDSET.md",
}

HYGIENE_DIRS = ("evidence", "worklog", "reports", "archive", "scratch", "research", "hard-set")


def build_mission(mission: Path, values: dict[str, str], profile: str = "") -> None:
    mission.mkdir(parents=True, exist_ok=True)
    for directory in HYGIENE_DIRS:
        (mission / directory).mkdir(parents=True, exist_ok=True)
    for name, template in TEMPLATES.items():
        path = mission / name
        if not path.exists():
            path.write_text(fill(template, values), encoding="utf-8")
    state_path = mission / "state.json"
    if not state_path.exists():
        state_path.write_text(
            json.dumps(
                {k: (fill(v, values) if isinstance(v, str) else v) for k, v in STATE_JSON_TEMPLATE.items()},
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
    claims_path = mission / "CLAIMS.jsonl"
    if not claims_path.exists():
        claims_path.write_text("", encoding="utf-8")
    if profile:
        (mission / "PROFILE.md").write_text(
            f"# Profile\n\nDomain profile: `{profile}` — "
            f"see skill `references/profiles/{profile}.md`.\n",
            encoding="utf-8",
        )


def self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        mission = Path(tmp) / "m"
        build_mission(mission, {"GOAL": "t", "ACCEPTANCE": "a"}, profile="ascend-cann")
        expected = {*TEMPLATES, "state.json", "CLAIMS.jsonl", "PROFILE.md"}
        missing = [n for n in expected if not (mission / n).exists()]
        assert not missing, f"missing: {missing}"
        assert json.loads((mission / "state.json").read_text(encoding="utf-8"))["round"] == 0
        for d in HYGIENE_DIRS:
            assert (mission / d).is_dir(), d
    print("init_mission --self-test: OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mission", default="", help="Mission directory to initialize")
    parser.add_argument("--goal", default="", help="Final objective")
    parser.add_argument("--acceptance", default="", help="Acceptance criteria summary")
    parser.add_argument("--operator", default="unknown", help="Workload name")
    parser.add_argument("--repo", default="unknown", help="Repository or workspace")
    parser.add_argument("--task-doc", default="unknown", help="Task document path or URL")
    parser.add_argument("--profile", default="", help="Domain profile, e.g. ascend-cann")
    parser.add_argument("--force", action="store_true", help="Overwrite known template files")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self test")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if not args.mission:
        parser.error("--mission is required (or use --self-test)")

    skill_root = Path(__file__).resolve().parent.parent
    if args.profile and not (skill_root / "references" / "profiles" / f"{args.profile}.md").is_file():
        parser.error(f"profile not found: references/profiles/{args.profile}.md")

    mission = Path(args.mission).expanduser().resolve()
    if mission.exists() and any(
        p.name not in {*HYGIENE_DIRS, ".git"} for p in mission.iterdir()
    ) and not args.force:
        parser.error(f"mission directory is not empty: {mission}; use --force")

    values = {
        "GOAL": args.goal or "(fill in)",
        "ACCEPTANCE": args.acceptance or "(fill in)",
        "OPERATOR": args.operator,
        "REPO": args.repo,
        "TASK_DOC": args.task_doc,
        "DATE": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }
    if args.force:
        shutil.rmtree(mission, ignore_errors=True)
    build_mission(mission, values, profile=args.profile)
    print(f"Mission initialized: {mission}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
