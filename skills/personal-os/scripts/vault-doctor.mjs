#!/usr/bin/env node
// vault-doctor.mjs — personal-os 仓库健康检查（Node 版，零依赖）
// 用法：node scripts/vault-doctor.mjs [--dir <vault 路径>]
// 检查：必需文件、AGENTS.md ≤150 行、MEMORY.md ≤100 行、frontmatter、.gitignore、约定目录
import { readFileSync, existsSync } from "node:fs";
import { join, resolve } from "node:path";

const args = process.argv.slice(2);
const dir = resolve(args[0] === "--dir" ? args[1] : args[0] || ".");
let fail = 0, warn = 0;
const ok = (m) => console.log(`  ok   ${m}`);
const bad = (m) => { fail++; console.log(`  FAIL ${m}`); };
const w = (m) => { warn++; console.log(`  warn ${m}`); };
const lines = (p) => readFileSync(p, "utf8").split("\n").length;
const hasFrontmatter = (p) => readFileSync(p, "utf8").startsWith("---\n");

console.log(`vault-doctor (node): ${dir}`);

for (const f of ["AGENTS.md", "CLAUDE.md", "PROFILE.md", "MEMORY.md", "STATE.md", "ideas.md", ".gitignore"]) {
  existsSync(join(dir, f)) ? ok(f) : bad(`缺失 ${f}`);
}
const ap = join(dir, "AGENTS.md");
if (existsSync(ap)) {
  const n = lines(ap);
  n <= 150 ? ok(`AGENTS.md ${n} 行`) : w(`AGENTS.md ${n} 行，超过 150 行建议精简`);
}
const mp = join(dir, "MEMORY.md");
if (existsSync(mp)) {
  const n = lines(mp);
  n <= 100 ? ok(`MEMORY.md ${n} 行`) : w(`MEMORY.md ${n} 行，超过 100 行建议折叠旧条目`);
}
for (const f of ["PROFILE.md", "MEMORY.md", "STATE.md"]) {
  const p = join(dir, f);
  if (existsSync(p)) hasFrontmatter(p) ? ok(`${f} 有 frontmatter`) : w(`${f} 缺 frontmatter`);
}
const gi = join(dir, ".gitignore");
if (existsSync(gi)) {
  /secret/i.test(readFileSync(gi, "utf8")) ? ok(".gitignore 覆盖 secret") : w(".gitignore 未提及 secret");
}
for (const d of ["memory/daily", "decisions", "projects", "people", "references", "data", "skills"]) {
  existsSync(join(dir, d)) ? ok(`目录 ${d}/`) : w(`缺目录 ${d}/（可选）`);
}

console.log(fail ? `\n${fail} 项 FAIL，${warn} 项 warn` : `\n通过（${warn} 项 warn）`);
process.exit(fail ? 1 : 0);
