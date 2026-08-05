# agent-plugins

Claude Code plugin marketplace by [KuaaMU](https://github.com/KuaaMU). A single
place to discover and install plugins that extend your coding agent.

## Install the marketplace

```bash
claude plugin marketplace add KuaaMU/agent-plugins
```

## Available plugins

| Plugin | What it does | Install |
|---|---|---|
| [mcp-vision-bridge](https://github.com/KuaaMU/mcp-vision-bridge) | Give your text-only agent (DeepSeek V4 Flash, Qwen, Kimi) vision: an `analyze_image` MCP tool, a `vision` skill, and an auto-loop clipboard hook. Routes images through any multimodal model you choose. | `claude plugin install mcp-vision-bridge` |

## Adding a new plugin

Each plugin lives in its own repository (best practice — one plugin per repo,
self-referencing `source: "./"`). To add it here, append an entry to
[`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) using
`git-subdir` (or `url`) pointing at the plugin repo:

```json
{
  "name": "your-plugin",
  "description": "One-line description.",
  "source": {
    "source": "git-subdir",
    "url": "https://github.com/you/your-plugin.git",
    "path": ".",
    "ref": "main",
    "sha": "<commit sha>"
  },
  "category": "development"
}
```

Then bump `version`, validate, and push:

```bash
claude plugin validate .
git push
```

## Notes

- The marketplace name `agent-plugins` signals that these extensions are
  agent-oriented (skills are broadly compatible across Claude Code / Codex /
  opencode; plugin and MCP mechanisms are per-platform).
- For the source plugin repos, see each plugin's own README for usage.
