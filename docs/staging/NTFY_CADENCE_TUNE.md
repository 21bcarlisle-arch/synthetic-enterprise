# NTFY_CADENCE_TUNE — director visibility, bounded silence (small standing rule)

**Staged:** 2026-07-08 by advisor, director-requested. **Tier:** 2, tiny change.

The director wants more visibility into progress via NTFY. Do NOT switch to
periodic heartbeats — R5 (transition-only, no noise) stands. Instead, add one
rule and enrich the existing transitions:

1. **Bounded silence:** while actively working a phase, if 60 minutes pass with
   no NTFY, send ONE line: current phase, current step, % feel, next expected
   transition. Clock resets on any NTFY. When idle/waiting with nothing queued,
   stay silent (idle is not progress worth reporting) — but a state CHANGE into
   blocked/waiting-on-director is itself a transition: notify immediately with
   what is blocking and what would unblock.
2. **Transition set (confirm all fire):** phase start (with decomposition/plan
   in one line), each numbered scope item done, phase close, anything
   consumer-verify-failed, anything blocked, any self-caught error worth a
   retro note.
3. Persist this in the harness docs (CLAUDE.md ops section or equivalent) so it
   survives session /clear and restarts. One NTFY to confirm adoption.

Director can still pull status on demand via the two-way channel at any time;
this rule is about push visibility between pulls.
