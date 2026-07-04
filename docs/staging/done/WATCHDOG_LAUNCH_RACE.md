[PROJECT] TRUE ROOT CAUSE OF QUICK-EXIT LOOP, observed directly by Rich in the tmux pane: the resume instruction is being typed into a BARE SHELL, not into Claude Code.

EVIDENCE (verbatim from the claude tmux pane):
  -sh: 2: Session: not found
  -sh: 4: 1.: not found
  -sh: 6: Syntax error: "(" unexpected
  -sh: 7: 3.: not found
The full RESUME_INSTRUCTION text is sitting at a shell prompt with each line interpreted as a command. Claude Code was NOT running in the pane. So the loop is: watchdog opens tmux session -> claude CLI fails to launch OR watchdog send-keys fires before claude is ready -> instruction lands in the shell -> nothing runs -> session ends -> watchdog restarts -> repeat.

This is a LAUNCH RACE / LAUNCH FAILURE, not an instruction-content problem. Sanitising the instruction text does not fix it.

FIX THE WATCHDOG LAUNCH SEQUENCE:
1. Launch claude with an ABSOLUTE PATH (non-interactive tmux shells often have a different PATH -- `which claude` in an interactive shell, hardcode that path or source the profile first).
2. VERIFY CLAUDE IS UP before sending any keys: after launch, poll the pane (tmux capture-pane) for Claude Code's UI marker, with a timeout. If the marker never appears, NTFY the actual launch error captured from the pane -- do not send the instruction into a dead pane, and do not loop.
3. BETTER: eliminate the race entirely -- pass the resume instruction as a launch argument (claude --dangerously-skip-permissions "Read docs/RESUME_INSTRUCTION.md and follow it") so there are no send-keys at all. Keep the instruction in a file; the argument just points at it.
4. On any quick-exit, capture-pane the last 30 lines into the watchdog log and include the first error line in the single deduped NTFY. The loop went undiagnosed for hours because nothing captured what the pane actually showed -- Rich had to attach manually.

VERIFY: deliberately kill the claude session once. Watch the watchdog bring it back cleanly: claude launches, instruction accepted BY CLAUDE CODE (not the shell), work resumes, exactly one NTFY. Then report done with the captured pane text proving CC accepted the instruction.
