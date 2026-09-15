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
# A real path reachable ONLY one frame down: `background/run_rotation._write_index` writes its
# parameter, and the cursor constant is handed to it. The leg that uses it proves the "only"
# rather than asserting it.
HELPER_REACHED_REAL_PATH = "docs/observability/run_rotation_cursor.json"


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


def test_MUTATION_the_atomic_write_idiom_is_a_write(tmp_path):
    """`tmp.replace(final)` -- write beside, then rename over -- is how six producers here avoid a
    half-written artefact, and the destination is the only argument. The stdlib two-argument form
    (`os.replace(src, dst)`) was handled and this one was not, so the path a producer takes care to
    write atomically was the one the oracle could not see."""
    _tree(tmp_path, publisher=HEADER + (
        'FINAL = ROOT / "docs" / "design" / "baseline.json"\n'
        "def save(data):\n"
        '    tmp = FINAL.with_suffix(".tmp")\n'
        '    tmp.write_text("{}")\n'
        "    tmp.replace(FINAL)\n"))
    assert "docs/design/baseline.json" in fs.written_artefacts(tmp_path)


def test_MUTATION_a_method_does_not_borrow_a_class_body_constant(tmp_path):
    """Python scoping, asserted because the oracle had to be told: a method does not see a class
    body's names -- inside `save` that constant is `self.path`, never a bare `path`. Without it, a
    class attribute lends its path to any method parameter that happens to share its name, which is
    the same shape that reported the director's axes as a generated artefact.

    THE COLLISION IS THE FIXTURE. A first version of this test gave the class an attribute called
    `PATH` and the method a parameter called `p`, and passed with the scoping deliberately broken --
    nothing shadowed anything, so there was no leak to catch and the leg was coverage rather than a
    control. The names must MEET for the mutation to fire.

    NO REAL PATH MOVES ON THIS TODAY: no class body in the live tree binds a path constant a method
    parameter shadows, so this is an EQUIVALENCE there and a fixture is the only place it can fire.
    That is recorded here rather than left for a reader to assume it was the flattering one."""
    _tree(tmp_path, store=HEADER + (
        'OUT = ROOT / "docs" / "reports" / "out.json"\n'
        "class Store:\n"
        '    path = ROOT / "docs" / "design" / "AUTHORED.md"\n'
        "    def save(self, path):\n"
        '        Path(path).write_text("{}")\n'
        "def publish():\n"
        '    OUT.write_text("{}")\n'))
    assert fs.written_artefacts(tmp_path) == {"docs/reports/out.json"}


# ---------------------------------------------------------------------------
# One frame down: the helper the constant is handed to
# ---------------------------------------------------------------------------
def test_MUTATION_a_path_written_ONE_FRAME_DOWN_IN_A_HELPER_is_found(tmp_path):
    """THE GAP THIS MODULE'S OWN DOCSTRING USED TO NAME. A producer that factors its write into
    `_write_json(BASELINE_PATH, data)` writes the constant just as surely as one that spells
    `.write_text` beside it -- and the scan could only see the second, so every producer of the
    first shape was classified AUTHORED and the reconciler offered to land its output. That is the
    exact defect the write-site key was built to end, surviving through a helper.

    THE HELPER IS THE ONLY ROUTE HERE. No scope in this fixture writes the constant directly, so
    without the frame the oracle finds nothing at all and RAISES."""
    _tree(tmp_path, ratchet=HEADER + (
        'BASELINE_PATH = ROOT / "docs" / "design" / "orphan_baseline.json"\n'
        "def _write_json(path, payload):\n"
        '    path.write_text(payload)\n'
        "def freeze(data):\n"
        "    _write_json(BASELINE_PATH, data)\n"))
    assert fs.written_artefacts(tmp_path) == {"docs/design/orphan_baseline.json"}


def test_MUTATION_a_helper_that_only_READS_its_parameter_reports_nothing(tmp_path):
    """The partner leg, and the expensive direction. Both helpers below take a `docs/design`
    constant one frame down; only one writes it. A frame that followed any parameter INTO a helper
    would mark the register generated, and the remedy a consumer applies to a generated path is to
    throw the local bytes away -- so reaching one frame must not cost the naming/writing boundary
    the whole scan is keyed to."""
    _tree(tmp_path, ratchet=HEADER + (
        'BASELINE_PATH = ROOT / "docs" / "design" / "orphan_baseline.json"\n'
        'REGISTER_DOC = ROOT / "docs" / "design" / "WALL_CROSSING_DISPOSITION_REGISTER.md"\n'
        "def _write_json(path, payload):\n"
        '    path.write_text(payload)\n'
        "def _load(path):\n"
        "    return path.read_text()\n"
        "def run(data):\n"
        "    _load(REGISTER_DOC)\n"
        "    _write_json(BASELINE_PATH, data)\n"))
    found = fs.written_artefacts(tmp_path)
    assert found == {"docs/design/orphan_baseline.json"}, found


