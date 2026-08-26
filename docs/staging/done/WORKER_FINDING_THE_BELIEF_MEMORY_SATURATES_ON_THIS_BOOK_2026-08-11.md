# WORKER FINDING — the belief dimensions cannot see a company that never forgets

**Severity:** LATENT · **Lane:** H_harness

**Atom:** `H27_payment_belief_gap` — Expert Hour **#9**, on the corrected instrument
**Date:** 2026-08-11 (worker tick) · **Reshape minted as:** `D27_belief_window_saturates_on_this_book`
**Class:** `DIMENSION_DRIFT_RESOLUTION`'s **OFF-PATH state** — fifth escape of a register's own keying

Hour #8 left three leads in order. The first: *"`belief` and `belief_population_mix` are OFF this
drift's path, so their smallest visible company error is still unmeasured — no counterfactual organ
knob for the arrears-severity belief exists in this harness at all."* It is the defect, and the hole
was one level up from where the lead pointed: it is not that the knob was missing by oversight, it is
that the register's off-path STATE never required one.

## The class — an indiscriminate degenerate is not a resolution measurement

D25 built `DIMENSION_DRIFT_RESOLUTION` to ask what the **smallest company error each published
dimension can see**. On-path entries answer it with a graded band (`invisible_drifts` /
`visible_drifts`, measured by re-scoring against a declared counterfactual company). The **off-path**
state — the exemption shape D21 hid behind for five Hours — was given a weaker rule: name an
`exercised_by` probe and have it MEASURED to move the dimension. Both belief dimensions named
`HEADLINE_DIRECTION_COVERAGE`, whose probe is the dimension's own **indiscriminate degenerate**.

A degenerate is the **largest error there is**. It establishes that a dimension is not inert and
measures *no resolution whatever*. So two of five published dimensions had no measured resolution at
all — inside the register built to close exactly that hole.

## The finding — the shipped company sits 309 days inside its own blind band (observed, R9)

Both belief dimensions read exactly **one** company parameter: `_dd_failure_window_days`, how far back
`PaymentObservationConsumer._arrears_risk_belief` still counts an observed failed collection. An event
at age `a` is counted iff `a <= window`. This book's **oldest observed failure is 91 days old** at
`as_of`, and the harness builds the company with `DD_FAILURE_WINDOW_DAYS = 400`.

So no event can ever fall out of that memory. Measured against a **new declared counterfactual
company** — `organ_failure_window_drift_days`, the supplier holding the wrong lookback window; the
world comes out bit-identical record-for-record, asserted inside the measurement — n=300,
**bit-identical on seeds 7 / 11 / 23**:

| company memory drift | what the company is | `belief` (seed 7 / 11 / 23) |
|---|---|---|
| `-308 d` (window 92) | forgets 308d sooner | **0.151899 / 0.191358 / 0.135294** — unchanged |
| **`0` (shipped, 400)** | the scored company | **0.151899 / 0.191358 / 0.135294** |
| **`+1 d` … `+500 d`** | **never lets a failure go** | **0.151899 / 0.191358 / 0.135294** — unchanged |
| `-310 d` (window 90) | forgets 310d sooner | 0.170886 / 0.203704 / 0.141176 |
| `-320 d` (window 80) | forgets 320d sooner | 0.246835 / 0.228395 / 0.200000 |

Three things:

- **The band is UNBOUNDED ABOVE.** Every window from ~92 days to infinity publishes one number. The
  figure cannot distinguish the scored company from one that **never forgets a failure** — the
  direction that keeps a recovered customer sitting in collections. That direction is not merely
  coarse here; it is *structurally invisible at every magnitude*.
- **The organ's own default is outside the band.** `PaymentObservationConsumer` ships
  `dd_failure_window_days=90`, and at 90 the published gap is **0.1709** against the scored 0.1519 at
  seed 7 (+12.5%). So the harness scores a company it configured 4.4x past the organ's own default,
  and that choice moves the published number.
- **A design note stood in for a measurement.** The 400 is deliberate and its reason is still in the
  constant's comment — *"Generous on purpose: isolates the CHANNEL blind spot as the thing this
  scenario measures, rather than letting the belief's own recency-decay window confound the
  reading."* That reason is sound. What was never measured or declared is that the same choice costs
  the dimension **all** resolution on the only company parameter it reads. Hour #5's lesson, again.

