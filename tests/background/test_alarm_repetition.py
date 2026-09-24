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
import calendar
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
    assert "6 consecutive firing(s)" in body, "the caller's streak is the finding; state it"
    assert "net_margin_gbp" in body, "the diagnostic payload was dropped (R5)"
    assert "1.0h" in body, "the window the repeats covered is missing"
    assert "observed to hold on 1 separate day(s)" in body, (
        "the document must state what IT can establish, not only what the caller reported")


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


# ---------------------------------------------------------------------------
# ONE DOCUMENT PER SIGNATURE, NOT ONE PER SIGNATURE PER DAY (2026-08-24)
# ---------------------------------------------------------------------------

# UTC, deliberately: `escalate()` stamps dates with `datetime.fromtimestamp(..., timezone.utc)`,
# and `time.mktime` is LOCAL — on a BST machine it shifted every expected date by a day and the
# per-day idempotence test read as broken when it was the fixture that was wrong.
_DAY1 = calendar.timegm(time.strptime("2026-08-22", "%Y-%m-%d"))
_DAY2 = _DAY1 + 86_400
_DAY3 = _DAY1 + 2 * 86_400


def test_the_same_alarm_on_a_LATER_DAY_files_no_second_document(tmp_path):
    """THE DEFECT THIS FIXES, measured on the live tree 2026-08-24.

    Idempotence used to be keyed on a path containing the DATE, so an unchanged condition
    refiled itself every midnight. The staging root held NINE of these documents that
    morning -- three signatures on each of three days -- which was 15 of the 18 actionable
    items the tick's own draw prompt carried. The escalation built to stop a process
    re-creating a finding hourly was re-creating one daily.
    """
    first = ar.escalate(FAIL_252, key="k", repeats=3, first_ts=_DAY1, staging_dir=tmp_path,
                        now=_DAY1 + 60)
    assert first is not None

    second = ar.escalate(FAIL_252, key="k", repeats=40, first_ts=_DAY1,
                         staging_dir=tmp_path, now=_DAY2)
    third = ar.escalate(FAIL_252, key="k", repeats=90, first_ts=_DAY1,
                        staging_dir=tmp_path, now=_DAY3)
    assert second is None and third is None
    assert len(list(tmp_path.glob("WORKER_FINDING_REPEATING_ALARM_*.md"))) == 1


def test_the_continuing_condition_is_RECORDED_on_the_one_document(tmp_path):
    """Nothing is lost by not filing again -- the new fact is one line, not a new copy."""
    p = ar.escalate(FAIL_252, key="k", repeats=3, first_ts=_DAY1, staging_dir=tmp_path,
                    now=_DAY1 + 60)
    ar.escalate(FAIL_252, key="k", repeats=40, first_ts=_DAY1, staging_dir=tmp_path, now=_DAY2)
    ar.escalate(FAIL_252, key="k", repeats=90, first_ts=_DAY1, staging_dir=tmp_path, now=_DAY3)
    text = p.read_text(encoding="utf-8")
    assert "## Still live" in text
    assert "2026-08-23" in text and "2026-08-24" in text
    assert "90 consecutive firing(s)" in text, "the caller's latest streak is not recorded"


def test_MANY_calls_on_ONE_day_add_ONE_line(tmp_path):
    """The same defect at a finer grain: a tick that runs 48 times must not write 48 lines.

    COUNTS THE LINES, NOT THE DATE (2026-08-28). The assertion was `count("2026-08-23") == 1`,
    which was a proxy for "one still-live line" that held only while the document had one
    dated line-shape in it. It now has two -- the still-live note and the instance list the
    family collapse added, both of which carry the day they were first written -- so the
    proxy went red while the property it stood for was untouched. Counting each line-shape
    directly says what is meant and cannot be broken by a third dated line arriving later.
    """
    p = ar.escalate(FAIL_252, key="k", repeats=3, first_ts=_DAY1, staging_dir=tmp_path,
                    now=_DAY1 + 60)
    for i in range(20):
        ar.escalate(FAIL_252, key="k", repeats=10 + i, first_ts=_DAY1,
                    staging_dir=tmp_path, now=_DAY2 + i * 60)
    text = p.read_text(encoding="utf-8")
    assert text.count("— still live.") == 1
    assert text.count("(first seen ") == 1


def test_a_document_parked_in_IN_PROGRESS_still_suppresses_a_refile(tmp_path):
    """`in_progress/` is a live room, not an archive (CLAUDE.md: it is a BUILD queue).

    A finding someone has picked up and parked must not spawn a duplicate in the root while
    they are working on it.
    """
    p = ar.escalate(FAIL_252, key="k", repeats=3, first_ts=_DAY1, staging_dir=tmp_path,
                    now=_DAY1 + 60)
    parked = tmp_path / "in_progress"
    parked.mkdir()
    p.rename(parked / p.name)
    assert ar.escalate(FAIL_252, key="k", repeats=40, first_ts=_DAY1,
                       staging_dir=tmp_path, now=_DAY2) is None
    assert not list(tmp_path.glob("WORKER_FINDING_REPEATING_ALARM_*.md"))


def test_MUTATION_an_ARCHIVED_finding_does_NOT_suppress_a_new_episode(tmp_path):
    """THE NULL CONTROL, and the limb that stops this becoming a silencer.

    A condition that returns after being archived is a NEW episode and an R3 two-strike
    signal -- the fix did not hold. If `done/` were searched too, the second occurrence of a
    recurring fault would be swallowed for ever by a document someone closed weeks ago, and
    the suppression built to reduce noise would be deleting the one signal that matters.
    """
    p = ar.escalate(FAIL_252, key="k", repeats=3, first_ts=_DAY1, staging_dir=tmp_path,
                    now=_DAY1 + 60)
    done = tmp_path / "done"
    done.mkdir()
    p.rename(done / p.name)
    again = ar.escalate(FAIL_252, key="k", repeats=3, first_ts=_DAY2,
                        staging_dir=tmp_path, now=_DAY2 + 60)
    assert again is not None, "an archived finding must not suppress a fresh episode"
    assert again.exists()


