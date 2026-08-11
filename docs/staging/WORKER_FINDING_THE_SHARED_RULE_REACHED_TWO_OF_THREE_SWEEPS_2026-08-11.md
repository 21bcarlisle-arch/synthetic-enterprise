# H27 Expert Hour #13 — the shared saturation rule reached two of three sweeps, and the third is the register that started the line

**Date:** 2026-08-11 · **Atom:** `H27_payment_belief_gap` (HARDEN, self-refill draw 2→3)
**Subject:** `tools/couple_w2_11_d5.py` · **Reshape minted as:** `D31_the_recon_grid_saturates_beyond_this_books_window` (L0)
**Held at L2.** Thirteen Hours, thirteen defects, and this Hour changed the instrument again.

---

## The lead this took, and why it was the right one

Hour #12 left three leads. Lead 1 was the census: `SCENARIO_CONSTANT_CENSUS` records
`PAYMENT_TERMS_DAYS` as `bounds_resolution: False` — true of the invoice-AGE band it measures —
and discharges it in prose: *"It bounds the DETECTION-LATENCY dimension instead (D23/D24), which
is a resolution claim about a different reading and **is registered there**."*

It was not registered there. `ORGAN_QUERY_GRID` named no constant at all. Following that pointer
found something larger than a missing field.

## The finding, measured not asserted

**D29 built one saturation rule for two sweeps and said so in as many words** —
`_check_saturation_and_collapse` exists "so a saturation rule can no longer exist on one side of
`in_causal_path` and not the other", called from both checkers, "because there is only one of it."
There are **three** counterfactual-company knobs in this harness. The rule reached two.

The third is `organ_reconciliation_drift_days`, whose register is `ORGAN_QUERY_GRID` — **atom
D23's, the register that found this whole class**. Its measurement still built the sweep the
original way:

```
drifts = {0, 1} | invisible | visible | collapsed pairs | distinct pairs
```

so every claim it makes was checked at exactly the points it had already named, and it had no
notion of a collapsed RUN, a saturation EDGE or an UNDEFINED reading at all. **Eighth escape of a
register's own keying, and this time it is the origin register.**

Measured on a grid derived from the BOOK instead (`book_recon_drift_grid`: one integer per day
from one step below the earliest issue-date crossing to one step above the last `as_of` crossing —
109 counterfactual companies, 110 once the register's own declared −30 is unioned in;
AST-asserted never to reach a register), n=300, seeds 7/11/23, every run identical on all three:

### 1. The SET reading — which IS the published `detection` gap — has sixteen collapses

| | declared before | measured |
|---|---|---|
| collapses | 2 pairs | **16 runs** |
| saturates below | — | **−6** (16 companies, all reading 0.5) |
| saturates above | — | **+82** |

Below −6d every company has already flagged every invoice by `as_of`, so the gap is the no-skill
**0.5**: a supplier whose reconciliation fires a week early and one three weeks early are one
number, and the two declared PAIRS were a 2-point sample of that tail. The interior runs
(`{−4,−3}`, `{0,+1}`, `{+6,+7}`, `{+9,+10}`, `{+11,+12,+13}`, `{+17..+24}`, …) show the reading is
quantised rather than continuous anywhere.

**The witness that it was unreachable and not merely unnoticed:** `+7` was **declared VISIBLE** —
offered as this entry's evidence that the reading resolves the company — and it sits inside the
collapsed run `{+6, +7}`. That is D29's own rule ("resolution is being told apart from your
NEIGHBOURS"), live one register over, unenforced because this register never routed through it.
It is replaced by `+8`, which the sweep reads apart from both neighbours.

### 2. The DATE reading stops reading, and the absence counted as resolution

At `+87`/`+88` no failure is detected before `as_of` at all: the latency population empties and
the mean is `None`. `None != baseline`, so the old measurement counted **an instrument that had
stopped reading as RESOLUTION** — the exact fail-open D28 closed for the other two knobs, live
here because the rule that closes it was never called.

### 3. The floor is two harness constants, and one of them was discharged onto this register

The date reading saturates below at **−19**, which is
`−(PAYMENT_TERMS_DAYS + DEFAULT_RECONCILIATION_GRACE_DAYS)`: the day the drifted detector reaches
the invoice's own issue date, where the whole latency population sits on
`n_recon_dated_at_issue_floor`. The census pointed `PAYMENT_TERMS_DAYS` here and this register
never received it; the other half of the edge, the grace window, **is not even in the census's
subject** — that keyset comes off `build_scenario`'s AST, and the grace window enters at
`score_triad`. A constant discharged onto a register that never received it is unowned twice over.

