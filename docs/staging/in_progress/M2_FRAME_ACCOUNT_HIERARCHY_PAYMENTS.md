**STATUS (2026-07-11): REGISTERED, NOT STARTED. Queued behind the two
director-witnessed live-bug fixes already in flight (thesis-chart chart-
rendering side, bill-arithmetic fix task). This is FRAME-only per its own
DoD (design doc + charter updates + sequencing proposal, no portal build) --
appropriate to queue rather than interrupt live-bug remediation.**

---

# M2 FRAME ADDENDUM — account hierarchy, combined billing, payment allocation (P1, FRAME)

**Staged:** 2026-07-11 by advisor; director-raised from live portal review
("still single fuel; need parent-account view; how do payments and partial
payments allocate; can it be one model for resi/SME/I&C?"). This is FRAME
work for M2 — design and record before the DD/cash engine hardens around
implicit answers. Coordinate with in-flight M2 build; do not rip up what
exists — frame, then converge.

## 1. Hierarchy (universal, all segments)
party -> account -> agreement -> supply point (MPAN/MPRN).
- Dual-fuel resi: one party, one account, TWO agreements, ONE combined
  statement. C1-class customers must gain a parent/account view in the
  portal (fuel tabs remain as drill-down).
- Multi-site I&C: one party, many sites/agreements; consolidated vs per-site
  invoicing is an account-level setting.
- SME: same skeleton, breadth in between.
One hierarchy; segments differ only in breadth and the accounting model (2).

## 2. Two accounting models over one ledger (the fork, per segment)
- **Balance-based** (resi + micro-SME, DD/budget-plan native): bills post
  debits, payments post credits, account carries a rolling balance; partial
  payment reduces balance; no bill-matching. DD plan vs actuals reconciles
  at account level (this is what makes flat-DD-vs-seasonal-bills coherent).
- **Open-item** (I&C + larger SME): payment allocates to specific invoices —
  per remittance advice where given, else OLDEST-FIRST; disputed invoices
  are excluded from ageing and dunning while held (dispute register already
  exists — wire it).
Both models emit the SAME ledger events (bitemporal) so E-lane accounts and
the three clocks are model-agnostic.

## 3. Non/partial payment physics (segment-parameterised, one engine)
Ageing buckets (30/60/90+), dunning paths per segment, statutory
late-payment interest for business debt only, write-offs as dated,
reasoned, P&L-visible events (fixes tonight's C1 settled-vs-outstanding
class properly). Feeds existing collections/PPM physics for resi.

## 4. Portal consequences (C-lane, sequence behind the mechanism)
Parent-account view: combined statement, balance ledger view (resi) /
open-item ageing view (I&C), per-fuel and per-site drill-down. The C1 page
the director reviewed becomes the drill-down, not the top.

## Anchors & verification
Anchor allocation rules to published practice (supplier terms, Ofgem debt
rules, Late Payment of Commercial Debts Act for B2B interest); record in
ASSUMPTIONS.md. Cold-eyes walk on the new statement views as part of DoD.

## DoD (FRAME)
Design doc committed (hierarchy, fork, allocation rules, event schema);
charters for D/E updated; build sequencing proposed into the M2 movement
plan; no portal build until the mechanism lands. One digest line.