def test_a_DIFFERENT_signature_still_files_its_own_document(tmp_path):
    """The suppression keys on the condition, not on 'a repeating-alarm finding exists'."""
    ar.escalate(FAIL_252, key="k1", repeats=3, first_ts=_DAY1, staging_dir=tmp_path,
                now=_DAY1 + 60)
    other = ar.escalate(OTHER_FAULT, key="k2", repeats=3, first_ts=_DAY2,
                        staging_dir=tmp_path, now=_DAY2)
    assert other is not None
    assert len(list(tmp_path.glob("WORKER_FINDING_REPEATING_ALARM_*.md"))) == 2


# ---------------------------------------------------------------------------
# UUIDs (2026-08-25) -- the variable that survived normalisation in pieces
# ---------------------------------------------------------------------------

def test_a_session_UUID_does_not_survive_normalisation_in_PIECES():
    """THE MEASURED DEFECT. `seat_continuity` put the dead session's id in its subject, and the
    staging root filled with EIGHTEEN copies of one alarm in nine hours -- SESSION_B_C_D_A_A_E,
    SESSION_F_E_EE_A_E, SESSION_C_C_A and fifteen more.

    A UUID is not caught by the git-hash rule: `{7,40}` eats its 8- and 12-character groups but
    its 4-character groups are too short, the trailing number rule then eats their digits, and
    the LETTERS come out the other side as a per-session fingerprint. So the de-duplicator saw
    eighteen distinct conditions where there was one, and `_slug`'s own docstring names exactly
    this outcome ("a fresh document per repetition") as the thing it exists to prevent.

    Truncated ids are included because that is what actually arrives: seat_continuity stored
    `session_id[:24]`, which cuts mid-group and leaves a trailing hyphen.
    """
    ids = [
        "c7e894aa-3221-45f7-8713-b1a18a6232a9",   # full
        "f0e2ee4a-e5b1-4c3d-9a2b-77c0d5e1a884",   # full, different
        "c7e894aa-3221-45f7-8713-",               # truncated at [:24]
        "f0e2ee4a-e5b1-4c3d-9a2b-",               # truncated, different
    ]
    slugs = {ar._slug(f"[SEAT] session {i} stopped mid-work") for i in ids}

    assert len(slugs) == 1, f"one condition produced {len(slugs)} filenames: {sorted(slugs)}"


def test_MUTATION_ORDINARY_hyphenated_words_are_NOT_eaten_by_the_UUID_rule():
    """The null half, and it is the one that decides whether the rule is safe to keep.

    A pattern loose enough to swallow `pre-commit-gate` or `test-driven-code` would blur alarms
    that differ only in which hyphenated thing failed -- the exact opposite defect, and a much
    quieter one. Three-plus hex-only groups is the line: real words are not hex.
    """
    keep = ["pre-commit-gate", "test-driven-code", "read-only-probe", "half-hourly-spine"]
    for word in keep:
        assert ar.normalise(word) == word, f"the UUID rule ate {word!r}"

    assert ar.alarm_signature("the pre-commit-gate refused") != \
        ar.alarm_signature("the test-driven-code refused")


def test_TWO_DIFFERENT_alarms_that_merely_both_quote_a_uuid_stay_apart():
    """Normalising the id must not merge two genuinely different conditions -- everything the
    alarm says ABOUT the id is preserved, which is the same contract a KeyError and a TypeError
    from one daemon already have."""
    a = "[SEAT] session c7e894aa-3221-45f7-8713 stopped mid-work"
    b = "[FORK] worker c7e894aa-3221-45f7-8713 never merged home"

    assert ar.alarm_signature(a) != ar.alarm_signature(b)


# ---------------------------------------------------------------------------
# THE FAMILY RULE (director, 2026-08-28: "twelve of them 'claimed and hasn't moved'")
# ---------------------------------------------------------------------------
#
# The real strings again, verbatim from docs/staging/ on the morning of 2026-08-28. Every one
# of these filed its OWN document under the pre-family rule, because what varies between them
# is PROSE -- a work-id, a directory list -- and `normalise()` only removes numbers. Sixteen
# documents for one condition and nine for another, all of them ahead of the director's own
# guidance in an alphabetically-ordered draw.

SEAT_CLAIMS = [
    ("[SEAT] land-the-ceiling-priced-half-the-book was claimed and has not moved for 1.7h",
     "seat-claim:the-ceiling-priced-half-the-book"),
    ("[SEAT] run-both-instruments-at-full-window was claimed and has not moved for 3.1h",
     "seat-claim:run-both-instruments-at-full-window"),
    ("[SEAT] reconcile-the-directors-red-census was claimed and has not moved for 2.4h",
     "seat-claim:reconcile-the-directors-red-census"),
]

UNCOMMITTED = [
    "[SEAT] docs, tests, the tree root, tools left uncommitted by a session that stopped "
    "mid-work holding 0 claim(s)",
    "[SEAT] company, docs, simulation, tests and elsewhere left uncommitted by a session that "
    "stopped mid-work holding 2 claim(s)",
    "[SEAT] docs, saas, simulation, tests and elsewhere left uncommitted by a session that "
    "stopped mid-work holding 1 claim(s)",
]


def test_the_family_is_the_declared_key_not_the_message():
    assert ar.family("seat-claim:land-the-widened-world") == "seat-claim"
    assert ar.family("seat-continuity") == "seat-continuity"
    assert ar.family("deadman_commit") == "deadman_commit"


def test_an_auto_key_is_its_own_whole_family():
    """An `auto:` key is the sha of the normalised message: it has no instance half, and
    splitting it would make every auto-keyed alarm in the machine one family called `auto`."""
    sig = ar.alarm_signature(FAIL_252)
    assert ar.family(sig) == sig
    assert ar.family(sig) != "auto"


