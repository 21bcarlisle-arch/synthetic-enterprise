**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `give-the-c2-reason-mix-its-svt-route`

# A foreign SVT sibling is what makes the account-denominator control pass

**Filed 2026-08-31, delivery seat, Lane 0.**
Subject: `tools/departure_population.py` (`load_svt_decisions`, `declare_rows`,
`account_denominator_refusal`, `union_by_year`), `docs/reports/ladder_churn_factors*`.
Prior, adjacent, and **not this**: `WORKER_FINDING_AN_EMPTY_SVT_SIBLING_WOULD_HAVE_CERTIFIED_THE_RENEWAL_ROUTE_AS_THE_WHOLE_BOOK_2026-08-31.md`.

---

## What was already known, and the half of it that was left standing

The empty-sibling finding closed the case where the SVT sibling **does not exist or is empty**. Its
repair is producer-side: `capture_departure_factors.emit_svt_sibling` now writes *no* file when the
run carries no recorder, so a missing sibling stays missing and `declare` reports
`covers_svt_route: false` with a reason. That repair is correct and it holds.

It closed the empty case. **It did not close the populated-and-foreign case**, and that case is live
in this tree right now.

`load_svt_decisions` accepts any readable file that happens to sit at the derived sibling path. Its
only questions are *does it exist* and *does it parse*. Nothing asks whether it is a reading of
**this run**, or of **this world**. So the producer was hardened while the reader was left trusting
the filesystem — and a producer that is not in git can still put a file there, because one already
did.

## The measurement

`docs/reports/ladder_churn_factors_svt_segment_decisions.json` is committed (`87709c617`),
1,266 rows, 50 `churned`. **Its producer is in no commit.** `run_phase2b` has no `_svt_decisions`
recorder and its return dict carries no `svt_decisions` key; `simulation/svt_product.py` states no
roster assigns the product and that *"an account on this product cannot currently leave"*;
`test_svt_product.py::test_no_account_is_on_the_svt_product_yet` holds that. Six fields in that
sibling — `route`, `data_regime`, `sim_svt_inertia`, `sim_years_on_svt`, `sim_segment_days`,
`company_svt_drift_estimate` — have **consumers in this tree and no producer**
(`tools/measure_churn_heterogeneity.py`, `tools/fit_year_level_anchor.py` read them; nothing writes
them).

The two ladder files are **not the same run**:

| | renewal table | SVT sibling |
|---|---|---|
| decisions | 144 | 1,266 |
| accounts | 68 | 116 (53 shared, 63 SVT-only, 15 renewal-only) |
| years | 2016–2025 **with no 2022 at all** | 2016–2025 **including 198 rows in 2022** |

63 SVT-only accounts is not by itself evidence — an account on SVT never renews. **The 2022 column
is.** The renewal table has zero rows in 2022; the sibling has 198.

## The two declarations, side by side, and the wrong one is the quiet one

```
ladder_churn_factors.json      population: renewal decisions + SVT segment decisions
                               covers_svt_route: true   causes_not_observable: []
                               "this reading's own route accounts for 39% of the departures"
                               warning: None                       <- no warning at all

c2_departure_factors.json      population: renewal decisions only
                               covers_svt_route: false  causes_not_observable: ['svt_inertia']
                               ⚠ no SVT segment-decision file beside this table
                               ⚠ this reading CANNOT SEE the SVT inertia route
```

The **honest** table prints two warnings. The **fabricated** one prints a clean bill of health and a
confident 39%. A reader comparing them concludes the ladder capture is the better-covered of the
two. That is the reader-goes-quiet shape, one surface over from where it was last looked for.

## The part that makes this worse than a stale number: it defeats its own control

`account_denominator_refusal` exists to refuse a whole-book rate when an account is invisible for an
interior year. Measured:

```
account_denominator_refusal(renewal, orphan_sibling)  ->  None          (PASSES)
account_denominator_refusal(renewal, None)            ->  refuses, loudly
```

**The orphan file is what makes the control green.** Accounts absent from the renewal table in 2022
are supplied by the sibling, so the interior-gap check finds no gap. Remove the phantom evidence and
the control fires correctly. `union_by_year` then publishes a whole-book departure rate per year —
including **2022: 55 accounts, 4 departures, 7.27%**, a row in which the renewal table participates
with nothing and every account and every departure comes from a run that is in no commit.

This is the coupled-harness class: the artefact fabricates the observable, and the control that
would have caught it is graded on the fabrication.

## Blast radius

`tools/measure_churn_heterogeneity.py` takes the ladder stem as its `DEFAULT_TABLE`. Seven staging
documents take the "two-route capture" as their measured subject, including
`..._THE_COMPANY_FORMS_NO_BELIEF_ON_THE_ROUTE_CARRYING_61_PERCENT_OF_DEPARTURES_...` and
`..._THE_ROUTE_CARRYING_MOST_DEPARTURES_IS_INVARIANT_TO_THE_RECORD_IT_IS_FITTED_AGAINST_...`. Every
"61%", "50 of 82", "1,410 decisions" figure in the record traces to this file. **The lane draw that
produced this turn cites it too** — *"the SVT route carries the majority of them"* — which is how a
phantom artefact set a delivery priority.

Those readings are not necessarily *wrong*; they measure a world that has an SVT departure route.
They are wrong about **this** committed world, and nothing on their face says so.

## Why the same-run property is not checkable today, which is the repair

Neither file records which run produced it. There is no capture identity, no timestamp, no run id in
either artefact — so `load_svt_decisions` has nothing to compare and cannot be made to fail on
provenance without one. The 2022 asymmetry above is *evidence* of two runs, not a *test* for it: a
genuine single run may legitimately have a year with no renewals.

**So the stamp comes first, and the refusal is keyed to it.** Landed in this commit: the producer
stamps every sibling it writes with the identity of the capture that wrote it, and `declare` carries
`svt_provenance` so a reading says on its face whether its sibling can be tied to its renewal table.

**Deliberately NOT landed in this commit:** flipping `covers_svt_route` to `false` for an unstamped
sibling. That is the correct end state and it is one line, but it turns the ladder stem red, changes
`measure_churn_heterogeneity`'s default reading, and marks seven filed findings as measured on a
population this world does not have. That is a disposition over other lanes' published work, not a
mechanical repair, so it is surfaced here rather than taken unilaterally mid-flight.

**Recommendation, and I will carry it out unless the director objects:** land the refusal next turn,
re-file the seven affected readings against the stamped world, and leave the C2 declaration exactly
as it is — it is true, and it cannot be made truer until the world has an SVT departure route to
see. The route itself is the real owed work.
