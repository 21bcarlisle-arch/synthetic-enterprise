**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: the settlement curve at 400 founder households, budget 7,700 (2026-10-20)

Written before the probe. Acts on the director's ruling of 20 Oct 17:40
(`docs/staging/advisor/done/DIRECTOR_RULING_FOUNDER_HOUSEHOLDS_WITH_BUDGET_RAISED_2026-10-20.md`).

## 1. The budget, derived rather than typed

At seed 20260724 on origin `7858b89a6`, `founder_book()` gives:

| Unit | Records | Founder committed cy (to 2026-01-01) |
|---|---|---|
| supply_points (today) | 400 | 3,793.5 |
| households (the ruling) | 689 | 6,535.7 |

The campaign's room today is 5,000 − 3,793.5 = **1,206.5 cy**. Keeping it gives 6,535.7 + 1,206.5 =
**7,742.2**. Shipped at **7,700**, floored to 50 by the rule this constant has always used, so that
the memory leg keeps a margin rather than starting at zero. The campaign keeps 1,164.3 cy, 96.5% of
today's. Correction beside the row: the `for_the_director` row said 697 records and 6,603 cy. Those
figures came from a tree before the current founder draw. Today's book gives 689 and 6,535.7.

## 2. Why a probe and not a constant change

`test_the_settlement_ceiling_does_not_outrun_the_measured_memory_curve` prices the ceiling from
the newest `settlement_ceiling_slope_*.json`. The 9 Oct curve supports about 6,657–6,857, so 7,700
cannot land on it, and it is right that it cannot: that curve was measured at 400 supply points.
The curve is re-taken at the new shape. The unit and the budget land together on the new curve.

## 3. The run

`tools.settlement_ceiling_probe --budgets 7000 7700`, in a scratch worktree at `7858b89a6` with
`founder_unit: households`, full window, the live path's compute. The two points run serially.

## 4. Predictions (from the 19 Oct small-book line: 1,160 MB + 0.458 MB per founder cy, ~1 MB per campaign cy)

- **P1.** The peak child RSS at 7,700 is 5,000–5,700 MB. The central estimate is 5,350–5,540.
- **P2.** The peak at 7,000 is 4,600–5,200 MB.
- **P3.** The wall time at 7,700 is 7,000–10,000 s.
- **P4.** The curve supports a ceiling at or above 7,700 against 0.25 × guest. If not, the shipped
  budget is the largest that the curve supports, floored to 50, and he is told.
- **Decision rule, fixed now.** If the 7,700 peak plus the 227 MB production parent is within 5% of
  6,008 MB (above 5,708 MB), I do not switch. Production stays at 400 supply points, and I bring a
  proposal (his caveat).

## 5. Grade

*(Below this line, beside the predictions. No prediction is edited.)*
