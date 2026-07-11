> **STATUS (2026-07-11):** Queued, non-interrupting per its own instruction.
> Take at next natural boundary -- after the current Stop-hook-fix +
> security-profile + M2-wiring work this turn.

# ADVISOR_STEER — auto-update line, final kill (Tier 2, tiny)

**Staged:** 2026-07-11 by advisor. Non-interrupting; take at next boundary.

The "Auto-update failed: no write permission to npm prefix" line STILL shows
in the live session despite the env mechanism being verified (tmux -g global,
watchdog per-launch, autonomous_runner belt-and-braces). Remaining hypothesis
to test FIRST: current Claude Code versions control auto-update via
settings.json (`"autoUpdates": false`), not the legacy DISABLE_AUTOUPDATER
env var — we may be setting a switch the binary no longer reads. Check the
installed version's actual config mechanism (claude-code-guide/docs), apply
the supported setting, and close with proof per the pixel rule's spirit:
capture-pane grep showing the line ABSENT after the next session restart.
If the settings route is also already correct, R4 differential-diagnose
(sticky UI line? npm prefix perms making the binary emit regardless?) — but
no more env-var patches; find the mechanism the binary actually honours.
One digest line with the evidence.
