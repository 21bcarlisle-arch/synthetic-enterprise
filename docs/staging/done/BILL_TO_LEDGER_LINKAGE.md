# BILL_TO_LEDGER_LINKAGE — does the P&L read the bills? (P0 question, evidence required)

**Staged:** 2026-07-12 by advisor. **Advisor correction on record first:** the
advisor repeatedly claimed published net was "frozen" and the SC fix had not
landed. That was WRONG — net moved £1,523,825 -> £1,523,952 -> £1,524,023 ->
£1,524,058. The advisor was reading a single day's window and inferring a
trend (R9 failure, advisor's own). The agent's evidence was right. Record this
in the retro; the advisor is not exempt.

## The question the correction exposes
Total net movement across ALL of yesterday's and last night's fixes: **+£233
on £1.52M = 0.015%, and UPWARD.**

The standing-charge defect was: every resi/SME bill, both fuels, 2016-2025,
double-charging the standing charge (~44% over on the 2024 elec SC line). SC
is roughly a tenth of a typical bill (C1: £8 of £73). Removing a decade-long
overcharge of that size should reduce revenue by a PERCENT-LEVEL amount —
i.e. tens of thousands of pounds, DOWNWARD. It did not.

Therefore exactly one of these is true — determine which, with evidence:

**(a) Propagation gap:** the fix corrected the rendered bill artefact but the
revenue ledger / P&L path still carries the old figures (or never recomputed).
-> Find it, fix it, republish, report before/after.

**(b) The P&L does not derive from bills at all** — revenue is booked from the
settlement path (which always had the correct SC), so the double-charge lived
only in the customer-facing artefact and never touched the accounts.
-> **This is the more serious finding.** It means the bill is DECORATIVE: the
company can bill a customer £X and book £Y with nothing objecting. In a real
supplier the bill IS the revenue-recognition event, and the "billed" clock in
the three-clocks design means exactly "what we actually billed". A billed
clock that does not read the bills is not a billed clock.
-> If (b): raise as an architectural defect against the three-clocks work
(M2), specify that billed-revenue must be derived from issued bill artefacts
(sum of bill lines), and add a Tier-1 invariant: **for any period, revenue
recognised on the billed clock == sum of bills issued** (to the penny;
divergence = held exception). Then re-run and report the true P&L impact of
the SC fix.

## Non-negotiables
Answer with evidence (code paths + a worked example on one customer, e.g. C1
July 2020: what the bill charged vs what the ledger booked). No narrative.
State (a) or (b) plainly. If it is (b), do not soften it — it is exactly the
class of defect this project exists to catch, and catching it is a success,
not an embarrassment.

## DoD
Root cause stated (a or b) with evidence; the divergence invariant specified
(and built if (b)); true SC-fix P&L impact published with before/after; one
digest line; adjudication ledger entry.
