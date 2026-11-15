**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 3 · **Atom:** `C32_one_obligation_one_vulnerability_scorer`

# Recovery through the meter is a step to collect with no company door to stop it (2026-11-15)

Found by the census of every debt action (C32 ninth pass, item 12, step 2). The census is
`DEBT_STEP_CENSUS` in `company/billing/winter_moratorium.py` and is derived from the code by
`tests/company/billing/test_the_enforcement_table.py`.

## The defect

After a Consent move, the world takes weekly debt deductions from top-ups. The company only
*reads* them (`collections_journey._read_meter_recoveries`, through `get_meter_recoveries`). No seam
door lets it set or suspend a deduction. In a Breathing Space moratorium, SI 2020/1311 reg 7(7)(a)
forbids "a step to collect" moratorium debt, so those deductions would go on unlawfully. Nor could
the company act on its own hold, a 27A finding of self-disconnection, or the ability to pay.

## Live effect

None today:
- no run changes a meter (every Consent offer is withheld on the S&RP finding);
- no run holds a moratorium (`BreathingSpaceRegister.register_entry` has no caller).

It becomes live as soon as either of those is built. So it is ordered **before** a run that moves
meters, not after.

## What landed

- The `recovery_through_the_meter` row, in the table and on the commons §5 page:
  - Breathing Space: covered;
  - own hold: covered;
  - ability to pay, 27A, Safety Net, PSR and 28.15: GAP.
- The row is in `UNROUTED_ACTIONS`, so the gate answers it, but no route asks.

## What would close it

A world door: `SimInterface.suspend_meter_recovery(account, from, reason)`, or a deduction rate
set by the company. Then `_read_meter_recoveries` asks `may_take(METER_RECOVERY)` and suspends on
a refusal. The bypass pattern already names `suspend_deduction*`, so a door added under that name
must ask the gate.

NEXT: C32_one_obligation_one_vulnerability_scorer

## Done

2026-11-15, C37: the door is built. `SimInterface.suspend_deduction(account, after, reason)` pauses
the world's deduction (`HouseholdPlanBook.suspend_recovery`; `meter_recoveries(suspended_after=)`).
`_read_meter_recoveries` now asks `may_take(METER_RECOVERY)` at every read and pauses on a refusal,
so the row is routed (out of `UNROUTED_ACTIONS`; census `get_meter_recoveries` maps to it). The
Breathing Space and own-hold cells are now asked on the live path, and 27A is covered (commons
s.5, "Recovery through the meter, on the 27A watch"). Still not live: no run holds a moratorium
(`BreathingSpaceRegister.register_entry` has no caller), and no run moves a meter at take-up 0.

