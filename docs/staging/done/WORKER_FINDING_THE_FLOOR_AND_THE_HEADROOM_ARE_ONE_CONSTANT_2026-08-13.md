# FINDING — the floor and the headroom are one constant, so the atom's own knob cannot fix the atom's own defect

**Severity:** LATENT · **Lane:** D_billing_metering · **Disposition:** QUEUED (not fixed on sight)

**Atom:** `D29_the_as_of_buffer_floors_the_memory_grid` (LANE 3 idle draw, DISCOVER/FRAME, 2026-08-13)
**Class:** a mint's recorded blast radius names the dimensions it cannot move and omits the one it does

Full derivation and every number: `docs/design/simplifications/D29_the_as_of_buffer_floors_the_memory_grid.yaml`.

## Observed, with evidence

All measurements in a detached worktree **at HEAD** — `tools/couple_w2_11_d5.py` is
modified-uncommitted in the shared tree by another lane (+596/−139), so the desk tree is not the
subject.

**1. `AS_OF_BUFFER_DAYS` translates the age band; it never widens it.** Through
`predict_event_age_span_from_constants` over eleven values (0, 1, 5, 10, 20, 30, 60, 120, 338, 339,
400) both edges move one-for-one and the width is invariant at **62 days** at every one. `N_PERIODS`
3 → 20 moves the top alone (92 → 449, width 62 → 419), so the distinction is real and only this
constant is a translation.

**2. Therefore the floor and the headroom are conserved against each other**, exactly:

```
amnesia_floor = newest_failure_age − 1
headroom      = DD_FAILURE_WINDOW_DAYS − oldest_failure_age
floor + headroom = DD_FAILURE_WINDOW_DAYS − event_age_span − 1      (free of `as_of`)
```

Measured through the shipped `measure_belief_window_resolution`, n=300, seeds 7/11/23, at buffers
5 / 30 / 338 — the sum is 338 / 337 / 338 per seed and does not move:

| seed | buf | floor | headroom | sum | saturated |
|---|---|---|---|---|---|
| 7 | 5 | 4 | 334 | 338 | True |
| 7 | 30 | 29 | 309 | 338 | True |
| 7 | 338 | 337 | 1 | 338 | True |
| 11 | 30 | 29 | 308 | 337 | True |
| 23 | 30 | 30 | 308 | 338 | True |

`buf = 338` is the only value that brings the band's top to the scored company's 400-day window, and
it does so by making a supplier with **eleven months** of memory count nothing — D29's own named
defect, eleven times worse. `saturated` is still `True` at 338 on all three seeds, so **no** value
of this constant de-saturates the company being graded.

**3. The atom's mint justification is false as measured.** Its `name` says the reshape "moves every
published belief figure on this pair". Scored through `score_triad`, n=300, seeds 7/11/23, buffer
30 → 5 (the atom's own first candidate reshape):

| dimension | buf=30 (seed 7) | buf=5 (seed 7) | |
|---|---|---|---|
| `ageing` | 0.11296259117981663 | 0.08016507936507936 | **MOVED** |
| `belief` | 0.1518987341772152 | 0.1518987341772152 | bit-identical |
| `belief_population_mix` | 0.07999999999999997 | 0.07999999999999997 | bit-identical |
| `detection` | 0.014505119453924915 | 0.014505119453924915 | bit-identical |
| `detection_latency` | 2.343137 | 2.343137 | bit-identical |

Seeds 11 and 23 agree in full. Neither belief figure moves — at drift 0 the scored company holds 400
days and every failure age is under 400 at both buffers, so the counted set is identical (D30's "the
scored company is inert", from the other side). The figure that **does** move is `ageing`, which the
atom never mentions.

## Why it matters

The atom is still correctly a MINT — it moves a published figure and every declared edge on the
belief pair. But anyone sizing its blast radius off the `name` protects the two figures that cannot
move and misses the one that does. And the map's `D30 depends_on: [D29]` is right as *history* and
backwards as *build order*: where the floor sits is a free choice inside the edit that chooses the
span, and the span is D30's.

## Why it is queued, not fixed

The false sentence is the atom's `name` in `docs/design/maturity_map.yaml`, whose shared index
already carries another lane's staged `level_current`/`loop_stage` move — a pathspec commit of the
map would land their level change under this message (the constraint the D33 and EP10 passes each
hit on this file). SELF-INTERRUPT DISCIPLINE: registered, not fixed on sight.

## What closes it

1. `D29`'s `name` corrected to state the measured radius (`ageing` moves; the belief pair does not
   at drift 0) — one map edit, on a clean index.
2. The exit test for D29/D30's reshape asserts the **conserved sum** moved, not the floor: `floor +
   headroom` before and after, computable from the book with no re-scoring.
3. `saturated == False` for the scored company at drift 0 — the one statement no `AS_OF_BUFFER_DAYS`
   value can buy.

R12: no published number was tuned or written to any artefact; the five figures were scored only as
alternative books at a perturbed harness constant, inside a throwaway worktree.
