[PROJECT] Flag EVERY session launcher -- the 19:44 write-blocked session proves a second spawn path (likely autonomous-runner) still launches without --dangerously-skip-permissions.

The blocked session's task (phases.json generator) was completed 14 min later by a flagged session -- system self-healed, but unflagged spawns waste budget designing work they cannot write.

DO: grep the whole repo/background for every claude launch string (watchdog is fixed; autonomous-runner and any scheduler/other spawn path are suspects). Add --dangerously-skip-permissions to ALL of them, per the closed Tier 1 gate (director-approved at console, recorded). Restart every affected daemon (R2: committed != running). Verify by spawning one background session and confirming it can write. Single NTFY with the list of launchers fixed.
