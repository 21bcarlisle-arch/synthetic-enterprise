"""The heartbeat may not land inside the gate the content publish is running.

THE DEFECT, MEASURED (2026-09-16, publish failure #41 -- the first of its class in 41). The
content publish landed nothing with `total_red: 0` and its own scoped suite GREEN. The log names
what beat it:

    17:26 Publish landing lost the race on attempt 1/2 (base 96b99dea4 -> 3be374b75)
    17:43 Publish landing lost the race on attempt 2/2 (base 3be374b75 -> fa4f2ea40)

`3be374b75` is `chore(liveness): publish heartbeat while sim output unchanged`, committed at
17:21:49 by `process_run_complete._refresh_published_liveness_on_skip` -- the SAME MODULE, one
minute into the gate it invalidated. The publisher lost the race to itself.

WHY IT IS THE DIRECTOR'S RULING AND NOT A NEW RULE. "Liveness must never be easier to publish
than content" (2026-08-13, the eighteen-hour freeze) was wired on the hook-chain DEADLINE, and
`test_liveness_is_never_easier_to_publish_than_content` still holds it there -- its own docstring
records that the two paths stopped sharing a constant on 2026-09-08. Equal deadlines and liveness
is STILL the easier publish, because the paths differ in a way no deadline describes: content
re-gates from scratch when HEAD moves and gives up after `PUBLISH_LAND_ATTEMPTS`, while the
heartbeat is a narrow pathspec that never holds the lock across its commit, every thirty minutes.
A rule named for a property, implemented as one number, and violated on the dimension the number
does not measure. 2026-08-12 is the same picture through the deadline door: twenty-one killed
content commits with a heartbeat landing on origin throughout.

AND THE TRIGGER IS THE WEDGE. The heartbeat fires "while sim output unchanged" -- by construction
the state that holds while a content publish has not landed. These are not independent writers
that happened to collide: the condition arming the heartbeat is the condition the content publish
exists to end, so the collision is positively correlated, not a coin toss.

WHAT THIS FILE REFUSES TO ASSERT. Not "the heartbeat is off", not "publishes succeed" -- a
fail-closed interlock cannot make a publish land, and a control that predicted one would be
predicting a defect. It asserts the PROPERTY: while a landing is in flight the heartbeat declines,
and in every other state -- no marker, a dead marker, an unreadable one -- it beats. Both halves,
because a guard that declined always would satisfy the first leg alone and reintroduce Fault #1
(2026-07-25), the freeze the heartbeat was built to end.
"""
import ast
import inspect
import json

import background.process_run_complete as prc


def _write_marker(tmp_path, monkeypatch, payload):
    """Point the module's marker at a scratch file holding `payload`."""
    target = tmp_path / ".publish_landing_in_flight.json"
    monkeypatch.setattr(prc, "LANDING_IN_FLIGHT_FILE", target)
    if payload is not None:
        target.write_text(payload if isinstance(payload, str) else json.dumps(payload),
                          encoding="utf-8")
    return target


def test_the_heartbeat_declines_while_a_content_landing_is_in_flight(tmp_path, monkeypatch):
    """A live marker is the one state in which liveness yields the tree.

    Fires on: the interlock being deleted, its expiry being widened past the heartbeat's own
    cadence, or `_landing_in_flight` being inverted.
    """
    _write_marker(tmp_path, monkeypatch, {"started": prc.datetime.now(prc.timezone.utc).timestamp(),
                                          "writer": "a test"})
    verdict = prc._landing_in_flight()
    assert verdict["live"], (
        "a landing marker written a moment ago does not read as in flight, so the heartbeat will "
        "take the race from the content publish exactly as it did on 2026-09-16: " + verdict["why"])
    assert "in flight" in verdict["why"], (
        "the verdict carries no reason a reader of the log could act on: " + verdict["why"])


def test_the_heartbeat_BEATS_when_no_landing_is_running(tmp_path, monkeypatch):
    """THE OTHER HALF. An interlock that always declined would pass the leg above and freeze the
    liveness surface -- which is Fault #1 itself, not a fix for it."""
    _write_marker(tmp_path, monkeypatch, None)
    verdict = prc._landing_in_flight()
    assert not verdict["live"], (
        "with NO marker on disk the heartbeat still yields, so liveness is gated on a file that is "
        "absent almost all the time: " + verdict["why"])


def test_a_landing_marker_left_by_a_DEAD_publisher_stops_being_believed(tmp_path, monkeypatch):
    """A crashed publish must not be able to freeze liveness -- it could before 2026-07-25.

    Keyed to the CADENCE, not to a literal: whatever the heartbeat's own interval is, a marker
    older than one beat is a corpse. Fires if the bound is widened to the landing's worst
    permitted cost (`PUBLISH_LAND_ATTEMPTS * surgical_land.GATE_TIMEOUT_SECONDS`, two hours),
    which is the tempting wrong number.
    """
    stale = prc.datetime.now(prc.timezone.utc).timestamp() - (prc.PUSH_THROTTLE_SECONDS + 60)
    _write_marker(tmp_path, monkeypatch, {"started": stale, "writer": "a publisher that died"})
    verdict = prc._landing_in_flight()
    assert not verdict["live"], (
        "a marker older than one heartbeat interval is still believed, so one publisher that died "
        "mid-landing holds the liveness surface down indefinitely: " + verdict["why"])
    assert "died" in verdict["why"], (
        "the reason does not tell the reader the marker was read as a corpse, which is the one "
        "thing that distinguishes this from suppression: " + verdict["why"])
    assert prc.LANDING_MARKER_TRUSTED_SECONDS == prc.PUSH_THROTTLE_SECONDS, (
        "the marker's trusted window has drifted off the heartbeat's own cadence, so 'liveness "
        "yields at most one beat' is no longer what this mechanism does")