def test_SIXTEEN_stale_claims_file_ONE_document(tmp_path):
    """The director's twelve, driven with the real strings."""
    for message, key in SEAT_CLAIMS:
        ar.escalate(message, key=key, repeats=1, first_ts=_DAY1, staging_dir=tmp_path,
                    now=_DAY1 + 60)
    filed = sorted(tmp_path.glob("WORKER_FINDING_REPEATING_ALARM_*.md"))
    assert len(filed) == 1, [p.name for p in filed]


def test_the_collapse_KEEPS_every_work_id(tmp_path):
    """A collapse that loses the work-ids is not a fix, it is a deletion with a rationale.
    Each instance must be nameable from the one surviving document."""
    # POPULATION FLOOR, before the loop. Every assertion below is INSIDE a loop over
    # `SEAT_CLAIMS`, so an empty or shrunken fixture would pass this test while proving
    # nothing -- the exact shape `tests/architecture/test_no_tree_scan_passes_on_an_empty_population.py`
    # exists to catch, and it caught this one. The count is the sixteen work-ids the
    # 2026-08-28 collapse had to keep; if the fixture legitimately changes, change the
    # number deliberately rather than letting the guard empty.
    assert len(SEAT_CLAIMS) >= 3, (
        "the seat-claim fixture is {} row(s). Three distinct work-ids is the minimum that can "
        "show a collapse KEEPING them all -- one proves nothing about collapsing and two cannot "
        "distinguish 'kept both' from 'kept the last'. An empty or thinned fixture passes every "
        "assertion below without checking anything".format(len(SEAT_CLAIMS)))
    for message, key in SEAT_CLAIMS:
        ar.escalate(message, key=key, repeats=1, first_ts=_DAY1, staging_dir=tmp_path,
                    now=_DAY1 + 60)
    text = sorted(tmp_path.glob("*.md"))[0].read_text(encoding="utf-8")
    for _, key in SEAT_CLAIMS:
        assert f"- `{key.split(':', 1)[1]}` (" in text


def test_an_instance_is_listed_ONCE_however_often_it_fires(tmp_path):
    """The pile rebuilt inside one file is the same defect at a finer grain."""
    message, key = SEAT_CLAIMS[0]
    for i in range(12):
        ar.escalate(message, key=key, repeats=1 + i, first_ts=_DAY1, staging_dir=tmp_path,
                    now=_DAY1 + 60 + i * 3600)
    text = sorted(tmp_path.glob("*.md"))[0].read_text(encoding="utf-8")
    assert text.count("- `the-ceiling-priced-half-the-book` (") == 1


def test_NINE_uncommitted_seats_file_ONE_document(tmp_path):
    """`seat_continuity` always passed a stable key; the varying DIRECTORY LIST in its message
    is what produced nine documents, and the key is what fixes it."""
    for message in UNCOMMITTED:
        ar.escalate(message, key="seat-continuity", repeats=1, first_ts=_DAY1,
                    staging_dir=tmp_path, now=_DAY1 + 60)
    filed = sorted(tmp_path.glob("WORKER_FINDING_REPEATING_ALARM_*.md"))
    assert len(filed) == 1, [p.name for p in filed]


def test_TWO_FAMILIES_STAY_TWO_DOCUMENTS(tmp_path):
    """THE MUTATION THAT MATTERS. Every test above rewards collapsing harder, and the failure
    this module exists to prevent is over-collapsing -- two different conditions folded into
    one, the second silently absorbed by the first's document and never converged on. Stale
    claims and a dead session are two conditions; they must stay two."""
    ar.escalate(SEAT_CLAIMS[0][0], key=SEAT_CLAIMS[0][1], repeats=1, first_ts=_DAY1,
                staging_dir=tmp_path, now=_DAY1 + 60)
    ar.escalate(UNCOMMITTED[0], key="seat-continuity", repeats=1, first_ts=_DAY1,
                staging_dir=tmp_path, now=_DAY1 + 60)
    assert len(sorted(tmp_path.glob("WORKER_FINDING_REPEATING_ALARM_*.md"))) == 2


def test_a_document_named_the_OLD_way_is_still_found(tmp_path):
    """Twenty-eight documents already carried slug names when the family rule landed. A lookup
    that only knew the new stem would have filed a twenty-ninth beside them on the first
    firing -- the defect reintroduced by its own fix."""
    message, key = SEAT_CLAIMS[0]
    old = tmp_path / f"WORKER_FINDING_REPEATING_ALARM_{ar._slug(message)}_2026-08-22.md"
    old.write_text("**Severity:** LATENT · **Lane:** H_harness\n\n# old shape\n",
                   encoding="utf-8")
    assert ar.escalate(message, key=key, repeats=3, first_ts=_DAY1, staging_dir=tmp_path,
                       now=_DAY1 + 60) is None
    assert len(sorted(tmp_path.glob("WORKER_FINDING_REPEATING_ALARM_*.md"))) == 1


def test_still_live_and_instance_lines_land_under_their_OWN_headings(tmp_path):
    """Both note-writers appended to end-of-file, which was correct while there was one
    section. With two, end-of-file filing puts every still-live line under `Instances seen`."""
    message, key = SEAT_CLAIMS[0]
    ar.escalate(message, key=key, repeats=3, first_ts=_DAY1, staging_dir=tmp_path,
                now=_DAY1 + 60)
    ar.escalate(SEAT_CLAIMS[1][0], key=SEAT_CLAIMS[1][1], repeats=9, first_ts=_DAY1,
                staging_dir=tmp_path, now=_DAY2)
    text = sorted(tmp_path.glob("*.md"))[0].read_text(encoding="utf-8")
    live_at = text.index("## Still live")
    inst_at = text.index(ar.INSTANCES_HEADING)
    assert live_at < inst_at
    assert text.index("— still live.") < inst_at, "a still-live line filed under Instances"


