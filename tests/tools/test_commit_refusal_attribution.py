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


# --- The fixed serial gate order, and what it PROVES about a recurrence -----------------------
#
# `core.hooksPath` is `tools/git-hooks` and every gate there is `python3 ... || exit 1`, so the
# named cause is the FIRST failing gate. These controls are over that inference, not over the
# counts it produces.

def _fake_root(tmp_path, emitters, sources=None):
    """A repo root whose hook invokes `emitters` IN THE GIVEN ORDER.

    The emitter paths and banner texts are the REAL ones, taken from the publisher's own table --
    only the order is synthetic. A fixture that invented its own gate names would pass while the
    join to that table was broken, which is the one thing these controls exist to check.
    """
    hooks = tmp_path / "tools" / "git-hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    (hooks / "pre-commit").write_text(
        "\n".join(["#!/bin/sh"] + ["python3 {} || exit 1".format(e) for e in emitters]))
    (hooks / "commit-msg").write_text("#!/bin/sh\n")
    for emitter, body in (sources or {}).items():
        path = tmp_path / emitter
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
    return tmp_path


TEST_GATE = "tools/pre_commit_test_gate.py"
ORPHAN_GATE = "tools/orphan_ratchet.py"
_SOURCES = {
    TEST_GATE: 'print("[test-gate] \\u274c FINDING-CLASS CONSOLIDATION BROKEN")\n'
               'r = subprocess.run([sys.executable, "-m", "pytest", *targets])\n',
    ORPHAN_GATE: 'print("orphan-ratchet: THIS COMMIT ADDS WORK THAT NOTHING RUNS")\n',
}


def test_the_same_recurrence_is_a_flap_or_a_mask_depending_on_the_hook_order(tmp_path):
    """THE ORDERING CONTROL: the two orders must produce DIFFERENT verdicts on ONE sequence.

    The defect this names is the whole reason the question was open. `RED TEST, orphan, RED TEST`
    is a proven flap only if the orphan ratchet runs AFTER the test gate -- reaching it proves the
    suite passed in between, so the red test was cleared and re-broke. Run the orphan ratchet
    FIRST and the identical sequence proves nothing: the red test may have stood broken behind it
    the whole time. A classifier that ignored the hook and answered from the sequence alone would
    give one answer here and be right by accident half the time.
    """
    seq = [attr.RED_TEST, "orphan-ratchet", attr.RED_TEST]
    pair = attr.recurrence_pairs(seq)[0]
    assert pair["cause"] == attr.RED_TEST and pair["between"] == ["orphan-ratchet"]

    tests_first = attr.gate_order(
        _fake_root(tmp_path / "a", [TEST_GATE, ORPHAN_GATE], _SOURCES))
    orphan_first = attr.gate_order(
        _fake_root(tmp_path / "b", [ORPHAN_GATE, TEST_GATE], _SOURCES))
    assert attr.classify_recurrence(pair["cause"], pair["between"], tests_first) == attr.PROVEN_FLAP
    assert attr.classify_recurrence(pair["cause"], pair["between"], orphan_first) == attr.MASKABLE


def test_a_step_to_an_earlier_gate_is_proven_new_breakage_and_never_a_queue_step(tmp_path):
    """A queue and new breakage are opposite conclusions and the order separates them.

    `orphan-ratchet` then `RED TEST` means an EARLIER gate refused on the second cycle -- it was
    reached and passed on the first, so something broke it in between. Calling that a queue step
    would license "the publisher just needs to be told about every refusal at once", which is
    exactly wrong when the tree is being broken underneath it. The reverse direction must come out
    as the queue step, or the classifier is simply labelling every transition the same way.
    """
    order = attr.gate_order(_fake_root(tmp_path, [TEST_GATE, ORPHAN_GATE], _SOURCES))
    assert attr.classify_transition("orphan-ratchet", attr.RED_TEST, order) == attr.NEW_BREAKAGE
    assert attr.classify_transition(attr.RED_TEST, "orphan-ratchet", order) == attr.QUEUE_STEP


def test_an_unknown_position_is_undecidable_and_is_never_folded_onto_either_side(tmp_path):
    """FAIL CLOSED. The unattributable buckets have no position by construction, and a gate the
    hook does not invoke has none either. Guessing -- treating unknown as 'later', or dropping it
    so the pair reads MASKABLE -- would manufacture the flap/queue verdicts this measurement is
    entirely about. Same discipline as the UNATTRIBUTABLE bucket one level up.
    """
    order = attr.gate_order(_fake_root(tmp_path, [TEST_GATE, ORPHAN_GATE], _SOURCES))
    assert attr.NO_BLOCK not in order and attr.UNNAMED not in order
    assert attr.classify_recurrence(attr.RED_TEST, [attr.NO_BLOCK], order) == attr.UNDECIDABLE
    assert attr.classify_transition(attr.RED_TEST, attr.UNNAMED, order) == attr.UNDECIDABLE
    # A gate that IS known, mixed with one that is not, still resolves when the known one PROVES
    # the flap -- one proven later gate is enough, and refusing there would hide a real finding.
    assert attr.classify_recurrence(
        attr.RED_TEST, [attr.NO_BLOCK, "orphan-ratchet"], order) == attr.PROVEN_FLAP


