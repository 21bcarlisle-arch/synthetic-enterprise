#!/usr/bin/env python3
"""R15 proof for the PER-PATH hatch on a PREFIX refusal, and for the hatch it must never become.

THE DEFECT IT NAMES (delivery seat, 2026-09-15). `offends()` decided a `file_scope` entry by tree
PREFIX and nothing else, so declaring a tree refused EVERY entry under it. That made the bar for a
declaration "every path under this tree is generated" -- strictly stricter than the property the
gate wants, which is *does a `file_scope` naming this STARVE its atom* -- and the frame before this
one declined two probably-real generated trees on exactly that bar, writing the reason down as
structural rather than evidential. A starvation door left open for want of a mechanism is the wrong
kind of open, so the mechanism is `AUTHORED_UNDER_A_GENERATED_TREE` and this is its proof.

THE SECOND DEFECT IS THE REPAIR ITSELF, and it is the one that would have cost something. The item
that drew this said to build the exception "the way the two oracles already have
`WRITTEN_BUT_NOT_REPRODUCIBLE`". Sharing that SET would be a fail-open in the shape this module
exists to close: that list holds paths a module REWRITES and cannot reproduce, and an accumulated
ledger is irreproducible precisely BECAUSE every run rewrites it -- maximally dirty, maximally
starving. `site/state/live_decisions_log.jsonl` would have been its first member under the newly
declared trees. So the two sets are held disjoint here, by a control, and the ledger is asserted to
go on offending.

BOTH FAILURE DIRECTIONS ARE KEYED TO THE PROPERTY, NOT TO TODAY'S MEMBERSHIP, because this set has
no live `file_scope` exercising it -- measured, and predicted in advance as the question most
likely to fail:
  * a member that becomes WRITE-REACHED is a real generator this set is hiding (fail-open), and
  * a member no longer under a declared prefix is dead weight the prefix test already handles.
Neither is a snapshot; both go red on a change to the tree and stay green as the tree grows.
"""
from __future__ import annotations

import textwrap
from pathlib import Path

from tools import file_scope_generated_paths as fs

# The live instance. `docs/reports` is 33 tracked files: 32 are a run's output (9 write-reached,
# the rest written under computed names like `path.stem + "_svt_segment_decisions.json"`, eight
# carrying their own `how_to_regenerate` or `producing_commit` key) and this one is hand-written
# prose no module anywhere writes.
AUTHORED = "docs/reports/REPORTING_BACKLOG.md"
# Its neighbour in the same tree, rendered by `saas/reporting/annual_report.py`. The control that
# the tree really is declared -- without it every assertion about `AUTHORED` could be passing
# because the prefix went away rather than because the hatch works.
GENERATED_NEIGHBOUR = "docs/reports/ANNUAL_REPORT.md"
# The path that must NOT be exempt, and the reason the two hatches are separate sets. An append
# ledger every run adds to is the starving shape itself.
THE_LEDGER_THAT_MUST_STILL_OFFEND = "site/state/live_decisions_log.jsonl"
NEWLY_DECLARED = (("site", "state"), ("docs", "reports"))


# ---------------------------------------------------------------------------
# The predicate, driven over the whole partition in one control
# ---------------------------------------------------------------------------
def test_MUTATION_the_authored_document_is_exempt_and_everything_around_it_is_not():
    """ONE control over the partition rather than a leg per branch, because a hatch that exempts
    EVERYTHING passes a test that only asks whether it exempts the one path.

    Emptying `AUTHORED_UNDER_A_GENERATED_TREE` fails the first assertion. Widening it to the tree,
    or dropping either new `GENERATED_TREES` entry, fails one of the rest.
    """
    generated = fs.generated_artefacts()
    assert not fs.offends(AUTHORED, generated), (
        f"{AUTHORED} is hand-written prose no module writes, and the gate refuses it with "
        "`Scope the GENERATOR, not the generated` -- naming a generator that does not exist")
    assert fs.offends(GENERATED_NEIGHBOUR, generated), (
        "the authored document's own tree no longer refuses a rendered report, so the exemption "
        "above may be passing because `docs/reports` stopped being declared")
    assert fs.offends("docs/reports", generated) and fs.offends("docs/reports/", generated), (
        "the tree itself is no longer refused in both live spellings, which is the declaration "
        "G13 actually made and the one the whole gate was extracted from")
    assert fs.offends(THE_LEDGER_THAT_MUST_STILL_OFFEND, generated), (
        "an append ledger every run writes to is exempt from the starvation gate -- the fail-open "
        "that sharing `WRITTEN_BUT_NOT_REPRODUCIBLE` would have caused")


