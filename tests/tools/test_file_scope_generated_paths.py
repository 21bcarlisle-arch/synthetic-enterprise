#!/usr/bin/env python3
"""R15 proof for the generated-path file_scope gate (class fix for the G13 starvation).

The control's job is to make one declaration impossible: an atom claiming ground a generator
rewrites, which makes it permanently invisible to its own build lane. So the mutations drive
that boundary from both sides -- generated ground offends, authored source does not -- and the
ratchet is driven in both directions, because a freeze that can only grow is a place debt goes
to be forgotten.

The fail-closed direction is toward RAISING. The tempting failure here is very quiet: if the
oracle finds nothing, no scope entry matches anything, `violations()` returns `[]`, and the gate
prints a clean tree. That is the FAIL-OPEN killer pattern exactly -- a passing result computed
from evidence nobody could read -- so both empty-oracle paths are tested to raise.
"""
from __future__ import annotations

import pytest

from tools import file_scope_generated_paths as fs
from tools import maturity_map_store as map_store  # noqa: E402

GENERATED = {"site/data/dashboard.json", "site/data/glossary.json"}


# ---------------------------------------------------------------------------
# The predicate: what counts as generated ground
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("entry", [
    "site/data/dashboard.json",   # the artefact itself
    "site/data/",                 # the directory, with a slash   (G13's actual declaration)
    "site/data",                  # the directory, without one    (H14's actual declaration)
    "docs/observability/",
    "docs/observability/scale_probe_10k/report.json",   # nested below the tree
])
def test_MUTATION_every_shape_of_generated_ground_offends(entry):
    """All three shapes are LIVE in the map today; a gate catching only the tidy one would have
    missed G13, which is the case it exists for."""
    assert fs.offends(entry, GENERATED)


@pytest.mark.parametrize("entry", [
    "tools/lab_query.py",
    "tests/tools/test_lab_query.py",
    "company/analytics/clv_three_horizon.py",
    "site/index.html",              # site/, but not site/data/
    "docs/design/maturity_map.yaml",  # docs/, but not a generated tree
])
def test_authored_source_does_NOT_offend(entry):
    """The other side of the boundary. A gate that flags ordinary source gets disabled, and a
    disabled gate is how the eight-day starvation happens again."""
    assert not fs.offends(entry, GENERATED)


# ---------------------------------------------------------------------------
# The ratchet: both directions
# ---------------------------------------------------------------------------
def test_MUTATION_a_new_declaration_fails_the_commit(monkeypatch):
    monkeypatch.setattr(fs, "violations",
                        lambda root=None: sorted(fs.FROZEN | {("NEW_atom", "site/data/x.json")}))
    problems = fs.gate_violations()
    assert len(problems) == 1
    assert problems[0].startswith("NEW: NEW_atom")
    assert "never be drawn" in problems[0]


def test_MUTATION_a_repaired_declaration_ALSO_fails_so_the_freeze_can_only_shrink(monkeypatch):
    """The direction people forget. If a repair does not force the freeze to shrink, the list
    silently becomes a permanent amnesty and the gate stops meaning anything."""
    frozen = sorted(fs.FROZEN)
    monkeypatch.setattr(fs, "violations", lambda root=None: frozen[1:])
    problems = fs.gate_violations()
    assert len(problems) == 1 and problems[0].startswith("STALE FREEZE:")


def test_the_frozen_set_exactly_matches_the_live_map(monkeypatch):
    """The ratchet's resting state. Green today; goes red the moment either side moves, which
    is the whole point of freezing rather than ignoring."""
    assert fs.gate_violations() == []


# ---------------------------------------------------------------------------
# FAIL-CLOSED -- the quiet one
# ---------------------------------------------------------------------------
def test_MUTATION_FAIL_CLOSED_an_oracle_that_scans_nothing_raises(monkeypatch, tmp_path):
    """Nothing scanned -> nothing generated -> no scope matches -> a serene clean tree. That is
    the exact fail-open shape R15 names, and it must raise instead."""
    with pytest.raises(fs.OracleUnavailable):
        fs.generated_artefacts(root=tmp_path)


