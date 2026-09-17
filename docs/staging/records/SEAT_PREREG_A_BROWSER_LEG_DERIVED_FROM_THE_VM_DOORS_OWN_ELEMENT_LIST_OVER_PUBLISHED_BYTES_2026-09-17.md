# PRE-REGISTRATION — what a browser reading of every published door will find, before I look

**Severity: INFO** — a prediction, filed before the measurement, so the measurement can refute it.
**Filed:** 2026-09-17, delivery seat, claim
`the-vm-backed-door-suites-still-have-no-browser-leg-and-only-one-of-twenty-four-was-ever-built`.

## The question

`site/harness/test_the_deployment_reading_is_visible_to_a_browser.py` is the only per-suite browser
leg in the tree. The other ~24 vm-backed door suites grade what the page COMPUTED inside node's
`vm` and call it what a person READS. G4 (`live_pixel_verify`, landed `e18ca3ab4`) takes the reader
side for every DEPLOYED door against the live host — but it is a door-close tool, costs a browser
launch per door, and is in no gate. Nothing in the COMMIT path takes a reader-side reading.

I intend one control, not twenty-four files: for every published door page, derive the element list
the way G4 does — **from the vm harness's own output**, the ids the door's script actually wrote
content into — then read those same ids in chromium against the PUBLISHED (index) bytes served over
local http. Nothing hand-kept; the population and the element list are both derived.

## What I do not know, and am predicting

The measurement is: run that derivation over all 22 published `index.html` pages and count the
elements that fail `exists` or `visible`.

**P1. Population.** ~22 pages, of which 2 are static (no inline script: the Front Door and
`/privacy/`) and get only the `:body` whole-page reading.
**P2. `exists` failures: ZERO.** Every id a door's script writes into is in that door's markup
today. If this is wrong, the control has found a live instance of breakage C — the vm minting an
element that is not on the page — and that is a finding, not a bug in the control.
**P3. `visible` failures: ZERO to THREE, and if non-zero they are legitimately-hidden-on-load
panels** (a tab body, a details pane, a stage a reader has to click into) rather than defects.
**P4. Wall-clock:** 22 chromium launches at ~2.5s ≈ 55s; with a single launch driving all 22 pages,
≈ 35s.

## What each outcome means, decided now

- **P2 or P3 refuted with a REAL defect** → the defect is the finding; the control lands red-by-
  design only if I cannot fix the page this turn, and the finding says which.
- **P3 refuted by legitimately hidden panels** → I do **not** write an exception set. An exception
  set beside a guard is this project's recorded fail-open shape. The honest narrowing is a property:
  the `visible` clause applies to elements the page renders ON LOAD, and "on load" is decided by the
  browser, not by a list of names. If no such property can be stated, the `visible` clause is
  dropped to `exists` + a whole-page `:body` reading and the gap is stated on the surface.
- **P4 refuted upward (> 3 minutes)** → the control moves out of the per-commit selection and says
  so in its own docstring, rather than silently costing every lane three minutes.

I am writing this before running anything. The result goes in the WORKER_RESULT beside it, next to
this prediction, whichever way it falls.
