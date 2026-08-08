# episode 批量积累

## 目标

把单份 episode 从“偶发样例”变成可持续积累的数据资产。

## 每次任务

- 产出 episode 草稿（格式见 episode-format.md）。
- 在 EPISODES.md 登记一行：id、日期、任务类型、状态、训练授权、路径。
- 默认 status=draft，training_usage=not-allowed-by-default。

## 批量整理

每 N 个任务或每月做一次：

- 复查每份 episode：脱敏是否完整、actions 是否带 result/decision、reflection 是否有 outcome。
- 通过的移入 episodes/ 目录，状态改 scrubbed。
- 只有作者显式授权后，training_usage 才改为 allowed。

## 数据集发布闸门

- 每份 episode 都有授权声明，缺授权不发布。
- 做批量脱敏复查，不只相信单份检查。
- 仓库 README 写明用途、许可证、是否可训练。
- 发布后把 URL 回填 EPISODES.md 和 OUTPUTS.md。

## EPISODES.md 示例

```markdown
| id | date | task_type | status | training_usage | path |
| --- | --- | --- | --- | --- | --- |
| ep-2026-08-08-001 | 2026-08-08 | integration | draft | not-allowed-by-default | episodes/ep-2026-08-08-001.json |
```
