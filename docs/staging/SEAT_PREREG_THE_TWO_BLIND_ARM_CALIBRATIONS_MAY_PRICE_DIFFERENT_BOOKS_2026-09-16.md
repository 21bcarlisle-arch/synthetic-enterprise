**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** `unminted`

# [SEAT][PRE-REGISTRATION] The two blind-arm calibrations may not be two calibrations at all

**Written BEFORE the measurement, against `fd899ddf0`.** The answer is not known at the time of
writing. If the measurement refutes what is below, the refutation stays here beside the prediction.

## The claim I was handed

Lane 0 drew `the-blind-arm-rerun-sits-uncommitted-and-disagrees-with-the-published-baseline`, whose
premise is:

> `docs/observability/value_based_pricing_arms.json` in the working tree is a finished re-run (1,491
> lines against HEAD's 73) ... HEAD says `world_curve_basis: "saturated -- past the ceiling"`,
> shortfall −£467.81, belief error 41.1pp; the working copy says `"observed -- inside the calibrated
> window"`, +£303.27, 18.7pp

It frames this as **one baseline, two calibrations, one of which must be refuted**.

## What is already established without measuring anything

Three of the premise's factual claims about the tree are already false, checked against
`fd899ddf0` and the shared tree at `/home/rich/synthetic-enterprise`:

1. **"HEAD's 73 lines"** — HEAD's copy is **15,799 lines**. It has not been 73 lines since
   `856b65d9d` (2026-08-25).
2. **"a re-run of 1,491 lines"** — the shared tree's uncommitted copy is **10,361 lines**, i.e.
   *smaller* than HEAD, not larger. The premise has the direction of the change backwards.
3. **`world_curve_basis: "saturated"` is not a HEAD-wide statement.** It is a per-account field.
   HEAD carries `"observed -- inside the calibrated window"` on many accounts (lines 389, 428, 467,
   506, 545 …) and `"saturated"` on the first one. The premise read `accounts[0]` and reported it as
   the artefact's verdict.

And the decisive structural fact:

| | HEAD `fd899ddf0` | shared tree, uncommitted |
|---|---|---|
| `accounts_priced` | **397** | **226** |
| `endpoint_at_ceiling` | 1 | 17 |
| `endpoint_at_floor` | 18 | 2 |
| `median_implied_bill_change_pct` | 52.1 | 46.3 |
| `population` block | **absent** | present, 8 keys |
| `belief_vs_truth` keys | 12 | 15 |

## The prediction

**The two files price different books, so `accounts[0]` is a different customer in each, and the
"decisive term inversion" the item reports is not a disagreement about calibration at all.**

Specifically I predict:

- **P1.** `accounts[0].customer_id` differs between the two files, OR — if it is the same id — that
  customer's `eac_kwh` differs, i.e. it is not the same account.
- **P2.** The 226 accounts in the working copy are a **subset** of HEAD's 397, not a re-draw.
- **P3.** On accounts present in BOTH files with the same `customer_id` and same `eac_kwh`, the
  `world_curve_basis` / shortfall / belief-error fields will **agree** for most accounts — because
  neither file re-calibrated the world curve; one of them merely prices a narrower book.
- **P4.** The ceiling/floor flip (1→17 ceiling, 18→2 floor) is explained by **which accounts are in
  the book**, not by a changed grid or a changed bound. The working copy's own `population` block
  already states `"lawful_ceiling_passed": false` and that `endpoint_at_ceiling` "is not a
  measurement of anything" at this call site.

## What would refute each

- **P1/P2 refuted** if the id sets are equal, or disjoint, or overlap partially — any of those makes
  it a re-draw rather than a narrowing, and then the populations genuinely are rivals.
- **P3 refuted** if the shared accounts disagree on `world_curve_basis` or shortfall. That WOULD be a
  real recalibration and the item's framing would be correct after all, and I would then have to
  establish which curve is right rather than which book is right.
- **P4 refuted** if the shared accounts' `endpoint_side` differs — that would mean the grid or the
  bound moved, not the book.

## Why this matters more than the item's framing

If P1–P4 hold, then **"land it or discard it" is the wrong pair of options**, because the working
copy is not a rival calibration to be adjudicated — it is a *differently-scoped* run, and landing it
over HEAD would silently shrink the published baseline from 397 accounts to 226 while the page
carrying it says nothing changed. The director's thesis needs "the same book run by a supplier
applying flat rules" — **the same book** is the load-bearing phrase, and a baseline that quietly
drops 171 accounts cannot serve it whichever curve it uses.

If P3 is refuted, the item is right and the curve is the question.
