---
name: work-output
description: >-
  把任务过程沉淀成四轨工作产出：任务轨交付物与证据、过程轨可复现命令与失败记录、复用轨 skill/模板/经验、公开轨案例/文章/训练语料。用于任何工程、研究或创作任务收尾时生成分层简报（一句话/五行/证据附录）、维护 OUTPUTS.md 与 LEARN.md、按发布闸门脱敏并许可后开源沉淀，并把任务轨迹转成适合下一代模型训练的结构化 episode。当用户希望工作产出反补自己、帮助理解任务、对外展示价值或作为训练语料时使用。
---

# Work Output

## 核心立场

- 产出是副产物，不是额外劳动：优先蒸馏本来就会产生的东西（命令、日志、diff、决策、失败），不为“看起来有产出”制造文件。
- 产出跟着问题走：每条产出回答一个问题，并带 as-of 时间、当时假设、证据。世界会变，产出记录的是“当时为什么这么做”。
- 四轨分层：任务轨（交付）、过程轨（可复现）、复用轨（自反馈）、公开轨（世界价值）。先保证前两轨，再谈后两轨。
- 分层可读：一句话结论 → 五行摘要 → 证据附录。用户负责项目只看五行，深挖再看附录。
- 发布有闸门：公开前过脱敏、许可、可复现、无夸大四项检查。

## 启动

1. 创建 OUTPUTS.md：四轨分区 + 发布待办 + 下一轮问题。
2. 有可复用经验时创建 LEARN.md；没有就先空着。
3. 把任务目标、验收标准和关键链接写进 OUTPUTS.md 头部（引用 TRUTH.md 而非复制）。

## 每个检查点/每轮收尾（5 分钟蒸馏）

写三条：

- 新事实：更新 TRUTH.md（来源 + 版本 + 核对时间）。
- 新经验：写进 LEARN.md，格式“下次遇到 X 先试 Y，因为证据是 Z”。
- 公开候选：写进 OUTPUTS.md 公开轨，标状态：草稿/可发布/不发。

不要等任务结束才写；证据和教训过期最快。

## 分层简报

每次交付或用户要求了解进度时，输出三层：

1. 一句话结论。
2. 五行摘要：问题、决策、证据、风险、下一步。
3. 证据附录：可复现命令、输出、文件路径、失败记录。

模板见 references/layered-brief.md。

## 四轨产出

- 任务轨：交付物 + 出口证据，属于用户验收。
- 过程轨：可复现命令、环境、失败与 BLOCKED、回滚路径，反补自己。
- 复用轨：LEARN 条目、skill、模板、提示词、checklist，攒够就固化。
- 公开轨：案例、文章、开源仓库、结构化 episode；必须过发布闸门。

细节与清单见 references/four-tracks.md。

## 结构化 episode（训练语料候选）

任务收尾时，把轨迹整理成 episode：goal → context（TRUTH 事实）→ actions（命令/决策轨迹）→ evidence → reflection（结果标签 + 教训）。

只整理高质量、已脱敏、有许可证的 episode；原始聊天记录不直接作为语料。

格式与示例见 references/episode-format.md。

## 发布闸门

公开任何产出前逐项确认：

- 脱敏：无密钥、Token、IP、串口、路径泄露、个人信息。
- 许可：明确 MIT/CC-BY 等，声明是否允许训练。
- 可复现：命令与数据可重复，结果不夸大。
- 价值：一篇案例胜于十篇流水账；每项目最多一篇主案例 + 一个可复用资产。

检查表见 references/publication-gate.md。

## 参考文件

- references/four-tracks.md：四轨模型与各轨清单。
- references/layered-brief.md：三层简报模板与示例。
- references/distillation-rules.md：检查点蒸馏规则与 LEARN 写法。
- references/episode-format.md：结构化 episode schema 与示例。
- references/publication-gate.md：发布前检查表与许可说明。

## 与 adaptive-mission 的关系

本 skill 不依赖具体任务流程。配合 adaptive-mission 使用时，STATE/TRUTH/PLAN/REVIEW 提供事实与证据，本 skill 负责把它们沉淀成四轨产出；独立使用时在任意任务收尾调用本 skill 即可。