Same shape as D25 and D26, one boundary further out: **the book has no event sitting BESIDE the line
this dimension reads.**

## What was closed at the class (R10), and what was not

**Not fixed on sight** — moving the window (or lengthening the book) moves every published belief
figure on this pair, so the reshape is minted as **atom D27** at L0, not applied under an Hour.

Closed here:

1. **`organ_failure_window_drift_days`** — the third declared counterfactual company in this harness,
   and the first that reaches this organ at all. It lives on `build_scenario` (the window is a
   constructor argument, so the counterfactual must be *built*), never in a test's monkeypatch — the
   D20 rule. It refuses a negative memory rather than constructing one.
2. **Off-path entries now owe a graded band.** `_check_off_path_entry` requires an `own_drift`; a new
   sibling control `measure_own_drift_resolution` / `check_own_drift_resolution` measures each
   off-path dimension against its **own organ's** knob and puts the declared band on trial with the
   same EXACTNESS rule D25 earned (a band that may only shrink is the decay the register exists to
   stop), plus two rules this state needs: **unbounded-above is its own violation class** (a positive
   invisible drift means saturation, and the book must independently agree), and the band must be
   owned by an `own_debt_atom`.
3. **The measurement is DIFFERENTIAL and R13-clean.** The knob must move the dimensions that declare
   it and **not** the ones that do not (measured: it moves only the two belief dimensions, on every
   seed, while `ageing` / `detection` / `detection_latency` are bit-identical), and the world it
   builds is compared record-by-record against the undrifted one.
4. **A population-side predictor, independent of the organ.** `measure_belief_window_resolution`
   derives the resolution from the **world's own event dates** and the declared window — never from
   `_arrears_risk_belief`'s severity thresholds, whose hand-copy was the D20 defect and whose literal
   import was D21's. It predicted the smallest visible memory error at **310 days**; the drift sweep,
   re-scoring through the dimension's own shipped scorer, measured **310**. The test asserts the
   predictor's *code* (AST, docstring excluded) never names the organ.
5. **The caveat is stamped AT SOURCE** on both belief dimensions — `note` **and** `components`
   (the ledger writer, live wiring and dashboard read components and never the prose — D22) — and
   **re-derived from the book each call**, so a live `run_phase2b` population no sweep has visited
   carries its own resolution rather than the offline scenario's.
6. **It runs in the CLI**, not only in the tests — a control the reader about to quote a belief gap
   never meets is one that protects the test suite, not the figure (D25's rule).

## R15 — proven both ways

- **On the register (7 mutations):** the off-path exemption returning (`own_drift` removed →
  *"measures NO resolution"*), an understated band, an overstated sight, a debt entry outliving its
  debt, an unowned hole, and a declaration checked against a reading nobody took.
- **On the source (3 mutations):** an **inert probe** (the knob silently stops drifting → *"moved
  NOTHING"*), a knob that **moves everything** (→ *"off its own organ"*), and a counterfactual that
  changes the **world** rather than the company (→ *"CHANGED THE WORLD"*).

## Evidence

- `tools/couple_w2_11_d5.py` — `organ_failure_window_drift_days`, `measure_own_drift_resolution`,
  `check_own_drift_resolution`, `_check_own_band`, `_world_fingerprint`,
  `measure_belief_window_resolution`, `belief_resolution_caveat`, the `own_drift` register block, and
  the control printed in the CLI.
- `tests/tools/test_couple_w2_11_d5.py` — 10 new tests, **302 green** (was 271).
- CLI, live: `belief blind to [-308, -100, -1, 1, 500], sees [-380, -350, -320, -310] … book: 102
  failure events, oldest 91d vs a 400d memory -> SATURATED … 309d headroom … verdict: every
  declaration held`.

## Hour #10 leads, in order

1. The two leads Hour #8 left and this Hour did not take: the pinned generated value
   `assert c["n_recon_detected_undated"] == 0`, and whether the other dimensions' normalisation notes
   have the same gap between what they DENY and what they ESTABLISH.
2. **The on-path entries have never been checked for saturation the way this one now is.** The
   unbounded-above rule fires only where a positive drift is declared invisible — no on-path band
   declares one, so the rule has never been asked of `detection` or `ageing`.
3. `DD_FAILURE_WINDOW_DAYS = 400` is not the only harness constant chosen to *remove* a confounder.
   Each such choice is a resolution decision taken silently; the census of them has not been made.
