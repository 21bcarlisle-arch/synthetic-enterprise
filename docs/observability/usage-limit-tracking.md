# Usage Limit Tracking

Empirical tracking to infer the actual token values behind Claude Pro's
4-hour (rolling "5-hour limit" in the UI) and weekly usage limits, by
combining Rich's reported usage % (from `/status` in Claude Code, or the
claude.ai usage page) with this session's token consumption (from `/cost`).

Anthropic doesn't publish exact token thresholds for these windows, and
`session_watchdog.py`'s usage-limit detection (`USAGE_LIMIT_PATTERN`) is
reactive — it only catches Claude Code's own on-screen message when a limit
is *already* hit, with unconfirmed wording. This log is a side-channel to
build an empirical estimate over time, which could eventually inform a
proactive warning before the limit is hit.

## How to log an entry

Append a row to the relevant table below. Don't edit past rows except to
fix errors.

- **reported_pct**: the usage percentage Rich reads from `/status` (Claude
  Code) or the claude.ai usage settings page, for the relevant window
  (4-hour / weekly).
- **reset_at**: the reset time shown alongside that percentage (convert to
  UTC if shown in local time).
- **session_tokens_since_reset**: run `/cost` in Claude Code and report the
  total tokens for the current session (input + output + cache creation —
  see `token-log.md` for the breakdown convention). Only meaningful if this
  session is the *only* consumer of the window (no other concurrent Claude
  Code/claude.ai usage on the account in that window) — note in "notes" if
  that assumption doesn't hold.
- **implied_limit_tokens**: `session_tokens_since_reset / (reported_pct / 100)`
  — a rough estimate, only as good as the assumption above. Leave blank if
  the assumption clearly doesn't hold; record the raw numbers anyway so a
  later pass can still use them.

## 4-Hour Window

| logged_at (UTC) | reported_pct | reset_at | session_tokens_since_reset | implied_limit_tokens | notes |
|---|---|---|---|---|---|
| 2026-06-13T16:25:00Z | 54% | 2026-06-13T17:39:00Z | 25474400 | 47175000 | from /cost: haiku 162.2k (29.2k in + 4.0k out + 101.8k cache read + 27.2k cache write) + sonnet 25312200 (4.5k in + 171.2k out + 24.4m cache read + 736.5k cache write). Assumes this session is the sole consumer of the current 4h window. |
| 2026-06-13T19:53:00Z | 83% | 2026-06-13T21:39:00Z | | | reported_pct only (no /cost run this time) — this is a new 4h window (previous one reset at 17:39Z), so the prior implied_limit_tokens doesn't directly carry over. |

## Weekly Window

| logged_at (UTC) | reported_pct | reset_at | session_tokens_since_reset | implied_limit_tokens | notes |
|---|---|---|---|---|---|
| 2026-06-13T16:25:00Z | 12% | 2026-06-15T02:59:00Z | 25474400 | | same /cost total as the 4h row above, but the weekly window started before this session — other sessions likely contributed too, so this total is a lower bound only. implied_limit left blank. |
| 2026-06-13T19:53:00Z | 15% | 2026-06-15T02:59:00Z | | | reported_pct only. 12%->15% over ~3.5h (16:25Z->19:53Z), consistent with the 4b-5 work + full portfolio re-run now running in the background. |
