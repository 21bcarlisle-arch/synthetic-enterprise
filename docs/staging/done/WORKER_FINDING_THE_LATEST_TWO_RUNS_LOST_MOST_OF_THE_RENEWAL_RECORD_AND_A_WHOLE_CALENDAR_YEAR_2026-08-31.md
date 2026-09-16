**Severity:** LATENT · **Status:** ATTRIBUTED, REPAIRED AND SETTLED 2026-08-31 — the pre-registered prediction HELD on the run that settles it; one debt remains open and is named under "Still owed" · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB3_book_growth_as_earned_outcome`

# The latest two runs lost most of the renewal record, and 2022 is not in it at all

*Filed 2026-08-31, delivery seat, while closing §11 B and C of
`docs/market_research/gb_switching_rate_denominators.md` (§13). Found by needing a sound run to mark
a prediction against, and refusing to mark against this one.*

## What was measured

`customer_events` is the renewal record: one row per household renewal decision, carrying the
churn probability, the roll, the outcome, and — since 2026-08-30 — the departure cause. It is the
subject of the departure-level measurement, of `tools/measure_departure_level.py`, and of every
before/after on churn this project publishes.

Counted straight off the run records in `docs/reports/`:

| run | renewal events | distinct households | churn events | churned billing accounts | years present |
|---|---|---|---|---|---|
| `56718a719` 2026-08-30T17:37Z | 681 | 130 | 43 | 43 | 2016–2025 |
| `ff44d0bce` 2026-08-30T20:03Z | 465 | 131 | 79 | 79 | 2016–2025 |
| `112eb0b11` 2026-08-30T21:31Z | 143 | 68 | 33 | **83** | **2022 absent** |
| `87d49e187` 2026-08-30T23:11Z | 143 | 68 | 33 | **83** | **2022 absent** |

Three things break at once between 20:03Z and 21:31Z, and they break together:

1. **Churn events and churned billing accounts stop agreeing.** They agree exactly in every earlier
   run — 43/43, then 79/79. In the last two they are 33 against 83. **Fifty departures happen with
   no renewal event to carry them**, so fifty departures now have no cause, no roll and no
   probability anywhere in the record.
2. **The record loses half its households.** 131 distinct households → 68, against a
   `per_cid_pnl` of 251 that did not move.
3. **The year 2022 is absent from `customer_events` entirely.** Every other year is present. 2022 is
   the crisis year, it is the year the departure band is narrowest (2.9–4.3%), and it is a fact of
   the historical record rather than a scenario.

## Why this matters more than a count

The departure-level anchor landed the same evening and is measured *through this record*. A control
whose subject has silently lost half its rows and one of its ten years cannot fail in the direction
that matters: fewer renewal events with the departures still landing reads as a **higher** departure
rate per renewal, which is the direction the anchor was fitted to produce. The instrument and the
result move the same way, and nothing in the tree compares the two counts.

`tools/measure_departure_level.py` reports 8 years inside the band on `world_mean_pct` 16.20%. That
figure is not from these runs — it is from the 2026-08-30 captures — but the same reader will
compare it against a run whose record is missing a year, and the two are already published side by
side on `site/data/value_arms.json`.

## What is NOT claimed here

I have not diagnosed the cause. The commits between the 20:03Z and 21:31Z run markers are
`00d855cf2`, `60d30b0a6` and `112eb0b11`; two of them are publish-lane work and one adopts a test
change. The renewal record is written by `simulation/run_phase2b.py` and the departure path was
edited twice that evening (`1596019fc`, `71242c941`, `3bf3345de`). **Which of those did it is a
question, not an answer, and no number here is attributed to any of them.**

## The one-leg control this earns

The two counts are supposed to be the same population counted twice, so the cheapest control that
can actually fail is the reconciliation the run already contains and never checks:

> every billing account in `churned_billing_accounts` has at least one `customer_events` row with
> `event_type == "churned"`, and every year of the reported window appears in `customer_events`.

That is one assertion over an artefact the run already writes. It is red on the last two runs and
green on the two before them, which is what makes it worth having: it is keyed to the property (the
record covers the departures it reports) and not to today's answer.

## Status

**LATENT.** Nothing published today reads the broken runs — the publisher has been wedged on a level
declaration since 22:04Z and `site/data/value_arms.json` still carries the 10:37Z pre-anchor run. It
becomes BLOCKING the moment the wedge clears, because the next publish takes its book counts,
its CLV population and its departure figures from exactly this record.


---

# ATTRIBUTED — 2026-08-31, delivery seat

**It is none of the three commits, and it is not data loss. It is C1b, uncommitted in this tree,
plus one line the reducer between the run and the artefact never named.**

## Ruled out, with what was read

| Candidate | Ruled out by |
|---|---|
| `00d855cf2`, `60d30b0a6`, `112eb0b11` — the three commits inside the window | `git show --stat` on each: one test file, and two documents. **No commit in the window touches `simulation/`, `saas/` or `tools/` at all.** |
| `1596019fc`, `71242c941`, `3bf3345de` — the departure-path edits that evening | All three are *before* the 20:03Z run marker, which is green on both legs. |
| `background/sim_runner.py` dropping rows | It copies the child's JSON byte for byte (`latest_json.write_bytes(out_json.read_bytes())`). |
| `tools/run_annual_report` | It writes `extract_report_data(raw_output)` verbatim and filters nothing itself. |

A run marker's git hash names the HEAD the run **sat beside**, not the code it **ran**: the sim
executes the working tree. That is why bisecting the committed history could not have found this,
and it is the general lesson — for an artefact produced by a daemon in a shared tree, the commit
graph is not the changelog.

## The cause: one mechanism, three symptoms

C1b is uncommitted in `simulation/renewals.py`, `run_phase2b.py`, `svt_product.py` and
`departure_risks.py`. `build_renewal_schedule` now sends a domestic fixed account that fails its
`rolls_active_renewal` engagement roll onto a standard-variable stint instead of building it
another fixed term.

1. **465 → 144 renewal events, 131 → 68 households.** An SVT stint has no renewal point, so it
   convenes no decision and writes no `customer_events` row. C1b's own note in `departure_risks.py`
   states the size of it: *"roughly 55–58% of domestic account-days no longer reach that roll at
   all."* The rows were never written, not lost.
2. **2022 absent** is that same mechanism at its extreme, and it is deliberate world behaviour
   rather than a hole: the 2022 crisis-year forcing inside the engagement roll collapses the
   generated fixed share that year, so essentially no domestic account reaches a renewal point in
   2022. **`customer_events` is a log of renewal DECISIONS, and in 2022 this world convened almost
   none.** The wall is not breached — 2022 is still in `years`, still settled, still billed — but a
   reader who takes `customer_events` for "the lifecycle record" gets a hole exactly where the
   crisis is, and both departure-level readers do take it for that.
3. **The 50 unexplained departures were produced, recorded, and then dropped in transit.**
   `run_phase2b` adds each SVT departure to `churned_billing_accounts` *and* writes its full record
   — cause, roll, hazard, years-on-SVT — to a new list, `svt_departures`.
   **`saas/reporting/annual_report.extract_report_data` did not name that key.** It is the reducer
   between the raw run and `docs/reports/run_output_latest.json`, and a key it does not name is
   dropped silently. So the churn crossed into the artefact and its evidence did not.

## The class, and that we had already paid for it once

Twenty lines above the repair, in the same dict, is the comment left by the last time this
happened: *"`run_output_latest.json` is this function's REDUCED output, not the raw run — so a key
the reducer does not name is dropped between the two, silently and with no error anywhere."* That
was `three_horizon_clv_snapshots`, and it cost four consecutive runs. C1b carefully enumerated the
consumers it owed — `tools/population_anchor._churn_by_year`, `tools/measure_departure_level` — and
the reducer was not on the list, because it is not a consumer: it is the pipe. **A new output key
has two obligations, not one: the readers who want it, and the reducer that has to carry it.**

## Repaired

`saas/reporting/annual_report.py` now forwards `svt_departures` — **untouched, and under its own
name**. It is deliberately *not* unioned into `customer_events`: an SVT departure convened no
renewal decision and carries none of that log's fields, and twelve consumers index
`churn_probability` on it unguarded. Two populations, two lists; a reader whose subject is all
departures unions them itself.

## Still owed, and NOT repaired here

- `tools/population_anchor._churn_by_year` and `tools/measure_departure_level` still read the
  renewal log alone, so the departure level they publish is missing the SVT route entirely. C1b
  names this debt; it is now live rather than pending, because the route exists in the artefact.
- The per-year departure ratio has **no denominator at all in 2022** under this world. That needs a
  named refusal on the surface, not a zero and not a silent gap.
- Nothing here re-opens whether C1b's assignment is right. It is the other lane's work and it is
  mid-flight; this finding is only about what the record shows and what carries it.

## PRE-REGISTERED, filed before the run that settles it

The reducer repair lands before the next scheduled run (~06:37Z, 2026-08-31). **I predict that run
will show `unexplained churns = 0` and `2022` covered by the lifecycle record** — covered by
`svt_departures` rather than by renewals, because in 2022 the whole domestic book is on the default
tariff and every cap period is an inertia roll at the 5–25% per-segment hazard C1b measured.

**If 2022 is still absent after that run, this prediction is refuted and the finding is deeper than
a reducer key**: it would mean a year in which this world convenes no recorded decision of any kind
about who stays, which no reducer can repair.

## SETTLED — the run has been, and the prediction holds

*Written 2026-08-31 by the next tick, against the artefact the predicted run actually produced.*

`run_complete_20260831T063611Z` is that run. It executed the working tree — the reducer repair was
staged, not committed, which is the same mechanism that made this defect invisible to a bisect in
the first place — and rewrote `docs/reports/run_output_latest.json` at 07:47:58Z. Measured on it:

| predicted | measured | verdict |
|---|---|---|
| unexplained churns = 0 | **0** (82 churned accounts; 32 renewal churns + 50 SVT departures, union exact, no remainder) | HELD |
| 2022 covered by the lifecycle record | **covered** — 2022 present in `svt_departures` (4 rows, each with cause `svt_inertia`, roll, hazard) | HELD |
| covered by `svt_departures` and NOT by renewals | **`customer_events` still has zero 2022 rows**; every 2022 departure arrives by the SVT route | HELD, including the mechanism |

The prediction named the route as well as the outcome, and the route is what came true. That is
the part worth keeping: the reducer key was the whole of the 50 unexplained departures, and the
2022 hole was never a reducer defect at all — it was this world convening no domestic renewal
decision in the crisis year, showing through a reader that mistook the renewal log for the
lifecycle record.

**Independently re-derived before this was written, because the attribution above deserved a second
route to it.** `simulation/renewal_engagement.rolls_active_renewal` opens
`if year in CRISIS_PASSIVE_YEARS: return False`, and `CRISIS_PASSIVE_YEARS` is
`frozenset({'2022'})` — unconditional, no probability consulted. `renewals.build_renewal_schedule`
sends every domestic fixed account failing that roll onto an SVT stint. So *every* resi fixed
renewal falling in 2022 becomes an SVT segment with no renewal decision, by construction and not by
chance. The run record agrees from the other end: **2,012 terms are processed and 256 of them start
in 2022** — more than any year but 2023 — while `customer_events`, `retention_log` and
`no_offer_churn_log` are all empty for that year. The terms were processed; the decisions were not
convened. The two accounts with a 2022 term that are *not* resi (`C3_2`, `C8`) are on indexed
tariffs, which `run_phase2b` gates out of the renewal decision at the same seam.

**What this settles and what it does not.** It settles that the record is whole again and that the
missing year is world behaviour rather than data loss. It does not settle whether that behaviour is
right: `CRISIS_PASSIVE_YEARS = {'2022'}` is a hard forcing that removes the company's ability to
make a single domestic pricing decision in the crisis year, and it was written long before C1b gave
it a consequence. `tools/svt_generated_share_check` puts the generated 2022 fixed share at **21.5%
against a published 10–20%** — so the direction is defensible and marginally generous to us, which
is the honest reading and not a vindication. That constant is now load-bearing in a way it was not
when it was written, and it is a question for the lane that owns C1b, not a repair to make here.

## The control, landed

`tests/saas/reporting/test_a_churned_account_has_a_departure_record.py`, keyed to the property and
carrying no count. Graded across six run artefacts:

| run | unexplained churns | years absent |
|---|---|---|
| `56718a719` 17:37Z | 0 | — |
| `ff44d0bce` 20:03Z | 0 | — |
| `112eb0b11` 21:31Z | 50 | 2022 |
| `87d49e187` 23:11Z | 50 | 2022 |
| `2b9fb79d9` 02:09Z | 50 | 2022 |
| `4240e1478` 05:07Z | 50 | 2022 |

| `4240e1478` 05:07Z | 50 | 2022 |
| **`063611Z` run, 07:47Z** | **0** | **—** |

**It was RED at birth and it went GREEN on the predicted run, which is the transition it was built
to observe.** The row above is the whole point of having filed it before the run rather than after.

**And going green cost it its FAIL-branch evidence, so that has been replaced rather than assumed.**
The original argument was "no mutant is needed, it is red at HEAD" — true when written, false the
moment the artefact was repaired. The mutation now stated in the file's own docstring and re-run
against the live artefact is: **delete `svt_departures` from the artefact**, which is precisely the
reducer defect this finding attributes. Both live legs fail together under it — 50 unexplained,
`["2022"]` absent — so the control demonstrably fails by the exact route that made it necessary.
The four synthetic-artefact cases remain the PASS-branch reachability proof (green via the renewal
log, green via the SVT log, red for an unexplained account, red for an absent year), and a fifth
closes the vacuous pass an empty artefact would otherwise report.


---

# AND THE COMPANY'S OWN CRM IS BLIND TO THE SAME FIFTY — found while attributing the above

`simulation/run_phase2b._build_company_event_log` is the company's CRM feed, and it builds its
`"churn"` rows from **`customer_events_log` alone**:

```
for evt in customer_events_log:
    if evt["event_type"] == "churned":
        result.append({"event_type": "churn", ...})
```

Under C1b, an SVT departure never enters that list. So the world knows about 82 departures and the
company's CRM learns about 32 — **the company does not know that two thirds of its book left**.
This is worse than the reducer key repaired above, and in a different way: the reducer defect made
the departures unreadable to us, this one makes them unknown to the company, and the company's
believed book is one side of the coupled-triad gap that `PB3_book_growth_as_earned_outcome` is
scored on. A gap measured against a CRM that cannot see a departure route is not a measurement of
belief quality; it is a measurement of the feed.

**It announces itself and needs no new watcher.**
`tests/simulation/test_run_phase2b_event_log.py::test_every_churned_account_appears_in_the_event_log`
already asserts set equality both ways between `churned_billing_accounts` and the CRM churn rows,
on a 2017-truncated run. It should be red at HEAD for exactly this reason, and it is in the
selected set for any commit touching `simulation/run_phase2b.py` — which is C1b's own pathspec.

**Not repaired here, deliberately.** The fix is one append inside C1b's own SVT branch, in a file
another lane has open and mid-flight; landing across their hunks to save them one line is the
trade this project has already lost twice. What is owed with it is the `reason` field: the existing
rows say `"non-renewal"`, and an SVT drift is not a non-renewal — it is the absence of one.
