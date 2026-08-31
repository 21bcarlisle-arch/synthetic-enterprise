**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `give-the-c2-reason-mix-its-svt-route`

# An empty SVT sibling would have certified the renewal route as the whole book

**Filed 2026-08-31, delivery seat, Lane 0.**
Pre-registration: `WORKER_PREREGISTRATION_WHAT_RE_RUNNING_THE_C2_CAPTURE_ON_THE_CURRENT_WORLD_MUST_SHOW_2026-08-31.md`,
filed before the capture was run and before any code was touched.
Subject: `tools/capture_departure_factors.py`, `tools/departure_population.py`,
`tests/architecture/test_a_departure_reading_declares_its_population.py`.

---

## The instruction, and why carrying it out would have been the defect

Lane 0 drew: *"Re-run `tools/capture_departure_factors` … so the sibling
`c2_departure_factors_svt_segment_decisions.json` exists, then re-fit and republish … **the data is
not missing, it is under another capture's name.**"* It also said, correctly: *"do not touch the
declaration except by making it true."*

**The premise is false, and the two halves of the instruction are in conflict.** The data is
missing. Re-running the capture would have created the sibling and, by creating it, replaced a true
declaration with a false one.

## What the world actually contains

`067a00dfd` — the commit the C1b work is attributed to — landed the SVT **product**, not the SVT
**departure route**. `simulation/svt_product.py` says so in its own words:

> *"An account on this product cannot currently leave. … **So the product exists and settles, and
> nothing is assigned to it.**"*

and lists what is owed before assignment: an inertia hazard, assignment generated from behaviour,
and the published fixed/SVT split printed beside the result as a check.

Confirmed at this HEAD, both legs of the pre-registration:

* **P4 — green.** `tests/simulation/test_svt_product.py::test_no_account_is_on_the_svt_product_yet`,
  7 passed. No account is on the product, so there is nothing for a recorder to record.
* **P3 — confirmed statically.** `simulation.run_phase2b.main()` returns a dict of **63 keys** and
  `svt_decisions` is not one of them. The only `svt`/`churn` keys are `churned_billing_accounts`,
  `churn_basis_risk`, `no_offer_churn_log`, `company_gas_churn_log`, `churn_model_performance`,
  `churn_journey_log`.

So the 1,266-row siblings under `ladder_churn_factors*` were produced by a working tree carrying
another lane's uncommitted departure roll *and* an uncommitted `_svt_decisions` recorder.
`tests/architecture/test_churn_carries_per_customer_signal.py:19-26` says exactly this — and it says
it in a **comment**, which is the same failure mode this whole area was repaired for in
`b8e6ba32d`: *"a deliberate debt taken at a seam needs something that FAILS; a named comment is
neither."* The comment was right and it did not act; the lane draw was written straight past it.

## The defect, and it was four characters wide

`tools/capture_departure_factors.py` read the run's recorder as:

```python
svt = result.get("svt_decisions", []) if isinstance(result, dict) else []
```

That `[]` default collapses the two states the entire two-file design exists to keep apart —
**"the recorder ran and nobody drifted off SVT"** and **"there is no recorder"** — into the same
empty file. And this is the *only* place in the chain where they are still distinguishable, because
only here is the run's own return dict in scope.

`tools/departure_population.load_svt_decisions` states the rule in its docstring — *"'nobody was on
SVT' and 'the recorder was never wired' produce the identical artefact and a reader must not have to
tell them apart by inference"* — and then discriminates on `None` vs `[]`, which is a fact about
**whether a file exists**, not about whether anything was measured. Under the producer above, an
unwired recorder lands squarely on the `[]` branch that `declare_rows` counts as coverage.

**P5 — confirmed by direct measurement**, feeding `declare_rows` the real 465-row renewal table and
an empty SVT list:

