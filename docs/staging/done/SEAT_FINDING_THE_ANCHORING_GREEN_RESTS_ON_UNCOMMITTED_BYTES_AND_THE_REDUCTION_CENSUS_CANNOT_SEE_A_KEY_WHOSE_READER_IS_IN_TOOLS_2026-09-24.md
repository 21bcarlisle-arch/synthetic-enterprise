**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The anchoring green rests on uncommitted bytes, and the reduction census cannot see a key whose only readers live in `tools/`

A live site reading — `covers_svt_route: true`, over 1974 SVT decisions — was produced by code that
was in no commit. The single census built to catch exactly this class of drop is structurally blind
to it, and was green throughout.

**Date:** 2026-09-24
**Claim:** `rescue-the-svt-departure-keys-the-refresh-door-nearly-discarded`
**Subject:** `saas/reporting/annual_report.py::extract_report_data`, the publication whitelist.
Measured from an isolated worktree at `46ad84a2a` (== `origin/main`, 0 ahead / 0 behind), surveying
the shared tree `/home/rich/synthetic-enterprise`.

---

## The premise as drawn, re-measured

The item was drawn citing `19f340e65` and `971e3680c`, both already ancestors of `origin/main`.
Re-measured at draw: still ancestors. The *code* premise is spent; the *bytes* premise is not —
the two keys were still unlanded, which is the work.

**One of the item's stated reasons has rotted, and in the direction that makes it worse, not
better.** The item's WHY reads:

> `covers_svt_route: false` is live on the site because the producer does not emit it — 49 SVT
> departures published as a numerator with no denominator.

Measured on the shared tree and in this worktree, `site/state/population_anchoring.json:17` reads
**`"covers_svt_route": true`**, over `{"renewal": 101, "svt_segment": 1974}` decisions and
`{"renewal": 42, "svt_segment": 46}` departures. The refusal the item describes is not live.

That is not the repair having landed. `git grep svt_departures origin/main -- saas/` returns
**nothing**. The reading is `true` because the run that wrote that file executed a **working tree
carrying the two lines uncommitted**. The artefact on disk agrees:
`docs/reports/run_output_latest.json` carries `svt_departures` (48 rows) and `svt_decisions`
(1218 rows) — keys `origin/main`'s reducer cannot produce.

**So the green was the fragile kind, and the refresh door this claim is named for would have
destroyed it silently.** Nothing on the site or in any control would have gone red at the moment
the bytes were discarded; the next run would simply have written `covers_svt_route: false` again
and it would have read as a property of the world.

Corollary, in the other direction: the same dirty copy **reverts** `971e3680c`'s gas-shape keys, and
`run_output_latest.json` carries **neither** `gas_shape_provider_by_customer` nor
`gas_shape_refusals`. A landed repair is already being un-published by the working copy that holds
the unlanded one. Both halves are the same fact — the artefact is a function of a working tree, not
of the record.

## PRE-REGISTRATION (written before the measurement)

`tests/saas/reporting/test_a_log_the_run_makes_and_a_section_reads_survives_the_reduction.py` is the
census built for precisely this class — "a log the run computes and a report section reads must
survive `extract_report_data`" — and it found three dropped logs when one was being chased.

**Prediction: it does NOT cover `svt_departures` or `svt_decisions`, and would not have gone red
for either.** Reason: its reader-side term is `_keys_read_off_data`, every `data.get("...")` in
`saas/reporting/annual_report.py`. The consumers of these two keys are not report sections — they
are `tools/population_anchor.py`, `tools/departure_population.py`,
`tools/capture_departure_factors.py`, `tools/fit_year_level_anchor.py`,
`tools/measure_departure_level.py`. The census's subject is scoped to one module's readers, so a
key whose only readers live outside that module is invisible to it, and its silence means nothing.

If the prediction is wrong, the census names these keys and the drop should have been caught, which
is a different and more interesting defect.

**RESULT: see "Measured" below — appended after running it.**

## Measured

**The prediction held.** Running the census's own `_keys_read_off_data` term over
`saas/reporting/annual_report.py`: **69** keys are read off `data` inside that module.
`svt_departures` is not one of them. `svt_decisions` is not one of them.

The census passes (`3 passed`) both before and after this repair, and would have passed for every
run in which the keys were dropped. Its reachability floor (`_MIN_LOGS_UNDER_CENSUS = 4`) is
comfortably met, so it is not silent for the vacuous reason — it is *correctly* green about a
population that structurally excludes its subject.

**This is a scoped-subject blindness, not a bug in the census.** The census's property — "the
intersection of what the run returns and what a report SECTION reads" — is sound and was chosen
deliberately. These two keys are outside it because their readers are not sections: they are
`tools/population_anchor.py`, `tools/departure_population.py`,
`tools/capture_departure_factors.py`, `tools/fit_year_level_anchor.py` and
`tools/measure_departure_level.py`. The reduced artefact has a second class of consumer the census
was never told about.

