#!/usr/bin/env python3
"""R15 proof for alarm-repetition escalation (director instruction, 2026-08-20):

    "the alerts repeated identically all night ... make a repeating alert escalate itself
     into the draw instead of re-telling me."

This control sits on the path that PAGES THE DIRECTOR, so the mutation that matters most is
not "does it escalate" but "can it silence something it should not". Two ways that could
happen, and both are driven hardest here:

  1. Over-normalising -- two DIFFERENT faults collapsing to one signature, so the second is
     suppressed as a repeat of the first and he never hears about it.
  2. Escalation swallowing the alarm -- an exception while filing the work item taking the
     page down with it, turning a loud outage into a silent one.

The real overnight messages are used verbatim as fixtures rather than invented ones. That is
not decoration: the first version of the number pattern carried a trailing `\\b`, which cannot
match "252" inside "after 252s", so the six pages still produced six signatures. It read
correctly and did nothing, and only the real strings showed it.
"""
from __future__ import annotations

import json
import time

import pytest

from background import alarm_repetition as ar

# Verbatim from docs/observability/sim-runner-log.md, 2026-08-19 23:39Z -> 2026-08-20 00:26Z.
FAIL_252 = "[SIM] Run FAILED after 252s — KeyError: 'net_margin_gbp' (full tail in sim-runner-log.md)"
FAIL_255 = "[SIM] Run FAILED after 255s — KeyError: 'net_margin_gbp' (full tail in sim-runner-log.md)"
FAIL_253 = "[SIM] Run FAILED after 253s — KeyError: 'net_margin_gbp' (full tail in sim-runner-log.md)"
OTHER_FAULT = (
    "[SIM] Run FAILED after 251s — TypeError: replacement_cost_avoided_gbp() got an "
    "unexpected keyword argument 'counted_in_guard' (full tail in sim-runner-log.md)"
)


# ---------------------------------------------------------------------------
# The signature: what counts as "the same alarm"
# ---------------------------------------------------------------------------
def test_MUTATION_the_six_real_overnight_pages_share_one_signature():
    """THE case. These three differ only in elapsed seconds and are the same condition."""
    sigs = {ar.alarm_signature(m) for m in (FAIL_252, FAIL_255, FAIL_253)}
    assert len(sigs) == 1, f"the same failure produced {len(sigs)} signatures: {sigs}"


def test_MUTATION_a_DIFFERENT_fault_from_the_same_daemon_is_a_DIFFERENT_alarm():
    """The over-normalising direction, and the one that costs most if wrong: a TypeError
    suppressed as a repeat of a KeyError is an outage the director is never told about.
    Both of these really did occur on the same night, from the same runner."""
    assert ar.alarm_signature(FAIL_252) != ar.alarm_signature(OTHER_FAULT)


def test_a_worsening_counter_is_still_the_same_condition():
    """Deliberate. "3 consecutive" and "9 consecutive" are one condition getting worse, and
    the answer to that is the work item, not another page at 4am."""
    a = "[SIM] Operational signal RED, persistent (3 consecutive) -- paged"
    b = "[SIM] Operational signal RED, persistent (9 consecutive) -- paged"
    assert ar.alarm_signature(a) == ar.alarm_signature(b)


def test_a_varying_git_hash_does_not_split_the_signature():
    a = "[SIM] CONSISTENCY GATE FAILED (git=a77784f4a) — surfaces disagree"
    b = "[SIM] CONSISTENCY GATE FAILED (git=a11556e23) — surfaces disagree"
    assert ar.alarm_signature(a) == ar.alarm_signature(b)


# ---------------------------------------------------------------------------
# The filing
# ---------------------------------------------------------------------------
def test_escalate_files_a_finding_naming_the_alarm_and_its_count(tmp_path):
    p = ar.escalate(FAIL_252, key="auto:abc", repeats=6, first_ts=time.time() - 3600,
                    staging_dir=tmp_path)
    assert p is not None and p.is_file()
    body = p.read_text(encoding="utf-8")
    assert "**Severity:**" in body and "**Lane:**" in body, "not a classifiable finding"
    assert "6 times" in body, "the repetition count is the finding; it must be stated"
    assert "net_margin_gbp" in body, "the diagnostic payload was dropped (R5)"
    assert "1.0h" in body, "the window the repeats covered is missing"


def test_MUTATION_the_SAME_alarm_on_the_same_day_files_nothing_further(tmp_path):
    """The defect this remedy could most easily become. A process re-creating one finding
    hourly cost four manual clears on 2026-08-19; an escalation that filed per repetition
    would be that defect rebuilt inside its own cure."""
    first = ar.escalate(FAIL_252, key="k", repeats=3, first_ts=time.time(), staging_dir=tmp_path)
    again = ar.escalate(FAIL_255, key="k", repeats=4, first_ts=time.time(), staging_dir=tmp_path)
    assert first is not None
    assert again is None, "a repeat filed a second document"
    assert len(list(tmp_path.glob("*.md"))) == 1