| field | today (honest) | after re-running the capture |
|---|---|---|
| `covers_svt_route` | `false` | **`true`** |
| `routes_readable` | `['renewal']` | **`['renewal', 'svt_segment']`** |
| `share_of_departures_visible` | `null` | **`1.0`** |
| `causes_not_observable` | `['svt_inertia']` | **`[]`** |
| `causes_observable` | 3 causes | **4 causes** |
| `warning` | `SVT_BLIND_WARNING` | **`null`** |
| `account_denominator_refusal` | refuses | **`None`** — a "whole-book" rate over renewals only |

Every one of those is the reading certifying its own blind spot, off a file that measured the SVT
route not at all. `share_of_departures_visible: 1.0` is the sharpest: the C2 mix would have declared
that the renewal route accounts for **100%** of the book's departures, on the same page whose
existing text records the route it cannot see as *"the single largest departure route in a real
domestic book"*.

This is the R15 fail-open shape the catalogue already names — **a missing quantity arriving as a
small one** — with the extra twist that the control written to catch it,
`test_an_unreadable_route_is_not_reported_as_an_empty_one`, **asserts the fail-open in its
assertions while forbidding it in its docstring**.

## The repair

Not "flip the assertion". The test's counter-argument is right as far as it goes: an empty sibling
that is genuinely a measurement must stay a measurement, and reporting it as blind would discard a
real reading. The information needed to tell the two apart exists — it is just thrown away. So the
repair carries it through instead.

1. **`tools/capture_departure_factors.emit_svt_sibling`** (split out of `main` so a control can
   reach it without a ten-minute world run) reads the key with **no default**. Absent → **no sibling
   is written**, loudly, and downstream declarations correctly report `covers_svt_route: false`.
   Present, even empty → written, because that is a measured zero.
2. A **stale sibling beside a fresh unwired run is refused** (rc 2), not silently left: the two files
   would describe two different runs while every reader unions them as one capture. Refused rather
   than deleted — removing another lane's committed artefact from inside a capture tool is a bigger
   blast radius than this needs.
3. `svt_sibling` is now imported from `departure_population` rather than the path convention being
   spelled a second time in the producer.
4. `load_svt_decisions`'s docstring records why the sentence it already carried did not save
   anyone, beside the sentence.

**`[] → covers_svt_route: true` is left exactly as it was, and is now true by construction rather
than true by luck.**

## The control, and the mutations that prove it

`test_a_run_with_no_svt_recorder_writes_no_sibling_rather_than_an_empty_one`, three legs, each run
and each proven to fire (2026-08-31, `python3 -B`):

| mutation | leg that fires |
|---|---|
| restore `result.get("svt_decisions", [])` | 1 — the sibling appears |
| stale-sibling refusal returns `0` instead of `2` | 3 |
| never write the sibling at all (the over-correction) | 2 — a measured zero is discarded |

Leg 2 is the one that stops this repair becoming its own opposite. It is keyed to the property, not
to today's world: nothing asserts that the recorder is missing, so the day the SVT route lands, leg
2 does the work and leg 1 becomes vacuous-but-correct.

## What is still owed, and it is not a capture

**The C2 reason mix cannot be given its SVT route from this tree.** The blocker is the world, not
the artefact, and the queue entry should say so. In order, from `simulation/svt_product.py`'s own
list:

1. an inertia hazard — `simulation.departure_risks.svt_inertia_hazard` **already exists** and is
   reached by nothing in `simulation/`; only `tools/` and `company/` call it;
2. assignment generated from behaviour, so accounts actually sit on the product;
3. the departure roll at the segment boundary, plus an `svt_decisions` recorder on
   `run_phase2b`'s return;
4. *then* the capture, the re-fit, and the republish the draw asked for — at which point the
   declaration becomes true because the world made it true.

Until then `covers_svt_route: false`, `causes_not_observable: ['svt_inertia']` and
`share_of_departures_visible: null` are the correct published values and **must not be moved**. An
honest `null` with a named reason is worth more than a plausible number, because the number will be
read as established and the `null` cannot be.
