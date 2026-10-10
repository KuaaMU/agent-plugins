---
name: personal-os
description: >-
  Methodology (open source) for a personal data vault: private GitHub repo + AGENTS.md
  cross-AI entry point + markdown, so any AI can seamlessly take over your long-term
  memory, decisions, projects, and ideas. Includes a new-AI onboarding protocol,
  hard session-end sync discipline, memory curation bar (Verified/Reusable/Stable),
  security red lines, and node/sh dual-version vault health-check scripts. The
  methodology is a public good; your data stays private forever. Model-invoked:
  auto-loads at session start (session-start protocol).
---

# personal-os

## Philosophy: three-layer separation

- **Methodology is a public good**: this skill, the AGENTS.md convention, the repo template —
  open source, anyone can use them
- **Data is private property**: your PROFILE / MEMORY / projects / people live only in your
  own private repo, never public
- **Runtime binds to nothing**: the core depends only on `git` + `markdown`, two things everyone
  has; bundled scripts ship in node / shell dual versions with zero third-party dependencies

## Repo template

```
personal-os/              # your private repo (this skill defines the structure, never touches your data)
├── AGENTS.md             # cross-AI standard entry (≤150 lines): reading order, sync discipline, security red lines
├── CLAUDE.md             # bridge: Strictly follow ./AGENTS.md.
├── README.md             # human-facing navigation
├── PROFILE.md            # about you (with YAML frontmatter)
├── MEMORY.md             # long-term memory, target ≤100 lines
├── STATE.md              # current state: what's in flight, what's next
├── memory/daily/         # daily logs YYYY-MM-DD.md
├── decisions/            # ADR-style decision records (0001-xxx.md)
├── projects/            # one directory per project
├── people/               # relationships, one file per person
├── ideas.md              # idea inbox
├── skills/               # reusable skills
├── references/           # saved references
├── data/                 # program-consumed JSON, never hand-written
└── .gitignore            # passwords/keys/plaintext backups never enter the repo
```

## New-session startup protocol (any AI)

1. `git pull --rebase` (clone first if missing)
2. Read in order: `AGENTS.md` → `PROFILE.md` → `MEMORY.md` → `STATE.md`
3. Read on demand: `projects/`, `decisions/`, `people/`, `ideas.md`, today's daily
4. Don't read the whole repo; don't guess at what you haven't read

## Sync discipline (hard rules)

- **A task isn't done until memory is updated.** Retrieval can only find what's written down;
  writing is the only bottleneck
- After every substantive piece of work: `git pull --rebase` → update `memory/daily/YYYY-MM-DD.md`
  → curate `MEMORY.md` → record important decisions in `decisions/` → update `STATE.md` →
  commit → push
- Commit format: `memory: …` / `docs: …` / `decision: …`
- No "I'll write it later"; sync before the session ends

## Memory curation

- Admission bar (all three required): **Verified** / **Reusable** / **Stable**;
  anything missing one goes to daily, not MEMORY.md
- Keep: preferences, decisions, commitments, relationships, verified conclusions, lessons from failures;
  don't keep: procedural details, tool-call traces, unverified rumors
- Edit: precisely edit the matching entry and date it; never leave contradicting old text behind

## Security red lines

- Passwords, API keys, tokens, private keys **never enter the repo**
- Videos, images, and other large files don't enter the repo — index only
- Glance at `git status` before every push

## Scripts (node / shell dual versions, zero dependencies)

- `scripts/vault-doctor.mjs` — `node scripts/vault-doctor.mjs [--dir <vault>]`
- `scripts/vault-doctor.sh` — `bash scripts/vault-doctor.sh [<vault>]`

Checks: required files present, AGENTS.md ≤150 lines, MEMORY.md ≤100 lines, key files have
frontmatter, .gitignore covers secrets, conventional directories exist. FAIL exits 1.
