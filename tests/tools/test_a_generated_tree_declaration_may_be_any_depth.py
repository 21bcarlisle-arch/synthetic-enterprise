#!/usr/bin/env python3
"""R15 proof that a generated-tree declaration is a PATH PREFIX, and for the floor it keeps.

REUSE: tests/tools/test_a_generated_tree_declaration_may_be_any_depth.py
CLASS: CUSTOM
INDEX: searched "generated tree", "file_scope", "declaration depth", "path prefix", "segment pair".
       Three sibling controls cover `tools/file_scope_generated_paths.py` and none covers this.
       `test_file_scope_generated_paths.py` proves the STARVATION gate and the freeze's
       shrink-only property, keyed to `offends()` and `gate_violations()`; it says nothing about
       the SHAPE of a member. `test_a_generated_tree_may_hold_an_authored_document.py` proves
       `AUTHORED_UNDER_A_GENERATED_TREE`, the per-path hatch on a prefix refusal, and
       `test_a_generated_tree_may_hold_an_unreproducible_record.py` proves the other hatch. Both
       take the declared set as given and ask what may be excepted FROM it; this asks what may be
       admitted TO it. Extending either would put a question about the declaration's type inside a
       module whose whole subject is the exceptions to it.

THE DEFECT IT NAMES (delivery seat, 2026-09-15). `GENERATED_TREES` held `(parent, child)` pairs, so
a generated tree one segment deep or three could not be DECLARED. Two consecutive findings named
that as a structural limit and acted on neither -- which is how a named gap becomes furniture --
and the census that named it published only its two-segment rows, so the limit never acquired a
count either.

WHAT THE PAIR SHAPE ACTUALLY COST, which is more than "a deeper tree cannot be declared". The match
is a MEMBERSHIP test over an assignment's string constants and the path it emits is HARD-JOINED
from the declared pair. `simulation/premise_population.py:1189` writes
`... / "docs" / "observability" / "scale_probe_10k" / "report.json"`; `docs` and `observability`
both matched, `scale_probe_10k` carries no artefact suffix and was dropped, and the oracle emitted
`docs/observability/report.json` -- which is not a file. So the real artefact was in NEITHER oracle
and the reconciler was offering a LANDING on a producer's output, while a path that does not exist
sat in the generated set claiming to be one. The fabrication half is a SEPARATE defect with its own
finding and its own count (7 sites); this module is the expressiveness half.

WHY THE FLOOR IS THE LOAD-BEARING LEG AND NOT A STYLE RULE. Widening a membership test downward is
the one direction this change is dangerous in. A two-segment member needs two independent string
constants to coincide in one assignment; a ONE-segment member needs a coincidence that happens
constantly -- every assignment in the repo that merely mentions `"site"` beside any `.json` name
would emit `site/<that name>` into the generated set, and the remedy a consumer applies to a
generated path is REVERT. The census found nothing wanting a depth-1 declaration (5 top-level
directories hold a write-reached file, the densest is `site` at 0.103, all overwhelmingly
authored), so the floor costs nothing today and is asserted rather than left to a comment.

EVERY LEG IS KEYED TO A PROPERTY AND NOT TO TODAY'S SET, and each names the mutation that reddens
it, because a control over a declaration list is exactly the shape that passes by describing
itself.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from tools import file_scope_generated_paths as fs

PROJECT = Path(__file__).resolve().parents[2]

# The depth-3 instance that forced the widening, and the producer that builds it. It is NO LONGER
# DECLARED -- ordered reconstruction reaches it under `("docs", "observability")` -- and it is kept
# here as the live subject of the nested-destination control below, which asserts exactly that.
# Held as data so a failure message can name the producer rather than the assertion.
DEEP_MEMBER = ("docs", "observability", "scale_probe_10k")
DEEP_ARTEFACT = "docs/observability/scale_probe_10k/report.json"
DEEP_PRODUCER = "simulation/premise_population.py"


def _tracked() -> set[str]:
    out = subprocess.run(["git", "ls-files"], cwd=PROJECT, capture_output=True,
                         text=True, check=True).stdout.split()
    return set(out)


def test_a_declaration_may_not_be_one_segment_deep() -> None:
    """THE FLOOR. A member is a path prefix of any depth AT OR ABOVE TWO.

    The property, not the count: the segment match is `all(seg in parts for seg in segs)` over one
    assignment's string constants, so the evidence a member demands is the COINCIDENCE of its
    segments. One segment is not a coincidence -- `"site"` and `"docs"` appear as bare constants
    throughout this tree -- and a member that cheap would emit a path per artefact name in scope
    into a set whose consumer's remedy is REVERT.

    MUTATION THAT REDDENS IT: append `("site",)` to `GENERATED_TREES`. Verified by doing it.
    """
    shallow = [segs for segs in fs.GENERATED_TREES if len(segs) < 2]
    assert not shallow, (
        f"{shallow} declared with fewer than two segments. The segment match is a membership test "
        "over one assignment's string constants, so a one-segment member fires on any assignment "
        "that merely mentions that directory name and emits a path per artefact name in scope. "
        "The consumer's remedy for a generated path is REVERT, so the cost of a wrong member is a "
        "lane's real work. If a genuinely one-segment generated tree exists, it needs a different "
        "mechanism than this membership test, not a shorter tuple."
    )


def test_a_nested_declaration_is_subsumed_by_its_parent_at_the_gate() -> None:
    """A member NESTED inside another may not move `offends()`, and that is why it needed no
    freeze re-measurement where `("docs", "status")` did.

    THE PROPERTY IS SUBSUMPTION AND IT IS ASKED THE ONLY WAY THAT CAN FAIL: each nested member is
    REMOVED, and a path under it must still offend on the strength of the remaining prefixes alone.
    Asserting it with the member present would be a tautology -- the prefix it just added answers
    for itself.

    WHY IT MATTERS RATHER THAN BEING PEDANTRY. The rule this project pays for is that widening the
    prefix set without re-measuring `FROZEN` leaves a STALE freeze that refuses EVERY lane's commit.
    A nested member is exempt from that rule and a first-level one is not, so the distinction has
    to be checkable rather than remembered -- someone adding `("docs", "reports", "2026")` is safe
    and someone adding `("sim", "weather_cells")` is not, and nothing else here says which.

    MUTATION THAT REDDENS IT: nest the probe member under a prefix that is NOT declared -- e.g.
    `("sim", "weather_cells", "x")` -- and the removal leaves nothing to answer.

    THE NESTED MEMBER IS MANUFACTURED NOW, AND THAT IS THE FIX FOR A CONTROL WITH NO SUBJECT
    (delivery seat, 2026-09-15). This used to assert that a nested member was DECLARED and then walk
    the live ones. The only one there has been was withdrawn the moment ordered reconstruction made
    it furniture, so the live list emptied and the loop asserted nothing -- the docstring above
    predicted exactly that and told the next reader it would be a silent pass. A rule the next
    person to declare a nested tree needs does not stop being worth holding because nobody has
    declared one today, so the probe member is built here and the live ones are still walked beside
    it. Both halves fail for the same reason and neither depends on the set having an example in it.
    """
    declared = set(fs.GENERATED_TREES)
    live_nested = [segs for segs in declared
                   if any(other != segs and segs[:len(other)] == other for other in declared)]
    # SORTED, not `next(iter(...))`: a set of tuples of strings iterates in an order that moves with
    # `PYTHONHASHSEED`, and a control that probes a different member on every run is one whose green
    # nobody can reproduce.
    manufactured = (*sorted(declared)[0], "a_nested_probe_dir")
    assert any(manufactured[:len(o)] == o for o in declared), (
        f"{manufactured} is not nested under any declared member, so this control would be asking "
        "whether an UNDECLARED prefix offends -- which it must not. `GENERATED_TREES` is empty or "
        "its members are not path prefixes."
    )
    for segs in [*live_nested, manufactured]:
        probe = "/".join(segs) + "/probe.json"
        without = tuple(t for t in fs.GENERATED_TREES if t != segs)
        original = fs.GENERATED_TREES
        try:
            fs.GENERATED_TREES = without
            still = fs.offends(probe, set())
        finally:
            fs.GENERATED_TREES = original
        assert still, (
            f"{segs} is declared inside another member but `offends()` stops answering for "
            f"{probe} once it is removed -- so it is NOT subsumed and it IS a new prefix. A new "
            "prefix makes every `file_scope` entry under it offend at once, and `FROZEN` was "
            "measured against the prefix set WITHOUT it. Re-measure the freeze in the SAME commit "
            "or the tree goes red for every lane, not just this one."
        )


def test_NO_declared_member_is_furniture() -> None:
    """EVERY member must reach something no other member reaches. The class, not the instance.

    THIS CONTROL WAS `test_the_depth_three_member_is_load_bearing` AND IT WENT RED DOING ITS JOB
    (delivery seat, 2026-09-15). It was keyed to one entry, `("docs", "observability",
    "scale_probe_10k")`, admitted the day before because the tree-keyed oracle HARD-JOINED its
    emitted path from the declared prefix and so flattened `.../scale_probe_10k/report.json` to
    `docs/observability/report.json`. Replacing that join with ordered reconstruction emits the
    artefact WHOLE from `("docs", "observability")` alone, the deeper member stopped reaching
    anything, this went red, and its failure message named the remedy -- "another declaration now
    covers it, in which case remove this one". It was removed. The control is generalised here
    rather than re-pointed, because the property it was holding for one entry was never about that
    entry, and a control keyed to today's declaration list goes red when the code becomes MORE
    honest -- which is exactly backwards and is how it behaved.

    THE PROPERTY IS ASKED THE ONLY WAY IT CAN FAIL: each member is REMOVED and the oracle recomputed.
    A member earns its place by taking a path out of the oracle when it goes, or by shrinking the
    effective prefix set `offends()` reads. Asserting it with every member present would be the
    tautology the sibling control's docstring warns about.

    A GATE-ONLY MEMBER IS ALLOWED AND IS NOT A LOOPHOLE. A prefix that reaches no oracle member
    still refuses every `file_scope` entry under it, which is this gate's whole subject, so a member
    whose removal lets a path under it stop offending has earned its place on that alone.

    AND THE GATE LEG ASKS `offends()`, NOT `_tree_prefixes()`, WHICH IS WHERE THE FIRST DRAFT OF
    THIS CONTROL WAS WRONG (delivery seat, 2026-09-15). It compared the raw prefix SET before and
    after, and a nested member ADDS AN ELEMENT to that set while changing nothing `offends()`
    answers -- `offends()` walks `startswith` over every prefix, so a path under
    `docs/observability/scale_probe_10k` is refused by `docs/observability` whether the deeper one
    is declared or not. The set comparison therefore skipped precisely the member class this control
    exists to catch, and the mutation below passed. Caught by running that mutation rather than by
    reading the code, and it is the same subsumption shape the module's own docstrings keep
    pointing at, arriving one level up in a control ABOUT it.

    MUTATION THAT REDDENS IT: re-add `("docs", "observability", "scale_probe_10k")`. Verified by
    doing it: the member is nested, so a probe under it still offends without it, and ordered
    reconstruction reaches its artefact without it -- 216 members with and 216 without.
    """
    original = fs.GENERATED_TREES
    live = fs.generated_artefacts()
    furniture = []
    try:
        for segs in original:
            probe = "/".join(segs) + "/a_probe_artefact.json"
            fs.GENERATED_TREES = tuple(t for t in original if t != segs)
            if not fs.offends(probe, set()):
                continue  # the gate stops refusing under it -- it carries a real prefix
            if fs.generated_artefacts() != live:
                continue  # it reaches an oracle member nothing else reaches
            furniture.append(segs)
    finally:
        fs.GENERATED_TREES = original
    assert not furniture, (
        f"{furniture} reach nothing: removing them changes neither `_tree_prefixes()` nor the "
        "oracle membership, so they are declarations that describe an intention rather than doing "
        "any work. Remove them WITH THE REASON -- a declaration list that keeps entries for things "
        "that no longer reach anything stops being a list anyone can trust, which is the argument "
        "this module already makes about its own freeze list."
    )


def test_the_deep_artefact_is_reached_WITHOUT_a_declaration_of_its_own() -> None:
    """The repair that made the depth-3 member furniture, asserted as the property that replaced it.

    `docs/observability/scale_probe_10k/report.json` is a TRACKED file that a producer builds four
    segments deep, and the reason it once needed its own declaration was a matcher that could not
    emit a path deeper than the prefix it matched. Ordered reconstruction can, so this asserts the
    capability directly: a nested destination arrives WHOLE under a first-level declaration.

    `tracked` is the second half of the claim on purpose. The shape this replaced emitted
    `docs/observability/report.json`, which is not a file at all, so "the oracle contains a path
    that looks right" was exactly the reading that hid the defect for eight weeks.

    MUTATION THAT REDDENS IT: restore the hard join (`found.update(f"{prefix}/{s}" for s in parts
    ...)`). The artefact is then flattened back to `docs/observability/report.json` and leaves the
    oracle. Verified by doing it.
    """
    assert DEEP_ARTEFACT in _tracked(), (
        f"{DEEP_ARTEFACT} is not tracked by git. If {DEEP_PRODUCER} no longer builds it, this "
        "control has lost its subject and the nested-destination capability needs a different live "
        "instance -- not a fixture, which would stop measuring the real tree."
    )
    assert DEEP_MEMBER not in fs.GENERATED_TREES, (
        f"{DEEP_MEMBER} is declared again, which makes this control tautological: the artefact "
        "would be reached by its own prefix and nothing here would be asking about reconstruction. "
        "test_NO_declared_member_is_furniture should have refused it first."
    )
    assert DEEP_ARTEFACT in fs.generated_artefacts(), (
        f"{DEEP_ARTEFACT} is not in the tree-keyed oracle. {DEEP_PRODUCER} builds it as "
        "`... / \"docs\" / \"observability\" / \"scale_probe_10k\" / \"report.json\"`, so either "
        "the producer changed shape or the matcher has gone back to joining the path from the "
        "DECLARED prefix -- which drops `scale_probe_10k` and emits a file that does not exist."
    )


def test_the_declared_set_is_what_both_consumers_read() -> None:
    """The two derived views must both be rebuilt from `GENERATED_TREES`, at whatever depth.

    THE DEFECT THIS WOULD HAVE CAUGHT is the half-done generalisation: widening the tuple type and
    leaving one consumer still unpacking `for a, b in ...`. That does not raise on a 2-tuple, so
    the tree stays green and the deeper member is silently honoured by one view and not the other
    -- which is precisely the shape this module's sibling exists for, a carve-out honoured by one
    of two unioned oracles being no carve-out at all.

    MUTATION THAT REDDENS IT: pin either derived view to `f"{a}/{b}"`. It raises `ValueError` on
    the 3-tuple rather than asserting, which is a redder red than this control needs and is fine.
    """
    expected = {"/".join(segs) for segs in fs.GENERATED_TREES}
    assert fs._tree_prefixes() == expected, (
        "`_tree_prefixes()` disagrees with the declared set -- the gate's prefix view has stopped "
        "being derived from it."
    )
    assert set(fs._whole_path_prefixes()) == {p + "/" for p in expected}, (
        "`_whole_path_prefixes()` disagrees with the declared set -- the whole-string spelling of "
        "the SAME trees has stopped being derived from it, so a path spelled as one constant "
        "under the deeper prefix reaches one oracle and not the other."
    )

    # AND IT IS ASKED OF A SET THAT IS NOT TODAY'S, which is the leg the import-time constant could
    # never pass. Both views used to be rebuilt from `GENERATED_TREES` -- one at call time and one
    # ONCE, at import -- and the two read identically until something moved the declaration list.
    # Everything that asks what a member is worth moves it, so the frozen view answered for the old
    # set while the live one answered for the new, and every such control measured a difference it
    # had not made. Driving the substitution HERE is what makes that a property of the module rather
    # than a habit of whoever writes the next control.
    original = fs.GENERATED_TREES
    try:
        fs.GENERATED_TREES = (("probe_tree", "probe_child"),)
        assert fs._tree_prefixes() == {"probe_tree/probe_child"}
        assert set(fs._whole_path_prefixes()) == {"probe_tree/probe_child/"}, (
            "a derived view did not follow `GENERATED_TREES` when it changed, so it is stored "
            "rather than derived. Every control that removes a member and recomputes is then "
            "measuring the OLD declaration set through that view, and passes on a difference it "
            "never made."
        )
    finally:
        fs.GENERATED_TREES = original