# =============================================================================================
# THE COUNTS THE DOCUMENT DERIVES FROM ITSELF (2026-09-24)
# =============================================================================================
# THE DEFECT, MEASURED, in two halves that turned out to be one.
#
# Half one (finding `612bd9ffe`): four call sites reach `escalate()` directly, `repeats` was
# REQUIRED, so all four passed the literal `1`. `SEAT_CONTINUITY` opened with "fired **1 times
# without its state changing**" above eight days of still-live lines and twenty-three members;
# `DELIVERY_LANE_STRANDED` carried four consecutive days of "1 repeats over 1.7h", identical
# because a frozen constant measures nothing.
#
# Half two (measured while fixing half one, pre-registered in
# `docs/staging/records/SEAT_PREREG_WHETHER_THE_FROZEN_HEADER_IS_THREE_FAMILIES_OR_THE_WHOLE_
# POPULATION_2026-09-24.md` and partly refuted there): the header was stamped at birth for EVERYONE, so
# `STRETCH_LOG` led with "fired **3 times**" above a line reading 2132. Four of the seven live
# documents carrying still-live lines understated themselves in their own first sentence.
#
# So the mutation that matters here is a COUNT THAT DOES NOT MOVE. Every control below is keyed
# to the header CHANGING as the document accrues evidence -- the property -- rather than to any
# number it happens to show today, because a control pinned to today's answer goes red when the
# code becomes more honest and stays green when the claim rots.


def _fire_on_days(tmp_path, *, key_for, message_for, days, repeats=None):
    """Fire one family on `days` consecutive days, one new member each day. Returns the doc.

    OMITS `repeats` ENTIRELY when there is none, rather than passing `repeats=None`. Those are
    different calls and only one of them is what the four direct call sites make. Caught by a
    mutation that went GREEN: setting the default back to `1` passed every test here, because
    every test was naming the argument and nothing exercised the default at all.
    """
    extra = {} if repeats is None else {"repeats": repeats}
    for i in range(days):
        ar.escalate(message_for(i), key=key_for(i), first_ts=_DAY1,
                    staging_dir=tmp_path, now=_DAY1 + i * 86_400 + 60, **extra)
    return sorted(tmp_path.glob("WORKER_FINDING_REPEATING_ALARM_*.md"))[0]


def test_MUTATION_the_HEADER_COUNT_MOVES_as_the_document_accrues_evidence(tmp_path):
    """THE DEFECT ITSELF. Eight days of evidence under a header that says one.

    Keyed to the property -- the header must equal what the test CAUSED (eight distinct days,
    eight distinct members) -- and not to the string the current code emits on day one. Stamping
    the header at birth again, from any source, fails this on both numbers.
    """
    doc = _fire_on_days(tmp_path, days=8,
                        key_for=lambda i: f"seat-claim:work-{i}",
                        message_for=lambda i: f"[SEAT] work-{i} was claimed and has not moved")
    body = doc.read_text(encoding="utf-8")
    head = body[body.index(ar.COUNTS_BEGIN):body.index(ar.COUNTS_END)]
    assert "8 separate day(s)" in head, f"the header did not age with the document:\n{head}"
    assert "8 member(s)" in head, f"the header lost members of its own family:\n{head}"
    assert head.count("day(s)") == 1, "two counts in one header is two places for them to rot"


def test_MUTATION_the_header_is_REWRITTEN_not_APPENDED(tmp_path):
    """The obvious wrong fix: append a fresh count each firing and leave the stale one above it.

    A document with two headers is worse than one with a stale header, because now a reader has
    to decide which to believe and the first one they meet is the wrong one.
    """
    doc = _fire_on_days(tmp_path, days=6, repeats=3,
                        key_for=lambda i: "deadman-worktree",
                        message_for=lambda i: f"worktree undeclared after {i}s")
    body = doc.read_text(encoding="utf-8")
    assert body.count(ar.COUNTS_BEGIN) == 1 and body.count(ar.COUNTS_END) == 1
    assert body.count("**Filed automatically by ") == 1, "a second header was grown beside the first"


def test_MUTATION_a_caller_that_measures_NO_streak_never_has_one_INVENTED_for_it(tmp_path):
    """`repeats` is the CALLER'S quantity and a direct caller cannot know it. An honest absence
    with a named reason is worth more than a `1`, because the `1` is read as established.

    Also asserts the threshold is named as NOT APPLIED. The old line read "Repeats before
    escalation: 1 (threshold `ESCALATE_AFTER_REPEATS`)" -- a number BELOW the bar, printed next
    to the bar, as though the bar had been cleared.
    """
    doc = _fire_on_days(tmp_path, days=3,
                        key_for=lambda i: f"seat-claim:work-{i}",
                        message_for=lambda i: f"[SEAT] work-{i} was claimed and has not moved")
    body = doc.read_text(encoding="utf-8")
    assert "consecutive firing(s)" not in body, "a streak was reported for a caller that has none"
    assert "not measured" in body and "was never applied" in body, (
        "the absence must be STATED, with its reason, not left to look like a zero")
    assert f"= {ar.ESCALATE_AFTER_REPEATS}" in body, "the bar that did not apply is not named"
    # And the document still says what it CAN establish -- an absence is not an excuse for silence.
    assert "3 separate day(s)" in body and "3 member(s)" in body


def test_MUTATION_a_caller_that_DOES_measure_a_streak_gets_its_LATEST_one_not_its_FIRST(tmp_path):
    """The other half of the partition, and the one the refuted pre-registration was about.

    `notify()` families were not spared: their header held the birth streak forever. This fires
    a growing streak and asserts the header carries the last, not the first.
    """
    for n, day in ((3, _DAY1), (298, _DAY1 + 5 * 86_400)):
        ar.escalate(f"worktree undeclared after {n}s", key="deadman-worktree", repeats=n,
                    first_ts=_DAY1, staging_dir=tmp_path, now=day + 60)
    body = sorted(tmp_path.glob("*.md"))[0].read_text(encoding="utf-8")
    head = body[body.index(ar.COUNTS_BEGIN):body.index(ar.COUNTS_END)]
    assert "298 consecutive firing(s)" in head, f"the header froze at the first streak:\n{head}"
    assert "3 consecutive firing(s)" not in head