def test_MUTATION_the_argument_is_matched_to_its_POSITION_not_to_the_first_parameter(tmp_path):
    """`_dump(payload, path)` puts the destination SECOND, and `background/naive_organ` and
    `tools/sample_gate_rss_premium` both order their helpers that way. Binding by position is the
    only thing that makes this right, and a resolver that bound the first argument would bind the
    PAYLOAD as a destination -- silently reporting whatever path happened to be in it."""
    _tree(tmp_path, publisher=HEADER + (
        'OUT = ROOT / "docs" / "reports" / "out.json"\n'
        'AUTHORED = ROOT / "docs" / "design" / "AUTHORED.md"\n'
        "def _dump(payload, path):\n"
        "    path.write_text(payload)\n"
        "def run():\n"
        "    _dump(AUTHORED.read_text(), OUT)\n"))
    assert fs.written_artefacts(tmp_path) == {"docs/reports/out.json"}


def test_MUTATION_a_KEYWORD_argument_binds_too(tmp_path):
    """`_write_json(path=OUT, payload=rows)` is the same call. Position is how most of this tree
    spells it and keyword is how the rest does; a frame that only read `call.args` would find the
    same producer through one door and not the other."""
    _tree(tmp_path, publisher=HEADER + (
        'OUT = ROOT / "docs" / "reports" / "out.json"\n'
        "def _write_json(path, payload):\n"
        "    path.write_text(payload)\n"
        "def run(rows):\n"
        "    _write_json(payload=rows, path=OUT)\n"))
    assert fs.written_artefacts(tmp_path) == {"docs/reports/out.json"}


def test_MUTATION_a_parameter_REBOUND_in_the_helper_is_not_followed(tmp_path):
    """After `path = SOMEWHERE_ELSE` the write does not go where the caller said, and following it
    anyway MANUFACTURES a path -- it reports the argument as written when the argument is never
    touched. The names must meet for this to fire, so the caller hands in an authored document and
    the helper writes over the name with its own destination: a resolver without the rebound check
    accumulates BOTH and reports the authored one."""
    _tree(tmp_path, publisher=HEADER + (
        'AUTHORED = ROOT / "docs" / "design" / "AUTHORED.md"\n'
        "def _write(path):\n"
        '    path = ROOT / "docs" / "reports" / "actual.json"\n'
        '    path.write_text("{}")\n'
        "def run():\n"
        "    _write(AUTHORED)\n"))
    found = fs.written_artefacts(tmp_path)
    assert found == {"docs/reports/actual.json"}, found


def test_MUTATION_TWO_frames_is_not_followed(tmp_path):
    """ONE frame, and the boundary is structural rather than a depth counter: a binding does not
    travel, so `_outer` cannot hand `_inner` what `run` passed it.

    BOTH HALVES ARE IN THE ONE FIXTURE, or this leg would pass just as happily with the whole frame
    dead. `SHALLOW` goes one frame and MUST be found; `DEEP` goes two and must not. `_outer` is a
    real helper here -- it writes `LOG` -- so the question being asked is genuinely "does the frame
    recurse", not "is `_outer` a helper at all", which is what a version of this fixture without
    that write would have silently asked instead."""
    _tree(tmp_path, publisher=HEADER + (
        'SHALLOW = ROOT / "docs" / "reports" / "shallow.json"\n'
        'LOG = ROOT / "docs" / "reports" / "log.json"\n'
        'DEEP = ROOT / "docs" / "design" / "DEEP.md"\n'
        "def _inner(p):\n"
        '    p.write_text("{}")\n'
        "def _outer(q):\n"
        '    LOG.write_text("{}")\n'
        "    _inner(q)\n"
        "def run():\n"
        "    _inner(SHALLOW)\n"
        "    _outer(DEEP)\n"))
    found = fs.written_artefacts(tmp_path)
    assert found == {"docs/reports/shallow.json", "docs/reports/log.json"}, found


