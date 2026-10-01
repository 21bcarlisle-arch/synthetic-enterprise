**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon — Lane 0 delivery

# Pre-registration: does "legs, then rate" replicate on a run the rule was not discovered on?

Claim `ep1-fuel-split-rule-replicate-on-independent-run`. The duplicate-work note named this same
id as "already held". That was this draw's own write: at 05:58 no other process held the id and no
`surgical_land` was running. The premise is not spent. `24542747c` landed the discovery-sample
grade and handed replication on, and nothing since has run it.

Filed BEFORE any replicated number was computed. The two runs were launched first, at 05:59, and
nothing has been read from them except that they started.

## What run this is, and what it is not

**This is not a different population.** `run_phase2b.main` has no seed argument. The only way to
draw a different cast of households is `tools/run_value_cycle_ab.py --book-seeds`. That rebinds
`live_population._DEFAULT_BASE_SEED`. The tool refuses any non-default seed until
`docs/design/curriculum/varied_population_draw_activation.json` exists, because a different book
is `EP17_varied_population_draw`, which is R13 curriculum and the director's. That file does not
exist on origin. I have not rebound the seed by hand: doing so would get round the door rather
than go through it.

**What it is.** It is the default book, with the two sanctioned noise-floor keys re-drawn for
every account:

- `churn_roll` (each renewal's dice);
- `elasticity` (each household's price sensitivity).

Both use `tools.run_value_cycle_ab.resolve_redraw_target`, the same factories `noise_floor` and
`book_member` use. The floor seeds are 101 and 202, chosen as labels and never tuned. Who leaves,
and when, is re-drawn, so which accounts are on the book at each cutoff changes too. Because the
campaign plans against the book, some acquisitions change as well. **What stays fixed:** the
founders' dwellings, consumption and fuel legs. A pass here is therefore a replication over the
*realisation*, not over the *population*. If the leg-count signal is a fact about these particular
households, it can survive this test and still fail on a new book.

Script: `/tmp/ep1r/run_floor.py <seed>`. It writes `run_<seed>.pkl` and `snaps_<seed>.json`. The
grading pipeline is `/tmp/ep1r/rep.py`. It is `build.py` → `fwd.py` → `strat.py` → `lex.py` /
`loco.py`'s M2, collapsed into one script that takes a run and its own EP1 snapshot series.

## Control first (C0): the rewritten pipeline must reproduce the discovery sample

`build.py` took each account's first valuation year from the PUBLISHED run output's belief series
(`run_output_latest.json`), which a fresh run does not have. `rep.py` takes it from the run's own
`build_three_horizon_clv_snapshots`. Applied to the discovery run (`/tmp/ep1bk/run.pkl` +
`snaps.json`), C0 holds if:

- graded rows are within ±10 of 298;
- LEX(L,I1) − I1 is within ±0.02 of +0.131.

If C0 fails, the replication numbers are not comparable to the discovery figures, and I will say
that instead of grading.

## Informativeness (C1): did the redraw move enough of the book to test anything?

Over accounts graded in both the discovery run and a floor run, C1 is the share whose
last-settlement month differs. If it is below 25%, that floor run is uninformative. I will report
that rather than count a pass. Separately, I report the share of graded rows in the floor run whose
(account, cutoff) does not occur in the discovery sample.

## Predictions (each floor run separately; same statistic `wsp`, per-account cluster CIs, 1000 draws, `Random(0)`)

| | Prediction |
|---|---|
| R1 | LEX(L,I1) − I1 > 0 with the cluster CI excluding 0. Point estimate in [+0.05, +0.25]. |
| R2 | LEX(L,I1) − L: the CI contains 0 and \|point\| < 0.08. "Rate" adds nothing measurable over legs alone, as in discovery (−0.020). |
| R3 | L alone − I1 > 0 (point). Discovery: +0.153 [+0.006, +0.299]. |
| R4 (M2) | Single-fuel median within-(cutoff, L) IQR ratio I2/`fn` < 0.5. Dual-fuel ratio in [0.7, 1.4]. Discovery: 0.24 and 1.01. |

**Licence rule, fixed now.** "Legs, then rate" is licensed as EP1's company-side ranking input
only if C0 holds, C1 holds on both seeds, and R1 holds on both seeds. Even then, the licence
covers this book only. Generalisation to a new population waits on the EP17 ruling. R2–R4 are
mechanism reads; they do not gate the licence.
