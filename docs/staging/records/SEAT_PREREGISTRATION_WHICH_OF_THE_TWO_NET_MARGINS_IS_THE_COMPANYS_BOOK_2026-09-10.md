# SEAT PREREGISTRATION — which of the two net-margin figures is the company's book

**Severity:** RECORDED
**Lane:** 0 (delivery seat)
**Date:** 2026-09-10
**Claim:** `two-artefacts-claim-to-be-the-companys-net-margin-and-the-gap-is-16597`

---

## The question

`site/data/value_arms.json`'s `realised.is_the_published_supplier` is WITHHELD, naming two figures:

| figure | £ | where the feed reads it |
|---|---|---|
| `published_run_net_gbp` | 131,289.34 | `docs/reports/run_output_latest.json` → `total_net_gbp` |
| `dashboard_net_gbp` | 147,886.78 | `site/data/dashboard.json` → `portfolio.net_margin_gbp` |

Gap £16,597.44. The refusal is honest and settles nothing. The item forbids resolving it by
taking whichever is nearer, so it must be resolved by establishing which artefact is the
company's book.

## What is already established before the measurement (no prediction needed)

These are facts read off the tree this turn, not forecasts:

1. **`run_output_latest.json` is the committed artefact 18+ site generators read.**
   `generate_customers_json`, `generate_customer_data`, `generate_customer_sample`,
   `generate_invoice_data`, `generate_customer_consumption`, `generate_portfolio_event_stream`,
   `generate_supplier_json`, `project_portfolio_to_2026`, `population_anchor`,
   `generate_snapshot`, `generate_margin_bridge`, `saas/reporting/annual_report`
   (`DEFAULT_REPORT_DATA_PATH`), `background/dd_h_solvency_gap`, `simulation/dd_collection_book`
   all name that exact path.

2. **`generate_dashboard_data` reads a DIFFERENT file, and it is not tracked.**
   `_find_latest_run_json()` globs `docs/reports/run_output_*[0-9Z].json` — a character class
   that deliberately excludes `latest` — and sorts by **mtime**. `.gitignore:40` ignores
   `docs/reports/run_output_*.json`; only 7 are force-added, and the one the live dashboard
   names in its own meta, `run_output_36e3ee8c4_20260909T210648Z.json`, is **not in the
   repository at all**. `site/data/dashboard.json` at HEAD therefore carries a figure from a
   local, gitignored, mtime-ranked artefact that no other generator reads and that no clean
   checkout can reproduce.

3. **`generate_margin_bridge` reads `run_output_latest.json`** (`RUN_OUTPUT_PATH`, line 30) and
   its own docstring says "the same `run_output_latest.json` both headline figures come from".
   Yet `site/data/margin_bridge.json` publishes `settlement_net_margin_gbp` = **147,886.78** —
   the dashboard's figure, not its own stated input's 131,289.34.

Fact 3 is the tell, and it is what makes the next measurement decisive rather than a tiebreak.

## The measurement, and what each outcome would mean

