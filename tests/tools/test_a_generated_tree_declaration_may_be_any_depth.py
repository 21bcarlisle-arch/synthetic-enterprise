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

# The live depth-3 instance and the producer that forced it. Held as data so the failure message
# can name the producer rather than the assertion.
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

    MUTATION THAT REDDENS IT: nest a member under a prefix that is NOT declared -- e.g. replace the
    depth-3 member with `("sim", "weather_cells", "x")` -- and the removal leaves nothing to answer.
    """
    declared = set(fs.GENERATED_TREES)
    nested = [segs for segs in declared
              if any(other != segs and segs[:len(other)] == other for other in declared)]
    assert nested, (
        "no nested member is declared, so this control is asserting nothing. It is kept keyed to "
        "the property rather than deleted, but if the depth-3 member has been withdrawn then "
        "test_the_depth_three_member_is_load_bearing should have said so first -- a silent pass "
        "here beside that red is the tautology this docstring warns about."
    )
    for segs in nested:
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


def test_the_depth_three_member_is_load_bearing() -> None:
    """The population answer, asserted the only way it can fail: REMOVE it and lose a real path.

    A declaration that reaches nothing is furniture, which is the failure mode the two findings
    before this one described from the other side. The member earns its place by putting a TRACKED
    file into the oracle union that nothing else puts there -- and `tracked` is the second half of
    the claim on purpose, because the shape this replaces emitted a path that was not a file at all.

    MUTATION THAT REDDENS IT: drop `("docs", "observability", "scale_probe_10k")` from
    `GENERATED_TREES`. Verified by doing it -- the artefact leaves the union and this goes red while
    every other control in this module and its three siblings stays green.
    """
    assert DEEP_ARTEFACT in _tracked(), (
        f"{DEEP_ARTEFACT} is not tracked by git. The member was declared because a real generated "
        f"file was in NEITHER oracle; if the file is gone the member is furniture and should be "
        f"removed with the reason, not left reaching nothing."
    )
    assert DEEP_ARTEFACT in fs.generated_artefacts(), (
        f"{DEEP_ARTEFACT} is not in the tree-keyed oracle. {DEEP_PRODUCER} builds it as "
        "`... / \"docs\" / \"observability\" / \"scale_probe_10k\" / \"report.json\"`; if that "
        "producer has changed shape, the member no longer reaches anything and the pair-shaped "
        "blindness it was added to close has moved rather than gone."
    )

    original = fs.GENERATED_TREES
    try:
        fs.GENERATED_TREES = tuple(t for t in original if t != DEEP_MEMBER)
        without = fs.generated_artefacts()
    finally:
        fs.GENERATED_TREES = original
    assert DEEP_ARTEFACT not in without, (
        f"{DEEP_ARTEFACT} is reached even without {DEEP_MEMBER} declared, so the member adds "
        "nothing and this control was passing on somebody else's work. Either another declaration "
        "now covers it -- in which case remove this one -- or the oracle stopped being keyed to "
        "declared trees, which is a much larger thing."
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
    assert set(fs._WHOLE_PATH_PREFIXES) == {p + "/" for p in expected}, (
        "`_WHOLE_PATH_PREFIXES` disagrees with the declared set -- the whole-string spelling of "
        "the SAME trees has stopped being derived from it, so a path spelled as one constant "
        "under the deeper prefix reaches one oracle and not the other."
    )