def test_MUTATION_the_FILENAME_is_built_from_the_normalised_text(tmp_path):
    """Why the previous test passes at all. On the RAW message these three would be
    ..._AFTER_252S_..., _255S_, _253S_ -- three paths, so idempotence-by-path would file
    three documents and the hourly-recreation defect would be back."""
    day = "2026-08-20"
    names = {ar.finding_path(m, today=day, staging_dir=tmp_path).name
             for m in (FAIL_252, FAIL_255, FAIL_253)}
    assert len(names) == 1, f"one condition produced {len(names)} filenames: {names}"


def test_a_different_fault_files_its_own_document(tmp_path):
    ar.escalate(FAIL_252, key="k1", repeats=3, first_ts=time.time(), staging_dir=tmp_path)
    ar.escalate(OTHER_FAULT, key="k2", repeats=3, first_ts=time.time(), staging_dir=tmp_path)
    assert len(list(tmp_path.glob("*.md"))) == 2


def test_MUTATION_a_test_run_cannot_file_into_the_REAL_staging_directory(monkeypatch):
    """A test fixture must be STRUCTURALLY unable to reach the director (R15 / G-N2), and a
    document in his draw queue reaches him as surely as a page does.

    THIS IS NOT HYPOTHETICAL. Within hours of the module going live, five findings appeared in
    docs/staging/ and one of them quoted `SOME_DOC.md` -- a fixture filename from
    tests/background/test_deadmans_switch.py. `send_ntfy` has carried a guard of this exact
    shape since 2026-07-16 ("my phone is spamming with test messages"); I built the escalation
    BESIDE that guard rather than behind it, so the send was protected and the write was not.

    The guard is scoped to the real directory on purpose: a test that passes its own tmp_path
    is exercising the mechanism honestly and must keep working, or the module becomes
    untestable -- which is how a guard like this ends up deleted."""
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "test_x (call)")
    assert ar.escalate(FAIL_252, key="k", repeats=3, first_ts=time.time()) is None, (
        "a pytest run filed a work item into the real docs/staging/"
    )


def test_a_test_supplying_its_own_directory_still_files(tmp_path, monkeypatch):
    """The other half: the guard must not make the mechanism untestable. Both routes a test
    can legitimately take are driven -- passing staging_dir, and redirecting the module's
    STAGING_DIR, which is what the end-to-end fixture below does and what my first version of
    the guard broke."""
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "test_x (call)")
    assert ar.escalate(FAIL_252, key="k", repeats=3, first_ts=time.time(),
                       staging_dir=tmp_path) is not None
    monkeypatch.setattr(ar, "STAGING_DIR", tmp_path / "other")
    assert ar.escalate(OTHER_FAULT, key="k2", repeats=3, first_ts=time.time()) is not None


def test_MUTATION_an_unfilable_finding_RAISES_rather_than_reporting_success(tmp_path):
    """Fail-closed on the escalation itself: returning None on an OSError would be
    indistinguishable from 'already filed', and the caller would latch `escalated` on a
    document that does not exist -- suppressing the alarm forever with nothing in the draw."""
    blocked = tmp_path / "not-a-dir"
    blocked.write_text("x", encoding="utf-8")
    with pytest.raises(ar.EscalationUnavailable):
        ar.escalate(FAIL_252, key="k", repeats=3, first_ts=time.time(), staging_dir=blocked)


# ---------------------------------------------------------------------------
# The contract: notify() end to end
# ---------------------------------------------------------------------------
@pytest.fixture
def wired(tmp_path, monkeypatch):
    """notify() with its transition store and staging dir redirected, and the wire cut."""
    monkeypatch.setenv("SE_NTFY_TOPIC", "test-topic")
    from background import notify as n
    monkeypatch.setattr(n, "TRANSITIONS_FILE", tmp_path / "transitions.json")
    monkeypatch.setattr(ar, "STAGING_DIR", tmp_path / "staging")
    sent = []
    monkeypatch.setattr(n.ntfy_utils, "send_ntfy",
                        lambda msg, **kw: sent.append(msg) or "id-1")
    # Route everything instantly; the digest path is a different subject.
    from background import notification_digest
    monkeypatch.setattr(notification_digest, "is_instant", lambda *a, **k: True)
    return n, sent, tmp_path / "staging"


