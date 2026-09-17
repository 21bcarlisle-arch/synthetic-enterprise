# RESULT — the reader-side sweep's first derivation filtered out the one element a reader loses

**Severity: LATENT** — the hole was found and closed inside the turn that built it, by the mutation
that was supposed to prove the control worked. Filed as a class instance because the SHAPE is one
this repository keeps paying for, not because this instance survived.

**Class:** `controls_that_cannot_fail`.
**Prediction filed before the measurement:**
`SEAT_PREREG_A_BROWSER_LEG_DERIVED_FROM_THE_VM_DOORS_OWN_ELEMENT_LIST_OVER_PUBLISHED_BYTES_2026-09-17.md`,
beside this file. Claim
`the-vm-backed-door-suites-still-have-no-browser-leg-and-only-one-of-twenty-four-was-ever-built`.

## What was built

`site/test_every_door_element_a_reader_meets.py` — one control, not twenty-four legs. For every
published (index-copy) door it drives the page's own script under node's `vm` via
`_live_harness.mjs`, takes the element ids out of that run's OWN OUTPUT, and reads those same ids in
chromium against the same published bytes served over local http. Nothing is written down: the door
list is globbed out of the extract and the id list is the harness's output, so a door that gains a
section gains coverage the same day.

`site/_browser_probe.mjs` gained a `--jobs` form: one chromium launch drives every page.

## The prediction against the result

| | predicted | measured |
|---|---|---|
| population | ~22 doors, **2 static** | 22 doors, **1 static** (`/privacy/`) — the Front Door renders client-side |
| `exists` failures | 0 | **0** |
| `visible` failures | 0–3, legitimately hidden panels | **0** |
| wall clock, one launch | ~35s | **30s** (22 separate launches: 3m14s) |

So the tree is clean on the reader side today, and the control goes green on a correct tree — which
is the thing a "no element is broken" sweep most needs proving about itself.

## THE FINDING: the derivation filtered out exactly the element that matters

The first derivation took the ids the door's script **wrote content into** — the same rule G4 uses
on the live host. Three breakages were then constructed on `/harness/` to prove the control could
fail:

* **A** a `#deployment { display: none }` rule in the page's own `<style>` → **fires** (`visible`)
* **C** the container renamed to `#deployment-panel` → **fires on both legs**: `exists` for the
  renamed container, and `visible` for `#corrections` and `#control-kpis`, the two sections the
  swallowed TypeError left at zero height. That cascade is the defect exactly as it was measured on
  2026-09-17, now caught before it deploys instead of after.
* **B** a later inline `<script>` clearing the section → **DID NOT FIRE.**

B not firing is the finding, and it took two attempts to establish which kind of not-firing it was.

1. The first B cleared `#deployment` synchronously. That is **an equivalence, not a hole**: the
   harness page renders from `fetch(...).then(...)`, so in a real browser the clear runs at parse
   time and the render fills the section afterwards. It is not a breakage at all, in either half.
   The construction in `WHAT_THE_VM_DOORS_GRADE.md` only breaks a page whose render is synchronous.
2. The second B deferred the clear (`setTimeout(..., 300)`) so it lands AFTER the render. That one
   leaves a reader with a dead section — and it **still passed**, because `_live_harness.mjs` maps
   `setTimeout(fn, delay)` to `setTimeout(fn, 0)`, so the clear fires in the vm too, the element
   comes back empty, and the "wrote content" filter **drops it from the sweep's own subject**. The
   control never asks the browser about the one element the reader just lost.

That is the recorded shape *a control's own filters empty its evidence, and the guard reads empty as
no complaint*. The remedy is not an exception: the subject is now **every element the door's script
asked for**, `getElementById` included, whether it ended up with content or not. Measured before
adopting rather than argued — over the 22 doors the wider subject is **417 ids against 414, and all
three extras read visible**. The filter was buying nothing and costing the element that mattered.
With it removed, deferred-clear B fires (`#deployment ... box=820x0`).

## What is NOT covered, stated here rather than discovered later

An element the door's script never mentions is outside this subject, so a section deleted from BOTH
the markup and the script is invisible to this file. That is the vm suites' question — they assert
the words — and it is why this is an addition to them, not a replacement.

## Mutation record

| mutation | leg that fires |
|---|---|
| `#deployment{display:none}` in the page's `<style>` | `..._is_visible_to_a_reader` |
| `<div id="deployment">` → `#deployment-panel` | `..._exists_on_the_page_a_reader_gets` **and** `..._is_visible_to_a_reader` |
| deferred `<script>` clearing `#deployment` after the render | `..._is_visible_to_a_reader` |
| derivation returns no ids (the fail-open) | `test_the_sweep_can_fail` |

Each was applied to the **index** (the sweep reads the published copy, so a working-tree edit is
invisible to it) in this isolated worktree, and reverted.

## Still owed

The per-door browser leg that names a door's OWN sections and their own words exists for exactly one
door (`site/harness/test_the_deployment_reading_is_visible_to_a_browser.py`). This sweep does not
replace it — it grades readability, never content — and the remaining ~23 doors still have no leg of
that kind. That is a smaller gap than it was: the class of defect (A, B, C) is now caught for all 22
doors in the commit path, and what is left is per-door wording.
