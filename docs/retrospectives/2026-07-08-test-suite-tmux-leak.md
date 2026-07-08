# Incident: test suite sent real tmux keystrokes into the live session (2026-07-08)

Filed per `docs/staging/NTFY_CHANNEL_HARDENING.md` item 5 and the director's direct
correction. Every claim below is labelled **OBSERVED** (I verified it directly against
real state — a file, a log, a topic history) or **INFERRED** (a conclusion drawn from
observed facts, not itself independently checked) — per the new R9 rule this incident
produced.

## What happened

Earlier the same session, I built an event-driven wake mechanism
(`background/staging_watcher.py::_relay_wake_to_claude`, then committed `45a1e701`):
when a genuinely new staged file appears, the watcher's existing poll loop injects one
`tmux send-keys` turn into the live `claude` session.

After building it, I ran the full pytest suite (`SIM_FAST_MODE=1 pytest tests/`) several
times over the following ~40 minutes, alongside restarting the live `staging_watcher.py`
daemon twice to live-test the new mechanism against a real staged file. Shortly after, a
flood of bracketed `[STAGING WATCHER: new staged instruction(s) landed -- ...]` messages
appeared in this session's own input, naming files that never existed on disk
(`TASK_NEW.md`, `A.md`, `B.md`, `NEW.md`, `maintenance_due_202610.md`).

## My first response was wrong, and asserted ahead of the evidence

I concluded these were externally injected — a prompt-injection / spoofing attempt
mimicking the new mechanism's output format, using my own test fixture names (which I'd
just pushed publicly) as bait. I reported this to the director as an attacker narrative.

**This was INFERRED, not OBSERVED, and I presented it as though it were established.** I
had checked that the flagged filenames didn't exist on disk and that the real watcher log
only recorded 2 genuine wake events — real, useful checks — but I never checked the one
thing that would have distinguished "external actor publishing to the topic" from "my own
process talking to itself locally": the actual ntfy.sh topic history. The director checked
it himself and found it clean — no such messages were ever published there.

## Real root cause (OBSERVED — verified by reading the actual code and log)

The flood was 100% local, produced by this session's own test suite, not any external
channel.

- **OBSERVED**: `tests/background/test_staging_watcher.py` contains five *pre-existing*
  tests — `test_check_once_notifies_only_for_new_files` (writes `TASK_OLD.md`/
  `TASK_NEW.md`), `test_check_once_persists_seen_state` (`TASK_NEW.md`),
  `test_check_once_notifies_for_multiple_new_files` (`A.md`, `B.md`),
  `test_check_once_returns_updated_seen` (`NEW.md`), and
  `test_monthly_maintenance_marker_gets_notified_via_check_once` (which calls
  `check_monthly_maintenance(datetime(2026, 10, 1, ...))`, producing
  `maintenance_due_202610.md`) — that predate the wake feature and monkeypatch `ntfy`
  but never mocked the new `_relay_wake_to_claude()` call `check_once()` gained.
- **OBSERVED**: `_relay_wake_to_claude()`, as originally written, called real
  `subprocess.run(["tmux", "send-keys", "-t", "claude", ...])` with no test-isolation
  guard of any kind — `SESSION_NAME = "claude"` is the actual live session name, not
  test-scoped.
- **INFERRED (but now solidly grounded)**: every time I ran the test suite after adding
  the wake call to `check_once()` (I ran it at least five times over ~40 minutes, per this
  session's own command history), each of those five old tests fired a real, unmocked
  `tmux send-keys` into the live `claude` pane using its own fixture filename — which is
  the exact, repeated, filename-matching pattern observed. I have not re-run the exact
  historical sequence to reproduce the precise count, but the mechanism, the filenames,
  and the timing window all line up without residue.
- **OBSERVED**: `docs/staging/NTFY_CHANNEL_HARDENING.md` (advisor-staged, arrived the same
  morning) itself asserted "the fake flood is consistent with external publish to the open
  topic" and cited "advisor-verified via API" as confirmed exposure. Given the director's
  direct check of the topic history found nothing there, and my own evidence above fully
  accounts for the flood without requiring any external actor, **that specific claim in the
  staged document was also asserted ahead of its evidence** — the same failure class this
  incident is about, arriving from a different source. Recorded here, not silently accepted.

## The 11:54/12:02 BST duplicate NTFY (a separate, smaller, real issue)

**OBSERVED**: two identical `"New staged instruction: CORE_FIDELITY_BEFORE_LOOPS.md"`
NTFYs were sent seven minutes apart (10:54:56 and 11:02:06 UTC, per the ntfy.sh topic
history). **OBSERVED**: this was caused by me deliberately removing
`CORE_FIDELITY_BEFORE_LOOPS.md` from the watcher's persisted seen-state and restarting the
daemon twice, specifically to force a live re-fire and prove the new wake mechanism worked
end-to-end (verified via `tmux capture-pane`). Not a bug in the running mechanism — a
side-effect of my own test methodology that I should have flagged to the director before
doing it.

## What is genuinely still open (real vulnerability, independent of today's root cause)

The ntfy topic name (`skynet-synthetic`) is committed in plaintext across several tracked
files in a public repository. **OBSERVED**: nothing published to the real topic during
this incident. That does not mean the exposure isn't real — an unauthenticated, public
topic name in a public repo is genuinely publishable-to by anyone who reads the repo,
regardless of whether anyone has done so yet. This is closed out separately in the same
session via `docs/staging/NTFY_CHANNEL_HARDENING.md` (topic rotation to a secret,
gitignored value + wake-message signing) — see that file and the commits that closed it
for the mechanics.

## Fixes landed this session

1. `background/tmux_relay.py` (new): the one shared `send_keys()` helper `session_watchdog.py`,
   `dispatcher.py`, and `staging_watcher.py` now all call, with a structural test-isolation
   guard (`PYTEST_CURRENT_TEST` env var, set by pytest for the duration of every test it
   runs) — a silent no-op under pytest regardless of whether any individual test remembers
   to mock it. This is the real fix: not "remember to mock every call site" (which just
   failed), but a guard that cannot be forgotten.
2. The five old tests that lacked a mock now have one too (defense in depth — belt and
   braces alongside the module-level guard).
3. R9 (below) — evidence before narrative in incident reporting, going forward.

## R9 (new permanent rule, added to CLAUDE.md)

**R9. Incident reports label every claim `observed-with-evidence` or `inferred`, evidence
before narrative.** A conclusion about *why* something happened — especially one implying
an external actor, a security compromise, or blame — must be checked against the most
direct available evidence (here: the actual channel's history) before being asserted, not
after. If the direct check hasn't been done yet, say so explicitly rather than presenting
an inferred narrative as established.
