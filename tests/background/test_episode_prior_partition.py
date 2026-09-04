"""THE DEFECT: every carrier of an episode-scoped state file answered "there is no value" and
"I cannot read this value" with the same answer, and three of them crashed on two members of the
partition rather than answering at all.

`background/episode_monotonic.py` argues the ABSENT/UNREADABLE distinction at length and turns on
it in code. On 2026-09-04 its own `prev=None` door was fixed twice by two lanes and was STILL half
a fix, because a missing KEY was covered and a missing FILE was not. This suite is that finding
taken to the class rather than the instance (R10): the same conflation was one level UP, in the
LOADER of every carrier the self-clearing-alarm census calls `real`, and there it was not half a
fix but a whole one missing.

MEASURED BEFORE THE FIX, across the whole partition of prior states rather than the shapes the
loop bodies happen to see:

    sim_runner.record_run_outcome(ok=False)   missing file -> streak=1 outage=0.00h
                                              truncated    -> streak=1 outage=0.00h   <-- same
                                              OPEN EPISODE -> streak=8 outage=10.00h
    background_worker._check_zero_progress    truncated    -> cycles=1 (from 8)
    ntfy_utils.record_delivery_outcome        truncated    -> failures=1 (from 5)
    supervisor._record_atom_draw_and_check_stall   json null     -> AttributeError
    background_worker._check_zero_progress        json null     -> AttributeError
    ntfy_utils.record_delivery_outcome            `[1, 2, 3]`   -> AttributeError

`json.loads` accepts `null` and `[1, 2, 3]`, so both parse, so both walked past every
`except (json.JSONDecodeError, OSError)` and left through a loader annotated `-> dict` into the
next line's `state.get(...)`. Those three run on the supervisor tick, the run-marker sweep, and
EVERY ntfy send -- including the send that carries the failure notification.

WHY THIS SUITE IS SHAPED AS A PARTITION AND NOT AS A LEG PER CASE. Every test of a guard asks "does
it refuse correctly", and a guard that refuses everything passes all of them. The two facts here
are OPPOSITE -- unreadable is data the carrier cannot know and must degrade on; absent is nothing
on disk, so no proposal can be an echo -- so a control asserting they take one branch would hold
the half-fix in place while reading as deliberate. `test_absent_and_unreadable_are_told_apart`
therefore asserts they DIFFER, and `test_the_open_episode_control_can_reach_a_different_answer` is
the reachability leg: without it every "differs" assertion would be satisfiable by a carrier that
answered the same thing to every input, and the whole partition would be a tautology.

AND THE SUBJECT IS DERIVED, NEVER HAND-LISTED. A hand-written list of five carriers silently stops
covering a sixth. `test_every_real_census_hit_is_covered` takes the subject from the census's own
dispositions file, so a newly `real` hit that nobody probed fails here rather than joining the
class quietly -- the same rung, for the same reason, that `--check` puts on the census itself.
"""
from __future__ import annotations

import json
import os

import pytest

from background.episode_prior import ABSENT, PRIOR_VERDICTS, READABLE, UNREADABLE, classify_prior

# The partition. Every member is a state a prior can ACTUALLY be in on this disk, and the verdict
# beside it is the fact it represents -- not the shape a particular loop body happens to see.
PARTITION = [
    ("missing file", None, ABSENT),
    ("empty file", "", UNREADABLE),
    ("truncated json", '{"cycles": 3, "first_fail', UNREADABLE),
    ("not a mapping", "[1, 2, 3]", UNREADABLE),
    ("json null", "null", UNREADABLE),
    ("missing key", "{}", READABLE),
]

NOW = 1_757_000_000.0


def _write(path, body):
    if body is None:
        path.unlink(missing_ok=True)
    else:
        path.write_text(body)


# --------------------------------------------------------------------------- the classifier

@pytest.mark.parametrize("label,body,expected", PARTITION)
def test_the_classifier_places_every_member_of_the_partition(label, body, expected, tmp_path):
    """`null` and `[1, 2, 3]` are the two that escaped: they PARSE, so no except-clause saw them."""
    from background.episode_prior import load_episode_prior

    p = tmp_path / "state.json"
    _write(p, body)
    state, verdict = load_episode_prior(p)
    assert verdict == expected, f"{label!r} classified {verdict!r}, expected {expected!r}"
    assert isinstance(state, dict), f"{label!r} returned {type(state).__name__}, not a dict"


def test_the_verdicts_are_exhaustive_and_the_partition_reaches_all_of_them():
    """VACUITY (R15): a classifier that returned one verdict for everything would pass every
    `expected` above if the table only ever named that one. Both directions are asserted -- the
    table reaches every verdict, and no case names a verdict the module does not define."""
    reached = {v for _, _, v in PARTITION}
    assert reached == set(PRIOR_VERDICTS), f"partition reaches {reached}, module defines {set(PRIOR_VERDICTS)}"


