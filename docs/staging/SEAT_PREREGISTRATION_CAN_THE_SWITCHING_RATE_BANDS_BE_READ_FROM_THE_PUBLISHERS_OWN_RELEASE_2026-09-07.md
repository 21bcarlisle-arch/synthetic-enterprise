**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a-commons-artefact-cannot-tell-when-its-source-was-revised

# Pre-registration: can `gb_domestic_switching_rate` be re-sited onto the publisher's own release, and does any band move when it is?

**Written:** 2026-09-07, delivery seat, BEFORE reading a single figure off the DESNZ series.
**Subject:** `docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json`, the last
commons artefact still `cannot_tell`.

## Why this exists rather than just doing the work

The artefact is honest about its own defect: `how_to_recheck` opens **"THIS ARTEFACT CITES A
DERIVATION, NOT AN EDITION, and that is the thing to fix rather than to check around."** Its ten rows
are stamped `secondary` against a legend whose `primary` level is defined and deliberately reached by
nothing, because reaching it is the artefact's own stated open job. So the verdict is not a stale
fetch — there is no edition in the file to compare anything against.

**One thing is already established before any prediction below, because it is the artefact's own
recheck recipe run to completion rather than a measurement of an unknown:** the URL the artefact
stores, `https://www.gov.uk/government/collections/domestic-energy-switching-statistics`, returns
**HTTP 404**. The recipe therefore could not terminate in anything but `cannot_tell`, for the same
structural reason the cap composition's recipe could not — *a recipe nobody has run to completion*.
This is the second instance of that class in two days and the first where the page is simply gone.
The live series is at `/government/statistical-data-sets/quarterly-domestic-energy-switching-statistics`,
a **statistical data set**, which gov.uk stamps with `public_updated_at` — an edition marker of
exactly the kind the artefact says it lacks.

## Predictions, fixed before measurement

| # | prediction | confidence |
|---|---|---|
| **P1** | The data set carries a domestic **electricity** switch count per period covering 2016 through at least 2025, at a granularity that annualises. If it is gas-and-electricity combined only, the artefact's numerator definition (external CoS on an MPAN) cannot be matched and the re-siting fails. | moderate |
| **P2** | For at least one of **2022, 2023, 2024, 2025**, the publisher's own annual count falls **OUTSIDE** the stored band. These four are the ones to doubt: their bands are round numbers (0.8–1.2m, 2.5–3.5m, 3.5–4.5m, 4.0–5.0m), which is the tell of an estimate, not of a reading. | moderate |
| **P3** | For **2016–2021** the publisher's count sits inside the stored band. Those six carry precise stated values (4.82, 3.84, 5.54, 5.88, 6.39, 5.06m) and two were separately live-adjudicated against Energy UK. | moderate-high |
| **P4** | The verdict leaves `cannot_tell`. | high |

**P2 is the one that matters, and its named failure mode is that the test is uninformative rather
than supportive.** The 2023–2025 bands are ~1.0m wide on a ~3m level — wide enough that a band
CONTAINING the published figure is weak evidence the band was right, and only a band MISSING it is
strong evidence it was wrong. So a clean sweep of P2 will be reported as *"the bands were too wide to
be refuted"*, not as *"the bands were confirmed"*. The band widths are themselves a finding either
way: a band that cannot be wrong is not doing the work a band is for.

## The downstream question I will not pre-judge

Eight modules read this artefact, including `simulation/departure_level_anchor.py`,
`simulation/market_switching_propensity.py` and `tools/measure_departure_level.py`. If any band
moves, a world-side level may move with it.

**I am NOT registering "the anchor will not move".** A downstream figure computed from a band that
moved moves by construction, and a "will not move" claim about it would be unfalsifiable dressed as a
prediction. What I register instead is the procedure: **if any band moves, I measure the anchor
before and after and report the delta**, whatever it is; if no band moves, that question does not
arise and I will say so rather than reporting a null as a result.

## What done means for this item

The direction that drew this work names no exit test, so: **the artefact carries a per-row edition
marker naming the release each rate was read from, its stored URL resolves, and its verdict is
something other than `cannot_tell` — or, if the publisher genuinely cannot supply the numerator,
`cannot_tell` STANDS with the specific reason upgraded from "no edition exists in this file" to a
named property of the publication.** The second outcome is a real result and will not be dressed as
a failure to finish.

## What this does not test

Whether the band is the right band to aim the world inside. That is `reserved` in the artefact and is
the director's under the mission brief of 2026-08-30 section 7; nothing here touches it.