def test_MUTATION_FAIL_CLOSED_an_oracle_that_finds_zero_artefacts_raises(monkeypatch, tmp_path):
    """Modules present, no artefacts found -- a plausible outcome of a refactor that changes how
    output paths are built. This project publishes a site from generated JSON, so zero is a
    broken oracle rather than good news, and the message says which."""
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "x.py").write_text("A = 1\n")
    with pytest.raises(fs.OracleUnavailable) as exc:
        fs.generated_artefacts(root=tmp_path)
    assert "broken oracle" in str(exc.value)


def test_MUTATION_FAIL_CLOSED_an_unreadable_map_raises(monkeypatch, tmp_path):
    monkeypatch.setattr(fs, "generated_artefacts", lambda root=None: GENERATED)
    with pytest.raises(fs.OracleUnavailable):
        fs.violations(root=tmp_path)


# ---------------------------------------------------------------------------
# The live tree
# ---------------------------------------------------------------------------
def test_the_oracle_finds_the_real_generated_artefacts():
    """Asserts the oracle's REACH, not a count. Pinning 116 would go red on the next generator
    added -- the pinned-literal defect this project found four times this week."""
    found = fs.generated_artefacts()
    assert len(found) > 50, "the segment-join oracle has lost its reach"
    assert any(p.startswith("site/data/") for p in found)
    assert any(p.startswith("docs/observability/") for p in found)


# ---------------------------------------------------------------------------
# The OTHER spelling of the same tree (delivery seat, 2026-09-15)
# ---------------------------------------------------------------------------
def _module(tmp_path, name: str, body: str):
    d = tmp_path / "tools"
    d.mkdir(exist_ok=True)
    (d / name).write_text(body, encoding="utf-8")


def test_MUTATION_a_path_spelled_as_ONE_WHOLE_STRING_is_generated(tmp_path):
    """THE DEFECT: the matcher wanted `docs` and `observability` as SEPARATE constants in one
    assignment, so `tools/canon_drift_check.py`'s `DEFAULT_REPORT =
    "docs/observability/canon_drift.json"` was invisible while its artefact sat squarely inside a
    GENERATED_TREES member. Restoring the segment-pair-only matcher makes this RAISE
    (nothing found at all), which is how the mutation was proven rather than assumed."""
    _module(tmp_path, "drift.py",
            'from pathlib import Path\n'
            'ROOT = Path(__file__).resolve().parents[1]\n'
            'DEFAULT_REPORT = "docs/observability/canon_drift.json"\n')
    assert fs.generated_artefacts(root=tmp_path) == {"docs/observability/canon_drift.json"}


def test_a_loose_constant_naming_SOMEBODY_ELSES_artefact_is_not_swept(tmp_path):
    """THE SCOPE IS THE DISTINCTION, and it is measured rather than inherited. An ASSIGNMENT is
    where a module names its own destination; a constant in a `for rel in (...)` that the body
    then READS is where it names an artefact belonging to somebody else --
    `knowledge_layer_gate.orphan_research` is the live instance. Widening to every string constant
    also sweeps PROSE (`"site/data/customers.json + site/data/dashboard.json"` is a real constant
    in this tree), so this control holds the boundary in both directions at once."""
    _module(tmp_path, "gateish.py",
            'from pathlib import Path\n'
            'PROJECT = Path(__file__).resolve().parents[1]\n'
            'ARTEFACT = "docs/observability/mine.json"\n'
            'def read_them():\n'
            '    for rel in ("site/data/not_mine.json", "site/data/nor_this.json"):\n'
            '        (PROJECT / rel).read_text()\n')
    found = fs.generated_artefacts(root=tmp_path)
    assert found == {"docs/observability/mine.json"}


