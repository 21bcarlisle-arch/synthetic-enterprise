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


## Done, addendum (2026-11-15, delivery seat, drawn as `the-company-can-stop-recovery-through-the-meter`)

C37 (4f68e139c) landed the door, the routed row and the 27A leg under its own id, so this draw
took the disposition for those and built only the leg C37 had not proved: **a moratorium takes no
deduction from its first day.** C37 paused from the read day, so the deduction due on a Breathing
Space moratorium's start day was still taken, and that is a step to collect inside it (reg 7(7)(a);
the moratorium starts the day after the register entry the supplier is notified of, reg 26(1),
25(2)(b)). When `breathing_space` or the own hold refuses, `_pause_recovery` now pauses from the day
before the read; 27A keeps the read day. Controls in
`tests/company/billing/test_recovery_through_the_meter_reads_the_27a_watch.py`: zero deductions
from the start under either moratorium, the quiet partition, and 27A unchanged. Mutation: restoring
the read-day pause reds 1; skipping the gate reds 5. With no moved meter the desk returns before
the changed line, so a bill run is unchanged (no run moves a meter while take-up is 0). Ability to
pay stays GAP on this row (no world door gives the figure; never picked). Not built: refunding the
deductions taken between a start and a lagging read (GAP on the K8 page).
