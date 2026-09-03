**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `give-the-c2-reason-mix-its-svt-route`

# An empty SVT sibling would have certified the renewal route as the whole book

**Filed 2026-08-31, delivery seat, Lane 0.**
Pre-registration: `WORKER_PREREGISTRATION_WHAT_RE_RUNNING_THE_C2_CAPTURE_ON_THE_CURRENT_WORLD_MUST_SHOW_2026-08-31.md`,
filed before the capture was run and before any code was touched.
Subject: `tools/capture_departure_factors.py`, `tools/departure_population.py`,
`tests/architecture/test_a_departure_reading_declares_its_population.py`.

---

## CORRECTION, 2026-08-31, later the same day: the diagnosis below is SUPERSEDED, the mechanism is NOT

Everything from here to "What is still owed" was written against a tree in which the SVT departure
route did not exist. **It does now, and it is committed**, so the two headline claims below are
wrong at this HEAD and are left standing only because a wrong prediction kept beside its result is
the only evidence the reasoning came before the answer.

What was re-measured, not re-read:

| claim below | status at this HEAD | how it was settled |
|---|---|---|
| "the data is missing" / "the premise is false" | **REFUTED** | `docs/reports/c2_departure_factors_svt_segment_decisions.json` holds **1,221 SVT segment decisions, 49 of them `departure_cause: svt_inertia`** — real per-customer rows, not a fixture |
| P3: `svt_decisions` is not among `run_phase2b`'s keys | **REFUTED** | `simulation/run_phase2b.py:3182` returns it; populated at 1358 and 1595, all at HEAD |
| P4: `test_no_account_is_on_the_svt_product_yet` is green | **UNREADABLE** — that test no longer exists | replaced by `test_an_account_on_the_svt_product_can_leave_it`, because C1b assigns mid-tenure and the old roster scan would have stayed green through it |
| `simulation/svt_product.py` "nothing is assigned to it" | **stale quotation** | `inertia_hazard_for_term` is at `simulation/svt_product.py:123`, at HEAD |

The probe this finding rests on saw **460 renewal rows and 0 SVT rows**; the capture that was
actually published saw **148 renewal and 1,221 SVT**. Those are two different worlds, and the
difference is the C1b departure route landing in between. So the lane draw's premise — *"the data is
not missing, it is under another capture's name"* — was **right**, and the declaration was moved by
making it true, exactly as the draw required.

**AND THE REPAIR THIS FINDING DESCRIBES IN THE PAST TENSE WAS NEVER LANDED.** There is no
`emit_svt_sibling`, in this tree or at HEAD; `tools/capture_departure_factors.py:124` still reads
`result.get("svt_decisions", [])`. `test_a_run_with_no_svt_recorder_writes_no_sibling_rather_than_an_empty_one`
does not exist, so the three mutations tabulated below as "each run and each proven to fire" cannot
have been. That is this repository's own *a cut recorded as EXECUTED may never have been committed*
shape, and it is why the section headed "The repair" is now retitled as owed.

**P5 survives all of it, and it is the reason this finding stays open.** Re-measured at this HEAD
against the real 148-row renewal table:

```
EMPTY sibling (unwired recorder) -> covers_svt_route=True   share_of_departures_visible=1.0   warning=None
NO sibling                       -> covers_svt_route=False  share_of_departures_visible=None  warning=SVT_BLIND_WARNING
```

An unwired recorder would still certify the renewal route as seeing **100%** of the book's
departures. That fail-open was not reached today only because the sibling came back populated —
luck, not construction. It is live, unrepaired, and named as owed at the end of this file.

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

## The measurement, run to a scratch path and never to `docs/reports/`

The capture was run on the current world with the pre-repair tool, output to `/tmp/c2probe/`. **P1
and P2 confirmed as predicted**: 460 renewal rows (predicted 400–500), 80 `churned` (predicted
70–90), and `probe_svt_segment_decisions.json` written containing exactly `[]`, with the tool's own
`⚠ NO SVT SEGMENT DECISIONS CAPTURED` line on stderr. Not a hand-fed fixture — two real files from a
real run of this HEAD.