# ---------------------------------------------------------------------------
# The path the MODULE wrote, not one joined from what was DECLARED
# (delivery seat, 2026-09-15)
# ---------------------------------------------------------------------------
def test_MUTATION_a_DEEPER_destination_is_emitted_WHOLE_and_not_flattened(tmp_path):
    """THE DEFECT: the match was MEMBERSHIP over an assignment's string constants and the emitted
    path was HARD-JOINED from the DECLARED prefix to any artefact-suffixed constant in scope. An
    intermediate directory segment carries no artefact suffix, so it was dropped from the join and
    the oracle emitted a path that skipped it. `simulation/premise_population.py:1189` writes
    `... / "docs" / "observability" / "scale_probe_10k" / "report.json"` and the oracle held
    `docs/observability/report.json`, which is not a file -- while the real artefact was in NEITHER
    oracle, so `origin_reconcile` classified a producer's output as somebody's work and led with how
    to LAND it.

    BOTH LEGS, because only one of them is the defect. The flattened path must be ABSENT and the
    whole path PRESENT: a control asserting only the second would pass with the fabrication still
    being emitted beside it, which is the state this replaced.

    MUTATION THAT REDDENS IT: restore `found.update(f"{prefix}/{s}" for s in parts if
    s.endswith(ARTEFACT_SUFFIXES))` under an `all(seg in parts ...)` membership test. Verified by
    doing it -- `site/data/report.json` comes back and `site/data/probe_dir/report.json` goes.
    """
    _module(tmp_path, "deep_producer.py",
            'from pathlib import Path\n'
            'PROJECT = Path(__file__).resolve().parents[1]\n'
            'OUT = PROJECT / "site" / "data" / "probe_dir" / "report.json"\n')
    found = fs.generated_artefacts(root=tmp_path)
    assert found == {"site/data/probe_dir/report.json"}, (
        "the matcher is not reconstructing the path in source order: a directory segment carrying "
        "no artefact suffix has been dropped from the join, so the oracle names a file that does "
        "not exist and misses the one that does"
    )


def test_MUTATION_two_declared_trees_in_ONE_assignment_do_not_emit_a_CROSS_PRODUCT(tmp_path):
    """THE SECOND HALF OF THE SAME DEFECT, and the one with the bigger count. `parts` was every
    string constant in one assignment, so an assignment naming TWO declared trees satisfied BOTH
    membership tests and emitted every artefact name under BOTH prefixes.
    `tools/mirror_github_pages.py:22` names four state files across `site/state` and `site/data` and
    the oracle held EIGHT members for it, four of them fictional.

    THE FIXTURE MIRRORS THAT SHAPE EXACTLY -- one assignment, one tuple, two trees -- because the
    defect is a property of the assignment and not of the file. Reading each `/`-chain separately is
    what fixes it, and the assertion is EQUALITY rather than two `in` checks: the cross product's
    harm is the members that should not be there, so a control that only asks for the right two
    passes with the wrong two beside them.

    MUTATION THAT REDDENS IT: the same restoration as the control above -- the set grows to four.
    """
    _module(tmp_path, "mirrorish.py",
            'from pathlib import Path\n'
            'PROJECT = Path(__file__).resolve().parents[1]\n'
            'PAIRS = (\n'
            '    PROJECT / "site" / "state" / "from_state.json",\n'
            '    PROJECT / "site" / "data" / "from_data.json",\n'
            ')\n')
    found = fs.generated_artefacts(root=tmp_path)
    assert found == {"site/state/from_state.json", "site/data/from_data.json"}, (
        "one assignment naming two declared trees is emitting the cross product -- every artefact "
        "name under both prefixes, whichever tree it actually belongs to"
    )


