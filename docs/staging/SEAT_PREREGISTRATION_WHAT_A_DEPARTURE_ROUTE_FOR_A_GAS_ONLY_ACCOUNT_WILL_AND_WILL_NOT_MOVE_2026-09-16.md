**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, "a gas-only account must be able to leave before the 158 can be priced"

# Pre-registration: what a departure route for a gas-only account will and will not move

Delivery seat, 2026-09-16, **written before the repair is built and before any of it is run.**
Filed because the answers below are not known here, and a prediction recorded after the answer is
not a prediction.

The finding this discharges:
`docs/staging/SEAT_RESULT_THE_LAST_158_REFUSED_RENEWALS_ARE_EIGHTEEN_GAS_ONLY_ACCOUNTS_THAT_CANNOT_LEAVE_2026-09-16.md`.

---

## The repair being predicted

`simulation/run_phase2b.py` guards both of its departure bookings with `commodity ==
"electricity"` (lines 1783 and 1982). The proposed repair replaces that literal with the account's
**decision leg** — the one supply point that carries its departure roll:

> electricity if the billing account holds an electricity leg on this roster, otherwise gas.

That predicate is chosen so the repair is, by construction, **behaviour-preserving for every
account that has an electricity leg** and opens a route for exactly the accounts that do not. It is
not a widening of who may leave per renewal cycle: each account still rolls on exactly one leg.

## P1 — the roster shape the repair has to sit on

`build_churn_risk` raises `KeyError` for a billing account with no entry in `customers` keyed by
`customer_id`, and it is already called today over **all** settlement records — gas-only accounts
included — on every electricity renewal roll.

**Predicted:** it does not raise today, therefore the 18 gas-only accounts' supply points are
registered under ids that ARE their own billing account (no `g` suffix to strip), not under a
suffixed id whose stripped form names no customer. Confidence: moderate — the alternative is that
something upstream of `score_experience_signals` drops them, which would be a second finding.

**Refuted if:** the 18 carry `g`-suffixed ids, in which case `roll_lifecycle_event` cannot be
reached for them without a second repair and this turn's scope grows.

## P2 — does the route actually carry a decision, or only reach one?

A booking site being reachable is not the same as a decision being produced.
`roll_lifecycle_event` returns `None` — silently, no event, no departure — when the churn model
holds no renewal entry for that billing account at that term month.

**Predicted:** a gas-only account at `term_index >= 1` produces a non-`None` event on the great
majority of its renewals, because `build_churn_risk` is driven by settlement records and is
commodity-blind (it keys off `score_experience_signals`, which reads billing periods, not fuels).

**Refuted if:** the gas-only accounts reach the roll and it returns `None` throughout. That
outcome is the important one to catch: it would mean the route is *lexically* open and *materially*
closed, which is worse than the present defect because it looks repaired. **A route that books
zero departures over a decade across 18 accounts is a refutation, not a result**, and this
document is the reason that cannot be quietly reported as success.

## P3 — the accounts that already had a route

**Predicted:** the set of departing billing accounts that hold an electricity leg is **unchanged,
element for element**, and so is every departure date. The decision-leg predicate returns
`"electricity"` for all 146 of them, so the guard's truth value cannot have moved.

**Refuted if:** any electricity-holding account's departure appears, disappears or moves. That
would mean the predicate is not the identity on that population and the repair is not the
behaviour-preserving one described here — a defect, not a finding.

## P4 — magnitude, stated as a range so it can be wrong

**Predicted:** over the 2016–2025 window, **between 3 and 12** of the 18 gas-only accounts depart
at least once. Reasoning: ~7 renewal points each at this book's anchored whole-population departure
level. Recorded as an interval rather than a point because the only thing the number has to do is
be capable of being outside it.

Deliberately **not** predicted: the sign of the effect on the value arm's verdict. Repair 2 (the
gas `tariff_type` read as the C1b roll) moves roughly a third of the already-labelled gas legs onto
SVT and shrinks the priced population, while the 158 enlarge it. Two effects in opposite
directions, one of them not yet built — nothing here can attribute a move in the verdict, and the
honest statement is that this turn is not entitled to one.

## P5 — what this turn does NOT claim

It does not claim `method_skill` states a side. It does not admit the 158. It does not touch
`UPLIFTABLE_TARIFF_TYPES` or the gas `tariff_type` read. Those are downstream of this, and the
determination is explicit that doing the second without the first is the defect.

## OUTCOME, appended 2026-09-16 — two of four refuted

Recorded here beside the claims and **nothing above this line was edited**, because a prediction
revised after its answer is not a prediction. Full result:
`SEAT_RESULT_A_GAS_ONLY_ACCOUNT_CAN_NOW_LEAVE_AND_THE_BOOKS_RENEWAL_DECISION_POPULATION_NEARLY_DOUBLES_2026-09-16.md`.

- **P1 held.** All 18 are drawn `SYN-2016-*` points with no `g` suffix.
- **P2 held, and decisively.** 18 of 18 produce renewal decisions — 81 where there were 0.
- **P3 REFUTED.** 74 → 75 elec-holding departures: `PROS-2019-0261` leaves in the repaired world
  and did not at HEAD. A third, single-variable arm attributes it to the guard widening alone (the
  four supporting edits reproduce HEAD element for element). **The predicate did not move for any
  of the 136 — I predicted a set identity over a COUPLED world, and 15 gas-only departures change
  the book every later decision is taken in. Wrong in the premise, not the arithmetic.**
- **P4 REFUTED.** 15 of 18 depart, against a predicted 3–12. The interval was built from the book's
  average exposure and all 18 are 2016 acquisitions with up to nine renewal points each. Per
  DECISION the rate is 18.5%, which is unremarkable. **Wrong about the denominator.**

The one thing worth having predicted and not predicted: the renewal-decision population going 91 →
171. Neither P2 nor P4 asks for a book-level count, so the largest number this change produced was
not on the card at all.

## How each of these is settled

One run of `simulation.run_phase2b.main()` on the live roster, before and after, compared on
`churned_billing_accounts` — not on a headline. P1 and P2 are read from the run's own logs
(`_svt_decisions`, the lifecycle event stream); P3 is a set comparison; P4 is a count.
