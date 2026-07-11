# ADVISOR_STEER — thesis chart credibility fixes (Tier 2, Door-1 follow-up)

**Staged:** 2026-07-11 by advisor after the director's live Expert Hour on the
deployed front door (screenshots reviewed). The page overall is strong; the
thesis chart — the single element built to impress — currently undermines
credibility. Three defects, one page:

## 1. Floor-vs-benchmark reads as too-good-to-be-true
£100 TRUE vs £4,489 benchmark (98% gap) with a caveat admitting the TRUE side
is "a floor, not a complete figure" (AI-compute cost unpopulated). An expert
reads the bars, then the caveat, and discounts the whole chart. Fix: do not
show a headline gap built on an admitted-incomplete side. Either (a) populate
the AI-compute line now from the token/usage logs at Anthropic list price (the
costing basis the director already decided in B2 — check the open question and
close it), or (b) until then, re-frame the visual as "cost FLOOR vs benchmark
— full figure pending" with the incompleteness in the CHART, not a footnote.
Prefer (a): the data exists.

## 2. £4,489/household fails the sniff test
Real incumbent opex per household is a few hundred pounds; £4,489 smells like
a whale-distorted mixed-book average (I&C in a "per household" figure).
Root-cause the basis. The chart must compare like-for-like: benchmark
LOWER-QUARTILE INCUMBENT COST PER SEGMENT vs TRUE cost PER SEGMENT, or an
honestly-weighted book total — never a blended per-household over a book
containing I&C. Label the basis on the chart (passport rule).

## 3. Same-page inconsistency: 11 vs 13 accounts
Pulse strip says "11 accounts as of 2025"; the chart says "across 13
accounts". One page, two book sizes. Fix the numbers AND extend the
consistency gate: all figures rendered on a single page must reconcile or the
gate fails — add this as an invariant, not a one-off correction (R10).

## DoD
Chart re-rendered with honest basis + populated or explicitly-floored TRUE
side; per-segment or clearly-labelled basis; page-internal consistency
invariant live and this page passing it; pixel-verified; one digest line. The
per-year historical series remains registered backlog (fine) — but the
CURRENT chart must be defensible in an expert's first sixty seconds.
