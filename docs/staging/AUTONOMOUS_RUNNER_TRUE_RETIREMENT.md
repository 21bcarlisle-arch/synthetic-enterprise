[PROJECT] AUTONOMOUS_RUNNER_STILL_RUNNING.md -- steer. Your finding is correct and your restraint (no blind kill, no S1 collision) was exactly right.

CONFIRMED: the 07-07 "retired" instruction was wrong -- it assumed a console kill was durable; start_worker.sh respawns on any stack restart, so the daemon never actually stopped, only the alerting about it did. That is worse than either state (hidden + still spawning + still burning budget). My error, correcting now.

DO, in order:
1. COMMENT AUTONOMOUS-RUNNER OUT OF start_worker.sh -- durable fix, your own recommendation, approved. This is the part you CAN safely do without an ambiguous kill (editing the launcher script, not guessing which live tmux session is which).
2. IDENTIFY every claude -p process this spawner owns (pstree/ps parent-child from the autonomous-runner pid, or grep the spawner's own logging for session IDs) BEFORE any kill -- write the list to the gate file so Rich kills the right ones.
3. Rich will console-kill the identified autonomous-runner process(es) directly -- do not attempt this from within a session that may itself be one of its children (you correctly flagged this risk already).
4. AFTER Rich confirms the kill: verify via ps/pstree that no claude -p process remains parented to the old spawner, THEN restore normal health-check alerting for autonomous-runner as "retired" (true retirement this time, not suppressed-while-hidden).
5. Fold into MAINTENANCE.md: "retiring" a daemon = edit its launcher script, not just kill the process -- otherwise the stack restart resurrects it. Add this as a standing check.

ON S1: correct call not to start a second track record build. Once the mid-building session's Phase RX lands (verify via git, not the tree), pick up wherever it leaves off -- don't duplicate.

Rich -- your action needed: (1) look at the identified-process list CC writes to the gate file, (2) console-kill those specific autonomous-runner processes, (3) confirm back so alerting can be safely restored.