def test_a_chain_with_an_OPAQUE_MIDDLE_segment_is_declined_whole(tmp_path):
    """A MISSING SEGMENT FABRICATES AND A MISSING HEAD DOES NOT, which is the asymmetry the
    reconstruction rests on and the reason it is asserted rather than commented.

    `PROJECT / subdir / "x.json"` cannot be read: the middle segment is a name this oracle does not
    resolve, and joining what IS legible would re-manufacture exactly the flattened path the repair
    removed -- `site/data/x.json` for a file that lives somewhere else entirely, in a set whose
    consumer's remedy is REVERT. So the chain is declined whole. An opaque LEFT ROOT is the ordinary
    case and must NOT be declined: `PROJECT` is where every producer in this tree starts.

    BOTH DIRECTIONS IN ONE FIXTURE ON PURPOSE. A control holding only the decline would pass if the
    resolver declined everything, which is the fail-closed reading that looks identical to a clean
    one -- so the legible producer beside it is what proves the decline is selective. It also keeps
    the call off `OracleUnavailable`, which an empty result would raise.

    MEASURED COST: 2,464 `/`-chains in the scanned trees, 1,599 declined this way, and ZERO of those
    end in an artefact-suffixed name -- they are arithmetic (`len(stayed) / len(scored)`), which
    shares an operator with the path join and nothing else.

    THE OPAQUE CHAIN IS AN ASSIGNMENT AND THE FIRST DRAFT HAD IT IN A `return`, WHICH MADE THIS
    CONTROL A TAUTOLOGY (delivery seat, 2026-09-15). Both the matcher and the shape it replaced are
    held to `Assign`/`AnnAssign` nodes, so an expression in a bare `return` is never visited by
    either -- the control passed because nothing looked at its fixture, not because the chain was
    declined, and it stayed green with the hard join restored. Found by running the mutation this
    docstring names rather than by reading it, which is the only way that class of pass is ever
    found.
    """
    _module(tmp_path, "opaque.py",
            'from pathlib import Path\n'
            'PROJECT = Path(__file__).resolve().parents[1]\n'
            'def build(subdir):\n'
            '    out = PROJECT / "site" / "data" / subdir / "buried.json"\n'
            '    return out\n')
    _module(tmp_path, "legible.py",
            'from pathlib import Path\n'
            'PROJECT = Path(__file__).resolve().parents[1]\n'
            'OUT = PROJECT / "site" / "data" / "legible.json"\n')
    found = fs.generated_artefacts(root=tmp_path)
    assert found == {"site/data/legible.json"}, (
        "a chain whose MIDDLE segment could not be read was joined anyway, which invents a path "
        "for a file that lives somewhere else -- or the opaque ROOT case was declined too, which "
        "would blind the oracle to every producer that starts from PROJECT"
    )


def test_MUTATION_a_GLOB_PATTERN_is_not_a_destination(tmp_path):
    """THE DEFECT: this oracle has NO write-site evidence requirement, so a search pattern satisfies
    it exactly as a destination does. `tools/couple_value_based_pricing.py:499` and
    `tools/r1_inference_ceiling.py:182` both spell
    `glob.glob(str(PROJECT / "docs" / "reports" / "run_output_*.json"))`, and the oracle held
    `docs/reports/run_output_*.json` as if it were a file. Ordered reconstruction reads that chain
    PERFECTLY -- which is the point: this is not a reading defect, it is the classifier standing on
    a declaration where its sibling `written_artefacts` stands on a write site.

    BOTH SPELLINGS IN ONE FIXTURE, because the refusal is placed AFTER both branches and that
    placement is the claim. A `/`-chain pattern and a whole-string pattern are two different doors
    into the same set, and this project's own record is full of carve-outs honoured by one of two
    unioned routes -- which is no carve-out at all. The real destination beside them is what keeps
    the control from passing on a resolver that declines everything.

    IT CANNOT COST A REAL PATH TODAY, asked of `git ls-files` rather than assumed: zero tracked
    paths in this repo contain `*`, `?` or `[`.

    MUTATION THAT REDDENS IT: delete the `GLOB_METACHARACTERS` filter in `generated_artefacts`.
    Verified by doing it -- both patterns come back.
    """
    _module(tmp_path, "globber.py",
            'import glob\n'
            'from pathlib import Path\n'
            'PROJECT = Path(__file__).resolve().parents[1]\n'
            'REAL = PROJECT / "docs" / "reports" / "ledger.json"\n'
            'FOUND = glob.glob(str(PROJECT / "docs" / "reports" / "run_output_*.json"))\n'
            'ALSO = "docs/reports/run_output_?.json"\n')
    assert fs.generated_artefacts(root=tmp_path) == {"docs/reports/ledger.json"}, (
        "a glob PATTERN reached the generated set as if it were a write destination. A path with a "
        "metacharacter can never match anything git reports, so it is inert at the reconciler and "
        "purely misleading to a reader -- which is exactly the reading that hid the hard-join "
        "defect for eight weeks: the oracle contained a path that looked right"
    )


