# 理念：三层分离

personal-os 的设计哲学可以一句话概括：**方法论是公共品，数据是私人财产，运行不绑定语言。**

## 为什么分离

早期设计把"怎么做"（skill、AGENTS.md 约定）和"是什么"（PROFILE、MEMORY、项目）放在同一个私人仓里。
问题：方法论本身是通用知识，藏在私人仓里无法分享、无法被社区检验；
而数据一旦和开源的方法论混在一起，又容易误公开。

## 三层

1. **开放标准层（公共）**：AGENTS.md 跨 AI 标准、Git、Markdown——都是不属于任何人的公共品，直接用，不重复发明。
2. **方法论层（开源）**：本 skill、上手协议、落盘纪律、策展规范、检查脚本。放在公开仓（如 `KuaaMU/agent-plugins` 的 `skills/personal-os/`），MIT 协议，任何人可拿去用。
3. **数据层（私有）**：你的 PROFILE / MEMORY / STATE / projects / people / daily。只活在你自己的私人仓，永不公开。

## 运行无关

核心只依赖 `git` + `markdown`——两种几乎每台机器、每种 AI 环境都有的东西。
附带脚本提供 node / shell 双版本、零第三方依赖：
Node 版服务 Node 系 agent harness（Claude Code、OpenClaw、skills.sh 生态），
Shell 版服务一切有终端的环境。行为一致，退出码一致。
