**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

*RECORDED, not LATENT: a pre-registration refutes nothing on its own. It exists so the measurement
filed beside it can be shown to have been designed before its answer was known.*

# Pre-registration: what the first NATIVE SVT capture must show

**Filed 2026-09-01, delivery seat, Lane 0, AFTER launching `tools/capture_departure_factors.py` and
BEFORE reading a single line of its output.** The run was started against
`/tmp/svtcap/c2_marketterm.json` at the commit below; nothing in this file was written with a result
in view.

---

## Why this run is possible today and was not yesterday

`WORKER_FINDING_THE_SVT_ROUTE_CAN_NOW_SEE_THE_MARKET_AND_THE_NEXT_GATE_IS_A_STALE_CAPTURE_2026-09-01.md`
closed with four owed items and called item 1 **the binding one**:

> **Land the SVT departure route's recorder in `run_phase2b`** so a capture can be regenerated.
> Until then no whole-book anchor can be emitted by the ordinary route. This is the binding item and
> it is in another lane.

**That item is discharged, and I did not discharge it — I found it already done.** `run_phase2b.py`
carries `_svt_decisions` at line 1419, appends at 1656, and returns `"svt_decisions": _svt_decisions`
at 3244. All three are **in `HEAD`**, verified with `git show HEAD:simulation/run_phase2b.py` rather
than by reading the working tree, because this repo has paid for exactly that confusion
(`WORKER_FINDING_A_PUBLISHED_CAPTURE_WAS_PRODUCED_BY_CODE_THAT_WAS_NEVER_COMMITTED_2026-08-31.md`).
It landed at **`6db30a350`** — *"the SVT belief can finally tell two households apart, and it is
still inside its null"* — a commit whose headline claim is about something else entirely, which is
why the finding one lane over could still call the item outstanding in good faith.

**So this is the first capture in this repo's history whose SVT sibling has a producer in git.**
Every SVT sibling read by any instrument to date is the 1,266-row foreign artefact at `87709c617`,
whose producer is in no commit and whose renewal table is a different run
(`WORKER_FINDING_A_FOREIGN_SVT_SIBLING_IS_WHAT_MAKES_THE_ACCOUNT_DENOMINATOR_CONTROL_PASS_2026-08-31.md`:
144 renewal decisions over 68 accounts against 1,266 SVT decisions over 116 accounts, only 53 shared).

**A stale docstring is filed alongside, not fixed here.** `tools/capture_departure_factors.py`'s
module docstring still asserts *"At this HEAD that is every run: `run_phase2b`'s return dict has 63
keys and `svt_decisions` is not one of them"*. `6db30a350` falsified that sentence and did not edit
it. It is a false statement in a live module, and it is the sentence a reader consults before
deciding whether re-capturing is worth ten minutes — so it is load-bearing, not cosmetic.

**Captured to a stem of its own, deliberately.** `/tmp/svtcap/`, not `docs/reports/`. `emit_svt_sibling`
refuses to leave a stale sibling beside a fresh renewal table because every reader joins the two as
one capture; writing to the live stem would have put a fresh table beside the foreign 1,266-row
sibling and made that refusal my problem instead of a diagnostic.

---

## The predictions

Five, each with a direction and a magnitude, each falsifiable by the run now in flight. **This is
deliberately not an invariance**: an invariance measured on the old code embeds the defect being
removed.

### P1 — a sibling is written, by a producer in git, and it is not a measured zero

`emit_svt_sibling` reads `result.get("svt_decisions")` with **no default**, so the three outcomes are
distinguishable. Predicted: the key is **present** and the list is **non-empty** — a sibling file is
written and neither stderr warning fires.

*Refuted by:* `⚠ NO SVT RECORDER IN THIS RUN` (key absent — `6db30a350` does not reach the return
path I read), or `⚠ THE SVT RECORDER RAN AND RECORDED NOTHING` (present but empty — the product
exists and no roster assigns it, which `test_svt_product.py::test_no_account_is_on_the_svt_product_yet`
asserted as recently as 08-31).