def test_MUTATION_the_counts_block_IS_NOT_READ_BACK_AS_AN_OBSERVATION(tmp_path):
    """A control reading its own output agrees with itself. This one must not.

    The block prints dates -- the first and last observation. If `_observation_dates` ever
    matched them, a refresh would be an observation, the document would look freshly observed
    every time anything touched it, and `reask()` could never clear anything again. Refreshing
    at a far-future `now` must move NEITHER the day count NOR `last_observed`.
    """
    doc = _fire_on_days(tmp_path, days=3,
                        key_for=lambda i: f"seat-claim:work-{i}",
                        message_for=lambda i: f"[SEAT] work-{i} was claimed and has not moved")
    before = (ar.document_counts(doc), ar.last_observed(doc))
    for i in range(5):
        ar._refresh_counts(doc, key="seat-claim:work-0", repeats=None,
                           first_ts=_DAY1, now=_DAY1 + (90 + i) * 86_400)
    assert (ar.document_counts(doc), ar.last_observed(doc)) == before, (
        "refreshing the header aged the document, so the re-ask can never clear it")


def test_the_THREE_PLACEMENTS_of_the_counts_block_are_ALL_REACHABLE(tmp_path):
    """One control over the whole partition, not a leg each.

    `_refresh_counts` places the block three ways -- between existing markers, over the LEGACY
    fixed paragraph, and after the title when there is neither. A placer that refused everything
    would pass a leg-per-branch suite; asserting all three land, with distinct starting shapes,
    cannot be passed by refusing.
    """
    legacy = (
        "**Severity:** LATENT · **Lane:** H_harness\n\n"
        "# [SEAT] something was claimed and has not moved\n\n"
        "**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has\n"
        "fired **1 times without its state changing**, over **95.9h**. Under the\n"
        "director's instruction of 2026-08-20 a repeating alert escalates itself into the draw.\n\n"
        "## Still live\n"
        "- **2026-09-16** — still live. The condition was observed to hold again today.\n\n"
        "## Instances seen\n"
        "- `alpha` (first seen 2026-09-15)\n")
    bare = legacy.replace(legacy[legacy.index("**Filed"):legacy.index("## Still live")], "")

    shapes = {}
    for name, text in (("legacy", legacy), ("bare", bare)):
        p = tmp_path / f"WORKER_FINDING_REPEATING_ALARM_{name.upper()}_2026-09-15.md"
        p.write_text(text, encoding="utf-8")
        assert ar._refresh_counts(p, key="seat-continuity", repeats=None, first_ts=_DAY1,
                                  now=_DAY1), f"{name} was refused"
        shapes[name] = p.read_text(encoding="utf-8")
        # SECOND pass: now the markers exist, so this is the third placement.
        assert ar._refresh_counts(p, key="seat-continuity", repeats=None, first_ts=_DAY1,
                                  now=_DAY1), f"{name} was refused on its second pass"
        shapes[name + "-again"] = p.read_text(encoding="utf-8")

    for name, body in shapes.items():
        assert body.count(ar.COUNTS_BEGIN) == 1, f"{name}: {body.count(ar.COUNTS_BEGIN)} blocks"
        assert "2 separate day(s)" in body, f"{name} did not count its own two dated lines"
        assert "1 member(s)" in body, f"{name} did not count its own instance"
    assert "fired **1 times" not in shapes["legacy"], "the frozen paragraph survived the repair"
    assert shapes["legacy"] == shapes["legacy-again"], "the repair is not idempotent"
    assert shapes["bare"] == shapes["bare-again"]


def test_the_FOUR_DIRECT_CALL_SITES_PASS_NO_REPETITION_COUNT():
    """The control that stops the literal coming back, on the real call sites.

    BOTH LEGS, because an offender census with an empty result is green whether the pattern is
    right or the population is empty. The first leg asserts the call sites are still FOUND -- if
    a refactor moves them this goes red rather than silently passing on nothing.
    """
    import re as _re
    from pathlib import Path
    root = Path(ar.__file__).resolve().parent
    calls, offenders = 0, []
    for name in ("seat_continuity.py", "seat_work_in_hand.py", "delivery_lane.py"):
        src = (root / name).read_text(encoding="utf-8")
        for m in _re.finditer(r"alarm_repetition\.escalate\((.*?)\n\s*\)", src, _re.S):
            calls += 1
            if "repeats=" in m.group(1):
                offenders.append(f"{name}: {m.group(1).strip()[:80]}")
    assert calls >= 4, f"only {calls} direct escalate() call sites found; the census is blind"
    assert not offenders, (
        "a direct caller cannot know a consecutive-firing count and must not invent one: "
        + "; ".join(offenders))


# =============================================================================================
# THE RE-ASK (director direction, Lane 0, 2026-09-23)
# =============================================================================================
# Everything above this line is driven by an alarm FIRING. The re-ask is the only thing in this
# module driven by an alarm NOT firing, and that inverts which mutation matters. For escalation the
# dangerous direction is silencing a page; here it is ARCHIVING A LIVE CONDITION -- removing a work
# item from the director's queue because nobody happened to annotate it, which loses the finding
# and leaves no trace that it was lost.
#
# The fixture documents are all written by `escalate()` itself rather than hand-typed. That is
# load-bearing: the re-ask parses the lines `_note_still_live` and `_note_instance` produce, so a
# hand-typed fixture would let the parser and the writer drift apart and every test here would keep
# passing while the real documents stopped being readable.

_REASK_TODAY = calendar.timegm(time.strptime("2026-09-23", "%Y-%m-%d")) + 12 * 3600
_LONG_AGO = _REASK_TODAY - 30 * 86_400


def _file_alarm(staging_dir, *, key, message, when):
    """One alarm document, filed by the production filing path at `when`."""
    return ar.escalate(message, key=key, repeats=3, first_ts=when - 600,
                       staging_dir=staging_dir, now=when)


