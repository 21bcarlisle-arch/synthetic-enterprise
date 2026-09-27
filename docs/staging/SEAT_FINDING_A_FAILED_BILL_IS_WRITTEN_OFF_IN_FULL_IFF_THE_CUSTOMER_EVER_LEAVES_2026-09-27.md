**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`

# A failed bill is written off in full if and only if the customer ever leaves, so tenure multiplies a leaver's bad debt

**2026-09-27.** Found while root-causing the selection residual
(`records/SEAT_RESULT_THE_SELECTION_SWITCH_IS_ONE_ACCOUNTS_CHURN_ROLL_AND_ITS_MONEY_IS_THE_WRITE_OFF_RULE_2026-09-27.md`).

## What the world does

`simulation/arrears_engine.py:519` `compute_emergent_bad_debt`, unchanged since `a1c7b4b50`
(2026-07-04):

    if outcome not in ("failed", "dispute"): continue
    will_be_written_off = cid in churned_ids
    if not will_be_written_off: continue
    ... result[(cid, write_off_year)] += amount     # the whole bill

Two consequences, and both are odd against how a supplier's arrears actually resolve:

1. **A customer who leaves at any point has every bill that ever failed written off in full.** This
   includes a bill that failed years before they left, while they were still on supply and still
   being billed. A write-off date is taken from the bill's own due date, so the write-off lands
   while the account is live.
2. **A customer who never leaves has no failed bill ever written off**, however many fail.

The rule is keyed to a future event (end-of-window churn membership). It is sim-side, so this is not
an epistemic-wall breach, but it is a fidelity question.

## Why it matters now

It is the whole money of the selection switch. Retaining PROS-2016-0098 for three extra years earns
+£1,415.95 of margin and costs about £6,767 of write-offs, only because it eventually leaves. The
published selection figure's sign on a seed is decided by this.

## The question for the director (the third side of knowledge)

Is it right that a failed payment during tenure becomes a written-off debt because the customer
leaves later? My understanding is that it should not. A failed direct debit is normally re-presented
or chased, and what a supplier writes off is the balance **still unpaid when the account closes**
(the final-bill debt after collection). A long-standing customer with persistent unpaid arrears can
also be written off without leaving. **Recommendation:** re-key the rule to the unpaid balance at the
account's close (plus persistent-arrears write-off for stayers), sourced from published write-off
practice before any constant is set. I will not change the world until he confirms the frame,
because the baseline/curriculum split requires the world change for a fidelity reason, and this one
was noticed through a company result.