**P1 is the one I am least sure of, and I am saying so before the answer.** The empty case is live:
if no roster assigns the SVT product in a default `run_phase2b`, the recorder runs and records
nothing, and that is a *measured zero* rather than a failure. If P1 lands empty, the finding is that
the route exists in code and carries no accounts — which would make the 61%-of-departures figure a
property of the foreign artefact and not of this world, and that is a bigger finding than the one I
set out to file.

### P2 — the staleness leg goes to exactly zero

`svt_composition_refusal` classifies each row into `unanchored` / `anchored` / `market_blind` /
`neither`, in that order. Predicted: **`market_blind == 0` and `unanchored == total`.**

The mechanism: the world now runs the market-factored hazard, and the refusal reconstructs `raw`
with the same factor from each row's own `market_year`, so every row matches the *first* branch.
Note the branches are ordered and mutually exclusive — rows from 2019–20, where `factor ≈ 1.0`,
match `unanchored` before `market_blind` is ever evaluated. So `market_blind == 0` is **not**
evidence that those years are market-blind, and I am recording that here so the count is not
over-read afterwards.

*Refuted by:* any non-zero `market_blind` (the run did not use the term the fit assumes), any
non-zero `anchored` (the world multiplies the level anchor into the SVT route, which would make the
whole-book fit's held-fixed contribution wrong), or any non-zero `neither` (mechanism disagreement).

### P3 — the account-denominator refusal is the coin-flip, and I predict it LIFTS

`account_denominator_refusal` refuses on three properties: rows with no `customer_id`, an account
departing **more than once**, and an account invisible **between** two of its own decisions.
Predicted: **returns `None`.**

The argument for lifting: the foreign sibling failed the *provenance* question, not these three, and
a single coherent run cannot produce the 63-SVT-only / 15-renewal-only split that made the joined
pair incoherent. Both routes now come from one `run_phase2b` over one roster.

**The argument against, which I am filing because it is real:** the prior finding's title is that a
*foreign* sibling is what makes this control **pass**. A native capture puts renewal and SVT
decisions for the *same* account into one union for the first time, and if a household can churn on
the SVT route and also reach a renewal roll that records a departure, `twice` fires. Predicted
`None`, with maybe 65% confidence — and if it refuses on `twice`, **that is a finding about the
world (a departure is not terminal), not about the capture**, and it must not be repaired by
de-duplicating in the reader.

### P4 — a whole-book fit is emitted for the first time

Conditional on P1, P2 and P3. Predicted: `── WHOLE-BOOK FIT ──` prints and per-year anchors are
emitted, replacing the standing `REFUSED — no YEAR_LEVEL_ANCHOR block is emitted from this capture`.

### P5 — 2022 is reachable, and the other nine years are too

Predicted: **2022's SVT floor lands below its 4.30% target**, so the year is `reachable` and the
renewal anchor for it is a positive finite number. Magnitude: floor in **1.5%–3.5%**, straddling the
**2.33%** / **2.34%** the two diagnostic runs recorded, and *not* equal to either — this is a third
population.

Predicted: **2023's renewal anchor is above 1.0** and no longer the **0.03** that made the priceable
route near-extinct. Predicted range 1.5–3.5, widened from the 1.3–2.0 I got wrong last time, on the
same measured evidence (2.4417) rather than on hope.

*Refuted by:* any year printing `NOT FITTED — unreachable: SVT alone expects …`.

**Absolute counts will differ from both prior tables and that is not a result.** The denominator has
moved twice already today (2022: 55 → 52 accounts). Differencing a cell across two populations
measures the population, not the hazard.

---

## What must NOT happen when this is scored

Named in advance so the flattering repair is not available afterwards:

1. **No constant is pasted into `simulation/departure_level_anchor.py`** on the strength of one
   capture, however green. If P4 lands, the fit emitting a block is the result; adopting it is a
   separate decision with its own evidence.
2. **No widened band and no clamp on 2022.**
3. **`population_anchor._churn_by_year` is not repaired by inserting a `sim_churn_rate` of 0.0** for
   2022. That publishes a measured zero-churn crisis year. Its arithmetic consumers fail closed.
4. **If P3 refuses on `twice`, the reader is not de-duplicated.** The refusal is then correct and the
   question moves to the world.
