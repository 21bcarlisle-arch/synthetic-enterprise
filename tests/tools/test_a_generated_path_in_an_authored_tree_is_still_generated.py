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
# A real path reachable ONLY through a signature DEFAULT: `tools/generate_capabilities_door.py`
# spells `def generate(out=OUT_PATH)` and `__main__` calls `generate()` with no argument, so there
# is no call site carrying the destination for the helper frame to bind. The leg that uses it
# proves the "only" by removing the seeding, rather than asserting it.
DEFAULT_REACHED_REAL_PATH = "site/data/capabilities_door.json"
# A real path reachable ONLY through an INSTANCE ATTRIBUTE: `PublishStepLedger.__init__` binds
# `self.project_dir` and `write` falls back to `self.project_dir / "site" / "data" /
# "publish_steps.json"`, with `background/process_run_complete.py:4525` calling `_ledger.write()`
# bare. It is the frame's ONE live instance in this tree -- the count is in
# `docs/staging/records/PREREG_WHAT_THE_WRITE_KEYED_ORACLE_GAINS_FROM_AN_INSTANCE_ATTRIBUTE_
# DESTINATION_2026-09-15.md` -- so the leg that uses it asserts the path and NOT a floor.
ATTRIBUTE_REACHED_REAL_PATH = "site/data/publish_steps.json"


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


def test_MUTATION_a_STARRED_argument_does_not_shift_the_written_position(tmp_path):
    """A `*args` makes every LATER position unknowable, and counting through it does not lose an
    attribution -- it manufactures a false one. Here the expression sitting in the slot the count
    lands on is the authored register, so a resolver that kept counting reports a document this
    module only reads, and the consumer's remedy for a generated path is REVERT.

    The partner of the position leg above: that one proves positions are counted, this one proves
    the counting STOPS where it stops meaning anything."""
    _tree(tmp_path, splat=HEADER + (
        f'REGISTER_DOC = ROOT / "docs" / "design" / "{Path(NAMED_NEVER_WRITTEN).name}"\n'
        'OUT = ROOT / "docs" / "reports" / "out.json"\n'
        "def _write_json(prefix, path, data):\n"
        '    path.write_text("{}")\n'
        "def run(head):\n"
        "    _write_json(*head, REGISTER_DOC, {})\n"
        '    OUT.write_text("{}")\n'))
    found = fs.written_artefacts(tmp_path)
    assert found == {"docs/reports/out.json"}, found


def test_MUTATION_a_KEYWORD_argument_is_matched_by_NAME_through_the_same_starred_call(tmp_path):
    """The partner to the leg above, and the reason abandoning a starred call WHOLESALE would have
    been too much. A keyword names its parameter whatever preceded it, so the one shape that cannot
    be counted positionally stays readable. Without this leg the safe-looking fix -- drop every
    starred call -- is a silent narrowing paid for by the false positive next door (R15: a narrowing
    added to fix a false positive is asymmetric, and only the false positive gets a comment)."""
    _tree(tmp_path, splat=HEADER + (
        f'BASELINE_PATH = ROOT / "{AUTHORED_TREE_GENERATED}"\n'
        "def _write_json(prefix, path, data):\n"
        '    path.write_text("{}")\n'
        "def run(head):\n"
        "    _write_json(*head, path=BASELINE_PATH, data={})\n"))
    assert fs.written_artefacts(tmp_path) == {AUTHORED_TREE_GENERATED}


