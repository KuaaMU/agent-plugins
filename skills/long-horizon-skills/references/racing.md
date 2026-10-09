# §12 赛马纪律（L2 权威正文）

> 多 agent 的价值来自独立视角、并行验证、职责隔离，
> 不来自同时改同一个文件。先定所有权，再谈并行。

## 核心三角色

- **Orchestrator**：维护目标、验收 contract、checkpoint、优先级；
  分配 worktree / 稀缺资源 / 任务边界；裁决候选；汇总证据；
  不替 Driver 写实现。
- **Driver**：独占一个 worktree 和一个 checkpoint；做单变量实验，
  产出原始证据与回退点；不碰他人文件；合并请求交 Orchestrator。
- **Reviewer**：只读交付物、出口标准、原始证据；不接受 Driver 口头结论；
  独立复现至少一条关键证据；输出明确 verdict。
  （与 §8 独立审计者配合：Reviewer 审单轮交付，审计者审全程证据链。）

可选角色（按需）：Specialist（只做研究不改代码）、Guard（高风险操作前审查）、
Integrator（只合已过 gate 的候选、维护交付分支）。

## 赛马纪律

WHEN 存在 ≥2 个可行技术路线 THEN 必须赛马，不许单路线恋战。

1. **低成本并行**：git worktree 在同一台机器零成本开多工作区；
   稀缺硬件（NPU/真机/付费 API）只用于决赛圈，初赛用本地/模拟/小样本。
2. **统一记分牌**：所有候选登记在 CANDIDATES.md，字段一致
   （假设/单变量/基线/结果/裁决/回退点）；用 `new_candidate.py` 登记。
3. **定期处决**：每 N 轮（建议 5）Orchestrator 强制看一次记分牌，
   kill 明显落后候选；被 kill 的写清失败家族与重开条件，允许未来复活。
4. **决赛圈**：只把 top-2 候选送上稀缺资源做目标口径验证。

WHEN 连续两轮处决点无候选被 kill 且整体无进展 THEN 说明赛马流于形式，
Orchestrator 必须引入一个外部新路线（换算法家族，而非换参数）。

## 稀缺资源租约

WHEN 资源稀缺（专用硬件、限时容器、付费配额）或共享 THEN 建租约：

```text
owner: / resource: / start-end: / purpose: / worktree: /
expected load: / cleanup: / 释放条件:
```

无租约不启动可能影响他人测量或占用资源的任务；测量前检查空闲、
残留进程、热状态与并发。

## 消息协议

Agent 间只交换结构化记录，不传"我觉得好了"：
task / owner / base authority / worktree+hash / goal /
allowed+forbidden paths / commands / evidence / result /
regressions / open risks / decision request / stop condition。
关键决策同步到文件，不依赖对话历史。

## 合并条件

候选交给集成的条件：有独立候选记录与回退点；gate 结论来自原始证据；
无未解释的已通过区间回归；diff 只含目标变更；实验开关已移除；
版本/hash/命令/数据完整；Reviewer 已独立验证。
