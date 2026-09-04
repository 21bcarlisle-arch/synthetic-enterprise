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

Both arms returned 2026-09-04T04:52:36Z. This section was written after; everything above it was
committed in `74cef0040` before either arm had produced a JSON.

### The result

| figure | published PRE (`9c1c24f76`) | **ARM B** | published POST (`79af956b1`) | **ARM A** | exact |
|---|---|---|---|---|---|
| `total_net_gbp` | 149,156.202822 | **149,156.202822** | 138,152.772886 | **138,152.772886** | ✓ |
| `total_gross_gbp` | 401,580.427294524 | 401,580.427294524 | 378,553.660743486 | 378,553.660743486 | ✓ |
| `total_revenue_gbp` | 718,261.614239951 | 718,261.614239951 | 681,725.485319816 | 681,725.485319816 | ✓ |
| `bills_total` | 11,565 | 11,565 | 11,008 | 11,008 | ✓ |
| `enterprise_value_account_count` | 76 | 76 | 70 | 70 | ✓ |
| `enterprise_value_gbp` | 128,435.070587008 | 128,435.070587008 | 122,874.029780836 | 122,874.029780836 | ✓ |
| `provisioned_net_gbp` | 126,487.715539 | 126,487.715539 | 118,614.389071 | 118,614.389071 | ✓ |
| `final_treasury_gbp` | 399,156.20 | 399,156.20 | 388,152.77 | 388,152.77 | ✓ |
| `cost_to_serve_portfolio_gbp` | 52,250.216324047 | 52,250.216324047 | 49,710.635273855 | 49,710.635273855 | ✓ |
| `total_bad_debt_gbp` | 10,182.83 | 10,182.83 | 11,601.01 | 11,601.01 | ✓ |
| `avg_clv_gbp` | 3,310.993045437 | 3,310.993045437 | 3,371.251086705 | 3,371.251086705 | ✓ |
| `total_acquisition_spend_gbp` | 61,305.05 | 61,305.05 | 61,415.08 | 61,415.08 | ✓ |
| `total_churn_events` | 36 | 36 | 42 | 42 | ✓ |

```
published move   : -11,003.429936
one-variable arm : -11,003.429936
share explained  : 100.000000%
```

**Seven float literals account for the entire move, to the penny, on every headline figure.**

### Prediction by prediction

**P1 — CONFIRMED.** ARM A returned `138152.772886` against a published `138,152.77`, and matched
the published run on all twelve other figures. The run is deterministic from code and the isolated
worktree is a faithful copy. Everything below is readable because of this.

**P2 — its interval HOLDS and its heading is WRONG, and the heading is the part that mattered.**
The stated falsifier was "a value outside [147,000, 149,500]"; 149,156.20 is inside it, so by its
own written test P2 is confirmed. But the heading claimed *"recovers most of the move but NOT all
of it"* and *"≥ 80%"*, and the answer is **100.000000%**. **The falsifier could not catch the error
in the claim it was attached to** — a lower bound of 147,000 cannot refute "not all of it" when
"all of it" is 149,156.20 and sits inside the interval.

This is the trap named in my own notes — *a prediction's heading can claim more than its `Refuted
by:` list covers* — walked into again, one file after writing the heading. The lesson takes: the
falsifier has to be constructed from the heading's strongest word, and here that word was **NOT**.
The interval should have been `[147,000, 149,000]`, which the result would have refuted cleanly.

*Why the reasoning was wrong, specifically.* I argued from the first re-fit's own recorded
one-variable pair (provisioned net 126,487.72 → 120,932.62) that two passes could not compose back
onto the published pair, because the second was fitted against a capture taken under the first.
That is true of the **fit** and irrelevant to the **run**. The anchors are seven numbers; setting
them back to their pre-first-pass values restores that world exactly, whatever path the fitting
took to leave it. I confused a property of how the values were derived with a property of what they
do.

**P3 — CONFIRMED, and exactly.** Predicted `enterprise_value_account_count` 70 → ~76, `bills_total`
11,008 → ~11,565, `total_churn_events` 42 → ~36. Returned 76, 11,565 and 36. The mechanism is book
size, not margin per customer: six more accounts survive, 557 more bills are issued, six fewer
churn events fire, and `avg_clv_gbp` moves the *other* way (3,371 → 3,311) — the smaller book is a
better book per customer, which is why this cannot be read as a margin squeeze.

**P4 — CONFIRMED.** ARM A (the live world) is £11,003 worse for Poesys than ARM B (the retired
one). Nothing here is a regression to repair. A departure level fitted to the published GB
switching record made the world harder to hold a book in; the company's result fell because the
world got more honest, not because the company got worse at its job. This is the direction
`gb_switching_rate_denominators.md` §8 prediction 3 exists to check, and it did not fire.

### The must-not-happen constraint, discharged

`docs/reports/run_output_latest.json` in the main repo has mtime **05:03:52**, written by the
publish cycle before ARM A started at **05:21:06**; `simulation/` is untouched. Both arms wrote
only inside `/var/tmp/se-onevar-anchor` (which did accumulate run state — that is what the
isolation was for) and to the session scratchpad. **No file in `/home/rich/synthetic-enterprise`
was written by either arm.**

### What this establishes, and what it does not

It establishes that `YEAR_LEVEL_ANCHOR` is the **complete proximate cause** of the move — not the
largest contributor, the only one. The static narrowing said so first (outside `tests/`, `docs/`,
`site/`, `background/` and `tools/`, those two simulation modules are the only files that changed
in eighty commits) and the arms confirm it to six decimal places.

It establishes **nothing about whether the new level is right.** That question is open and BLOCKING
in `SEAT_FINDING_THE_LEVEL_IS_CLAMPED_AND_THE_MECHANISM_UNDER_IT_IS_COMPRESSED_NOT_MISDIRECTED_2026-09-03.md`:
the level is fitted per year rather than emerging from households, and six of eight years are still
outside the published band. A figure that moved for a fully understood reason is not the same as a
figure that is now correct.

**Disposition of the figure: CORRECT, with the caveat mechanised.** £138,153 is what this world
earns and no part of it is withdrawn. What was missing was any way for a reader to know the world
had moved — repaired in `74cef0040` (`world_level` on every run output) and `19770cf50`
(`world_level_digest` published in `dashboard.json`), and filed as instance 10 of
`no_caller_and_never_runs`.
