**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `unminted` — Lane 0 delivery

# The rival's ledger now sees only electricity strikes, and electricity churn p fell on 17 of 101 renewals

Claim `observe-only-the-electricity-leg-in-the-rival-ledger`. Results against
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_OBSERVING_ONLY_THE_ELECTRICITY_LEG_IN_THE_RIVAL_LEDGER_MOVES_2026-10-01.md`,
which was written before either arm ran. Parent:
`SEAT_FINDING_A_GAS_RENEWAL_IS_NOW_PRICED_AGAINST_THE_GAS_SVT_AND_THE_RIVAL_LEDGER_MIXES_BOTH_FUELS_2026-10-01.md`.

## What changed

- `CompanyPositionLedger.observe` takes `commodity` as a **required keyword with no default**.
  It keeps electricity strikes, ignores gas, and refuses any other fuel by name.
- The rule lives in the ledger, not in the one caller, so no future caller can mix the fuels
  again. `run_phase2b` now passes the leg's fuel.

## Correction to the item's own direction (made in the pre-registration, before the run)

The item predicted "differential vs market UP, churn p UP". Removing gas strikes, which sit below
every electricity strike, raises the quarter mean. That lifts the rival's reference, so the same
offer reads cheaper and the differential falls. I registered DOWN, and DOWN is what happened.

## Controls

- `test_MUTATION_a_gas_strike_never_moves_the_rivals_electricity_position` asserts both legs of
  the partition: an electricity strike IS a position, and a gas strike leaves it unchanged.
  Deleting the gas-ignore line turns it red.
- `test_a_fuel_the_ledger_does_not_know_is_refused_by_name`.
- The run-wiring control now requires `commodity=commodity` at the call. Hard-coding
  `"electricity"` there turns it red.
- 211 passed across the reference, VAT-basis, churn, customer-events, `run_phase2b`, price-ladder
  and coupling suites. `tests/design/` and the static ratchet are green.

## Results: one variable, two `git archive` extracts of `e9c014e48`

Both arms had 256 customers. There were 107 base renewals and 108 new; all 107 base renewals matched.

| prediction | result | verdict |
|---|---|---|
| R1: electricity reference never falls | 17 up, 83 same, 1 down (2024-12-16, downstream of the 2021 flip) | HOLDS |
| R2: differential falls where R1 rose | 17 down, 1 up (the same downstream event) | HOLDS |
| R3: p falls on at least as many as it rises; mean −0–10% | 17 fell, 1 rose; mean 0.3267 → 0.3244 (**−0.7%**) | HOLDS, at the low end |
| R4: electricity churned −3..0 | 35 → 34. PROS-2020-0221 2021-07-05: p 0.206 → 0.179, churned → renewed | HOLDS (one roll) |
| R5: gas identical | 6 of 6 | HOLDS |
| R6: `vs_svt` identical | 99 of 101; the 2 moves are on 2021-07-10 and 08-15, after the flip | HOLDS, with the divergence exception |

**Why only 17 of 101 moved.** The ledger reads the PREVIOUS quarter only. Gas-only renewals are
6 events in 10 years, so a quarter holding a gas strike is rare (2016Q4/2017Q1, 2019Q1–Q2,
2021Q2). In every other quarter the two ledgers are the same. Where it did bind, the
reference moved by £8–18/MWh, a 5–10% lift.

**Pass-through is diluted again.** Differentials moved by 5–10 points, and p moved by 1–12%
relative. This is the same competing-risk dilution the two parent findings measured. Electricity
churn was overstated by this defect, but only by about 1% of mean p on this book.

## Not changed

The rival still has no gas side. A gas leg is read against the published gas default and nothing
moves it. That is a stated gap, as the parent finding recorded, and nothing in the knowledge layer
yet establishes how a gas rival defends.
