**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: cost per result and rework rate, before the first figure (2026-11-17)

Written before any figure below was computed. Steer:
`docs/staging/advisor/done/DIRECTOR_STEER_COST_PER_RESULT_AND_REWORK_RATE_FOR_THE_MACHINE_NOT_FOR_THE_DIRECTOR_2026-11-17.md`.

## What a result is (fixed from today; a change to it is a dated amendment here, never a silent edit)

Three distinct experiences, measured apart and never summed:

- **staging_closed**: a landed commit moves a file out of the `docs/staging/` root into
  `docs/staging/done/`. One file is one result.
- **level_move**: a landed commit appends a row to `docs/observability/gate_authorizations.jsonl`.
  One appended row is one result.
- **steer_done**: a landed commit moves a file from `docs/staging/advisor/` into
  `docs/staging/advisor/done/`. One file is one result.

The cost of a result is the cost of the sessions that landed it, read from Claude Code transcripts
and priced by `tools.tick_burn_rate`. A session that lands several results splits its cost equally
across them. Spend by sessions that landed no result is published beside the figure as its own share,
and is never spread over the results. That is the flattering-definition guard: small items cannot
lower the figure by hiding the cost of the sessions that produced nothing.

## What rework is

A landed non-merge commit on `origin/main` that changes code (`*.py` outside `tests/`) is
**reworked** if any line it added is changed or deleted by a later trunk commit within 14 days
(`git blame --reverse`). A commit is counted only once its 14 days have passed. The rate is
reworked commits over code commits, published with a Wilson 90% bound. The share of added lines
changed is published beside it.

Known over-count: this cannot tell a correction from a follow-up planned in the result's own
done-test (the steer's exclusion), from a reformat, or from a sibling step in the same planned
chain. The figure is therefore an upper bound on rework, and is read for its trend and for which
kind of work it falls in, not for its level.

## Predictions (before the first computation)

- **Rework**, for code commits from 27 Oct to 3 Nov: commit share 35% (would not surprise me between
  20% and 55%); line share 10% (between 4% and 20%). Harness code (`background/`, `tools/`) will
  rework more than world code (`sim/`, `simulation/`).
- **Cost per result**, last 7 days: steer_done costs more per result than staging_closed. More than
  30% of the week's spend is in sessions that landed no result.

## Result (added after the run; everything above was written first, sha256 e3e3504e…5ad at 06:28Z)

`python3 -m tools.work_cost_estimate --results`, run 17 Nov about 07:10Z.

**Rework, the pre-registered week (27 Oct to 3 Nov):** 126 code commits, 60 reworked: **48% (90% bound
40–55%)**. Line share **6%**. Harness 28 of 52 (54%), supplier 18 of 37 (49%), world 12 of 31 (39%).
- Commit share: predicted 35%, **missed** the point but sits inside the stated range (20–55%), at its top.
- Line share: predicted 10%; the result is inside the 4–20% range, below the point.
- Harness above world: **held**.
- **Read:** about half of code commits have at least one line changed within 14 days, but only about
  one line in twenty is. Most rework is a small touch-up to an otherwise kept change. The rate is flat
  across the four weeks read (46–50%, bounds overlapping), so no kind of work has a rising trend yet.
  Spot-checked both ways. 5654fa2e7f counted as reworked, and its lines really were changed: a second
  lane had landed the same fix a minute earlier as 58d49405e2, and both were later moved into a helper.
  87a83c4300 counted as untouched, and its three lines really were.

**Cost per result, last 7 days:** staging_closed 0.22 points (0.18–0.27, n=29), level_move 0.20
(0.17–0.24, n=9), steer_done 0.18 (0.13–0.22, n=53).
- **No-result share 86%** (72–86% across four weeks). Predicted more than 30%: **held, by far**.
- steer_done above staging_closed: **not held**. It was lower this week and level in two of the
  three weeks before; the bounds overlap.

**Two corrections made before the first figure was published.**
- **Double counting.** The first cost pass summed spend per session, and read 245 points for a week
  that `tick_burn_rate.weighted_usd_between` puts at 87. Forked and resumed transcripts carry their
  parent's messages under the same ids. Spend is now priced once across all transcripts (by the
  transcript that started first) and matches the burn total to the decimal.
- **What the 86% is not.** It is not 86% wasted. A result reaches this figure only if the session's
  own tool output carries a `[surgical-land] landed` line. Spend is therefore missed in three cases:
  - a landing done by a systemd long job (D5 has landed through nine), because the launching
    session never sees the line;
  - work that is not one of the three result kinds (code fixes, findings, records);
  - the gate and orientation turns that end in no commit.

  So the share is an upper bound on spend that produced nothing. The first act on it is to attribute
  long-job landings to the session that launched them (backlog row E-r2), not to cut work.

**What the machine does with it now.** Rework is flat, so there is no autonomy change. The
efficiency backlog gains E-r (the two lines, KEEP as instruments) and E-r2 (long-job attribution).
Nothing is raised to the director: no strategic implication yet.
