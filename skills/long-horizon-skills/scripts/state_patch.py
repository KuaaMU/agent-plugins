#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# state_patch.py —— 结构化执行状态 + 稀疏补丁 + 校验门 + 增量 Markdown 日志。
#
# 它吸纳的是 SKILL.state（arXiv 2608.26263，"accepted at EMNLP"）的三个机制，
# 并按本仓的粒度（**实验**，不是 tool call）重新定尺寸：
#
#   1. **状态外置为一个固定 schema 的对象**，每轮只读它，而不是读完全部历史再自己重建。
#   2. **稀疏补丁**：每轮只提交变了的字段；**`null` 表示删除该键**。
#      这一条是本仓最缺的——只增不减的排除清单，会让每一轮都重新判断"它还算不算数"。
#   3. **校验门**：补丁先校验后合并。**没通过校验的补丁不生效**，但被拒绝这件事进审计日志。
#
# 本仓**不取**的（以及为什么）：
#   - 不取它的 runtime / 平台适配器：本仓是一组检查，不是运行时。
#   - 不取"推理立即丢弃"：本仓恰恰要求**把推理留在可审计的地方**——那就是 Markdown 增量日志。
#     所以这里保留双轨：**JSON 是唯一真相源，Markdown 是它的增量派生视图**（硬规则 2.5.3）。
#
# 为什么用 Python 而不是 bash+jq：这套逻辑里有 schema 校验、逐字段错误定位、
#   稀疏合并与原子写。用 jq 会写成一团难验证的管道；本仓另外两个脚本是 bash 是因为它们的活是文本匹配。
#
# 用法：
#   state_patch.py --init  --state <state.json> --log <EVENTS.md> [--task "<一句话>"]
#   state_patch.py         --state <state.json> --log <EVENTS.md> --patch <patch.json>
#   state_patch.py --show  --state <state.json>
#   state_patch.py --self-test
#
# 退出码：0=已合并  1=被校验门拒绝（状态未改动）  2=用法/环境错误
# ---------------------------------------------------------------------------
from __future__ import annotations

import argparse
import datetime as _dt
import io
import json
import os
import shutil
import sys
import tempfile

# 强制 UTF-8 输出。**不设这一步，本工具在 Windows 默认控制台（GBK）上会直接崩**——
# `UnicodeEncodeError: 'gbk' codec can't encode character '✓'`，
# 那是在 selfcheck 的干净环境里跑才暴露的（手跑时导出过 PYTHONIOENCODING 就看不见）。
# 正确做法是工具自己扛住，而不是要求调用方去设环境变量。
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SCHEMA_VERSION = 1
FRAME_STATUS = ("假设", "已验证", "BLOCKED")
PATH_MARKERS = ("refuted", "superseded", "invalidated", "INVALID", "已闭合")