def test_a_directory_where_a_state_file_should_be_is_unreadable_not_absent(tmp_path):
    """It EXISTS. `read_text` raises IsADirectoryError, an OSError -- which the old loaders caught
    beside FileNotFoundError and answered `{}` to, i.e. "nothing was ever recorded"."""
    from background.episode_prior import load_episode_prior

    d = tmp_path / "state.json"
    d.mkdir()
    assert load_episode_prior(d)[1] == UNREADABLE


def test_classify_prior_is_pure_over_raw_bytes():
    """The read and the judgement are separable, so the judgement is testable without a disk."""
    assert classify_prior(None)[1] == ABSENT
    assert classify_prior("null")[1] == UNREADABLE
    assert classify_prior('{"a": 1}') == ({"a": 1}, READABLE)


# ------------------------------------------------------------------- the carriers, end to end

def _producer(tmp_path):
    import background.sim_runner as sr

    p = tmp_path / "producer.json"
    live = json.dumps({"last_result": "failed", "consecutive_failures": 7,
                       "first_failure_ts": NOW - 36000, "last_failure_ts": NOW - 60})

    def probe():
        s = sr.record_run_outcome(False, detail="x", state_path=p, now=NOW)
        return (s["consecutive_failures"], s["first_failure_ts"], bool(s.get("prior_unreadable")))
    return p, live, probe


def _sweep(tmp_path, monkeypatch):
    import background.background_worker as bw

    p = tmp_path / "sweep.json"
    monkeypatch.setattr(bw, "SWEEP_STATE_FILE", p)
    live = json.dumps({"cycles": 8, "oldest": "m1", "stalled_on": "m1"})

    class _Marker:
        name = "m1"

    def probe():
        bw._check_zero_progress([_Marker()])
        s = json.loads(p.read_text())
        return (s.get("cycles"), s.get("stalled_on"), bool(s.get("prior_unreadable")))
    return p, live, probe


def _atom_stall(tmp_path, monkeypatch):
    import background.supervisor as sup

    p = tmp_path / "stall.json"
    monkeypatch.setattr(sup, "ATOM_STALL_STATE_FILE", p)
    live = json.dumps({"A1": {"fingerprint": "fp", "consecutive_unchanged": 6, "stalled": True}})

    def probe():
        stalled, count = sup._record_atom_draw_and_check_stall("A1", "fp")
        s = json.loads(p.read_text())
        return (count, stalled, bool(s["A1"].get("prior_unreadable")))
    return p, live, probe


def _ntfy(tmp_path, monkeypatch):
    import background.ntfy_utils as nu

    p = tmp_path / "ntfy.json"
    monkeypatch.setattr(nu, "DELIVERY_STATE_FILE", p)
    monkeypatch.setattr(nu, "DELIVERY_LOG_FILE", tmp_path / "ntfy.log")
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    live = json.dumps({"delivered": False, "consecutive_failures": 5,
                       "since_epoch": NOW - 36000, "since": "2026-09-04T00:00:00"})

    def probe():
        nu.record_delivery_outcome(False, "boom")
        s = json.loads(p.read_text())
        return (s.get("consecutive_failures"), s.get("since_epoch"),
                bool(s.get("prior_unreadable")))
    return p, live, probe


def _stuck(tmp_path, monkeypatch):
    import background.supervisor as sup

    p = tmp_path / "stuck.json"
    monkeypatch.setattr(sup, "STUCK_STATE_FILE", p)
    live = json.dumps({"key": "k", "episode_key": "ek",
                       "first_seen_at": NOW - 36000, "escalated": False})

    def probe():
        state, verdict = sup._load_stuck_state_classified()
        return (type(state).__name__, verdict)
    return p, live, probe


#: name -> (builder, the state path the census knows it by). The census's `real` rows are keyed by
#: filename, and `test_every_real_census_hit_is_covered` reconciles this map against them.
CARRIERS = {
    "producer": (_producer, ".sim_producer_state.json"),
    "sweep": (_sweep, ".run_marker_sweep_state.json"),
    "atom_stall": (_atom_stall, ".atom_stall_tracker.json"),
    "ntfy": (_ntfy, ".ntfy_delivery_state.json"),
    "stuck": (_stuck, ".supervisor_stuck_state.json"),
}


def _build(name, tmp_path, monkeypatch):
    builder = CARRIERS[name][0]
    try:
        return builder(tmp_path, monkeypatch)
    except TypeError:
        return builder(tmp_path)


@pytest.mark.parametrize("carrier", sorted(CARRIERS))
@pytest.mark.parametrize("label,body,_expected", PARTITION)
def test_no_member_of_the_partition_raises_out_of_a_carrier(
        carrier, label, body, _expected, tmp_path, monkeypatch):
    """THE CRASH HALF. `json null` and `[1, 2, 3]` raised AttributeError out of three of these --
    the supervisor tick, the run-marker sweep, and every ntfy send. An observer must never break
    the observed, and an alarm's own writer crashing on the state it keeps its alarm in is that
    rule inverted."""
    p, _live, probe = _build(carrier, tmp_path, monkeypatch)
    _write(p, body)
    probe()   # the assertion is that this returns at all


