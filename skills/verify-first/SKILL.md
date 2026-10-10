---
name: verify-first
description: >-
  Model-invoked verification-discipline micro-skill: before announcing any conclusion
  (done, fixed, faster), run a forced 5-step loop — define what counts as evidence, run
  the real environment, read raw output, check discriminability, actively seek
  counterexamples. Includes a rationalization pre-buttal table. Model-invoked: loads
  when you're about to claim completion, a fix, or an improvement.
---

# Verify First

One sentence: **no assertions, only evidence.**

## Trigger

Before announcing any of these, run the 5-step loop first:
done / bug fixed / performance improved / approach works.

## The loop (5 steps, 2 minutes)

1. **Define evidence**: write down "what would prove it works" BEFORE running.
   Finding evidence after the fact is self-justification.
2. **Run the real environment**: simulations, dry runs, and unit tests are process evidence,
   not acceptance evidence. Acceptance must run in the real environment.
3. **Read raw output**: read the logs/data/screenshots themselves, not your summary.
   Summaries lie; raw output doesn't.
4. **Discriminability check**: ask yourself — if it actually hadn't run / had failed,
   would what I see look any different? If no → this verification has zero discriminability. Redo it.
5. **Actively seek counterexamples**: first think "what evidence would overturn my conclusion,"
   then go find it. Only if you can't, it passes.

## Rationalization pre-buttal table

| Excuse | Pre-buttal |
|---|---|
| "All tests pass" | Unit tests prove process, not acceptance. Did it run in the real environment? |
| "The logs look right" | Looks right ≠ discriminability check. What do the logs look like on failure — compared? |
| "That's how it was done before" | That's historical evidence, not this run's evidence. |
| "No time to verify" | An unverified conclusion is an assertion. Mark it "unverified," don't present it as a conclusion. |

## Relationship with long-horizon-skills

Heavy verification (apparatus gate, probe liveness, evidence ledger, independent auditor) lives in
long-horizon-skills. I'm the lightweight version: any task, any scale, 5 steps in 2 minutes.

## Anti-patterns

- The loop ran but the conclusion was written beforehand → that's theater, not verification.
- Marking "unverified" as "done" → the most serious violation in this repo.