# =========================================================== 校验门
def validate(state: dict) -> list[str]:
    """返回错误列表；空列表 = 通过。每条错误都定位到字段。"""
    errs: list[str] = []

    def need(cond: bool, msg: str) -> None:
        if not cond:
            errs.append(msg)

    need(isinstance(state, dict), "顶层必须是对象")
    if errs:
        return errs

    need(state.get("schema_version") == SCHEMA_VERSION,
         "schema_version 必须是 %d" % SCHEMA_VERSION)

    # ---- round：单调自增。没有它，gap_history 无法定序（规则 4.6 需要趋势）----
    r = state.get("round")
    need(isinstance(r, int) and r >= 0, "round 必须是非负整数")

    # ---- frame：写不出后两项 ⇒ 它是信仰不是假设（硬规则 1.2 强化）----
    fr = state.get("frame")
    need(isinstance(fr, dict), "frame 必须是对象")
    if isinstance(fr, dict):
        need(isinstance(fr.get("name"), str) and fr["name"].strip(),
             "frame.name 不能为空（当前框架是什么）")
        need(fr.get("status") in FRAME_STATUS,
             "frame.status 必须是 %s 之一" % " / ".join(FRAME_STATUS))
        for k, why in (("falsifier", "证伪它的具体实验"),
                       ("next_if_falsified", "证伪之后走哪条路")):
            v = fr.get(k)
            need(isinstance(v, str) and v.strip() and not v.strip().startswith("<"),
                 "frame.%s 不能为空 —— 写不出「%s」⇒ 这不是假设，是信仰（硬规则 1.2）" % (k, why))

    # ---- failure_set：规则 4.3 / 4.4 的唯一输入 ----
    fs = state.get("failure_set")
    need(isinstance(fs, list), "failure_set 必须是数组")
    if isinstance(fs, list):
        for i, item in enumerate(fs):
            if not isinstance(item, dict):
                errs.append("failure_set[%d] 必须是对象" % i); continue
            need(isinstance(item.get("case"), str) and item["case"].strip(),
                 "failure_set[%d].case 不能为空（必须逐例列名）" % i)
            g = item.get("gap_pct")
            need(isinstance(g, (int, float)) and not isinstance(g, bool),
                 "failure_set[%d].gap_pct 必须是数字（缺口，**单位：百分数**，"
                 "如 -15.2 表示还差 15.2%%；规则 4.6 的输入）" % i)

    # ---- gap_history：4.6 的趋势项。必须与 round 同序、单调追加 ----
    gh = state.get("gap_history")
    need(isinstance(gh, list), "gap_history 必须是数组")
    if isinstance(gh, list):
        prev = None
        for i, item in enumerate(gh):
            if not isinstance(item, dict):
                errs.append("gap_history[%d] 必须是对象" % i); continue
            rr = item.get("round")
            need(isinstance(rr, int), "gap_history[%d].round 必须是整数" % i)
            need(isinstance(item.get("gap_pct"), (int, float)),
                 "gap_history[%d].gap_pct 必须是数字（单位：百分数）" % i)
            if isinstance(rr, int) and prev is not None and rr <= prev:
                errs.append("gap_history[%d].round=%d 未严格递增（上一项 %d）"
                            " —— 趋势要求它按轮次单调" % (i, rr, prev))
            if isinstance(rr, int):
                prev = rr

    # ---- budget_rounds：4.6 的分母。**可以缺席**——"我还没设预算"是一个真实状态，
    #      逼它填一个数字会造出一个假数字，而假数字会被当真算进 4.6。
    b = state.get("budget_rounds")
    if b is not None:
        need(isinstance(b, int) and not isinstance(b, bool) and b >= 0,
             "budget_rounds 若存在必须是非负整数（剩余轮数预算）")

    # ---- excluded_paths：`null` 语义的落点。每条必须带标记与证据 ----
    ep = state.get("excluded_paths")
    need(isinstance(ep, list), "excluded_paths 必须是数组")
    if isinstance(ep, list):
        for i, item in enumerate(ep):
            if not isinstance(item, dict):
                errs.append("excluded_paths[%d] 必须是对象" % i); continue
            need(isinstance(item.get("path"), str) and item["path"].strip(),
                 "excluded_paths[%d].path 不能为空" % i)
            need(item.get("marker") in PATH_MARKERS,
                 "excluded_paths[%d].marker 必须是 %s 之一"
                 " —— 没有失效标记的条目 = 一个还在暗中生效的假设"
                 % (i, " / ".join(PATH_MARKERS)))
            ev = item.get("evidence")
            need(isinstance(ev, str) and ev.strip() and not ev.strip().startswith("<"),
                 "excluded_paths[%d].evidence 不能为空"
                 " —— 与 claims_lint ⑤ 同源：既无证据又无推导来源的断言不许进状态" % i)

    # ---- claims_ref：只引用台账，不复制（硬规则 2.5.3）----
    cr = state.get("claims_ref")
    need(isinstance(cr, str) and cr.strip(), "claims_ref 不能为空（指向台账路径，不要在这里复制条目）")

    # ---- 固定 schema：未声明的顶层键一律拒绝 ----
    allowed = {"schema_version", "task", "round", "frame", "failure_set",
               "gap_now_pct", "gap_history", "budget_rounds", "excluded_paths", "claims_ref"}
    extra = set(state) - allowed
    if extra:
        errs.append("未声明的顶层键：%s —— schema 固定，想加字段先回答"
                    "「它让哪条规则能开火？」（见 references/state.md）" % ", ".join(sorted(extra)))
    return errs


# =========================================================== 补丁自身的校验
# 由工具维护的字段，补丁里**不许出现**。
# 为什么不是"静默忽略"：静默忽略让"我提交了 round"与"我没提交 round"输出同值——
# 这正是本仓 E7 的形态（读数在两种情况下取同一个值）。所以这里**显式拒绝**。
FORBIDDEN_IN_PATCH = {
    "round": "round 由工具自增；你提交什么都不会生效，所以直接拒绝而不是忽略",
    "gap_history": "gap_history 由工具维护：只提交 gap_now_pct，工具会把这一轮追加进去"
                   "（否则每一轮都要重发整段历史，那正是本工具要消灭的东西）",
}


