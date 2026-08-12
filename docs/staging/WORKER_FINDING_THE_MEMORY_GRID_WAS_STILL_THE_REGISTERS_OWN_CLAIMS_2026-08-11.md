# H27 EXPERT HOUR #11 — the other half of the keying, and the floor nobody could see

**Severity:** BLOCKING · **Lane:** H_harness

**Atom:** `H27_payment_belief_gap` (2→3 HARDEN draw, worker tick, 2026-08-11)
**Verdict:** HELD AT L2. Eleventh Hour, eleventh defect, and this Hour changed the instrument again.
**Lead taken:** Hour #10's lead 1 — *"the own-drift grid is still the register's own claims … the
belief saturation edge of -308 is an artefact of where D27 happened to sweep, not a measured
boundary"* — which on measurement also discharged lead 3 (*"the census of harness constants chosen to
remove a confounder has not been made"*) at its second member.
**Reshape minted as:** `D29_the_as_of_buffer_floors_the_memory_grid` (L0)
**Class:** `ORGAN_QUERY_GRID`'s **seventh escape** — a reading taken on a grid of the harness's own
making is quantised to that grid.

---

## The finding, measured not asserted

**A LEAD IS NOT A CONTROL.** Hour #10 removed the register's grip on the *terms* grid, wrote the
remaining half up as its top lead, and shipped. `measure_own_drift_resolution` went on building the
memory sweep the old way:

```python
drifts = {0} | own_invisible_drifts | own_visible_drifts
```

So every claim D27 made about what the belief dimensions can resolve was checked at the points D27
had already named. The two things that followed are both real and both were invisible by
construction.

### 1. The band saturates BELOW as well as above, and nobody could have seen it

The memory knob admits a grid that is not merely dense but **complete**: an event at age `a` is
counted iff `a <= window`, so the reading can only change as the window crosses an event age.
Scoring `{a, a-1}` for every observed failure age, plus total amnesia and the shipped company, is 70
counterfactual companies and it measures resolution **over the whole real line** — which no bounded
integer sweep does. Measured at `n=300`, seeds 7/11/23, every run identical on all three:

| | declared before (D27/D28) | measured on the book's grid |
|---|---|---|
| `belief` | saturates above `-308`, **below `None`**, 1 collapsed run | above `-308`, **below `-371`**, **5 runs** |
| `belief_population_mix` | saturates above `-308`, **below `None`**, 1 run | **above `-309`**, **below `-371`**, **4 runs** |

The book's **youngest** observed failure is 30 days old. So every company memory of **29 days or
less counts nothing at all**: a supplier that forgets a failed collection after three weeks and one
that never remembers it are one number here. D27 measured `saturates_below = None` on the very same
instrument for a mechanical reason — a collapsed run needs two points and the register's own claims
put exactly **one** below the book.

Why 30 days: **`AS_OF_BUFFER_DAYS`**, and that is Hour #10's lead 3 arriving. It is the second
harness constant chosen to *remove* a confounder, and its comment says *"comfortably past"* in the
same voice `DD_FAILURE_WINDOW_DAYS = 400` says *"generous on purpose"*. Both reasons are sound. Both
are silent resolution decisions, and this one floors the grid.

**`-380d` — which D27 declared VISIBLE, as its evidence of resolution — sits inside that tail.** It
takes the memory to 20 days on a book whose youngest failure is 30 days old, so it counts nothing,
exactly like total amnesia. Differing from the scored company is not resolution.

Four further interior collapses (`{-358,-357,-356}`, `{-333,-332}`, `{-331,-330}`) show the sighted
region is quantised rather than continuous, at exactly the window values where this book has no
event.

### 2. The register put one dimension's ceiling at its sibling's

`belief_population_mix` was declared to saturate above `-308`, the same as `belief`. It saturates at
**`-309`** — one day blinder, because dropping the oldest events moves an account's severity tier
without moving the population **mix**. That is a real difference between two published numbers, and
the register asserted it away by never scoring the point.

---

## What was closed at the class (R10), and what was not

**Not fixed on sight** — giving the book events beside the short end of a plausible memory (an
`as_of` closer to the last event, several `as_of` readings, a book running right up to it) moves
every published belief figure on this pair, so the reshape is minted as **atom D29** at L0. **R12: no
published number moved in this commit.**

