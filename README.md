# agent-plugins

[![skills.sh](https://skills.sh/b/KuaaMU/agent-plugins)](https://skills.sh/KuaaMU/agent-plugins)

Cross-agent skills and plugins by [KuaaMU](https://github.com/KuaaMU).

Skills here are plain [`SKILL.md`](https://agentskills.io) directories — they work
in Claude Code, Codex, opencode, Cursor, and anything else that reads
`SKILL.md`. Plugins are Claude Code specific.

## Install

```bash
npx skills add KuaaMU/agent-plugins
```

That installs every skill. To pick one:

```bash
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

## Skills

| Skill | What it does |
|---|---|
| [adaptive-mission](skills/adaptive-mission) | Minimal-plan, drift-tolerant workflow for long engineering and research missions: 3-5 checkpoints, STATE/TRUTH/PLAN/REVIEW records, optional subagents, and real-environment acceptance. |
| [work-output](skills/work-output) | Distill any task into four-track outputs: deliverables, reproducible process traces, reusable lessons, and publishable artifacts. Generates layered briefs, OUTPUTS.md/LEARN.md, case-study drafts, and an episode backlog, with proactive publication proposals behind a user-approved gate. |
| [long-horizon-skills](skills/long-horizon-skills) | Anti-drift toolbox for hitting a hard numeric target over weeks: guards against framework lock-in, self-confirmation bias, goal drift, dead apparatus, gate-semantics drift, and evidence-strength mismatch. Ships the §1–§10 protocol, shape→execution-family derivation, upstream reconnaissance, structured state with sparse patches, a JSONL claims-ledger linter, and an independent auditor agent. |
| [personal-os](skills/personal-os) | Cross-AI personal data vault methodology: private GitHub repo + AGENTS.md entry point + markdown memory any AI can onboard to. Session-start protocol, hard session-end sync discipline, curation bar (Verified/Reusable/Stable), security red lines, and zero-dependency vault-doctor scripts in Node and shell. Methodology is open source; your data stays private. |

Each is self-contained; install only the ones you want.

### External skills

Maintained in their own repositories, so they version independently. This repo
only indexes them.

| Skill | Source |
|---|---|
| [ascend-operator-tackling](https://github.com/KuaaMU/ascend-operator-tackling) | [KuaaMU/ascend-operator-tackling](https://github.com/KuaaMU/ascend-operator-tackling) |

## Plugins

Claude Code only.

| Plugin | What it does |
|---|---|
| [mcp-vision-bridge](https://github.com/KuaaMU/mcp-vision-bridge) | Give your text-only agent (DeepSeek V4 Flash, Qwen, Kimi) vision: an `analyze_image` MCP tool, a `vision` skill, and an auto-loop clipboard hook. Routes images through any multimodal model you choose. |

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
bad one. Bump it when you want a new version of the plugin out.

## Notes

- Adding a skill needs no config: drop a directory with a `SKILL.md` under
  `skills/` and add a row to the table above. The workspace globs the
  directory.
- `long-horizon-skills` ships three runnable scripts
  (`claims_lint.py`, `state_patch.py`, `probe_liveness.sh`). The Python ones
  are stdlib-only and self-test with `--self-test`; the shell one needs bash.
