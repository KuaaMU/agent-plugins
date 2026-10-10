---
name: long-horizon-skills
description: >-
  Anti-failure + execution system for hard numeric targets (pass rate/latency) over
  multiple weeks: six failure classes (framework lock-in / self-confirmation bias /
  goal drift / dead apparatus / gate-semantics drift / evidence-strength mismatch),
  task anchoring, evidence ledger (CLAIMS.jsonl + linter), apparatus gate (probe
  liveness checks), failure-set merging with stall triggers, exhaustion triggers,
  upstream recon, independent auditor, JSON state machine (state.json + sparse patches)
  with dual-track Markdown ledgers, racing discipline, file-hygiene discipline,
  hard-set, and profile mechanism. Triggers: hard numeric target spanning days/weeks,
  ≥5 experiments each touching production code, taking over someone else's unfinished
  tree, existence of external reference implementations. Model-invoked: auto-loads when
  any trigger condition hits.
---

# Long-Horizon Assault: Anti-Failure Protocol + Execution Loop

> This skill solves "engineering assaults with a hard numeric target, iterating over days/weeks."
> What it prevents isn't "lack of effort" but **six classes of "looks-like-normal-progress" failure**:
> framework lock-in / self-confirmation bias / goal drift / dead apparatus / gate-semantics drift /
> evidence-strength mismatch.
> "Dead apparatus" is the stealthiest: an experiment that **never actually ran** produces
> well-formatted records with tidy numbers — while every conventional discipline passes.

## 0. When to load · Framework notes · How to use

### 0.1 When to load (any two)

- The goal is a **hard numeric target** (e.g. pass rate `N/N`, latency ≤ X), spanning days/weeks;
- Expecting **≥ 5 experiments**, each touching production code;
- Continuing on **someone else's existing code** (taking over, inheriting, or your own tree from a previous round);
- **External reference implementations** exist (upstream PRs, competitor commits, reference libs);
- Failure is expensive: rework, drift, and forgetting all waste large amounts of time.

### 0.2 Framework notes: why two layerings but only one is used

This skill's L0/L1/L2/L3 are divided by "**when it enters context**" (following the actual
loading model of Claude Code / Codex-class agents: only the description is resident, the body
loads on invocation, references/ and scripts/ load or run on demand). There's an alternative
L0–L4 divided by "abstraction level" (first principles → decision framework → process →
checklist → scripts) — **the two are orthogonal, don't force-fit them**.
This skill takes the former as its skeleton: first principles don't get their own layer but sit
at the top of L1 as the "decision foundation" (§0.4); abstraction-level details (gate checklists,
scripts) enter L2 / L3 by "when used."

| Layer | When it enters context | Contains | Carrier | Budget |
|---|---|---|---|---|
| **L0 trigger** | Resident | name + description: when to use | frontmatter | ≤ 300 chars |
| **L1 operations** | On invocation | **§0.4 decision foundation** · §1–§15 **rule index** (one line each) · per-round loop checklist · tool entries | this file's body | ≤ 250 lines |
| **L2 deep read** | On demand | Full text of each rule (with its **real cost**) · failure catalog · templates · schemas | `references/*.md` | on demand |
| **L3 execution** | On invocation | Seven tools; each proves it fires | `scripts/` | 0 (never enters context) |

**Three key conventions**:

1. **L1 is an "index," not "the rules themselves"** — one line each, e.g.
   `4.6 Before a run, write down "if this works, how will the failure set change?"`
   One scan tells you which L2 entry to read; **don't read everything**.
2. **Rule numbers (`§4.6` / `G3`) are cross-file primary keys** — cite by number only,
   **never restate the text**.
3. **Authoritative text lives in L2**. When the L1 index conflicts with L2, L2 wins.

### 0.3 How to use (three paths)

| Where you are | Read | Produce |
|---|---|---|
| Just got the task brief | `references/asset-index.md` §4 "from brief to first experiment" | `TASK_ANCHOR.md` + `CLAIMS.jsonl` + `state.json` |
| Each experiment round | §11 loop; read L2 entries the index points to, on demand | state patch + ledger entries |
| Before declaring done | §9 completion criteria + §8 independent auditor | verbatim criteria restatement + measured-value comparison |

