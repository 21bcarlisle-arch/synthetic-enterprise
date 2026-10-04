# The H27 book re-drawn through the one payment draw refutes D26's calendar claims

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 2 · **Atom:** `W2_payment_channel_dd_consistency_invariant` · **Claim:** `redraw-the-h27-calibration-book-through-the-one-payment-draw` (Lane 0 delivery)

**2026-10-04.** The owed work from
`SEAT_FINDING_THE_LEDGER_PAYS_BY_ONE_METHOD_DRAW_AND_THE_SEAM_REPORTS_ANOTHER_2026-10-03.md`:
`tools/couple_w2_11_d5.py` drew its `H27S…` book through `_calibration_book_method`, a byte copy of
the retired second stream. It now draws through `generate_payment_method`, and the copy is deleted.

## Premise, re-measured at draw time

Still live: `_calibration_book_method` was on origin/main (`598676ac3`). Nobody else held this
claim. A concurrent lane (`agent-aecf2424…`, SLC 14 debt objection) has uncommitted hunks in the
same file, adding `settled_on`. Those hunks do not touch the method draw.

## What the change does to the sample (measured before any test was run)

| n | old DD/PPM/SO/card | new DD/PPM/SO/card | same method |
|---|---|---|---|
| 60 | 44/8/4/4 | 40/11/4/5 | 29 |
| 120 | 84/18/6/12 | 86/19/6/9 | 60 |
| 200 | 145/27/12/16 | 148/29/10/13 | 105 |
| 400 | 292/58/23/27 | 297/50/26/27 | 221 |

Both draws read the same anchors, so the **mix** is unchanged within sampling noise. **Which
account** has which method is close to independent: about 52–55% of accounts keep their method,
which is what two independent draws give (0.72² + 0.17² + … ≈ 0.55).

## Prediction (written before the test run was read)

1. About 36 registers go red, the number the 2026-10-03 attempt saw. Every red is a **count or a
   rate over a sample** whose members changed, not a change in mechanism.
2. **No structural control goes red.** That covers partitions, independence (R15), the
   counterfactual populations that use `force_payment_method`, and the resolution differentials.
   If one does, it was keyed to the old sample by accident. That would be a finding, and it would
   be fixed as one rather than re-pinned.
3. Each moved count should move by no more than its sampling noise on the book it is measured
   over. A move bigger than that means the register depended on WHICH accounts paid by DD in a way
   no world draw supports. It gets read and explained before it is re-pinned.

## Result (2026-10-04, read after the prediction above was written)

**Prediction 1 held: 36 red**, all in `tests/tools/test_couple_w2_11_d5.py`. The other five suites
that import the harness stayed green (112 passed).

**Prediction 2 was WRONG, and that is the finding.** Structural controls went red as well as
counts. The register checkers, run on one cached measurement each (n=300, seeds 7/11/23):

| checker | violations | what moved |
|---|---|---|
| `check_dimension_drift_resolution` | 32 | detection collapse runs re-drawn wholesale; upper edge 82 -> 83; **detection +1d now moves on seed 7**; ageing gains a [53, 54] collapse |
| `check_organ_query_grid_saturation` | 31 | the same runs on the recon grid (they share `_DETECTION_COLLAPSED_RUNS`); +8d now sits inside a collapse |
| `check_own_drift_resolution` | 14 | belief memory-drift collapse runs re-drawn; `belief_population_mix` -1d now moves on seed 11 |
| `check_recon_collapsed_runs_stress_axis` | 4 | the NULL CONTROL is red: on `mix`, the book the declaration was written on, the origin no longer sits in a collapse |
| `check_published_resolution_floor` / caveat | 4 + 2 | belief floor 4d -> 2d (both belief figures) |
| `check_recon_band_population_axis` | 1 | upper edge range [49, 88] -> [46, 88] |

The collapse runs and edges are where this sample's invoices sit relative to each line. About
half the accounts changed method, so these moving wholesale is expected. They get re-derived.

### D26's two measured claims were properties of the old draw

`D26_detection_grace_line_has_no_book_beside_it` (closed, L2) claims two things. The shipped
reading date cannot resolve +1d ("calendar, holds 10/10 seeds"). Its own reading date resolves
"+1..+2" (`DETECTION_RESOLUTION_CEILING_DAYS = 2`). Here is the smallest visible over-drift
re-measured on the redrawn book, over the same ten seeds and the same n=300:

| seed | 7 | 11 | 23 | 1 | 2 | 3 | 5 | 13 | 29 | 31 |
|---|---|---|---|---|---|---|---|---|---|---|
| shipped (old draw) | +2 | +4 | +6 | +2 | +5 | +2 | +3 | +8 | +5 | +6 |
| shipped (redrawn) | **+1** | +2 | +3 | +3 | **+1** | +3 | none | **+1** | +7 | +7 |
| own (old draw) | +1 | +1 | +2 | +1 | +2 | +2 | +1 | +1 | +1 | +1 |
| own (redrawn) | +1 | +2 | +1 | +1 | +1 | **+3** | +1 | +1 | +1 | +1 |

- **The +1d blindness at the shipped date is not the calendar.** It breaks on 3/10 seeds.
- **The reshape's resolution is not +1..+2.** Seed 3 reads +3, past the ceiling.
- **What survives:** the own date is never worse than the shipped date (10/10), and it is
  strictly better on 5/10.

**Why +1d became visible: a hole in the by-construction argument.** Seed 7, k=0 -> +1: one
COUNTED false flag drops (14 -> 13, `flagged_size` 328 -> 323). It is `H27S7C000116` period 2, a
prepayment account. It paid **on its due date**, so it is in N (`days_late = 0 <= grace`). But
the account's period-1 bill was paid 27 days late. The D8 oldest-first fallback credits the
on-time payment to the older open invoice, so the company sees period 2 settled on period 1's
late date, six days past due: exactly `grace + 1`.

The register's `why` says the exclusion boundary and the detector line "are keyed on THE SAME
QUANTITY, so the cases a small over-drift can carry across the line are by construction the cases
the headline declines to score". That holds only when the company sees the true `days_late`.
The exclusion reads the world's `days_late`, while the line reads the date the company's
allocation produced. A mis-allocated in-N case at `grace + 1` is a counted case the line carries
across. No case like that existed in the old draw's 10 seeds, and three of the redrawn ones have
one.

**What this means.** D26's register entry (`invisible_drifts: (1,)`, `structural_scope["+1_edge"]:
"calendar"`, both bands, the ceiling) has to be re-derived as a DRAW property, the same thing its
own build note already did to FRAME's 3-seed claim. It is not a one-number re-pin, and the
ceiling is not widened to fit. `DETECTION_RESOLUTION_TARGET_DAYS = 1` stands.

## Disposition

- `tools/couple_w2_11_d5.py` re-draws through `generate_payment_method` and `_calibration_book_method`
  is deleted. That edit is made but NOT landed: it cannot land until the 36 reds are re-derived,
  because the gate runs this test file.
- Next, in order: (1) re-derive the pure-measurement registers (collapse runs, edges, belief floor,
  band ranges) from one cached measurement; (2) re-state D26's entry as above, with a per-seed
  scope instead of "10/10 calendar"; (3) the literal pins (latency 84-53, ageing 0.0999,
  `flagged_size` 328, seed 11's belief probe), each read for whether its premise still holds.
