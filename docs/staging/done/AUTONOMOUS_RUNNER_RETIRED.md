[PROJECT] autonomous-runner DELIBERATELY STOPPED by Rich at the console (2026-07-07, ~15:00 BST). Not an outage -- do not restart it, do not alarm on it.

RATIONALE: its background spawns ran stale pre-flag code since Jul 5 (pid 4223), hitting the write-block on ~10 consecutive phases (RA-RR "node gated behind unapprovable prompt" pattern) -- burning budget designing work they could not save -- and it was the second writer in both tree-race incidents (RM mid-edit sweep, RG duplicate pipeline run). With weekly burn already hot (39% by Tuesday), removing it is both the waste fix and the throttle.

EFFECT: the interactive claude session (watchdog-managed, flagged) is now the SINGLE writer. Staging triage, phases, and auto-resume all continue through it unchanged.

DO: (1) mark autonomous-runner as intentionally-stopped in the System tab's agent-health data (status "retired (director decision)" or similar -- not red/down) and suppress any missing-daemon alerting for it; (2) fold the restart question into the next weekly re-rank: it returns ONLY with the single-writer tree lock proven and the flagged launch config, if idle-time coverage is actually missed in practice.