def test_MUTATION_a_write_helper_in_ANOTHER_module_is_not_followed(tmp_path):
    """SAME-MODULE ONLY, asserted rather than assumed. A bare `Name` call is the only call shape
    whose target is knowable without resolving imports; taking any call to a name that happens to
    match some other module's writer attributes across a boundary this scan cannot see. The fixture
    makes the names COLLIDE -- both modules define `_write_json`, only one writes its parameter --
    because without the collision there is nothing for the mutation to get wrong.

    AND THE SCAN ORDER IS PART OF THE FIXTURE, not cosmetic naming. `_write_reached_paths` walks
    `sorted(rglob("*.py"))`, so a leaked helper map can only carry the writer's entry into the
    consumer if the writer is read FIRST. Named `a_writer`/`b_consumer` for that reason: with the
    alphabetical order the other way round this leg passes with the leak installed, which is how a
    control becomes coverage."""
    _tree(tmp_path,
          a_writer=HEADER + ("def _write_json(path, data):\n"
                             '    path.write_text("{}")\n'),
          b_consumer=HEADER + (
              f'REGISTER_DOC = ROOT / "docs" / "design" / "{Path(NAMED_NEVER_WRITTEN).name}"\n'
              'OUT = ROOT / "docs" / "reports" / "out.json"\n'
              "def _write_json(path, data):\n"
              "    return path.read_text()\n"
              "def run():\n"
              "    _write_json(REGISTER_DOC, {})\n"
              '    OUT.write_text("{}")\n'))
    found = fs.written_artefacts(tmp_path)
    assert found == {"docs/reports/out.json"}, found


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
# The default in the signature: a destination with no call site to read
# ---------------------------------------------------------------------------
def test_MUTATION_a_destination_parameters_DEFAULT_is_a_write_site(tmp_path):
    """`def generate(out=OUT_PATH)` writes `OUT_PATH` on every call that names no destination, and
    `generate()` with no argument is how nine producers in this tree are actually called. The
    helper frame cannot see it: there is no argument at the call site to bind, so the frame binds
    nothing and takes its `if not bound: return` exit.

    NO OTHER ROUTE EXISTS IN THIS FIXTURE, which is what stops the leg passing with the seeding
    dead. `OUT_PATH` is never written at module scope and never handed to anything; the signature
    is the only place it meets the write."""
    _tree(tmp_path, publisher=HEADER + (
        'OUT_PATH = ROOT / "site" / "data" / "capabilities_door.json"\n'
        "def generate(out=OUT_PATH):\n"
        '    out.write_text("{}")\n'
        "def main():\n"
        "    generate()\n"))
    assert fs.written_artefacts(tmp_path) == {"site/data/capabilities_door.json"}


def test_MUTATION_a_default_on_a_parameter_that_is_only_READ_reports_nothing(tmp_path):
    """The partner on the expensive side of the boundary. A default goes into the NAME MAP, and
    only a write DESTINATION is harvested out of it -- `_load(register=REGISTER_DOC)` declares its
    default just as loudly and the register is never written. A seeding that reported every
    defaulted path would mark it generated, and the remedy a consumer applies to a generated path
    is REVERT.

    BOTH DEFAULTS ARE IN THE ONE FIXTURE. Without the writing half the leg would pass on a scan
    that had stopped reading defaults altogether."""
    _tree(tmp_path, publisher=HEADER + (
        'OUT = ROOT / "docs" / "reports" / "out.json"\n'
        'REGISTER_DOC = ROOT / "docs" / "design" / "WALL_CROSSING_DISPOSITION_REGISTER.md"\n'
        "def _load(register=REGISTER_DOC):\n"
        "    return register.read_text()\n"
        "def run(out=OUT):\n"
        "    _load()\n"
        '    out.write_text("{}")\n'))
    found = fs.written_artefacts(tmp_path)
    assert found == {"docs/reports/out.json"}, found


def test_MUTATION_a_parameter_REBOUND_under_its_own_DEFAULT_is_not_followed(tmp_path):
    """After `path = SOMEWHERE_ELSE` the write does not go where the signature said, and seeding
    the default anyway MANUFACTURES a path -- `_scope_path_names` accumulates rather than
    replaces, so the oracle would report BOTH and claim one this `def` provably never writes.

    THE NAMES MUST MEET FOR THIS TO FIRE. The default is an authored document and the body writes
    over the name with its real destination, so a seeding without the rebound check offers a
    REVERT on the document."""
    _tree(tmp_path, publisher=HEADER + (
        'AUTHORED = ROOT / "docs" / "design" / "WALL_CROSSING_DISPOSITION_REGISTER.md"\n'
        "def run(path=AUTHORED):\n"
        '    path = ROOT / "docs" / "reports" / "actual.json"\n'
        '    path.write_text("{}")\n'))
    found = fs.written_artefacts(tmp_path)
    assert found == {"docs/reports/actual.json"}, found


