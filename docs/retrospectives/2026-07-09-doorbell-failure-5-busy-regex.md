# Retrospective: doorbell failure #5 — busy-spinner regex false-positive

Filed per CLAUDE.md's phase-close retro trigger (a harness rule/mechanism
changed) and the recurring-pattern criterion — this is the fifth distinct
failure mode found in the wake/turn-granting subsystem across two days
(Phase SB corruption, strike 3 relay race, strike 4 THE SUPERVISOR
rebuild, this morning's R4 copy-mode wedge, and this one). Every claim
below is labelled **OBSERVED** or **INFERRED** per R9.

## What happened

**OBSERVED**: the director reported, in-console, that the session had sat
idle for ~5 hours with real work queued (the Epoch-2 evidence-pass
verdicts already delivered in the same turn as this incident was reported,
and a staged `BUDGET_UNCONSTRAINED.md` left unactioned) and that the
supervisor's fingerprint-escalation NTFY (built specifically to catch a
stuck/silent failure, doorbell failure #4) never fired.

**OBSERVED**: `docs/observability/supervisor-log.md` showed the line
"Session busy -- skipping this cycle" on every single 2-minute cycle from
at least 14:00 UTC through 20:52 UTC (2026-07-09) with zero exceptions --
over 6.5 hours continuous. The session was genuinely idle (no active turn)
for nearly all of that window; a live capture at 20:53 UTC (mid-response
to the director's message, genuinely busy) confirmed the busy-detection
mechanism does correctly fire during real activity, so the fault was
specifically a false-positive during idle time, not a total detector
failure.

**OBSERVED**: `background/tmux_relay.py::_BUSY_SPINNER_LINE`'s regex
(`^\s*\S\s+\S.*[.…]{1,3}\s*$`, introduced commit `d5769184`, Phase SB,
2026-07-08 -- one day older than the same morning's R4 copy-mode fix, in
the same function) was tested directly against a real captured pane and
confirmed to match Claude Code's own persistent completed/pending
task-list panel (bullets `◼ ◻ ✔ ✘`, each line truncated with an ellipsis)
-- and, separately, confirmed NOT to match the actual live spinner line
itself (`✽ Running the Epoch-2 desk-work evidence pass… (51s)`), since
that line's ellipsis sits mid-line, not at the end. The regex was matching
the wrong lines outright, in both directions.

**OBSERVED**: that task-list panel is not transient -- it is Claude Code's
own standing UI element and stays visible in the pane's last 30 lines
indefinitely once any checklist-tracked work has happened in the session,
which is most of the time in ordinary use. The false "busy" reading was
therefore not an edge case but close to the default state for any session
with a task history, explaining why it went undetected through Phase SB,
strikes 3/4, and this morning's R4 fix -- none of those incidents'
regression tests happened to include a pane snapshot with this specific
static-checklist shape; all used a hand-written idle-pane fixture without
one.

**OBSERVED, second bug found during the same investigation**: the
separate `_BUSY_FOOTER_HINT = "esc"` check was a bare substring search
across the *entire* captured pane content, not scoped to the actual
footer line. A regression test written to prove the spinner-regex fix
(using the word "description" in fixture text) failed for an unrelated
reason: "description" contains "esc" as a substring, and would have
false-positived the footer check on its own, independent of the spinner
fix. Fixed by scoping the check to the line containing the stable "bypass
permissions" marker.

## Why fingerprint-escalation (doorbell failure #4's fix) didn't catch this

**INFERRED, follows directly from the code**: `supervisor.py::run_cycle()`
checks `is_session_idle()` first and returns immediately on `False`,
before `find_work()` or `grant_turn()` ever run. The fingerprint/stuck-grant
escalation logic lives entirely downstream of a successful grant attempt --
it detects "grants keep succeeding with no progress," not "grants are never
attempted at all." A false-busy reading exits the cycle before that logic
is ever reached, so this failure mode was structurally outside what
doorbell failure #4's fix was built to catch. This is not a flaw in that
fix; it is a different failure surface in the same daemon that hadn't yet
been exercised.

## Fix

`_BUSY_SPINNER_LINE` now requires the elapsed-time suffix a genuine
spinner line actually carries (`(<N>s)` / `(<N>m <N>s)`), which static
checklist bullets never show. `_BUSY_FOOTER_HINT`'s check is now scoped to
the pane's actual footer line. Three regression tests added using the
exact real captured pane text (not a synthetic guess) for both the
completed-task-list case and the footer-scoping case. Full background
suite (388) and epistemic verifier re-run clean. All four tmux-relay-
consuming daemons (supervisor, session-watchdog, staging-watcher,
dispatcher) killed and restarted live from the fixed code -- R2 discipline
(committed != running).

## Pattern across all five incidents (not actioned further here, noted for the next retro-worthy event)

Every one of the five failures lived in real-vs-assumed pane content:
Phase SB (a corrupted send under busy-state input handling), strike 3
(two daemons racing into the same pane), strike 4 (verified-delivered
grants producing no observable work, root cause never fully confirmed
from outside the CLI), this morning's R4 (a frozen copy-mode/scrollback
view), and this one (a persistent UI element misread as a live spinner).
Four of five were only found once someone looked at an *actual* live pane
capture rather than reasoning from an assumed shape. Worth a standing
practice, not repeated here as a new rule: when writing a regression test
for pane-content detection logic, prefer a captured real pane over a
hand-written fixture wherever one is available, precisely because every
hand-written fixture so far has under-represented a real UI state that
went on to cause an incident.
