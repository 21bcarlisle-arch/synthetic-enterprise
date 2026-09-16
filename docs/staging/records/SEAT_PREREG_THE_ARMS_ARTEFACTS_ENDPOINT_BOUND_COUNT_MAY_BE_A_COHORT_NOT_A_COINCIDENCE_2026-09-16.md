**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
"the-arms-artefact-cannot-name-the-book-or-the-world-it-priced"

# Pre-registration: is `endpoint_bound == 19` in both arms artefacts a coincidence, or a cohort?

Delivery seat, 2026-09-16, written against `5a63cb3a3` **before any of the measurements below were
run**. The answer is not known to me at the time of writing.

---

## The question, as the drawn item put it

> `endpoint_bound` is 19 in BOTH the HEAD and working copies despite near-disjoint books of 397 and
> 226 accounts (split 1/18 vs 17/2) — either coincidence or a constant leaking into a count, not
> established, one probe owed.

`docs/observability/value_based_pricing_arms.json` at HEAD carries `endpoint_bound: 19`,
`endpoint_at_ceiling: 1`, `endpoint_at_floor: 18` over 397 accounts. The shared tree's uncommitted
copy — *another lane's live work, which this finding does not touch* — carries `endpoint_bound: 19`
over 226 accounts with the split near-reversed at 17/2.

## What was ALREADY measured before this file was written, and is therefore not a prediction

Recorded here so the two are not confused later.

1. `grep '\b19\b' company/pricing/value_based_renewal.py` returns **no hit on the decision path**.
   The three counts are three independent sums over one `per_account` list
   (`tools/couple_value_based_pricing.py:788-792`); there is no cap and no shared constant.
2. Therefore "a constant with the value 19" is already ruled out in its literal form. **The
   surviving form of the item's worry is a POPULATION leaking into a count, not a constant** — a
   fixed-size cohort that is floor-bound for a structural reason, which would look exactly like a
   constant to a reader diffing two artefacts.

## The predictions

**P1 — the cohort.** HEAD's 18 accounts with `endpoint_side == "floor"` are **exactly** the 18
gas-only accounts that could not depart, recorded in
`SEAT_RESULT_A_GAS_ONLY_ACCOUNT_CAN_NOW_LEAVE_…` as "all drawn `SYN-2016-*` points". Operationally:
the 18 floor-bound customer ids at HEAD are all gas legs, and their id set is a subset of the
non-departing gas-only cohort.

*Why I expect it:* 18 is a small number appearing twice, on the same book, in two artefacts written
days apart, and an account the world will not let leave has no churn response — so the value arm's
search has nothing to trade against price and falls to the bottom of the candidate grid. That is a
floor, mechanically.

**P2 — the equality is a coincidence.** The two 19s decompose into **disjoint mechanisms**: at HEAD
it is 18 floor + 1 ceiling; in the working copy it is 17 ceiling + 2 floor. If P1 holds, the two
counts do not measure the same thing and their agreement carries no information.

**P3 — internal consistency.** `endpoint_bound == endpoint_at_ceiling + endpoint_at_floor` in
HEAD's artefact (19 = 1 + 18). This is close to true by construction; registered so that a FAILURE
here would be the finding instead.

**P4 — the count is not size-invariant.** `endpoint_bound` is a sum over priced accounts with no
cap, so pricing a strict subset of the book yields a count `<= 19`. If a subset ever returns
exactly 19 when the mechanism says it should not, P4 is refuted and the item's "constant leaking"
reading is back.

## What would refute each

| prediction | refuted by |
|---|---|
| P1 | any of the 18 floor-bound ids being an electricity-only account, or the set not matching the gas-only non-departing cohort |
| P2 | the two 19s decomposing into the *same* cohort — i.e. the same customer ids bound at both |
| P3 | `19 != 1 + 18` in the artefact as published |
| P4 | a strict subset of the book returning `endpoint_bound == 19` |

## What this probe is NOT

It does not read, grade, or land the shared tree's uncommitted copy. The 17/2 split quoted above is
taken from `SEAT_RESULT_THE_TWO_BLIND_ARM_ARTEFACTS_ARE_TWO_WORLDS_NOT_TWO_CALIBRATIONS_AND_NEITHER_
CAN_GRADE_THE_OTHER_2026-09-16.md`, which established that that copy is another lane's live,
in-flight work and must not be landed.

**Result filed beside this as `SEAT_RESULT_…`, with any refutation kept rather than revised.**
