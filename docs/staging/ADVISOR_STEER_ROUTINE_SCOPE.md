# ADVISOR_STEER — Routine scope decision (Tier 2: tightening + conditional re-enable)

**Staged:** 2026-07-11 by advisor, relaying the director's decision from live
conversation (he has seen and approved this routing). The pause was correct —
exactly what the kill-switch was for.

## Decision on trig_01Xj4Xkj7sD5Fmv7nZVzW41c
Reconfigure BEFORE any re-enable:
- allowed_tools = read/fetch only. No Bash, Write, Edit, MultiEdit, tmux,
  REPL, SendUserFile.
- ALL MCP connectors stripped. Gmail/Spotify were never intended; remove
  them, and never wire account-level connectors into any routine.
- Output channel = open a GitHub issue only. No pushes, no PRs to start.
- Schedule unchanged; pause switch retained.

## Standing rule (add to CLAUDE.md, routines section)
Every routine creation must set an explicit MINIMAL allowed_tools and an
EMPTY connector list, then VERIFY the created config against the binding
constraint before first run — R1 applies to routine configs (re-fetch the
trigger config and diff it against the constraint; the creation response is
not evidence).

## Re-enable condition
Only after posting the verified (re-fetched) config in a digest line. If
read-only cannot be guaranteed on this platform, leave the routine dead —
the pilot is not worth the surface. The 03:01 run either happens read-only
and verified, or does not happen.
