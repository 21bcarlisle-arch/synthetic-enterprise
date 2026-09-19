**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — found while
landing the Lane 0 SVT-band item

# A false regulatory citation was corrected in the RENDERING and not in the SOURCE, so every regeneration reverts it

*Found by accident and confirmed on purpose: a test run during another turn's work regenerated
`site/data/simplified.json` and the diff REVERTED a landed correction. The correction had been
applied to the published artefact and never to the file the generator reads.*

---

## The mechanism

`tools/generate_simplified_data.py` reads each atom's notes from
`docs/design/simplifications/*.yaml` and copies them **byte-identically** — its own comment says so:
*"`notes` stays byte-identical (rule 5: the site is a rendering, never an edit)"*. So the rendering
can never differ from the source unless somebody edited the rendering.

Somebody did, on 2026-09-03:

| | text |
|---|---|
| `docs/design/simplifications/DD_seasonal_cashflow_physics.yaml` (source) | `Ofgem SLC 27B +/-5pct variance` |
| `site/data/simplified.json`, `site/data/dashboard.json` (rendering) | `Ofgem SLC 27.15 duty with our own +/-5pct band -- there is no SLC 27B; corrected 2026-09-03` |

**There is no SLC 27B.** The correction is right and the citation it replaced is a reference to a
regulation that does not exist. It reached the two published artefacts by hand and never reached the
one file that regenerates them, so the committed bytes were the only thing holding it — and the next
`process_run_complete` would have published the false citation back onto the live site with nothing
anywhere able to notice.

That the correction is *sixteen days old* and survived only as hand-edited bytes is the part worth
keeping: it means no regeneration ran in that window, and the first one that did would have undone
it silently.

## Why nothing caught it

The rendering-vs-source comparison that would catch this is the generator itself, and it only runs
forwards. Nothing compares the published bytes against what the generator WOULD produce, so an edit
applied downstream of a byte-identical copy is invisible until the copy runs again. This is the
project's own catalogued shape — *the generator re-draws what the reporting call fixed* — with the
twist that here the fix was never in the generator's reach at all.

## What was done

The source `.yaml` now carries the corrected sentence verbatim, and re-running
`python3 -m tools.generate_simplified_data` moves **only** `generated_at` — which is the proof the
two sides now agree and the correction survives regeneration.

## What was NOT done, and is the next piece

**Nothing checks that a published `site/data/*.json` matches what its generator would produce.** This
instance is repaired; the class is not. Any other hand-edit to a generated artefact — there is no
reason to think this was the only one — sits in exactly the same state right now: correct on disk,
reverted at the next regeneration, and unobservable in between.

The smallest mechanism that could fail here is one leg: regenerate into a temp location and compare
every key except the timestamps. It is a one-file control and it would have caught this on the day
it was made. It is NOT built here, because building the control that watches the work is the second
job and this turn's first job was landed elsewhere.
