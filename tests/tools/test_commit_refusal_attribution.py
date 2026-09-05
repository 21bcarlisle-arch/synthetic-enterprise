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


# ---------------------------------------------------------------------------
# EPISODES -- what a refusal COSTS. A count of cycles is not a cost, and the
# defects below are the ways a cost measurement flatters itself.
# ---------------------------------------------------------------------------


def _failed(ts, outcome):
    """A cycle that failed for some reason OTHER than commit_refused."""
    return "\n".join([
        "- [{} UTC] [process_run] Committing and pushing (net=£1)".format(ts),
        "- [{} UTC] [process_run] Commit/push failed ({})".format(ts, outcome),
    ])


def test_an_unterminated_episode_is_censored_and_excluded_not_counted_as_short():
    """The log ending mid-wedge has no landing to measure against, and that episode is exactly
    the one most likely to be the longest -- nobody has cleared it yet. Treating the last refusal
    as its end would report an ONGOING outage as a finished, short one, biasing the headline
    toward comfort in precisely the case that matters most."""
    log = "\n".join([
        _cycle("2026-08-20 10:00", refused=True, hook_body=ORPHAN_HOOK),
        _cycle("2026-08-20 11:00", refused=False),
        _cycle("2026-08-20 12:00", refused=True, hook_body=ORPHAN_HOOK),
        _cycle("2026-08-20 13:00", refused=True, hook_body=ORPHAN_HOOK),
    ])
    ep = attr.episode_report(log)
    assert len(ep["censored"]) == 1
    assert ep["censored"][0]["from"] == "2026-08-20 12:00"
    # A lower bound, and never a number that can be maxed or medianed.
    assert ep["censored"][0]["outage_s"] is None
    assert [e["from"] for e in ep["bounded"]] == ["2026-08-20 10:00"]
    assert ep["longest"]["from"] == "2026-08-20 10:00"


def test_the_two_run_definitions_give_different_answers_on_the_same_log():
    """A cost episode ends at a LANDING; a cycle-share run ends at anything that is not this
    failure mode. A `behind_origin` cycle mid-wedge is a recovery under one and not the other,
    and the publisher did NOT land -- so the cost definition must merge what the share definition
    splits. If both definitions returned the same number on a log built to separate them, the
    distinction would be decorative and the module would be reporting one figure twice."""
    log = "\n".join([
        _cycle("2026-08-20 10:00", refused=True, hook_body=ORPHAN_HOOK),
        _failed("2026-08-20 11:00", "behind_origin"),
        _cycle("2026-08-20 12:00", refused=True, hook_body=ORPHAN_HOOK),
        _cycle("2026-08-20 13:00", refused=False),
    ])
    ep = attr.episode_report(log)
    assert ep["episodes_strict"] == 2
    assert ep["episodes_cost"] == 1
    assert ep["episodes_cost"] < ep["episodes_strict"]
    # And the merged episode spans the interloper: 10:00 -> 13:00, not two 1-cycle runs.
    assert ep["bounded"][0]["cycles"] == 3
    assert ep["bounded"][0]["outage_s"] == 3 * 3600


def test_a_single_cycle_episode_has_a_real_outage_although_its_span_is_zero():
    """Span excludes the recovery, so a 1-cycle episode has span 0 -- and reporting THAT as the
    cost says a refusal is free. It is not: the publisher cannot publish until the next attempt
    lands, which is at least one inter-attempt gap away."""
    log = "\n".join([
        _cycle("2026-08-20 10:00", refused=True, hook_body=ORPHAN_HOOK),
        _cycle("2026-08-20 10:45", refused=False),
    ])
    e = attr.episode_report(log)["bounded"][0]
    assert e["span_s"] == 0
    assert e["outage_s"] == 45 * 60


def test_an_episode_with_two_causes_is_attributed_to_neither():
    """The same discipline as the unattributable bucket, one level up. Assigning a mixed episode
    to its first or its commonest cause is how 74% of the cost gets a tidy label it did not earn,
    and the by-cause medians then describe episodes that were never purely that cause."""
    log = "\n".join([
        _cycle("2026-08-20 10:00", refused=True, hook_body=ORPHAN_HOOK),
        _cycle("2026-08-20 11:00", refused=True, hook_body=RED_HOOK),
        _cycle("2026-08-20 12:00", refused=False),
    ])
    ep = attr.episode_report(log)
    assert ep["bounded"][0]["cause"] == attr.MIXED
    assert ep["bounded"][0]["causes"] == [attr.RED_TEST, "orphan-ratchet"]
    assert attr.RED_TEST not in ep["by_cause"] and "orphan-ratchet" not in ep["by_cause"]
    assert ep["mixed"] == 1


def test_the_cause_sequence_separates_gates_queueing_from_one_gate_flapping():
    """Two episodes with the SAME cause set and the same length mean opposite things: A,B,B is
    each gate cleared once in turn; A,B,A is a gate that was cleared and broke again. They call
    for opposite responses -- reorder the gates, versus find what keeps re-breaking one -- and a
    set of causes cannot tell them apart, so the order has to survive into the record."""
    def build(bodies):
        return "\n".join(
            [_cycle("2026-08-20 1{}:00".format(i), refused=True, hook_body=b)
             for i, b in enumerate(bodies)]
            + [_cycle("2026-08-20 19:00", refused=False)])

    queue = attr.episode_report(build([ORPHAN_HOOK, RED_HOOK, RED_HOOK]))["bounded"][0]
    flap = attr.episode_report(build([ORPHAN_HOOK, RED_HOOK, ORPHAN_HOOK]))["bounded"][0]
    assert queue["causes"] == flap["causes"]
    assert queue["cause_sequence"] != flap["cause_sequence"]
    assert queue["cause_sequence"] == [attr.RED_TEST if b is RED_HOOK else "orphan-ratchet"
                                       for b in (ORPHAN_HOOK, RED_HOOK, RED_HOOK)]


def test_a_landing_is_the_absence_of_a_failure_line_and_the_blind_span_is_not_read_as_landings():
    """This log has no success line: the publisher announces an attempt and speaks again only if
    it failed. So a landing is an ABSENCE, and an absence only means anything after the named
    outcomes arrived. Reading the blind span as a wall of successful cycles would put an
    enormous, entirely fictional recovery in front of the first real episode."""
    log = "\n".join(
        [_cycle("2026-07-01 10:0{}".format(i), refused=False) for i in range(4)]
        + [_cycle("2026-08-20 10:00", refused=True, hook_body=ORPHAN_HOOK),
           _cycle("2026-08-20 11:00", refused=False)])
    seq = attr.cycles(log)
    assert [c["at"] for c in seq] == ["2026-08-20 10:00", "2026-08-20 11:00"]
    assert seq[-1]["outcome"] == attr.LANDED and seq[-1]["cause"] is None
    assert attr.episode_report(log)["bounded"][0]["outage_s"] == 3600
