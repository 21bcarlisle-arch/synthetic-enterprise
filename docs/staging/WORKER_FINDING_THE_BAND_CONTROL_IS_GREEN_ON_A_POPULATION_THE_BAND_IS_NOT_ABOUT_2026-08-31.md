**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

# The band control is green on a population the band is not about

**Filed 2026-08-31, delivery seat, Lane 0.**
Pre-registration: `WORKER_PREREGISTRATION_WHAT_THE_BAND_CONTROLS_STALE_SUBJECT_MUST_SHOW_2026-08-31.md`,
filed before the legs were written and before any mutation was run.
Subject: `tests/architecture/test_switching_rate_commons.py`.
Instrument: `tools/measure_departure_level.py`, `tools/departure_population.py` (`b8e6ba32d`).

---

## The finding

`test_the_worlds_realised_departure_rate_is_inside_the_published_band` has been green since
2026-08-30 and is green now. It is not wrong: it fires on its own subject, proven. **Its subject is
the wrong quantity, and nothing in the file could say so.**

Two independent reasons, and each is sufficient on its own:

**1. SCOPE.** The subject is `world_realised_rate_pct` — a mean over renewal DECISIONS. The band it
is judged against counts external changes of supplier over *all* GB domestic electricity accounts.
Before C1b those were merely different denominators. After C1b the renewal route carries **39%** of
the world's departures, so the green is a statement about the households that reach a renewal roll
— the ones who demonstrably shop — read as a statement about the book. Post-C1b the renewal
population is a *selected* sub-population, and a mean over it is not comparable to a
whole-population switching rate.

**2. STALENESS.** The artefact it reads, `docs/reports/c2_departure_factors.json`, has no
`_svt_segment_decisions.json` sibling. It was captured before the world had a second departure
route at all. The control's green comes from a world that no longer exists, and the table kept its
rows and every field populated throughout — it was the SCOPE of the population that moved, not its
size, so no population floor could fire.

**What the comparable quantity actually reads.** Measured on the two-route capture
`docs/reports/ladder_churn_factors.json` — every departure on either route over the accounts on the
book, which is the record's own numerator and denominator:

| year | published % | whole book, expected % | miss (pp) |
|---|---|---|---|
| 2017 | 13.5–14.0 | 14.26 | +0.26 |
| 2018 | 19.5–20.0 | 22.52 | +2.52 |
| 2019 | 20.7–21.3 | 18.94 | −1.76 |
| 2020 | 22.5–23.0 | 20.33 | −2.17 |
| 2021 | 17.9–18.4 | 16.73 | −1.17 |
| 2022 |  2.9–4.3  | 12.80 | +8.50 |
| 2023 |  8.9–12.5 | 17.36 | +4.86 |
| 2024 | 12.5–16.1 | 16.62 | +0.52 |

**Out of band in all eight full years.** 2022 has ZERO renewal decisions, which is why the
renewal-only column prints `nan` there and the 2017–2024 summary mean is `nan` — the one year the
record collapses to 2.9–4.3% is the year the old subject cannot see at all.

## Why this is not "the world is wrong"

It is not, and the distinction is the point. That the world misses the record is already filed
(`WORKER_FINDING_THE_ROUTE_CARRYING_MOST_DEPARTURES_IS_INVARIANT_TO_THE_RECORD_IT_IS_FITTED_AGAINST_2026-08-31.md`,
`18a09617d`) and is blocked on a mechanism: `svt_inertia_hazard` has no parameter the market could
arrive through, so the route carrying most departures is invariant to the record it is fitted
against, and `tools/fit_year_level_anchor.py` refuses to emit a re-fitted `YEAR_LEVEL_ANCHOR`.

**This finding is one level up.** It is that the control reporting on all of that was green, and had
no leg that could go otherwise. A reader could not tell whether its green meant *the world matches
the record* or *the subject is a stale slice the band was never about*. Both worlds produce the
identical PASS.

## The repair, and it is three legs and a rename

Landed in `tests/architecture/test_switching_rate_commons.py`:

* **`_PRINCIPAL_SUBJECT` renamed** to carry its route. It read *"the world's own realised departure
  rate"* — a whole-book name on a renewal-decision reading — and the register key is the only place
  a reader would have seen which one they had.
