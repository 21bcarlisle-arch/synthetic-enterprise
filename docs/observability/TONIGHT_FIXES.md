# TONIGHT_FIXES.md — the five roots behind the overnight stack failure (2026-07-16)

Context: the stack was DOWN and a 30-min cron (`start_worker.sh`) had been resurrecting a
broken stack all night, spamming the director's phone. Rich disabled the cron and asked
for five roots to be fixed, each diagnosed **from the code** and verified **against the
running system, not the commit**. The stack was NOT restarted and cron was NOT re-enabled
(per instruction). Each fix is its own commit.

Commits (newest first):
- `a9dbf8a19` Item 5 — auto-restart starts the FIXED stack only
- `b5514ad58` Item 4 — clear `publish_gate_wedged`
- `c1b410ad6` Item 3 — a restart must deploy current HEAD
- `e601f06f0` Item 2 — watchdog: no console-kill, no thrash (+ Item 1b)
- `610acfb1d` Item 1 — pytest never sends a real NTFY

Everything below is labelled `observed-with-evidence` or `inferred` per R9.

---

## Item 1 — pytest must NEVER send a real NTFY  (`610acfb1d`, + Item 1b in `e601f06f0`)

**Real cause (observed):** `background.ntfy_utils.send_ntfy` POSTs to the director's live
ntfy topic. Any test that exercised a notification path without mocking the send buzzed
his phone with synthetic content ("fake reason", "atom X"). Three separate processes run
the suite and all did this: the publish gate's fast suite every sim cycle, an auto-resumed
session's recovery-checklist pytest run, and plain interactive `pytest`.

**Fix (mechanism, not discipline):**
- `send_ntfy()` hard-guards on `PYTEST_CURRENT_TEST`: inside any test it returns the
  `"pytest-suppressed"` sentinel and never invokes curl. A test that genuinely exercises
  the POST/parse internals opts in with `_allow_real_send=True` (curl mocked, still no
  network).
- `tests/conftest.py` adds a **global autouse** fixture replacing `send_ntfy` with a
  recording no-op for every test (belt-and-suspenders; `@pytest.mark.real_ntfy` escape
  hatch for the internals tests).
- Item 1b: the watchdog's `RESUME_INSTRUCTION` (the "Session resuming after crash"
  recovery checklist) no longer routine-pings on every restart — NTFY only on a real
  transition/blocker (R5) — and points at `PRIORITIES.md`, not the retired
  `MASTER_BACKLOG.md`. The pytest guard means the pytest that checklist runs cannot page.

**Verified against the running interpreter (stack down):** with `PYTEST_CURRENT_TEST` set
and `subprocess.run` sabotaged to raise on any call, `send_ntfy` returned
`"pytest-suppressed"` with **zero** curl invocations; `_allow_real_send=True` still
reached the curl path. `tests/background/test_ntfy_utils.py` 24/24 pass.

---

## Item 2 — watchdog must not kill interactive console sessions, and must not thrash  (`e601f06f0`)

Three sub-roots, all in `background/session_watchdog.py`:

**(a) Console-kill hazard (observed in code).** `reap_orphan_interactive_claude()` (added
earlier tonight to kill a crash-recovery ghost) SIGTERM'd **every** interactive `claude`
process except its own pid. A legitimate second console session the director started
himself would have been reaped. **Fix:** reap ONLY true orphans — a `claude` process NOT
backed by a live tmux pane (checked via `tmux list-panes -a` + an ancestor walk). The
managed session AND the director's own console session are both pane-backed, so both are
spared, always. **Fails safe:** if the tmux pane list is unavailable we cannot prove a
process is an orphan, so we reap NOTHING.

**(b) The wedge itself (observed).** That same reap used a function-local `import os as
_os`, so its test's `monkeypatch.setattr(watchdog.os, ...)` raised `AttributeError` and
RED-wedged the whole publish gate — this is Item 4's rc=1. `os`/`signal` are now
module-level.

**(c) False/repeated DEGRADED + crash pages (observed).** A real orphan ghost made the
single-session health check read "MULTIPLE interactive Claude sessions" **every cycle for
a full day**, and the post-restart daemon-health page fired on every restart. **Fix:** the
DEGRADED page is now DEBOUNCED (re-check after a short delay; page only problems present in
BOTH passes, so a post-respawn race drops out) and RATE-LIMITED (≥1h cooldown, so a restart
storm cannot become a page storm). The crash page is deduped to once per crash-streak (R5),
reset on confirmed-alive so a genuinely new crash still pages.

**Verified against the live system (stack down, this session is the only `claude`, running
as `-p`):** `interactive_claude_pids()` correctly EXCLUDES this `-p` session; with no tmux
server `_live_tmux_pane_pids()` is empty so `reap_orphan_interactive_claude()` is a
fail-safe no-op; this pid is never in the reap set. 93/93 in `test_session_watchdog.py` +
`test_health_check.py`, including new tests: reap spares a live console + reaps only the
orphan, reap fail-safe on no-tmux, transient DEGRADED does not page, DEGRADED rate-limited.

---

## Item 3 — a restart must DEPLOY current HEAD  (`c1b410ad6`)