def _point_transitions_at(monkeypatch, tmp_path, payload):
    """Make the re-ask read a REAL transition store file through its REAL reader.

    Injecting a dict into `reask()` would have been shorter and would have proved the injection:
    `_read_transitions_for_reask` does a late import of `notify.TRANSITIONS_FILE` precisely because
    `notify` imports this module, and that late import is the part most likely to break.
    """
    from background import notify
    store = tmp_path / ".notify_transitions.json"
    store.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(notify, "TRANSITIONS_FILE", store)
    return store


def _population(tmp_path, monkeypatch, *, transitions=None):
    """One room holding all three answers at once, so the partition can be asserted whole."""
    _point_transitions_at(monkeypatch, tmp_path, transitions or {})
    room = tmp_path / "staging"
    room.mkdir()
    _file_alarm(room, key="still-burning", message="[X] the thing is still on fire",
                when=_REASK_TODAY)
    _file_alarm(room, key="long-quiet", message="[X] the thing was on fire a month ago",
                when=_LONG_AGO)
    # No signature line, no date in the filename: nothing to date the silence from.
    (room / f"{ar.ALARM_DOCUMENT_STEM}NO_DATE_IN_THIS_NAME.md").write_text(
        "**Severity:** LATENT\n\n# an alarm document with nothing datable in it\n", encoding="utf-8")
    return room


def test_the_re_ask_reaches_ALL_THREE_VERDICTS_and_they_are_DISTINCT(tmp_path, monkeypatch):
    """THE PARTITION, as one control over the whole thing rather than a leg per branch.

    A re-ask that returned `still_holds` for everything would satisfy every individual "does it
    hold this one correctly" assertion below, and would be the whole mechanism not working: the
    defect it exists to fix is documents that sit unchanged forever. Equally, a re-ask that could
    only ever say `cannot_tell` refuses everything and passes every safety leg. So the reachability
    of all three, and their being three rather than two shapes sharing a name, is asserted FIRST
    and in one place -- CLAUDE.md's "assert it CAN be taken before asserting what it does".
    """
    results = ar.reask(staging_dir=_population(tmp_path, monkeypatch), now=_REASK_TODAY)
    assert len(results) == 3, [r.path.name for r in results]
    by_verdict = {r.verdict: r for r in results}
    assert set(by_verdict) == set(ar.REASK_VERDICTS), (
        "the re-ask returned {} over a population built to produce all three. A verdict that "
        "cannot be reached is a branch no test below is really testing".format(sorted(by_verdict)))
    # DISTINCTNESS, not just three names: three verdicts over three documents is blind to two
    # documents collapsing onto one verdict while a third name goes unused.
    assert len({r.path.name for r in results}) == 3
    # And each verdict must say WHY. A verdict with an empty reason is the unrankable document
    # the whole direction was about, wearing a machine's clothes.
    assert all(len(r.reason) > 20 for r in results), [(r.verdict, r.reason) for r in results]


def test_a_CLEARED_condition_ARCHIVES_ITSELF_CARRYING_THE_EVIDENCE(tmp_path, monkeypatch):
    """The director's words: *"archives itself WITH the evidence it re-ran"*.

    Both halves are the test. An archival that moved the file and said nothing would leave a reader
    in `done/` unable to tell a diagnosed disposition from a machine's guess -- and this project
    has already paid for archival moves whose diff read as content-neutral and were not.
    """
    room = _population(tmp_path, monkeypatch)
    cleared = [r for r in ar.reask(staging_dir=room, now=_REASK_TODAY)
               if r.verdict == ar.CLEARED]
    assert len(cleared) == 1, [(r.verdict, r.path.name) for r in cleared]
    original = cleared[0].path

    applied = [r for r in ar.reask(staging_dir=room, now=_REASK_TODAY, apply=True)
               if r.verdict == ar.CLEARED]
    assert applied[0].applied is True
    assert not original.exists(), "the cleared document is still in the queue"
    archived = room / ar.ARCHIVE_ROOM / original.name
    assert archived.exists(), sorted(p.name for p in (room / ar.ARCHIVE_ROOM).glob("*"))
    text = archived.read_text(encoding="utf-8")
    assert "## Re-asked and cleared, 2026-09-23" in text
    assert "**Last observation:**" in text
    assert "long-quiet" in text, "the archived document does not name the condition it re-asked"
    # THE EVIDENCE MUST NOT OVERCLAIM. Nothing diagnosed this; saying so is what stops the next
    # reader treating an archived guess as a resolved fault.
    assert "What this does NOT claim" in text


def test_a_STILL_HOLDING_condition_GAINS_A_LINE_rather_than_SITTING_UNCHANGED(tmp_path, monkeypatch):
    """The other half of the direction, and the half that makes the queue rankable.

    THE DEFECT: before this, a document that was re-checked and found still burning was
    byte-identical to one nobody had looked at since it was filed. Nine of them sat at ORDER 60
    with no reading that could separate them.
    """
    room = _population(tmp_path, monkeypatch)
    live = [r for r in ar.reask(staging_dir=room, now=_REASK_TODAY)
            if r.verdict == ar.STILL_HOLDS][0]
    before = live.path.read_text(encoding="utf-8")
    ar.reask(staging_dir=room, now=_REASK_TODAY, apply=True)
    after = live.path.read_text(encoding="utf-8")
    assert after != before, "a re-asked document is unchanged, which is the defect itself"
    assert ar.REASK_HEADING in after
    assert f"- **2026-09-23** — re-asked: **{ar.STILL_HOLDS}**." in after
    assert live.path.exists(), "a still-holding condition must NEVER be archived"


