# 状态文件总览：JSON 是血，Markdown 是肉（§10）

> 合并裁决：v2 的 markdown 状态文件体系与 LHS 的 JSON 状态机**不重复**——
> 前者是"人读的视图与台账"，后者是"机器每轮读的真相源"。
> 同一事实只允许一处权威（§2.5.3），下表是唯一的映射关系。

## 双轨契约

| 机器轨（`state.json`） | 人读轨（Markdown） | 关系 |
|---|---|---|
| `task` / `round` / `frame` | `TASK_ANCHOR.md`、`STATE.md` | anchor 与快照是 frame 的**渲染视图**，不另存真相 |
| `failure_set[]` | `STATE.md` 失败集合摘要 | 逐例明细只在 JSON；Markdown 只写摘要+指向 |
| `gap_now_pct` / `gap_history` | `METRICS.md` | 趋势图在 Markdown，数在 JSON |
| `excluded_paths[]` | `LESSONS.md`（模式） | JSON 记条目+证据；LESSONS 只记提炼出的**模式** |
| `claims_ref` → `CLAIMS.jsonl` | （无散文 TRUTH） | v2 的 `TRUTH.md` 已被 `CLAIMS.jsonl` 取代，不再设此文件 |
| `candidates_summary` | `CANDIDATES.md` | 候选明细的权威是 Markdown 台账；JSON 只放摘要 |
| `hard_set_ref` → `HARDSET.md` | `HARDSET.md` | 困难集独立管理（§14），不进日常评分 |
| — | `PLAN.md` | 检查点（目的/实验/通过条件/kill 线），orchestrator 维护 |
| — | `REVIEW.md` | 独立评审结论（§8），reviewer 写 |
| — | `HANDOFF.md` | 最短恢复路径；新 agent 第一纪律：验证而不是相信 |
| — | `EVENTS.md` | 增量日志（只追加），回答"我是怎么走到这里的" |
| — | `INDEX.md`、`AGENT.md` | 导航与任务内阅读顺序 |

## 单 writer 规则

同一时间只允许一个 writer 改权威文件；sub-agent 写自己的
`worklog/` 与证据，由 owner 汇总进权威文件。

## 目录（文件财政纪律 §13）

`evidence/`（原始证据）· `worklog/`（过程）· `reports/`（报告）·
`archive/`（归档）· `scratch/<候选id>/`（实验产物，候选关闭即清）·
`research/`（外部资料，配额 20）· `hard-set/`（困难集工作区）。
`mission_lint.py` 对 orphan-scratch / research 超量 / 根目录游荡 md 做检查。