def test_MUTATION_a_nested_def_does_not_inherit_a_name_its_OWN_signature_shadows(tmp_path):
    """SCOPE, for the third time and through the door seeding defaults opened. Putting PARAMETER
    names into the resolved map for the first time makes an enclosing `out`/`path`/`dest` reachable
    by an inner `def` that declares its own -- and those three names repeat across nested defs all
    over this tree. An inner parameter is NOT the outer name, and lending it the outer path is the
    flat-name-map defect that reported the director's axes as generated, one scope deeper.

    THE COLLIDING NAMES MUST STAND ON OPPOSITE SIDES OF THE BOUNDARY, or the leg cannot fire. A
    first version had both `out`s resolving to the same log file: the set deduplicated the leaked
    copy and the fixture passed just as happily with the strip deleted. Here `outer`'s default is
    an AUTHORED register it only hands on, `inner` declares its own `dest` and writes it, and a
    scan without the strip lends the register to that write and offers a REVERT on it. `LOG` is
    the module's honest write, so the oracle has something to find either way and this is not
    measuring the fail-closed raise."""
    _tree(tmp_path, publisher=HEADER + (
        'LOG = ROOT / "docs" / "reports" / "log.json"\n'
        'AUTHORED = ROOT / "docs" / "design" / "WALL_CROSSING_DISPOSITION_REGISTER.md"\n'
        "def outer(dest=AUTHORED):\n"
        '    LOG.write_text("{}")\n'
        "    def inner(dest):\n"
        '        dest.write_text("{}")\n'
        "    inner(dest.read_text())\n"))
    found = fs.written_artefacts(tmp_path)
    assert found == {"docs/reports/log.json"}, found


def test_MUTATION_a_METHODS_default_resolves_against_the_MODULES_names(tmp_path):
    """The class-shaped half, kept to the property rather than to the narrowing. A method's
    default IS evaluated in the enclosing scope, so a module constant standing in a method
    signature is a destination -- and `_paths_written_by_scope` hands a class's nested scopes what
    the CLASS inherited, which is the module, so this is the case that must work.

    Deliberately NOT a leg about the class body. Python would let a method default see a class
    attribute and this resolver does not take it; asserting that absence would pin a control to
    today's narrowing and go red the day the oracle became more honest."""
    _tree(tmp_path, publisher=HEADER + (
        'LEDGER = ROOT / "docs" / "reports" / "ledger.json"\n'
        "class Writer:\n"
        "    def write(self, path=LEDGER):\n"
        '        path.write_text("{}")\n'))
    assert fs.written_artefacts(tmp_path) == {"docs/reports/ledger.json"}


# ---------------------------------------------------------------------------
# The instance attribute: a destination the method never names
# ---------------------------------------------------------------------------
def test_MUTATION_an_instance_attribute_bound_in_INIT_is_a_write_site(tmp_path):
    """`__init__` holds the destination and the writing method only spells `self.`. This is the
    door the `self._write(...)` search was really pointing at, and unlike that one it has a live
    instance: `PublishStepLedger` binds `self.project_dir` and `write` falls back through it.

    THE READ-ONLY ATTRIBUTE IS IN THE SAME FIXTURE, on the expensive side of the boundary. An
    attribute goes into the NAME MAP and only a write DESTINATION is harvested out of it --
    `self.register.read_text()` declares its path just as loudly and is never written, and the
    remedy a consumer applies to a generated path is REVERT. Without this half the leg would pass
    just as happily on a resolver that reported every attribute it could resolve.

    `LOG` IS WHY A FAILURE HERE IS A FAILURE OF THE FRAME. Without a write the resolver can already
    see, removing the frame empties the set and `_write_reached_paths` takes its fail-closed raise
    -- so the leg would be distinguishing "the frame is dead" from "the oracle refused to answer",
    which are not the same finding."""
    _tree(tmp_path, publisher=HEADER + (
        'LEDGER = ROOT / "docs" / "reports" / "ledger.json"\n'
        'LOG = ROOT / "docs" / "reports" / "log.json"\n'
        f'REGISTER = ROOT / "docs" / "design" / "{Path(NAMED_NEVER_WRITTEN).name}"\n'
        "class Writer:\n"
        "    def __init__(self):\n"
        "        self.out = LEDGER\n"
        "        self.register = REGISTER\n"
        "    def save(self):\n"
        '        LOG.write_text("{}")\n'
        '        self.out.write_text("{}")\n'
        "    def load(self):\n"
        "        return self.register.read_text()\n"))
    found = fs.written_artefacts(tmp_path)
    assert found == {"docs/reports/ledger.json", "docs/reports/log.json"}, found