**The generalisation, which is the part worth keeping:** `extract_report_data`'s output has two
audiences — report sections in the same module, and `tools/` modules that open the saved artefact —
and only the first has a control over the whitelist. Every key in the second class is dropped
silently and indefinitely, exactly as these two were, and the only symptom is a downstream consumer
refusing to answer. That refusal then reads as a property of the world.

Widening the census to a second reader-side population is the obvious move and is **not** proposed
here without measuring it first: the reader-side term would have to span `tools/`, where `data` is
not the parameter name, and a widened detector that matches nothing is unfalsifiable — an empty
offender list is green either way. The honest next step is a census of how many `tools/` modules
read the reduced artefact and which keys they ask for, run as a measurement before any control is
written on top of it.

## What was landed

The two keys, out of the shared tree's mixed working copy, **addition hunks only**: 36 insertions,
0 deletions, `971e3680c`'s gas-shape keys preserved. The item's own instruction not to run
`refresh_to_head` on this path was correct and was followed — that classifier's advice is the
defect banked in
`SEAT_FINDING_THE_STAGED_TOO_DOORS_POPULATION_WAS_EMPTIED_BY_A_COMMIT_NOT_BY_THE_DOOR_2026-09-24.md`.

`svt_decisions` is forwarded with **no default**, deliberately: `.get(key, [])` would hand every
consumer an empty decision list, which `declare_rows` reports as `covers_svt_route: true` over zero
decisions — an unobservable population arriving as a measured absence. Absent stays `None` so the
refusal downstream keeps naming its own cause.

## The wall channel the landing had to rule, which the item did not anticipate

The first landing attempt was **refused by the gate**, correctly, and the refusal is worth recording
because it is the one thing in this piece of work that the drawn item did not see coming:

> `A WALKER-INVISIBLE WALL CHANNEL HAS GROWN IN THIS COMMIT'S TREE -- COMMIT REFUSED.`
> `NEW on channel F_published_artefact (2): + svt_decisions, + svt_departures -> saas/reporting/annual_report.py`

Naming a run-output key in `extract_report_data` is what creates the literal the channel-F walker
joins on, so **the repair itself widens the wall's published-artefact channel by two.** That is a
real crossing and not a formality: both row types carry `sim_`-prefixed ground truth
(`sim_svt_inertia`, `sim_action_propensity`, `sim_level_anchor`, `sim_years_on_svt`) alongside
`random_roll` and `realized_churn_probability`.

**Ruled, not amnestied.** `--freeze` was NOT run — it rewrites the baseline from the tree and would
have swept in any other new member as a side effect, which the baseline's own `_meta` calls "a
freeze without a reason is an amnesty". Two rows were added **by hand**, and the reason is written
into `_meta.last_freeze` beside them. What was checked before ruling it:

- The crossing is the same one as `customer_events -> saas/reporting/annual_report.py`, **already a
  member** — the *first* departure route's log into the *same* reader, by the same mechanism.
- `extract_report_data` **forwards** both lists untouched and reads no field of either row.
- Nothing in `saas/` or `company/` reads any `sim_` field, the roll, or the realized probability
  **off these two logs** — grepped at this rev. Their consumers are five `tools/` modules outside
  the wall. (`company/analytics/counterfactual_retention.py` does read `random_roll` and
  `realized_churn_probability`, but off `customer_events`, which is a pre-existing ruled crossing
  this landing neither widens nor touches.)
- The ruling is explicitly bounded: **if a `saas/` section ever reads a `sim_` field off an SVT row,
  that is a new crossing and this ruling does not cover it.**

The second surface — `F_nested_schema` — then had to be pinned too, and this is the half that will
actually catch something later. It pins the **closed set** of nested field names under every key a
business module reads, deliberately not a `sim_*`/`true_*` denylist (pass 25 established that a
prefix detector was fail-open on 9 of 11 truth fields). `svt_departures` is pinned at its **13**
field names and `svt_decisions` at its **16**, computed with the tool's own walker rather than
hand-typed so the pin is exactly what the checker recomputes. Any field added to an SVT row from
here fires; a field disappearing does not, because that is a paydown.

## What is still owed

The control that was supposed to catch this — `test_a_churned_account_has_a_departure_record.py` —
**grades the artefact on disk, not the code**, so it read green throughout on an artefact the dirty
working tree produced. That is the subject of `0b8a8156f` ("five controls were green only because
of uncommitted work beside them, and none of them gated anything") and this is a sixth instance of
it, found from the other end.

A control keyed to the **function** rather than the artefact is what closes it: feed
`extract_report_data` a run output carrying both keys, assert the reduced dict forwards them, and
assert that an absent `svt_decisions` arrives as `None` and not `[]`. Its mutation is the historical
defect exactly — delete either line and it fires — and unlike the artefact control it cannot be made
green by an uncommitted tree.
