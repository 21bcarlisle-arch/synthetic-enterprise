"""The hook-chain series holds PER-CHAIN costs, and a landing that lost races holds several.

THE DEFECT THIS CLOSES (2026-09-17). `_land_publish_commit` times the whole
`surgical_land.land(attempts=PUBLISH_LAND_ATTEMPTS)` call with one stopwatch. That call RE-GATES
after a lost compare-and-swap, so the elapsed time can hold `len(lost) + 1` full chains -- and
the producer wrote that TOTAL into a series whose ceiling, banding, headroom ratio and sole
reader all speak one chain.

Measured: `b55667741` lost both attempts and recorded **666.95s**, two chains of ~333s. The
reader's discriminator drops a multi-chain row only when its TOTAL clears `ceiling_seconds`
(880), so 666.95 was kept and read as ONE chain costing 667s. That redded
`test_the_deadline_has_headroom_over_what_THIS_MACHINE_actually_costs_today` on
`worst <= 0.75 * 880` -- 666.95 against 660.0, missing by seven seconds -- and a red in
`tests/background/` refuses every ordinary commit in the shared tree, the publisher's own
liveness heartbeat included. No re-measurement could clear it: the remedy the assertion names is
to re-measure the committed constant, and the failing comparison does not contain that constant.
A deadline cannot be made generous against a number that counts two of the thing it bounds.

WHY THE PRODUCER AND NOT THE READER. A threshold-shaped discriminator can only catch the
multi-chain rows that happen to be large; the producer knows the count exactly, every time. The
2026-09-16 repair chose the threshold and left this door open, which is why the same defect
arrived twice in two days through two different sizes of the same row.

KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. These assert the relationship "what is recorded is
what the ceiling bounds" -- one chain -- rather than any particular duration, so they stay true
when the machine gets faster, when PUBLISH_LAND_ATTEMPTS moves, and when the series is empty.
"""

import inspect

import background.process_run_complete as prc
import background.suite_duration_watch as _sdw

#: The real writer's parameters, read ONCE at import and deliberately not inside `_recorded`.
#: A test that calls `_recorded` twice has already patched `sdw.record_gate_run` by the second
#: call, so a signature read there binds against the STUB -- `(*args, **called_with)` accepts
#: everything and `bound.arguments` comes back as `{"args": ..., "called_with": ...}`: a
#: non-empty dict holding none of the names asserted over, which fails as a `KeyError` on the
#: instrument rather than a verdict. Caught by the first run of the repaired file.
_WRITER_SIGNATURE = inspect.signature(_sdw.record_gate_run)


def _recorded(monkeypatch, elapsed, **kwargs):
    """Drive the real recorder and return the arguments it handed the shared series writer.

    THE STUB'S PARAMETERS ARE THE REAL WRITER'S, READ OFF IT (2026-09-18), AND THIS FILE IS THE
    REASON. It landed at `387798957` with a hand-typed five-parameter stub. Three hours later
    `8cb9a6b96` added `chains=` to the call in `_record_commit_hook_duration` to put the count on
    the row -- the stub raised `TypeError`, the recorder's documented NEVER RAISES swallow ate it,
    `seen` came back EMPTY, and all four controls below reported `KeyError: 'duration'`. A red in
    `tests/background/` refuses every commit in the shared tree, so the repair that finally
    recorded the chain count is what wedged the publish path from 18:24 UTC until 2026-09-18.

    Binding through the live signature is not politeness about future parameters: it means the
    stub accepts exactly what the writer accepts and refuses exactly what it refuses, so the
    stand-in cannot drift from its subject at all. A `**kwargs` stub would also have stayed
    green -- and would have gone on being green if the caller started passing a keyword the
    writer had REMOVED, which is the same defect pointing the other way.
    """
    seen = {}

    def _fake_record_gate_run(*args, **called_with):
        bound = _WRITER_SIGNATURE.bind(*args, **called_with)
        bound.apply_defaults()
        seen.update(bound.arguments)
        return None

    monkeypatch.setattr(_sdw, "record_gate_run", _fake_record_gate_run)
    prc._record_commit_hook_duration(elapsed, "deadbeef1", "refused", **kwargs)
    assert seen, (
        "`_record_commit_hook_duration` never reached the series writer, so there is no evidence "
        "here to assert over. It NEVER RAISES by design: anything that goes wrong between the "
        "call and the writer -- a moved import, a parameter this stub will not accept -- arrives "
        "as an EMPTY dict, and without this line every assertion below reports a `KeyError` on "
        "its own instrument instead of a verdict about its subject. An empty evidence set is not "
        "a passing one, and it is not a readable failure either."
    )
    return seen


def test_a_landing_that_lost_two_races_records_one_chain_not_three(monkeypatch):
    """MUTATION: drop the `/ chains` division and this reds at 900.0 against 300.0."""
    seen = _recorded(monkeypatch, 900.0, chains=3)
    assert seen["duration_seconds"] == 300.0, (
        "a 900s stopwatch spanning THREE gated chains must reach the series as one chain's "
        "300s: the ceiling it is graded against bounds one `git commit`, so a total is a "
        "measurement of something the deadline does not bound"
    )


