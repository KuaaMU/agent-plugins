# Agent 阅读顺序

1. `TASK_ANCHOR.md` —— 验收契约是什么、起始站位、框架假设是什么
2. `state.json` —— 当前机器状态（只读这一个对象，不重建历史）
3. `CLAIMS.jsonl` —— 哪些结论是"已实测"，哪些只是"未受攻击"
4. `CANDIDATES.md` —— 赛马记分牌：谁在跑、谁被 kill 了、为什么
5. `EVENTS.md` 最近 5 条 —— 刚发生了什么
6. `HARDSET.md` —— 困难集（别在日常轮里碰）

纪律：
- 验证而不是相信：动手前先验证 state.json 的 frame / hash / 环境是否还成立
- 单 writer：只改属于你的文件；权威文件由 owner 汇总
- 每轮结束：状态补丁（state_patch.py）+ 台账条目 + EVENTS 日志，三件缺一不可
