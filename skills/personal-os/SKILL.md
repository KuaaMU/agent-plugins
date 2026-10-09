---
name: personal-os
description: >-
  个人数据仓库的方法论（开源）：用 GitHub 私人仓 + AGENTS.md 跨 AI 标准入口 + markdown，让任何 AI 都能无缝接手你的长期记忆、决策、项目与想法。包含新 AI 上手协议、会话结束落盘纪律、记忆策展三条杠（Verified/Reusable/Stable）、安全红线，以及 node/sh 双版本的 vault 健康检查脚本。方法论是公共品，数据永远私有。
---

# personal-os

## 理念：三层分离

- **方法论是公共品**：本 skill、AGENTS.md 约定、仓库模板，开源共享，任何人可用
- **数据是私人财产**：你的 PROFILE / MEMORY / projects / people，只活在你自己的私人仓，永不公开
- **运行不绑定语言**：核心只依赖 `git` + `markdown` 两种人人有的东西；附带脚本提供 node / shell 双版本，零第三方依赖

## 仓库模板结构

```
personal-os/              # 你的私人仓（本 skill 只定义结构，不碰你的数据）
├── AGENTS.md             # 跨 AI 标准入口（≤150 行）：阅读顺序、落盘纪律、安全红线
├── CLAUDE.md             # 桥接：Strictly follow ./AGENTS.md.
├── README.md             # 给人看的导航
├── PROFILE.md            # 关于你（带 YAML frontmatter）
├── MEMORY.md             # 长期记忆，目标 ≤100 行
├── STATE.md              # 当前状态：正在进行什么、下一步是什么
├── memory/daily/         # 每日流水 YYYY-MM-DD.md
├── decisions/            # 决策记录 ADR 式（0001-xxx.md）
├── projects/             # 一目录一项目
├── people/               # 关系网，一人一文件
├── ideas.md              # 想法收件箱
├── skills/               # 可复用 skills
├── references/           # 资料收藏
├── data/                 # 程序消费的 JSON，不手写
└── .gitignore            # 密码/密钥/明文备份永不进仓
```

## 新会话启动协议（任何 AI）

1. `git pull --rebase`（没有就先 clone）
2. 按顺序读：`AGENTS.md` → `PROFILE.md` → `MEMORY.md` → `STATE.md`
3. 按需读：`projects/`、`decisions/`、`people/`、`ideas.md`、当日 daily
4. 不要通读整个仓库，不要猜测没读到的内容

## 落盘纪律（硬规则）

- **一个任务不算完成，直到记忆已经更新**。检索只能找到写下来的东西，写是唯一的瓶颈
- 每次实质性工作后：`git pull --rebase` → 更新 `memory/daily/YYYY-MM-DD.md` → 策展 `MEMORY.md` → 重要决定记入 `decisions/` → 更新 `STATE.md` → commit → push
- commit 格式：`memory: …` / `docs: …` / `decision: …`
- 不许"等下一起写"；会话结束前先落盘

## 记忆策展规范

- 准入三条杠：**Verified**（验证过）/**Reusable**（会复用）/**Stable**（长期稳定）；有一条不满足就进 daily，不进 MEMORY.md
- 收：偏好、决定、承诺、人际关系、验证过的结论、踩过的坑；不收：流水细节、工具调用过程、未经证实的传言
- 改：精准编辑对应条目并注明日期，不留互相矛盾的旧话

## 安全红线

- 密码、API key、token、私钥**永不进仓**
- 视频、图片等大文件不进仓，只存索引
- 每次 push 前看一眼 `git status`

## 脚本（node / shell 双版本，零依赖）

- `scripts/vault-doctor.mjs` — `node scripts/vault-doctor.mjs [--dir <vault>]`
- `scripts/vault-doctor.sh` — `bash scripts/vault-doctor.sh [<vault>]`

检查：必需文件齐全、AGENTS.md ≤150 行、MEMORY.md ≤100 行、关键文件有 frontmatter、.gitignore 覆盖 secret、约定目录存在。FAIL 退出码 1。
