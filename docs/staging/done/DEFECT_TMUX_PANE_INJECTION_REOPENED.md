> **[CLOSED 2026-07-13, director-confirmed]** "Injection fix CONFIRMED -- no [Pasted text] accumulation since." R3 redesign held a >=30min clean window + director confirmation. Retro filed. H16 stability-gate now IMPLEMENTED in _safe_to_inject.

> **[PARKED in_progress 2026-07-13]** R3 REDESIGN SHIPPED + OBSERVING (NOT closed -- director confirmation required). Root cause found: single-snapshot spinner-format idleness guessing; replaced with a format-INDEPENDENT gate _safe_to_inject (byte-stability: the spinner elapsed-timer ticks every second so a processing pane is never static, whatever the format; + input-box-occupancy: never inject while a [Pasted text] chip is unconsumed, so accumulation is impossible). Live-verified _safe_to_inject=False on a busy pane; 4 flow tests reworked + 3 new; source PROVEN via the injection log (supervisor grant_turn). OBSERVATION: 0 injections in ~17min busy (was ~1/2min). UNBLOCKS-TO-CLOSE: >=30min window clean + director confirmation. Banned closed language until then.

# DEFECT_TMUX_PANE_INJECTION — REOPENED (R3 two-strike triggered)

**Priority:** P1 — director-repeated. Second occurrence after "defect closed."
**Staged by:** advisor (director-reported, 2026-07-13 ~20:50 UTC)

## Fact

Director is still seeing `[Pasted text #NNN]` accumulation in the claude pane AFTER the 19:56 UTC "FIXED at the source / defect closed" NTFY and the 0d83d12cf deploy.

## R3 applies — this is strike two

Strike one: the pattern-list fix (self-corrected). Strike two: the spinner-regex fix, live-verified, defect closed — and the symptom persists. Per R3, do not patch the idle-detection heuristic again. Eliminate the mechanism: pane-scrape-plus-regex idleness guessing has now failed twice in one day against a moving spinner format it does not control.

## Required

1. Read the LIVE injection log (docs/observability/injection-log.jsonl on disk — the committed copy is stale at 19:48) for all entries since 19:56 UTC. Identify source(s) of the post-fix injections. If the log shows nothing while the director sees pastes, the logging has a gap — close that first (R10: class fix).
2. Redesign injection gating so that a wrong idleness guess is IMPOSSIBLE to convert into pane input. Your own H16 byte-stability gate is one candidate; a design that does not read the pane at all is also acceptable. Choice is yours — the non-negotiable is that spinner/format changes in Claude Code can never again cause mid-turn injection.
3. The 4 send_keys_when_idle flow tests being "reworked" is not a reason to defer — that was the deferral rationale and the defect recurred the same day.
4. Do not NTFY "fixed" until verified against the R1 standard: sustained observation (≥30 min of busy-pane activity) with zero unauthorised injections, evidenced from the injection log, plus director confirmation. "Defect closed" language is banned for this defect until the director confirms.

## Report

Transition-only NTFY: (a) post-19:56 injection sources identified, (b) redesign shipped, (c) observation window result.
