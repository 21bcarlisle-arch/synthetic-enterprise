# NEXT_PHASE.md -- S1 design note staged

**Status (2026-07-07):** Phase RW closed PRIORITIES.md's entire P2 queue
(SAAS_COVERAGE_MAP.md, the last of five items). See PROJECT_OVERVIEW.md Section 4 Phase RW,
CLAUDE.md "Current state".

**Front of queue next:** S1 (proof-first: shadow-live track record, public scorecard from day
one, misses included) -- adopted into PRIORITIES.md's ranked queue per the pre-agreed advisor
direction (docs/staging/done/STRATEGIC_HORIZON_DECISIONS.md) now that its stated condition
("P2 completes first") is met. S1 needed its own concrete design note before implementation
(a visible, one-way-door-adjacent public surface, same caution already applied to the
frozen-policy-baseline tab) -- that note is now written: docs/staging/S1_SHADOW_LIVE_TRACK_RECORD_DESIGN.md.

**Headline finding in the design note:** the existing daily shadow-decision log
(site/state/live_decisions_log.jsonl, built Phase QE/PV) is currently degenerate -- four real
days of entries (2026-07-04 through 2026-07-07) are byte-identical except the run timestamp,
because both the market-data as-of date and the renewal-day countdown are pinned to the sim's
frozen historical cache end (2025-06-07) with no wall-clock advance. A track record that never
changes can never be scored. Recommended fix (Option B in the design note): decouple wall-clock
elapsed time (renewal countdowns, future grading) from market-price freshness (genuinely bounded
by real Elexon data availability, honestly labelled with its age) -- unlocks a real, gradeable
track record immediately, independent of whether newer real settlement data can be fetched
(Option A, a fast-follow contingent on an open question this session could not verify: network
access was unavailable in this run).

Tier 3, 4h opt-out per the design note -- proceeding with Option B (wall-clock decoupling +
scorecard scaffold + retention-EV field added to the daily decision log) unless redirected.