Closed here:

1. **`book_memory_grid`** — derived from the book's own event dates, asserted against its **AST**
   never to reach `DIMENSION_DRIFT_RESOLUTION`, and complete by the counted-set argument above. The
   declarations are still **unioned in**, so a declaration outside the grid is scored rather than
   skipped into a free pass; they no longer *define* what gets asked.
2. **`OWN_DRIFT_BOOK_GRIDS`, fail-closed.** A knob with no book-derived grid **RAISES**. The
   fallback *is* the defect, and a silent one would put the next off-path entry straight back where
   D27's was.
3. **Both edges predicted from the population** (`predicted_saturates_below_drift` / `_above`) and
   cross-checked against the sweep **one-directionally**: beyond the predicted edge no event can
   change side, so movement there is a violation; inside it a dimension may saturate earlier, which
   is a blinder *measurement* and not a lie. D27 had this pair on the upper edge only — which is
   precisely how the lower one read `None` with nothing to disagree with it.
4. **A drift declared VISIBLE may not sit inside a collapsed run.** D28 observed this in prose —
   *"the -8 the old grid read as MOVED, as evidence of resolution, sits inside the saturated tail"* —
   and built no rule, so the same shape survived one register field over.
5. **A saturation owner PER EDGE.** These two tails stop for two different reasons — above, the
   company's memory outruns the book (D27); below, `as_of` outruns it (D29) — and one
   `saturation_atom` field could only ever name the one that had been looked at.
6. **The amnesia floor is stamped AT SOURCE** on both belief dimensions — `note` **and**
   `components` (D22) — and re-derived from the book each call, so a live `run_phase2b` population
   carries its own floor.
7. **It runs in the CLI**, printing both edges and their owning atoms (D25's rule).

## R15 — proven both ways

- **On the register (5 mutations):** the low edge declared absent (the pre-D29 state), an owner for
  one tail only, a dense-grid collapse left undeclared, a declared collapse the sweep reads apart,
  and a visible drift restored inside the saturated run.
- **On the source (3):** a sweep that outruns the book's proof at either edge, and a knob with no
  book-derived grid (which must raise, not fall back).
- **Inherited and still proven:** the inert probe, the knob that moves everything, and the
  counterfactual that changes the WORLD rather than the company.

## Evidence

- `tools/couple_w2_11_d5.py` — `book_memory_grid`, `OWN_DRIFT_BOOK_GRIDS`,
  `_check_book_predicts_both_edges`, the visible-inside-a-run and per-edge-owner rules in
  `_check_saturation_and_collapse`, the re-derived `belief` / `belief_population_mix` entries, the
  amnesia floor in `measure_belief_window_resolution` + `belief_resolution_caveat`, and both edges in
  the CLI.
- `tests/tools/test_couple_w2_11_d5.py` — 12 new tests, **327 green** (was 315).
- CLI, live: `saturates below -371d (atom D29_the_as_of_buffer_floors_the_memory_grid) / above -308d
  (atom D27_belief_window_saturates_on_this_book), 5 collapsed run(s) on the 70-point book-derived
  grid … oldest 91d / youngest 30d vs a 400d memory … verdict: every declaration held`.

## Hour #12 leads, in order

1. **The interior collapses have no owner of their own.** `{-358,-357,-356}`, `{-333,-332}`,
   `{-331,-330}` are quantisation inside the *sighted* region, and they point at D27 because the
   general `own_saturation_atom` field does. Whether the reshape that fixes the tails also fills
   those gaps has not been asked.
2. **The census of confounder-removing constants is now two of an unknown number.**
   `DD_FAILURE_WINDOW_DAYS = 400` (D27) and `AS_OF_BUFFER_DAYS = 30` (D29) were each found by
   tripping over them. `BILLING_CYCLE_SPREAD_DAYS`, `N_PERIODS` and the reconciliation grace window
   have not been put through the same question.
3. The two leads Hour #8 left and no Hour has taken: the pinned generated value
   `assert c["n_recon_detected_undated"] == 0`, and whether the other dimensions' normalisation
   notes have the same gap between what they DENY and what they ESTABLISH.
