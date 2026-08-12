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


def module_is_compliant(source: str) -> bool:
    """Does `source` obtain its gate root from the shared helper, given that it drives the gate?

    A module that never reaches the gate entry point is trivially compliant -- it cannot supply
    a root to the refusal. One that does must name the helper.
    """
    if GATE_ENTRY_POINT not in source:
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
