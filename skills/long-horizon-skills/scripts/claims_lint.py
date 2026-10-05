#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# claims_lint.py —— 台账（CLAIMS）的机械检查。**原生载体是 JSONL，不是 markdown 表格。**
#
# 为什么换载体（2026-09-14，第二次独立战役的实操反馈）：
#   旧版把 **markdown 表格当数据格式**，于是那一轮四条修复里**三条是这个选择直接导致的**：
#     · 单元格内容含裸 `|`（`a||b`、`|x|`）⇒ `awk -F'|'` **静默把行切开**，
#       而报出来的是症状（"证据路径不存在""引用悬空"），不是病因；
#     · 证据路径是目录时 `test -f` 假阴性；
#     · `derived_from` 与「取代」的分工没写清（误触失效闭包）。
#   ⇒ **换载体，而不是继续给表格打补丁。** 同一个教训本仓已经吃过一次：
#     执行状态从散文换成 `state.json` 之后，"每轮重发全部历史"那一类问题整类消失。
#
# 分工（与 state.json 同构）：
#   **JSONL 是唯一真相源**（一行一条，机器读写）；**markdown 表格是派生视图**（人读）。
#   `--render` 生成视图；`--from-md` 把旧表格转成 JSONL（**一次性迁移**，之后会 WARN 提示）。
#
# 用法：
#   claims_lint.py --ledger CLAIMS.jsonl [--root DIR] [--doc 派生文档]... [--strict]
#   claims_lint.py --ledger CLAIMS.md --to-jsonl        # 迁移：输出 JSONL 到 stdout
#   claims_lint.py --ledger CLAIMS.jsonl --render       # 渲染：输出 markdown 表格
#   claims_lint.py --self-test
#
# 退出码：0=通过（可能有 WARN）  1=有 ERROR  2=无法判定（用法/文件错误）
# ---------------------------------------------------------------------------
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys

# 强制 UTF-8 输出：Windows 默认控制台是 GBK，会直接崩在 ✓ 上。
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

COLUMNS = ["id", "结论", "等级", "原始证据路径", "derived_from",
           "valid_from", "invalidated_at", "invalidated_by", "记录人"]
# JSON 字段名 ⇄ markdown 列名
J2C = {"id": "id", "claim": "结论", "grade": "等级", "evidence": "原始证据路径",
       "derived_from": "derived_from", "valid_from": "valid_from",
       "invalidated_at": "invalidated_at", "invalidated_by": "invalidated_by",
       "recorder": "记录人"}
GRADES = {"已被独立复核": 3, "已实测": 2, "未受攻击": 1, "INVALID": 0}
EMPTY = ("", "—", "-", None)

ERR = WARN = 0
def err(m):
    global ERR; ERR += 1; print("ERROR: " + m)
def warn(m):
    global WARN; WARN += 1; print("WARN : " + m)

def _blank(v) -> bool:
    return v in EMPTY or (isinstance(v, str) and not v.strip())

def _ids(v):
    """derived_from / invalidated_by 允许字符串或数组。"""
    if _blank(v):
        return []
    if isinstance(v, list):
        return [str(x).strip() for x in v if not _blank(x)]
    return [x.strip() for x in str(v).replace("，", ",").split(",") if x.strip()]

def is_dead(c: dict) -> bool:
    """「已失效」谓词。**④ 与 ⑤ 必须用同一个**，否则会出现
    「⑤ 豁免了、④ 却仍当它活着」的裂缝（旧版被夹具抓到过）。"""
    g = str(c.get("grade", ""))
    if not _blank(c.get("invalidated_at")) or not _blank(c.get("invalidated_by")):
        return True
    return g == "INVALID" or "invalidated" in g or "superseded" in g


