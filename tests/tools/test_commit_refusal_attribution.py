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


LEVEL_HOOK = ("  git/hook output (last 40 lines):\n"
              "[level-gate] ❌ unauthorized level move\n364 passed in 40s")
SITE_HOOK = ("  git/hook output (last 40 lines):\n"
             "[site-lane] ❌ a site door is red\n364 passed in 40s")


def _episode(bodies):
    """One bounded episode whose refusals carry `bodies`, in order, then a landing."""
    log = "\n".join(
        [_cycle("2026-08-20 {:02d}:00".format(i), refused=True, hook_body=b)
         for i, b in enumerate(bodies)]
        + [_cycle("2026-08-20 23:00", refused=False)])
    return attr.ordering_report(log)[0]


def test_a_needle_absent_from_its_emitter_yields_no_rank_rather_than_the_first_position():
    """THE FAIL-OPEN THIS MODULE ALMOST SHIPPED. Gate banners are written as adjacent string
    literals split across source lines, so a runtime needle need not occur contiguously in the
    file that prints it. `.find()` returns -1, and treating -1 as offset 0 ranks that gate FIRST
    inside its emitter -- the strongest position available. Every later cause would then look
    like a step back to it, i.e. an ESTABLISHED re-arrival, manufactured out of a failed lookup.
    None is the only safe answer, and the cause must leave the analysis."""
    assert attr._needle_pos("nothing like it here", "❌ A BANNER THIS FILE NEVER PRINTS") is None
    assert attr._needle_pos("... [level-gate] ❌ ...", "[level-gate] ❌") == 4
    ranks = attr.gate_ranks(hook_text="python3 tools/only_gate.py || exit 1",
                            emitter_texts={"tools/only_gate.py": "no banner in here"})
    # The write-time gate is exempt: it is not in the pre-commit file at all (commit-msg runs it
    # after the whole chain), so its position is structural rather than looked up.
    in_chain = {k: v for k, v in ranks.items() if v[0] != attr._AFTER_PRE_COMMIT}
    assert in_chain == {}, "a gate whose banner was never found kept a rank: {}".format(in_chain)


def test_a_short_but_exact_needle_is_ranked_and_not_dropped_by_the_shrink_floor():
    """The over-correction for the defect above, caught by printing the table. A floor applied to
    the needle ITSELF rather than to the shrinking dropped `[level-gate] ❌`, `[site-lane] ❌` and
    `[scope-evidence] ❌` -- three of the commonest causes in the log -- leaving an analysis that
    read as clean because its biggest gates had silently left it."""
    ranks = attr.gate_ranks()
    for cause in ("level-promotion gate", "site-lane gate", "scope-evidence ratchet"):
        assert cause in ranks, "{} lost its rank; the analysis is blind to it".format(cause)


def test_the_rank_order_is_the_hooks_invocation_order_and_not_a_table_written_here():
    """Keyed to the ENFORCEMENT. `process_run_complete` carries a comment asserting its classifier
    table is the chain's order; a comment cannot be checked and this is why the order is derived
    from `tools/git-hooks/pre-commit` instead. Reorder the hook and this goes red, which is the
    point: a stale rank table would silently invert every backward-step verdict below."""
    ranks = attr.gate_ranks()
    hook = attr.HOOK.read_text(encoding="utf-8")
    order = attr._hook_order(hook)
    for name, _, emitter in attr._REFUSING_GATE_BANNERS:
        if name in ranks and emitter in order:
            assert ranks[name][0] == order[emitter]
    assert ranks["level-promotion gate"] < ranks["site-lane gate"] < ranks["orphan-ratchet"]


def test_pytest_ranks_last_inside_its_emitter_so_a_red_test_proves_the_earlier_checks_passed():
    """The fact that makes the largest episode in the log analysable at all. finding-class,
    finding-severity and RED TEST share one emitter and one chain position, so ranking them equal
    would make the 68.8h episode's finding-class/RED-TEST alternation untestable. `main()` runs
    the consolidation check second and invokes pytest LAST, so a named red test is a positive
    observation that finding-class passed that cycle."""
    ranks = attr.gate_ranks()
    assert (ranks["finding-class consolidation"] < ranks["finding-severity gate"]
            < ranks[attr.RED_TEST])
    assert ranks["finding-class consolidation"][0] == ranks[attr.RED_TEST][0]