def test_an_UNREADABLE_marker_lets_the_heartbeat_beat(tmp_path, monkeypatch):
    """FAIL OPEN, AND THE DIRECTION IS THE ARGUMENT. R15 says an unavailable check is a failed
    check; here the two failures are not symmetric. A heartbeat that beats during a landing costs
    ONE content publish, retried next run. A heartbeat that does not beat costs the only signal
    anyone outside has that the machine is alive."""
    _write_marker(tmp_path, monkeypatch, "{not json at all")
    assert not prc._landing_in_flight()["live"], (
        "a malformed marker reads as a live landing, so a single corrupt write freezes the "
        "liveness surface -- the fail-CLOSED direction is the wrong one here")


def test_the_marker_is_HELD_ACROSS_the_landing_and_released_after(tmp_path, monkeypatch):
    """The mechanism exists AND spans the gate AND lets go. An interlock that set the marker and
    never cleared it would be caught by the corpse rung above only after a whole beat was lost."""
    target = _write_marker(tmp_path, monkeypatch, None)
    with prc._landing_in_flight_marker("abc123def"):
        assert prc._landing_in_flight()["live"], (
            "the marker is not live INSIDE its own context manager, so nothing is interlocked "
            "during the window that matters")
        assert json.loads(target.read_text())["git_hash"] == "abc123def", (
            "the marker does not name the run it is landing, so a reader of a stale marker cannot "
            "tell which publish left it")
    assert not prc._landing_in_flight()["live"], (
        "the marker outlives the landing, so the next heartbeat yields to a landing that finished")


def test_a_RAISING_landing_still_releases_the_marker(tmp_path, monkeypatch):
    """The `finally` is the reason the corpse window is a backstop and not the normal case."""
    _write_marker(tmp_path, monkeypatch, None)
    try:
        with prc._landing_in_flight_marker("deadbeef1"):
            raise RuntimeError("the landing blew up")
    except RuntimeError:
        pass
    assert not prc._landing_in_flight()["live"], (
        "a landing that raised leaves its marker behind, so the next heartbeat is suppressed by a "
        "publish that is no longer running")


def test_the_CONTENT_LANDING_CALL_IS_WIRED_INSIDE_THE_MARKER():
    """THE WIRING, NOT THE MECHANISM -- the two failures this class keeps producing separately.

    Every rung above drives `_landing_in_flight_marker` directly, and all of them stay green if
    the call site is unwrapped: an interlock nobody entered. So this reads the publisher's own
    source and asserts the `_land_publish_commit(...)` call is lexically INSIDE a
    `with _landing_in_flight_marker(...)` block.

    MUTATION: unindent the landing call out of the `with` and this is the only rung that reds.
    """
    tree = ast.parse(inspect.getsource(prc.git_commit_push).lstrip())
    guarded = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.With):
            continue
        opens_marker = any(
            isinstance(item.context_expr, ast.Call)
            and getattr(item.context_expr.func, "id", None) == "_landing_in_flight_marker"
            for item in node.items)
        if not opens_marker:
            continue
        for inner in ast.walk(node):
            if (isinstance(inner, ast.Call)
                    and getattr(inner.func, "id", None) == "_land_publish_commit"):
                guarded = True
    assert guarded, (
        "`_land_publish_commit` is called OUTSIDE `_landing_in_flight_marker`, so the marker is "
        "never set while the gate runs and the heartbeat can take the tree from the content "
        "publish again -- the mechanism is present and unwired")


def test_the_heartbeat_path_actually_CONSULTS_the_interlock():
    """The symmetric wiring leg, on the consuming side.

    A marker written by a landing that no reader checks is the same defect in the mirror. Asserted
    against the liveness function's own source, so deleting the check reds here rather than going
    quietly green everywhere.
    """
    source = inspect.getsource(prc._refresh_published_liveness_on_skip)
    assert "_landing_in_flight()" in source, (
        "`_refresh_published_liveness_on_skip` does not consult `_landing_in_flight`, so the "
        "landing marker is written, expired and never read -- liveness is easier to publish than "
        "content again, on the dimension the deadline invariant does not measure")
    # AND IT IS CONSULTED BEFORE THE COMMIT, not after: a check that runs past
    # `_commit_and_push_paths` would observe the race it was meant to prevent.
    assert source.index("_landing_in_flight()") < source.index("_commit_and_push_paths"), (
        "the interlock is consulted AFTER the heartbeat commits, so it reports the collision "
        "instead of preventing it")