# ============================================================ 载入
def load_jsonl(path: str) -> list[dict]:
    out = []
    for n, line in enumerate(io.open(path, encoding="utf-8"), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            o = json.loads(line)
        except json.JSONDecodeError as ex:
            err("第 %d 行不是合法 JSON：%s" % (n, ex)); continue
        if not isinstance(o, dict):
            err("第 %d 行不是对象" % n); continue
        o["_line"] = n
        out.append(o)
    return out


CANON = {"id": "id", "结论": "claim", "等级": "grade", "原始证据路径": "evidence",
         "derived_from": "derived_from", "valid_from": "valid_from",
         "invalidated_at": "invalidated_at", "invalidated_by": "invalidated_by",
         "记录人": "recorder"}


def _norm_key(k: str) -> str:
    """列名规范化：**去掉括号后缀**再比对。
    真实台账里那一列常写成 `结论（一句话）`——锚定模板说的是"列按名字识别"，
    所以按 `结论` 精确匹配是错的（迁移真实台账时撞到过，整列读成空）。"""
    k = k.strip().lower()
    return re.split(r"[（(]", k)[0].strip()


def load_md(path: str) -> tuple[list[dict], list[str]]:
    """把旧的 markdown 表格读进来。**这是迁移路径，不是稳态。**
    返回 (条目, 结构性问题)。"""
    rows, probs = [], []
    hdr = None
    for n, line in enumerate(io.open(path, encoding="utf-8"), 1):
        if not line.lstrip().startswith("|"):
            continue
        cells = line.strip().strip("|").split("|")
        cells = [c.strip() for c in cells]
        if hdr is None:
            low = [_norm_key(c) for c in cells]
            if "id" in low:
                hdr = low
            continue
        if re.fullmatch(r"[-: ]+", "".join(cells)):
            continue
        # ★ 列数不符 ⇒ **直接报病因**，而不是让错位的值去冒充结论
        if len(cells) != len(hdr):
            probs.append("第 %d 行有 %d 列，表头是 %d 列 —— **这一行的内容里有一个裸的 `|`**，"
                         "它把行切开了。病因在这一行，不要把它读成'某条证据不存在'。"
                         % (n, len(cells), len(hdr)))
            continue
        raw = {k: v for k, v in zip(hdr, cells)}
        rec = {f: raw.get(k, "") for k, f in CANON.items()}
        rec["derived_from"] = _ids(rec.get("derived_from"))
        rec["invalidated_by"] = _ids(rec.get("invalidated_by"))
        rec["_line"] = n
        rows.append(rec)
    return rows, probs


def render_md(claims: list[dict]) -> str:
    out = ["| " + " | ".join(COLUMNS) + " |",
           "|" + "|".join(["---"] * len(COLUMNS)) + "|"]
    for c in claims:
        cells = []
        for k in ["id", "claim", "grade", "evidence"]:
            cells.append(str(c.get(k) or "—").replace("|", "\\|"))
        cells.append(", ".join(_ids(c.get("derived_from"))) or "—")
        cells.append(str(c.get("valid_from") or ""))
        cells.append(str(c.get("invalidated_at") or ""))
        cells.append(", ".join(_ids(c.get("invalidated_by"))) or "")
        cells.append(str(c.get("recorder") or ""))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


# ============================================================ 检查
def run(claims: list[dict], docs: list[str], root: str, strict: bool, probs=None) -> int:
    global ERR
    for p in (probs or []):
        err("① " + p)

    by_id = {}
    for c in claims:
        cid = str(c.get("id") or "").strip()
        if cid not in by_id:
            by_id[cid] = c

    # ---- ① id 唯一 / 合法 ----
    seen = set()
    for c in claims:
        cid = str(c.get("id") or "").strip()
        if not re.fullmatch(r"[A-Z]+-[0-9]+", cid):          # 约定是 `C-001`：前缀大写
            err("① id 格式非法: %r（应为 C-001 形式）" % cid)
        if cid in seen:
            err("① 重复 id: %s（第 %d 行）" % (cid, c.get("_line", 0)))
        seen.add(cid)
    # ---- 字段名 ----
    for c in claims:
        extra = set(c) - set(J2C) - {"_line"}
        if extra:
            err("① 第 %d 行有未声明的字段: %s（字段集固定，别加私有字段）"
                % (c.get("_line", 0), ", ".join(sorted(extra))))
        if not _blank(c.get("grade")) and str(c.get("grade")) not in GRADES:
            err("① %s 的等级 `%s` 不在 {%s} 里（`未验证` 由本工具算出，不要手写）"
                % (c.get("id"), c.get("grade"), " / ".join(GRADES)))

    # ---- ② 证据路径存在性（-e：**文件或目录都算**） ----
    degraded = with_ev = miss_ev = 0
    for c in claims:
        ev = c.get("evidence")
        if _blank(ev):
            continue
        with_ev += 1
        p = str(ev)
        full = p if os.path.isabs(p) else os.path.join(root, p)
        if not os.path.exists(full):
            warn("② %s 的原始证据路径不存在 ⇒ 降级为 未验证 : %s" % (c.get("id"), ev))
            degraded += 1; miss_ev += 1
    if miss_ev > 1 and miss_ev == with_ev:
        print("     ⇒ **全部 %d 条证据路径都找不到。** 先怀疑 `--root` 给错了：" % with_ev)
        print("       当前 root=%s。台账里的路径是相对它解析的。" % root)
        print("       换个 root 再跑一遍，再判断台账本身。")

    # ---- ⑤ 无支撑断言 / ⑥ invalidated_by 悬空 ----
    for c in claims:
        cid = c.get("id")
        if _blank(c.get("evidence")) and not _ids(c.get("derived_from")) and not is_dead(c):
            err("⑤ %s 是【无支撑断言】：既无原始证据路径，也无 derived_from，且**未标失效**。" % cid)
            print("       ⇒ 这正是「从未被声明的隐含前提」的形态（例：\"探针真的跑了\"）。")
            print("       ⇒ 要么给出证据路径，要么写明它从哪几条推出；若本就已被推翻，"
                  "请标 grade=INVALID 并填 invalidated_at / invalidated_by。")
        for r in _ids(c.get("invalidated_by")):
            if r not in by_id:
                err("⑥ %s 的 invalidated_by 指向不存在的 id: %s" % (cid, r))

    # ---- ④ 失效的传递闭包 ----
    eff = {c.get("id") for c in claims if is_dead(c)}
    hop = 0
    while hop < 50:
        hop += 1
        snap, added = set(eff), set()
        for c in claims:
            if c.get("id") in eff:
                continue
            for p in _ids(c.get("derived_from")):
                if p in snap:
                    err("④ 闭包（第 %d 跳）：%s 依赖 %s，而 %s 已失效/被取代 ⇒ **%s 必须一并标掉**（当前未标）。"
                        % (hop, c.get("id"), p, p, c.get("id")))
                    if hop == 1:
                        print("       ⇒ 这就是 G1：『未测』被写成『已实测』后，撤回不传播，假结论留在派生文档里。")
                    eff.add(c.get("id")); added.add(c.get("id")); break
        if not added:
            break
    if hop >= 50:
        err("④ 闭包在 50 跳内未收敛 —— 台账里可能有环（derived_from 互相引用）。")

    # ---- ③ 派生文档 ----
    for d in docs:
        if not d:
            continue
        if not os.path.exists(d):
            warn("③ 派生文档不存在: %s" % d); continue
        text = io.open(d, encoding="utf-8", errors="replace").read()
        # 切成 (id, 紧随其后的片段)：片段到**下一个 id**为止。
        # 不做行级归属 —— 一行里列多个 id 时，行级归属会把别人括号里的等级算到自己头上（夹具抓到过）。
        found = [(m.group(0), m.start()) for m in re.finditer(r"[A-Za-z]+-[0-9]+", text)]
        for i, (rid, pos) in enumerate(found):
            end = found[i + 1][1] if i + 1 < len(found) else len(text)
            seg = text[pos + len(rid):end]
            if rid not in by_id:
                err("③ %s 引用了台账中不存在的 id: %s" % (d, rid)); continue
            lg = str(by_id[rid].get("grade") or "")
            for tok in ("已实测", "已被独立复核", "未受攻击"):
                if tok in seg and GRADES.get(tok, -1) > GRADES.get(lg, -1):
                    m = "③ %s 里 %s 被标为 `%s`，而台账是 `%s` —— 派生文档不得升级等级" % (d, rid, tok, lg)
                    (err if strict else warn)(m)
    return ERR


# ============================================================ 自检
def self_test() -> int:
    import tempfile
    P = F = 0
    def ok(m):
        nonlocal P; P += 1; print("  ✓ " + m)
    def bad(m):
        nonlocal F; F += 1; print("  ✗ " + m)
    def run_case(claims, docs, root, strict, expect_err, desc, want=None):
        global ERR, WARN
        ERR = WARN = 0
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            run(claims, docs, root, strict)
        finally:
            sys.stdout = old
        out = buf.getvalue()
        if (ERR > 0) == expect_err:
            ok(desc + ("（报错）" if expect_err else "（不报错）"))
        else:
            bad("%s → 期望 %s，实际 ERROR=%d\n%s" % (desc, "报错" if expect_err else "不报错", ERR, out))
        if want and want not in out:
            bad("%s → 输出里没有 [%s]" % (desc, want))

    T = tempfile.mkdtemp()
    os.makedirs(os.path.join(T, "ev"), exist_ok=True)
    io.open(os.path.join(T, "ev", "real.md"), "w").close()
    os.makedirs(os.path.join(T, "ev", "dir_evidence"), exist_ok=True)

    def C(i, g="已实测", ev="ev/real.md", der=None, invby=None, invat=None):
        return {"id": i, "claim": "c", "grade": g, "evidence": ev,
                "derived_from": der or [], "valid_from": "2026-01-01",
                "invalidated_at": invat, "invalidated_by": invby, "recorder": "t", "_line": 0}

    # 阴性样本
    run_case([C("C-001"), C("C-002", der=["C-001"])], [], T, False, False, "阴性样本：干净台账不报错")
    # 逐条正样本
    # ② 是 **WARN**（降级为未验证），不是 ERROR —— 所以这里期望"不报 ERROR"，但文案必须出现。
    run_case([C("C-001", ev="ev/missing.md")], [], T, False, False,
             "② 证据路径不存在 ⇒ WARN 降级（不是 ERROR）", "降级为 未验证")
    run_case([C("C-001", g="未受攻击", ev=None, der=None)], [], T, False, True, "⑤ 无支撑断言", "无支撑断言")
    run_case([C("C-001"), C("C-002", invby=["C-999"])], [], T, False, True, "⑥ 悬空引用", "不存在")
    # ④ 的链必须**从一个真的死条目开始**：C-003 被推翻 ⇒ C-004 依赖它 ⇒ C-005 依赖 C-004。
    chain1 = [C("C-001"), C("C-002"),
              C("C-003", invat="2026-01-02", invby=["C-001"]),
              C("C-004", der=["C-003"])]
    run_case(chain1, [], T, False, True, "④ 闭包第 1 跳", "第 1 跳")
    chain2 = chain1 + [C("C-005", der=["C-004"])]
    run_case(chain2, [], T, False, True, "④ 闭包第 2 跳（撤回确实传播）", "第 2 跳")
    # 反面对照：依赖一条**活着**的条目，不该开火（否则它是假阳性机器）
    run_case([C("C-001"), C("C-002", der=["C-001"])], [], T, False, False,
             "④ 阴性对照：依赖活条目不开火")
    run_case([C("c-1")], [], T, False, True, "① id 格式非法", "格式非法")
    run_case([C("C-001"), C("C-001")], [], T, False, True, "① 重复 id", "重复")
    run_case([C("C-001", g="大概吧")], [], T, False, True, "① 等级非法", "不在")
    # ⑤ 的豁免口径必须与 ④ 一致：只填 invalidated_by 也应豁免
    run_case([C("C-001", g="未受攻击", ev=None, invby=["C-002"]), C("C-002")],
             [], T, False, False, "⑤ 豁免只填 invalidated_by 的条目（失效谓词一致）")
    # ★ 目录作证据路径：必须**不**判缺失（旧版 test -f 会给假阴性）
    run_case([C("C-001", ev="ev/dir_evidence")], [], T, False, False, "★ 目录作证据路径 ⇒ 算存在")
    # ③ 派生文档不得升级
    doc = os.path.join(T, "d.md")
    io.open(doc, "w", encoding="utf-8").write("见 C-001(已被独立复核)。\n")
    run_case([C("C-001", g="已实测")], [doc], T, True, True, "③ 派生文档升级等级（strict）", "不得升级")

    # ★ markdown 导入：裸 `|` 必须报**病因**，而不是让错位的值冒充结论
    md = os.path.join(T, "OLD.md")
    io.open(md, "w", encoding="utf-8").write(
        "| id | 结论 | 等级 | 原始证据路径 | derived_from | valid_from | invalidated_at | invalidated_by | 记录人 |\n"
        "|---|---|---|---|---|---|---|---|---|\n"
        "| C-001 | 表达式 a||b | 已实测 | ev/real.md | — | 2026-01-01 | | | t |\n")
    rows, probs = load_md(md)
    if probs and "裸" in probs[0]:
        ok("★ markdown 导入：裸 `|` 报的是**病因**（这一行多了一列）")
    else:
        bad("markdown 导入未报病因：%s" % probs)

    # 往返：md → JSONL → 渲染 → 再导入，条目数一致
    md2 = os.path.join(T, "OK.md")
    io.open(md2, "w", encoding="utf-8").write(
        "| id | 结论 | 等级 | 原始证据路径 | derived_from | valid_from | invalidated_at | invalidated_by | 记录人 |\n"
        "|---|---|---|---|---|---|---|---|---|\n"
        "| C-001 | 甲 | 已实测 | ev/real.md | — | 2026-01-01 | | | t |\n"
        "| C-002 | 乙 | 未受攻击 | — | C-001 | 2026-01-01 | | | t |\n")
    r2, p2 = load_md(md2)
    rendered = render_md(r2)
    io.open(md2, "w", encoding="utf-8").write(rendered + "\n")
    r3, p3 = load_md(md2)
    if not p2 and not p3 and len(r2) == len(r3) == 2 and r3[0]["id"] == "C-001":
        ok("往返一致：markdown → 内部 → 渲染 → 再导入，条目数与 id 不变")
    else:
        bad("往返不一致：%d/%d 条，问题 %s/%s" % (len(r2), len(r3), p2, p3))

    print("\n  PASS=%d FAIL=%d" % (P, F))
    print("  全部通过。" if F == 0 else "  有断言失败 —— 上面每条 ✗ 都是【本工具不再可信】的证据。")
    return 0 if F == 0 else 1


# ============================================================ 入口
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="台账 lint（原生 JSONL）")
    ap.add_argument("--ledger")
    ap.add_argument("--root", default="")
    ap.add_argument("--doc", action="append", default=[])
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--to-jsonl", action="store_true", help="把旧 markdown 台账转成 JSONL（迁移用）")
    ap.add_argument("--render", action="store_true", help="把 JSONL 渲染成 markdown 表格（人读）")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)

    if a.self_test:
        print("== claims_lint 自检 ==")
        return self_test()
    if not a.ledger or not os.path.exists(a.ledger):
        print("找不到台账: %s" % a.ledger, file=sys.stderr); return 2
    root = a.root or os.path.dirname(os.path.abspath(a.ledger)) or "."

    is_md = a.ledger.lower().endswith(".md")
    if is_md:
        claims, probs = load_md(a.ledger)
        if a.to_jsonl:
            for c in claims:
                c.pop("_line", None)
                print(json.dumps(c, ensure_ascii=False))
            return 0
    else:
        claims, probs = load_jsonl(a.ledger), []

    if a.render:
        print(render_md(claims)); return 0

    print("=== claims_lint · 台账 %s （%d 条）===" % (a.ledger, len(claims)))
    if is_md:
        warn("载体是 **markdown 表格**（旧格式）。迁移到 JSONL 一次即可：")
        print("     ⇒ `python3 claims_lint.py --ledger %s --to-jsonl > CLAIMS.jsonl`" % a.ledger)
        print("       markdown 表格里裸的 `|` 会**静默切行**，而报出来的是症状不是病因——换载体能整类消除它。")
    if not claims:
        warn("台账里 0 条：**格式已解析成功**，脚本可运行；但别忘了登记条目。")
        print("     ⇒ 第 0 天的空转检查到此即完成（退出码 0）。")

    run(claims, a.doc, root, a.strict, probs)

    print()
    print("=== 结论 ===")
    print("ERROR=%d  WARN=%d  台账条目=%d" % (ERR, WARN, len(claims)))
    if ERR:
        print("不通过。[退出码 1]")
        print("⇒ ERROR 级都是【能机械判定】的：补证据路径、补 derived_from、补失效标记、修 id 引用。")
        return 1
    print("通过。[退出码 0]")
    print("!! 提醒：本 lint 只能检查【你写下来的】依赖边，不能替你发现漏写的依赖（§2.5.2 边界）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