def test_MUTATION_the_gates_OWN_freeze_list_is_not_evidence_about_itself(monkeypatch, tmp_path):
    """CIRCULARITY, and it is the reason `_SELF` exists. `FROZEN` holds `(atom_id, file_scope)`
    pairs COPIED OUT OF THE MATURITY MAP -- the declarations this gate judges. Read back as
    constants they make four map declarations prove that the ground they name is generated, so
    `violations()` would agree with the map by construction and a frozen entry would keep itself
    alive. Both legs are driven: with `_SELF` pointed elsewhere the fixture's freeze path IS read
    (so the control cannot pass by the fixture simply missing the matcher), and with `_SELF`
    pointed at it, it is not."""
    _module(tmp_path, "gate_with_a_freeze.py",
            'FROZEN = frozenset({\n'
            '    ("SOME_atom", "docs/observability/frozen_debt.json"),\n'
            '})\n')
    _module(tmp_path, "a_real_producer.py",
            'from pathlib import Path\n'
            'OUT = Path(__file__).resolve().parents[1] / "site" / "data" / "real.json"\n')

    assert "docs/observability/frozen_debt.json" in fs.generated_artefacts(root=tmp_path)

    monkeypatch.setattr(fs, "_SELF", (tmp_path / "tools" / "gate_with_a_freeze.py").resolve())
    found = fs.generated_artefacts(root=tmp_path)
    assert found == {"site/data/real.json"}, (
        "the gate read its own freeze list as a producer's evidence -- an atom's declaration "
        "proving the ground it stands on is generated"
    )


def test_the_gate_half_is_SUBSUMED_by_the_prefix_test_and_the_docstring_says_so(monkeypatch):
    """A PROPERTY, NOT TODAY'S ANSWER, and the claim it guards is load-bearing prose. The drawn
    item said a path this oracle cannot see is a `file_scope` entry that silently starves its
    atom. It is not: `offends()` decides every entry under a generated-tree PREFIX without
    consulting the set at all, and every member this oracle can return is under one -- so
    `gate_violations()` cannot move however wide the oracle gets, and the consumer that DOES move
    is `origin_reconcile`'s exact-membership union. If a GENERATED_TREES entry or `offends` ever
    changes so that membership stops being subsumed, this goes red and the docstring above is
    stale -- which is the only way that sentence can be kept honest."""
    found = fs.generated_artefacts()
    escaping = sorted(p for p in found if not fs.offends(p, set()))
    assert escaping == [], (
        f"{len(escaping)} oracle members are no longer caught by the prefix test alone "
        f"({escaping[:3]}), so widening the oracle now CAN move the commit gate and the frozen "
        "debt list must be re-measured against the wider set"
    )


def test_the_repaired_instance_stays_repaired():
    """G13 is the atom this class fix was extracted from. Asserts the PROPERTY (no generated
    ground in its scope) rather than the exact path list, so a legitimate scope edit does not
    fail here while a regression to `site/data/` does."""
    import yaml
    loaded = map_store.load_atoms(fs.MAP_PATH)
    atoms = loaded if isinstance(loaded, list) else (loaded or {}).get("atoms", [])
    g13 = next(a for a in atoms
               if isinstance(a, dict) and a.get("id") == "G13_projection_consumers")
    generated = fs.generated_artefacts()
    offending = [s for s in (g13.get("file_scope") or []) if fs.offends(s, generated)]
    assert offending == [], (
        f"G13 has regressed onto generated ground ({offending}) -- it will stop being drawn "
        "again, silently, exactly as it did for the eight days before 2026-08-19"
    )
    assert g13.get("file_scope"), "G13 now has an EMPTY file_scope, which starves it differently"


