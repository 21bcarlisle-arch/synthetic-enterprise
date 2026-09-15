#!/usr/bin/env python3
"""R15 proof for the WRITE-keyed half of the generated-path oracle.

THE DEFECT IT NAMES (2026-09-15). `generated_artefacts` is keyed to generated TREES -- the
`(parent, child)` segment pairs `site/data`, `docs/observability`, `docs/market_data`. On
2026-09-15 the single path holding the shared tree behind origin was
`docs/design/orphan_baseline.json`: written by `tools/orphan_ratchet.py --freeze`, a photograph of
a scan, living in an otherwise AUTHORED tree. Invisible to a tree-keyed oracle by construction, so
`origin_reconcile._split_generated` called it this tree's work and the refusal led with the
landing recipe -- and landing a local photograph drops whatever rows origin's later freeze
recorded. `written_artefacts` is the second oracle, keyed to the write SITE instead.

THE BOUNDARY IS WRITING vs NAMING, AND BOTH SIDES ARE DRIVEN HERE. Authored paths are assigned as
module constants all over this repository. The remedy a consumer applies to a GENERATED path is
REVERT, so a classifier keyed to naming would quietly discard a lane's real work -- a worse failure
than the one being fixed, because it destroys rather than over-warns. Every leg below therefore has
a partner on the other side of that boundary.

FIXTURES ARE COPIED FROM THE REAL IDIOMS, NOT TUNED UNTIL THEY AGREE. Each synthetic module below
reproduces a shape that is live in this tree today, and the real-tree legs re-ask the same question
of the repository itself so the fixture cannot be the only evidence.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools import file_scope_generated_paths as fs

# Two real paths standing on opposite sides of the boundary. Neither is asserted from memory: the
# leg that uses each one first proves it is on the side it claims.
AUTHORED_TREE_GENERATED = "docs/design/orphan_baseline.json"
NAMED_NEVER_WRITTEN = "docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md"


def _tree(root: Path, **modules: str) -> Path:
    (root / "tools").mkdir(parents=True, exist_ok=True)
    for name, body in modules.items():
        (root / "tools" / f"{name}.py").write_text(body, encoding="utf-8")
    return root


HEADER = (
    "from pathlib import Path\n"
    "ROOT = Path(__file__).resolve().parents[1]\n"
)


# ---------------------------------------------------------------------------
# The boundary: a write site, against a name that only ever gets read
# ---------------------------------------------------------------------------
def test_MUTATION_a_path_written_in_an_authored_tree_is_found(tmp_path):
    """The whole defect, in one fixture: `docs/design` is not a generated tree, and the oracle
    must still find a baseline a ratchet freezes into it. Copied from `tools/orphan_ratchet.py`,
    including the `(path or CONST)` receiver -- a scan accepting only a bare Name misses it."""
    _tree(tmp_path, ratchet=HEADER + (
        'BASELINE_PATH = ROOT / "docs" / "design" / "orphan_baseline.json"\n'
        "def freeze(data, path=None):\n"
        '    (path or BASELINE_PATH).write_text("{}")\n'
    ))
    assert fs.written_artefacts(tmp_path) == {"docs/design/orphan_baseline.json"}


def test_MUTATION_a_path_that_is_only_NAMED_is_never_reported(tmp_path):
    """The partner leg, and the more expensive failure. Both modules assign a `docs/design` path
    as a constant; only one writes it. A classifier keyed to naming marks the register generated,
    and its consumer's remedy for a generated path is to throw the local bytes away."""
    _tree(tmp_path,
          ratchet=HEADER + (
              'BASELINE_PATH = ROOT / "docs" / "design" / "orphan_baseline.json"\n'
              'BASELINE_PATH.write_text("{}")\n'),
          reader=HEADER + (
              'REGISTER_DOC = ROOT / "docs" / "design" / "WALL_CROSSING_DISPOSITION_REGISTER.md"\n'
              "def load(path=REGISTER_DOC):\n"
              "    return path.read_text()\n"))
    found = fs.written_artefacts(tmp_path)
    assert found == {"docs/design/orphan_baseline.json"}, found


