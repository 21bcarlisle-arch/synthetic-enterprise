# [WORKER-FINDING] The call-set guard hardened ONE fixture; its unguarded sibling then cost nine hourly pages (2026-08-14)

**Severity:** LATENT · **Lane:** H_harness · **Status:** measured, not repaired — queued rather
than fixed on sight (SELF_INTERRUPT_DISCIPLINE); the drawn PRIORITY-ZERO work was the red itself,
landed at `fb1493702`.

## The observation, `observed-with-evidence`

`tests/controls/test_daemon_loop_mutation.py::test_dms_isolated_accounts_for_every_check_run_cycle_calls`
is a good control. It derives `run_cycle`'s call set from the shipped SOURCE (`inspect.getsource` +
regex), refuses to be green over an empty set, and forces every name into either
`NEUTRALISED_BY_DMS_ISOLATED` or `RUN_FOR_REAL_BY_DMS_ISOLATED` with a stated reason. On
2026-08-13 it was deliberately WIDENED past the `_check_*` naming convention, and that widening
caught `_flush_notification_digest` — recording the symptom exactly:

> observed as a second entry ("[DIGEST] 21 batched item(s)") breaking `assert len(calls) == 1` in
> all six stall/cooldown tests.

**One day later the identical defect, in the identical function, took the operational-layer signal
red for nine consecutive hourly checks** (this tick's draw). Because the guard's subject is the
`dms_isolated` fixture *in its own file*, and the ~27 tests that actually went red live behind a
different fixture in a different file: `tests/background/test_deadmans_switch.py::_isolate`, which
hand-lists six `run_cycle` checks and never grew a seventh.

So the control was correct, current, and green throughout — it was simply pointed at one of two
fixtures that make the same promise. The class guard closed the call-set axis for `dms_isolated`
and left its sibling on the naming-convention footing it had just been widened off.

## Why this is the class, not a second instance

The guard's own docstring says it exists so that "a hand-maintained enumeration of someone else's
call set rots silently — this makes it rot LOUDLY." That is true of the enumeration it checks. It
is not true of the *set of enumerations*: nothing relates "fixtures that neutralise `run_cycle`"
to "fixtures the guard audits", so a second such fixture is invisible to it, exactly as a seventh
check was invisible to `_isolate`. The rot moved up one level.

## The fix, stated so a future draw can take it

Make the guard's subject the CLASS of fixtures, not one fixture. Concretely: enumerate the
fixtures that monkeypatch any `run_cycle` callee (derivable — walk `tests/**` for
`monkeypatch.setattr` targets resolving into `background.deadmans_switch`), and assert each
accounts for the full source-derived call set with the same NEUTRALISED / RUN_FOR_REAL split. Add
the vacuity guard the existing test already has (`>= 2` fixtures found, else the guard has lost
its subject) and a mutation: introduce a third fixture neutralising five of the checks and confirm
it is NAMED, not passed over.

Interim mitigation already landed at `fb1493702`: the digest queue+state are pinned at directory
scope in `tests/background/conftest.py`, so this particular leak cannot recur in
`tests/background/` regardless of any per-file list. That is a pin on one real-state source, not a
closure of the call-set axis for the second fixture — the two are complementary, and this finding
is the second one.

Related: the eighth-instance pin and the R15 both-ways proof are described in
`WORKER_FINDING_THE_OPERATIONAL_SIGNAL_WAS_RED_BECAUSE_ITS_OWN_DAEMON_RAN_IT_2026-08-14.md`.