# ---------------------------------------------------------------------------
# A destination bound in TWO expressions (delivery seat, 2026-09-15)
# ---------------------------------------------------------------------------
def test_MUTATION_a_destination_bound_in_TWO_expressions_is_generated(tmp_path):
    """THE DEFECT: resolution stopped at the assignment boundary. A module that binds its output
    DIRECTORY in one statement and its files beside it was invisible to this oracle, because
    neither expression alone names a path that is under a declared tree AND an artefact -- the
    directory has no suffix, the join has no legible head.

    THE FIXTURE IS `tools/scale_probe_10k.py:119-121` REDUCED, and that module is the measured
    instance rather than an illustration: it contributed NOTHING to either oracle. Its
    `report.json` was a member only because `simulation/premise_population.py:1190` happens to
    spell the whole chain in one expression as a READER, and `prediction_register.json`, which no
    reader spells whole, was in NEITHER oracle -- so `origin_reconcile._split_generated` called a
    producer's output somebody's WORK and led with how to LAND it.

    THE THIRD LEG IS THE ONE THAT MATTERS AND IT IS THE UNRESOLVED HEAD. `elsewhere` is joined onto
    a name this scope never binds, and it must NOT appear: that is the opaque-head fallback the
    whole reconstruction rests on, and a resolver that guessed a prefix for it would fabricate
    under a declared tree, in a set whose consumer's remedy is REVERT. Asserting only the two
    recovered paths would pass with that fabrication sitting beside them.

    MUTATION THAT REDDENS IT: delete the `ast.Name`/`known` branch in `_chain_segments` so an
    unresolved head is the only head. Verified by doing it -- both `probe_dir` paths go and the
    set collapses to `{"site/data/legible.json"}`.
    """
    _module(tmp_path, "two_expressions.py",
            'from pathlib import Path\n'
            'PROJECT = Path(__file__).resolve().parents[1]\n'
            'ARTEFACT_DIR = PROJECT / "site" / "data" / "probe_dir"\n'
            'REPORT_PATH = ARTEFACT_DIR / "report.json"\n'
            'REGISTER_PATH = ARTEFACT_DIR / "prediction_register.json"\n'
            'STRANDED = elsewhere / "never_bound.json"\n')
    _module(tmp_path, "legible.py",
            'from pathlib import Path\n'
            'OUT = Path(__file__).resolve().parents[1] / "site" / "data" / "legible.json"\n')
    found = fs.generated_artefacts(root=tmp_path)
    assert found == {
        "site/data/probe_dir/report.json",
        "site/data/probe_dir/prediction_register.json",
        "site/data/legible.json",
    }, (
        "a destination whose directory and filename are bound in two expressions is not being "
        "resolved (so its producer's output is offered a LANDING by the reconciler), or a chain "
        "whose head this scope never bound was given a prefix anyway, which fabricates"
    )