def test_the_ordinary_single_chain_landing_is_unchanged(monkeypatch):
    """The repair must not move the 99% case -- a won-first-time landing is one chain."""
    assert _recorded(monkeypatch, 412.5, chains=1)["duration_seconds"] == 412.5
    assert _recorded(monkeypatch, 412.5)["duration_seconds"] == 412.5, (
        "the default must stay 1: every caller outside the lander records a single chain and "
        "none of them should have to say so"
    )


def test_a_nonsense_chain_count_over_reports_rather_than_shrinking(monkeypatch):
    """FAIL-SAFE DIRECTION, asserted rather than described.

    A broken caller must push this series toward over-reporting the cost -- the direction every
    consumer is already safe in -- never toward reporting a chain as cheaper than it was. A
    division by 0 or by a bool is the shape that would otherwise raise or silently shrink.

    THE COUNT ON THE ROW IS GRADED TOO (2026-09-18), because it is what a reader uses to tell a
    divided row from the nine days of totals behind it. Writing the nonsense value through while
    dividing by one would leave the series saying "this row holds 1.5 chains", and the reader
    that believes it has no way back to the honest reading.
    """
    for bad in (0, -2, None, "2", 1.5, True):
        seen = _recorded(monkeypatch, 500.0, chains=bad)
        assert seen["duration_seconds"] == 500.0, (
            "chains={!r} must be read as ONE chain, leaving the total intact".format(bad)
        )
        assert seen["chains"] == 1, (
            "chains={!r} was read as one chain for the division but reached the row as {!r}: a "
            "reader differencing the two gets a per-chain cost this recorder never wrote"
            .format(bad, seen["chains"])
        )


def test_the_recorded_value_is_the_one_the_ceiling_bounds(monkeypatch):
    """THE WHOLE POINT, as one assertion: what is written is comparable to what it is graded by.

    MUTATION: restore the total and this reds, because 1200s is not a quantity
    GIT_COMMIT_HOOK_TIMEOUT_SECONDS bounds -- two chains of 600 both fit under 880 while their
    sum does not.
    """
    seen = _recorded(monkeypatch, 1200.0, chains=2)
    assert seen["ceiling_seconds"] == prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS
    assert seen["duration_seconds"] <= seen["ceiling_seconds"], (
        "two 600s chains each fit inside the 880s deadline; their 1200s sum does not, and "
        "recording the sum is what makes a satisfiable deadline look unsatisfiable"
    )


def test_every_landing_outcome_declares_its_chain_count():
    """THE LEG THAT CATCHES THE NEXT ONE. `_land_publish_commit` has THREE exits that record --
    refused, raised, and passed -- and the 2026-09-17 defect would have survived a repair that
    fixed only the refusal path, because the `pass` row is the one the headroom control most
    wants. So the control is over the WHOLE partition rather than one leg per exit.

    MUTATION: drop `chains=` from any one of the three calls and this reds naming the count.
    """
    import inspect

    source = inspect.getsource(prc._land_publish_commit)
    recorded = source.count("_record_commit_hook_duration(")
    declared = source.count("chains=_chains_run(")
    assert recorded >= 3, (
        "expected the lander's three recording exits (refused / raised / passed); found "
        "{} -- if an exit was added or removed, this control needs to see it".format(recorded)
    )
    assert declared == recorded, (
        "{} of {} recording exits in `_land_publish_commit` declare their chain count. Every "
        "one of them is reached with `lost` populated, so an exit that stays silent writes a "
        "multi-chain total into a per-chain series -- which is the defect this file "
        "closes".format(declared, recorded)
    )


def test_an_exhausted_landing_counts_the_chains_that_RAN_not_one_more():
    """THE OFF-BY-ONE, AND IT IS THE ONLY CASE PRODUCTION HAS EVER PRODUCED.

    `on_lost` fires after a chain has already run, so `len(lost)` counts COMPLETED chains. When
    the loop EXHAUSTS its attempts there is no further chain to add -- and both multi-chain rows
    this machine has recorded (`2c89bd534`, `b55667741`) are exhaustions. A flat `len(lost) + 1`
    would have divided b55667741's 666.95s by three and filed 222s as a chain cost that was
    really 333s, which INVENTS headroom in a control whose whole job is to refuse when headroom
    has gone.

    ONE ASSERTION OVER THE WHOLE PARTITION rather than a leg per ending, because a counter that
    returns the same number for both endings passes any single-ending test.

    MUTATION: make `_chains_run` ignore its argument (return `len(lost) + 1` always, or
    `len(lost)` always) and this reds -- the two endings must not agree.
    """
    import inspect

    source = inspect.getsource(prc._land_publish_commit)
    namespace: dict = {}
    # Rebuild the helper alone, against a `lost` of known size, so the two endings can be
    # compared without driving a real landing.
    body = source[source.index("def _chains_run("):source.index("def _on_lost(")]
    exec("lost = [1, 2]\n" + "\n".join(  # noqa: S102 -- the subject IS this source text
        line[4:] if line.startswith("    ") else line for line in body.splitlines()), namespace)
    chains_run = namespace["_chains_run"]

    assert chains_run(True) == 2, (
        "two lost attempts that exhausted the loop ran TWO chains; counting a third divides the "
        "stopwatch by one too many and reports a chain as cheaper than it was"
    )
    assert chains_run(False) == 3, (
        "two lost attempts followed by a chain that returned a verdict ran THREE chains"
    )
    assert chains_run(True) != chains_run(False), (
        "the two endings must be counted apart -- a counter blind to how the loop ended is the "
        "defect this leg exists to catch"
    )
