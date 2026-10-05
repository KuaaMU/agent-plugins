#!/usr/bin/env bash
# probe_liveness.sh —— 装置门（SKILL §3）的可执行形态。
#
# 解决的问题（E1）：一个 routed / gated / env-gated 探针，如果它的分支对目标输入
#   **根本不可达**，两臂跑的就是同一份代码——"逐例平坦"会被读成一次干净的否定结果。
#   预注册、A/B/A 对照、精度门、性能门**全部放行**；只有对装置本身的检查能拦住它。
#
# 本脚本自动执行 §3.1 的【方法①结构检查】；把【②廉价行为】【③决定性内核名】
#   与【④只有新路径能影响的用例】的确切命令打印出来（它们需要设备/构建，脚本不代跑）。
#
# 用法：
#   probe_liveness.sh --src <host.cpp> --func <入口函数名> --probe <探针标记正则> \
#                     --target <目标谓词> [--target <目标谓词>]... [--label <标签>]
#
# 例（目标：一个在 n<=16 时被更早分支拦截的探针）：
#   probe_liveness.sh --src <host 源文件> --func <算子入口> \
#     --probe 'MY_PROBE_ENV' \
#     --target 'n <= 16' --target 'lda == n' --target 'flags != nullptr'
#
# 退出码：
#   0 = 未发现拦截（结构上可能可达；**仍须**完成 ② 或 ③ 才能读任何数字）
#   1 = INVALID —— 探针之前存在覆盖目标输入的 return（实验没有发生）
#   2 = 无法判定（找不到函数/探针标记，或源码结构超出本脚本的启发式范围）
#
# 边界：① 是**启发式**的（括号深度 + if 守卫链 + 简单别名解析 + 无括号 if 的前置行）。
#   命中 ⇒ 可判 INVALID（脚本会把守卫原文与行号打出来供复核）。
#   未命中 ⇏ 已证明可达。**永远不要把退出码 0 当作生效证据。**

set -uo pipefail

SRC=""; FUNC=""; PROBE=""; LABEL=""
TARGETS=()

usage() { sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'; }

while [ $# -gt 0 ]; do
  case "$1" in
    --src)    SRC="${2:-}";   shift 2 ;;
    --func)   FUNC="${2:-}";  shift 2 ;;
    --probe)  PROBE="${2:-}"; shift 2 ;;
    --target) TARGETS+=("${2:-}"); shift 2 ;;
    --label)  LABEL="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "未知参数: $1" >&2; usage; exit 2 ;;
  esac
done

[ -n "$SRC" ] && [ -n "$FUNC" ] && [ -n "$PROBE" ] || { usage; exit 2; }
[ -f "$SRC" ] || { echo "找不到源文件: $SRC" >&2; exit 2; }
[ "${#TARGETS[@]}" -gt 0 ] || { echo "至少需要一个 --target（目标输入必须写成显式谓词）" >&2; exit 2; }

LABEL="${LABEL:-$SRC}"
TMP="$(mktemp)"; REVIEW="$(mktemp)"; trap 'rm -f "$TMP" "$REVIEW"' EXIT

norm() { printf '%s' "$1" | tr -d ' \t\r\n'; }
split_preds() { printf '%s' "$1" | awk '{n=split($0,a,"&&"); for(i=1;i<=n;i++){gsub(/^[ \t]+|[ \t]+$/,"",a[i]); if(length(a[i])) print a[i]}}'; }
text_of() { awk -F'|' -v L="$1" '$1==L{s=$0; sub(/^[0-9]+\|[0-9]+\|/,"",s); print s; exit}' "$TMP"; }
db_of()   { awk -F'|' -v L="$1" '$1==L{print $2; exit}' "$TMP"; }