def test_MUTATION_a_name_does_not_leak_ACROSS_scopes(tmp_path):
    """THE FABRICATION THE NAME MAP BUYS IF IT IS FLAT, and the reason this half scopes at all.
    `_own_scope`'s docstring records what a module-wide map did to the write-keyed oracle: a
    one-letter `p` bound to `DIRECTOR_AXES.md` in one function answered a `p.write_text(...)` in
    another, and the gate reported the DIRECTOR'S OWN AXES as a generated artefact -- a set whose
    consumer's remedy is `git show HEAD:<path> > <path>`.

    THE TWO FIXTURE NAMES COLLIDE ON PURPOSE. A scope-leak control whose scopes use DIFFERENT
    names passes with the defect fully installed, because nothing in the flat map can answer for
    anything else -- it measures the fixture, not the mechanism. So both functions bind `OUT_DIR`,
    and the leak has somewhere to go.

    THE DIRECTION IS ASYMMETRIC AND ONLY ONE HALF IS VISIBLE. `docs/design` is not a declared tree,
    so the leak that MATTERS is `site/data` answering the axes join -- `site/data/DIRECTOR_AXES.md`,
    a path that does not exist, under a declared tree, offered a REVERT. The other direction
    (`docs/design/feed.json`) is dropped by the prefix test either way and proves nothing, which is
    why the assertion is EQUALITY.

    MEASURED, AND THE ANSWER WAS ZERO. A flat module-wide map over the five scanned trees adds no
    member beyond the scoped one on 2026-09-15 -- so today the tree-keyed half is safe by ACCIDENT,
    exactly as `WRITTEN_BUT_NOT_REPRODUCIBLE` was until `("docs", "status")` was declared. That is
    why this control is a FIXTURE and not a census over the live tree: a census would be green with
    the scoping deleted, and would go red only once the accident had already cost something.

    MUTATION THAT REDDENS IT: hand `known` (not `inherited`) down in `_generated_in_scope`, or
    replace the scoped walk in `generated_artefacts` with `ast.walk(mod)` over one name map.
    Verified by doing it -- `site/data/DIRECTOR_AXES.md` appears.
    """
    _module(tmp_path, "two_scopes.py",
            'from pathlib import Path\n'
            'PROJECT = Path(__file__).resolve().parents[1]\n'
            'def publishes_a_feed():\n'
            '    OUT_DIR = PROJECT / "site" / "data"\n'
            '    feed = OUT_DIR / "feed.json"\n'
            '    return feed\n'
            'def reads_the_directors_axes():\n'
            '    OUT_DIR = PROJECT / "docs" / "design"\n'
            '    axes = OUT_DIR / "DIRECTOR_AXES.md"\n'
            '    return axes\n')
    found = fs.generated_artefacts(root=tmp_path)
    assert found == {"site/data/feed.json"}, (
        "a name bound in ONE function answered a join in ANOTHER -- the flat-name-map defect that "
        "reported the director's own axes as a generated artefact, arriving through the "
        "tree-keyed door this time"
    )


def test_a_CLASS_BODY_does_not_lend_its_names_to_its_methods(tmp_path):
    """PYTHON, NOT A NICETY. A method's bare `OUT_DIR` reads the module global; it never sees the
    class attribute beside it, and a resolver that let it would emit a path the code cannot build
    -- `NameError` at runtime, a member under a declared tree in the set.

    THE JOIN IS AN ASSIGNMENT AND NOT A `return`, which is the trap this file has already been
    caught by once (see `test_a_chain_with_an_OPAQUE_MIDDLE_segment_is_declined_whole`): both
    halves of the matcher are held to `Assign`/`AnnAssign`, so a chain in a bare `return` is never
    visited and the control would pass for lack of a SUBJECT rather than because the name was
    refused. The legible producer beside it keeps the call off `OracleUnavailable`, which an empty
    result raises.

    IT CAUGHT ITS OWN AUTHOR, WHICH IS WHY IT IS HERE RATHER THAN A COMMENT. The first draft of
    `_generated_in_scope` tested `isinstance(nested, ast.ClassDef)` -- the CHILD -- which reads
    plausibly and does the exact opposite: it lends a class body's names to its own methods. This
    control went red on the commit that added it.

    AND THE DEFECT COST ZERO MEMBERS ON THE LIVE TREE: 227 / union 255 with it and without it. A
    census would have been green on a resolver that emits paths the code could not build, so the
    property is held by a fixture and the zero is recorded rather than mistaken for absence.

    MUTATION THAT REDDENS IT: hand `known` instead of `inherited` into the `ClassDef` branch of
    `_generated_in_scope`. Verified by doing it -- `site/data/fabricated.json` appears.
    """
    _module(tmp_path, "classy.py",
            'from pathlib import Path\n'
            'PROJECT = Path(__file__).resolve().parents[1]\n'
            'class Writer:\n'
            '    OUT_DIR = PROJECT / "site" / "data"\n'
            '    def go(self):\n'
            '        target = OUT_DIR / "fabricated.json"\n'
            '        return target\n')
    _module(tmp_path, "legible.py",
            'from pathlib import Path\n'
            'OUT = Path(__file__).resolve().parents[1] / "site" / "data" / "legible.json"\n')
    found = fs.generated_artefacts(root=tmp_path)
    assert found == {"site/data/legible.json"}, (
        "a class attribute answered a method's bare name -- the resolver is emitting a path the "
        "module could not build if it ran"
    )