def test_the_re_ask_DOES_NOT_READ_ITS_OWN_LINES_AS_AN_OBSERVATION(tmp_path, monkeypatch):
    """THE TAUTOLOGY THIS MECHANISM IS ONE LINE AWAY FROM, and the mutation that matters most.

    The re-ask stamps a dated line. `last_observed()` reads dated lines. If it read the re-ask's
    own line, the FIRST re-ask would refresh every document's apparent age and nothing could ever
    clear again -- a control reading its own output and agreeing with itself, green forever while
    the queue silted up exactly as before.

    MUTATION RESULT, RECORDED BECAUSE IT DID NOT FIRE: `_without_reask_section` -> `return text`
    leaves THIS leg green, and that is an EQUIVALENCE rather than a gap. Established, not assumed:
    the re-ask writes `- **<date>** — re-asked: ...`, and both observation patterns are narrower
    than that -- `_STILL_LIVE_DATE` requires the literal `— still live.` and `_INSTANCE_DATE`
    requires a backticked name followed by `(first seen <date>)`. Neither can match a re-ask line,
    so on today's line format the section-exclusion is defence in depth and not the thing holding
    this up. `test_MUTATION_a_STILL_LIVE_SHAPED_LINE_under_the_re_ask_heading...` below is the leg
    that makes it load-bearing, and it is the one that reds under that mutation.
    """
    # A room where the machinery is QUIET, so the stale document lands on `cannot_tell` and is
    # ANNOTATED rather than archived -- the only verdict that leaves a re-ask line on a document
    # the next pass must still judge stale.
    _point_transitions_at(monkeypatch, tmp_path, {})
    room = tmp_path / "staging"
    room.mkdir()
    doc = _file_alarm(room, key="long-quiet", message="[X] quiet for a month", when=_LONG_AGO)

    first = ar.reask(staging_dir=room, now=_REASK_TODAY, apply=True)
    assert [r.verdict for r in first] == [ar.CANNOT_TELL], [r.reason for r in first]
    assert f"- **2026-09-23** — re-asked: **{ar.CANNOT_TELL}**." in doc.read_text(encoding="utf-8")

    # The line is now in the document, dated TODAY. The condition was still last observed a month
    # ago and the verdict must not have moved.
    assert ar.last_observed(doc) == "2026-08-24", (
        "the re-ask's own line is being read as an observation of the condition")
    again = ar.reask(staging_dir=room, now=_REASK_TODAY)
    assert [r.verdict for r in again] == [ar.CANNOT_TELL]


def test_SILENT_OBSERVERS_ARE_CANNOT_TELL_AND_NEVER_CLEARED(tmp_path, monkeypatch):
    """FAIL CLOSED, in the one situation where failing open destroys the most.

    If every observer is down -- a frozen WSL2 guest, a dead supervisor -- then no document gains a
    line, every document looks quiet, and a re-ask that read quiet as cleared would archive THE
    ENTIRE QUEUE at exactly the moment the queue mattered most. Nothing else in this module can
    catch that: each document, judged alone, looks exactly like a genuine clear.
    """
    _point_transitions_at(monkeypatch, tmp_path, {})
    room = tmp_path / "staging"
    room.mkdir()
    for n in range(3):
        _file_alarm(room, key=f"quiet-{n}", message=f"[X] condition {n} went quiet",
                    when=_LONG_AGO - n * 86_400)
    results = ar.reask(staging_dir=room, now=_REASK_TODAY, apply=True)
    assert len(results) == 3
    assert {r.verdict for r in results} == {ar.CANNOT_TELL}, [(r.verdict, r.reason) for r in results]
    assert all(r.path.exists() for r in results), "a queue was archived on the observers' silence"
    # And it must SAY so on the surface, not in a footnote: "we cannot tell" is a result.
    assert all("evidence about the observers" in r.reason for r in results)


def test_A_FIRING_IN_THE_STORE_CONTRADICTS_A_STALE_LOOKING_DOCUMENT(tmp_path, monkeypatch):
    """The store's one permitted use, and the direction is the whole point.

    MEASURED, 2026-09-23: `deadman_origin_fork` had a still-live line stamped 1.5h earlier and was
    ABSENT from `.notify_transitions.json`, because `deadmans_switch` calls `clear_transition()`
    (which DELETES the key) every time the fork closes and the condition oscillates. So absence in
    that store is a snapshot of an oscillating condition, NOT a clear -- the first draft of this
    re-ask read it as one and would have archived a condition that fired the same afternoon.
    A firing may therefore OVERRULE a stale document; an absence may never clear one.
    """
    room = _population(tmp_path, monkeypatch, transitions={
        "long-quiet:an-instance": {"state": "x", "ts": _REASK_TODAY - 3600,
                                   "last_seen": _REASK_TODAY - 3600},
    })
    results = {r.family: r for r in ar.reask(staging_dir=room, now=_REASK_TODAY)}
    assert results["long-quiet"].verdict == ar.STILL_HOLDS, results["long-quiet"].reason
    assert "contradicts the silence" in results["long-quiet"].reason
    assert ar.CLEARED not in {r.verdict for r in results.values()}


def test_MUTATION_an_ABSENT_key_ALONE_never_clears_a_RECENTLY_OBSERVED_document(tmp_path, monkeypatch):
    """The inverse of the leg above, keyed to the PROPERTY and not to today's answer.

    The population that made this concrete: FOUR of the ten live alarm families have no key in the
    transition store at all, and only one of the four is absent because anything cleared. Three of
    them -- `seat-continuity`, `seat-claim:*`, `delivery-lane-stranded:*` -- call `escalate()`
    directly and have never written that store in their lives. A store-keyed re-ask would have
    archived three live conditions out of ten, in the fail-open direction.
    """
    room = _population(tmp_path, monkeypatch, transitions={})
    live = [r for r in ar.reask(staging_dir=room, now=_REASK_TODAY)
            if r.family == "still-burning"]
    assert len(live) == 1
    assert live[0].verdict == ar.STILL_HOLDS
    assert ar._family_last_seen("still-burning", {}) is None, (
        "the fixture no longer exercises the absent-key path this test is about")