### 0.4 Decision foundation (five first principles)

Every rule below is one of these five expanded for a concrete scenario; on conflict, come back here.

- **G1 Evidence over memory**: conclusions that change decisions must trace back to reproducible
  evidence; state belongs to files, not to context.
- **G2 Acceptance criteria are the only anchor**: write down the goal, acceptance criteria,
  constraints, and droppables first; when criteria change, re-verify all old conclusions —
  never swap criteria silently.
- **G3 Attribution before modification**: locate the critical path / failure mechanism first, then run
  minimal, single-variable, falsifiable experiments; never run "don't know why it's slow, let's just
  change something" experiments.
- **G4 Generalization before special cases**: prefer structural, cross-case solutions; forbid piling
  special cases per test (allowlist creep is a local-optimum trap).
- **G5 Failure must have a price**: every candidate has a kill line; consecutive failures must change
  paths, never just retune parameters.

## 1. Task anchoring — rule index (see `references/rules-ch1-anchor.md`)

- `1.1` An inherited framework is a hypothesis, not a given; if you can't answer "why does it
  compute this shape?" mark it unverified.
- `1.2` Force re-anchoring every ≤5 experiments or 24h: rebuild from raw evidence without reading
  old summaries; if you can't write "falsifying experiment + where to go if falsified" ⇒ it's faith, not a hypothesis.
- `1.3` Read the measured object itself (case-generator / case-table source text) before modeling.
- `1.4` Every unverified assumption must bind to a scheduled falsifying experiment; if you can't
  schedule it, test it on the spot or explicitly accept it.
- `1.5` The anchor doc has a machine form: `state.json` is the one object read every round;
  sparse patches, `null` deletes keys.
- `1.6` Criteria, cases, and acceptance scripts are measured objects too; ★ run the reference
  implementation through the same gate as the system under test.

## 2. Evidence ledger — rule index (see `references/rules-ch2a-ledger.md` + `rules-ch2b-structures.md`)

- `2.1` Numbers carry four elements before entering conclusions: value / defining formula / unit /
  source; comparisons state A relative to B.
- `2.2` Compared numbers must have subjects; bare "+40%" is forbidden.
- `2.3` Never cite your own old summaries as evidence; re-read raw logs/CSVs/source.
- `2.4` Metrics with unverified dimensions don't count as evidence (defining formula? units? can it exceed 1?).
- `2.5` Derived docs inherit evidence level, never upgrade it; `CLAIMS.jsonl` ledger +
  `claims_lint.py` six mechanical checks; entries are never deleted, only invalidated;
  derived_from required on entries without an evidence path.
- `2.6` Verify the readable time window before citing external implementations; existence claims
  name the repo and path verified; negative conclusions need two independent channels.
- `2.7` Decisive external artifacts get persisted on sight (source file + hash + ledger registration).

## 3. Apparatus gate — rule index (see `references/rules-ch3-apparatus.md`)

- `3.0` Discriminability check: in the worst case (it didn't run / doesn't exist / failed), would the
  output look exactly like success? If yes ⇒ zero discriminability.
- `3.1` Probes don't count as evidence until proven live (`probe_liveness.sh` or the four cheap
  methods: behavioral / kernel-name / differential cases — differential preferred).
- `3.2` Measured two-arm difference smaller than structural difference ⇒ suspect the probe first.
- `3.3` The control arm proves reproducibility, not validity.
- `3.4` A green light proves "the path taken was correct," not "which path was taken";
  performance gates don't validate numbers.
- `3.5` "Do less work" probes must pre-register their claim and pass the accuracy gate first.
- `3.6` Can't prove liveness ⇒ mark `INVALID`, never `refuted`.
- `3.7` Under concurrency, "device idle" is not a mutex criterion — locks are; short tasks never
  queue behind long ones.

## 4. Failure merging & stall triggers — rule index (see `references/rules-ch4-counting.md`)

- `4.1`/`4.2` "3 tactics = 1 architecture" and "stop at 2 cumulative architectures" are calibrated
  values, not derived ones — rough heuristics only.
