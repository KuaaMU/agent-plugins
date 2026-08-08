# 结构化 episode

## 用途

episode 是把一次任务整理成带结果标签的过程监督数据，供下一代模型训练、复盘或复现使用。它不是聊天记录转储。

## Schema

```json
{
  "meta": {
    "id": "ep-2026-08-08-001",
    "date": "2026-08-08",
    "task_type": "operator-dev | hardware-debug | research | integration",
    "tools": ["codex", "claude-code"],
    "models": ["deepseek-v4-flash"],
    "license": "MIT",
    "privacy_status": "scrubbed"
  },
  "goal": "原始目标",
  "context": [
    {"fact": "一句话事实", "source": "URL/路径", "as_of": "2026-08-08"}
  ],
  "plan": [
    {"checkpoint": "检查点", "exit_evidence": "完成证据"}
  ],
  "actions": [
    {
      "step": 1,
      "action": "运行命令/做出决策",
      "tool": "shell | codex | reviewer",
      "result": "成功/失败/部分成功",
      "evidence": "关键输出摘要或文件路径",
      "decision": "为什么这么做"
    }
  ],
  "reflection": {
    "outcome": "success | partial | failed",
    "what_worked": "有效做法",
    "what_failed": "失败与原因",
    "next_problem": "留下的下一个问题"
  }
}
```

## 硬规则

- 发布前必须脱敏：无密钥、Token、IP、串口、姓名、组织内部路径。
- 明确许可证，并声明是否允许用于模型训练。
- 不包含第三方版权内容；引用只留来源链接。
- actions 必须带 result 和 decision，否则不构成过程监督数据。
- reflection 必须有 outcome 标签，不让下游猜测成败。