def test_the_two_hatches_are_DISJOINT_and_must_stay_so():
    """The two sets read as interchangeable and are opposite on the decisive case. A path cannot be
    both 'rewritten whole by a module, irreproducibly' and 'written by no run at all', so an overlap
    is not a judgement call -- it is one of the two entries being wrong about its own subject."""
    overlap = sorted(fs.AUTHORED_UNDER_A_GENERATED_TREE & fs.WRITTEN_BUT_NOT_REPRODUCIBLE)
    assert overlap == [], (
        f"{overlap} is claimed both WRITTEN-but-irreproducible and authored-so-never-written. "
        "If the write evidence is real the path starves an atom and must keep offending; if it is "
        "not, the path does not belong in the irreproducible carve-out either")


# ---------------------------------------------------------------------------
# Both failure directions, over the LIVE tree
# ---------------------------------------------------------------------------
def test_no_exempt_path_is_WRITE_REACHED_or_the_hatch_is_hiding_a_generator():
    """THE FAIL-OPEN DIRECTION, and the control that makes this set shippable at all.

    `offends()` has no live `file_scope` exercising the exemption today, so no assertion about
    `violations()` can fail on tree state. This one can, every run: the moment any module in a
    scanned tree acquires a resolvable write site for an exempt path, the path IS generated, an atom
    declaring it WILL starve, and the exemption has become the invisible G13 defect wearing a
    comment that says otherwise.
    """
    reached = sorted(fs.AUTHORED_UNDER_A_GENERATED_TREE & fs._write_reached_paths())
    assert reached == [], (
        f"{reached} now has a write site, so the gate is being told to permit a `file_scope` on "
        "ground a generator rewrites. Remove the entry -- do not widen the comment")


def test_every_exempt_path_is_UNDER_a_declared_prefix_or_it_is_dead_weight():
    """THE OTHER DIRECTION. An exemption outside every declared tree exempts a path the prefix test
    was never going to refuse, so it buys nothing and hides the fact that it buys nothing. Keyed to
    `GENERATED_TREES` rather than to a literal list, so retiring a tree reddens this instead of
    leaving a member quietly inert."""
    prefixes = tuple(f"{a}/{b}/" for a, b in fs.GENERATED_TREES)
    stranded = sorted(p for p in fs.AUTHORED_UNDER_A_GENERATED_TREE
                      if not p.startswith(prefixes))
    assert stranded == [], (
        f"{stranded} is exempt from a prefix refusal that does not apply to it. Either the tree it "
        "sits in was undeclared -- in which case delete the entry -- or it was never under one")


def test_the_exemption_does_not_leak_into_the_reconcilers_union():
    """The two oracles feed ONE union, so an exemption honoured by `offends()` alone would leave the
    tree-keyed oracle producing the path and the reconciler offering a REVERT on a hand-written
    document -- the exact one-sidedness the frame before this one was extracted from.

    The subtraction removes zero members on the tree it landed against, which is why this is keyed
    to the property: no exempt path may be in the union, however the oracle's reach grows.
    """
    union = fs.generated_artefacts() | fs.written_artefacts()
    leaked = sorted(fs.AUTHORED_UNDER_A_GENERATED_TREE & union)
    assert leaked == [], (
        f"{leaked} is called authored by the gate and generated by the union, so the reconciler "
        "will advise `git show HEAD:<path> > <path>` and discard whatever a lane wrote in it")


