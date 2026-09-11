**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a-commons-artefact-cannot-tell-when-its-source-was-revised

# `cannot_tell` was the one verdict that owed nothing, and it is the verdict that cost twelve Ofgem editions

**Measured:** 2026-09-08, delivery seat. Predictions fixed before any historical copy was read, in
`SEAT_PREREGISTRATION_WHAT_A_CANNOT_TELL_VERDICT_ACTUALLY_SAID_WHEN_IT_STOOD_2026-09-08.md`.
**Class:** `figures_on_a_superseded_clock`.
Discharges item 4 of
`SEAT_FINDING_THE_CAP_COMPOSITION_CITES_A_MODEL_TWELVE_EDITIONS_STALE_AND_ITS_RECHECK_RECIPE_NAMED_THE_WRONG_PAGE_2026-09-07.md`.

## The one-sentence finding

`tools/commons_source_supersession.py` refused a `superseded` verdict that named no open finding —
and required **nothing whatever** of `cannot_tell`, the verdict that means *the recipe did not
terminate*, so an artefact could record "I could not ask" forever, in a shape that reads exactly
like a question that was asked and answered.

## Why this is the generalisation and not a second instance

The landed finding above ends with item 4: *"re-point the other `in_filename_only` artefacts'
recipes at a page that carries the file — that is not a property of this artefact, it is a property
of recipes nobody has ever run to completion."*

**The instances are already clean, and I checked rather than assumed.** Both `in_filename_only`
artefacts now cite the version-history page that carries the full v1.2–v1.31 series.
`capacity_market_supplier_levy` is `in_url` and its recipe sends the reader to the OLD cap landing
page — which is correct for it, because that page carries exactly one `.xlsx` and it is the Annex 9
workbook the levy is derived from. The recipe terminates.

So the open work was never the four recipes. It was that **nothing could tell a recipe that does not
terminate from one that does**, and the only signal it produces — `cannot_tell` — was free to record
and free to leave. `RECHECKABLE` does not catch it: that leg refuses an EMPTY recipe, and the cap
composition's was detailed, careful and unrunnable.

## What was PREDICTED and what happened

| # | prediction | outcome |
|---|---|---|
| P1 | the composition records `cannot_tell` at `5a2778d06` | **CONFIRMED** |
| P2 | ≥2 distinct artefacts stood at `cannot_tell` in some committed tree | **CONFIRMED** — three artefacts, four blocks |
| P3 | nothing at HEAD is `cannot_tell`, so the new leg cannot be shown reachable from the live tree | **CONFIRMED** |
| P4 | the stale blocks carried prose, so a "names a reason" leg passes vacuously on its own subject | **CONFIRMED**, and this is the one that mattered |

P4 was registered at moderate confidence with the fork it decided named in advance, because the
outcome it predicted is the one that would have tempted a weaker control.

## The measurement that decided the design

Every one of the 26 commits touching `docs/domain_artefact_library/` was walked. Four `cannot_tell`
blocks were ever committed, across three artefacts. **All four carried an articulate note. None
carried an `open_finding`.** Two asserted their own honesty inside the note:

> "An honest cannot_tell, with the missing thing named."
> "`cannot_tell` is the honest verdict and is recorded rather than a guess."

They were honest. **Honesty was never the missing thing.** A leg keyed to "a `cannot_tell` must say
WHY" would have gone green on all four — satisfied by the exact instances it existed to refuse.

So the leg demands an **act**, not a sentence: a filed finding that resolves in the tree, the same
obligation `superseded` already carried. A stuck block can always supply another sentence and cannot
supply that.

## What was built

`OWNED`, a seventh leg, sharing one implementation with `ACTIONED` via `UNRESOLVED_VERDICTS`.
`current` is the only verdict that settles anything, so it is the only one that owes nothing.

**Reachability is proven on the real bytes, not on the live tree.** The live pass is green and says
nothing about this leg, because nothing at HEAD is `cannot_tell` — a control green on an empty
subject is not a control. The test reads all four blocks out of the commits that carried them via
`git show` and asserts `OWNED` is the **sole** refusal on each, so a passing test cannot be
collateral from some other leg.

`test_a_reason_shaped_leg_would_have_passed_every_one_of_them` pins the design reason itself: it
fails if a future session weakens `OWNED` back to a prose check, because the notes are still there.

## A FAIL-OPEN found by the mutation battery, and it was in the OLD leg too

Four mutations were run. Three were killed. **M4 survived: removing `.strip()` from the emptiness
test left all 39 tests green.**

That is not cosmetic. `open_finding: ""` joins to the **repository root**, which exists, so the
existence check reads it as a finding that was filed and the obligation is discharged completely. A
whitespace path is the cheapest possible way to silence the leg and would look like an author who
meant to fill the field in later.

Established as a **missing test, not an equivalence** — the code was right and nothing was asking.
It was in `ACTIONED` from the day that leg was written, unnoticed for as long as it has existed.
Now covered for both verdicts across three blank forms, and M4 is killed.

## What is next

1. **The switching band is still the open debt.** `gb_domestic_switching_rate` is `superseded` with
   its finding filed and unrepaired: the publisher disagrees in 8 of 10 years, and the band change
   and `simulation/departure_level_anchor.py`'s re-fit are ONE atom that must land together.
2. **Re-site `ofgem_default_tariff_cap_windows`' pre-2026 unit rates** off the third-party
   compilation onto Ofgem's published cap-table PDFs. The trap is already named in that artefact's
   `how_to_recheck`: re-siting onto the MODEL WORKBOOK instead would make those rows share a source
   with `ofgem_cap_unit_rate_composition`'s derivation and destroy the 21 independent periods its
   cross-check — the only evidence its decomposition is right — currently stands on.
3. **The 2,700 and 2,500 bases still have no cross-checked period**, because the windows artefact
   reaches no 2026 period with a published level. `which_periods_the_cross_check_reaches` says so on
   the artefact's face; item 2 is what would close it.
