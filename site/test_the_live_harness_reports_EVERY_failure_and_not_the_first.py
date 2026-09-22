"""The live-door harness reports every failure it saw, not the first one and then silence.

THE DEFECT: `scriptError` was one slot filled with `x = x || ...` across every inline script block
AND every document-ready listener. A door broken in three places reported ONE. A caller who
repaired that one learned about the second only by re-running, and -- the way this was actually
found -- a caller reading a mostly-blank page beside a single terse message has no way to tell one
defect from the first of several. The natural reading of one error next to a quiet page is that
the page has nothing more to say.

AND THE SECOND HALF, which was worse: an unhandled promise rejection KILLED the harness process.
The caller got no stdout at all, so which elements had rendered and which feeds were unresolved
were destroyed along with the failure -- the evidence a reader needs most, thrown away at exactly
the moment it is produced.

WHY THIS IS A CONTROL ON THE INSTRUMENT AND NOT ON A DOOR. Every `*_reaches_the_reader` control in
`site/` reads this harness's output and most assert `_meta["scriptError"] is None`. An instrument
that loses failures makes all of them weaker at once, and none of them can see it: a door with two
breaks that is repaired down to one still reports one message, and the suite reads identically
before and after. This is the only place that difference is visible.

REAL DOORS ARE NOT USED AS FIXTURES HERE, deliberately. A control over "the harness reports N
errors" needs a subject with a known number of errors in known places; pointing it at a shipped
page would pin it to that page's current health and red the day the page is fixed. The doors are
written here, minimal, and each break is placed on purpose.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent / "_live_harness.mjs"

#: A door broken in THREE places, one per channel the harness evaluates: two inline blocks and a
#: document-ready listener. Each writes before it throws, so the control can also tell "the block
#: did not run" from "the block ran and broke" -- those are different defects and the old single
#: slot reported them the same way.
THREE_BREAKS = """<html><body>
<script>
  document.getElementById("a").textContent = "block one ran";
  throw new Error("FIRST BLOCK BROKE");
</script>
<script>
  document.getElementById("b").textContent = "block two ran";
  throw new Error("SECOND BLOCK BROKE");
</script>
<script>
  document.addEventListener("DOMContentLoaded", function () {
    throw new Error("READY LISTENER BROKE");
  });
</script>
</body></html>
"""

#: A door that leaves a fetch rejection unhandled -- no `.catch`. This used to take the process
#: down before it could print anything.
UNHANDLED_REJECTION = """<html><body>
<script>
  document.getElementById("rendered-before").textContent = "this survived";
  fetch("../data/missing.json").then(function (r) { return r.json(); })
    .then(function (d) { document.getElementById("never").textContent = "unreachable"; });
</script>
</body></html>
"""

#: A door that is entirely healthy. Without it every assertion below is satisfied by a harness that
#: reports errors unconditionally, which is the fail-closed mirror of the defect being fixed.
HEALTHY = """<html><body>
<script>
  document.getElementById("ok").textContent = "rendered";
