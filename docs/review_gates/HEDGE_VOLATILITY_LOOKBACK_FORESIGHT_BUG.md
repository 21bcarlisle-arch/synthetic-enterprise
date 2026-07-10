# REVIEW GATE (Tier 1 — one-way door): hedge-decision volatility lookback uses future data

**Status:** DIRECTOR-AUTHORIZED IN-CONSOLE (Option A/B hybrid), 2026-07-10. Exact words: *"Hedge
gate: fix it, re-run, but HOLD republishing headline figures until I review the re-derived
numbers. The naked-hedging finding must be re-derived and re-framed, not auto-published. Not a
one-way door once fixed — proceed."* Code fix applied (`simulation/run_phase2b.py::
_price_history_as_of()`, bounded to the two `decide_hedge_fraction()` call sites, per this gate's
own recommendation -- `company/trading/hedge_decision.py` untouched). Regression tests added,
epistemic PASS. `background/sim-runner` daemon PAUSED (reversible -- restart once the reviewed
figures are ready to go live) so it cannot complete a fixed-code run and get auto-published by the
routine batch pipeline before director review. An isolated verification run (output to a scratch
path, NOT `docs/reports/run_output_latest.json`) compared old-vs-new headline figures and the
hf=0.00 finding specifically. This gate stays open until the director reviews these results and
says go-live.

## Re-derivation results (2026-07-10, isolated run, one BEFORE snapshot vs one FIXED run)

**Headline P&L: barely moves.** total_net_gbp -0.02% (-£342.76), total_revenue_gbp +0.00%,
total_bad_debt_gbp +9.66% (+£323.61, small in absolute terms). The fix does not meaningfully
change the portfolio financials.

**Hedge fractions: small effect in about half the years, honestly re-examined.** First
comparison attempt was WRONG (a bug in my own comparison script checked non-existent `avg`/`min`/
`max` keys on the year dict, always silently defaulting to 0 -- caught before reporting, redone
correctly against the real per-customer `hedge_fractions[cid].avg_hf` structure). Real result,
population avg/min/max hedge fraction by year:

| Year | BEFORE | FIXED | Differs? |
|---|---|---|---|
| 2016 | 0.889/0.850/0.922 | 0.889/0.850/0.922 | no |
| 2017 | 0.895/0.850/0.943 | 0.891/0.850/0.943 | yes (~0.4pp) |
| 2018 | 0.895/0.850/0.931 | 0.893/0.850/0.922 | yes (~0.2-0.9pp) |
| 2019 | 0.835/0.000/0.962 | 0.835/0.000/0.962 | no |
| 2020 | 0.811/0.000/0.960 | 0.811/0.000/0.960 | no |
| 2021 | 0.844/0.000/0.970 | 0.846/0.000/0.970 | yes (~0.2pp) |
| 2022 | 0.863/0.000/0.974 | 0.865/0.000/0.974 | yes (~0.2pp) |
| 2023 | 0.839/0.000/0.961 | 0.839/0.000/0.961 | no |
| 2024 | 0.806/0.000/0.944 | 0.806/0.000/0.944 | no |
| 2025 | 0.880/0.850/0.894 | 0.880/0.850/0.894 | no |

**Genuinely surprising finding, the real headline here: the population is NOT running "naked"
in this codebase's current output.** The average hedge fraction sits at 0.80-0.90 throughout,
including the 2016-2020 "calm" years the original hf=0.00 flagship finding was about. The
"min: 0.000" entries every year 2019-2024 trace to exactly ONE customer, `C_IC3g` -- a
pass-through gas account, which is DESIGNED never to hedge (bills at spot by construction, per
Phase 56's own comment in run_phase2b.py: "Pass-through gas customers must not hedge -- they bill
at spot, so a forward hedge creates wrong-way risk"), not a behavioural naked-hedging choice.
Every other customer stays hedged in the 0.85-0.97 range in every year checked.

**Implication for the flagship finding:** the original "hf=0.00 during calm 2016-2020, right
before the 2021-22 crisis" result (Phase 1d/1e, an early-build finding) does not reproduce in
the current codebase's real output at all -- this run shows consistently HIGH hedging the whole
way through, calm years included. This is NOT something the volatility-lookback fix caused (the
BEFORE run, still on the buggy code, shows the exact same high-hedging pattern) -- it looks like
the flagship finding reflects an EARLIER architecture (before `evolve_hedge_fraction`'s Phase 22b
backward-looking evolution and the Phase 43b VaR-decision system existed), superseded by later
building, and the "hf=0.00" story was never re-verified against the current build. This needs
the director's own re-framing decision, per his own instruction -- flagging honestly rather than
guessing at a narrative.

**Recommendation:** do not republish the old "hf=0.00 naked hedging" framing at all pending
director review -- it appears to no longer describe this codebase's real behaviour. The
volatility-lookback fix itself is real, correct, and low-risk to land (headline P&L barely
moves) -- but the interesting story here is arguably not the bug fix, it's that the original
flagship finding may be stale/superseded and needs the director's own decision on how (or
whether) to re-state it.

**Original finding (2026-07-10)**, in response to a real director page comment on `/supplier/` (Trading &
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
