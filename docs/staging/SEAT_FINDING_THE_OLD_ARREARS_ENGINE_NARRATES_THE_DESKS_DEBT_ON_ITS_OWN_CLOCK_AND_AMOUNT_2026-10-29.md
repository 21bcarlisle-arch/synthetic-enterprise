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
