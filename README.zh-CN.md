# agent-plugins

[![skills.sh](https://skills.sh/b/KuaaMU/agent-plugins)](https://skills.sh/KuaaMU/agent-plugins)

[KuaaMU](https://github.com/KuaaMU) 的跨 agent skills。纯 [`SKILL.md`](https://agentskills.io)
目录——Claude Code、Codex、opencode、Cursor 以及任何能读 `SKILL.md` 的工具都能用。

[English](README.md)

## 安装

```bash
# 全部安装
npx skills add KuaaMU/agent-plugins

# 只装一个
npx skills add KuaaMU/agent-plugins --skill mentor
```

CLI 会写到 `~/.agents/skills/`，并链接或复制到它找到的各 agent 目录。
`--agent codex` 限定 agent，`--global` 跳过项目级作用域，`-y` 跳过确认。
其余选项见 `npx skills add --help`。

## 我该用哪个 skill？

| 如果你… | 拿这个 |
|---|---|
| 不知道该用哪个 — 让 router 帮你选 | **router**（user-invoked） |
| 准备宣布"做完了/修好了/变快了" — 先验证 | **verify-first**（model-invoked） |
| 想在交付的同时真正搞懂项目，让 AI 带你成长 | **mentor**（user-invoked） |
| 在啃硬性数值目标（通过率/时延），干了几周还在"有进展"但不收敛 | **long-horizon-skills** |
| 在跑长期工程/研究任务，需要防漂移的检查点 | **adaptive-mission** |
| 想把做完的工作沉淀成经验、简报或可发布的产出 | **work-output** |
| 想建一个任何 AI 都能接手的私人知识库 | **personal-os** |

## Skills

| Skill | 说明 |
|---|---|
| [router](skills/router) | **User-invoked** 选型路由器：不知道用哪个 skill 时显式调用，它帮你选（或直说都不合适）。同时记录全仓触发策略。 |
| [verify-first](skills/verify-first) | **Model-invoked** 验证纪律微 skill：宣布任何结论前强制走 5 步闭环（定义证据→真实环境→原始输出→判别力检查→找反例），附借口预驳表。 |
| [mentor](skills/mentor) | **User-invoked** 认知对齐 skill：伴读跨会话读取主线 agent 的工作，带你真正搞懂项目——诊断先行、渐进式引导、四个问题、三种模式、费曼检验。从不干扰主线。核心理念：认知对齐 + 让 AI 带你成长。 |
| [adaptive-mission](skills/adaptive-mission) | 最小计划、抗漂移的长期工程/研究任务流：3–5 个检查点、STATE/TRUTH/PLAN/REVIEW 记录、按需子 agent、真实环境验收。 |
| [long-horizon-skills](skills/long-horizon-skills) | 硬性数值目标的多周攻坚：防失效 + 执行系统——六类失效模式、触发式规则、独立审计者、JSON 状态机、赛马纪律、文件财政、困难集、领域 profile。 |
| [work-output](skills/work-output) | 把任务沉淀成四轨产出：交付物、可复现的过程轨迹、可复用的经验、可发布的产出。 |
| [personal-os](skills/personal-os) | 跨 AI 个人数据仓库方法论：私人 GitHub 仓 + AGENTS.md 入口 + markdown 记忆，任何 AI 都能接手。 |

每个 skill 自包含；只装你需要的。

## 添加新 skill

无需配置：在 `skills/` 下放一个带 `SKILL.md` 的目录，并在上面两张表里加一行。
`name` 必须和目录名一致，否则安装器会跳过。`SKILL.md` 用英文写；在 description
里声明 user-invoked 还是 model-invoked。

## 质量门（eval & pruning）

- **准入**：新 skill 必须满足——`name` 与目录名一致、description 写清触发条件并声明
  user-invoked / model-invoked、正文 ≤100 行或采用索引结构（重型内容下沉 `references/`）。
- **Eval**：改版前后用同一个真实任务盲测一遍，看 agent 行为是否真的变好；
  只改文字、没改行为的版本不合并。
- **Pruning**：每季度 review 一次——长期无实际调用的、与其他 skill 重叠的，
  退役或合并；退役记录进 `ARCHIVED.md`（首次退役时建）。

## 备注

- `long-horizon-skills` 自带七个可运行脚本（纯标准库 Python + 一个 bash），
  每个都自测（`--self-test`）；合并前先跑一遍。
- `long-horizon-skills` v2（2026-10-10）合并了原独立仓
  `ascend-operator-tackling`（已归档），Ascend/CANN 专属内容保留在
  `references/profiles/ascend-cann.md`。
