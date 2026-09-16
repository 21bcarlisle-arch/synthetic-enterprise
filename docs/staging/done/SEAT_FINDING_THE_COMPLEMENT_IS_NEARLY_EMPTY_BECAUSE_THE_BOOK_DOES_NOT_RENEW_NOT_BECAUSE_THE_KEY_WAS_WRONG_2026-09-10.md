**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery · **Class:** measurements_that_mirror

# FINDING — the complement is nearly empty because the book does not RENEW, not because the key was wrong

**A roster of 100 inside a rolling population of 70 has almost no complement, along any draw.**

Measured by `tools/run_value_cycle_ab.py --partition-probe` at `a9ae86351`, world
`39a192ce04c1eda8`, full window, against the 100-account roster in
`value_cycle_ab_s1_three_arm.json`. Artefact:
`docs/observability/value_cycle_ab_floor_partition_probe_both_keys.json`.

Pre-registered and **graded beside its own predictions** in
`docs/design/PREREGISTRATION_WHETHER_THE_REST_OF_THE_BOOK_REACHES_A_CHURN_ROLL_AND_WHETHER_REDRAWING_IT_MOVES_SELECTION_2026-09-10.md`.

---

## The numbers

| | elasticity draw | churn roll |
|---|---|---|
| calls | 298 | **315** |
| accounts that took it | 67 | **70** |
| of the 100-account roster | 67 | 68 |
| roster accounts that took it **never** | 33 | 32 |
| **outside the roster** | **0** | **2** |
| `except` leg | **WOULD REFUSE** | has a complement |

Book: **164** billing accounts settled in the window. Accounts that roll but never draw: **3**. The
two outside-roster accounts are `PROS-2020-0287` and `PROS-2020-0303`. `selection_gbp` on the
pass: **−£332.64**, `settled-realised`.

## What this refutes, including my own prediction

**The direction's premise was that the complement is empty because the key is wrong.** Half true.
The elasticity draw *is* gated behind an offered rate and *is* therefore unreachable by unpriced
households — that was measured before this turn and is not in doubt. The inference drawn from it —
that a key the rest of the book takes would give a measurable complement — is **wrong**, and the
probe says so.

**My own pre-registered prediction 1b was wrong by more than two orders of magnitude.** I predicted
more than 300 outside-roster accounts and there are **2**. I wrote at the time that I had no basis
for the number and would report it plainly if badly wrong in either direction. It was.

The fact I did not have: **only 70 of the 164 settled accounts reach a renewal point in this window
at all**, and the arm's priced roster is 100. The complement of a 100-account roster inside a
70-account rolling population is a handful by arithmetic. **The rest of the book does not renew
here.** No choice of re-draw key touches that.

## What the re-keying did and did not buy

**Did:** `except_leg_would_refuse` goes from `true` to `false`. A churn-roll `except` leg would now
RUN rather than die on its first seed after 39 minutes. `V_rest` would be a real, imprecise
measurement instead of a zero that is an algebraic identity — a genuine difference in kind.

**Did not:** make it worth having. `V_rest` over **two households** is the category
`SEAT_FINDING_THE_FLOOR_DECOMPOSITIONS_REST_OF_BOOK_HALF_IS_EMPTY_..._2026-09-10` already ruled
inadequate for one household and the five-account leg on disk. Nothing about two changes that.

**So the nine-seed churn-roll `except` leg was NOT launched.** Six hours of compute for a
two-household `V_rest` buys a number that cannot support the claim it would be published under.
That is a decision, not a deferral, and it is recorded here rather than left as silence.

## Why this is LATENT and not RECORDED

It invalidates planned work. The prior finding's item 3, the direction that drew this claim, and the
value-arms page's own owed-work sentence all point at "a floor keyed to something the rest of the
book has". That work now has a measured answer: **the key was never the binding constraint.** Anyone
picking this up without reading this file spends six hours to learn it.

It is not BLOCKING: nothing on a surface is currently wrong. The page's figures stay correctly
withheld, and the mechanism landed this turn (`a9ae86351`, `a553f2f96`) is sound — it just cannot be
fed a sample worth publishing on this book.

## What would actually move it

Not a key, and not more seeds. The rolling population is the binding constraint, so:

* **a longer window**, or a window placed where more of the book has anniversaries; or
* **a funnel that offers renewals more widely** — 32 of the 100 priced roster accounts never roll
  at all, which is its own question and is not answered here; or
* **a different instrument entirely**, which is what the prior finding's "attained bound" result
  already concluded from the other direction.

None of those is a change to `run_value_cycle_ab`. **Each of the first two is a change to the world
or the arm and is not mine to make unilaterally** — the window is a run parameter, but which window
the published comparison lives on is a director-facing choice about what the page's figures mean.

## Corrections landed beside their claims

The code sentence "it is the quantity the rest of the book HAS" appeared in two places
(`simulation/customer_events.churn_roll_for_renewal` and `run_value_cycle_ab.REDRAW_KEYS`). Both are
corrected in place with the counts and the reason, and neither is deleted: it was right about the
mechanism and wrong about the magnitude, and a reader needs to see which half moved.

## What is still untested

`V_rest`'s actual value under the churn-roll key. It was not measured, and this finding makes no
claim about whether the wider book's churn cascade moves `selection_gbp` — only that **this
instrument cannot answer it on this book**, and now for a reason that is measured rather than
inferred.
