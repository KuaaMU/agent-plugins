---
name: adaptive-mission
description: >-
  Minimal-plan, drift-tolerant workflow for long engineering and research missions
  (competition operator dev, hardware bring-up, AI platform integration, multi-week
  delivery): clarify direction first, advance through 3–5 checkpoints with exit evidence,
  re-check the spec/acceptance criteria against the latest version every round; manage
  state, fact sources, disposable plans, and acceptance evidence with lightweight
  STATE/TRUTH/PLAN/REVIEW records; enable Driver/Specialist/Reviewer/Guard subagents
  on demand; only the real environment counts as done. For specs that may change every
  few days, where details can't be frozen early. Model-invoked: auto-loads when a task
  is expected to span days/rounds or its spec/acceptance criteria may change.
---

# Adaptive Mission

## Core principles

- Plans are tools, not contracts: keep only the direction, 3–5 checkpoints, and each
  checkpoint's exit evidence. Details solidify only where requirements are stable.
- Fact sources are living: re-check the spec, acceptance criteria, interfaces, and
  environment facts at every checkpoint; update TRUTH.md; never carry stale assumptions
  from an old plan.
- State persists, plans are disposable: maintain STATE.md, TRUTH.md, REVIEW.md;
  PLAN.md may be thrown away and rewritten at any time.
- Doing and judging are separate: an independent Reviewer signs off after each round.
  Any "I think it's done" is not evidence.
- Only the real environment counts as done: simulations, dry runs, and unit tests are
  process evidence, not acceptance evidence.
- Stop-loss: 3 consecutive failed approaches on the same problem → stop grinding in place,
  switch paths or ask the user, and write a BLOCKED record.

## Kickoff clarification (under 10 minutes)

1. Read the spec, user-provided links, existing code and resources.
2. Extract four things: goal, acceptance criteria, constraints, deliverables. Record the
   source and version time for each key fact.
3. Write PLAN.md: 1–2 sentences of direction + 3–5 checkpoints + each checkpoint's evidence.
4. Initialize STATE.md, TRUTH.md, REVIEW.md.
5. No detailed task list. Details grow naturally as you go.

## Cadence: clarify → build → deliver

Every round is the same three-loop, no fixed phases:

1. Clarify: re-read the latest spec/acceptance criteria, diff against last round; update
   TRUTH.md; if direction or acceptance changed, update PLAN.md first, then continue.
2. Build: work only the current checkpoint. Write outputs, logs, and data into the workspace;
   record progress in STATE.md. Don't patch the old plan just to "keep it complete."
3. Deliver: produce the current deliverable; have the Reviewer independently accept it per
   references/review-rubric.md; write conclusions and evidence into REVIEW.md. Pass → next
   checkpoint; fail → back to build for the shortest fix.

End every round back at clarify: assume the spec changed every two or three days until
you've checked and confirmed it didn't.

## Minimal assets

- STATE.md: current checkpoint, done/in-progress/blocked, last checkpoint, BLOCKED records
  (problem, approaches tried, why they failed, new path).
- TRUTH.md: facts, source links or doc paths, versions or dates, last check time.
  Record contradictions first, then decide what to do.
- PLAN.md: direction + checkpoints + evidence. Deletable and rewritable anytime.
- REVIEW.md: each round's Reviewer verdict, evidence list, unresolved risks.

## Responding to requirement drift

- Acceptance criteria changed: don't force-complete the old plan. Update TRUTH.md and
  PLAN.md first, confirm the new direction with the user, then continue.
- Acceptance criteria contradict each other: write the contradiction into STATE.md/TRUTH.md,
  continue with the best-evidenced version, and request confirmation.
- Fact source expired: re-check and record the time. Don't make key decisions on expired facts.
- Platform/tool/dependency updates: run a minimal smoke test before migrating; record in TRUTH.md.

## Subagents on demand

Enable only when the round genuinely needs them — not to "look professional":

- Driver: main-line execution, owns the current checkpoint.
- Specialist: hard-problem discussion, domain research, option design; outputs options and trade-offs.
- Reviewer: independent acceptance; works from evidence and exit criteria only, never from the implementer's conclusions.
- Guard: checks safety boundaries, irreversible operations, and preconditions before real-environment actions.

Usage, prompt templates, and isolation rules: references/roles-subagents.md.

## Acceptance & evidence

- Accept with the P0/P1/P2 tiers from references/review-rubric.md.
- Exit evidence first: real-environment run logs, result data, regression comparisons,
  screenshots/recordings, reproducible commands.
- Dry runs/simulations/unit tests are process evidence — useful for debugging, never a
  substitute for real-environment acceptance.
- When the Reviewer rejects: record the specific gap, go back to build, take the shortest path.

## Reference files

- references/checkpoints.md: checkpoint design, exit evidence, drift response.
- references/roles-subagents.md: Driver/Specialist/Reviewer/Guard roles and prompt templates.
- references/review-rubric.md: P0/P1/P2 acceptance checklist and customizable template.
- references/reference-ingestion.md: distilling links/docs into versioned TRUTH facts.
- references/dual-tool-split.md: Claude Code + Codex dual-tool split, telemetry, stop-loss.

## Boundaries

This playbook is domain-agnostic. Hardware specifics (CANN operators, embedded bring-up, etc.)
come from a dedicated environment skill; this skill owns only process, evidence, and drift management.