**Run:** read `total_net_gbp` from `git show 0247f3061^:docs/reports/run_output_latest.json` —
the content of that path immediately *before* commit `0247f3061` ("publish the run output the
customer book was actually made from, and its wall freeze") replaced it.

**Prediction, filed before running it:** that figure is **147,886.78** (to the penny, or within
rounding of `_fmt`'s 2dp).

**If the prediction holds** — the two artefacts are not two runs competing for one quantity.
They are **one path at two times**. `0247f3061` swapped the occupant of `run_output_latest.json`
to the customer-book run; every committed downstream feed still carries the *previous*
occupant's figure because none of them was regenerated after the swap. The company's book is
then unambiguously `run_output_latest.json` @ 131,289.34, the wrong reader is
`generate_dashboard_data`'s untracked mtime pick, and `margin_bridge.json`/`company.json`/
`dashboard.json` are stale rather than rival.

**If the prediction fails** (the pre-`0247f3061` figure is neither 147,886.78 nor 131,289.34) —
then the dashboard's 147,886.78 came from a run that was never at `run_output_latest.json`, the
staleness story is wrong, and the two really are rival runs. The repair would then have to
establish which run the customer book was drawn from independently, and I would say so here
beside this prediction rather than revising it.

**What will NOT move, and why it is independent:** the three A/B arm figures in
`value_arms.json` (`control` 147,954.26, `value` 165,398.23, `level` 165,079.13). Those are read
from `docs/observability/value_cycle_ab_*.json`, a different producer with no edge to either
path under test. Their staying put is not evidence for either branch — it is stated so that a
move there is read as contamination of the experiment and not as a result.

*The control arm at 147,954.26 sits £67.48 from the dashboard figure and £16,665 from the run
artefact. That is exactly the "whichever is nearer" reasoning the item forbids, and it is
recorded here as the trap, not as evidence. Nearness across two different producers is not
identity, and £67.48 is 6,748 times the feed's own £0.01 same-supplier tolerance.*

---

## RESULT — the prediction was WRONG, and the mechanism it was wrong about is the answer

**Measured:** `git show 0247f3061^:docs/reports/run_output_latest.json` → `total_net_gbp` =
**£1,529,288.58**. Not 147,886.78, not 131,289.34, and not within three orders of magnitude of
either.

So the "one path at two times" story I filed above is **refuted as stated**. The figure the
dashboard publishes was never the previous occupant of `run_output_latest.json`. Left here beside
the result rather than revised, because a prediction edited after its answer is not a prediction.

**What the refutation sent me to look at, and what was actually there.** If 147,886.78 never sat
at that path, it must come from somewhere else — so I followed it instead of the arithmetic:

* `site/data/dashboard.json`'s own `meta.source_file` names
  `run_output_36e3ee8c4_20260909T210648Z.json`, with `git_commit_source: "run_stamp"` — the
  authoritative tier. That file is **not in the repository**: `.gitignore:40` ignores
  `docs/reports/run_output_*.json` and only seven are force-added.
* `background/sim_runner.py:417-418` copies each fresh versioned run **onto**
  `docs/reports/run_output_latest.json` after every run.
* The shared tree's working copy of that path reads `total_net_gbp` **147,886.781507**,
  `producing_commit.commit` **36e3ee8c4**, `generated_at` 2026-09-09T21:19:02Z — and `git status`
  reports it **`M`**, modified and uncommitted.
* `site/data/publish_provenance.json`, which IS committed every publish, states
  `showing_run.run_id` = `run_output_36e3ee8c4_20260909T210648Z.json`.

**So both figures are the same path, but the split is working-copy versus committed-blob, not
occupant-then versus occupant-now.** The company's book is **£147,886.78**. £131,289.34 is not a
rival book: it is the committed blob, frozen at `0247f3061` (2026-09-01), because the path is not
in `process_run_complete.git_commit_push`'s publish surface. `0247f3061` predicted this in its own
STILL OWED section — *"the next publish that moves the book will ship the output without the input
again"* — and nineteen publishes in the following seven days did exactly that.

**The prediction's error was worth making.** It assumed the staleness lived in git history, so it
looked in git history. The staleness lives in the gap between the working tree and git — which is
why no commit-to-commit comparison could have found it, and why the *shape* the prediction was
reaching for (one path, two times) was right while every specific in it was wrong.

**The independence claim held.** The three A/B arm figures did not move: control 147,954.26, value
165,398.23, level 165,079.13, unchanged through the repair. They are read from
`docs/observability/value_cycle_ab_s1_three_arm.json`, which has no edge to either path under test.

**The £67.48 that was underneath.** Once identity is established against the published run, the
feed answers the real question and the answer is a **£67.47 divergence** between the published
supplier (147,886.78) and the baseline arm (147,954.26) — 0.046% of the book. That is a stated,
honest divergence and it is a *separate* open question from the one this item closed. It was
masked half the time by a £16,597 staleness artefact wearing the same refusal.
