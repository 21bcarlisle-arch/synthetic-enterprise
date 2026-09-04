**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION — what the one-variable arm must return if the departure anchor is what moved net margin

**Filed:** 2026-09-04, before either arm had produced a JSON. The two runs were launched in the same
minute this file was written; each takes ~12 minutes, so no result existed when the predictions
below were fixed. **Graded in this file, in place.**

---

## The move being attributed

The first publish after the twelve-hour outage carried a net margin **£11,003 lower** than the last
publish before it:

| | last publish before the outage | first publish after |
|---|---|---|
| publish commit | `a298e7a9f` | `2b6decd4c` |
| code the run executed at | `9c1c24f76` | `79af956b1` |
| run artefact | `run_output_9c1c24f76_20260903T055708Z.json` | `run_output_79af956b1_20260903T175542Z.json` |
| **`total_net_gbp`** | **149,156.20** | **138,152.77** |

Eighty commits separate the two runs. **Two of them touch anything the simulation executes**:
`712ae5323` and `8242dcc25`, both re-fits of `simulation.departure_level_anchor.YEAR_LEVEL_ANCHOR`.
The only other behavioural-layer change in the window is `+28` purely additive lines in
`simulation/market_switching_propensity.py` (`published_departure_band`, a read accessor) and three
docstring/accessor commits on the anchor module itself (`a7b161469`, `dda5a27b2`, `2927fdba5`).

That narrowing is observational and it is not the experiment. A diff that touches nothing else is
consistent with the anchor being the cause and equally consistent with the cause being something
the diff does not show — an input artefact, an unpinned clock, a run that is not reproducible at
all. **The arms are what decide it.**

## The design

Both arms run at `79af956b1` in one locked worktree (`/var/tmp/se-onevar-anchor`), by the same
entry point the daemon uses (`python3 -m tools.run_annual_report`), differing in **seven float
literals** and nothing else.

- **ARM A (control)** — the block as it stands at `79af956b1`.
- **ARM B (treatment)** — the same tree with `YEAR_LEVEL_ANCHOR` restored to its `9c1c24f76`
  values (2017: 4.547299, 2018: 2.882178, 2019: 4.803900, 2020: 6.412007, 2021: 4.488202,
  2023: 0.364038, 2024: 3.053619).

**ARM A is load-bearing, not ceremony.** If it does not reproduce the published figure, ARM B's
difference is not attributable to the anchor — only to "this worktree is not that run" — and the
whole comparison is void whatever number it prints.

## Predictions (fixed before the answer)

**P1 — ARM A reproduces the published figure to the penny.** `total_net_gbp == 138,152.77`.
Refuted by: any other value.
*If P1 fails the run is not deterministic from code, which is a larger and more interesting finding
than the one being chased, and P2–P4 are unreadable.*

**P2 — ARM B recovers most of the move but NOT all of it.** `total_net_gbp` lands in
**[147,000, 149,500]**, i.e. the anchor accounts for **≥ 80%** of the £11,003.
Refuted by: a value outside that interval.
*Why not all of it: the docstring of the first re-fit records its own one-variable pair as moving
provisioned net 126,487.72 → 120,932.62, and the live run's provisioned net is 118,614.39 — the two
passes together move further than the first alone, but there is no reason the two arms' arithmetic
should land exactly on the published pair when the second pass was fitted against a capture taken
under the first.*

**P3 — the mechanism is book size, not margin per customer.** ARM B carries **more** accounts and
**more** bills than ARM A (`enterprise_value_account_count` 70 → ~76, `bills_total` 11,008 →
~11,565) and **fewer** churn events (`total_churn_events` 42 → ~36).
Refuted by: ARM B moving net without moving account count and bill count in the same direction.
*This is the falsifiable half. `avg_clv_gbp` rose across the published pair (3,311 → 3,371) while
revenue fell 5.1% — consistent with a smaller book of better customers, and inconsistent with a
margin squeeze. If ARM B moves net while leaving the book the same size, the story is wrong.*

**P4 — the move is against the company, and that is the correct direction.** ARM A (the live world)
is worse for Poesys than ARM B (the retired one). Nothing about this is a regression to repair:
a departure level fitted to the published GB switching record made the world **harder** to hold a
book in, and the company's result fell because the world got more honest, not because the company
got worse at its job.
Refuted by: ARM A beating ARM B.

## What must NOT happen

No file in `/home/rich/synthetic-enterprise` is written by either arm. Both run inside the locked
worktree; both `--save-json` paths are in the session scratchpad, outside every worktree. Evidence
to paste at grading time: `git -C /home/rich/synthetic-enterprise status --porcelain` unchanged in
`simulation/` and `docs/reports/`.

---

## GRADING

*(to be completed in place when both arms return — including any prediction that fails)*