def test_a_missing_hook_yields_no_order_at_all_rather_than_file_order(tmp_path):
    """The order is DERIVED, so its absence must be visible. If `gate_order` fell back to the
    banner table's own listing order, the classification would keep answering confidently from a
    list that has no relationship to what the hook runs -- a private vocabulary drifting from the
    thing it names, one level up from the defect the banner reuse already fixed.
    """
    assert attr.gate_order(tmp_path) == {}
    assert attr.classify_recurrence(attr.RED_TEST, ["orphan-ratchet"], {}) == attr.UNDECIDABLE


def test_a_cause_firing_five_times_is_four_recurrences_and_not_ten():
    """Pairing every occurrence with every later one makes the flap count a function of episode
    LENGTH rather than of flapping, and the longest episode would then dominate the answer purely
    for being long. Consecutive occurrences only; and an uninterrupted repeat is not a recurrence
    at all, because nothing proves the gate was ever cleared between the two.
    """
    seq = [attr.RED_TEST, "orphan-ratchet"] * 4 + [attr.RED_TEST]
    # RED TEST occurs 5 times -> 4 consecutive gaps; orphan-ratchet 4 times -> 3. Not 10 and 6.
    assert len(attr.recurrence_pairs(seq)) == 7
    assert sum(1 for p in attr.recurrence_pairs(seq) if p["cause"] == attr.RED_TEST) == 4
    assert attr.recurrence_pairs([attr.RED_TEST, attr.RED_TEST, attr.RED_TEST]) == []


def test_an_absent_subject_is_refused_and_never_reported_as_zero_outage(tmp_path, capsys):
    """THE FAIL-OPEN DEFECT THIS MODULE SHIPPED WITH.

    Every line this measures was written to the daemon's WORKING copy; the committed copy was
    truncated to 2026-07-17 on 2026-08-31. So a clean checkout, an isolated worktree or a
    `git archive HEAD` extract holds a log with no named outcome in it -- and both landed findings
    published `python3 -m tools.commit_refusal_attribution` as their re-derivation instruction.
    The original answered `0 refusals, share 0.0%, total bounded outage 0.0h`: a fully formatted,
    entirely confident report that the publisher never failed once. An absent subject read as a
    clean result is the comfortable direction, so it must REFUSE and say which copy it read.
    """
    log = tmp_path / "sim-runner-log.md"
    log.write_text("\n".join(_cycle("2026-07-0{} 10:00".format(i), refused=False)
                             for i in range(1, 5)))
    assert attr.main(["--log", str(log)]) == 2
    out = capsys.readouterr().out
    assert out.startswith("REFUSED:")
    assert "2026-08-31" in out and "working copy" in out
    # The refusal must REPLACE the report, not precede it. A zero printed underneath a warning is
    # still a zero a reader will quote.
    assert "total bounded outage" not in out and "0.0%" not in out


def test_a_red_test_recurrence_is_split_by_node_id_because_red_test_is_a_bucket(tmp_path):
    """`RED TEST` names the gate, not the test. One test re-breaking and two different tests
    breaking in turn are different findings -- the first is a flaky or contended control, the
    second is ordinary traffic -- and both arrive here labelled identically. Where the hook block
    retained the node ids, the two must come out distinguishable.
    """
    def red(node):
        return ("  git/hook output (last 40 lines):\n"
                "FAILED {} - AssertionError\n1 failed, 40 passed".format(node))

    def build(second_red):
        return "\n".join(
            [_cycle("2026-08-20 10:00", refused=True, hook_body=red("tests/t.py::a")),
             _cycle("2026-08-20 11:00", refused=True, hook_body=ORPHAN_HOOK),
             _cycle("2026-08-20 12:00", refused=True, hook_body=red(second_red)),
             _cycle("2026-08-20 13:00", refused=False)])

    root = _fake_root(tmp_path, [TEST_GATE, ORPHAN_GATE], _SOURCES)
    same = attr.recurrence_report(build("tests/t.py::a"), root)
    diff = attr.recurrence_report(build("tests/other.py::b"), root)
    reds = [r for r in same["recurrences"] if r["cause"] == attr.RED_TEST]
    assert len(reds) == 1 and reds[0]["verdict"] == attr.PROVEN_FLAP
    assert reds[0]["same_test"] is True
    assert [r["same_test"] for r in diff["recurrences"] if r["cause"] == attr.RED_TEST] == [False]


def test_one_hook_file_missing_yields_no_order_rather_than_the_survivor_ranked_first(tmp_path):
    """The partial-hook case, and it INVERTS the order rather than shortening it.

    Found by a surviving mutation: relaxing `gate_order`'s missing-file refusal from `return {}`
    to `continue` still answers `{}` when BOTH hooks are absent, so the whole-repo control above
    passes either way. But with `pre-commit` gone and `commit-msg` present, the survivor's single
    gate is enumerated from index 0 -- and that gate is `write-time`, which really runs LAST, after
    all fifteen others. Every classification would then be computed against an order that is
    exactly backwards, and would read as confident. Fail closed on ANY missing hook file, not only
    on all of them.
    """
    hooks = tmp_path / "tools" / "git-hooks"
    hooks.mkdir(parents=True)
    (hooks / "commit-msg").write_text('#!/bin/sh\npython3 tools/write_time_gate.py "$1" || exit 1\n')
    assert not (hooks / "pre-commit").exists()
    assert attr.gate_order(tmp_path) == {}
