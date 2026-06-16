# Latest Status (mobile snapshot)

This file is served by `/ui/status` on the file API for quick mobile checks.
For full detail see `STATUS.md` at the repo root.

**Share with Claude.ai**: paste this URL into a claude.ai chat and Claude
will fetch the live content directly — no copy/paste needed, always
up to date with the latest push to `main`:
https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md

Last updated: 2026-06-16T13:06:00Z

**NTFY spam fixed (2026-06-16)**: Root bug: `_autoloop_waiting_notified` was
reset to `False` before the cap check on every idle cycle, so the "autoloop
cap reached" NTFY fired every ~5 min while idle (not once per cap window).
Fixed: flag only resets in the success path (just before sending the nudge).
Watchdog restarted on fixed code. 333 tests passing.

**GitHub Pages confirmed correct (2026-06-16)**: Pages at
https://21bcarlisle-arch.github.io/synthetic-enterprise/reports/ANNUAL_REPORT.md
is serving Phase 6b+7a figures (3.2%, £3,027) — Pages build at 09:47 UTC
picked up commit 125b0c4 correctly. Prior complaint was likely a cached view.

**Phase 6b+7a validated — first clean full run complete (2026-06-16)**:
Full 2016-2025 run (PID 106909) completed with working committee calls.
Root cause of all previous failures: `think:false` for qwen3:14b must be
at the request **top level** in `/api/chat` calls — inside `options{}` it
is silently ignored. Fix: `f190a9a`.

**Validated financial figures (Phase 6b+7a baseline)**:
| Metric | Value |
|--------|-------|
| Revenue | £93,868 |
| Gross margin | £4,174 |
| Capital cost | £1,147 (27.5% of gross) |
| Net margin | £3,027 (**3.2%** of revenue, within 2-5% benchmark ✓) |
| Treasury start → end | £29,846 → £32,873 |
| Committee interventions | 148 (vs 1 in buggy run) |
| 2021 crisis net margin | £-343 (4 committee wake-ups) |
| 2022 crisis net margin | £+238 (21 committee wake-ups) |
| Ledger events | 2,121,727 (P&L agrees ✓) |

**Churn events (deterministic, unchanged from Phase 6b)**:
- 2020-06: C3 | 2021-12: C1, C5 | 2022-03: C2 | 2024-03: C6 | 2024-09: C4
- HH customers C7/C8/C9 survived full 2016-2025 window