* **`test_the_register_names_the_route_its_principal_subject_can_see`** — two legs. Leg (i) COUNTS
  the population the subject means over and requires it to equal `departure_population`'s renewal
  decision count, from a different module: this is what catches a mean widened to span both routes,
  the mean-across-two-populations failure this repository has already paid for. Leg (ii) then
  requires the register key to name that route. The string check only means anything because the
  count leg pinned the population first.
* **`test_the_whole_book_departure_level_is_inside_the_published_band`** — the verdict the band was
  always about, on `world_book_rate_pct()`. **`xfail(strict=True)`**, because it is red for a cause
  that cannot be discharged in this lane and a plain red would wedge every lane's commit against
  this file. Strict is the load-bearing word: it FAILS the day the world comes into band, forcing
  the marker off and the real verdict on. Same device that held the pre-anchor 3.15x gap open until
  `departure_level_anchor` closed it. **The marker is the thing to delete, never a target.**
* **`test_the_whole_book_reading_refuses_with_a_named_cause_and_never_the_renewal_one`** — the
  refusal must not degrade to the quantity it CAN compute under the name of the one it cannot. The
  renewal reading sits in band in all eight years, so that fallback would buy a green.

Keyed to the property throughout: none of these asserts a value. They lift by construction when a
two-route capture becomes the subject and the anchor is re-fitted.

## Predictions, and the answers beside them

Each was filed before the mutation was run. `python3 -B` throughout — a same-second, same-size edit
matches on `(mtime, size)` and CPython serves the previous `.pyc`, which is how a mutation harness
reports the flattering answer.

**P5 — the file is green at HEAD, so any red is mine.** **CONFIRMED.** 24 passed, 0 failed.

**P1 — the rename mutation fires leg 1 and nothing else.** **CONFIRMED.** Dropping the route
qualifier from `_PRINCIPAL_SUBJECT`: 1 failed (`test_the_register_names_the_route_its_principal_
subject_can_see`), 25 passed, 1 xfailed.

**P2 — the flattering-fallback is reported LOUDLY by leg 2, not absorbed.** **CONFIRMED, and wider
than predicted.** Making `world_book_rate_pct()` return the renewal reading on refusal: **2 failed,
25 passed, and no xfail at all** — the strict marker converted the XPASS into a failure exactly as
predicted, AND the refusal leg caught the same mutation independently by the byte-identity of the
two readings. I predicted one leg; two fired. Recorded as it happened rather than as I wrote it.

**P3 — a causeless refusal fires leg 3.** **CONFIRMED.** Returning `""` as the refusal: 1 failed
(the refusal leg), 25 passed, 1 xfailed.

**P4 — the rename breaks nothing else.** **CONFIRMED.** After the change: 26 passed, 1 xfailed —
the same 24 as before plus the two new green legs, with leg 2 held open. No pre-existing leg moved.

**M4, not pre-registered and stated as such** — a leg that cannot fire is not a control, and leg (i)
of the register test is the one that gives leg (ii) its meaning, so it needed its own proof.
Dropping a single row from `world_outcome`: 1 failed (the register test), 25 passed, 1 xfailed. The
count leg is live and is not passing by construction.

## What is owed, and where it goes

1. **The SVT route needs a parameter the market can arrive through.** Blocking item, filed at
   `18a09617d`, baseline not curriculum, needs its own capture–fit–capture cycle. Until it lands,
   no whole-book anchor is fittable and leg 2 stays xfailed.
2. **`docs/reports/c2_departure_factors.json` needs re-capturing on a tree that has C1b.** Not done
   here deliberately: it is the published C2 artefact that other lanes read, the re-capture changes
   what they read, and the anchor it would be judged against is not re-fittable yet. Doing it now
   would move a published figure into a world whose anchor is known stale.
3. **Open, no number attached:** whether drift off SVT is an *external change of supplier* at all.
   `svt_rates` §4's bottom row — "all customers ~20-22%" — is the same quantity as the published
   band, which would make the SVT rows a COMPONENT of that rate rather than a route on top of it.
   If that is right, the whole-book union is double-counting and the misses above shrink. Filed
   without a number because nothing established establishes it.