def test_MUTATION_an_open_for_READING_is_not_a_write(tmp_path):
    """`open(P)` defaults to "r". A scan that took any `open` would classify every module that
    reads a committed document as that document's producer -- which is most of this tree."""
    _tree(tmp_path,
          writer=HEADER + ('OUT = ROOT / "docs" / "reports" / "out.json"\n'
                           'open(OUT, "w").write("{}")\n'),
          reader=HEADER + ('IN_DOC = ROOT / "docs" / "design" / "AUTHORED.md"\n'
                           "open(IN_DOC).read()\n"
                           'open(IN_DOC, "r").read()\n'))
    assert fs.written_artefacts(tmp_path) == {"docs/reports/out.json"}


def test_MUTATION_an_APPEND_is_not_a_rewrite(tmp_path):
    """Keyed to the reason the revert remedy is cheap: a rewritten path can be made again. An
    appended ledger -- `docs/direction/decisions.jsonl` is the director's own decisions, one line
    at a time -- cannot, so it stays on the authored side and is offered a landing."""
    _tree(tmp_path,
          appender=HEADER + ('LEDGER = ROOT / "docs" / "direction" / "decisions.jsonl"\n'
                             'open(LEDGER, "a").write("{}\\n")\n'),
          rewriter=HEADER + ('OUT = ROOT / "docs" / "reports" / "out.json"\n'
                             'OUT.write_text("{}")\n'))
    assert fs.written_artefacts(tmp_path) == {"docs/reports/out.json"}


def test_MUTATION_a_destination_chosen_by_a_conditional_is_still_a_destination(tmp_path):
    """`dest = OUT_PATH if out_path is None else out_path` is how `generate_value_arms_data`
    writes the proof page's feed. Resolving only the first branch that answers would have dropped
    it, and it is the path the 2026-09-09 instance of this same defect was found on."""
    _tree(tmp_path, publisher=HEADER + (
        'OUT_PATH = ROOT / "site" / "data" / "value_arms.json"\n'
        "def publish(data, out_path=None):\n"
        "    dest = OUT_PATH if out_path is None else out_path\n"
        '    dest.write_text("{}")\n'))
    assert fs.written_artefacts(tmp_path) == {"site/data/value_arms.json"}


def test_MUTATION_a_local_name_does_not_borrow_another_functions_constant(tmp_path):
    """SCOPE, proven on the shape that actually produced a false finding. A module-wide name map
    read `Path(p).write_text(...)` in one function against a `p` bound to `DIRECTOR_AXES.md` in
    another, and reported the director's axes as a generated artefact. One-letter destination
    names are everywhere here, so a flat map manufactures exactly the misclassification this
    oracle exists to avoid -- and does it on the most expensive paths in the repo."""
    _tree(tmp_path, supervisor=HEADER + (
        'DIRECTOR_AXES = ROOT / "docs" / "design" / "DIRECTOR_AXES.md"\n'
        "def read_axes():\n"
        "    p = DIRECTOR_AXES\n"
        "    return p.read_text()\n"
        "def record_cooldown(p):\n"
        '    Path(p).write_text("{}")\n'
        "def write_report():\n"
        '    out = ROOT / "docs" / "reports" / "cooldown.json"\n'
        '    out.write_text("{}")\n'))
    found = fs.written_artefacts(tmp_path)
    assert found == {"docs/reports/cooldown.json"}, found


# ---------------------------------------------------------------------------
# The real tree: the fixture must not be the only evidence
# ---------------------------------------------------------------------------
def test_the_ratchets_baseline_is_write_reached_in_the_REAL_tree():
    """The instance the oracle was built for, asked of the repository rather than a fixture."""
    assert AUTHORED_TREE_GENERATED in fs.written_artefacts()


def test_the_union_is_not_vacuous_because_the_tree_keyed_oracle_cannot_see_this_class():
    """THE POISON ROUND FOR THE WHOLE CHANGE. If the write-keyed set were a subset of the
    tree-keyed one, unioning them in `_split_generated` would be ceremony: every leg elsewhere
    would still pass while the union added nothing. So prove the residue is populated, and that
    the path this was built for is in the residue and not merely in the union."""
    write_keyed = fs.written_artefacts()
    tree_keyed = fs.generated_artefacts()
    residue = write_keyed - tree_keyed
    assert AUTHORED_TREE_GENERATED in residue
    assert len(residue) > 1, "one path is an instance; this was filed as a class"


