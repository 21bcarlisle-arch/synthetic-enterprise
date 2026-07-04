[PROJECT] Watchdog must read the EXIT REASON before restarting -- stop blind restart loops and NTFY spam

OBSERVED (04:00-05:20 this morning): CC sessions dying 2-3 minutes after launch, repeatedly. Watchdog restarts blindly, hits 3/hour cap, pauses 60 min, repeats. Rich received a dozen+ identical NTFYs. Background auto-process unaffected (commits every 10 min throughout). Last real work: Phase PX 03:54.

LIKELY CAUSE: usage/rate limit reached (clean exits immediately after first API call). But the watchdog cannot tell -- and that is the defect. It treats every exit identically: restart, cap, pause, spam.

FIX THE WATCHDOG:
1. CAPTURE EXIT REASON: before restarting, parse the tail of the CC session output (tmux capture-pane or session log). Classify: (a) usage/rate limit, (b) genuine crash/error, (c) clean task completion, (d) unknown.
2. ACT ON THE REASON:
   - Usage limit -> do NOT burn restart attempts. Parse the reset time if present in the message; sleep until then (or exponential backoff starting 30 min if no reset time). ONE NTFY: "Usage limit hit. Sleeping until ~HH:MM. Work paused, will auto-resume." Then silence until resume or state change.
   - Genuine crash -> restart (current behaviour), but include the actual error text in the NTFY so diagnosis is possible from the phone.
   - Clean completion -> restart normally, no alert needed.
3. DEDUPE NTFYs: never send the same status twice in a row. A state machine: alert on TRANSITIONS (working->limited, limited->resumed, working->crashed), not on every cycle. A dozen identical "session ended -- restarting" messages carry zero information and bury real alerts.
4. LOG each exit reason + timestamp to a watchdog log file so patterns are auditable later.

Then confirm via a single NTFY what the actual exit reason was this morning (from the captured output/log) -- so Rich knows definitively whether this was usage limits or something else.

SEPARATELY -- instruction fidelity flag: Phase PX (Correlated Synthetic Market Generator) directly contradicts the staged instruction PU_ADAPTER_AND_CORRELATED_ENDGAME.md, which said queue the correlated generator in the backlog and "Do NOT start it now." Explain in the next session report why it was started, and hold further correlated-generator work until observability (PROJECT_STATE.txt external freshness) is confirmed done -- that instruction (STATE_FILE_COPY_LATEST_MECHANISM.md) remains the top priority.