- `4.3` **Stall trigger**: the same failing-case group unmoved for 3 consecutive rounds
  (members + gap) ⇒ counts as 1 framework failure.
- `4.4` After every experiment, copy down the failure set (name each case).
- `4.5` Before a run, write "if this works, how will the failure set change?"; changes with no
  information content don't run.
- `4.6` **Magnitude extrapolation**: extrapolate by the average shrink of the last k rounds;
  if it can't arrive within budget ⇒ the path is unreachable (the only trigger that doesn't
  require self-doubt first).

## 5. Exhaustion triggers — rule index (see `references/rules-ch5-exhaustion.md`)

- `5.1` Busy-pipe >95% + actual issued work == algorithmic lower bound + all structural items
  excluded ⇒ micro-leverage experiments forbidden; only family switches or benchmarking allowed.
- `5.2` "This path is exhausted" ≠ "this problem is unsolvable" — one "change the shape" action apart.
- `5.3` `blocked` is a state, not a decision; terminating requires three things: restart
  conditions / takeover path / handoff recipient.

## 6. Upstream recon — rule index (rules in `references/rules-ch6-recon.md`, method guide in `references/upstream-recon.md`)

- `6.1` The critical path must not pass through "possibly nonexistent external artifacts."
- `6.2` Sources ranked by availability: sibling operators > own A/B on adjacent shape segments >
  upstream docs > competitor commits; two mandatory points (day 0 / first case failure).
- `6.3` A neighbor's existence proof is evidence; "not applicable" needs evidence too, otherwise
  it's an unverified assumption.
- `6.4` Tiers should be derived (capacity/bit-width constraints); hand-tuned tables are tech debt.
- `6.5` Benchmark numbers go through §2 and §3 as well (subjects complete, same reference).

## 7. Self-falsification — rule index (see `references/rules-ch7-self-falsify.md`)

- `7.1` Every re-anchoring must answer: which old conclusion is least certain, and what evidence
  would overturn it.
- `7.2` Conclusion labels, only four: `measured` / `independently reviewed` / `unchallenged` /
  `INVALID`; anything you haven't challenged yourself can only be `unchallenged`.
- `7.3` When new evidence overturns an old conclusion, edit the old doc with a correction banner —
  no silent replacement; check whether derived docs copied the overturned conclusion.

## 8. Independent audit — rule index (see `references/rules-ch8-audit.md`)

- `8.1` The main attacker never audits themselves; an independent context does the audit;
  only new evidence — not tone — overturns conclusions; the auditor must report what they retracted.