def test_only_a_step_to_a_lower_rank_is_established_and_a_forward_step_never_is():
    """THE WHOLE INFERENCE, over the partition rather than one leg. A forward step is what a
    genuine queue AND a set of gates red from the start both produce, so it establishes nothing;
    a step back is a gate that demonstrably passed and then refused. Asserting only the forward
    leg would pass on an analysis that called EVERYTHING uninformative, and asserting only the
    backward leg would pass on one that called everything established."""
    forward = _episode([LEVEL_HOOK, ORPHAN_HOOK])
    backward = _episode([ORPHAN_HOOK, LEVEL_HOOK])
    assert not forward["established"] and forward["backward_steps"] == []
    assert backward["established"] and len(backward["backward_steps"]) == 1
    assert backward["backward_steps"][0]["cause"] == "level-promotion gate"


def test_a_repeated_cause_is_persistence_and_not_a_re_arrival():
    """A tie is not a step back. The gate was named, and still refuses -- nothing passed in
    between, so nothing went passing->refusing. Fail-closed: the ambiguous case is scored as
    uninformative, the direction that makes the result WEAKER."""
    same = _episode([ORPHAN_HOOK, ORPHAN_HOOK, ORPHAN_HOOK])
    assert not same["established"] and not same["recurrence"]


def test_an_unattributable_cycle_between_two_named_ones_neither_creates_nor_hides_a_step():
    """Unattributable causes have no rank and are SKIPPED, never imputed. The passed-below-rank
    observation is per-cycle, so an unreadable cycle in between does not break the comparison
    across it -- and it must not be allowed to invent one either."""
    blind = "  git/hook output (last 40 lines):\nsomething nobody has a needle for"
    with_gap = _episode([ORPHAN_HOOK, blind, LEVEL_HOOK])
    without = _episode([ORPHAN_HOOK, LEVEL_HOOK])
    assert with_gap["established"] == without["established"] is True
    assert len(with_gap["backward_steps"]) == len(without["backward_steps"])
    # Three refused cycles, only two of them rankable: the blind one is skipped, not imputed.
    assert with_gap["ranked_causes"] == 2 and with_gap["cycles"] == 3


def test_every_recurrence_implies_a_backward_step_which_is_a_check_on_the_rank_table():
    """ANALYTIC, not empirical. If a cause appears at i and again at k with a different cause at
    j between them, then either rank(j) > rank(i) -- and the return to rank(i) descends -- or
    rank(j) < rank(i) and the step INTO j already descended. Either way a recurrence cannot exist
    without a backward step. So a recurrence scored as unestablished means the RANK TABLE is
    wrong, not that the gates behaved oddly, and this is the control that says so."""
    for bodies in ([ORPHAN_HOOK, LEVEL_HOOK, ORPHAN_HOOK],
                   [LEVEL_HOOK, ORPHAN_HOOK, LEVEL_HOOK],
                   [SITE_HOOK, ORPHAN_HOOK, LEVEL_HOOK, SITE_HOOK]):
        e = _episode(bodies)
        assert e["recurrence"] and e["established"], bodies


def test_the_ordering_verdict_is_reachable_both_ways_on_one_log():
    """The rare-branch control, over the whole partition in one assertion. A classifier that
    answered `established` for everything, or for nothing, would satisfy every per-episode leg
    above written on its own; this refuses both at once."""
    log = "\n".join([
        _cycle("2026-08-20 01:00", refused=True, hook_body=LEVEL_HOOK),
        _cycle("2026-08-20 02:00", refused=True, hook_body=ORPHAN_HOOK),
        _cycle("2026-08-20 03:00", refused=False),
        _cycle("2026-08-20 04:00", refused=True, hook_body=ORPHAN_HOOK),
        _cycle("2026-08-20 05:00", refused=True, hook_body=LEVEL_HOOK),
        _cycle("2026-08-20 06:00", refused=False)])
    verdicts = [e["established"] for e in attr.ordering_report(log)]
    assert verdicts == [False, True]


def test_a_step_back_is_measured_against_the_running_peak_not_the_previous_cause():
    """AN EQUIVALENCE THE MUTATION PASS FOUND, made into a real control rather than left to the
    reader. Replacing the running maximum with "compare to the previous cause" survives every
    other control here, and for the ESTABLISHED verdict it genuinely is an equivalence: if any
    rank sits below the running peak then some ADJACENT pair must descend, or the sequence would
    be non-decreasing throughout. It is not an equivalence for the COUNT, which the docstring
    claims is "whether or not something else intervened adjacently" -- orphan-ratchet(108) ->
    level-promotion(32) -> site-lane(41) is two gates that each passed and then refused, and the
    previous-cause reading sees only one because 41 > 32."""
    e = _episode([ORPHAN_HOOK, LEVEL_HOOK, SITE_HOOK])
    assert e["established"]
    assert [s["cause"] for s in e["backward_steps"]] == ["level-promotion gate", "site-lane gate"]


# --- The subject, and what the same early exit costs the cause split -------------------------

