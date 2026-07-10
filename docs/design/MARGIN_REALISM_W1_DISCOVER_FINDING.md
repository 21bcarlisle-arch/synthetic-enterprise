# W1 reveal-over-time (Maturity Map DISCOVER stage) finding: two inconsistent point-in-time safety patterns

**Status:** DISCOVER-stage finding, research only. NO CODE CHANGED -- this atom touches the
epistemic law (SIM/company boundary, point-in-time blindfold), CLAUDE.md Tier 1 category (a).
`loop_stage: discover` means background research/design is self-startable; implementation
requires the hard Tier 1 REVIEW_GATE (explicit director approval, no timeout) first. Filed
from the fourth dial-weighted maturity-map self-refill draw, 2026-07-10.

## What was checked

The atom's own name -- "point-in-time blindfold at the source, not just company/ code" --
implies today's enforcement is NOT fully "at the source". Audited how price-history data
actually flows into decision-making functions, focused on the exact area the recent
`HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG.md` review gate already touched, to see whether
that fix closed an isolated instance or revealed a wider pattern.

## The finding: two structurally different safety patterns coexist

**Pattern 1 -- safe "at the source"** (`sim/risk_engine.py::calculate_sigma_recent()`):
takes an explicit `reference_date` parameter and filters `system_price_records` internally
to strictly-before that date, with the filtering logic living inside the function itself.
This function is safe regardless of what any caller passes in, including a caller that
(by mistake or a future refactor) hands it the whole run's history.

**Pattern 2 -- caller-trusted** (`company/trading/hedge_decision.py::estimate_price_volatility()`):
takes only a bare `price_records` list, no date parameter at all, and simply uses "the last
`VOL_LOOKBACK_DAYS`" positionally from the END of whatever list it receives. This is exactly
the shape of function that produced the real, already-fixed hedge-volatility bug: a caller
in `simulation/run_phase2b.py` was passing the FULL run's `elec_records` (all years), so
every decision across the whole 2016-2025 run shared one volatility estimate drawn from
near the run's end. The fix (`_price_history_as_of()`) was applied as an external wrapper
**at the one known call site**, truncating the array before it reaches
`estimate_price_volatility()` -- the function itself was not changed and remains unsafe on
its own terms. Confirmed via grep: there is currently only ONE production call path into
`estimate_price_volatility()` (via `decide_hedge_fraction()`), and it IS patched -- so there
is no live second violation today. But nothing in the function's own signature or body
would catch a future call site, or a refactor of the existing one, making the same mistake
again. This is exactly the "not just company/ code [discipline]" gap the atom names: safety
here depends on every future caller remembering a convention, not on the function itself.

## Why this matters beyond one function

The review gate that fixed the original bug explicitly scoped itself narrowly ("bounding
the blast radius to this one call site... not touching estimate_price_volatility itself")
-- a deliberate, correct, minimal-risk choice at the time (Tier 1 caution). But it means the
underlying anti-pattern (a caller-trusted function with no internal date awareness) still
exists in the codebase as a template other code could unknowingly copy. The epistemic
verifier (`tools/epistemic_verifier.py`) was separately extended this week to catch
data-flow/timing violations, which is the right complementary control (catches misuse after
the fact) -- but a structurally self-contained function (pattern 1) prevents the mistake
from being possible in the first place, which is the stronger property "at the source"
actually means.

## What "reveal-over-time... at the source" would concretely require (design sketch, not built)

Rather than continuing to patch individual caller sites as each is discovered (the same
mechanism-repair discipline as R3 -- eliminate/redesign a recurring failure class, don't
patch the same shape of bug twice), the atom's own target (level 3) most plausibly means:
a single, structural point-in-time data-access abstraction (a "snapshot" or "as-of view"
object, constructed once per decision with a bound simulated date, that every price/
weather/generation/demand read goes through) rather than N independently-audited functions
each re-implementing their own filtering correctly or not. This is a real, Tier-1-gated
BUILD decision (touches the SIM/company boundary directly) -- named here as this DISCOVER
task's concrete recommendation, not implemented.

## External research dispatched

A discovery-agent task is checking real-world precedent: how quantitative finance/
backtesting systems name and enforce this pattern (point-in-time databases, "as-of" query
abstractions), whether "self-contained as-of function" vs "caller-trusted" is a recognised
good-practice-vs-anti-pattern distinction with citable sources, and any documented real
incidents from inconsistent look-ahead-bias protection. Findings will land in
`docs/market_research/ASSUMPTIONS.md` under "W1 reveal-over-time (Maturity Map DISCOVER)".

## Next step (not this turn, and Tier 1 gated)

Once the external research lands, this should become a named, evidence-cited FRAME-stage
proposal (lane charter update per MATURITY_MAP.md Section 2) for the director's Tier 1
review -- specifically proposing the structural snapshot/as-of-view abstraction sketched
above, scoped to which data sources it would cover first. No implementation before that
gate opens and closes.