def test_MUTATION_the_attribute_is_followed_through_a_LOCAL_and_a_CHOICE(tmp_path):
    """THE LIVE SHAPE, COPIED RATHER THAN IMAGINED, and the reason a shallow probe for
    `self.<attr>` standing in the destination expression returns zero and is wrong.
    `PublishStepLedger.write` spells `target = Path(path) if path else (self.project_dir / "site" /
    "data" / "publish_steps.json")` and then writes `target`: the attribute reaches the write
    through a LOCAL, inside a CHOICE whose other branch resolves to nothing.

    `__init__` carries the same choice shape -- `Path(project_dir) if project_dir else ROOT` -- so
    both halves of the chain are driven. The parameterised branch must contribute NOTHING (an
    argument this scan never sees) while the default branch contributes the root, which is exactly
    what makes the resolved path the one written when the caller names neither.

    `LOG` is here for the reason the leg above carries one: it keeps a failure attributable to the
    frame rather than to the fail-closed raise an empty set triggers."""
    _tree(tmp_path, publisher=HEADER + (
        'LOG = ROOT / "docs" / "reports" / "log.json"\n'
        "class Ledger:\n"
        "    def __init__(self, project_dir=None):\n"
        "        self.project_dir = Path(project_dir) if project_dir else ROOT\n"
        "    def write(self, path=None):\n"
        '        LOG.write_text("{}")\n'
        "        target = Path(path) if path else "
        '(self.project_dir / "site" / "data" / "publish_steps.json")\n'
        '        target.write_text("{}")\n'))
    found = fs.written_artefacts(tmp_path)
    assert found == {"site/data/publish_steps.json", "docs/reports/log.json"}, found


def test_MUTATION_a_REBOUND_instance_attribute_is_refused_WHOLE(tmp_path):
    """The same guard `_module_helpers` and `_default_destinations` carry, through the third door.
    An attribute bound in more than one place is not reliably either binding, and
    `_scope_path_names` ACCUMULATES rather than replaces -- so a resolver without the refusal
    reports BOTH and offers a REVERT on the authored document in the first one.

    THE NAMES MUST MEET FOR THIS TO FIRE, so the two bindings stand on opposite sides of the
    boundary: `__init__` points the attribute at an authored register and `retarget` moves it to a
    real output. REFUSED WHOLE is the assertion, not "the second binding wins": `actual.json` is a
    genuine destination and it is dropped too, because an attribute this resolver cannot fully see
    must fail toward saying nothing. `LOG` is the module's honest write, so a green here is the
    refusal working and not the fail-closed raise."""
    _tree(tmp_path, publisher=HEADER + (
        'LOG = ROOT / "docs" / "reports" / "log.json"\n'
        f'AUTHORED = ROOT / "docs" / "design" / "{Path(NAMED_NEVER_WRITTEN).name}"\n'
        "class Writer:\n"
        "    def __init__(self):\n"
        "        self.path = AUTHORED\n"
        "    def retarget(self):\n"
        '        self.path = ROOT / "docs" / "reports" / "actual.json"\n'
        "    def save(self):\n"
        '        LOG.write_text("{}")\n'
        '        self.path.write_text("{}")\n'))
    found = fs.written_artefacts(tmp_path)
    assert found == {"docs/reports/log.json"}, found


def test_MUTATION_a_class_body_name_answers_self_DOT_and_still_not_a_bare_name(tmp_path):
    """BOTH SIDES OF THE SCOPE RULE IN ONE FIXTURE, because each is the other's mutation.

    `self.DOTTED` genuinely IS the class attribute -- that is what Python resolves it to -- so the
    dotted map must answer it. A bare `BARE` inside a method is NOT: at run time it is a NameError,
    so a resolver that answered it would be reporting a path no execution can reach, and the
    module's long-standing `handed_down = inherited if isinstance(node, ast.ClassDef)` line exists
    to stop exactly that. Adding the dotted map is where that line could most easily be undone by
    accident, so the leg drives both spellings of a class attribute at once.

    THE TWO ATTRIBUTES STAND ON OPPOSITE SIDES OF THE BOUNDARY. If both were outputs the set would
    look identical whichever way the rule went; here a leak offers a REVERT on an authored
    document, which is the failure worth a control. `LOG` keeps a failure attributable to the rule
    rather than to the fail-closed raise."""
    _tree(tmp_path, publisher=HEADER + (
        'LOG = ROOT / "docs" / "reports" / "log.json"\n'
        "class Writer:\n"
        '    DOTTED = ROOT / "docs" / "reports" / "dotted.json"\n'
        f'    BARE = ROOT / "docs" / "design" / "{Path(NAMED_NEVER_WRITTEN).name}"\n'
        "    def a(self):\n"
        '        LOG.write_text("{}")\n'
        '        self.DOTTED.write_text("{}")\n'
        "    def b(self):\n"
        '        BARE.write_text("{}")\n'))
    found = fs.written_artefacts(tmp_path)
    assert found == {"docs/reports/dotted.json", "docs/reports/log.json"}, found