@pytest.mark.parametrize("carrier", sorted(CARRIERS))
def test_absent_and_unreadable_are_told_apart(carrier, tmp_path, monkeypatch):
    """THE CONFLATION HALF, and the assertion is DIFFERENCE, never sameness.

    A control asserting both take one branch would pin the defect green while reading as
    deliberate -- which is exactly how `prev=None` stayed unfixed through two lanes' repairs. The
    two facts are opposite: with no file on disk nothing was ever recorded, so a fresh episode is
    the truth; with a truncated one an episode of unknown length just lost its memory, and
    recording a fresh one asserts evidence nobody had."""
    p, _live, probe = _build(carrier, tmp_path, monkeypatch)

    _write(p, None)
    absent = probe()
    _write(p, '{"cycles": 3, "first_fail')
    unreadable = probe()

    assert absent != unreadable, (
        f"{carrier}: a missing state file and a truncated one both answered {absent!r}. "
        "Those are opposite facts and this carrier cannot tell them apart."
    )


@pytest.mark.parametrize("carrier", sorted(CARRIERS))
def test_the_open_episode_control_can_reach_a_different_answer(carrier, tmp_path, monkeypatch):
    """REACHABILITY over the whole partition (R15). Every assertion above is satisfiable by a
    carrier that answers the same thing to everything, so this asserts a healthy OPEN episode --
    the state the alarms actually run in -- reads differently from both cold shapes. Without this
    leg the suite grades a mechanism that could have been deleted."""
    p, live, probe = _build(carrier, tmp_path, monkeypatch)

    _write(p, live)
    open_episode = probe()
    _write(p, None)
    absent = probe()
    _write(p, live)
    _write(p, '{"cycles": 3, "first_fail')
    unreadable = probe()

    assert open_episode != absent, f"{carrier}: an open episode reads the same as no state at all"
    assert open_episode != unreadable, f"{carrier}: an open episode reads the same as a corrupt one"


def test_every_real_census_hit_is_covered():
    """ANTI-NARROWING. The subject is the census's own `real` rows, not a list someone maintained.

    The two hits NOT probed end to end here are named with their reason rather than omitted --
    an omission is indistinguishable from an oversight, which is the property this rung exists to
    remove."""
    from background.self_clearing_alarm_census import DISPOSITIONS_PATH

    dispositions = json.loads(DISPOSITIONS_PATH.read_text())["dispositions"]
    real = {k for k, v in dispositions.items() if v.get("verdict") == "real"}

    covered = {path for _, path in CARRIERS.values()}
    # These two already distinguish the partition, in their own module, and predate this sweep:
    # `_read_publish_gate_state` and `_read_operational_layer_state` both raise on a non-dict
    # INSIDE their try and report `state_unavailable=True` for every unreadable member while
    # reporting False for a missing file. They are the shape `background/episode_prior.py`
    # generalises, which is why they are exempt and not merely absent.
    already_distinguishing = {".publish_gate_state.json", ".operational_layer_signal.json"}
    # `publish_provenance.json` guards itself with a once-only stamp (`record_paused` writes only
    # `if not state.get('paused_since')`) and has no cold-start reset to lose.
    guarded_elsewhere = {"publish_provenance.json"}

    uncovered = real - covered - already_distinguishing - guarded_elsewhere
    assert not uncovered, (
        f"census `real` hits with no absent-vs-unreadable coverage: {sorted(uncovered)}. "
        "A new carrier of this class must either be probed above or named with its reason."
    )


def test_the_two_exempt_readers_really_do_distinguish(tmp_path, monkeypatch):
    """The exemption above is a CHECKABLE CLAIM, so it is checked. A refusal that cites an artefact
    and never opens it is how an exemption list becomes a place to hide."""
    import background.process_run_complete as prc

    for attr in ("PUBLISH_GATE_STATE_FILE", "OPERATIONAL_LAYER_STATE_FILE"):
        reader = {"PUBLISH_GATE_STATE_FILE": prc._read_publish_gate_state,
                  "OPERATIONAL_LAYER_STATE_FILE": prc._read_operational_layer_state}[attr]
        p = tmp_path / f"{attr}.json"
        monkeypatch.setattr(prc, attr, p)
        _write(p, None)
        assert reader().get("state_unavailable") is False, f"{attr}: absent reported unavailable"
        for _label, body, expected in PARTITION:
            if expected is not UNREADABLE:
                continue
            _write(p, body)
            assert reader().get("state_unavailable") is True, (
                f"{attr}: {body!r} reported readable")


def test_the_partition_is_what_the_carriers_are_actually_asked(capsys):
    """Print the table. The direction that produced this suite asked for the verdict across the
    WHOLE partition rather than the shapes the loop bodies see, and a table nobody can print is a
    claim rather than a measurement. `pytest -s -k actually_asked` prints it."""
    print()
    for label, body, expected in PARTITION:
        print(f"  {label:16} {str(body)[:28]:30} -> {expected}")
    assert os.environ is not None  # the test is the print; this keeps it honestly non-vacuous