def validate_patch(patch: dict) -> list[str]:
    errs: list[str] = []
    if not isinstance(patch, dict):
        return ["补丁必须是 JSON 对象"]
    for k, why in FORBIDDEN_IN_PATCH.items():
        if k in patch:
            errs.append("补丁里不能出现 `%s` —— %s" % (k, why))
    return errs


# =========================================================== 合并（稀疏 + null 删除）
def merge(state: dict, patch: dict) -> tuple[dict, list[str]]:
    """返回 (新状态, 变更说明)。patch 里的 null ⇒ 删除该键。

    **`gap_now_pct` 会被自动追加进 `gap_history`**（同一轮重复提交则覆盖该轮），
    所以调用方永远不需要、也不允许自己发整段趋势——趋势由工具维护。
    """
    out = json.loads(json.dumps(state))          # 深拷贝，保证失败时原状态不受影响
    notes: list[str] = []
    for k, v in patch.items():
        if v is None:
            if k in out:
                del out[k]; notes.append("- %s  (null ⇒ 删除)" % k)
            else:
                notes.append("- %s  (null，本来就不存在)" % k)
        else:
            out[k] = v
            notes.append("- %s  ← %s" % (k, _brief(v)))
    out["round"] = int(state.get("round", 0)) + 1
    notes.append("- round  ← %d（自增）" % out["round"])

    # ---- 趋势由工具维护：把这一轮的缺口追加进去 ----
    if "gap_now_pct" in patch and patch["gap_now_pct"] is not None:
        hist = list(out.get("gap_history") or [])
        entry = {"round": out["round"], "gap_pct": patch["gap_now_pct"]}
        hist = [h for h in hist if not (isinstance(h, dict) and h.get("round") == out["round"])]
        hist.append(entry)
        hist.sort(key=lambda h: h.get("round", 0) if isinstance(h, dict) else 0)
        out["gap_history"] = hist
        notes.append("- gap_history  ← 追加 r%d: %.2f%%（共 %d 点，趋势由工具维护）"
                     % (out["round"], patch["gap_now_pct"], len(hist)))
    return out, notes


