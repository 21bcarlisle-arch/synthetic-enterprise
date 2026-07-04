[PROJECT] WATCHDOG STILL BROKEN -- second false "fixed, live" claim. Pane at 08:38 shows sh, no claude, instructions being swallowed by a quote-continuation prompt. ELIMINATE send-keys entirely.

EVIDENCE (Rich's screenshot of the claude tmux pane, 08:38 BST): status bar [claude] 0:sh* -- the pane is running sh, not claude, AFTER the 07:37 claim "watchdog launch-race fixed, process restarted, live". The watchdog injected the resume instruction repeatedly into the bare shell. Bonus failure discovered: the instruction text contains an apostrophe (Rich's) -- sh enters PS2 quote-continuation (>) and silently swallows every subsequent line. /usage slash-commands are also being typed into sh.

THREE send-keys failure modes are now proven: (1) timing race, (2) PATH (claude not found in non-login sh), (3) quote-swallowing. Patching send-keys again is not acceptable. REMOVE IT.

THE REQUIRED DESIGN -- no keystroke injection anywhere:
1. Resolve the absolute claude binary path ONCE (bash -lc 'which claude'), store it in the watchdog config.
2. Launch the session with the instruction AS AN ARGUMENT, no send-keys:
   tmux new-session -d -s claude "bash -lc '<ABS_PATH_TO_CLAUDE> --dangerously-skip-permissions \"Read docs/RESUME_INSTRUCTION.md and follow it\"'"
   The instruction lives in the file; the argument only points at it. Nothing is ever typed into a pane.
3. VERIFY: within 60s, poll tmux capture-pane for the Claude Code UI marker. If absent, capture the last 30 pane lines, NTFY them verbatim, and STOP -- one alert, no retry loop, no injection.
4. /usage checks and any other slash-command interactions: only via capture-pane verification that claude is foreground first, or drop them entirely.
5. The RESUME_INSTRUCTION.md content stays out of shells forever -- apostrophes, parens, numbered lists are all shell-hostile and all present in it.

VERIFY BEFORE CLAIMING DONE (per Rule 2, and note this rule has now been violated twice on this exact component):
- Kill the claude session deliberately. Watch the NEW watchdog bring it back: claude launches from the argument, instruction accepted BY CLAUDE CODE, work resumes.
- Then kill it again with the claude binary path temporarily broken: confirm you get ONE NTFY containing the captured pane error, and no injection loop.
- Paste both observed outcomes (captured pane text) in the completion NTFY. A claim without the two test outcomes is not done.
