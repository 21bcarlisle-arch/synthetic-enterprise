**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, "a gas-only account must be able to leave before the 158 can be priced"

# A gas-only account can now leave, and the book's renewal-decision population nearly doubles

Delivery seat, 2026-09-16. Repair 1 of the two the determination said were owed, landed. Repair 2
(the gas `tariff_type` read as the C1b roll) is deliberately **not** in this commit — see the last
section for why that ordering is load-bearing rather than tidy.

Pre-registration, written before any of this was built or run:
`docs/staging/SEAT_PREREGISTRATION_WHAT_A_DEPARTURE_ROUTE_FOR_A_GAS_ONLY_ACCOUNT_WILL_AND_WILL_NOT_MOVE_2026-09-16.md`.
Determination this discharges:
`docs/staging/done/SEAT_RESULT_THE_LAST_158_REFUSED_RENEWALS_ARE_EIGHTEEN_GAS_ONLY_ACCOUNTS_THAT_CANNOT_LEAVE_2026-09-16.md`.

---

## What was built

`simulation.customer_events.departure_decision_leg` names, per billing account, the single supply
point its departure is rolled on: **electricity if the account holds an electricity leg on this
roster, otherwise gas**. `run_phase2b` resolves it once per term into `_decision_leg` and both
departure bookings are gated on it, replacing the literal `commodity == "electricity"` they carried
at lines 1783 and 1982.

Four things travelled with it, each because the widened branch would otherwise read a
fuel-specific thing about a fuel the account does not buy:

| what | why it could not stay as it was |
|---|---|
| `old_elec_rate` → `old_decision_leg_rate` | the prior rate the decision is taken against, on whichever leg decides. A name saying "elec" reads as correct beside a guard saying "electricity" however wrong the guard is, which is most of why this defect was invisible from inside the branch |
| `_elec_rate_shock_counts` → `_rate_shock_counts`, counted on the decision leg | a gas-only account's shock history was permanently empty, which reads downstream as "never had a bill rise" rather than "nobody looked" — understating its departure risk, the direction that flatters the company |
| `payment_channel_for_customer(ba, "electricity")` → `(ba, commodity)` | the function is keyed on (customer, fuel) **by design** — a 72% DD anchor for electricity against 75% for gas. Asking it about electricity for a household with no electricity leg drew a channel off a supply point that does not exist |
| the Phase 14b gas pressure log gated on `commodity != _decision_leg` | `estimate_secondary_fuel_churn` is a belief about a SECONDARY fuel. `commodity == "gas"` and "gas is not the deciding leg" were the same test only while gas could never decide. Without this, a gas-only account's primary renewal would get a second, differently-shaped belief logged under a name asserting it is about something else |

On every account that holds an electricity leg, each of those four is the identity on what it
replaced.

## The results, against what was predicted

| | predicted | measured | |
|---|---|---|---|
| **P1** roster shape | the 18 are registered under ids that ARE their billing account | all 18 are drawn `SYN-2016-*` points, no `g` suffix to strip | **held** |
| **P2** route materially open | non-`None` decisions on the great majority of their renewals | **18 of 18** produce decisions; 81 renewal decisions where there were 0 | **held** |
| **P3** electricity population untouched | departing elec-holding accounts unchanged element for element | **74 → 75.** `PROS-2019-0261` departs in the repaired world and did not at HEAD | **REFUTED** |
| **P4** magnitude | between 3 and 12 of the 18 depart | **15** | **REFUTED** |

Two of four refuted, and both refutations are recorded here rather than in a revised prediction.

### P4: fifteen, not three-to-twelve

15 of 18 gas-only accounts depart at least once across 2016–2025. The interval was reasoned from a
per-account rate and the accounts are not comparable on that basis: all 18 are 2016 acquisitions
with up to nine annual renewal points each, so their **exposure** is at the top of the book's range
while my interval was built from the book's average. Per DECISION the rate is 15/81 = **18.5%**,
which is not an outlier. The prediction was wrong about the denominator, not about the hazard.

Stated plainly because it is the flattering direction to skip: three of the 18 (`SYN-2016-016`,
`-024`, `-038`) renew nine times and never leave. The roll is not a one-way door dressed as a
decision.

### P3: one electricity account moved, and here is the attribution

Four things changed at once, so the move could not be attributed on the two-arm comparison —
`green/green/red across three trees is not attribution`. A **third arm** was run: every edit above
kept, and only the two booking guards reverted to the `"electricity"` literal. One variable.

| arm | departing elec-holding accounts | departing gas-only | renewal decisions | SVT departures |
|---|---|---|---|---|
| **HEAD** | 74 | 0 | 91 | 37 |
| **guards reverted, all four other edits kept** | **74** | 0 | **91** | 37 |
| **repaired** | 75 | 15 | 171 | 37 |

The middle arm is **element-for-element identical to HEAD** — the same 74 accounts, the same
`churned_billing_accounts` set entire, the same 91 renewal decisions. So all four supporting edits
are exactly the identity on the electricity population, as claimed, and the sole cause of
`PROS-2019-0261` moving is the guard widening itself.