# ---------------------------------------------------------------- 抓函数体
FSTART="$(grep -n "^[A-Za-z_].*[^A-Za-z0-9_]${FUNC}[[:space:]]*(" "$SRC" | head -1 | cut -d: -f1)"
[ -n "$FSTART" ] || { echo "ERROR: 在 $SRC 里找不到函数 $FUNC" >&2; exit 2; }
FEND="$(awk -v s="$FSTART" 'NR>s && /^\}/{print NR; exit}' "$SRC")"
[ -n "$FEND" ] || { echo "ERROR: 找不到 $FUNC 的结束大括号" >&2; exit 2; }

# ---------------------------------------------------------------- 深度表  行号|行前深度|原文
awk -v s="$FSTART" -v e="$FEND" '
function strip(l,  i,c,out,ins,inch){
  out=""; ins=0; inch=0
  for(i=1;i<=length(l);i++){
    c=substr(l,i,1)
    if(incmt){ if(c=="/"&&substr(l,i+1,1)=="*"){incmt=0;i++}; continue }
    if(ins){ if(c=="\\"){i++;continue}; if(c=="\""){ins=0}; continue }
    if(inch){ if(c=="\\"){i++;continue}; if(c=="'"'"'"){inch=0}; continue }
    if(c=="/"&&substr(l,i+1,1)=="/"){break}
    if(c=="/"&&substr(l,i+1,1)=="*"){incmt=1;i++;continue}
    if(c=="\""){ins=1;continue}
    if(c=="'"'"'"){inch=1;continue}
    out=out c
  }
  return out
}
NR>=s && NR<=e {
  printf "%d|%d|%s\n", NR, depth, $0
  st=strip($0); o=gsub(/\{/,"{",st); c=gsub(/\}/,"}",st); depth += o - c
}' "$SRC" > "$TMP"

PROBE_LINE="$(awk -F'|' -v p="$PROBE" '$0 ~ p {print $1; exit}' "$TMP")"
[ -n "$PROBE_LINE" ] || { echo "ERROR: 在 $FUNC 体内找不到探针标记 /$PROBE/" >&2; exit 2; }
FUNC_DEPTH="$(db_of "$FSTART")"

echo "=== 装置门 · 方法① 结构检查（启发式）==="
echo "文件      : $LABEL"
echo "入口函数  : $FUNC   (行 $FSTART..$FEND)"
echo "探针标记  : /$PROBE/  出现在第 $PROBE_LINE 行"
printf '目标输入  :'; for t in "${TARGETS[@]}"; do printf ' [%s]' "$t"; done; echo; echo

# ---------------------------------------------------------------- 条件文本抽取
# 若语句跨越数行（多行 if 条件），先把这些行拼起来再配对括号。
stmt_start() {  # $1 = 块起始行（以 '{' 结尾的那一行）→ 该语句的第一行
  local a="$1" pa da ta
  while :; do
    pa=$((a-1))
    [ "$pa" -ge "$FSTART" ] || break
    da="$(db_of "$a")"
    [ "$(db_of "$pa")" = "$da" ] || break          # 深度不同 ⇒ 不是同一语句的续行
    ta="$(text_of "$pa")"
    # 注意：空串经 printf 管道给 grep 是**零行**，'^[[:space:]]*$' 永远不匹配 ⇒ 必须用 strip 判空
    [ -z "$(printf '%s' "$ta" | tr -d ' \t\r')" ] && break
    printf '%s' "$ta" | grep -qE '^[[:space:]]*//'  && break
    printf '%s' "$ta" | grep -q '[;{}]'             && break
    a="$pa"
  done
  printf '%s' "$a"
}

cond_of_range() {  # $1..$2 = 行范围 → 第一个配对括号内的条件文本
  awk -v S="$1" -v E="$2" -v f="$SRC" 'NR>=S&&NR<=E{printf "%s ",$0}' "$SRC" | awk '
    { line=$0; s=index(line,"(")
      if(s==0) exit 1
      acc=substr(line,s); d=0
      for(i=1;i<=length(acc);i++){
        c=substr(acc,i,1)
        if(c=="(")d++
        else if(c==")"){d--; if(d==0){print substr(acc,2,i-2); exit}}
      } }'
}

resolve_alias() {
  awk -v N="$1" -v f="$SRC" '
  $0 ~ "(bool|int|uint32_t|const bool)[ \t]+"N"[ \t]*=" {
    line=$0; sub(/^[^=]*=/,"",line); acc=line
    while(acc !~ /;/ && (getline nxt)>0) acc=acc" "nxt
    sub(/;.*/,"",acc); gsub(/^[ \t]+|[ \t]+$/,"",acc)
    if(acc ~ /^\(.*\)$/){acc=substr(acc,2,length(acc)-2)}
    print acc; exit
  }' "$SRC"
}

# 归一化一段条件：解析别名 → 拆谓词
cond_preds() {
  local c="$1"
  if printf '%s' "$c" | grep -qE '^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*[[:space:]]*$'; then
    c="$(resolve_alias "$(printf '%s' "$c" | tr -d '[:space:]')")"
  fi
  [ -n "$c" ] || return 0
  split_preds "$c"
}

covered_by_targets() {  # $1=条件文本 → 0=被完全覆盖  1=未覆盖（缺失项写入 COV_MISS）
  local preds t miss=""
  preds="$(cond_preds "$1")"
  [ -n "$preds" ] || { COV_MISS="(条件无法解析)"; return 1; }
  for t in "${TARGETS[@]}"; do
    # 用 ' \t\r' 而**不是** '[:space:]'：后者会把换行也删掉，把多条谓词粘成一行
    printf '%s\n' "$preds" | tr -d ' \t\r' | grep -qxF "$(norm "$t")" || miss="$miss [$t]"
  done
  if [ -z "$miss" ]; then return 0; else COV_MISS="$miss"; return 1; fi
}

guard_chain() {  # $1=return 行 → 由内向外的 if 块起始行
  local L="$1" d a jt
  d="$(db_of "$L")"
  while [ "$d" -gt "$FUNC_DEPTH" ]; do
    a="$(awk -F'|' -v L="$L" -v T="$((d-1))" '$1<L && $2==T {n=$1} END{print n}' "$TMP")"
    if [ -n "$a" ]; then
      # 多行 if 条件的块起始行是条件的**最后一行**，它本身不以 "if (" 开头；
      # 因此先把语句拼起来（stmt_start..a）再判断。
      jt="$(guard_text "$a")"
      if grep -qE '^[[:space:]]*\}?[[:space:]]*(else[[:space:]]+)?if[[:space:]]*\(' <<< "$jt"; then printf '%s\n' "$a"; fi
    fi
    d=$((d-1))
  done
}

# 整条 if 语句的条件文本（处理多行条件）
guard_cond() { local a="$1"; cond_of_range "$(stmt_start "$a")" "$a"; }

guard_text() {  # 打印整条守卫语句（已去掉缩进，多行合并）
  local a="$1" s; s="$(stmt_start "$a")"
  awk -v S="$s" -v E="$a" -v f="$SRC" 'NR>=S&&NR<=E{t=$0; sub(/^[ \t]+/,"",t); printf "%s ", t}' "$SRC"
}

prev_code_line() {  # $1 之前最近的非空非注释行
  awk -F'|' -v L="$1" '$1<L && $0 !~ /\|[ \t]*($|\/\/)/ {n=$1} END{print n}' "$TMP"
}

# ---------------------------------------------------------------- 扫描
RETURNS="$(awk -F'|' -v P="$PROBE_LINE" '$1<P && $0 ~ /return[ \t]/ {print $1}' "$TMP")"
VERDICT=0; HITS=0; NREVIEW=0

for L in $RETURNS; do
  TEXT="$(text_of "$L" | sed 's/^[ \t]*//')"
  FOUND=0

  # (a) 无括号 if 同行：`if (cond) return X;`
  if printf '%s' "$TEXT" | grep -qE '^[[:space:]]*\}?[[:space:]]*(else[[:space:]]+)?if[[:space:]]*\('; then
    C="$(cond_of_range "$L" "$L")"
    if [ -n "$C" ]; then
      FOUND=1
      if covered_by_targets "$C"; then
        echo "!! 第 $L 行：无括号 if 同行 return，守卫**完全覆盖**目标输入"
        echo "     $L: $TEXT"
        echo "   ⇒ 结论 INVALID（探针不可达）。"; echo
        VERDICT=1; HITS=$((HITS+1)); continue
      fi
      echo "-- 第 $L 行：同行 if 未完全覆盖（缺:$COV_MISS）| $TEXT" >> "$REVIEW"; NREVIEW=$((NREVIEW+1))
    fi
  fi

  # (b) 上一行是无括号 if：`if (cond)` \n `return X;`
  P="$(prev_code_line "$L")"
  if [ -n "$P" ]; then
    PT="$(text_of "$P")"
    if grep -qE '^[[:space:]]*\}?[[:space:]]*(else[[:space:]]+)?if[[:space:]]*\(' <<< "$PT" && ! grep -q '{' <<< "$PT"; then
      C="$(cond_of_range "$(stmt_start "$P")" "$P")"
      if [ -n "$C" ]; then
        FOUND=1
        if covered_by_targets "$C"; then
          echo "!! 第 $L 行：return 由其上一行的无括号 if 守卫，**完全覆盖**目标输入"
          echo "     $(guard_text "$P")"
          echo "     $L: $TEXT"
          echo "   ⇒ 结论 INVALID（探针不可达）。"; echo
          VERDICT=1; HITS=$((HITS+1)); continue
        fi
        echo "-- 第 $L 行：上一行的 if 未完全覆盖（缺:$COV_MISS）| $(guard_text "$P")" >> "$REVIEW"; NREVIEW=$((NREVIEW+1))
      fi
    fi
  fi

  # (c) 花括号块内的守卫链
  CHAIN="$(guard_chain "$L")"
  if [ -z "$CHAIN" ]; then
    echo "!! 第 $L 行是**无条件** return（函数体内无任何 if 守卫），位于探针之前 ⇒ 拦截所有输入"
    echo "     $L: $TEXT"
    echo "   ⇒ 结论 INVALID（探针不可达）。"; echo
    VERDICT=1; HITS=$((HITS+1)); continue
  fi
  while read -r G; do
    [ -n "$G" ] || continue
    GC="$(guard_cond "$G")"
    if covered_by_targets "$GC"; then
      echo "!! 第 $L 行的 return 被守卫**完全覆盖**："
      echo "     守卫   $G: $(guard_text "$G")"
      echo "     条件      : $(cond_preds "$GC" | awk 'NR>1{printf " && "} {printf "%s", $0}')"
      echo "     return $L: $TEXT"
      echo "   ⇒ 目标输入满足该守卫 ⇒ 在探针之前就返回 ⇒ 结论 INVALID（探针不可达）。"; echo
      VERDICT=1; HITS=$((HITS+1)); FOUND=1; break
    else
      echo "-- 第 $L 行：守卫 $G 未完全覆盖（缺:$COV_MISS）| $(guard_text "$G")" >> "$REVIEW"; NREVIEW=$((NREVIEW+1))
    fi
  done <<< "$CHAIN"
  [ "$FOUND" = "1" ] && continue
done

if [ "$NREVIEW" -gt 0 ]; then
  echo "--- 其余更早的 return（未被完全覆盖，供人工确认；最多列 8 条）---"
  head -8 "$REVIEW"; echo "   （共 $NREVIEW 条）"; echo
fi

echo "=== 方法① 结论 ==="
if [ "$VERDICT" = "1" ]; then
  echo "INVALID —— 命中 $HITS 个拦截。                        [退出码 1]"
  echo "⇒ 本次实验**没有发生**：不得记 refuted，只能记 INVALID（SKILL §3.6）；"
  echo "  不进 §4 失败计数，但必须进 §7 自我否证清单。"
  echo "⇒ 把探针移到上述**最早的那个拦截守卫之前**，然后重跑本脚本。"
else
  echo "结构上未发现拦截（启发式）。                          [退出码 0]"
  echo "!! 这不等于已证明可达 —— 必须再完成 ② 或 ③ 才能读任何数字。"
fi
echo

cat <<'RUNBOOK'
=== 方法② 廉价行为（需一次构建 + 一次单例运行）===
  在探针分支内加：
      fprintf(stderr, "[PROBE-FIRED] n=%d batch=%u\n", n, batchSize);
  跑一个目标用例后：
      <run cmd> 2>&1 | grep PROBE-FIRED
  看到 ⇒ live；看不到 ⇒ INVALID。把这一行输出抄进实验记录。

=== 方法③ 决定性：内核名直方图（需一次采集）===
  <profiler> --kernel-names --app "<run cmd>" --out /tmp/verify_on    # 探针臂（命令属领域层）
  <profiler> --kernel-names --app "<run cmd>" --out /tmp/verify_off   # 对照臂
  [领域层] 读两份内核名清单并做直方图 \
    | awk -F, '{print $2}' | sort | uniq -c
  判据：探针臂出现探针所选内核（如 `probe_kernel`），对照臂是生产内核
        启动次数同时减半，与"一个内核替掉两次启动"一致。


=== 方法④ 找一条"只有新路径能影响"的用例（无需额外构建或采集，优先复用）===
  若探针改变了路由/分桶，找出**唯一能命中新桶**的用例，证明它动了。
  例：若探针新增了一个 (R,P) 的桶，去找**只有该尺寸**能命中它的用例，看它是否移动。
  找不到这样的用例 ⇒ 探针作用域与用例集不相交 —— 这本身就是警报。
RUNBOOK

exit "$VERDICT"
