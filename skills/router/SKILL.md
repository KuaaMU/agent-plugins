---
name: router
description: >-
  User-invoked skill 路由器：不知道该用哪个 skill 时显式调用我，我帮你选。
  覆盖 long-horizon-skills（硬性数值目标的多周攻坚）、adaptive-mission
  （需求易漂移的长期任务）、work-output（任务收尾沉淀产出）、personal-os
  （跨 AI 个人知识库）。没有合适的我会直说，不硬塞。
disable-model-invocation: true
---

# Router

不知道用哪个 skill 时，显式调用我。不要为了用 skill 而用 skill——
没有合适的就直接干，这是被允许的答案。

## 决策树

1. 目标是**硬性数值指标**（通过率、时延），要干多天/多周？
   → **long-horizon-skills**
2. 任务很长，但**任务书/验收标准隔几天就可能变**，细节不能过早固化？
   → **adaptive-mission**
3. 任务快收尾了，想把过程沉淀成简报、经验、案例或公开产出？
   → **work-output**
4. 想给自己建一个任何 AI 都能接手的长期记忆/知识库？
   → **personal-os**
5. 1 和 2 都像（硬指标 + 需求漂移）？
   → 先 **adaptive-mission** 定方向、管漂移，进入攻坚阶段切 **long-horizon-skills**。
6. 都不像？
   → 不用 skill，直接干。

## 全仓触发策略（一览）

| Skill | 触发方式 | 为什么 |
|---|---|---|
| router | user-invoked | 选型是编排决策，归用户；模型自选容易选错还烧上下文 |
| work-output | user-invoked | 沉淀和发布是用户决策（发什么、何时收尾），模型不该自作主张 |
| adaptive-mission | model-invoked | 任务一长、需求可能漂移就该自动上马，等用户想起来就晚了 |
| long-horizon-skills | model-invoked | 触发条件是客观的（硬指标/≥5 实验/接手旧树），命中即加载 |
| personal-os | model-invoked | 会话启动协议，任何 AI 开工前都该先读它 |

## 反模式

- **为了用 skill 而用 skill**：router 的合法输出包括"都不用"。
- **同时加载两个流程 skill**：adaptive-mission 和 long-horizon-skills 不同时上马，
  按上面的第 5 条分阶段用。
- **把 router 当常驻**：我只在你犹豫"用哪个"时出现一次，选定就退场。