**Which means P3 was refuted by the world being coupled, not by the predicate being wrong.** The
guard's truth value did not move for any of the 136 accounts holding an electricity leg — that is
asserted directly by
`test_the_leg_is_unchanged_for_every_account_that_has_an_electricity_supply_point`. What moved is
what those accounts are deciding *inside*: 15 gas-only households now leave, so the book every
later decision is taken in is a different book. I predicted a set identity over a coupled world,
and a coupled world does not owe anyone one. The prediction was wrong in its premise, not in its
arithmetic.

**Which coupling channel carried it is NOT established here, and one arm cannot say.** The renewal
branch writes two things that are not per-account: `_competitor_position_ledger` (the rival's view
of this company, fed by every offer struck and read a quarter later) and the acquisition funnel (a
departure frees a replacement win). Either could carry a 2019 electricity renewal across from a gas
household's 2018 exit. Naming the one that did needs its own single-variable arm, and this document
does not claim it. **One account of 136 is the size of the effect and the right size of the
follow-up** — it is recorded so it cannot be discovered later as a surprise, not escalated.

## The number that matters most, and it is not in the predictions

**The book's renewal-decision population goes from 91 to 171** — the gas-only accounts contribute
81 decisions, 47% of the repaired total, where they contributed none. SVT-route departures are
unchanged at 37 (the gas legs are all labelled `fixed` or `None` today, so the SVT branch has no
gas subject yet — it will after repair 2).

This is a large change to the baseline world and it is recorded as one. It is a **fidelity**
change, which is the only reason a baseline is allowed to move: a household that buys its gas from
us and its electricity from someone else can switch gas supplier like anyone else, and until today
18 of this book's accounts — 11% — were settled, renewed and billed for a decade with no route out.
The decision was taken blind to company P&L, on the published fact that gas-only households switch,
and the P&L consequence is reported below rather than consulted above.

**A book of immortal households earns more than a real one**, so the direction of the correction is
against the company. 91 departing accounts where there were 75.

## What this does NOT claim

It does not admit the 158. It does not touch `UPLIFTABLE_TARIFF_TYPES` or
`resolved_tariff_type`'s gas branch. `method_skill` does not state a side and this turn does not
make it.

**The ordering was the determination's whole point and it holds after measurement, not just before
it.** Doing repair 2 first would have admitted 158 decisions from accounts that cannot leave into
`method_skill.concordance`, which `_survivorship` publishes as conditioned on survival — decisions
surviving by construction rather than by being priced well. With repair 1 landed those accounts now
depart at 18.5% per renewal, so when the 158 are admitted they will be admitted as decisions with a
real outcome. **That is now true and it was not true this morning.**

Deliberately still not predicted: the sign of the effect on the value arm's verdict. Repair 2 moves
roughly a third of the 72 labelled gas legs onto SVT and shrinks the priced population while the
158 enlarge it — two effects in opposite directions, one unbuilt. Nothing here is entitled to a
verdict move and none is claimed.

## Controls

`tests/simulation/test_a_departure_rolls_on_exactly_one_named_leg.py` — five legs, each
mutation-proven against a mutated COPY of the world file (never the live one; a control proven by
editing a file a concurrent run has open is proven against a race):

- the AST view and the text view agree on which lines book a departure (respell one site → fires);
- no booking is gated on a fuel LITERAL — the original defect in any spelling (restore
  `commodity == "electricity"` → fires);
- every booking IS gated on the resolved leg — the **mirror** defect, which has never happened here
  and would be invisible: `churned_billing_accounts` is a SET, so a dual-fuel household rolling on
  both legs leaves at about double its hazard and the only trace is a date that moved earlier (drop
  the gate → fires);
- both answers of the predicate are attained on the live roster — without this, a world where
  `_decision_leg` is a name that resolves to `"electricity"` for everybody passes every structural
  leg above, which is the original defect wearing the repair's clothes (make every account
  electricity → fires);
- the predicate is the identity on all 136 accounts holding an electricity leg, which is the whole
  warrant for landing this (substitute a predicate that is not → fires).

`tests/simulation/test_a_departure_is_booked_only_on_an_electricity_leg.py` is **deleted** in the
same commit. Its own docstring set that contract: it asserted the negation of leg 2 above and the
two cannot both stand.

## What is owed next

Repair 2, and it is now unblocked: the gas `tariff_type` read as the C1b roll — opening term fixed
because an account arrives by taking a deal, every boundary after decided by
`rolls_active_renewal` — which needs `simulation.svt_product.build_svt_schedule`
fuel-parameterised. `simulation.svt_rates.get_svt_gas_rate_gbp_per_mwh` already carries the gas cap
at the same granularity. **Not** `or "fixed"` on its own: that is the blanket-fixed the 2026-08-28
determination refused. `tests/simulation/test_the_tariff_type_read_has_one_home.py` stays red until
it lands.
