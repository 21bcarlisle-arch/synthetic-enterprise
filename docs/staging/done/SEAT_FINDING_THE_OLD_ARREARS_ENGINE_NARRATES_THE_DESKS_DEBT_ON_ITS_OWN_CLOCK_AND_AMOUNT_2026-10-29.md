**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The old arrears engine still narrates the desk's debt, on its own clock and amount (2026-10-29)

**Question.** Why does "the page shows an overdue notice dated before the missed payment its story opens on"
refuse 217 of 402 debt matches on the 209c3350ab book (probe `/var/tmp/onemiss-scripts/debt_slot.py`; trace
`notice_trace.py`, same directory)?

**Prediction (the dispatch's, kept).** A second definition with two homes: `arrears_first_notice` and
`collections_missed_payment` on different clocks. **Result: half right.**

| shown decision before the miss | n | cause |
|---|---|---|
| `collections_repayment_plan_offer` / `_reoffer` / `final_notice` | 162 | an EARLIER desk journey, cleared (`collections_cured`) before the next opened. All 217 had a close between. Honest history, not a defect |
| `arrears_first_notice` / `arrears_second_notice` | 55 | the old engine, narrating the desk's own debt |

The check now exempts only the first group (`_JOURNEY_CLOSES` in `tools/generate_explore_cast.py`). On 209c3350ab:
refusals 217 -> 55, valid households 103 -> 195, the slot still fills.

**The real second home.** For the 55, e.g. OCC-9edd7eed4aab: the desk reads "GBP60.78 overdue" on 22 Jul 2019 and the
old engine's first notice the same day says "GBP18.71 outstanding"; OCC-69932b473610 prints GBP79.11 beside the desk's
GBP273.85. Two engines write notices for one debt, with different balances. A reader sees two amounts owed.

**Not fixed here.** Whether the arrears engine should stay silent while the desk holds the debt (one narrator) is a billing
change with an Ofgem-notice question (which document the customer is actually sent). K8 says the knowledge page comes
first. Next step: `debt_and_collections.md` section on who sends the overdue notice, then suppress or reconcile.
The next-largest debt refusal is separate: "places the debt with an agency, no moment shows it", 117 of 402.

## Done (2026-10-29)

Knowledge first: `docs/market_research/company_debt_management.md`, "Who sends the overdue notice while
the desk's journey is open: the desk, alone". One supplier sends one letter per act (SAP FI-CA dunning is
per account; the 2014 Ofgem debt-letter review on truthful letters). GAP N1: no published source names
the document, because it is too obvious to write down.

Built: `company/analytics/decision_event_ledger.yield_to_the_desk`. A ledger FIRST/SECOND_NOTICE dated
inside a desk journey on the same account (first stage to exit, open-ended if none) is not put on the
household record. The ledger's other stages stay. A dual-fuel gas leg yields to the home's account
(`desk_journeys`), because the desk holds a dual-fuel home on one account.

Measured on the 209c3350ab pages at origin/main: refusals 55 -> 3, valid debt households 195 -> 223,
ledger letters on the record 3,443 -> 66. The prediction of 0 was refuted. The first cut left 31 because
of the gas-leg keying, and this change fixes that. **Residual, not fixed:** 3 gas misses where the ledger
records a miss and the desk opened no journey (SYN-2016-606, gas DD failed 15 Oct 2020). There the ledger's
letter is the only narrator, so the refusal is honest. Why the desk saw nothing overdue is open. The
next-largest debt refusal is unchanged and separate: agency placement with no moment shown, 117 of 402.