def test_an_independently_CURATED_register_of_rendered_documents_agrees():
    """A second, hand-maintained oracle with its own completeness test names three `docs/design`
    markdown files as RENDERED rather than authored. It was built by a different lane for a
    different purpose, so agreement is evidence and not a restatement. Disagreement here means the
    write scan has stopped seeing a renderer everyone else knows about."""
    from background.derived_artefact_register import REGISTER

    write_keyed = fs.written_artefacts()
    curated = {a.rendered for a in REGISTER}
    assert curated, "the curated register is empty -- this leg would be vacuous"
    assert curated <= write_keyed, sorted(curated - write_keyed)


def test_a_register_the_tree_only_READS_is_not_called_a_producers_output():
    """The naming side, in the real tree. The first assertion is what stops this being vacuous:
    the path IS assigned as a module constant, so a naming-keyed classifier WOULD have claimed
    it."""
    import ast

    module = fs.PROJECT_DIR / "tools" / "wall_crossing_dispositions.py"
    parsed = ast.parse(module.read_text(encoding="utf-8"))
    named = {p for paths in fs._scope_path_names(fs._own_scope(parsed), module.resolve(), {}).values()
             for p in paths}
    assert fs.PROJECT_DIR / NAMED_NEVER_WRITTEN in named, (
        "the naming site moved -- this leg proves nothing now")
    assert NAMED_NEVER_WRITTEN not in fs.written_artefacts()


def test_the_not_reproducible_carve_out_is_load_bearing_and_can_only_shrink():
    """Every carve-out member must still be write-reached. A member that is no longer written is
    STALE, and a carve-out that keeps entries for things nothing writes stops being a shrinking
    list of exceptions and becomes a place exceptions go to be forgotten -- the same reasoning the
    FROZEN debt list above is governed by."""
    raw = fs._write_reached_paths()
    stale = fs.WRITTEN_BUT_NOT_REPRODUCIBLE - raw
    assert not stale, "stale carve-out entries, nothing writes them: {}".format(sorted(stale))
    assert not (fs.WRITTEN_BUT_NOT_REPRODUCIBLE & fs.written_artefacts())


def test_the_file_scope_GATE_does_not_consume_the_write_keyed_set():
    """The wall this change had to not cross. `generated_artefacts` feeds a fail-CLOSED gate that
    blocks commits and a FROZEN debt list measured against exactly that set; widening it would
    have changed a commit gate to fix a line of remedy prose. So the gate's verdict must be
    computable with the write-keyed oracle removed entirely."""
    import tools.file_scope_generated_paths as module

    real = module.written_artefacts
    try:
        module.written_artefacts = lambda root=None: (_ for _ in ()).throw(
            AssertionError("the file_scope gate reached for the write-keyed oracle"))
        assert module.gate_violations() == []
    finally:
        module.written_artefacts = real


# ---------------------------------------------------------------------------
# Fail-closed: an oracle that cannot answer raises
# ---------------------------------------------------------------------------
def test_MUTATION_an_empty_tree_RAISES_rather_than_reporting_no_generators(tmp_path):
    """The FAIL-OPEN killer, in its quietest form: an empty set classifies every producer's
    output as somebody's work, and the consumer then offers to land all of them."""
    with pytest.raises(fs.OracleUnavailable):
        fs.written_artefacts(tmp_path)


def test_MUTATION_modules_that_write_NOTHING_also_RAISE(tmp_path):
    """The second empty path, which the first leg does not reach: files were scanned and parsed,
    and still nothing was found. This project publishes a site and freezes ratchets from python,
    so zero is a broken oracle rather than a tree without generators."""
    _tree(tmp_path, reader=HEADER + ('DOC = ROOT / "docs" / "design" / "AUTHORED.md"\n'
                                     "DOC.read_text()\n"))
    with pytest.raises(fs.OracleUnavailable):
        fs.written_artefacts(tmp_path)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
