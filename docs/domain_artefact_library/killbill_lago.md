# Kill Bill & Lago — open-source billing/subscription platform entity models

**Purpose:** compare Kill Bill's and Lago's invoicing/dunning/subscription entity design
against this project's own billing module (`saas/bill_generator.py`, `company/billing/*`) as
prior art — design comparison only, not adoption of either platform's code.

## Sources (R9)

- Kill Bill subscription guide, https://docs.killbill.io/latest/userguide_subscription
  (version not stated on page).
- Kill Bill overdue/dunning system, https://docs.killbill.io/latest/overdue.html (same doc set).
- Lago invoicing guides: https://getlago.com/docs/guide/invoicing/void,
  https://getlago.com/docs/guide/invoicing/draft-invoices,
  https://doc.getlago.com/guide/dunning/automatic-dunning (no explicit version shown on any page).

## Kill Bill's entity model

Account (top-level customer record; subscriptions/invoices/payments all link to it, supports
parent/child hierarchies for reseller billing) → Bundle (groups related Subscriptions so a
cancel/change on one can cascade) → Subscription (belongs to one Bundle, created from a
catalog Plan with an effective date; Plan = Product + terms + billing). Invoices derive from
active subscriptions.

**Dunning/overdue state machine** (three named states, driven purely by days since the
earliest unpaid invoice):
- **WARNING** at 10 days unpaid — blocks plan changes, service stays on, re-evaluated every 4 days.
- **BLOCKED** at 14 days unpaid — same blocking, re-evaluated every 7 days, entitlement still active.
- **CANCELLATION** at 21 days unpaid — subscription cancelled at end-of-term, no proration.

Payment retries recommended 1 day before each boundary (days 9/13/20) to maximise recovery
before a transition fires.

## Lago's entity model

Customer → Subscription (assigned from a Plan) → Invoice. Invoice status is a linear,
one-way lifecycle: **draft** (editable — usage records, fee edits, coupons — auto-finalises
at grace-period end or manually) → **finalized** (locked, fires `invoice.created` webhook) →
**voided** (terminal, zero-value for reporting, immutable, kept only as an accounting
paper-trail — explicitly not the same as delete). Dunning is a separate **campaign** concept
(org-wide or per-customer), triggered by an **overdue-balance currency threshold** rather
than Kill Bill's day-count — a materially different dunning trigger philosophy
(amount-based vs. time-based).

## This project's own existing state machines (grepped directly, not assumed)

Already has ~20 dedicated `Status` enums in `company/billing/` covering UK-specific
processes Kill Bill/Lago have no equivalent for (`WHDStatus`, `PPMDebtLoadStatus`,
`BreathingSpaceStatus`, `DDMandateStatus`, `RevenueProtectionCaseStatus`, etc.). The closest
direct analogue is `account_closure.py::ClosureStatus` (a linear closure lifecycle:
`initiate → receive_final_read → issue_final_bill → return_deposit/apply_deposit_to_debt →
refer_to_debt_collection → close`) — structurally similar to Lago's draft→finalized→voided
linearity, but domain-specific (UK final-bill/deposit/debt-referral steps neither platform
models). No existing collections ladder in this repo currently combines BOTH a day-count AND
a balance-threshold trigger the way the two platforms together suggest could be worth
comparing against `arrears_engine.py` (not reviewed in this pass — a natural follow-up, out
of this pass's scope).

## Adopt/adapt/skip verdicts

- **Kill Bill's day-count dunning ladder (WARNING/BLOCKED/CANCELLATION): ADAPT.** The
  specific 10/14/21-day cadence is Kill Bill's own product default, not a UK regulatory
  anchor, but the *shape* (graduated severity + a re-evaluation interval decoupled from the
  trigger check) is a clean pattern worth comparing against this project's own collections
  ladder in `arrears_engine.py`.
- **Lago's invoice lifecycle (draft→finalized→voided): SKIP** as a direct import — this
  project's bills are generated programmatically from settlement data, not edited
  interactively, so a "draft, editable" state has no real analogue here. The
  **void-not-delete, paper-trail-preserving** principle is worth noting as general
  accounting-hygiene practice, but it's generic double-entry discipline, not distinctively
  Lago's.
- **Account/subscription entity split (both platforms): SKIP.** This project already has its
  own mature, UK-specific entity model (meter points, contracts, tariff changes) that
  predates and diverges from a generic SaaS subscription shape; forcing a
  Bundle/Subscription/Plan split on top would be a rewrite for no fidelity gain.

## Provenance tag

Neither source is data — both are external software-design references. Per the instruction's
own tagging scheme, neither `generator-anchor` nor `validator-anchor` cleanly applies (those
are for company-boundary DATA sources), and `company-knowable` doesn't fit either (not
something a real UK supplier "knows"). **Gap noted for the library maintainer**: this class
of source (external SOFTWARE-DESIGN reference, not a data anchor) recurs across this survey
(also true of PowerTAC) — the three-tag scheme may need a fourth category, or an explicit
"design-reference, no runtime tag" note, rather than forcing every entry into one of the
three data-oriented tags.

## Follow-up registered, not started this pass

Direct comparison against `arrears_engine.py`'s actual collections-ladder logic — this entry
only confirms no existing mechanism combines a day-count AND balance-threshold trigger; it
does not assess whether `arrears_engine.py` should adopt either idea.
