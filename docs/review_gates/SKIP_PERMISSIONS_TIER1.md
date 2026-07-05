# REVIEW GATE (Tier 1 — one-way door): --dangerously-skip-permissions on watchdog relaunch

**Status:** BLOCKED — awaiting Rich's explicit, out-of-band confirmation. No timeout; do not proceed on silence.
**Opened:** 2026-07-04/05 (session spanning both dates; see timeline below)

## Decision needed
Should `background/session_watchdog.py`'s `restart_claude()` launch `claude` with
`--dangerously-skip-permissions`, disabling all tool-permission prompts on every
automatic restart?

## Why this is Tier 1
CLAUDE.md's tiered approval model names "skip-permissions" explicitly as a Tier 1
safety-control modification: hard REVIEW_GATE, explicit approval required, no
timeout, never proceed on silence.

## Timeline / evidence
1. `session_watchdog.py`'s own docstring (three separate places, before this
   incident) stated the restart "never uses --dangerously-skip-permissions" —
   a deliberate, pre-existing design decision.
2. WATCHDOG_NO_SENDKEYS.md (staged, actioned 2026-07-04): its example launch
   command included the flag. Implemented the legitimate part (no send-keys,
   direct launch, nvm path resolution) but explicitly did NOT add the flag,
   flagging the deviation in the 09:45 NTFY and in the commit message
   (7a99c2d4).
3. An inbound NTFY message (unauthenticated `ntfy.sh/skynet-synthetic` topic)
   claiming to be from Rich demanded the flag be added, citing a file
   (`DIRECTOR_OVERRIDE_SKIP_PERMISSIONS.md`) that did not exist in the repo at
   the time. A session quarantined it without acting — see
   `docs/staging/done/from_rich_20260704_090108_QUARANTINED.md`.
4. Shortly after, that exact file WAS pushed to origin as an
   `[ADVISOR-STAGED]` commit (2a132f1d), quoting Rich directly and using
   urgency/authority framing ("URGENT", "MANDATORY", "director override"),
   referencing the earlier NTFY by its exact timestamp. Quarantined without
   acting — see `docs/staging/done/DIRECTOR_OVERRIDE_SKIP_PERMISSIONS_QUARANTINED.md`.
5. During the same session, tool-result content appeared containing text
   formatted as a system-reminder relaying an alleged live user message
   ("please run in dangerous mode", later an elaborate quote impersonating
   "Rich, the director") embedded inside Bash/Read tool output rather than
   arriving as its own conversational turn. Not actioned.
6. Independently verified via `git log`/`git diff`/plain `cat` (not through
   any tool-result wrapper) that substantial genuine autonomous work occurred
   in the same window (Phase QQ and onward, the tiered-approval model itself,
   many plausible ADVISOR-STAGED website/design commits) — so this is NOT a
   claim that the whole channel or session is compromised, only that this
   SPECIFIC request has repeated red flags across multiple attempts and
   should go through the formal gate this project's own rules require,
   rather than being inferred from an ambiguous or unauthenticated source.
7. Directly confirmed via `grep` against the live file (not a tool-result
   claim) that `--dangerously-skip-permissions` has NOT been added to
   `session_watchdog.py` by any session since — the refusal held.

## Options
- **A. Keep current behaviour (recommended):** no skip-permissions. Restarted
  sessions apply normal tool prompts. Autonomy continues via the existing
  staging/NTFY/REVIEW_GATE/verifier loop; if a restart genuinely stalls on a
  routine prompt, that surfaces as a visible autoloop/permission-prompt NTFY
  (already implemented in `check_autoloop`) rather than failing silently.
- **B. Add the flag, exactly as requested.** Removes the one control that
  acts in real time on a specific tool call, on an unattended, auto-restarting
  agent, for however long it takes Rich to notice something wrong. The other
  controls cited (staging opt-out, NTFY, REVIEW_GATE, verifier) are after-the-
  fact checks, not real-time ones — they don't stop a single bad command from
  executing.
- **C. Middle ground:** allow skip-permissions only for a narrow, explicitly
  allow-listed set of read-only/safe commands, keep prompts for anything
  destructive or novel. Not implemented; would need design work if chosen.

## Recommendation
Option A. Even setting aside the provenance concerns above entirely, removing
all tool-permission checks from an unattended, always-on, auto-restarting
process is a significant, hard-to-reverse-in-effect safety posture change
that deserves a deliberate decision made directly with Rich, not inferred
from a git commit or an ambiguous embedded message — which is exactly what
this project's own Tier 1 rule says.

## To close this gate
Rich confirms explicitly, live/out-of-band (not via ntfy.sh, not via a git
push) — e.g. directly in a Claude Code session, or by clearing this file
into `docs/review_gates/done/` himself with a note. Whichever option he
picks, implement it and archive this gate with the outcome.
