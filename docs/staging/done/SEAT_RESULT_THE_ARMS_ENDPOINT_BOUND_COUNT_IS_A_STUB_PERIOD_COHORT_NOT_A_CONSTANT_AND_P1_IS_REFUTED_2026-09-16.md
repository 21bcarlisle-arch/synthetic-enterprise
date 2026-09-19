**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
"the-arms-artefact-cannot-name-the-book-or-the-world-it-priced"

*LATENT: the count is not wrong, and nothing published is retracted by this. What it counts is not
what its name suggests, and the EAC understatement underneath it is a real pricing input defect
owned by whoever next touches `tools/couple_value_based_pricing.compare`.*

# `endpoint_bound` is a stub-period cohort, not a constant — and my own P1 was refuted

Delivery seat, 2026-09-16, against `5a63cb3a3`. Pre-registration written before any measurement:
`docs/staging/SEAT_PREREG_THE_ARMS_ARTEFACTS_ENDPOINT_BOUND_COUNT_MAY_BE_A_COHORT_NOT_A_COINCIDENCE_2026-09-16.md`.

---

## The question

The drawn item observed that `endpoint_bound` is **19 in both** the HEAD arms artefact (397
accounts, split 1 ceiling / 18 floor) and the shared tree's uncommitted copy (226 accounts, split
17/2), and asked whether that is coincidence or "a constant leaking into a count". One probe owed.

## Answer: neither. It is a **census of accounts whose consumption the producer understates**.

### P1 is REFUTED, and the refutation is kept here

I predicted HEAD's 18 floor-bound accounts were the 18 gas-only accounts that could not depart.
**They are not.**

| | predicted | measured |
|---|---|---|
| `SYN-2016-*` (the non-departing gas cohort) | 18 of 18 | **0 of 18** |
| ids ending `g` (a gas leg) | 18 of 18 | **10 of 18** |
| segment | mixed | **`resi`, 18 of 18** |

The 18 are **8 dual-fuel households** (`PROS-2025-0136` + `PROS-2025-0136g`, and seven more pairs)
plus two singleton gas legs. Two small numbers coinciding is exactly the trap the item was pointing
at, and I walked into it from the other side.

### P2 holds, P3 holds, P4 not reached

- **P3** — `19 == 1 + 18` in the artefact as published. Internally consistent.
- **P2** — the two 19s decompose into disjoint mechanisms and their agreement carries no
  information. Confirmed as far as it can be *without reading the other lane's live copy*, which
  this probe deliberately does not do.
- **P4** — not reached, and I am saying so rather than implying coverage. Pricing a subset needs a
  run output this worktree does not have (see the provenance finding below); the no-cap property
  was established by reading the code instead — the three counts are three independent sums over
  one `per_account` list, `tools/couple_value_based_pricing.py:788-792`, with no cap and no shared
  constant. **A constant with the value 19 is ruled out. A subset probe is still owed by anyone who
  wants P4 itself.**

## What the cohort actually is

The floor cohort separates from the rest of the book almost perfectly on **one variable**:

| | FLOOR (n=18) | INTERIOR (n=378) |
|---|---|---|
| `eac_kwh` median | **229.0** | **4,829.6** |
| `eac_kwh` range | 102.0 – 1,010.8 | 560.0 – 36,382.5 |
| `value_margin_gbp_per_mwh` | **0.50 on all 18** — the bottom rung of the candidate grid | median 76.88 |
| vintage | 17 of 18 are `PROS-2025-*` | spread across 2016–2025 |

An account consuming 229 kWh/yr earns pennies from a margin increase while carrying the same churn
risk as anyone else, so the value arm correctly drives its margin to the floor. **The arm is not
wrong. The input is.**

## The input defect underneath it

`compare` computes, at `tools/couple_value_based_pricing.py`:

```python
years = max(1.0, bills / BILLS_PER_YEAR)
eac   = total_kwh / years
```

Measured over the 81 priced accounts this tree's book can match:

| | FLOOR | OTHER |
|---|---|---|
| n matched | 4 | 77 |
| `bill_count` median | **2.0** (min 2, max 2) | 25.0 |
| clamped by `max(1.0, …)` | **4 of 4** | 9 of 77 |

Every matchable floor account has **two bills** — about two months on supply. Its true tenure is
0.167 years; the clamp reports 1.0. So `eac = total_kwh / 1.0` instead of `total_kwh / 0.167`, and
a newly-acquired household of ordinary consumption **is presented to the pricing arm as a 6×
understated micro-account**. That is why the cohort is 17/18 `PROS-2025-*`: 2025 is `as_of_year`, so
these are the accounts acquired in the final year.

**This is the half-month-stub class CLAUDE.md already names.** The clamp is not a bug in isolation —
it stops a divide-by-zero — but it silently converts "I have not observed a year of this customer"
into "this customer consumes very little", which is a different claim, and the pricing arm cannot
tell them apart.

## Why the count is stable near 19 across two different books

Not a constant, and not luck in the way the item guessed: **the cohort size tracks "accounts
acquired in the final year with under a year of bills"**, which two runs over the same simulated
market will land at similar values. The *totals* can agree while the *splits* diverge (1/18 vs
17/2) because the working copy's world lets a different population depart, moving accounts between
the ceiling and floor branches without changing how many sit at an endpoint at all.

## What is owed, and by whom

1. **`eac_kwh` should carry its own confidence, or the clamp should refuse.** An account with two
   bills has no established EAC, and an honest `None` with a named reason is worth more than a
   number 6× low that the arm will price on. *Not fixed here* — it changes what the published
   artefact prices and belongs with the lane that owns `compare`'s pricing inputs, not inside a
   provenance change.
2. **P4's subset probe**, if anyone wants the size-invariance leg directly.
3. `endpoint_bound` is not mis-stated and needs no rename; `book_identity.read_from` (landed
   alongside this) is what now lets a reader see that two artefacts' 19s came from two books.

## Standing correction

The pre-registration's P1 was wrong and is left standing above rather than revised. It was drawn
from a number — 18 — appearing in two places on one day, which is the same reasoning error the
drawn item made with 19, one level up.