def test_MUTATION_the_overnight_repeat_pages_ONCE_and_then_becomes_work(wired):
    """THE end-to-end case, replayed. Six real failures, six calls, one page, one work item.

    Before this change all six went through: sim_runner.py called notify() with no
    transition_key, so the contract's transition-only rule was never engaged."""
    n, sent, staging = wired
    results = [n.notify(m, kind="real_alarm")
               for m in (FAIL_252, FAIL_255, FAIL_253, FAIL_252, FAIL_255, FAIL_253)]
    assert len(sent) == 1, f"the director was paged {len(sent)} times, not once: {sent}"
    assert all(r.startswith("suppressed:unchanged:") for r in results[1:])
    filed = list(staging.glob("WORKER_FINDING_REPEATING_ALARM_*.md"))
    assert len(filed) == 1, f"expected exactly one work item, got {[p.name for p in filed]}"


def test_MUTATION_a_NEW_fault_still_pages_immediately_while_another_is_suppressed(wired):
    """The silencing direction. A suppressed alarm must not suppress its neighbours -- this
    is the failure mode that would make the whole change a net loss."""
    n, sent, _ = wired
    for _ in range(5):
        n.notify(FAIL_252, kind="real_alarm")
    assert len(sent) == 1
    n.notify(OTHER_FAULT, kind="real_alarm")
    assert len(sent) == 2, "a different fault was swallowed as a repeat of the first"


def test_MUTATION_escalation_failing_does_NOT_swallow_the_alarm(wired, monkeypatch):
    """A failure to file the work item must never take down the alarm that prompted it."""
    n, sent, _ = wired

    def boom(*a, **k):
        raise ar.EscalationUnavailable("disk gone")

    monkeypatch.setattr(ar, "escalate", boom)
    for _ in range(4):
        n.notify(FAIL_252, kind="real_alarm")
    assert len(sent) == 1, "the first page was lost when escalation broke"


def test_MUTATION_escalation_is_RETRIED_while_it_keeps_failing(wired, monkeypatch):
    """The latch must not close on a document that was never written. Otherwise one transient
    disk error suppresses that alarm permanently with nothing in the draw -- an alarm that is
    both silent and unrecorded, which is worse than the repetition it replaced."""
    n, sent, staging = wired
    calls = []

    real = ar.escalate

    def flaky(*a, **k):
        calls.append(1)
        if len(calls) < 3:
            raise ar.EscalationUnavailable("transient")
        return real(*a, **k)

    monkeypatch.setattr(ar, "escalate", flaky)
    for _ in range(6):
        n.notify(FAIL_252, kind="real_alarm")
    assert len(calls) >= 3, "escalation stopped being attempted after it failed"
    assert list(staging.glob("*.md")), "it never recovered and filed the work item"


def test_MUTATION_a_FAILED_send_is_retried_not_remembered_as_delivered(wired, monkeypatch):
    """THE regression this change nearly shipped. `send_ntfy` returns a falsy value when a
    send fails without raising -- an unreachable host, a parse failure, no topic configured.

    Auto-keying stamped the transition store on the ATTEMPT, so the failed page was
    remembered as delivered and the very next call was suppressed as a duplicate. The single
    notification an outage produces would have been lost silently. This is the 2026-07-18
    deadman incident exactly, and it was that incident's own R15 proof
    (test_deadmans_switch.py::test_run_cycle_failed_send_leaves_item_due_...) going red in the
    commit gate that caught it -- not this file, which was already green and wrong."""
    n, sent, _ = wired
    from background import ntfy_utils
    monkeypatch.setattr(ntfy_utils, "send_ntfy", lambda msg, **kw: sent.append(msg) or None)

    n.notify(FAIL_252, kind="real_alarm")
    n.notify(FAIL_252, kind="real_alarm")
    assert len(sent) == 2, "the retry after a failed send was suppressed as a duplicate"

    # Once a send is CONFIRMED, transition-only resumes and the third call is silent.
    monkeypatch.setattr(ntfy_utils, "send_ntfy", lambda msg, **kw: sent.append(msg) or "id-9")
    n.notify(FAIL_252, kind="real_alarm")
    assert len(sent) == 3
    n.notify(FAIL_252, kind="real_alarm")
    assert len(sent) == 3, "a confirmed send did not settle the alarm"


def test_an_explicitly_keyed_callers_semantics_are_untouched_by_delivery(wired, monkeypatch):
    """Commit-on-delivery is scoped to AUTO keys. Callers that key themselves already carry
    their own delivery bookkeeping, and changing when their transitions land would be a
    second, unasked-for change riding along with this one."""
    n, sent, _ = wired
    from background import ntfy_utils
    monkeypatch.setattr(ntfy_utils, "send_ntfy", lambda msg, **kw: sent.append(msg) or None)
    n.notify("x", kind="real_alarm", transition_key="explicit", state="S")
    n.notify("x", kind="real_alarm", transition_key="explicit", state="S")
    assert len(sent) == 1, "an explicitly-keyed caller's commit-on-attempt behaviour changed"


