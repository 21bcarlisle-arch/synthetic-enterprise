# [ADVISOR-REVIEW] — Data architecture and the 10k scale probe (2026-08-05)

**Type:** [FINDINGS + one experiment definition]. Answers the director's question of 2026-08-05: *"Is it in a single database? Do we have a scalable solution for 10k customers? 100k? 1m?"* Computed from the full git tree and direct source reads; no runtime access (machine offline). Refute with evidence where wrong. Feeds NET of `DIRECTOR_PROGRAMME_ARCHITECTED_OUT_2026-08-05.md` (the executable persistence constraint) — this supplies the inventory those checks need, plus the probe. It does not duplicate that programme.

## 1. What the data layer actually is (measured)

**There is no database.** No SQLite, no server DB, no migrations anywhere in the tree. The entire state layer is files:

- **Market ground truth:** large caches (123MB Elexon SSP + AGWS + demand) live on Skynet's disk only — `sim/cache/` has ZERO files in the repo. The repo cannot reconstruct the world without the box, or a re-prefetch.
- **Run truth:** `docs/reports/run_output_latest.json` (4.1MB, ~20 customers, full decade) + 6 historical run outputs kept in-repo (8.5MB total).
- **Money state:** `billing_ledger.json` at 2.4MB — in TWO copies (`docs/state/` and `site/state/`), the known FINDING 2 duplication. Which is written first and which should be derived remains the open question from the structural audit.
- **Published surfaces:** `site/data/` — 22 per-customer JSON files (4.1MB), 9 snapshot files (4.9MB) accumulating without a retention rule.
- **Append logs (.jsonl, 12 files, 11.4MB):** the closest thing to a real event log in practice — decision log, gate authorizations, level-ups. Note **10.7MB of the 11.4 is `naive_organ_log.jsonl`** — one diagnostic organ is 94% of the append-log estate, echoing its duplicate-question flood in LATEST.
- **The `BitemporalEventLog` (read directly): in-memory only.** Append-only discipline is real (copy-on-write/copy-on-read, no mutation), but there is no persistence path in the class — no file, no load/save. The "persistence behind the event-log interface" constraint currently has an event log with no persistence and persistence (JSON files) with no event log. The two halves exist and are not joined.

## 2. Scale arithmetic (linear extrapolation, to be replaced by probe measurement)

~200KB of run output per customer per decade. At **10k customers**: a ~2GB single JSON output (several × that in RAM to build and serialize), ~10k per-customer site files per publish, and run outputs far past any sane git commit. At **100k–1m**: not reachable by degrees from a files-in-RAM shape at all. Independent of output size, the in-run working set (per-customer half-hourly settlement across a decade) plausibly exhausts RAM before serialization is even reached — plausibly, because how much state is truly per-customer versus shared per-profile is exactly what nobody has measured. **The current shape is right for a 20-customer rig and unknown at 10k. Unknown, not doomed — that is what the probe is for.**

## 3. The 10k probe (the experiment — CC designs the mechanism)

**Purpose:** find the FIRST seam that tears, with a number on it. Knowledge is the success criterion — the probe succeeds even if the run dies, provided it dies measurably.

- **Shape:** synthetic 10k-customer book from the existing per-run population draw; instrumented for peak RSS, per-stage wall time, and per-artefact output size. Bounded: start at 1 year × 10k (SIM_FAST_MODE-class truncation) before any decade attempt; hard wall-time cap; canonical files untouched (scratch outputs only, established pattern).
- **Prediction register, written before running (falsifiable, project method):** advisor's ranked guesses — (1) in-run RAM at settlement build, (2) run-output serialization, (3) per-customer site publish, (4) git transport of outputs. The probe confirms or refutes the ranking; a surprise ordering is the most valuable outcome.
- **Explicitly NOT in scope:** any fix, any database or substrate adoption, any schema work. Measure first (R4). Probe findings return to the director before any substrate decision — a storage swap is an architecture door, not a build.
- **Sequencing:** post-restart, ordinary sized draw, non-blocking to current lanes.

## 4. Findings the probe does not need to wait for

- **a. The ledger duplication** (2 × 2.4MB) is the persistence constraint measurably not holding today, at 20 customers. Snapshot-or-fork question stands from the structural audit; if fork, single-writer + derived copy is the shape.
- **b. Snapshot accumulation** (`site/data/snapshots/`, 9 files and growing) has no retention rule — same class as the 4,909-file done/ drawer, smaller.
- **c. Historical run outputs in-repo** (6 files, 4.4MB) — the repo drifting toward being the database. A retention/archive rule belongs with (b).
- **d. The event-log join** — persistence for `BitemporalEventLog` (or an explicit register of why not yet) is the single change that makes the standing constraint true rather than aspirational. Registration-level note only; the build is CC's to sequence.

## 5. Limits of this review

Sizes are from the git tree: local-only artefacts (the big caches, any uncommitted state) are invisible except where named in canon. Runtime memory behaviour is entirely unmeasured — every RAM claim above is arithmetic, not observation. The event-log finding is a source read, not a runtime trace.

— Advisor review, 2026-08-05, prepared while the machine was offline.

## Correction (2026-08-06) — "no SQLite anywhere" was wrong
CCM characterization work (PR #9) surfaced what this review missed: **`company/billing/invoice.py` embeds SQLite** — `import sqlite3`, runtime-created `company/data/invoices.db` (untracked, not gitignored — minor hygiene item), in-repo schema, money-path in-degree 6. The review's method error, named for the record: it checked for database *artifacts* (.db files, migrations dirs) and never grepped for the *capability* (`import sqlite3`) — absence of artifact is not absence of engine. Revised §1 claim: the state layer is files/JSON **except one embedded SQLite store in the invoice path**, which is also the one money store already sitting behind a queryable engine — relevant context for any future substrate discussion. The probe and every other finding stand unchanged.