def test_an_absent_subject_is_refused_and_never_reported_as_zero_outage(tmp_path, capsys):
    """THE FAIL-OPEN DEFECT THIS MODULE SHIPPED WITH, found re-running it from a clean worktree.

    The log is tracked, but its committed copy was truncated to 2026-07-17 on 2026-08-31 and every
    line this module measures has been written to the daemon's WORKING copy since. So a clean
    checkout, an isolated worktree, CI or a `git archive HEAD` extract holds a file with no named
    outcome in it -- and three findings now publish `python3 -m tools.commit_refusal_attribution`
    as their re-derivation instruction. From one of those the module printed `0 refusals`,
    `share 0.0%`, `total bounded outage: 0.0h`: a complete, confidently formatted report that the
    publisher had never once failed, produced by an ABSENT subject rather than a clean one.
    """
    log = tmp_path / "sim-runner-log.md"
    log.write_text("\n".join(_cycle("2026-07-0{} 10:00".format(i), refused=False)
                             for i in range(1, 5)))
    assert attr.main(["--log", str(log)]) == 2
    out = capsys.readouterr().out
    assert out.startswith("REFUSED:")
    assert "2026-08-31" in out and "working copy" in out
    # The refusal REPLACES the report; it does not precede one. A zero printed underneath a
    # warning is still a zero a reader will quote.
    assert "total bounded outage" not in out and "0.0%" not in out


def test_a_deeper_gate_being_named_is_the_only_thing_that_proves_a_shallower_one_passed():
    """The exposure table's whole inference, and it must not be symmetric.

    A cycle naming a DEEPER gate proves this one passed. A cycle naming a SHALLOWER one proves
    nothing -- this gate was never reached. Counting the second as evidence of passing would turn
    the deepest gates, which are the least observed, into the best-evidenced, which is exactly
    backwards; and it is the error that makes a gate with no refusals read as a gate that never
    broke.
    """
    ranks = {"shallow": (1, 0), "deep": (9, 0)}
    log = "\n".join([_cycle("2026-08-20 10:00", refused=True, hook_body=ORPHAN_HOOK),
                     _cycle("2026-08-20 11:00", refused=False)])
    seq = [c for c in attr.cycles(log) if c["outcome"] == "commit_refused"]
    assert len(seq) == 1  # one refused cycle, whose cause is neither of the two ranked names

    def rows(cause):
        text = "\n".join([_cycle("2026-08-20 10:00", refused=True, hook_body=ORPHAN_HOOK),
                          _cycle("2026-08-20 11:00", refused=False)])
        return attr.masking_exposure(text.replace(attr.RED_TEST, cause), ranks)

    # `orphan-ratchet` is not in `ranks`, so it is ignorance for both -- never proven passing.
    out = rows("orphan-ratchet")
    assert out["shallow"]["proven_passing"] == 0 and out["shallow"]["unknown"] == 1
    assert out["deep"]["proven_passing"] == 0 and out["deep"]["unknown"] == 1


def test_the_deepest_gate_is_unknown_on_every_refused_cycle_it_did_not_itself_name():
    """The result that makes this table worth printing.

    The write-time gate runs after the entire pre-commit chain, so it is reached only when all
    fifteen gates before it pass. In the measured window it is named zero times AND proven passing
    zero times -- its state is unknown on every refused cycle. A reader who takes `by_gate`'s
    silence about it as "this gate never blocked a publish" has read a fact about the chain's
    order as a fact about the gate.
    """
    hook = "\n".join(["python3 tools/pre_commit_test_gate.py || exit 1",
                      "python3 tools/orphan_ratchet.py || exit 1"])
    ranks = attr.gate_ranks(hook_text=hook, emitter_texts={
        "tools/pre_commit_test_gate.py": 'x = [sys.executable, "-m", "pytest"]\n',
        "tools/orphan_ratchet.py":
            'print("orphan-ratchet: THIS COMMIT ADDS WORK THAT NOTHING RUNS")\n'})
    log = "\n".join([_cycle("2026-08-20 1{}:00".format(i), refused=True, hook_body=RED_HOOK)
                     for i in range(3)] + [_cycle("2026-08-20 19:00", refused=False)])
    out = attr.masking_exposure(log, ranks)
    # `gate_ranks` ranks the commit-msg gate after the whole pre-commit chain, so it is deepest
    # by construction -- which is exactly why it is the one nothing can observe.
    assert max(ranks, key=lambda g: ranks[g]) == "write-time gate"
    for deep in ("write-time gate", "orphan-ratchet"):
        assert out[deep]["named"] == 0, deep
        assert out[deep]["proven_passing"] == 0, deep
        assert out[deep]["unknown"] == 3, deep
    # ...while the gate that was actually reached is evidenced on all three.
    assert out[attr.RED_TEST]["named"] == 3