The bound itself is real and stays a bound: no supplier can reconcile a bill it has not issued.
What was missing is that its POSITION is arithmetic on two harness constants, and now it is
predicted from them (`predict_recon_floor_from_constants`, reads no book, no draw, no seed) and
cross-checked against the sweep. Both agree at −19.

### Corroboration the two knobs now give each other

With all three sweeps finally through one rule, the CLI prints both, and they agree where
agreement is meaningful: under the TERMS knob (D28) the detection gap also saturates below −6d
and the latency reading also saturates below −19d. Two different company errors, two different
registers, the same two edges — which localises both to this BOOK's placement rather than to
either knob, and is the kind of cross-check that only exists once the third sweep is on the same
footing as the other two.

## Closed at the class (R10)

* **`COUNTERFACTUAL_KNOB_ROUTE`** — the keyset is DERIVED (`counterfactual_knobs`, off
  `score_triad`/`build_scenario`'s own signatures), so a knob with no route **RAISES**: the
  fallback IS the defect. Each entry names a book-derived grid and a checker, and the checker is
  **AST-verified to reach `_check_saturation_and_collapse` transitively** — because naming the
  shared rule is not running it (Hour #11's *a lead is not a control*, in the shape this route
  could itself have taken).
* **`book_recon_drift_grid`** — provenance is the book; COMPLETE, not merely dense (the reading is
  constant below the issue-date crossing and absent above the `as_of` crossing, so integers
  between them measure resolution over the whole real line). The old declaration fields are still
  UNIONED in; `collapsed_runs` and `undefined_drifts` deliberately are **not** — they are what the
  sweep is for, and adopting them would put the answer back into the question.
* **An undefined region is a BOUND only with its witness** (D24's distinction, generalised into
  the shared rule): declared *and* witnessed by the population itself — `reading is None` exactly
  where the population is empty. Undeclared, it is the fail-open it always was. The differential
  is real: one seed still has a case at +87, reads a number, and its witness is a NON-empty
  population.
* **`edge_constants` is a claim, not a label** — caught on this Hour's own first draft, where the
  prediction was a fixed call and declaring `("N_PERIODS",)` fired nothing. The prediction is now
  built from the constants the entry NAMES, each perturbed one day, with a subset-attribution rule
  (D30's class) and an unknown-constant rule.

## R15 both ways

**Register mutations, each firing by name:** the pre-Hour `visible_drifts` (+7 inside a collapsed
run); a dropped run (15 undeclared collapses); an invented run ("reads them apart"); an understated
edge; a tail with no owner; a dropped `undefined_drifts` (the fail-open); an invented one; a
constant that reaches no knob; a subset attribution.

**Source mutations:** the grid put back the way it was — on its own declarations the register
scores 9 points, can confirm almost none of what it now declares, reads **neither** saturation edge
and cannot see the undefined region at all; and a route whose checker only names the shared rule.

## R12

**No published number moved.** The detection gap, the latency mean and both belief figures are
bit-identical before and after; what moved is what the instrument admits about itself. The
RESHAPE — a book whose invoices do not all fall inside one `as_of` window, so the detection set
can still change beyond +82 — is atom **D31**, minted at L0, not fixed on sight.

## Why still L2

Thirteen Hours, thirteen defects, none predicted by the Hour before it, and this is again the tick
that changed the instrument. Hour #4's stated-in-advance criterion of TWO CONSECUTIVE CLEAN HOURS
has still not been approached.

## Hour #14 leads, in order

1. **The route now proves every knob reaches the shared rule. Nothing proves the CAVEATS do.**
   Three registers now stamp resolution caveats at source; whether every published dimension
   carries the caveat of every knob that reaches it is the same coverage question one layer up,
   and it has never been asked.
2. **The interior collapses still have no owner of their own** (Hour #11's lead 1, still untaken,
   now with sixteen more of them).
3. **The two leads Hour #8 left and no Hour has taken:** the pinned generated value
   `assert c["n_recon_detected_undated"] == 0`, and whether the other dimensions' normalisation
   notes have the same gap between what they DENY and what they ESTABLISH.
