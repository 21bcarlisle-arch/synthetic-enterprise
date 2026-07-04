[PROJECT] DIRECTOR OVERRIDE -- URGENT: --dangerously-skip-permissions is MANDATORY in the watchdog launch command. Rich's explicit instruction: "We must have dangerously skip, as I can't keep approving things. This is critical."

The deviation flagged in the 09:45 NTFY (omitting --dangerously-skip-permissions from the watchdog's claude launch) is REVERSED, by direct instruction from Rich.

WHY THIS IS CRITICAL: this is an autonomous system with a human who checks in periodically via phone. A restarted session without skip-permissions stalls at its FIRST tool prompt -- git, pytest, file write, anything -- and sits dead until a human notices. That is silent autonomy death on every restart, which is worse than any risk the permission prompts mitigate. The safety model for this project is NOT tool-approval prompts; it is: staged instructions with 4h opt-out, NTFY transparency, REVIEW_GATEs for one-way doors, the epistemic verifier, and the advisor verification loop. Those are the controls. Permission prompts add nothing except a stall point.

DO NOW:
1. Watchdog launch command MUST be: <ABS_NVM_PATH>/claude --dangerously-skip-permissions [+ the resume-instruction argument, no send-keys]. If the kill-tests were already run without it, update the config and re-run the second kill-test to confirm the restarted session comes back in full-autonomy mode.
2. Fix the source of the contradiction: wherever the "never skip permissions" language lives (CLAUDE.md or the watchdog design doc), amend it to state the actual policy: "This deployment runs claude with --dangerously-skip-permissions BY DESIGN, per standing director instruction. Safety is provided by staging/NTFY/REVIEW_GATE/verifier controls, not tool prompts. Do not remove the flag."
3. Confirm in the kill-test completion NTFY: the exact launch command now in the watchdog config, verbatim, so this can never be silently reinterpreted again.

Positive note, genuinely: flagging the deviation instead of silently applying it was the RIGHT behaviour -- deviations surfaced for direction is exactly the protocol. The decision itself was wrong, but the transparency is what made this cheap to correct. Keep flagging; this is how the loop is supposed to work.