def test_an_archival_NEVER_OVERWRITES_AN_EARLIER_EPISODE_in_done(tmp_path, monkeypatch):
    """A file already in `done/` under this name is a PREVIOUS episode of the same family.

    Clobbering it would destroy the only record that this condition has returned before, which is
    the R3 two-strike signal the no-searching-`done/` rule exists to preserve -- and it would do it
    inside a diff that reads as a routine archival.
    """
    room = _population(tmp_path, monkeypatch)
    cleared = [r for r in ar.reask(staging_dir=room, now=_REASK_TODAY)
               if r.verdict == ar.CLEARED][0]
    earlier = room / ar.ARCHIVE_ROOM / cleared.path.name
    earlier.parent.mkdir(parents=True, exist_ok=True)
    earlier.write_text("AN EARLIER EPISODE, ARCHIVED BY A PERSON\n", encoding="utf-8")

    ar.reask(staging_dir=room, now=_REASK_TODAY, apply=True)
    assert earlier.read_text(encoding="utf-8") == "AN EARLIER EPISODE, ARCHIVED BY A PERSON\n"
    siblings = sorted(p.name for p in (room / ar.ARCHIVE_ROOM).glob("*.md"))
    assert len(siblings) == 2, siblings
    assert any("_REASK_2" in n for n in siblings), siblings


def test_the_re_ask_line_is_IDEMPOTENT_PER_DAY(tmp_path, monkeypatch):
    """Forty-eight ticks must not turn one document into forty-eight lines -- the collapsed pile
    rebuilt inside one file, which is the defect `_note_still_live` learned the same way."""
    room = _population(tmp_path, monkeypatch)
    for _ in range(5):
        ar.reask(staging_dir=room, now=_REASK_TODAY, apply=True)
    live = next(p for p in room.glob("*STILL*.md"))
    text = live.read_text(encoding="utf-8")
    assert text.count(f"- **2026-09-23** — re-asked: **{ar.STILL_HOLDS}**.") == 1, text


def test_A_TEST_RUN_CANNOT_ARCHIVE_THE_DIRECTORS_REAL_QUEUE(tmp_path, monkeypatch):
    """The same hard guard `escalate()` carries, for a sharper reason: escalate can only ADD a
    document to his queue and this can REMOVE one. Five real findings once appeared in
    `docs/staging/` from a test run quoting a fixture filename; the removing version of that
    accident would be silent."""
    assert ar.reask() == [], (
        "reask() reached the REAL docs/staging under pytest. It may archive documents, so an "
        "unguarded call is a test run deleting the director's work queue")


def test_MUTATION_a_STILL_LIVE_SHAPED_LINE_under_the_re_ask_heading_is_NOT_an_observation(
        tmp_path, monkeypatch):
    """What `_without_reask_section` is actually for, and the case that makes it load-bearing.

    The re-ask's OWN line shape cannot be mistaken for an observation -- see the equivalence
    recorded on the test above. The hole the section-exclusion really closes is a line in the
    observation SHAPE appearing under the re-ask heading, which is not hypothetical: these
    documents are hand-annotated (`DEADMAN_ORIGIN_FORK` carries a prose note a seat wrote), the
    still-live shape is the most copy-pasteable line in the file, and `_append_under` will happily
    put a line under whichever heading it is handed.

    If that line counted, a single mis-filed annotation would freeze one document as permanently
    live -- and the reader would have no way to see why, because the line says "still live" and
    that is exactly what the verdict would then say too.
    """
    _point_transitions_at(monkeypatch, tmp_path, {})
    room = tmp_path / "staging"
    room.mkdir()
    doc = _file_alarm(room, key="long-quiet", message="[X] quiet for a month", when=_LONG_AGO)
    doc.write_text(ar._append_under(
        doc.read_text(encoding="utf-8"), ar.REASK_HEADING,
        "- **2026-09-23** — still live. 3 repeats over 0.1h without the state changing."),
        encoding="utf-8")

    assert "still live" in doc.read_text(encoding="utf-8").split(ar.REASK_HEADING)[1], (
        "the fixture did not land the line under the re-ask heading, so this proves nothing")
    assert ar.last_observed(doc) == "2026-08-24", (
        "a still-live-shaped line under the RE-ASK heading is being counted as an observation of "
        "the condition, so anything written there freezes the document as permanently live")


def test_THE_CHAIN_the_staging_watcher_LOOP_actually_REACHES_the_re_ask():
    """A mechanism with a CLI and no caller is the consumed-not-absorbed shape.

    Every control above this one drives `reask()` directly, and all of them stay green forever if
    nothing in production ever calls it -- this project's own rule, learned the expensive way: a
    control on a rule proves nothing until the CHAIN to a production caller is controlled too.

    The loop it must be in is `staging_watcher.main()`, which is an infinite `while True`, so this
    asserts over the loop's SOURCE rather than by running it. That is a weaker instrument than
    executing the call and this test says so rather than implying otherwise -- but it is not
    vacuous: it fails if the call is deleted, if it is moved out of the loop body into
    module scope or a helper nothing calls, or if `apply=True` is dropped so the re-ask decides
    everything and writes nothing.
    """
    import inspect

    from background import staging_watcher

    src = inspect.getsource(staging_watcher.main)
    assert "alarm_repetition.reask(apply=True)" in src, (
        "staging_watcher.main() no longer calls the re-ask. Every other control in this file "
        "drives reask() directly and would stay green with nothing in production reaching it")
    # INSIDE the loop, not before it. A call above `while True` runs once at boot and then never
    # again, which for a mechanism whose whole subject is the passage of time is the same as absent.
    assert "while True" in src and src.index("while True") < src.index("alarm_repetition.reask"), (
        "the re-ask call is outside the watcher's loop, so it would run once at boot only")
    # And it must be guarded like its neighbours: staging hygiene may never take the watcher down.
    tail = src[src.index("alarm_repetition.reask"):]
    assert "except Exception" in tail[:600], (
        "the re-ask call is unguarded; a staging-hygiene failure would stop the watcher")
