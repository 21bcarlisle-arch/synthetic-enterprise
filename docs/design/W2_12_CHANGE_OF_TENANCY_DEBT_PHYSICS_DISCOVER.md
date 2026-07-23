# W2_12 — Change-of-tenancy debt physics: DISCOVER output (2026-07-23)

**Atom:** `W2_12_change_of_tenancy_debt_physics` (lane W2_customer_generator, value_stream
meter_to_cash, epoch 3, provenance proposal, loop_stage discover).
**Authority:** director verdict `DIRECTOR_SEGMENTS_REVIEW_VERDICTS_2026-07-23.md` §3 item 1.
**This is DISCOVER only.** No code changes. BUILD stays epoch-gated (author now, BUILD when opened).
Deliverable per the atom brief: *read the three current mechanisms and name the exact seam where the
debt/revenue physics of the move would attach; fold, do not duplicate.* Level-1 is PROPOSED (agent
proposes with evidence; the director owns the cell move).

## 1. The director's frame (register verbatim)

> Every tenancy change is ONE credit-risk exit PLUS TWO deemed-rate entries (double jeopardy), and
> simultaneously the prime acquisition moment for high-value low-churn customers.

The atom UNIFIES three things currently held **separately**: acquisition (thin), the deemed-tariff
path (built), bad debt (built). The task is to name where a unified *move event* attaches, not to
re-build any of the three.

## 2. What already exists (the read)

| Physics of the move | Built today in | State |
|---|---|---|
| **Move-OUT credit-risk exit** — final bill that may never be paid | `company/billing/account_closure.py` (final bill, deposit offset, `DEBT_REFERRED`, SLC 21B 42-day deadline; `ClosureReason.VACANT_PROPERTY`) | **Built**, but triggered as an *account* event, not wired to a tenancy-change event from the life-event stream. |
| **Move-IN deemed-rate entries** — new occupant(s) land on deemed supply | `company/billing/deemed_contract.py` (DeemedContractRegister; `DeemedSupplyReason.NEW_TENANT` / `VOID_PERIOD_ENDED`; Ofgem 5-working-day notify, 12-month extended-deemed obligations) + `company/billing/cot.py` (`deemed_rate_gbp_per_kwh` = SVT + 20% uplift capped at the Ofgem cap; `COTType.MOVE_OUT/MOVE_IN`; `_VOID_UPLIFT`) | **Built**, deemed rate + notification physics present. |
| **CoT orchestration / void** — supply transfer, debt-follows-person, void period | `company/crm/change_of_tenancy_register.py` (CoT register; `CoTType.NEW_TENANT/NEW_OWNER/LANDLORD_RETURNING/EMPTY_PROPERTY/VOID_PERIOD`; debt is the person's not the property's — SLC 27 / SLC 12.2; fresh deemed contract from day 1; 3-attempt/28-day abandonment) | **Built** as a register/lifecycle; the debt/revenue *outcomes* of each path are not folded in. |
| **Acquisition (thin)** — post-move win probability | `saas/home_move_win_rate.py` (win-prob vs market price × EPC; combined with churn into effective retention) | **Built as a win-probability model only.** No revenue/value physics for landing a high-value low-churn occupant. |
| **The trigger** — move events | `company/crm/life_events.py` (`LifeEventType.MOVE_IN` / `MOVE_OUT`; W2_5 dependency) | **Built.** Emits the events; nothing consumes them into the CoT debt/revenue path. |

**Conclusion of the read:** all five pieces exist. Nothing is missing at the *component* level. What
is missing is the **coupling** — a move event does not today fan out into (a) an outgoing-account
closure with a payable-or-not final bill, (b) one/two incoming deemed entries, and (c) an
acquisition-value scoring — as one causally-linked transaction with measured debt and revenue.

## 3. The seam (name it)

**`company/crm/change_of_tenancy_register.py` is the natural home** — it is already the CoT
orchestrator and already types the move (NEW_TENANT / VOID_PERIOD / …). The seam is: a
`life_events` MOVE event drives a CoT register entry, and that entry FANS OUT to the three existing
mechanisms rather than each firing independently:

```
life_events.MOVE_OUT/MOVE_IN  ──▶  change_of_tenancy_register (CoT entry, already typed)
                                        │
        ┌───────────────────────────────┼────────────────────────────────┐
        ▼ (credit-risk exit)             ▼ (deemed entries)                ▼ (acquisition moment)
  account_closure.py               deemed_contract.py + cot.py       home_move_win_rate.py
  final bill → paid? / DEBT_REFERRED   NEW_TENANT deemed rate,        win-prob → *value* of a
  (the DEBT physics — currently        void uplift (the REVENUE       high-value low-churn landing
  the missing piece: p(final          physics of the entry)          (the missing acquisition-
  bill unpaid) as a modelled                                          value physics)
  outcome, not just a status)
```

**Two gaps the BUILD would close (fold, do not duplicate):**

1. **Debt physics of the exit.** `account_closure.py` has the `DEBT_REFERRED` *status* but no
   modelled *probability* that a move-out final bill goes unpaid (the "credit-risk exit"). This is
   the double-jeopardy debt leg — attaches at the closure step, keyed off the departing account's
   engagement/affordability archetype (couples to the W2 affordability + engagement work).
2. **Acquisition-value physics of the entry.** `home_move_win_rate.py` produces a *win probability*
   but no *value* of the win. The director's "prime acquisition moment for high-value low-churn
   customers" needs the win outcome to carry the CLV of the landed occupant (couples to
   `saas/enterprise_value.py`). Deemed-rate revenue during the deemed window is already in
   `cot.py`/`deemed_contract.py`; the missing piece is the *conversion* value.

**Do NOT duplicate:** no new register, no new deemed-rate engine, no new closure engine, no new
win-rate model. The BUILD is a *coupling* layer on the CoT register that consumes MOVE events and
records the debt outcome + acquisition value against the existing engines.

## 4. Scale / portability notes (design-by-constraint, not built now)

- **C-S1 event-arrival tolerance:** the coupling must behave correctly if the MOVE_OUT and MOVE_IN of
  the same tenancy change arrive singly / out of order (a void period is exactly "move-out arrived,
  move-in has not yet"). The `VOID_PERIOD` type already anticipates this.
- **C-S3 asynchronous wall contract:** the final-bill-paid-or-not outcome resolves *later* than the
  closure event (28/42-day windows already in the code) — model it as a separate event in time, not
  a same-step resolution.
- **Product-as-first-class (portability):** the debt/revenue physics are fuel-agnostic; the seam must
  not hardcode electricity (both `cot.py` fuel tables and the deemed register are already keyed).

## 5. Board Spec 006 item 9 linkage

The move-out final-bill non-payment risk + move-in deemed landing + void-property problem are Board
Spec 006 item 9 (PARTIAL). This DISCOVER confirms the "PARTIAL" reading: the *lifecycle* exists, the
*debt/revenue outcome physics of the move itself* do not. Closing item 9 = the two gaps in §3.

## 6. Proposed disposition

- **Level 1 PROPOSED** (DISCOVER complete; seam named; fold-not-duplicate confirmed). Cell move is the
  director's — logged to `docs/observability/level_up_proposals.jsonl`.
- **BUILD gated** (EPOCH_GATING; epoch 3). depends_on `W2_5_life_event_stream` (the trigger) — already
  in the atom. When opened, BUILD is a coupling layer on `change_of_tenancy_register.py`, ~2 gaps, no
  new engines.
