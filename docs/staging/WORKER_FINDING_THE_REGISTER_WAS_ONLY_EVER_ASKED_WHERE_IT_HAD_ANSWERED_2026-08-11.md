# H27 EXPERT HOUR #10 — the resolution register's grid was its own claims

**Severity:** BLOCKING · **Lane:** H_harness

**Atom:** `H27_payment_belief_gap` (2→3 HARDEN draw, worker tick, 2026-08-11)
**Verdict:** HELD AT L2. Tenth Hour, tenth defect, and this Hour changed the instrument again.
**Lead taken:** Hour #9's lead 2 — *"the on-path entries have never been checked for saturation the
way this one now is"* — which on measurement turned out to have a cause one level up, and that cause
is lead 3's *"each such choice is a resolution decision taken silently"*.

---

## The finding, measured not asserted

**THE REGISTER WAS ONLY EVER ASKED WHERE IT HAD ALREADY ANSWERED.**

`check_dimension_drift_resolution` **derives its keyset** from what `score_triad` publishes — D25
removed that keying, and a published dimension with no entry now RAISES. Its **grid** was still built
the other way round:

```python
drifts = {0} | declared invisible | declared visible | declared collapsed pairs
```

So the exactness rule the register exists to enforce — *"a band that may only shrink is the decay this
register exists to stop"* — was applied **exactly at the points the band already named**. A blindness
nobody had guessed at was unreachable by construction, and two undeclared companies publishing one
number could not be seen at all. This is D23's `ORGAN_QUERY_GRID` class (a reading taken on a grid of
the harness's own making is quantised to that grid) escaped into the register built to close a
resolution hole. **Sixth escape of a register's own keying** — and this time only *half* the keying had
been removed: the *which dimensions* half, not the *which companies* half.

### What the grid the register did not choose finds

A grid derived from the **book** instead — every integer terms drift across one billing cycle either
way, 43 counterfactual companies, `n=300`, seeds 7/11/23, every run below identical on all three:

| dimension | declared before | measured on the dense grid |
|---|---|---|
| `detection` | blind to `{+1}`, sighted at `{-1}`, collapses **nowhere** | **7 collapsed runs, BOTH TAILS SATURATED** |
| `ageing` | sighted on 4 drifts | **43 distinct readings, no collapse anywhere** |
| `detection_latency` | sighted on 2 drifts | one tail run `{-21,-20,-19}` |
| `belief`, `belief_population_mix` | off-path | flat across all 43 (off-path confirmed, measured) |

`detection` saturates **below -6d** and **above +17d**. Every supplier holding terms **6 to 21 days
shorter** than the world publishes **ONE** bit-identical figure — sixteen companies, one number, every
seed — and every supplier 17 to 21 days longer publishes another. In between it is quantised rather
than continuous: `{-4,-3}`, `{0,+1}`, `{+6,+7}`, `{+9,+10}`, `{+11,+12,+13}`.

**The witness that this was unreachable, not merely unnoticed:** `-8d` *was* on the old grid — it was
in the *ageing* band — and the register read it as **MOVED**, i.e. as evidence of resolution. It sits
inside the saturated tail, indistinguishable from `-21d`. The old grid could confirm exactly **one** of
detection's seven collapses (the `{0,+1}` pair, because `+1` was the one drift it had declared).

**What it costs the reader.** A movement in the detection headline is not readable as days of company
error, and the `-6d` direction is the one that matters: a supplier whose terms are a week short flags
paying customers as in arrears and posts the dunning letter. This instrument cannot tell that supplier
from one three weeks out.

### Why this is the class and not the instance