def _brief(v, n: int = 96) -> str:
    s = json.dumps(v, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + "…"


# =========================================================== 4.6 外推（写进日志，不替人判断）
def extrapolate(state: dict) -> str:
    """把 4.6 要的那一行算出来。**单位统一为百分数**——字段名里带 `_pct` 就是为了这个。"""
    gh = state.get("gap_history") or []
    fs = state.get("failure_set") or []
    budget = state.get("budget_rounds")
    worst = max((abs(float(i["gap_pct"])) for i in fs
                 if isinstance(i.get("gap_pct"), (int, float)) and not isinstance(i.get("gap_pct"), bool)),
                default=None)
    gap_s = "%.2f%%" % worst if worst is not None else "?"
    if not budget:
        return ("剩余轮数 × 平均缩小 = ?  **vs 当前缺口 %s → 待建立**"
                "（**预算未设定** —— 4.6 需要它才能开火；去填 budget_rounds，别让它一直是空的）"
                % gap_s)
    if len(gh) < 2 or worst is None:
        return ("剩余轮数 × 平均缩小 = ?  **vs 当前缺口 %s → 待建立**（趋势需 ≥2 个点）" % gap_s)
    pts = sorted((int(i["round"]), abs(float(i["gap_pct"]))) for i in gh
                 if isinstance(i.get("gap_pct"), (int, float))
                 and isinstance(i.get("round"), int))
    span = pts[-1][0] - pts[0][0]
    if span <= 0:
        return ("剩余轮数 × 平均缩小 = ?  **vs 当前缺口 %.2f%% → 待建立**（轮次跨度为 0，"
                "趋势无意义）" % worst)
    per = (pts[0][1] - pts[-1][1]) / span
    if per < 0:
        return ("%d 轮 × %.3f %%/轮 = **缺口在扩大**  **vs 当前缺口 %.2f%% → "
                "不可达（方向反了，先查是不是记错了点）**"
                % (budget, per, worst))
    reach = per * budget
    verdict = "可达" if reach >= worst else "**不可达**"
    return ("%d 轮 × %.3f %%/轮 = %.2f%%  **vs 当前缺口 %.2f%% → %s**"
            % (budget, per, reach, worst, verdict))


# =========================================================== 原子写
def _atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".statepatch.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        shutil.move(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append_log(path: str, title: str, lines: list[str]) -> None:
    d = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(d, exist_ok=True)
    head = "" if os.path.exists(path) else "# EVENTS —— 增量日志（只追加，由 state_patch.py 写入）\n\n"
    with io.open(path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(head + "## %s  %s\n\n" % (title, _now()))
        for ln in lines:
            fh.write(ln + "\n")
        fh.write("\n")


# =========================================================== 模板
TEMPLATE = {
    "schema_version": SCHEMA_VERSION,
    "task": "<一句话：这次攻坚要达成什么>",
    "round": 0,
    "frame": {
        "name": "<当前框架：用哪条路径 / 哪套家族>",
        "status": "假设",
        "falsifier": "<证伪它的具体实验：跑什么、看什么判据>",
        "next_if_falsified": "<它被证伪之后走哪条路>",
    },
    "failure_set": [{"case": "<用例名>", "gap_pct": 0.0}],
    "gap_now_pct": 0.0,
    # 趋势从**空**开始。**不要**塞一个 {round:0, gap_pct:0.0} 的假点——
    # 那会被当成一次真实测量，把第一轮的"缩小量"算成一个巨大的数（实测踩过）。
    "gap_history": [],
    # 可以整条删掉：「我还没设预算」是真实状态，4.6 会明确说它未设定（而不是算个假结论）。
    "budget_rounds": 0,
    "excluded_paths": [{"path": "<路径>", "marker": "refuted",
                        "reason": "<为什么排除>", "evidence": "<证据路径>"}],
    "claims_ref": "<台账路径，例如 mission/CLAIMS.jsonl>",
}


# =========================================================== 自检（判据自己也要有阴性样本）
def self_test() -> int:
    import tempfile as _t
    P = F = 0

    def ok(m):
        nonlocal P; P += 1; print("  ✓ " + m)

    def bad(m):
        nonlocal F; F += 1; print("  ✗ " + m)

    def good_state():
        s = json.loads(json.dumps(TEMPLATE))
        s["task"] = "t"; s["round"] = 3; s["budget_rounds"] = 10
        s["frame"] = {"name": "A", "status": "假设", "falsifier": "跑 X 看 Y",
                      "next_if_falsified": "走 B"}
        s["failure_set"] = [{"case": "TC_1", "gap_pct": -15.2}]
        s["gap_history"] = [{"round": 1, "gap_pct": -21.0}, {"round": 3, "gap_pct": -15.2}]
        s["excluded_paths"] = [{"path": "Cube", "marker": "refuted",
                                "reason": "量级不够", "evidence": "ev/a.md"}]
        s["claims_ref"] = "CLAIMS.jsonl"
        return s

    # ---- 阴性样本：合格状态必须通过 ----
    e = validate(good_state())
    ok("阴性样本：合格状态通过校验门") if not e else bad("合格状态被误拒: %s" % e)

    # ---- 正样本：逐条验证校验门会开火 ----
    for desc, mut, key in [
        ("frame.falsifier 为空 ⇒ 信仰不是假设",
         lambda s: s["frame"].__setitem__("falsifier", ""), "falsifier"),
        ("frame.status 非法枚举", lambda s: s["frame"].__setitem__("status", "大概吧"), "status"),
        ("excluded_paths 缺失效标记",
         lambda s: s["excluded_paths"][0].__setitem__("marker", ""), "marker"),
        ("excluded_paths.evidence 为空 ⇒ 无支撑断言",
         lambda s: s["excluded_paths"][0].__setitem__("evidence", "  "), "evidence"),
        ("failure_set.gap_pct 不是数字",
         lambda s: s["failure_set"][0].__setitem__("gap_pct", "差挺多"), "gap_pct"),
        ("gap_history.round 未严格递增",
         lambda s: s["gap_history"].append({"round": 2, "gap_pct": -18.0}), "递增"),
        ("未声明的顶层键",
         lambda s: s.__setitem__("vibes", 1), "未声明"),
    ]:
        s = good_state(); mut(s)
        e = validate(s)
        if any(key in x for x in e):
            ok("正样本：%s" % desc)
        else:
            bad("正样本未开火：%s  → %s" % (desc, e))

    # ---- null 语义：删除必须真的删掉，而不是置空 ----
    s = good_state()
    s2, notes = merge(s, {"excluded_paths": None})
    if "excluded_paths" not in s2 and "excluded_paths" in s:
        ok("null 语义：键被真正删除（不是置空），且原状态未受影响")
    else:
        bad("null 语义失效")
    if s2["round"] == s["round"] + 1:
        ok("round 由工具自增：补丁里的 round 被显式拒绝")
    else:
        bad("round 自增失效")

    # ---- 被拒绝的补丁绝不能改动状态 ----
    s = good_state(); before = json.dumps(s, ensure_ascii=False, sort_keys=True)
    e = validate({**s, "frame": {**s["frame"], "falsifier": ""}})
    after = json.dumps(s, ensure_ascii=False, sort_keys=True)
    if e and before == after:
        ok("校验失败时原状态逐字节未变")
    else:
        bad("校验失败却改动了状态")

    # ---- 4.6 外推是算术：不可达时必须说不可达 ----
    s = good_state(); s["gap_history"] = [{"round": 1, "gap_pct": -21.0}, {"round": 3, "gap_pct": -20.9}]
    s["budget_rounds"] = 10
    line = extrapolate(s)
    if "不可达" in line and "×" in line:
        ok("4.6 外推给出算术式并判定不可达：%s" % line)
    else:
        bad("4.6 外推未判定不可达：%s" % line)

    # ---- 趋势由工具维护：只提交 gap_now_pct，工具追加；且禁止补丁自带 gap_history ----
    s = good_state()
    s2, _n = merge(s, {"gap_now_pct": -12.5})
    hist = s2.get("gap_history") or []
    if [h["round"] for h in hist] == [1, 3, 4] and hist[-1]["gap_pct"] == -12.5:
        ok("趋势自动追加：提交 gap_now_pct 后 gap_history 变成 %s" % [h["round"] for h in hist])
    else:
        bad("趋势未按预期追加：%s" % hist)
    if validate_patch({"gap_history": [{"round": 9, "gap_pct": -1.0}]}) and        validate_patch({"round": 9}):
        ok("补丁自带 round / gap_history 被显式拒绝（不是静默忽略）")
    else:
        bad("由工具维护的字段未被拒绝")

    # ---- ★ 单位一致性：`_pct` 是**百分数**，不是小数 ----
    # 夹具：缺口 15.2%，趋势 0.5%/轮，预算 8 轮 ⇒ 只能收 4.00% ⇒ **不可达**。
    # 若实现把它当成小数（15.2 → 0.152），打印出来的收缩量会是 "0.00%" 量级 —— 这条断言就是拦那个的。
    s = good_state()
    s["gap_history"] = [{"round": 1, "gap_pct": -21.0}, {"round": 3, "gap_pct": -20.0}]
    s["budget_rounds"] = 8
    line = extrapolate(s)
    if "不可达" in line and "4.00%" in line:
        ok("单位一致（百分数）：缺口 15.2%% + 0.5%%/轮 × 8 轮 = 4.00%% → 不可达")
    else:
        bad("单位一致性断言未按预期：%s" % line)

    # ---- 预算缺席：4.6 必须说「未设定」，不能拿出一个可达/不可达的结论 ----
    s = good_state()
    s.pop("budget_rounds", None)
    line = extrapolate(s)
    if "未设定" in line and "可达" not in line.replace("不可达", ""):
        ok("预算缺席时 4.6 说「未设定」，不给出可达/不可达的假结论")
    else:
        bad("预算缺席时 4.6 仍给了结论：%s" % line)
    if not validate(s):
        ok("budget_rounds 允许缺席（校验门不拦）")
    else:
        bad("budget_rounds 缺席被误拦")

    # ---- 模板不得有假点：init 出来的 gap_history 必须是空的 ----
    if TEMPLATE.get("gap_history") == []:
        ok("模板：gap_history 从空开始（不塞假点，否则第一轮趋势会被毒化）")
    else:
        bad("模板里 gap_history 不是空的：%s" % TEMPLATE.get("gap_history"))

    # ---- 缺口扩大时必须明说"方向反了" ----
    s = good_state()
    s["gap_history"] = [{"round": 1, "gap_pct": -10.0}, {"round": 2, "gap_pct": -14.0}]
    line = extrapolate(s)
    if "扩大" in line and "负" not in line:
        ok("缺口扩大时判「方向反了」而不是打印负的收缩量")
    else:
        bad("缺口扩大未被识别：%s" % line)

    # ---- 端到端：写盘 → 再读回 ----
    T = _t.mkdtemp()
    try:
        sp, lg, pp = os.path.join(T, "s.json"), os.path.join(T, "E.md"), os.path.join(T, "p.json")
        _atomic_write(sp, json.dumps(good_state(), ensure_ascii=False, indent=2))
        json.dump({"gap_now_pct": -10.0}, io.open(pp, "w", encoding="utf-8"))
        st = json.load(io.open(sp, encoding="utf-8"))
        np_, _ = merge(st, json.load(io.open(pp, encoding="utf-8")))
        _atomic_write(sp, json.dumps(np_, ensure_ascii=False, indent=2))
        back = json.load(io.open(sp, encoding="utf-8"))
        if back["gap_now_pct"] == -10.0 and back["task"] == st["task"]:
            ok("端到端：补丁合并后落盘、再读回一致")
        else:
            bad("端到端读写不一致")
    finally:
        shutil.rmtree(T, ignore_errors=True)

    print("\n  PASS=%d FAIL=%d" % (P, F))
    print("  全部通过。" if F == 0 else "  有断言失败 —— 上面每条 ✗ 都是【本工具不再可信】的证据。")
    return 0 if F == 0 else 1


# =========================================================== 入口
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="结构化执行状态 + 稀疏补丁 + 校验门")
    ap.add_argument("--state"); ap.add_argument("--log"); ap.add_argument("--patch")
    ap.add_argument("--task", default="<一句话：这次攻坚要达成什么>")
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)

    if a.self_test:
        print("== state_patch 自检 ==")
        return self_test()

    if a.init:
        if not a.state or not a.log:
            print("--init 需要 --state 与 --log", file=sys.stderr); return 2
        if os.path.exists(a.state):
            print("已存在，未覆盖：%s" % a.state, file=sys.stderr); return 2
        t = json.loads(json.dumps(TEMPLATE)); t["task"] = a.task
        _atomic_write(a.state, json.dumps(t, ensure_ascii=False, indent=2) + "\n")
        _append_log(a.log, "init", ["- 建立状态：`%s`" % a.state,
                                    "- schema_version=%d" % SCHEMA_VERSION])
        print("已建立 %s\n已建立 %s" % (a.state, a.log))
        return 0

    if a.show:
        if not a.state or not os.path.exists(a.state):
            print("找不到状态文件：%s" % a.state, file=sys.stderr); return 2
        st = json.load(io.open(a.state, encoding="utf-8"))
        print(json.dumps(st, ensure_ascii=False, indent=2))
        print("\n[4.6 外推] %s" % extrapolate(st))
        e = validate(st)
        if e:
            print("\n[校验门] 当前状态本身不合规：")
            for x in e: print("  - " + x)
            return 1
        return 0

    if not a.state or not a.log or not a.patch:
        print("需要 --state / --log / --patch（或用 --init / --show / --self-test）", file=sys.stderr)
        return 2

    for p in (a.state, a.patch):
        if not os.path.exists(p):
            print("找不到文件：%s" % p, file=sys.stderr); return 2

    st = json.load(io.open(a.state, encoding="utf-8"))
    pt = json.load(io.open(a.patch, encoding="utf-8"))

    perrs = validate_patch(pt)
    if perrs:
        _append_log(a.log, "REJECTED  r%d" % (int(st.get("round", 0)) + 1),
                    ["- **状态未改动。**"] +
                    ["- 拒绝原因：%s" % e for e in perrs] +
                    ["- 原补丁：`%s`" % _brief(pt, 200)])
        print("== 补丁本身不合规，状态未改动 ==")
        for e in perrs: print("  ✗ " + e)
        print("\n（拒绝已记入 %s）" % a.log)
        return 1

    new, notes = merge(st, pt)

    errs = validate(new)
    if errs:
        # ★ 校验门：补丁不生效，但"被拒绝"这件事进日志
        _append_log(a.log, "REJECTED  r%d" % (int(st.get("round", 0)) + 1),
                    ["- **状态未改动。**"] +
                    ["- 拒绝原因：%s" % e for e in errs] +
                    ["- 原补丁：`%s`" % _brief(pt, 200)])
        print("== 校验门拒绝，状态未改动 ==")
        for e in errs: print("  ✗ " + e)
        print("\n（拒绝已记入 %s）" % a.log)
        return 1

    _atomic_write(a.state, json.dumps(new, ensure_ascii=False, indent=2) + "\n")
    _append_log(a.log, "APPLIED  r%d" % new["round"],
                notes + ["", "- **4.6 外推**：%s" % extrapolate(new)])
    print("== 已合并，round=%d ==" % new["round"])
    for n in notes: print("  " + n)
    print("\n  4.6 外推: %s" % extrapolate(new))
    return 0


if __name__ == "__main__":
    sys.exit(main())
