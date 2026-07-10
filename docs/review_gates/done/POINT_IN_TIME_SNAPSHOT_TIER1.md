# REVIEW GATE (Tier 1 — one-way door): structural point-in-time data-access layer — CLOSED

**CLOSED 2026-07-10 (director NTFY reply, correlated with `docs/staging/done/
from_rich_20260710_165627.md`):** *"Approved as recommended: register, don't build now.
Placement correction: this is Epoch-2 core — the company-side face of the reveal-over-time
spine, sibling to D2 three-clocks, one architecture not two. The advisor's epoch framing will
sequence it. Until then, keep patching call-sites only if live bugs surface. Good gate — right
precedents, right restraint. Close it and continue the queue."*

Option B confirmed (register, sequence later — no code built). Placement correction applied:
`W1_reveal_over_time` and `D2_three_clocks` are reframed as the SAME architecture's two faces —
`W1` is the company-side/pricing-decision face, `D2` is the billing-side face, both riding the
same underlying "reveal-over-time" spine, not two independent capabilities. Both atoms' evidence
updated to cross-reference each other explicitly on this basis. Sequencing left to the advisor's
epoch framing, not decided here. Standing interim instruction: keep patching individual call
sites only if a live bug actually surfaces (matching the existing hedge-volatility precedent) —
no proactive/preventive build before the epoch sequencing names its turn.

**Status (historical):** OPEN — awaiting director decision. Filed 2026-07-10, from the
W1_reveal_over_time maturity-map atom's DISCOVER-stage findings (internal code review +
`docs/market_research/ASSUMPTIONS.md` "W1 Reveal-Over-Time" external research, both already
landed, both research/design only — no code touched to reach this point).

## Why this is Tier 1

Touches the epistemic law (SIM/company boundary, point-in-time blindfold) — CLAUDE.md category
(a). Hard gate, explicit director approval required, no timeout, never proceed on silence.

## Decision needed

Should the codebase build a single, structural point-in-time data-access abstraction (a
"snapshot" or "as-of view" object, constructed once per decision with a bound simulated date,
that every price/weather/generation/demand read goes through) — replacing the current pattern of
patching individual caller sites one at a time as each is discovered?

## Evidence (both findings already landed, no new code)

**Internal (`docs/design/MARGIN_REALISM_W1_DISCOVER_FINDING.md`):** two structurally different
patterns coexist today. `sim/risk_engine.py::calculate_sigma_recent()` is self-contained — it
takes an explicit `reference_date` and filters internally, safe regardless of what any caller
passes in. `company/trading/hedge_decision.py::estimate_price_volatility()` has no date
parameter at all — it trusts the caller to have already truncated the data, and was ONLY made
safe after a real bug (`docs/review_gates/done/HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG.md`) by
bolting an external wrapper (`_price_history_as_of()`) onto its one known call site. That review
gate deliberately scoped its own fix narrowly ("bounding the blast radius to this one call
site... not touching `estimate_price_volatility` itself") — a correct, minimal-risk choice at
the time, but it leaves the underlying anti-pattern in the codebase as a template a future call
site or refactor could copy without anyone noticing, since nothing in the function's own
signature enforces safety. No live second violation was found this session (confirmed via grep:
exactly one production call path exists, and it is patched) — this is a preventive proposal, not
a report of a live bug.

**External (`docs/market_research/ASSUMPTIONS.md`, "W1 Reveal-Over-Time — Point-in-Time Data
Access Patterns in Quant Finance"):** this is a well-studied, named problem in quantitative
finance, with real, citable precedent:
- "Look-ahead bias" is the standard term (confirmed verbatim in QuantConnect/LEAN's own glossary).
- QuantConnect and Zipline — the two major open-source backtesting engines — both architecturally
  prevent it via event-driven/streaming data delivery. QuantConnect names its own enforcement
  boundary the **"Time Frontier"**.
- The MORE mature pattern than a simple per-function as-of filter is a shared, uniformly-enforced
  access layer every caller must route through — named a **"point-in-time join"** (Feast, the
  open-source ML feature store) and, independently, **"bitemporal history"** (Martin Fowler).
  Marcos Lopez de Prado's *Advances in Financial Machine Learning* (Wiley, 2018) implements this
  as a reusable `PurgedKFoldCV` class with "purging" and "embargo" concepts — a named, citable
  engineering pattern for exactly this problem, not an invented analogy.
- Real, quantified cost of getting this wrong exists for the sibling bias (survivorship bias):
  Elton, Gruber & Blake (1996) estimated ~0.9%/year of overstated mutual-fund returns from
  non-point-in-time data assembly.
- Honest negative finding, not glossed over: no case study was found naming look-ahead bias
  specifically as caused by *inconsistent per-function enforcement within one codebase* (the
  exact shape of this project's own gap) — the closest documented analogue (Knight Capital's 2012
  $440m loss from stale code on one of eight servers) is flagged explicitly as a different bug
  class, not a look-ahead-bias precedent, and should not be cited as if it were.

`tools/market_data_port.py::MarketDataPort` (found during the separate W4_1_typed_adapters audit
refresh) is already the codebase's most mature existing example of the target pattern — a typed
`Protocol` where every method takes an explicit `as_of` date and filters internally. It would be
the natural reference implementation, not a design from scratch.

## Options

**A. Build the structural snapshot object now.** Scope: one new class/module (e.g.
`sim/point_in_time_view.py`) constructed with a bound `as_of` date, exposing the same
observables `company/interfaces/sim_interface.py` already names, backed initially by
`MarketDataPort`-style adapters for price data (the one area with a confirmed real precedent —
the hedge-volatility bug). Weather/generation/demand data access left out of the first pass
unless a similar caller-trusted gap is found there too (not yet audited). Estimated smallest
viable step: 1-2 files, a class + a handful of methods, existing call sites migrated one at a
time (each independently testable/revertable — a two-way door once the object itself exists).

**B. Register as scoped future work, do not build now.** No live violation exists today (the one
known caller-trusted function has its one call site already patched). The value is preventive,
not corrective. Given the current MARGIN_REALISM/maturity-map workload already in flight, this
may be lower priority than closing Steps 3-6 of that programme or the D2_three_clocks
reconciliation the E2/B1 root-cause trace surfaced.

**C. Do nothing beyond documenting the pattern.** The epistemic verifier's timing-extension
(added this week, from the hedge-volatility incident) already provides a detective control;
accept that as sufficient for now and revisit only if a second live violation is found.

## Recommendation

Option B. The evidence is real and well-sourced, and the preventive value is genuine, but there
is no live bug driving urgency (confirmed: zero live violations, the one known gap already
patched), and the current active workload (MARGIN_REALISM Steps 3-6, the D2_three_clocks
reconciliation) is director-sequenced ahead of new preventive infrastructure work. Recommend
registering this gate's decision as "approved in principle, sequence after the current
MARGIN_REALISM/maturity-map work" rather than building immediately — but this is the director's
call to make, not a default to proceed on.

## What happens on approval

If Option A is chosen: this becomes a named FRAME→BUILD transition for the W1_reveal_over_time
atom (level 0→1 for FRAME, further for BUILD), side-tagged WALL per the existing side-tagging
convention, sequenced per the director's placement decision. If Option B: this gate stays open
(re-pinged per the standing Tier 1 daily-reping rule) until the director names when to revisit,
or closes it outright as C.