D27 — **last Hour** — built the saturation rule (*"if a POSITIVE drift is invisible the parameter is
saturated and EVERY larger one is invisible too, to infinity, so the band must say so"*). It put it
inside `_check_own_band`, reached only from `check_own_drift_resolution`, which iterates only the
entries declaring an `own_drift` — the **OFF-PATH** ones. So the register that refuses an
unbounded-blind band *off* the causal path accepted one *on* it. **A rule keyed to a register STATE
rather than to what the instrument publishes: the same keying, inside the control written to close the
previous keying.**

---

## Closed at the class (R10)

1. **The grid's PROVENANCE, not its width.** `dense_drift_grid()` is derived from the scenario
   calendar (`DRIFT_GRID_SPAN_DAYS == PERIOD_SPACING_DAYS`, the cycle the book is spread over — the
   only non-arbitrary width available). A test parses its AST and fails if its code can reach
   `DIMENSION_DRIFT_RESOLUTION`. The declared drifts are still **unioned in**, so a declaration outside
   the grid is scored rather than skipped into a free pass — they no longer *define* what gets asked.
2. **Collapse is DERIVED, declared EXACTLY.** Every group of ≥2 companies publishing one reading **on
   every seed** is measured from the readings. An undeclared collapse RAISES (the defect); a declared
   collapse the sweep reads apart RAISES (a debt entry outliving its debt).
3. **Saturation is ONE function, called from BOTH checkers.** `_check_saturation_and_collapse` runs
   once per entry on the knob that reaches that entry's organ — the terms grid for an on-path entry,
   the entry's own graded knob for an off-path one. A rule that exists only once cannot exist on one
   side of `in_causal_path` and not the other. **Cross-check that the abstraction is right:** the
   generic rule, which knows nothing about failure events or `measure_belief_window_resolution`,
   re-derives D27's finding from the readings alone and puts the belief saturation edge at the same
   **-308**.
4. **The undefined-reading fail-open, closed.** A dimension whose population empties under a drift
   publishes `None`, and `None != baseline` reads as **MOVEMENT** — an instrument that has stopped
   reading at all, scored as though it had resolved the company. Now a named violation. (Reachable:
   `detection_latency` goes `None` at large positive drifts.)
5. **DIFFERENTIAL ON PURPOSE.** A register in which every on-path dimension saturates somewhere is an
   "everything is quantised" claim that would pass whatever the instrument did. `ageing` publishes 43
   distinct readings and collapses nowhere — the D25 reshape holding up under a grid it did not choose,
   which the sparse grid could only ever confirm on the four drifts D25 itself named.
6. **The caveat is stamped AT SOURCE** on `detection` — `note` **and** `components` (the ledger writer,
   live wiring and dashboard read components and never the prose, D22) — interpolated from the register
   on every call, so flipping the register flips the published sentence.

**Declared residual, not implied away:** there is no population-side *predictor* of detection's edges
(the D25/D27 shape). The caveat says so in as many words, and it is the minted atom's own debt — a
live `run_phase2b` book no sweep has visited carries the offline scenario's edges until it exists.

## R15 — proven both ways

- **On the register (6 mutations):** an undeclared collapse (the defect itself), a declared collapse
  the sweep reads apart, an understated edge in each direction, an unowned hole (`saturation_atom`),
  and an all-collapsed register. Plus the off-path mirror through the same shared function.
- **On the source (2 mutations):** the grid put back the way it was — `dense_drift_grid → (0,)` — and
  six of detection's seven collapses become unconfirmable, including the sixteen-company tail; and a
  runner that returns an absent reading, which the bands counted as resolution.

## Evidence

- `tools/couple_w2_11_d5.py` — `DRIFT_GRID_SPAN_DAYS`, `dense_drift_grid`, `_measure_collapse_runs`,
  `_check_saturation_and_collapse` (called from `_check_on_path_entry` **and** `_check_own_band`), the
  `collapsed_runs`/`saturates_below`/`saturates_above`/`saturation_atom` fields on all five register
  entries, `detection_resolution_caveat`, the D28 differential in
  `_check_register_is_differential`, and both controls printed in the CLI.
- `tests/tools/test_couple_w2_11_d5.py` — 13 new tests, **315 green** (was 302).
- Sibling/consumer suites: **122 green** (`test_d6_ageing_metric_shape`, `test_d7_ageing_measures`,
  `test_gap_metric_misapplication_class`, `test_epistemic_wall_indirect_ratchet`,
  `test_generate_proof_coupled_gaps`, `test_live_payment_triad`, `test_gap_ledger_reconciler`).
- CLI, live: `detection blind to [1] … SATURATES below -6d / above 17d on the 43-point book-derived
  grid; 7 collapsed run(s) (atom D28_the_detection_gap_is_quantised_by_this_books_placement) … verdict:
  every declaration held`, and on the memory control `saturates above -308d, 1 collapsed run(s)
  [shared rule]`.
- Mint: `D28_the_detection_gap_is_quantised_by_this_books_placement`, L0, `loop_stage: idle`,
  `depends_on: D26` (it moves a published number, so it is a mint and not a fix on sight).

## Hour #11 leads, in order

1. **The own-drift grid is still the register's own claims.** This Hour fixed the provenance of the
   *terms* grid; `measure_own_drift_resolution` still builds its sweep from `own_invisible_drifts ∪
   own_visible_drifts`. The shared rule now runs there, but on a grid the register chose — so the
   belief saturation edge of **-308** is an artefact of where D27 happened to sweep, not a measured
   boundary. A book-derived memory grid would need one scenario BUILD per drift, which is why it was
   not taken here.
2. The two leads Hour #8 left and no Hour has taken: the pinned generated value
   `assert c["n_recon_detected_undated"] == 0`, and whether the other dimensions' normalisation notes
   have the same gap between what they DENY and what they ESTABLISH.
3. `DD_FAILURE_WINDOW_DAYS = 400` was not the only harness constant chosen to *remove* a confounder —
   `AS_OF_BUFFER_DAYS = 30` carries the same "comfortably past" comment, and each such choice is a
   resolution decision taken silently. The census of them still has not been made.
