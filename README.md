# agent-plugins

[![skills.sh](https://skills.sh/b/KuaaMU/agent-plugins)](https://skills.sh/KuaaMU/agent-plugins)

Cross-agent skills by [KuaaMU](https://github.com/KuaaMU). Plain [`SKILL.md`](https://agentskills.io)
directories — works in Claude Code, Codex, opencode, Cursor, and anything else that reads `SKILL.md`.

[中文版](README.zh-CN.md)

## Install

```bash
# everything
npx skills add KuaaMU/agent-plugins

# just one
npx skills add KuaaMU/agent-plugins --skill mentor
```

The CLI writes to `~/.agents/skills/` and links or copies into whichever agent
directories it finds. `--agent codex` narrows it, `--global` skips the project
scope, `-y` skips the prompt. Run `npx skills add --help` for the rest.

## Which skill do I need?

| If you are… | Take |
|---|---|
| Not sure which skill fits — let the router decide | **router** (user-invoked) |
| About to claim "done / fixed / faster" — verify first | **verify-first** (model-invoked) |
| Want to actually understand the project while shipping, let AI mentor you | **mentor** (user-invoked) |
| Tackling a hard numeric target over days/weeks (pass rate, latency) and keep "making progress" without converging | **long-horizon-skills** |
| Running a long engineering or research mission and need drift-proof checkpoints | **adaptive-mission** |
| Turning finished work into lessons, briefs, or publishable artifacts | **work-output** |
| Building a private, cross-AI personal knowledge vault | **personal-os** |

## Skills

| Skill | What it does |
|---|---|
| [router](skills/router) | **User-invoked** skill router: when you don't know which skill fits, invoke it and it routes you (or tells you none fits). Also documents the repo-wide trigger policy. |
| [verify-first](skills/verify-first) | **Model-invoked** verification discipline micro-skill: 5-step loop (define evidence → real environment → raw output → discriminability check → seek counterexamples) before claiming anything works, plus a rationalization pre-buttal table. |
| [mentor](skills/mentor) | **User-invoked** cognitive-alignment skill: a study companion that cross-session reads the main agent's work and mentors you — diagnosis-first, progressive guidance, 4 questions, 3 modes, Feynman checks. Never interferes with the main line. Core ideas: cognitive alignment + letting AI grow you. |
| [adaptive-mission](skills/adaptive-mission) | Minimal-plan, drift-tolerant workflow for long engineering and research missions: 3–5 checkpoints, STATE/TRUTH/PLAN/REVIEW records, optional subagents, real-environment acceptance. |
| [long-horizon-skills](skills/long-horizon-skills) | Anti-failure + execution system for hard numeric targets over weeks: six failure modes, trigger-style rules, independent auditor, JSON state machine, racing discipline, file hygiene, hard-set, and domain profiles. |
| [work-output](skills/work-output) | Distill any task into four-track outputs: deliverables, reproducible process traces, reusable lessons, and publishable artifacts. |
| [personal-os](skills/personal-os) | Cross-AI personal data vault methodology: private GitHub repo + AGENTS.md entry point + markdown memory any AI can onboard to. |

Each is self-contained; install only the ones you want.

## Adding a skill

No config needed: drop a directory with a `SKILL.md` under `skills/` and add a
row to the tables above. Keep `name` in the frontmatter identical to the directory
name, or installers will skip it. Write the `SKILL.md` in English; declare
user-invoked vs model-invoked in the description.

## Quality gate (eval & pruning)

- **Admission**: a new skill must have `name` == directory name, a description stating its
  trigger + invocation mode, and a body ≤100 lines or an index structure (heavy content
  goes to `references/`).
- **Eval**: before/after a revision, blind-run the same real task and check whether agent
  behavior actually improved; text-only changes with no behavior change don't merge.
- **Pruning**: quarterly review — skills with no real usage or overlapping others get
  retired or merged; retirements are recorded in `ARCHIVED.md` (created on first use).

## Notes

- `long-horizon-skills` ships seven runnable scripts (stdlib-only Python + one
  bash). Every script self-tests (`--self-test`); run them before merge.
- `long-horizon-skills` v2 (2026-10-10) merged the former standalone
  `ascend-operator-tackling` repo (now archived). Ascend/CANN specifics live on
  as `references/profiles/ascend-cann.md`.