**Phase 7a complete — The Ledger (Gap #2 MVP, 2026-06-16)**:
Hollow gap #2 (no ledger) is now closed at MVP level. P&L is derivable as
the sum of transactions, not just a formula. New `saas/ledger.py`:
- `build_ledger(all_records, bills)` — derives chronological transaction log
  from existing simulation output (pure, no simulation changes)
- Three event types: `settlement_event` (wholesale cost, cash out per HH
  period), `capital_charge_event` (VaR charge, cash out per HH period),
  `billing_event` (revenue collected per customer-month, cash in)
- `derive_pnl(events)` — pure aggregation; verification section in report
  confirms ledger net matches simulation direct figure
- `docs/reports/ledger_latest.json` written alongside `run_output_latest.json`
  at end of every fresh full run (Phase 7a 4-hour gate passed, no redirect)

332 tests passing, lint clean.
Report: https://21bcarlisle-arch.github.io/synthetic-enterprise/reports/ANNUAL_REPORT.md

**Previous full runs failed (PIDs 96308, 101492)**:
- PID 96308: 147/148 committee calls failed (Ollama GPU-starved). Killed.
- PID 101492: All calls failed silently (think:false bug). Killed 2026-06-16.

**Phase 6b complete — event-driven customer lifecycle MVP (2026-06-16)**:
Gap #1 from the "five hollow gaps" (static customer roster since 2016) is
now closed at MVP level. At each annual renewal point, each billing account
rolls a deterministic churn/retain decision against
`effective_retention_probability` from the existing churn + home-move
win-rate models. If churned, the account stops generating settlement records
from that date forward — the portfolio genuinely shrinks.

Key design:
- `simulation/customer_events.py` — `roll_lifecycle_event()`: seeded by
  `random.Random(f"{billing_account}_{term_start}")` → deterministic per run
- Gas legs (C1g-C4g) share the billing-account decision with their electricity
  leg — churn of C1 also stops C1g automatically
- Point-in-Time safe: churn probability computed on records accumulated up
  to (not including) the renewal date
- New "Customer Lifecycle Events" section in ANNUAL_REPORT.md — replaces
  "Not available" for REPORTING_BACKLOG item 7

Churn pattern from degraded run (committee-independent, structurally valid):
- 46 renewal rolls, 6 churns
- 2020-06: C3 (unlucky roll)
- 2021-12: C1+C5 (energy crisis — bill shocks raised churn probability)
- 2022-03: C2 (crisis aftermath)
- 2024-03: C6, 2024-09: C4 (late attrition)
- C7/C8/C9 (HH customers) — all survived full window

332 tests passing, lint clean. Key commits: db56e35 (Phase 6b), ded6d11
(Phase 7a), fd44c70 (NTFY cleanup), 4175b6f (run-complete NTFY digest).

**Three simulation speed improvements committed (2026-06-16)**:
1. `think:False` + `num_predict:512` on risk committee Ollama calls —
   eliminates qwen3's verbose reasoning trace (~60s → ~15s per call)
2. `SIM_FAST_MODE=1` / `--fast` CLI flag — deterministic mock committee,
   no LLM calls; a 99-call full run goes from hours to minutes
3. `--end-year YYYY` — truncates the simulation window for iteration

Combined: `--fast --end-year 2020` gives a ~1 minute smoke-test loop.
`make run-fast` added as a shorthand target.

**Annual report republished with Phase A forward-curve figures (2026-06-16)**:
Pages: https://21bcarlisle-arch.github.io/synthetic-enterprise/reports/ANNUAL_REPORT.md
Gist: https://gist.github.com/21bcarlisle-arch/84943fc547781e6389e0561691ee5b4b

**Phase A forward-curve fix (daily-mean sigma) — re-run complete
(2026-06-16)**: `sim/forward_curve.py`'s volatility premium now uses
`pstdev(daily mean SSP)` instead of `pstdev(half-hourly SSP)` — fixing a
systematic ~4.3x inflation of the volatility term that was causing 40-290%
overpriced forwards (2016-2024 pervasive, not crisis-specific).

| Metric | Phase 6a baseline | +naked_kwh fix | +fwd curve Phase A |
|--------|------------------|----------------|-------------------|
| Revenue | £188,190 | £171,787 | £132,449 |
| Gross margin | £27,525 | £11,230 | £5,912 |
| Capital cost | £3,847 | £3,899 | £1,463 |
| Net margin | £23,679 | £7,331 | £4,450 |
| Net/revenue | 12.6% | 4.3% | **3.4%** |
| Naked counterfactual | £51,161 | £34,758 | £6,662 |

Key observations:
- Net margin 3.4% of revenue — inside the 2-5% industry benchmark ✓
- Capital cost dropped to £1,463 because VaR-based capital charge scales
  with forward price × naked position — more realistic forwards produce
  more realistic capital charges ✓
- SURVIVED full window, treasury £29,846 → £34,296

**Phase B (risk_factor recalibration 1.2→~0.25) on hold**: Phase A alone
brings net margin to 3.4%, within benchmark. Phase B would further reduce
revenue/gross and could push net margin below 2%.

**Phase 6a complete — HH smart meter customers (2026-06-15)**: three
half-hourly residential customers (C7/London, C8/Manchester, C9/Glasgow).
Phase 5c mandate-hedged baseline: net margin £23,678.55, treasury
£29,846 → £53,524, 168 committee wake-ups.

**Five hollow gaps status (as of 2026-06-16)**:
1. ~~No customer events firing~~ — **CLOSED by Phase 6b**: accounts can
   churn at renewal; portfolio can shrink. Replacement onboarding deferred.
2. ~~No ledger~~ — **CLOSED by Phase 7a**: transaction log built, P&L
   derivable from events, ledger_latest.json persisted on each full run.
3. SIM/company barrier structural not functional.
4. HH data path — **CLOSED by Phase 6a**: C7-C9 on real HH consumption.
5. Reporting — **CLOSED by Phase 5a/5b**: ANNUAL_REPORT.md, full pipeline.

**NTFY cleanup (2026-06-16)**: removed two per-cycle notifications that were
firing without needing Rich's attention:
- "usage-pause window has ended — autoloop resuming" (fired on every soft-pause
  expiry; not actionable)
- Verbose 7-line startup message → shortened to one sentence

332 tests passing, lint clean.
