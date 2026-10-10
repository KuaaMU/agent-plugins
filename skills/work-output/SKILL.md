---
name: work-output
description: >-
  Distill a task's process into four-track work outputs: task-track deliverables and
  evidence, process-track reproducible commands and failure records, reuse-track
  skills/templates/lessons, public-track case drafts/articles/open-source repos/training
  corpora. Use at the wrap-up of any engineering, research, or creative task to generate
  layered briefs (one-liner / five lines / evidence appendix), maintain OUTPUTS.md and
  LEARN.md, and publish distillations through a de-identification + licensing gate;
  the public track can produce case drafts, accumulate trajectories into a structured
  episode backlog, and proactively propose publications on schedule (final publishing
  still needs user approval). User-invoked: explicitly invoked by the user at task
  wrap-up when outputs need distilling.
disable-model-invocation: true
---

# Work Output

## Core stance

- Outputs are byproducts, not extra labor: distill what you'd produce anyway (commands,
  logs, diffs, decisions, failures) — don't manufacture files to "look productive."
- Outputs follow the problem: each output answers a question, with an as-of time, the
  assumptions at the time, and evidence. The world changes; outputs record "why we did
  it this way back then."
- Four tracks, layered: task track (delivery), process track (reproducible), reuse track
  (self-feedback), public track (world value). Secure the first two before talking about
  the last two.
- Layered readability: one-liner → five-line summary → evidence appendix. A user who only
  owns the project reads the five lines; dig into the appendix for depth.
- Publishing has a gate: de-identification, licensing, reproducibility, and no-hype checks
  before anything goes public.

## Kickoff

1. Create OUTPUTS.md: four-track sections + publication TODO + next-round questions.
2. Create LEARN.md when there's reusable experience; leave it empty until then.
3. Write the task goal, acceptance criteria, and key links at the top of OUTPUTS.md
  (reference TRUTH.md, don't copy it).

## End of each checkpoint/round (5-minute distillation)

Write three things:

- New facts: update TRUTH.md (source + version + check time).
- New lessons: write into LEARN.md as "next time I meet X, try Y first, because the evidence is Z."
- Public candidates: write into OUTPUTS.md's public track, marked: draft / publishable / won't-publish.

Don't wait until the task ends; evidence and lessons expire fastest.

## Layered briefs

At every delivery, or whenever the user asks for progress, output three layers:

1. One-liner conclusion.
2. Five-line summary: problem, decision, evidence, risks, next steps.
3. Evidence appendix: reproducible commands, outputs, file paths, failure records.

Template: references/layered-brief.md.

## The four tracks

- Task track: deliverables + exit evidence — what the user accepts.
- Process track: reproducible commands, environments, failures and BLOCKEDs, rollback paths — feeds back into yourself.
- Reuse track: LEARN entries, skills, templates, prompts, checklists — solidify once enough accumulates.
- Public track: case drafts, articles, open-source repos, structured episode backlogs — must pass the publication gate.

Details and checklists: references/four-tracks.md.

## Case drafts (public track)

When OUTPUTS.md's public track has a "publishable" candidate and the user signals intent
to show work externally, produce a case draft:

- Goal: turn one task into a tellable story, not a structured list.
- Contents: title, abstract, background problem, approach and trade-offs, evidence and results,
  lessons, links, de-identification statement.
- Rules: at most one flagship case per project; a draft is not published — publishing still
  requires the publication gate; never auto-write by default.

Template: references/case-study.md.

## Structured episodes (training-corpus candidates)

At task wrap-up, organize the trajectory into an episode:
goal → context (TRUTH facts) → actions (command/decision trail) → evidence →
reflection (result labels + lessons).

Only organize high-quality, de-identified, licensed episodes; raw chat logs never become corpora directly.

Register every episode in the EPISODES.md backlog index, default training_usage=not-allowed;
once enough accumulates (or on schedule), bundle into a licensed dataset repo — confirm
authorization and de-identification per episode before publishing.

Format and examples: references/episode-format.md; accumulation rules: references/episode-backlog.md.

## Proactive maintenance & publication proposals

Don't only distill at wrap-up — actively maintain at these points:

- Each checkpoint: update OUTPUTS.md / EPISODES.md statuses.
- Task milestones: acceptance passed, open-sourced, dataset reached N episodes.
- On schedule: weekly or monthly, review the public track and backlog, promote mature
  candidates into publication proposals.

A publication proposal must include: output link, why publish (reach value / timeliness /
completeness), suggested timing (strike while hot / batch / defer), risks
(privacy / hype / maintenance burden). Proposals execute only after user approval;
the agent never publishes on its own.

Rules and templates: references/active-maintenance.md.

## Publication gate

Confirm each item before publishing anything:

- De-identified: no keys, tokens, IPs, serial ports, path leaks, personal info.
- Licensed: explicit MIT/CC-BY etc.; state whether training use is allowed.
- Reproducible: commands and data repeat, results not exaggerated.
- Valuable: one good case beats ten logs; at most one flagship case + one reusable asset per project.
- User approval: proposals execute only after explicit user consent; the agent never publishes alone.

Checklist: references/publication-gate.md.

## Reference files

- references/four-tracks.md: the four-track model and per-track checklists.
- references/layered-brief.md: layered brief template and examples.
- references/distillation-rules.md: checkpoint distillation rules and LEARN writing.
- references/episode-format.md: structured episode schema and examples.
- references/episode-backlog.md: episode accumulation and dataset publishing.
- references/active-maintenance.md: proactive maintenance and publication proposals.
- references/publication-gate.md: pre-publication checklist and licensing.

## Relationship with adaptive-mission

This skill doesn't depend on any particular task process. Used with adaptive-mission,
STATE/TRUTH/PLAN/REVIEW supply facts and evidence while this skill distills them into
four-track outputs; used alone, invoke this skill at any task's wrap-up.
