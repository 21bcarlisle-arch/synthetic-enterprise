"""The red census is an INSTRUMENT, and an instrument that lies is worse than none.

Its whole value rests on two claims: it runs the gate's scope, and it runs it without the
gate's `-x`. Both are asserted here with mutation-shaped tests (R15) -- each one is written
so that breaking the property makes it FAIL, not so that it passes on the happy path.

Marked `operational`: this exercises the publish machinery's own harness rather than a
published number, so it belongs to the deselected operational tier (which has its own
independent-cadence green signal), not to the blocking content gate.
"""

import pytest

from background import process_run_complete as prc
from tools import enumerate_publish_gate_reds as census

pytestmark = pytest.mark.operational


class TestFailFastIsRemovedAndProvenRemoved:
    """`-x` is the ONE difference between the census and the gate."""

    def test_the_gate_argv_carries_fail_fast_and_the_census_argv_does_not(self):
        base = prc.publish_gate_pytest_argv("tests/")
        assert "-x" in base, "premise: the gate is fail-fast"
        assert "-x" not in census._argv_without_fail_fast(base)

    def test_every_other_flag_survives_verbatim(self):
        """Inheriting the deselections is the other half of 'same scope'. If the census
        dropped `-m` or an `--ignore`, it would enumerate reds the gate never runs and the
        batch would chase phantoms."""
        base = prc.publish_gate_pytest_argv("tests/")
        got = census._argv_without_fail_fast(base)
        assert got == [a for a in base if a != "-x"]
        assert "-m" in got and prc.PUBLISH_GATE_MARKER_EXPR in got
        for ignore in prc.PUBLISH_GATE_HEAVY_IGNORES:
            assert "--ignore=" + ignore in got

    @pytest.mark.parametrize("spelling", ["-x", "--exitfirst", "--exitfirst=1"])
    def test_it_strips_every_spelling_of_fail_fast(self, spelling):
        argv = ["python", "-m", "pytest", "tests/", spelling, "-q"]
        assert census._argv_without_fail_fast(argv) == ["python", "-m", "pytest", "tests/", "-q"]

    def test_it_REFUSES_an_argv_that_never_had_fail_fast(self):
        """THE MUTATION THAT MATTERS. If `publish_gate_pytest_argv` ever stops passing `-x`,
        this census is silently measuring something other than what it documents -- and its
        artefact would still look like a clean census. It must fail loudly instead."""
        with pytest.raises(AssertionError, match="carried no fail-fast"):
            census._argv_without_fail_fast(["python", "-m", "pytest", "tests/", "-q"])


class TestItEnumeratesTheWholeStackNotJustTheTop:
    """The defect the census exists to end: `-x` reports the first red and hides the rest."""

    def test_it_reports_every_red_in_collection_order(self):
        stdout = (
            "=== short test summary info ===\n"
            "FAILED tests/design/test_atom_notes_store.py::test_declarations_match_the_store - AssertionError: notes\n"
            "FAILED tests/design/test_simplifications_store.py::test_map_within_size_ratchet - over ratchet\n"
            "ERROR tests/tools/test_capability_index.py::test_live_register - DECORATIVE REFERENT x4\n"
        )
        reds = census.parse_reds(stdout)
        assert [r["node"] for r in reds] == [
            "tests/design/test_atom_notes_store.py::test_declarations_match_the_store",
            "tests/design/test_simplifications_store.py::test_map_within_size_ratchet",
            "tests/tools/test_capability_index.py::test_live_register",
        ], "a census that reports only the first red is the -x behaviour it replaces"
        assert reds[0]["kind"] == "FAILED" and reds[2]["kind"] == "ERROR"
        assert reds[2]["cause"] == "DECORATIVE REFERENT x4"

    def test_it_carries_the_cause_not_just_the_node(self):
        """R5: the artefact is the diagnostic payload. A census of bare node ids would cost
        a second run to find out what any of them said."""
        reds = census.parse_reds("FAILED tests/a.py::t - ValueError: boom\n")
        assert reds[0]["cause"] == "ValueError: boom"
        assert reds[0]["file"] == "tests/a.py"

    def test_a_green_run_enumerates_nothing(self):
        assert census.parse_reds("12 passed in 4.20s\n") == []

    def test_passing_lines_are_never_counted_as_red(self):
        """FAIL-OPEN's mirror: a parser that matched too eagerly would invent a batch."""
        stdout = ("tests/a.py::test_failed_login PASSED\n"
                  "PASSED tests/b.py::test_error_handling\n"
                  "1 failed, 2 passed\n")
        assert census.parse_reds(stdout) == []

    def test_a_repeated_node_is_counted_once(self):
        stdout = ("FAILED tests/a.py::t - first\n"
                  "FAILED tests/a.py::t - rerun\n")
        assert len(census.parse_reds(stdout)) == 1


class TestAnUnfinishedCensusSaysSo:
    """`feedback_a_wrapper_timeout_below_the_work_it_wraps_decides_the_verdict`: a run that
    hit its deadline has a LOWER BOUND on the red set, not a census of it. The distinction
    has to survive into the artefact, or the batch is built from a truncated list."""

    def test_the_outcomes_are_distinct_values(self):
        assert census.OUTCOME_COMPLETE != census.OUTCOME_TIMEOUT != census.OUTCOME_UNAVAILABLE

    def test_a_timed_out_census_is_not_reported_as_complete(self, monkeypatch, tmp_path):
        import subprocess

        monkeypatch.setattr(census.prc, "_head_sha", lambda: "deadbeef")
        monkeypatch.setattr(census, "_materialise_census_checkout", lambda sha: tmp_path)
        monkeypatch.setattr(census.publish_scope, "resolve_scope",
                            lambda root: {"full_suite": True, "tests": [], "sources": [],
                                          "reason": "full"})
        monkeypatch.setattr(census.publish_scope, "scoped_pytest_argv",
                            lambda base, scope, run_root: list(base))

        def _timeout(*a, **kw):
            raise subprocess.TimeoutExpired(cmd="pytest", timeout=1,
                                            output="FAILED tests/a.py::t - boom\n")

        monkeypatch.setattr(census.subprocess, "run", _timeout)
        out = census.run_census(deadline_seconds=1, keep_checkout=True)
        assert out["outcome"] == census.OUTCOME_TIMEOUT
        assert out["rc"] is None
        # It still reports what it DID see -- a lower bound is useful, mislabelling it is not.
        assert out["red_count"] == 1

    def test_an_unmaterialisable_checkout_is_unavailable_not_green(self, monkeypatch):
        """R15 fail-silent: a census that could not build its subject must never read as
        'no reds found'."""
        monkeypatch.setattr(census.prc, "_head_sha", lambda: "deadbeef")
        monkeypatch.setattr(census, "_materialise_census_checkout", lambda sha: None)
        out = census.run_census()
        assert out["outcome"] == census.OUTCOME_UNAVAILABLE
        assert "red_count" not in out, "an unavailable census must not report a red count at all"
