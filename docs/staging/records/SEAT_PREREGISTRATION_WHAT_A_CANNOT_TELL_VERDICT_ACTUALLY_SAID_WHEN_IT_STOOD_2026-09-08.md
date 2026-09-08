**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a-commons-artefact-cannot-tell-when-its-source-was-revised

# Pre-registration: what a `cannot_tell` verdict actually said, in the commits where it stood

**Registered:** 2026-09-08, delivery seat, BEFORE reading any historical copy of the artefacts.
Follows item 4 of
`SEAT_FINDING_THE_CAP_COMPOSITION_CITES_A_MODEL_TWELVE_EDITIONS_STALE_AND_ITS_RECHECK_RECIPE_NAMED_THE_WRONG_PAGE_2026-09-07.md`.

## The hole, which is established and not the thing being measured

`tools/commons_source_supersession.py` has six offline legs. `ACTIONED` refuses a `superseded`
verdict that names no `open_finding` — "knowing the source moved and doing nothing is the CM levy
failure with extra paperwork". **`cannot_tell` is refused by nothing.** It is enumerated as legal
and required to carry no reason, no diagnosis and no owner. `RECHECKABLE` refuses only an EMPTY
`how_to_recheck`, so a recipe that is detailed, well-written and *unrunnable* passes it forever.

That is exactly how the cap composition sat twelve editions stale: its recipe named a page that has
never carried the model, so the recipe terminated in `cannot_tell` every time it was run, and the
verdict was honest. **Honesty with no obligation attached is indistinguishable from the question
having been answered.**

## What I am about to measure, and I do not know the answer

For every commit in which any commons artefact recorded `cannot_tell`, what did the block say
beside the verdict? This decides the DESIGN, not just the evidence:

- If those blocks carried **no reason at all**, a leg asking "name why the recipe did not
  terminate" catches them and is worth building.
- If they carried **a prose note that reads like a reason**, then a leg keyed to "something is
  written here" is satisfied by the very instances it exists to refuse — vacuous on its own
  subject — and the leg must demand something a stale block cannot supply.

I am registering that fork before looking, because the second outcome is the one that would tempt a
weaker control, and a control designed after seeing which shape passes is fitted to its answer.

## Predictions

| # | prediction | confidence | how it fails |
|---|---|---|---|
| P1 | `ofgem_cap_unit_rate_composition` records `cannot_tell` at commit `5a2778d06` | high — the landed finding says it sat there | it was never committed in that state, only observed live |
| P2 | at least two DISTINCT artefacts stood at `cannot_tell` in some committed tree | moderate | only the composition ever did, and the class is an instance |
| P3 | no artefact at HEAD today is `cannot_tell`, so the new leg is green on the live tree and CANNOT be shown reachable from it | high | one is still `cannot_tell` and I misread the report |
| P4 | **the stale blocks DID carry prose beside the verdict** — so a "names a reason" leg would pass vacuously on its own subject | moderate, and this is the one that matters | they carried a bare verdict and the naive leg is sufficient |

P4 is the prediction with something at stake. P1 and P3 are cheap and I expect to confirm both.

## What done means for the leg this produces

Not "the tree is green". The leg must be shown to REFUSE a real pre-repair block read out of the
commit that contained it — the shape `commons_citation_supports_provenance`'s NOT_AFTER leg used
against the RO entry in `5a2778d06` — and a poison round must show it can fire at all, because at
HEAD there is nothing for it to catch and a control green on an empty subject proves nothing.