def test_MUTATION_an_argument_that_is_not_STATICALLY_a_path_binds_nothing(tmp_path):
    """The deliberate STRICTNESS, and the one place the frame is tighter than the scan around it.
    A write DESTINATION is structurally a path expression, so walking it for any known name is
    safe. An ARGUMENT is an arbitrary expression: walking `_save(derive(REGISTER))` for names finds
    a register this module only ever reads and reports it as written -- the naming-keyed
    misclassification, arriving one frame down instead of at the top. Missing a path costs a
    warning; claiming one costs a lane's work, so the argument is resolved by `_static_paths`
    alone."""
    _tree(tmp_path, publisher=HEADER + (
        'OUT = ROOT / "docs" / "reports" / "out.json"\n'
        'REGISTER = ROOT / "docs" / "design" / "WALL_CROSSING_DISPOSITION_REGISTER.md"\n'
        "def _save(path):\n"
        '    path.write_text("{}")\n'
        "def run():\n"
        "    _save(derive(REGISTER))\n"
        "    _save(OUT)\n"))
    found = fs.written_artefacts(tmp_path)
    assert found == {"docs/reports/out.json"}, found


def test_MUTATION_the_helper_inherits_the_MODULES_names_and_not_the_CALLERS(tmp_path):
    """SCOPE AGAIN, through the new door. A helper called from inside a function cannot see that
    function's locals, and lending them to it is the flat-name-map defect that once reported the
    director's axes as generated.

    THE COLLISION IS THE FIXTURE, AND IT TAKES TWO PARAMETERS TO BUILD. The caller's local is named
    `path`, exactly like the helper's destination parameter, and the call hands in something that
    does NOT resolve -- so if the helper inherited the caller's names, that unresolved parameter
    falls through to the caller's `path` and the authored document is reported as written.

    A FIRST VERSION OF THIS LEG PASSED WITH THE LEAK INSTALLED. It bound nothing at all, so the
    resolver took its `if not bound: return` exit and never consulted the inherited map on either
    side of the mutation -- a control measuring an early return rather than the scope rule. `log`
    is here to make the call bind SOMETHING, so the leak is reached and the collision can fire."""
    _tree(tmp_path, publisher=HEADER + (
        'LOG = ROOT / "docs" / "reports" / "log.json"\n'
        "def _save(path, log):\n"
        '    path.write_text("{}")\n'
        '    log.write_text("{}")\n'
        "def run(target):\n"
        '    path = ROOT / "docs" / "design" / "AUTHORED.md"\n'
        "    _save(target, LOG)\n"))
    found = fs.written_artefacts(tmp_path)
    assert found == {"docs/reports/log.json"}, found


# ---------------------------------------------------------------------------
# The real tree: the fixture must not be the only evidence
# ---------------------------------------------------------------------------
def test_the_helper_frame_is_LOAD_BEARING_in_the_REAL_tree():
    """THE POISON ROUND FOR THE FRAME. Every leg above is a fixture, and a frame that resolved
    nothing in the actual repository would pass all of them while changing no classification at
    all. So remove the frame from the live scan and measure what disappears.

    Keyed to the PROPERTY -- these paths are reachable only through a helper -- and not to the
    count of the day, which is why the named path is asserted individually and the rest is a floor.
    If a producer is later refactored to write its constant directly, this goes green on a smaller
    set rather than red on a number."""
    with_frame = fs._write_reached_paths()
    real = fs._module_helpers
    try:
        fs._module_helpers = lambda module: {}
        without_frame = fs._write_reached_paths()
    finally:
        fs._module_helpers = real
    gained = with_frame - without_frame
    assert HELPER_REACHED_REAL_PATH in gained, sorted(gained)
    assert len(gained) > 1, "one path is an instance; this was built as a class"


def test_a_document_a_daemon_edits_ONE_LINE_OF_is_not_a_photograph_of_a_run():
    """The frame found these two, and finding them is a different question from what to do with
    them. `background/discovery_agent._update_last_checked` regex-substitutes a single date line in
    the assumption library and writes it back; `background/naive_organ._rewrite_log` rewrites an
    answered-question ledger whole, which passes the writing-MODE test that an `"a"` append would
    have failed -- and the mode check cannot see that a read-modify-rewrite of an accumulated
    record is an append wearing a rewrite's clothes. Neither is reproducible by a run, so both are
    carved out; this leg is what goes red if someone deletes a carve-out entry because the scan
    'obviously' found a write."""
    raw = fs._write_reached_paths()
    offered = fs.written_artefacts()
    for path in ("docs/market_research/ASSUMPTIONS.md",
                 "docs/observability/naive_organ_log.jsonl"):
        assert path in raw, f"{path} is no longer write-reached -- this leg proves nothing now"
        assert path not in offered, f"{path} is being offered a REVERT"



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
