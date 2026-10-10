# agent-plugins

[![skills.sh](https://skills.sh/b/KuaaMU/agent-plugins)](https://skills.sh/KuaaMU/agent-plugins)

Cross-agent skills and plugins by [KuaaMU](https://github.com/KuaaMU).

Skills here are plain [`SKILL.md`](https://agentskills.io) directories — they work
in Claude Code, Codex, opencode, Cursor, and anything else that reads
`SKILL.md`. Plugins are Claude Code specific.

## Install

```bash
# everything
npx skills add KuaaMU/agent-plugins

# just one
npx skills add KuaaMU/agent-plugins --skill long-horizon-skills
```

The CLI writes to `~/.agents/skills/` and links or copies into whichever agent
directories it finds. `--agent codex` narrows it, `--global` skips the project
scope, `-y` skips the prompt. Run `npx skills add --help` for the rest.

### Claude Code plugins

```bash
claude plugin marketplace add KuaaMU/agent-plugins
claude plugin install mcp-vision-bridge
```

## Which skill do I need?

| If you are… | Take |
|---|---|
| Not sure which skill fits — let the router decide | **router** (user-invoked) |
| About to claim "done / fixed / faster" — verify first | **verify-first** (model-invoked) |
| Want to actually understand the project while shipping, let AI mentor you | **shadow-mentor** (user-invoked) |
| Tackling a hard numeric target over days/weeks (pass rate, latency) and keep "making progress" without converging | **long-horizon-skills** |
| Running a long engineering or research mission and need drift-proof checkpoints | **adaptive-mission** |
| Turning finished work into lessons, briefs, or publishable artifacts | **work-output** |
| Building a private, cross-AI personal knowledge vault | **personal-os** |

## Skills

| Skill | What it does |
|---|---|
| [router](skills/router) | **User-invoked** skill router: when you don't know which skill fits, invoke it and it routes you (or tells you none fits). Also documents the repo-wide trigger policy. |
| [verify-first](skills/verify-first) | **Model-invoked** verification discipline micro-skill: 5-step loop (define evidence → real environment → raw output → discriminability check → seek counterexamples) before claiming anything works, plus a rationalization pre-buttal table. |
| [shadow-mentor](skills/shadow-mentor) | **User-invoked** cognitive-alignment skill: while the main coding agent ships, a shadow agent (read-only worktree) mentors you — 4 questions (big picture / why-it-exists / alternatives / frontier), 3 modes (checkpoint briefings / ask-anytime / Feynman checks). Core ideas: 认知对齐 + 让 AI 带你成长. |
| [adaptive-mission](skills/adaptive-mission) | Minimal-plan, drift-tolerant workflow for long engineering and research missions: 3–5 checkpoints, STATE/TRUTH/PLAN/REVIEW records, optional subagents, real-environment acceptance. |
| [long-horizon-skills](skills/long-horizon-skills) | Anti-failure + execution system for hard numeric targets over weeks: six failure modes (framework lock-in, self-confirmation bias, goal drift, dead apparatus, gate-semantics drift, evidence mismatch), trigger-style rules, independent auditor, JSON state machine, racing discipline, file hygiene, hard-set, and domain profiles. |
| [work-output](skills/work-output) | Distill any task into four-track outputs: deliverables, reproducible process traces, reusable lessons, and publishable artifacts. |
| [personal-os](skills/personal-os) | Cross-AI personal data vault methodology: private GitHub repo + AGENTS.md entry point + markdown memory any AI can onboard to. Session-start protocol, hard session-end sync discipline, curation bar, security red lines. |

Each is self-contained; install only the ones you want.

## Plugins

Claude Code only.

| Plugin | What it does |
|---|---|
| [mcp-vision-bridge](https://github.com/KuaaMU/mcp-vision-bridge) | Give your text-only agent vision: an `analyze_image` MCP tool, a `vision` skill, and an auto-loop clipboard hook. Routes images through any multimodal model you choose. |

## Adding a skill

No config needed: drop a directory with a `SKILL.md` under `skills/` and add a
row to the table above. The workspace globs the directory. Keep `name` in the
frontmatter identical to the directory name, or installers will skip it.

## Adding a plugin

One plugin per repo, self-referencing `source: "./"`. Append an entry to
[`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json):

```json
{
  "name": "your-plugin",
  "description": "One-line description.",
  "source": {
    "source": "url",
    "url": "https://github.com/you/your-plugin.git",
    "sha": "<commit sha>"
  },
  "category": "development"
}
```

Then validate and push:

```bash
claude plugin validate .
git push
```

Pin `sha` to a commit that exists — `claude plugin install` fails outright on a
bad one. Bump it when you want a new version out.

## 质量门（eval & pruning）

- **准入**：新 skill 必须满足——`name` 与目录名一致、description 写清触发条件并声明
  user-invoked / model-invoked、正文 ≤100 行或采用索引结构（重型内容下沉 `references/`）。
- **Eval**：改版前后用同一个真实任务盲测一遍，看 agent 行为是否真的变好；
  只改文字、没改行为的版本不合并。
- **Pruning**：每季度 review 一次——长期无实际调用的、与其他 skill 重叠的，
  退役或合并；退役记录进 `ARCHIVED.md`（首次退役时建）。

## Notes

- `long-horizon-skills` ships seven runnable scripts (stdlib-only Python + one
  bash). Every script self-tests (`--self-test`); run them before merge.
- `long-horizon-skills` v2 (2026-10-10) merged the former standalone
  `ascend-operator-tackling` repo (now archived). Ascend/CANN specifics live on
  as `references/profiles/ascend-cann.md`.