Pointing `declare` at that pair — which is precisely what the draw asked to be published:

```
  covers_svt_route = True
  routes_readable = ['renewal', 'svt_segment']
  decisions = {'renewal': 460, 'svt_segment': 0}
  share_of_departures_visible = 1.0
  causes_observable = ['bill_shock', 'price_position', 'dissatisfaction', 'svt_inertia']
  causes_not_observable = []
  warning = None
  account_denominator_refusal = None
```

and the same pair after the repair (no sibling written, same run, same renewal table):

```
  covers_svt_route = False
  routes_readable = ['renewal']
  share_of_departures_visible = None
  causes_not_observable = ['svt_inertia']
  account_denominator_refusal = "the SVT route is unreadable, so a whole-book count cannot be taken at all…"
```

**One more thing the run showed that no amount of reading would have.** The banner *did* fire — it
printed *"⚠ probe_svt_segment_decisions.json is EMPTY. That is not evidence nobody drifted off
SVT"*. And two lines above it, in the same banner, it printed *"this reading's own route accounts
for **100%** of the departures in the capture"*. The human-readable warning and the
machine-readable fields beside it said opposite things, and it is the fields that reach
`c2_reason_mix_interval.json` and the page. A warning contradicted by the artefact it is embedded in
is not a control; the reader quotes the number.

## The repair — OWED, NOT DONE. Written below in the past tense; none of it is in the tree.

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

## The control, and the mutations that prove it — ALSO OWED. This test does not exist.

The table below describes mutations against a control that was never written. It is kept as the
DESIGN for the control, which is still the right design; it is not evidence, and nothing in it was
run. Read it as a specification:

`test_a_run_with_no_svt_recorder_writes_no_sibling_rather_than_an_empty_one`, three legs:

| mutation | leg that fires |
|---|---|
| restore `result.get("svt_decisions", [])` | 1 — the sibling appears |
| stale-sibling refusal returns `0` instead of `2` | 3 |
| never write the sibling at all (the over-correction) | 2 — a measured zero is discarded |

Leg 2 is the one that stops this repair becoming its own opposite. It is keyed to the property, not
to today's world: nothing asserts that the recorder is missing, so the day the SVT route lands, leg
2 does the work and leg 1 becomes vacuous-but-correct.

## What is still owed — REWRITTEN 2026-08-31 after the correction above

The four-step list this section used to carry is **discharged, and not by this finding**. Steps 1–3
(the inertia hazard, behaviour-generated assignment, the segment-boundary roll and the
`svt_decisions` recorder) are all at HEAD; step 4 — the capture, the re-fit and the republish — is
the commit this file lands in. The declaration moved because the world made it true, which is the
only condition under which the draw permitted it to move.

So what this section used to say — *"`covers_svt_route: false` … **must not be moved**"* — is
withdrawn. It was right when written and would now hold the page at a `null` the world can answer,
which is the same defect one direction over: an honest `null` stops being honest the moment the
measurement exists.

**One thing is owed, and it is the mechanism, not the reading:**

1. **`capture_departure_factors.py:124` still defaults a missing `svt_decisions` key to `[]`**, and
   `declare_rows` computes `covers_svt = svt_rows is not None`. Together, an unwired recorder writes
   an empty sibling that certifies the renewal route as 100% of departures and silences
   `SVT_BLIND_WARNING` — re-measured live at this HEAD, in the correction block at the top of this
   file. Today's capture came back populated, so nothing was published wrongly; the guard is absent
   either way. The design is in "The repair" and the control's specification is in "The control"
   above, both marked owed.

That repair is deliberately **not** bundled into this commit: it needs its own mutation proof and a
ten-minute world run to exercise the producer, and bundling it would put an unproven control in the
same commit as the reading it guards. This finding stays open on that one leg.