def test_MUTATION_an_hourly_re_ping_STOPS_once_the_condition_becomes_work(wired, monkeypatch):
    """The director's instruction is "escalate itself into the draw INSTEAD of re-telling me",
    and doing both is the noise with an extra step.

    MEASURED from the outbound mirror over 24h on 2026-08-20: after the escalation shipped, the
    dead-man's BLOCKED alarm still sent four times -- all hourly re-pings of one unchanged
    condition that had already been filed as work. It sets `re_escalate_after`, which predates
    there being any other channel to escalate INTO."""
    n, sent, staging = wired
    real_time = time.time
    for hour in range(0, 6):
        monkeypatch.setattr(time, "time", lambda h=hour: real_time() + h * 3600)
        n.notify(FAIL_252, kind="real_alarm", transition_key="dm", state="STUCK",
                 re_escalate_after=1800)
    assert len(sent) == 2, (
        f"the alarm paged {len(sent)} times over six hours. Expected TWO: the first page, one "
        "hourly re-ping, and then the third firing files the work item and goes quiet -- the "
        "same firing that escalates is the one that stops paging, which is the point. "
        f"Sent: {sent}"
    )
    assert list(staging.glob("*.md")), "it went quiet without filing anything -- that is worse"


def test_a_digest_is_not_auto_keyed(wired):
    """A digest IS the batch and re-sends by design; auto-keying it would suppress the
    periodic summary as a repeat of itself."""
    n, sent, _ = wired
    for _ in range(4):
        n.notify("Daily digest: 3 landings, 1 finding", kind="digest")
    assert len(sent) == 4


def test_an_explicit_transition_key_is_still_honoured(wired):
    """The auto-key is a DEFAULT, not a takeover: callers that already key themselves keep
    exactly the behaviour they had."""
    n, sent, _ = wired
    n.notify("state A", kind="real_alarm", transition_key="mine", state="A")
    n.notify("state A again, different words", kind="real_alarm", transition_key="mine", state="A")
    n.notify("now B", kind="real_alarm", transition_key="mine", state="B")
    assert len(sent) == 2, "the explicit key's own state, not the message text, must decide"


def test_MUTATION_a_quiet_gap_re_arms_an_auto_keyed_alarm(wired, monkeypatch):
    """R11's no-orphan-transitions rule applied to this store: a suppression whose release
    triggers nothing is a defect, and an auto-keyed alarm has no other release.

    THIS TEST CHANGED THE DESIGN. It was first written expecting a *recovery message* to
    re-arm the alarm, the way an explicitly-keyed one does. It failed, and it was right to:
    an auto-key derives its state from its own message, so "the condition cleared" is not
    expressible on that key, and the third repetition would have silenced that alarm
    permanently -- a page that is both silent AND has only one stale work item behind it.
    A quiet gap is the release EPISODE_GAP_SECONDS exists to provide."""
    n, sent, staging = wired
    for _ in range(5):
        n.notify(FAIL_252, kind="real_alarm")
    assert len(sent) == 1
    assert len(list(staging.glob("*.md"))) == 1

    # The condition goes away. Nothing announces that; there is simply silence.
    real_time = time.time
    monkeypatch.setattr(time, "time", lambda: real_time() + ar.EPISODE_GAP_SECONDS + 60)
    n.notify(FAIL_252, kind="real_alarm")   # ... and comes back tomorrow
    assert len(sent) == 2, (
        "a fault returning after a long silence was absorbed as repeat seven of the old "
        "episode -- the alarm had been permanently silenced"
    )


def test_MUTATION_a_SUSTAINED_outage_stays_ONE_episode(wired, monkeypatch):
    """The other side of the same threshold, and the one that matters at 4am. An outage that
    alarms every few minutes for hours must not tick over into a second episode and page
    again -- the gap has to be long relative to the producer's ~8-9 minute cycle."""
    n, sent, staging = wired
    real_time = time.time
    for minutes in range(0, 180, 9):        # three hours of failing runs, on cadence
        monkeypatch.setattr(time, "time", lambda m=minutes: real_time() + m * 60)
        n.notify(FAIL_252, kind="real_alarm")
    assert len(sent) == 1, f"a single sustained outage paged {len(sent)} times"
    assert len(list(staging.glob("*.md"))) == 1


def test_the_store_records_the_episode_not_just_the_last_state(wired):
    """The filed document quotes a repeat count and a window; both come from here, so the
    store has to carry them rather than the caller re-deriving them from a second source."""
    n, _sent, _ = wired
    for _ in range(4):
        n.notify(FAIL_252, kind="real_alarm")
    store = json.loads(n.TRANSITIONS_FILE.read_text())
    entry = next(v for k, v in store.items() if k.startswith("auto:"))
    assert entry["repeats"] == 4
    assert entry["escalated"] is True
    assert entry["first_ts"] <= entry["ts"]
