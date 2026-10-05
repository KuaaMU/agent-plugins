# EVENTS —— 增量日志（只追加，由 state_patch.py 写入）

## init  2026-09-14T04:19:21Z

- 建立状态：`state.json`
- schema_version=1

## APPLIED  r1  2026-09-14T04:19:21Z

- frame  ← {"name": "复用为大形状定尺寸的专用内核", "status": "BLOCKED", "falsifier": "已做：该内核在此形状上实测向量管占用已近饱和，结构项逐项排除", "…
- failure_set  ← [{"case": "case-A（该形状出现频率最高）", "gap_pct": -12.5}, {"case": "case-B（同族，形状略小）", "gap_pct": -2.1}]
- gap_now_pct  ← -12.5
- budget_rounds  ← 12
- excluded_paths  ← [{"path": "切换到矩阵单元", "marker": "refuted", "reason": "实测该形状下比向量路径慢 28% 以上", "evidence": "evidence…
- claims_ref  ← "CLAIMS.jsonl"
- round  ← 1（自增）
- gap_history  ← 追加 r1: -12.50%（共 1 点，趋势由工具维护）

- **4.6 外推**：剩余轮数 × 平均缩小 = ?  **vs 当前缺口 12.50% → 待建立**（趋势需 ≥2 个点）

## APPLIED  r2  2026-09-14T04:19:21Z

- gap_now_pct  ← -12.4
- round  ← 2（自增）
- gap_history  ← 追加 r2: -12.40%（共 2 点，趋势由工具维护）

- **4.6 外推**：12 轮 × 0.100 %/轮 = 1.20%  **vs 当前缺口 12.50% → **不可达****

## APPLIED  r3  2026-09-14T04:19:22Z

- gap_now_pct  ← -11.9
- round  ← 3（自增）
- gap_history  ← 追加 r3: -11.90%（共 3 点，趋势由工具维护）

- **4.6 外推**：12 轮 × 0.300 %/轮 = 3.60%  **vs 当前缺口 12.50% → **不可达****

## APPLIED  r4  2026-09-14T04:19:22Z

- excluded_paths  ← [{"path": "切换到矩阵单元", "marker": "refuted", "reason": "实测该形状下比向量路径慢 28% 以上", "evidence": "evidence…
- round  ← 4（自增）

- **4.6 外推**：12 轮 × 0.300 %/轮 = 3.60%  **vs 当前缺口 12.50% → **不可达****

## REJECTED  r5  2026-09-14T04:19:22Z

- **状态未改动。**
- 拒绝原因：excluded_paths[1].marker 必须是 refuted / superseded / invalidated / INVALID / 已闭合 之一 —— 没有失效标记的条目 = 一个还在暗中生效的假设
- 拒绝原因：excluded_paths[1].evidence 不能为空 —— 与 claims_lint ⑤ 同源：既无证据又无推导来源的断言不许进状态
- 原补丁：`{"excluded_paths": [{"path": "切换到矩阵单元", "marker": "refuted", "reason": "实测慢 28% 以上", "evidence": "evidence/<date>_cubepath/REFUTED.md"}, {"path": "再调调参数看看", "marker": "", "reason": "感觉有戏", "evidence":…`

