# M1 FRAME: "sim loop drains events not steps" + materiality gates/lazy valuation

**Status:** DISCOVER complete, FRAME (this doc). BUILD not started, deliberately.

## What the framing's abstract language actually maps to in real code

Investigated before writing any code (R4 diagnosis discipline: name the
nearest working analogue and state the diff before fixing). Two findings,
both load-bearing for scoping this correctly:

**1. The outer decision loop is already event-shaped — don't touch it.**
`simulation/run_phase2b.py:780-788` interleaves every customer's renewal/term
schedule into one flat, chronologically-sorted list (`all_terms`), then
iterates it once (`for term_start_str, cid, commodity, term in all_terms:`,
line 902). This is one iteration per real decision event (a term signing),
not nested customer×tick loops. It is already what "drains events not steps"
describes. A rewrite here would be pointless — it already works, and is
exactly what made the price-history migration (M1_PRICE_HISTORY_PIPELINE_
FINDING.md) safe to build on top of.

**2. The real step-based cost is one level deeper, in settlement generation
itself — and it's ground truth, not overhead.** Inside each term,
`simulation/hedged_settlement.py`'s `run_hedged_term()`, `run_deemed_term()`,
`run_flex_term()` each do `for period in range(1, 49):` for every day of the
term's duration, generating a genuine settlement record (revenue, wholesale
cost, margin, capital cost, hedge P&L) for every half-hour. This is real UK
settlement granularity (BSC settles per half-hour) — it is NOT wasted
compute in the way a naive "just skip some periods" read of "lazy
valuation" would suggest. Every one of these records is the actual data
every downstream consumer (billing, margin reporting, the whole
`per_customer_lifetime`/`by_billing_account` pipeline, this session's own
CT/VaR/forecast-cashflow work) is built from.

## Why this is not a same-day BUILD

Real runtime today: 468-484s (~8 min) for the full 2016-2025, ~19-customer
run (`docs/observability/sim-runner-log.md`, six recent runs sampled). Not
currently blocking anything — every phase-close this session that depended
on a fresh run got one within a normal work cycle. The framing's own
concern ("compute scales with events, not customers×ticks") is a genuine
FUTURE scaling risk, not a live problem: M3's per-run population draws (more
customers) and M4's full-history replay through the reveal engine are what
would actually make today's cost structure bite.

Given `hedged_settlement.py` produces the literal ground truth this entire
project's numbers are built from, and zero prior art exists for
"materiality"/"lazy valuation" anywhere in this codebase (confirmed by
direct grep — genuinely greenfield, not a rediscovery of partial existing
work), attempting a same-day rewrite here risks silently corrupting years
of historical data for a problem that isn't blocking today. This is
precisely the two-way-door filter's case: don't build against an
unresolved design question when nothing forces the decision now.

## What "materiality gates + lazy valuation" most plausibly means, once scoped

Not "skip generating some settlement records" (that would silently break
billing/margin, which need every real period). More plausibly: don't re-run
EXPENSIVE PER-PERIOD ANALYSIS that isn't decision-relevant at every tick --
e.g., churn-risk scoring, satisfaction tracking, or other company-side
diagnostics currently computed per-settlement-period when they only change
at renewal/event boundaries (many may already only fire at the right
boundaries, inheriting correctness from the outer loop's own event-shape --
this needs a real per-consumer audit, not assumed). The settlement record
itself (revenue/cost/margin per half-hour) stays fully materialized --
that's real data, not a cache to lazily populate.

## Recommendation

Defer the BUILD decision. Register this FRAME finding; do not move
`W1_reveal_over_time` to level 3 on the strength of a design doc alone (the
map's own rule: depth is earned, not claimed). Revisit when M3/M4 make the
current cost structure genuinely load-bearing, or if the director/advisor
judges the scaling risk worth pre-empting now. If/when built, the first
real step should be a narrow audit of which per-period company-side
computations (not settlement generation itself) are genuinely tick-bound
vs already event-bound, before touching any code.