- The auditor reads raw data, not summaries; actively hunts counterexamples; checks item by item:
  comparison subjects, probe liveness, ledger derived_from completeness and invalidation
  propagation (run `claims_lint.py`, don't eyeball it).

## 9. Completion criteria — rule index (see `references/rules-ch9-completion.md`)

- `9.1` Declaring done requires restating the acceptance criteria verbatim with measured-value
  comparison; of "achieved" / "close" / "not achieved," only the first may be used.
- `9.2` Wind-down rules for noisy criteria must be written and approved before the finish line;
  you may improve the estimator, never relax the semantics.
- `9.3` High pass counts ≠ correct; before claiming "close," confirm it was achieved on a
  numerically correct kernel.

## 10. State mechanism — dual track (see `references/state.md` + `state-files.md`)

- **Machine track**: `state.json` is the single object read every round (fixed schema + sparse
  patches + validation gate, see `references/state-schema.md`); `CLAIMS.jsonl` is the evidence
  source of truth (replaces prose TRUTH).
- **Human track**: `STATE.md` (current snapshot view), `CANDIDATES.md` (candidate ledger),
  `PLAN.md` (checkpoints), `REVIEW.md` (independent review verdicts), `METRICS.md` (scoreboard),
  `HANDOFF.md` (recovery path), `HARDSET.md` (hard set), `EVENTS.md` (incremental log).
- **Contract**: JSON is the source of truth, Markdown is the derived view; each fact has exactly
  one authority, everywhere else cites by number (`2.5.3`).

## 11. Per-round loop — rule index (see `references/round-loop.md`)

Each round executes exactly one highest-value loop, in two layers:

- **Outer loop (task round)**: re-anchor → read `state.json` → classify → verify baseline → attribute →
  falsifiable candidate → layered verification → gate verdict → decide (promote/iterate/revert/park/close) →
  persist (state patch + ledger) → racing retro point.
- **Inner loop (experiment round)**: hypothesis → pre-register → check environment/locks →
  **apparatus gate** → accuracy gate → performance gate → controlled measurement → six-way conclusion →
  archive failures first → copy failure set → submit state patch → update ledger.
- Escalate to the user only on: acceptance-criteria conflict / irreversible high-cost operations /
  missing goal resources / consecutive failures requiring a goal change — with: current goal,
  verified facts, closed routes, minimal request, default recommendation.

## 12. Racing discipline — rule index (see `references/racing.md`)

- `12.1` Race multiple candidates with git worktree (zero cost on one machine); scarce hardware
  goes to the finals only.
- `12.2` Every N rounds (5 recommended), force a scoreboard review and kill laggards; the killed
  leave behind their failure family and reopen conditions.
- `12.3` A new agent's first discipline: verify, don't trust (recompute hashes, re-run minimal
  smoke before continuing an old route).

## 13. File-hygiene discipline — rule index (see `references/file-hygiene.md`)

- `13.1` Directory contract: `mission/` holds only the fixed file list; experiment artifacts go to
  `scratch/<candidate-id>/`, archived/deleted when the candidate closes; `research/` files must
  carry a "source + date + one-line conclusion" header.
- `13.2` Search quota: each round's web search/scraping has a cap; when `research/` overflows,
  digest first, no new searches; tool downgrade chain: official docs/API > curl > scraper > browser automation.
- `13.3` Remote isolation: SSH remotes run code only, never notes; fetch back evidence files only;
  clear the remote workspace when the task ends.

## 14. Hard set — rule index (see `references/hard-set.md`)

- `14.1` Admission: ≥2 structural routes tried and still failing, conventional optimization yields
  only single-digit gains, unusual failure mechanism ⇒ moves to `HARDSET.md` under independent
  management; excluded from daily scoring.
- `14.2` Breakthroughs allow structural experiments only (change algorithm/layout/execution
  structure); parameter sweeps forbidden.
- `14.3` N consecutive rounds (5 recommended) with only single-digit overall gains and an unmoved
  hard set ⇒ stop parameter tuning, force a new algorithm family, validate on the hard set first.

## 15. Profile mechanism

Core is domain-agnostic and model/harness-agnostic (declarative: what to accept, not which button
to click). Domain specifics sink into `references/profiles/<name>.md` (plus optional
`<name>.tools.json`), loaded on demand. Example: `profiles/ascend-cann.md` (numeric gate details,
NPU optimization playbook, official tool list) — proof that "domain-agnostic" isn't empty talk.

## Tools (L3)

| Script | Role | Usage |
|---|---|---|
| `init_mission.py` | **Scaffolding**: create mission dir and templates | `--mission/--goal/--acceptance [--profile]` |
| `mission_lint.py` | **Scaffolding**: structural lint (missing files/placeholders/stale HANDOFF/scratch orphans/research overflow) | `<mission>`; nonzero exit means problems |
| `discover_environment.py` | **Scaffolding**: read-only environment discovery (profile-driven) | `[--profile]` |
| `new_candidate.py` | **Scaffolding**: register a falsifiable candidate | interactive or args |
| `state_patch.py` | **State**: read/write `state.json` sparse patches | `--state/--patch/--show`; `--self-test` |
| `claims_lint.py` | **Evidence**: six mechanical checks on `CLAIMS.jsonl` | `--ledger [--doc]... [--strict]`; `--self-test` |
| `probe_liveness.sh` | **Evidence**: structural probe-liveness check | `--src/--func/--probe/--target`; exits 0/1/2 |

One line per role: **scaffolding owns "what the task looks like," state/evidence tools own "what the world looks like."**
Tooling itself is bound by this protocol: before a criterion ships, it must pass both a
"known-should-fail" and a "known-should-pass" sample.

## Independent auditor

Role definition: `agents/long-horizon-auditor/AGENT.md` (duties in §8).
`agents/openai.yaml` is the entry point for Codex-class agents.
