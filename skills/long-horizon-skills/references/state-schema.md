# state.json schema 与补丁语义

> `state.md` 的配套：机器可读的 schema、补丁写法、校验门。

---

## 2. schema

```json
{
  "schema_version": 1,
  "task": "<一句话：这次攻坚要达成什么>",
  "round": 0,

  "frame": {
    "name": "<当前框架：用哪条路径 / 哪套家族>",
    "status": "假设 | 已验证 | BLOCKED",
    "falsifier": "<证伪它的具体实验：跑什么、看什么判据>",
    "next_if_falsified": "<它被证伪之后走哪条路>"
  },

  "failure_set": [ { "case": "<用例名>", "gap_pct": -15.2 } ],

  "gap_now_pct": -15.2,
  "gap_history": [ { "round": 3, "gap_pct": -12.4 } ],
  "budget_rounds": 10,

  "excluded_paths": [
    { "path": "Cube 路径", "marker": "refuted",
      "reason": "+28% 上限，量级不够", "evidence": "control/BLOCKED.md" }
  ],

  "claims_ref": "mission/CLAIMS.jsonl"
}
```

**两条硬纪律：**

1. **`_pct` 后缀是单位，不是装饰。** 缺口一律**百分数**：`-15.2` 表示"还差 15.2%"。
   字段名里不带单位时，这套东西出过一次真实的 100× 错误（`-0.152` 被当成 `-0.152%`，
   于是"不可达"被判成"可达"）。**单位写进名字，就丢不掉了**（硬规则 `2.1`）。
2. **`gap_history` 与 `round` 由工具维护，补丁里不许出现。**
   工具在每次合并后自动把 `gap_now_pct` 追加成一行趋势。
   让调用方自己发整段历史，就是把它退回"每轮重发全部状态"——那正是这套东西要消灭的。

`marker` 取值：`refuted` / `superseded` / `invalidated` / `INVALID` / `已闭合`。

**`budget_rounds` 可以缺席。** 「我还没设预算」是一个**真实状态**，
逼它填一个数字会造出一个假数字，而假数字会被当真算进 4.6。
缺席时 4.6 会**明说「预算未设定」**，而不是给出一个可达/不可达的结论——
**让缺的东西可见，比让缺的东西变成一个默认值好。**

---

## 3. 补丁：稀疏 + `null` 删除

一份补丁**只写变了的字段**：

```json
{ "gap_now_pct": -12.4,
  "excluded_paths": [ { "path": "非 2 的幂车道切分", "marker": "refuted",
                        "reason": "预测 −21%，实测 −0.1%", "evidence": "evidence/.../REFUTED.md" } ] }
```

```bash
python3 scripts/state_patch.py --state state.json --log EVENTS.md --patch p.json
```

- **没提到的字段不动。**
- **`null` 表示删除该键**：`{ "gap_now_pct": null }` 会把这一项**删掉**，而不是置空。
  这是"过时的前提要被显式删除"的落点——让下一个读状态的人**根本看不到它**，
  而不是每轮都要重新判断"这条还算不算数"。
- 数组（`failure_set` / `excluded_paths`）**整体替换**，不是逐项合并。
  理由：这两者的正确语义是"此刻的实际情况"，逐项合并会产生既不是旧值也不是新值的东西。

---

## 4. 校验门

**补丁先过校验，通过了才合并。没通过 ⇒ 状态逐字节不动**，但"被拒绝"这件事进日志。

它会拦下这些（每一条都对应一条已有规则）：

| 拦截 | 对应规则 |
|---|---|
| `frame.falsifier` / `next_if_falsified` 为空 | `1.2` 强化 —— 写不出就不是假设 |
| `frame.status` 不在 `假设/已验证/BLOCKED` | 状态枚举固定，防止自由发挥 |
| `excluded_paths[]` 缺失效标记 | `null` 语义 —— 没有标记的条目还在暗中生效 |
| `excluded_paths[].evidence` 为空 | 与 `claims_lint` ⑤ 同源：**既无证据又无推导来源的断言不许进状态** |
| `failure_set[].gap_pct` 不是数字 | `4.6` 的输入必须是可算的量 |
| `gap_history[].round` 未严格递增 | 趋势要求按轮次单调，否则趋势没有意义 |
| **未声明的顶层键** | schema 固定。**想加字段先回答"它让哪条规则开火"** |
| 补丁里出现 `round` / `gap_history` | 由工具维护。**显式拒绝，不是静默忽略**——静默忽略会让"我提交了它"与"我没提交"输出同值（E7 的形态） |

> **拒绝不是失败。** 一次被拒绝的补丁把"我打算这么改但没通过"记在日志里，
> 而状态保持干净。**这比让一个半对的补丁悄悄生效要好得多。**

---