**Real cause (observed, and a second occurrence of a named class).** The 2026-07-13 retro
built `health_check._check_stale_running_code()` to DETECT a daemon running code older than
its committed script ("committed != running") — but left it **detect-only**: it flagged the
drift, nothing acted. Worse, `start_worker.sh`'s `_start_session` SKIPS an already-running
session ("safe to re-run"), i.e. it deliberately LEAVES stale code running. So every fix
shipped to a running daemon stayed silently defeated until a human manually restarted it.

**Fix (the action half):** `health_check.stale_daemon_sessions()` returns the tmux session
names whose live process started before its own script's mtime; `start_worker.sh` kills
exactly those before its start block, so the following `_start_session` respawns them fresh
on current HEAD. Only stale sessions are touched — a daemon already on HEAD keeps its state.

**Verified against the running system:** helper runs live (stack down → `[]`, nothing to
kill); the exact command line embedded in `start_worker.sh` returns empty and the kill loop
is correctly skipped; `bash -n` clean. 19/19 stale-code tests pass, incl. a stale daemon is
named for restart and a fresh one is NOT (R15 mutation counterpart — never churn a current
daemon).

---

## Item 4 — clear `publish_gate_wedged` (rc=1 regression)  (`b5514ad58`)

**Real cause (observed).** The publish gate runs the full fast suite with `pytest -x`, so
ONE red test wedges the entire site/report pipeline. `docs/observability/sim-runner-log.md`
shows "Tests FAILED - not committing" repeating to the 22:04 UTC stack-down; the gate state
file recorded rc=1 `test_regression` across ~19 cycles. Root-caused it by **re-running the
exact gate command**: the single first failure was
`test_session_watchdog.py::test_reap_orphan_interactive_claude_never_kills_self` raising
`AttributeError` — the local-`import os` mismatch fixed in Item 2. (Rich's guess was a
stale-fact assertion at `7df80b55`; the actual cause was this uncommitted code/test
mismatch — same outcome, a red gate test silently wedges publishing.)

**Fix / clear:**
- The regression is fixed in Item 2 (`e601f06f0`).
- Resolved the `publish_gate_wedged` action-needed item with an honest root-cause answer
  and reset `.publish_gate_state.json` (failures `[]`, alarm re-armed) — the same effect
  `record_publish_gate_success()` has, no NTFY sent. (Stack is down, so no clean publish
  would auto-clear it.)
- Folded the CLASS into scheduled housekeeping (Rich's ask): the H22 frame gains a §3.7
  "tests that can wedge the publish pipeline" sweep — generalised to "a red gate test",
  run on cadence independent of sim runs, plus a dirty-working-tree flag (uncommitted
  in-flight code is what wedged it tonight).

**Verified against the running system:** the EXACT gate fast-suite (`SIM_FAST_MODE=1`, same
ignore set as `run_fast_tests`) now passes **18310 / 5 skipped / 2 xfailed, exit 0, 288s**
— well under the 600s gate timeout, so the next real publish clears the gate on its own.
`publish_gate_wedged.resolved == True` confirmed by reload.

---

## Item 5 — auto-restart must start the FIXED stack only; cron stays OFF  (`a9dbf8a19`)

**Real cause (observed).** A console kill of the stack is not durable — anything that
re-runs `start_worker.sh` (the 30-min cron) resurrects it. All night the cron brought a
broken stack back up (recovery session ran pytest and paged; daemons ran stale code).

**Fix — two startup guards in `start_worker.sh`:**
1. **Durable disable flag** `docs/observability/.stack_disabled`: if present, refuse to
   start (print the reason, exit 0). A deliberate DOWN state now survives a cron tick.
2. **Import smoke test**: before launching, import the core daemons; a broken import
   (syntax error from half-landed work, missing `SE_NTFY_TOPIC`) ABORTS startup (exit 1)
   instead of spawning a dozen instantly-crash-looping sessions.

With Item 3 (a start refreshes stale daemons to HEAD), a start deploys current committed
code that actually loads, or it refuses. **Cron is left OFF** (`crontab -l` empty; not
re-added). Documented in MAINTENANCE.md.

**Verified against the running system:** `crontab -l` empty (cron OFF); `bash -n` clean;
the import smoke test passes with the topic loaded and exits non-zero without it; the
disable-flag guard refuses when the flag is present and proceeds when absent; **no tmux
server was created by any test** (stack not started, per instruction).

---

## What was deliberately NOT done
- The stack was **not restarted** and **cron was not re-enabled** (per instruction). These
  fixes take effect the next time the stack is started; the disable flag + smoke test + HEAD
  refresh mean that start will bring up the fixed, current stack.
- The `publish_gate_wedged` alarm was cleared to reflect the fixed root cause; it was not
  suppressed — the gate re-verifies and re-arms on the next real publish.

## Follow-up worth queuing (not blocking)
- The publish gate coupling the ENTIRE 18k-test suite (`pytest -x`) to the live-site
  pipeline is the structural fragility behind this class: any red test anywhere wedges
  publishing for hours with only one signal. H22 §3.7 now covers detection; a real fix
  (decouple publish from the full suite, or run the gate on a cadence independent of sim
  runs) is a BUILD item.