# ---------------------------------------------------------------------------
# That the exempt branch CAN be taken at all, on a fixture, because no live atom takes it
# ---------------------------------------------------------------------------
_FIXTURE_MODULE = '''
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
RENDERED = PROJECT / "docs" / "reports" / "rendered_report.md"


def render(rows):
    RENDERED.write_text(rows, encoding="utf-8")
'''

# A TOP-LEVEL LIST, not `atoms:` -- `maturity_map_store._as_atom_list` refuses a mapping outright,
# which makes `violations()`'s own `(loaded or {}).get("atoms", [])` fallback unreachable. Written
# down because the fallback reads like the two shapes are both supported and only one is.
_FIXTURE_MAP = """
- id: ATOM_on_the_authored_document
  file_scope:
    - docs/reports/handwritten_backlog.md
- id: ATOM_on_the_rendered_one
  file_scope:
    - docs/reports/rendered_report.md
"""


def _fixture_root(root: Path) -> Path:
    (root / "tools").mkdir(parents=True, exist_ok=True)
    (root / "tools" / "report_producer.py").write_text(_FIXTURE_MODULE, encoding="utf-8")
    (root / "docs" / "design").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "design" / "maturity_map.yaml").write_text(
        textwrap.dedent(_FIXTURE_MAP), encoding="utf-8")
    return root


def test_MUTATION_the_exempt_branch_reaches_violations_and_the_unexempt_one_still_does(
        tmp_path, monkeypatch):
    """THE BRANCH IS PROVEN REACHABLE BEFORE IT IS PROVEN CORRECT. This project has entered the
    same trap three times: every leg asks whether a guard refuses correctly, and a guard that
    refuses everything passes all of them. Here the inverse -- there is no live `file_scope` under
    either new tree, so `violations()` cannot demonstrate the exemption on the real map and a
    green suite would mean nothing.

    So a synthetic map declares BOTH paths and the rendered sibling is the control: it must appear
    in `violations()` (the gate reaches this fixture at all) while the exempt one must not.
    Emptying `AUTHORED_UNDER_A_GENERATED_TREE` makes both appear and fails the first assertion.
    """
    _fixture_root(tmp_path)
    monkeypatch.setattr(fs, "AUTHORED_UNDER_A_GENERATED_TREE",
                        frozenset({"docs/reports/handwritten_backlog.md"}))

    found = set(fs.violations(root=tmp_path))
    assert ("ATOM_on_the_rendered_one", "docs/reports/rendered_report.md") in found, (
        "the fixture reaches no violation at all, so the exemption below would pass vacuously")
    assert ("ATOM_on_the_authored_document", "docs/reports/handwritten_backlog.md") not in found, (
        "an atom declaring the one hand-written document in a generated tree is still refused, so "
        "the per-path hatch does not reach the gate")


def test_the_two_newly_declared_trees_are_declared_and_the_freeze_was_re_measured_with_them():
    """A `GENERATED_TREES` addition moves the SUBSUMING predicate, so every `file_scope` entry
    under the new prefix starts offending at once and a freeze measured against the narrower set
    reads STALE -- which refuses EVERY lane's commit, not just the one that widened it. The
    declaration and the re-measured freeze therefore have to be one commit, and this is the leg
    that says so: it goes red if either tree is declared without the freeze being re-measured
    against it, or if the freeze is re-measured and a tree is dropped."""
    for tree in NEWLY_DECLARED:
        assert tree in fs.GENERATED_TREES, f"{tree} is not declared"
    assert fs.gate_violations() == [], (
        "the freeze does not match the live map under the widened prefix set -- every lane's "
        "commit is refused until the declaration and the freeze agree")
