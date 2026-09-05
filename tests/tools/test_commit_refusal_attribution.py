"""Controls over the commit-refusal attribution.

THE DEFECT EACH ONE NAMES is in its own name. All fixtures are synthetic: a control keyed to
today's log would go red the moment the publisher recovers, which is backwards -- these are
keyed to the PROPERTIES the measurement must have, so they stay green as the numbers move and
red when the measurement starts lying.
"""

from __future__ import annotations

import pytest

from tools import commit_refusal_attribution as attr


def _cycle(ts, *, refused, hook_body=""):
    """One publish cycle as the runner log writes it."""
    out = ["- [{} UTC] [process_run] Committing and pushing (net=£1)".format(ts)]
    if refused:
        out.append("- [{} UTC] [process_run] Nothing to commit or commit failed (rc=1)".format(ts))
        out.extend(hook_body.split("\n"))
        out.append("- [{} UTC] [process_run] Commit/push failed (commit_refused)".format(ts))
    else:
        out.append("- [{} UTC] [process_run] Committed locally".format(ts))
    return "\n".join(out)


RED_HOOK = "  git/hook output (last 40 lines):\nFAILED tests/test_x.py::test_y - AssertionError\n1 failed, 40 passed"
ORPHAN_HOOK = ("  git/hook output (last 40 lines):\n"
               "orphan-ratchet: THIS COMMIT ADDS WORK THAT NOTHING RUNS\n"
               "364 passed in 40s")


def test_a_blind_denominator_is_not_reported_as_the_rate():
    """The lifetime denominator counts cycles that COULD NOT have named a refusal.

    The direction that commissioned this divided 175 by every publish cycle ever logged and got
    9.2%, when three quarters of that denominator predates the named-outcome vocabulary. The two
    denominators must be reported separately and must actually differ when the log has a blind
    span -- a measurement that collapses them is the original defect wearing a script.
    """
    log = "\n".join(
        [_cycle("2026-07-01 10:0{}".format(i), refused=False) for i in range(5)]
        + [_cycle("2026-08-20 10:0{}".format(i), refused=True, hook_body=ORPHAN_HOOK)
           for i in range(3)])
    r = attr.attribute(log)
    assert r["refusals"] == 3
    assert r["attempts_lifetime"] == 8
    # The observable window opens at the FIRST nameable refusal, so the five blind cycles are out.
    assert r["attempts_observable"] == 3
    assert r["attempts_observable"] < r["attempts_lifetime"]


def test_a_non_test_gate_refusal_is_not_credited_to_a_red_test():
    """The loose-needle trap, in the direction that matters.

    A gate banner sits in output that also contains a passing pytest summary. A red-test detector
    matching the bare word `failed` -- or matching a summary line without anchoring it -- credits
    the orphan ratchet's refusal to a phantom red test, and sends the reader to run a green suite.
    That is the 2026-09-02 wedge exactly.
    """
    r = attr.attribute(_cycle("2026-08-20 10:00", refused=True, hook_body=ORPHAN_HOOK))
    assert r["by_gate"] == {"orphan-ratchet": 1}
    assert r["red_test"] == 0
    assert r["non_test_gate"] == 1


def test_a_red_test_refusal_is_not_credited_to_a_gate():
    r = attr.attribute(_cycle("2026-08-20 10:00", refused=True, hook_body=RED_HOOK))
    assert r["red_test"] == 1
    assert r["non_test_gate"] == 0


def test_an_unattributable_refusal_is_its_own_bucket_and_never_joins_a_side():
    """Honest ignorance must not be swept onto whichever side makes the split look cleaner.

    Two ways a refusal resists attribution -- no retained hook block, and a block naming neither
    a banner nor a red -- and BOTH must land outside `red_test` and `non_test_gate`, or the two
    shares silently include cycles nobody classified.
    """
    log = "\n".join([
        # A refusal whose hook block was never written (log truncated, or an older format).
        "- [2026-08-20 10:00 UTC] [process_run] Committing and pushing (net=£1)",
        "- [2026-08-20 10:00 UTC] [process_run] Commit/push failed (commit_refused)",
        _cycle("2026-08-20 11:00", refused=True,
               hook_body="  git/hook output (last 40 lines):\nsomething nobody has a needle for"),
    ])
    r = attr.attribute(log)
    assert r["refusals"] == 2
    assert r["unattributable"] == 2
    assert r["red_test"] == 0
    assert r["non_test_gate"] == 0
    # The whole partition, asserted as a partition -- this is what stops a future bucket being
    # added and quietly counted twice, or not at all.
    assert r["red_test"] + r["non_test_gate"] + r["unattributable"] == r["refusals"]


def test_the_partition_holds_over_a_mixed_log_with_every_bucket_populated():
    """One control over the WHOLE partition, with every branch REACHABLE.

    A per-bucket assertion passes for a classifier that returns one bucket for everything. This
    asserts all three are non-empty at once, so the trivially-constant classifier fails it.
    """
    log = "\n".join([
        _cycle("2026-08-20 10:00", refused=True, hook_body=RED_HOOK),
        _cycle("2026-08-20 11:00", refused=True, hook_body=ORPHAN_HOOK),
        _cycle("2026-08-20 12:00", refused=True, hook_body="  git/hook output:\nunknowable"),
        _cycle("2026-08-20 13:00", refused=False),
    ])
    r = attr.attribute(log)
    assert r["red_test"] and r["non_test_gate"] and r["unattributable"]
    assert r["red_test"] + r["non_test_gate"] + r["unattributable"] == r["refusals"] == 3
    assert r["attempts_observable"] == 4


def test_contiguous_refusal_runs_are_measured_not_assumed():
    """Clustering is the finding that decides whether a per-cycle rate means anything at all.

    Three refusals in a row and three spread apart give the same count and completely different
    advice, so the run structure must come out of the sequence, not out of the total.
    """
    clustered = "\n".join(
        [_cycle("2026-08-20 10:0{}".format(i), refused=True, hook_body=ORPHAN_HOOK)
         for i in range(3)] + [_cycle("2026-08-20 11:00", refused=False)])
    spread = "\n".join(
        "\n".join([_cycle("2026-08-20 1{}:00".format(i), refused=True, hook_body=ORPHAN_HOOK),
                   _cycle("2026-08-20 1{}:30".format(i), refused=False)])
        for i in range(3))
    a, b = attr.attribute(clustered), attr.attribute(spread)
    assert a["refusals"] == b["refusals"] == 3
    assert a["runs"] == [3]
    assert b["runs"] == [1, 1, 1]


@pytest.mark.parametrize("banner,expected", [
    ("[level-gate] ❌ COMMIT REFUSED (a level move must be BUILT)", "level-promotion gate"),
    ("[site-lane] ❌ the page and the feed disagree", "site-lane gate"),
    ("❌ FINDING-CLASS CONSOLIDATION BROKEN", "finding-class consolidation"),
])
def test_the_publishers_own_banner_table_is_what_names_the_gate(banner, expected):
    """No second vocabulary. A private needle list here would drift from the gates it names and
    every drifted gate would silently read as `UNNAMED` -- an under-count that looks like data."""
    r = attr.attribute(_cycle("2026-08-20 10:00", refused=True,
                              hook_body="  git/hook output:\n{}\n40 passed".format(banner)))
    assert r["by_gate"] == {expected: 1}