</script>
</body></html>
"""


def _run(tmp_path: Path, html: str, feeds: dict | None = None) -> dict:
    door = tmp_path / "door.html"
    door.write_text(html, encoding="utf-8")
    proc = subprocess.run(
        ["node", str(HARNESS), str(door)],
        input=json.dumps(feeds or {}), capture_output=True, text=True, timeout=120)
    if not proc.stdout.strip():
        pytest.fail(
            "the harness produced NO stdout (exit {}). That is the defect this file exists for: a "
            "run that dies reports nothing at all, so the elements that DID render and the feeds "
            "that were unresolved are destroyed with the failure.\nstderr:\n{}".format(
                proc.returncode, proc.stderr[:2000]))
    return json.loads(proc.stdout)


def test_the_partition_is_WHOLE(tmp_path):
    """DEFECT: a channel that reports everything, or nothing, and reads the same either way."""
    broken = _run(_mkdir(tmp_path, "broken"), THREE_BREAKS)
    clean = _run(_mkdir(tmp_path, "clean"), HEALTHY)

    assert broken["_meta"]["scriptErrors"], "a door broken in three places reported no failure"
    assert clean["_meta"]["scriptErrors"] == [], (
        "a healthy door reported a failure: {}. A channel that always reports passes every test "
        "of a report.".format(clean["_meta"]["scriptErrors"]))
    assert clean["_meta"]["scriptError"] is None
    assert clean["ok"]["textContent"] == "rendered"


def test_EVERY_break_is_reported_and_not_only_the_first(tmp_path):
    """DEFECT: `scriptError = scriptError || ...` -- three breaks, one message."""
    meta = _run(_mkdir(tmp_path, "three"), THREE_BREAKS)["_meta"]

    messages = [e["message"] for e in meta["scriptErrors"]]
    assert messages == ["FIRST BLOCK BROKE", "SECOND BLOCK BROKE", "READY LISTENER BROKE"], (
        "the harness reported {} of 3 breaks. A caller repairing the one it names learns about "
        "the rest only by re-running, once per defect.".format(len(messages)))


def test_each_break_names_WHERE_it_happened(tmp_path):
    """DEFECT: three messages with no way to tell which channel produced which.

    A block that throws and a document-ready listener that throws are different repairs, and a
    message alone cannot distinguish them -- the two can carry identical text.
    """
    meta = _run(_mkdir(tmp_path, "where"), THREE_BREAKS)["_meta"]

    where = [e["where"] for e in meta["scriptErrors"]]
    assert where == ["script[0]", "script[1]", "DOMContentLoaded"], where


def test_a_broken_door_still_reports_what_it_DID_render(tmp_path):
    """DEFECT: losing the render report along with the failure."""
    out = _run(_mkdir(tmp_path, "partial"), THREE_BREAKS)

    # Both blocks wrote before they threw. A harness that stopped at the first break would have
    # `b` absent, and a reader would conclude the second block never ran.
    assert out["a"]["textContent"] == "block one ran"
    assert out["b"]["textContent"] == "block two ran"


def test_an_unhandled_rejection_is_REPORTED_rather_than_fatal(tmp_path):
    """DEFECT: the process died, taking the whole report with it.

    This is the leg that would have failed loudest before the fix: `_run` fails the test outright
    when stdout is empty, which is exactly what this door used to produce.
    """
    out = _run(_mkdir(tmp_path, "reject"), UNHANDLED_REJECTION)
    meta = out["_meta"]

    assert [e["where"] for e in meta["scriptErrors"]] == ["unhandledRejection"], meta
    assert "no payload supplied" in meta["scriptError"]
    # AND THE EVIDENCE SURVIVES, which is the whole point of not dying: the caller can still see
    # which feed was missing and what had already rendered.
    assert meta["unresolved"] == ["../data/missing.json"]
    assert out["rendered-before"]["textContent"] == "this survived"


def test_scriptError_still_carries_the_FIRST_message(tmp_path):
    """DEFECT: breaking every existing control that reads `scriptError`.

    Controls across `site/` assert `_meta["scriptError"] is None`. The field is kept and derived
    from the list rather than renamed, and this pins that so a later tidy-up cannot quietly drop
    it and take every one of those controls fail-open with it.
    """
    meta = _run(_mkdir(tmp_path, "compat"), THREE_BREAKS)["_meta"]

    assert meta["scriptError"] == meta["scriptErrors"][0]["message"] == "FIRST BLOCK BROKE"


def test_a_static_door_reports_the_SAME_SHAPE(tmp_path):
    """DEFECT: a path where the field is absent, so "no errors" and "not reported" collapse."""
    meta = _run(_mkdir(tmp_path, "static"), "<html><body><p>no script here</p></body></html>")["_meta"]

    assert meta["static"] is True
    assert meta["scriptErrors"] == []
    assert meta["scriptError"] is None


def _mkdir(base: Path, name: str) -> Path:
    path = base / name
    path.mkdir(parents=True, exist_ok=True)
    return path
