---
name: router
description: >-
  User-invoked skill router: when you don't know which skill fits the task, invoke me
  and I'll route you. Covers long-horizon-skills (hard numeric targets), adaptive-mission
  (drift-prone long missions), work-output (distilling outputs at wrap-up), personal-os
  (cross-AI memory vault), verify-first (verification before claiming), mentor
  (cognitive-alignment companion). If none fits, I'll say so instead of forcing one.
disable-model-invocation: true
---

# Router

When you don't know which skill fits, invoke me explicitly. Don't use a skill for the
sake of using one — "none fits" is an allowed answer.

## Decision tree

0. About to claim "done / fixed / faster"?
   → Run **verify-first** (5-step verification loop) before announcing.
1. Hard **numeric target** (pass rate, latency) over days/weeks?
   → **long-horizon-skills**
2. Long task, but the **spec/acceptance criteria may change every few days**,
   details can't be frozen early?
   → **adaptive-mission**
3. Task is wrapping up and you want to distill it into briefings, lessons, cases,
   or publishable outputs?
   → **work-output**
4. Want to build a long-term memory/knowledge vault any AI can take over?
   → **personal-os**
5. Both 1 and 2 (hard target + drifting spec)?
   → Start with **adaptive-mission** to set direction and manage drift;
   switch to **long-horizon-skills** for the assault phase.
6. None of the above?
   → Use no skill. Just do the work.
7. Want to truly understand the project while shipping, let AI mentor you?
   → **mentor** (study companion: cross-session reads the main line, never interferes).

## Repo-wide trigger policy

| Skill | Trigger | Why |
|---|---|---|
| router | user-invoked | Routing is an orchestration decision — the user's call; model self-routing picks wrong and burns context |
| work-output | user-invoked | Distilling and publishing are user decisions (what to publish, when to wrap up); the model shouldn't decide alone |
| mentor | user-invoked | What to learn is your active decision; the companion only appears when you need to "understand" |
| adaptive-mission | model-invoked | Long tasks with likely drift should auto-engage; waiting for the user to remember is too late |
| long-horizon-skills | model-invoked | Triggers are objective (hard target / ≥5 experiments / inherited tree); load on hit |
| personal-os | model-invoked | Session-start protocol — every AI should read it before starting work |
| verify-first | model-invoked | Verification is discipline, not orchestration: engages when you're about to claim something, without waiting to be asked |

## Anti-patterns

- **Using a skill for the sake of it**: "none" is a valid router output.
- **Loading two process skills at once**: adaptive-mission and long-horizon-skills never run together —
  phase them per item 5 above.
- **Keeping the router resident**: I appear once when you're unsure "which one," then step back after routing.
