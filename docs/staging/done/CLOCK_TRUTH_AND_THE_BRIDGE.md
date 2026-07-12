# CLOCK_TRUTH_AND_THE_BRIDGE — the site is publishing the wrong clock (P0)

**Staged:** 2026-07-12 by advisor, following BILL_TO_LEDGER_LINKAGE answer (b)
(settlement-derived P&L, no code path from bills; ~4.2x divergence vs the
bill-derived view). Excellent finding — now finish it, because the public
consequence is live.

## The exposure (act today)
poesys.net's FRONT DOOR publishes "NET MARGIN (ALL-TIME) £1,523,952" and
"ENTERPRISE VALUE £7,735,816" (EV derived from margin). Both are
SETTLEMENT-derived, both carry NO BASIS LABEL, and a 4.2x bill-vs-ledger
divergence sits underneath them. An expert who finds a 4x gap between what a
supplier billed and what it booked does not file a finding — they leave.
Note the irony precisely: the site constitution's NUMBER-PASSPORT rule
(basis + freshness + provisional) exists to prevent exactly this, and the
site's single most prominent figure violates it.

## What to do — publish the bridge, not a number
1. **Do NOT simply swap to the bill-derived figure.** Neither view is "the
   P&L" until they reconcile. A real supplier reconciles billed revenue to
   settled volumes with explicit bridging items.
2. **Build and publish the reconciliation bridge** (this IS D2_three_clocks'
   real deliverable, and it now has a precise target):
   settlement-derived net -> [unbilled accrual] -> [estimated-vs-actual read
   differences] -> [held/unissued bills] -> [write-offs] -> [SC correction] ->
   [VAT treatment] -> [any others found] -> bill-derived net.
   Every reconciling item named, quantified, and evidenced. The 4.2x must be
   fully explained by named items or the remainder is an OPEN DEFECT and must
   be shown as such.
3. **Immediate passport pass (cheap, do first):** every public figure carries
   basis (billed / settled / banked), freshness stamp, and PROVISIONAL badge.
   The headline margin and EV get an explicit basis label TODAY, plus a link
   to the bridge (or, until the bridge exists, to a stated open-defect entry
   on the Simplified page). No unlabelled headline figures anywhere.
4. **EV inherits the divergence:** it is derived from margin. Recompute on the
   reconciled basis when the bridge lands; until then, label it as derived
   from the settled clock and flag the dependency on the site.
5. **Adjudicate the cold-walk finding** coldwalk:margin_reconciliation_
   portfolio_vs_ledger as REAL, root cause = this defect, resolved-by = the
   bridge. Two independent routes (blindfolded CFO persona; advisor's SC
   arithmetic chase) found the same defect within six hours — record that in
   the retro as evidence the immune system works.

## Standing rule (add to CLAUDE.md)
**No financial figure is published without its clock.** A number whose basis
is unstated is a defect, not a formatting choice. Extend the page-consistency
invariant: any published financial figure lacking a basis label fails the
gate.

## DoD
Passport pass live and pixel-verified on the front door (headline margin + EV
labelled, linked); bridge built with every reconciling item quantified or the
unexplained remainder shown as an open defect; EV basis stated; cold-walk
finding adjudicated; standing rule in CLAUDE.md; digest line. This is the
highest-value credibility work on the board — it outranks new features.
