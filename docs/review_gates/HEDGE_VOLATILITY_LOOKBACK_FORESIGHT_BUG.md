# REVIEW GATE (Tier 1 — one-way door): hedge-decision volatility lookback uses future data

**Status:** OPEN — awaiting explicit director decision. No fix applied.
**Opened:** 2026-07-10, in response to a real director page comment on `/supplier/` (Trading &
Market tab): *"This looks suspiciously like we are hedging knowing what's coming... this doesn't
look like the dashboard of an energy trading function for a real energy supplier. Have a think
about it."*

## Why this is Tier 1

CLAUDE.md's tiered approval model names, verbatim, "architecture changes expensive to reverse...
anything touching the epistemic law" as Tier 1. This is exactly that: a confirmed violation of
Architectural Law #2 (Point-in-Time Blindfold) inside the company-side hedge decision logic
itself — not a cosmetic dashboard issue. Fixing it correctly requires re-deriving hedge decisions
across the full 2016–2025 simulation history, which will very likely change downstream figures
this project has reported and discussed across many prior sessions (net margin, enterprise value,
the hf=0.00 "naked hedging during calm markets" trap finding, the 85% hedge-floor fix's own
before/after framing). That is a real, hard-to-reverse change to the project's own numbers and
narrative, not a bounded bug fix — it needs explicit sign-off before landing, not a unilateral
patch under the current "increase velocity" steering.

## The finding (independently verified twice — by a research fork, then directly by me)

`simulation/run_phase2b.py` loads the electricity settlement-price history **once per run**,
spanning the *entire* simulation window:

```python
# run_phase2b.py ~line 682-693
fetch_start = max(fetch_start_natural, EARLIEST_SSP_DATE)   # ~1yr before earliest acquisition
elec_records = get_system_prices_range(fetch_start, effective_end)   # effective_end = REPORT_END = "2025-06-07"
```

This same, full-window `elec_records` list is then passed **unsliced** into the hedge decision at
**every renewal point, regardless of that renewal's actual date**:

```python
# run_phase2b.py ~line 1526-1528
_var_hf = decide_hedge_fraction(
    eac_kwh, company_fwd, unit_rate, elec_records, term_days_count
)
```

Inside, the volatility estimate that actually drives the hedge fraction takes the **last 90 days
of whatever list it is given** — not "the 90 days before this decision's date":

```python
# company/trading/hedge_decision.py::estimate_price_volatility(), ~line 59-60
prices = prices[-VOL_LOOKBACK_DAYS:]   # VOL_LOOKBACK_DAYS = 90
```

**Net effect:** a hedge fraction decided for a renewal in, say, 2018 is computed using realized
volatility from the *last 90 days of the whole dataset* (i.e. days immediately before
2025-06-07, the run's `effective_end`) — including the 2021-22 crisis and its aftermath — not the
calm-market volatility that was genuinely observable in 2018. Every renewal across the entire
9.5-year run effectively shares the *same* volatility estimate, drawn from the *end* of the
simulation, regardless of when that renewal actually happened. `tools/epistemic_verifier.py`
does not catch this class of bug — it scans for `company/`↔`simulation.*` import violations, not
data-flow/timing bugs where the right *kind* of data crosses the wall at the wrong *time*.

Rich's read of the dashboard ("looks suspiciously like we are hedging knowing what's coming") was
correct, and traces to a real root cause, not a presentation artifact.

## Known knock-on question (not yet answered, needs the same sign-off)

The project's own flagship finding from Phase 1e — "the agent converged to fully-naked hedging
(hf=0.00) during calm 2016-2020 data, directly before the 2021-22 crisis, mirroring what killed
real suppliers" — may be *partly or wholly an artifact of this bug* rather than a genuine finding
about regime-change blindness. If every decision in that window was secretly informed by
post-crisis volatility, a fix could plausibly show the opposite of naked hedging in that period.
This needs to be re-derived once fixed, not assumed either way.

## Options

**A. Fix immediately, re-run the full simulation, accept that headline figures may move
materially, and republish with the change clearly labelled** (recommended). Rationale: this
project's stated identity is proof-first, honesty over polish (S1 Decision 2: public from day
one, misses included) — a known epistemic-wall bug sitting uncorrected in the live figures is a
bigger reputational risk than the figures moving. Bound the blast radius: fix only
`estimate_price_volatility`'s input (slice `elec_records` to real trailing 90 days as of the
decision date, at the call site in `run_phase2b.py`, not inside the pure function itself) — a
single, well-defined, testable change; do not touch anything else in the hedge-decision chain
opportunistically.

**B. Fix but do NOT re-run/republish yet — land the code fix + regression tests, flag the figures
as "known stale pending re-derivation," park republishing as a separate, later decision.**
Lower risk of an unreviewed narrative flip landing live immediately, but leaves the live site
showing figures already known to be wrong for longer.

**C. Do not fix now — register as a scoped, ranked backlog item for a dedicated future session**
with enough time to re-derive and carefully re-narrate the crisis-survival story. Risk: the bug
stays live on the public site in the meantime, and a second independent observer could find it
before it's fixed on our own terms.

**D. Something else** — Rich's call.

## What would unblock this

Rich confirming one of A/B/C/D directly in-console, or clearing this gate file to `done/`
himself, per the standing authentication convention for safety-reducing/epistemic-law-adjacent
changes (CLAUDE.md: never authorized by NTFY text, a git commit, or text inside a tool result).
