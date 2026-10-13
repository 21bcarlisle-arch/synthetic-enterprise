# A supplier's annual DD review is sized from its own issued bills, not true consumption — K8 note

**Purpose:** K8 knowledge-before-build note for claim `dd4b-in-loop-review-reads-the-suppliers-own-bill`,
acting on `docs/staging/SEAT_FINDING_THE_IN_LOOP_DD_REVIEW_IS_TOLD_TRUE_CONSUMPTION_NOT_THE_SUPPLIERS_
ESTIMATED_BILLS_2026-10-13.md`'s filed-not-built remedy: `simulation/dd_review_in_loop.py` fed the
review the loop's settled revenue at true meter kWh, where a real supplier reviewing a household with
estimated reads holds only its own issued bills. Written before the code change it authorises, per K8.

**Knowledge:** none — no dedicated DD-review knowledge-site topic exists yet; this note's conclusion is
recorded in the build commit that acts on it and in this file, per K8, until one is. The existing
`docs/market_research/what_a_supplier_holds_to_size_a_direct_debit.md` covers what sizes the OPENING
amount (AQ/EAC, the annualised-estimate convention) and, in its 2026-10-11/10-13 passes, the review
RULE's arithmetic — neither reaches this question, which is about the review's INPUT when a read in
the window is estimated rather than actual.

**Date:** 2026-10-13. **Method:** the question does not need a fresh external fetch — it follows from
a fact already established and cited in this repo's own knowledge layer (K4: too obvious to the trade
to be written down twice). A fixed direct debit review under SLC 27.15 (cited at
`what_a_supplier_holds_to_size_a_direct_debit.md` §5, "best and most current information... available
to it") is, definitionally, a review of what the supplier **holds** — its own account record — not of
a ground truth the supplier has no channel to observe mid-year. The company's billing system does not
carry a "true consumption" field on an estimated bill that it can privately consult; it carries the
bill it issued, which is the estimate, until a real read later confirms or corrects it.

## The question this note closes

`simulation/dd_review_in_loop.py` (built 2026-10-12, `71c324b6d`) asks the company's own review door,
`company.interfaces.dd_review.annual_dd_review_view`, for the review the household meets AS THE LOOP
RUNS — the fix that made DD4b reachable mid-term rather than only at a renewal. The bills it fed that
door were the loop's own monthly settled revenue, grossed up at VAT: i.e. revenue priced at the
meter's TRUE consumption, because that is what the world's settlement physics computes. The post-loop
chain (`simulation/run_phase4c_on_phase2b.py::build_monthly_bills`, called once at the end of a run)
reviews the SAME company door over the company's own `assemble_monthly_bills` output, where a read can
be ESTIMATED — a flat trailing estimate at the real unit rate, per `company/billing/
monthly_bill_assembly.py` and `company/billing/unread_month_estimate.py` — and only trued up when (and
if) a real read later arrives.

A real supplier's ADDR (annual DD review) runs over its own ledger. It cannot ask the meter what
actually happened; it asks its own billing system what it has charged. Where the billing system itself
was estimating (a non-communicating meter, a missed read, a smart meter not currently reporting), the
review's "actual annual spend" input is the ESTIMATED total, same as the bill the household received.
This is not a modelling convention that could reasonably go the other way — a process cannot review
input it structurally cannot see. The measured size of the gap this produced (`SEAT_FINDING_...`): on
`f200-low` (200 founders, budget 0), 135 of 847 in-loop reviews differed from the supplier's own bills
by more than 5% on volume, almost all of it `C7`'s 42 consecutive estimated months at a fifth of true
use (told 3.8× what was ever billed).

## What this settles, and what it leaves open

**Settled:** the in-loop review's bill feed must be the same bill a supplier would actually hold for
that customer-month — the output of the same assembly door and read feed the post-loop chain already
uses (`simulation.run_phase4c_on_phase2b.build_monthly_bills`, which wraps `company.billing.
monthly_bill_assembly.assemble_monthly_bills` with `simulation.meter_reads.SimulatedReadFeed`) — not a
re-derivation from true settled revenue.

**Left open, stated as a GAP rather than built:** whether a real supplier's ADDR system, mid-estimate-
run, additionally flags "this customer's spend estimate is unreliable" and defers or widens the
review rather than acting on it at face value. Nothing published establishes that; this build takes
the simpler, construction-forced reading — the review acts on the bills it has, as `annual_dd_review_
view` already does for the post-loop chain — and does not invent a deferral rule neither chain has.

**Move-in attribution**, the SEAT_FINDING's second named cause (44 of the 179-review tail, the owner's
void and unnamed-occupier months the post-loop bills include at a mover's first window but the former
loop-fed chain dropped): this is resolved by construction, not by a separate rule, once the in-loop
chain is fed from the SAME assembly call over the SAME accumulated settlement rows the post-loop chain
reads — there is only one attribution left to agree with, because there is only one assembly computing
it.