def test_MUTATION_an_attributes_binding_is_resolved_in_ITS_OWN_method(tmp_path):
    """SCOPE, for the fourth time and through the newest door. `self.X = base / "out.json"` is
    resolved against the locals of the method that WRITES it, never against a sibling method's --
    a flat map over the class would let `other`'s `base` answer `__init__`'s expression and the
    oracle would report a path no execution produces.

    THE LOCAL NAMES COLLIDE ON PURPOSE. Both methods bind `base`, to different trees, and only one
    of those trees is where the artefact actually lands. A first version with different local names
    passed with a flat map installed, which is how a control becomes coverage. `LOG` keeps a
    failure attributable to the scope rule rather than to the fail-closed raise."""
    _tree(tmp_path, publisher=HEADER + (
        'LOG = ROOT / "docs" / "reports" / "log.json"\n'
        "class Writer:\n"
        "    def __init__(self):\n"
        '        base = ROOT / "docs" / "reports"\n'
        '        self.out = base / "out.json"\n'
        "    def other(self):\n"
        '        base = ROOT / "docs" / "design"\n'
        "        return base\n"
        "    def save(self):\n"
        '        LOG.write_text("{}")\n'
        '        self.out.write_text("{}")\n'))
    found = fs.written_artefacts(tmp_path)
    assert found == {"docs/reports/out.json", "docs/reports/log.json"}, found


# ---------------------------------------------------------------------------
# The real tree: the fixture must not be the only evidence
# ---------------------------------------------------------------------------
def test_the_instance_attribute_frame_is_LOAD_BEARING_in_the_REAL_tree():
    """THE POISON ROUND FOR THE ATTRIBUTE FRAME. Every leg above is a fixture, and a frame that
    resolved nothing in the actual repository would pass all of them while changing no
    classification at all -- which is what the `self._write(...)` frame would have been, and why
    it was measured rather than built.

    NO `len(gained) > 1` FLOOR HERE, and that is the honest reading rather than a weaker control.
    This frame has exactly ONE live instance in this tree: 2,058 classes, 8 (class, method) pairs
    holding a write destination, 2 touching `self.<attr>`, 1 surviving the rebound guard. Asserting
    a floor of two would be asserting a population this turn measured and found to be one. What the
    leg does assert is the PROPERTY -- that path is reachable only through the attribute -- so if a
    producer later spells its destination beside the write, this goes green on a smaller set."""
    with_frame = fs._write_reached_paths()
    real = fs._class_self_paths
    try:
        fs._class_self_paths = lambda node, module_file, inherited: {}
        without_frame = fs._write_reached_paths()
    finally:
        fs._class_self_paths = real
    gained = with_frame - without_frame
    assert ATTRIBUTE_REACHED_REAL_PATH in gained, sorted(gained)



def test_the_DEFAULT_seeding_is_LOAD_BEARING_in_the_REAL_tree():
    """THE POISON ROUND FOR THE DEFAULT. Same shape as the frame's below: a seeding that resolved
    nothing in the actual repository would pass every fixture above while changing no
    classification at all. So remove it from the live scan and measure what disappears.

    Keyed to the PROPERTY -- these paths are reachable ONLY through a signature default -- not to
    the nine of 2026-09-15. If a producer later spells its destination beside the write, this goes
    green on a smaller set rather than red on a number."""
    with_defaults = fs._write_reached_paths()
    real = fs._default_destinations
    try:
        fs._default_destinations = lambda node, module_file, inherited: {}
        without = fs._write_reached_paths()
    finally:
        fs._default_destinations = real
    gained = with_defaults - without
    assert DEFAULT_REACHED_REAL_PATH in gained, sorted(gained)
    assert len(gained) > 1, "one path is an instance; this was built as a class"


def test_a_RUNNING_RECORD_rewritten_whole_is_not_a_photograph_of_a_run():
    """Three of the nine the default seeding found are the append-wearing-a-rewrite shape, which
    is a HIGHER proportion than the helper frame's two in eight -- a default is how a module spells
    "the one place I keep my running record", so the door that finds them finds more of them. Each
    reads what is there, merges one run's contribution and writes the whole back, which passes the
    writing-MODE test that an `"a"` append would have failed. The corner ledger's own docstring
    says coverage is a property of the ENSEMBLE of runs; the receipt's says a death mid-write must
    never cost "the record of the 10 GB already bought", and a REVERT costs exactly that."""
    raw = fs._write_reached_paths()
    offered = fs.written_artefacts()
    for path in ("docs/design/visited_corner_ledger.json",
                 "docs/observability/edge_traffic.jsonl",
                 "docs/market_research/haduk_grid_pull_receipt.json"):
        assert path in raw, f"{path} is no longer write-reached -- this leg proves nothing now"
        assert path not in offered, f"{path} is being offered a REVERT"


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
