#!/usr/bin/env bash
# vault-doctor.sh — personal-os 仓库健康检查（Shell 版，零依赖）
# 用法：bash scripts/vault-doctor.sh [<vault 路径>]
# 与 scripts/vault-doctor.mjs 同等检查项
set -u
DIR="${1:-.}"
fail=0; warn=0
ok()   { echo "  ok   $1"; }
bad()  { fail=$((fail+1)); echo "  FAIL $1"; }
w()    { warn=$((warn+1)); echo "  warn $1"; }

echo "vault-doctor (shell): $DIR"

for f in AGENTS.md CLAUDE.md PROFILE.md MEMORY.md STATE.md ideas.md .gitignore; do
  [ -f "$DIR/$f" ] && ok "$f" || bad "缺失 $f"
done

if [ -f "$DIR/AGENTS.md" ]; then
  n=$(wc -l < "$DIR/AGENTS.md")
  [ "$n" -le 150 ] && ok "AGENTS.md $n 行" || w "AGENTS.md $n 行，超过 150 行建议精简"
fi
if [ -f "$DIR/MEMORY.md" ]; then
  n=$(wc -l < "$DIR/MEMORY.md")
  [ "$n" -le 100 ] && ok "MEMORY.md $n 行" || w "MEMORY.md $n 行，超过 100 行建议折叠旧条目"
fi
for f in PROFILE.md MEMORY.md STATE.md; do
  if [ -f "$DIR/$f" ]; then
    head -1 "$DIR/$f" | grep -q '^---$' && ok "$f 有 frontmatter" || w "$f 缺 frontmatter"
  fi
done
if [ -f "$DIR/.gitignore" ]; then
  grep -qi secret "$DIR/.gitignore" && ok ".gitignore 覆盖 secret" || w ".gitignore 未提及 secret"
fi
for d in memory/daily decisions projects people references data skills; do
  [ -d "$DIR/$d" ] && ok "目录 $d/" || w "缺目录 $d/（可选）"
done

if [ "$fail" -gt 0 ]; then echo; echo "$fail 项 FAIL，$warn 项 warn"; else echo; echo "通过（$warn 项 warn）"; fi
exit $(( fail > 0 ? 1 : 0 ))
