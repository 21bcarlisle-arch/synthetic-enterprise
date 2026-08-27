"""THE CLASS CONTROL for a defect that wedged publishing twice in five hours.

THE CLASS. `background/publish_scope.py::resolve_scope` REFUSES a root that is not a checkout
of this repo, and `process_run_complete._run_gate_in` turns that refusal into `(False, False)`
before argv is ever built. Any test that hands `run_fast_tests` a hand-built stand-in tree is
therefore one declaration-change away from asserting against a refusal instead of against its
own subject -- and because the refusal is indistinguishable from a red at the publisher, the
whole machine stops publishing while every one of the new control's own tests stays green.

THE RECORD, both instances `observed-with-evidence`:

* 2026-08-12 03:44Z, `2b8a7f0c5` -- `test_publish_gate_scope.py`'s empty stub root. Fixed
  INLINE. ~60h of publishing.
* 2026-08-12 ~02:31Z onward, this tick -- `test_publish_gate_subject_is_head.py`'s `sandbox`
  repo, three tests at once, four more gate cycles red.

R10 is explicit that an absurdity-class defect may not be closed with an instance fix. The
shape now lives once in `publish_gate_root_shape.py`; this module is what makes a FUTURE
caller inherit it rather than hand-typing the shape a third time.

WHAT IS ASSERTED, in two independent halves:
1. BEHAVIOUR -- the shared helper's output really does clear the refusal, and a bare directory
   really does trip it (that pair is the helper's own mutation; without the second half the
   first could pass on a resolver that never refuses anything).
2. POPULATION -- every test module that calls `run_fast_tests` gets its root from the helper.
   The predicate is applied to SOURCE TEXT through `module_is_compliant`, so the mutation
   below can feed it a synthetic non-compliant module and prove the census can fail. A census
   only ever tried on a compliant population cannot be shown to detect anything.
"""
import ast
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from background import publish_scope  # noqa: E402
from tests.background.publish_gate_root_shape import (  # noqa: E402
    materialise_repo_shaped_root,
)

HELPER_MODULE = "publish_gate_root_shape"
GATE_ENTRY_POINT = "run_fast_tests("
TEST_ROOT = REPO / "tests"

# A module may sit outside the rule only with a stated reason, and the reason is read by a
# human, not by the test -- an exemption with no reason is what a silent carve-out looks like.
EXEMPT = {
    # module path (relative to the repo) -> why its roots can never reach resolve_scope
}


def _really_calls_the_gate(source: str) -> bool:
    """Does this module CALL `run_fast_tests`, or merely mention it?

    THE SUBSTRING TEST WAS NOT A TEST OF CALLING (2026-08-27). `GATE_ENTRY_POINT` is the literal
    text `run_fast_tests(`, and `tests/background/test_publisher_deadline_exceeds_its_gate.py`
    contains it inside a STRING LITERAL:

        body = src[src.index("tests_ok, timed_out = run_fast_tests("):]

    -- a module that reads the publisher's source to check where its refusal is composed. It
    calls nothing, supplies no root, and cannot reach `resolve_scope` at any depth. The census
    named it an offender anyway, and the only remedies on offer were to import a helper it has
    no use for or to take an EXEMPT entry for a rule it never broke.

    That is the mention-read-as-a-claim shape, and the honest fix is in the READER: parse the
    module and look for a real `ast.Call`. The substring survives as a cheap pre-filter, and an
    unparseable module FAILS CLOSED back to it -- a file this control cannot read is not thereby
    innocent.
    """
    if GATE_ENTRY_POINT not in source:
        return False
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return True
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "run_fast_tests":
            return True
        if isinstance(func, ast.Attribute) and func.attr == "run_fast_tests":
            return True
    return False


def module_is_compliant(source: str) -> bool:
    """Does `source` obtain its gate root from the shared helper, given that it drives the gate?

    A module that never reaches the gate entry point is trivially compliant -- it cannot supply
    a root to the refusal. One that does must name the helper.
    """
    if not _really_calls_the_gate(source):
        return True
    return HELPER_MODULE in source


def _modules_that_drive_the_gate():
    for path in sorted(TEST_ROOT.rglob("test_*.py")):
        rel = path.relative_to(REPO).as_posix()
        if rel in EXEMPT:
            continue
        try:
            source = path.read_text(errors="replace")
        except OSError:  # pragma: no cover -- an unreadable test file is its own alarm
            continue
        if GATE_ENTRY_POINT in source:
            yield rel, source


# ── 1. BEHAVIOUR: the helper clears the refusal, and its absence trips it ─────

def test_a_helper_shaped_root_is_not_refused(tmp_path):
    """The property every caller is relying on, asserted against the real resolver."""
    root = materialise_repo_shaped_root(tmp_path / "shaped")

    scope = publish_scope.resolve_scope(root=root)

    assert scope.get("root_unavailable") is not True, scope["reason"]


def test_a_bare_directory_is_refused(tmp_path):
    """MUTATION of the test above (R15): remove the shape and the verdict must flip.

    This is the exact condition both wedges supplied, and it is what proves the green above is
    produced BY the helper rather than by a resolver that refuses nothing."""
    bare = tmp_path / "bare"
    bare.mkdir()

    scope = publish_scope.resolve_scope(root=bare)

    assert scope.get("root_unavailable") is True, (
        "the refusal this whole module exists for did not fire -- if resolve_scope no longer "
        "refuses an absent root, the population half below is guarding nothing")


def test_the_shape_is_taken_from_the_declaration_not_hand_typed(tmp_path):
    """A source added to PUBLISH_PATH_SOURCES must appear in every stub root, automatically."""
    root = materialise_repo_shaped_root(tmp_path / "shaped")

    for source in publish_scope.PUBLISH_PATH_SOURCES:
        assert (root / source).exists(), source
    assert (root / publish_scope.ROOT_REPO_MARKER).is_dir()


def test_the_helper_does_not_overwrite_a_real_file(tmp_path):
    """Applied to a populated stand-in tree it must add shape, never replace content."""
    root = tmp_path / "populated"
    (root / "background").mkdir(parents=True)
    real = root / "background" / "process_run_complete.py"
    real.write_text("REAL = 1\n")

    materialise_repo_shaped_root(root)

    assert real.read_text() == "REAL = 1\n"


# ── 2. POPULATION: nobody hand-types the shape again ─────────────────────────

def test_every_module_that_drives_the_gate_uses_the_shared_root_shape():
    offenders = [rel for rel, source in _modules_that_drive_the_gate()
                 if not module_is_compliant(source)]

    assert not offenders, (
        "these test modules call {} with a root they build themselves: {}. Use "
        "tests/background/{}.materialise_repo_shaped_root -- a hand-typed root shape is the "
        "defect that wedged publishing on 2026-08-12, twice, from two different files."
        .format(GATE_ENTRY_POINT.rstrip("("), ", ".join(offenders), HELPER_MODULE))


def test_the_population_is_not_empty():
    """A census whose population is empty passes for the wrong reason (vacuity guard)."""
    assert list(_modules_that_drive_the_gate()), (
        "no test module drives the gate -- either the entry point was renamed (update "
        "GATE_ENTRY_POINT) or the coverage this census claims does not exist")


@pytest.mark.parametrize("source, compliant", [
    ("passed, timed_out = prc.run_fast_tests(sha)", False),
    ("from tests.background.publish_gate_root_shape import materialise_repo_shaped_root\n"
     "passed, timed_out = prc.run_fast_tests(sha)", True),
    ("head = tmp_path / 'head'\nhead.mkdir()", True),
])
def test_the_census_predicate_can_fail(source, compliant):
    """MUTATION of the census (R15): a synthetic non-compliant module must be flagged.

    The live population is compliant, so the assertion above passes today either way -- this
    is what shows it would stop passing when a new module hand-builds a root."""
    assert module_is_compliant(source) is compliant


# ── 3. THE NARROWING'S PARTNERS (2026-08-27) ─────────────────────────────────
# A narrowing that also silences the normal shape is worse than the over-trigger it fixed, so
# each direction gets its own assertion against a synthetic module.

def test_a_module_that_really_CALLS_the_gate_is_still_caught():
    """THE ONE THAT MATTERS. If the AST predicate stopped seeing real calls, this census would
    pass over every hand-typed root -- the exact defect that wedged publishing twice on
    2026-08-12 -- while looking greener than before."""
    offender = (
        "def test_thing(tmp_path):\n"
        "    root = tmp_path / 'mine'\n"
        "    root.mkdir()\n"
        "    tests_ok, timed_out = run_fast_tests(root=root)\n"
    )
    assert _really_calls_the_gate(offender)
    assert not module_is_compliant(offender)


def test_a_qualified_call_is_caught_too():
    source = "def t():\n    prc.run_fast_tests(root=r)\n"
    assert _really_calls_the_gate(source)


def test_a_module_that_only_QUOTES_the_entry_point_is_not_an_offender():
    """The 2026-08-27 false positive, frozen. `test_publisher_deadline_exceeds_its_gate.py`
    reads the publisher's own source to check where its refusal wording is composed."""
    reader = (
        "def test_the_refusal_is_composed_in_one_place():\n"
        "    body = src[src.index('tests_ok, timed_out = run_fast_tests('):]\n"
        "    assert '_gate_refusal(' in body\n"
    )
    assert not _really_calls_the_gate(reader)
    assert module_is_compliant(reader)


def test_an_unparseable_module_FAILS_CLOSED_to_the_substring():
    """A file this control cannot read is not thereby innocent. The narrowing must not become a
    way to escape the census by being syntactically broken."""
    broken = "def t(:\n    run_fast_tests(root=r)\n"
    assert _really_calls_the_gate(broken)
    assert not module_is_compliant(broken)


def test_a_module_that_never_mentions_the_gate_is_trivially_compliant():
    assert module_is_compliant("def test_unrelated():\n    assert True\n")
