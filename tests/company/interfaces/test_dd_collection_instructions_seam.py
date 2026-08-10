"""R15 control for the DD-COLLECTIONS seam (KNIFE pass 3, B4, the design's last edge).

WHAT THIS SUITE IS FOR — the property NO other instrument in the tree can see
-----------------------------------------------------------------------------
`B4_billing_mechanics_reached_directly` took `simulation/dd_collection_book.py`'s
import of `company.billing.direct_debit` and replaced it with instructions received
through `company/interfaces/dd_collection_instructions.py`. Before the cut the world
opened a `DirectDebitBook`, created mandates on it and appended `DDPaymentAttempt`s —
it OPERATED the supplier's collection register. After it, the world runs the rails and
reports what happened to the money.

That property rests on the door staying NARROW, and the door's narrowness is invisible
to every static instrument already watching:

  RE-EXPORTING THE REGISTER WOULD MOVE NO WALL EDGE. Adding `DirectDebitBook` (or
  `DDPaymentAttempt`, or `next_collection_on_day`, or the re-estimation constants) to
  this module would let the SIM construct the supplier's register again, and the
  epistemic ratchet would stay GREEN, because the SIM's import still terminates on the
  exempt seam package. The ratchet is blind to this BY CONSTRUCTION. Test 2 performs
  the widening on the real file and watches this control fire; test 3 is the vacuity
  guard that proves the blindness rather than assuming it — the same mutation leaves
  the walker's crossing set bit-identical, so this control is catching something
  nothing else does.

THE SECOND CONTROL, AND WHY IT ASKS THE WALKER RATHER THAN THE TEXT
--------------------------------------------------------------------
Test 4 asserts no SIM module names the register module at all. It calls
`tools.epistemic_wall.live_crossings()` — the one shared definition of "a crossing"
this pass extracted as its first step — and never a substring scan, because a
substring scan fails on its own subject here: the docstrings recording WHY the import
went away contain both `company.billing.direct_debit` and `DirectDebitBook`. That is
the `REVIEW_GATE must match idleness, not prose mentioning the string` class, which
bit this programme once already at §3a of the register.

THE LIMIT, STATED RATHER THAN GLOSSED
--------------------------------------
Neither control can see a COPY. If someone re-implemented `next_collection_on_day`'s
arithmetic inside `simulation/` under a different name, no edge would appear and no
forbidden name would be reachable — the world would simply hold a second copy of the
supplier's rule, which is the `one name, two numbers` defect this register names
elsewhere. Nothing here detects that, and saying so is cheaper than a control that
implies it does.
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys
from pathlib import Path

import pytest

import company.interfaces.dd_collection_instructions as seam
from tools.epistemic_wall import live_crossings

REPO_ROOT = Path(__file__).resolve().parents[3]
SEAM_SOURCE = REPO_ROOT / "company" / "interfaces" / "dd_collection_instructions.py"
WORLD_SOURCE = REPO_ROOT / "simulation" / "dd_collection_book.py"

# The company machinery a caller must not be able to reach through the door. Each
# entry is something the world genuinely held before this cut.
FORBIDDEN_AT_THE_DOOR = (
    "DirectDebitBook",          # it opened one
    "DirectDebitMandate",       # it read one
    "DDPaymentAttempt",         # it constructed them
    "next_collection_on_day",   # it snapped its own collection dates
    "AMENDMENT_MATERIALITY_THRESHOLD_GBP",  # it applied the supplier's re-estimation
    "AMENDMENT_WINDOW_BILLS",              # ... and chose its window
    "direct_debit",             # the module itself, reachable as an attribute
    "dd_collections_desk",
    "statistics",               # the re-estimation's own statistic
)


class _Mutant:
    """Perform a defect on the REAL source file, load THAT file as a throwaway
    module, then restore byte-for-byte and verify the restoration.

    Loaded under a fresh name rather than by `importlib.reload`: reload updates a
    namespace in place and never removes names, so a re-export mutation would survive
    its own restoration and leak into every later test in this file. Bytecode caching
    is off for the duration and the cached `.pyc` is dropped afterwards — a mutation
    that changes no bytes of LENGTH leaves the restored file the same size, often in
    the same mtime second, and CPython then serves the MUTANT back from cache for the
    rest of the session. A mutation harness that poisons the suite it protects is
    worse than none.
    """

    def __init__(self, path: Path, old: str, new: str, name: str):
        self.path, self.name = path, name
        self.original = path.read_text()
        assert old in self.original, "mutation target absent — the mutation is vacuous"
        self.mutated_text = self.original.replace(old, new, 1)
        assert self.mutated_text != self.original

    def __enter__(self):
        self._prev_dont_write = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        self.path.write_text(self.mutated_text)
        try:
            spec = importlib.util.spec_from_file_location(self.name, self.path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[self.name] = module
            spec.loader.exec_module(module)
        finally:
            self.path.write_text(self.original)
            self._drop_cached_bytecode()
            sys.dont_write_bytecode = self._prev_dont_write
        return module

    def _drop_cached_bytecode(self):
        try:
            os.unlink(importlib.util.cache_from_source(str(self.path)))
        except (FileNotFoundError, NotImplementedError, ValueError):
            pass
        importlib.invalidate_caches()

    def __exit__(self, *exc):
        sys.modules.pop(self.name, None)
        self.path.write_text(self.original)
        self._drop_cached_bytecode()
        assert self.path.read_text() == self.original, "restoration left the tree dirty"
        return False


class _MutantOnDisk:
    """Same restore discipline, but the mutation is only ever READ by the walker —
    nothing imports it. Used for the world-side re-injection, where importing the
    mutant would install a second copy of the SIM module in `sys.modules`."""

    def __init__(self, path: Path, old: str, new: str):
        self.path = path
        self.original = path.read_text()
        assert old in self.original, "mutation target absent — the mutation is vacuous"
        self.mutated_text = self.original.replace(old, new, 1)
        assert self.mutated_text != self.original

    def __enter__(self):
        self.path.write_text(self.mutated_text)
        return self

    def __exit__(self, *exc):
        self.path.write_text(self.original)
        assert self.path.read_text() == self.original, "restoration left the tree dirty"
        return False


# ── 1. The door publishes instructions, and nothing else ────────────────────


def test_the_door_exposes_only_the_desk_and_its_instructions():
    assert seam.__all__ == [
        "AmendmentInstruction",
        "CollectionInstruction",
        "DirectDebitCollectionsDesk",
        "MandateSetupInstruction",
        "open_collections_desk",
    ]
    reachable = [n for n in FORBIDDEN_AT_THE_DOOR if hasattr(seam, n)]
    assert reachable == [], (
        "the DD-collections door hands the world back the supplier's own collection "
        "register machinery: " + ", ".join(reachable) + ". The epistemic ratchet "
        "cannot see this — the SIM's import still terminates on the exempt seam "
        "package — so the widening would be silent."
    )


# ── 2. MUTATION: a widened door is caught ───────────────────────────────────


WIDENINGS = [
    # (a) The convenience re-export: "the world needs the type for its annotation".
    # This is the exact temptation `build_dd_collection_book`'s unannotated return
    # records refusing, so it is the mutation most likely to be performed for real.
    (
        "__all__ = [",
        "from company.billing.direct_debit import DirectDebitBook  # noqa: F401\n\n__all__ = [",
        "DirectDebitBook",
    ),
    # (b) "Let the world record its own attempts" — the register's construction back
    # in the world's hands, which is precisely what B4 said this edge was about.
    (
        "__all__ = [",
        "from company.billing.direct_debit import DDPaymentAttempt  # noqa: F401\n\n__all__ = [",
        "DDPaymentAttempt",
    ),
    # (c) The supplier's re-estimation routine, handed over as a constant.
    (
        "__all__ = [",
        "from company.billing.dd_collections_desk import AMENDMENT_WINDOW_BILLS  # noqa: F401\n\n__all__ = [",
        "AMENDMENT_WINDOW_BILLS",
    ),
]


@pytest.mark.parametrize("old,new,leaked", WIDENINGS)
def test_mutation_a_widened_door_is_caught(old, new, leaked):
    """PERFORM the widening on the real file and confirm the control's subject moves."""
    with _Mutant(SEAM_SOURCE, old, new, f"_mutant_ddcoll_{leaked}") as mutant:
        assert hasattr(mutant, leaked), "vacuity: the mutation did not widen the door"
    # The live door must NOT have this name — that is the property under test.
    assert not hasattr(seam, leaked)


# ── 3. THE VACUITY GUARD — proving the ratchet really is blind to it ────────


@pytest.mark.parametrize("old,new,leaked", WIDENINGS)
def test_the_ratchet_cannot_see_the_widening(old, new, leaked):
    """The claim in this module's docstring — that no existing instrument catches a
    widened door — is asserted by MEASUREMENT, not by argument.

    Without this, test 2 would be a control against a defect something else already
    catches, and the whole suite would be a `donated residual`: real-looking, and
    redundant. The walker's crossing set is compared before and after the mutation is
    on disk; if the ratchet could see this, the two would differ.
    """
    before = set(live_crossings())
    with _MutantOnDisk(SEAM_SOURCE, old, new):
        during = set(live_crossings())
    assert during == before, (
        "the ratchet DOES move on a widened seam — this control is redundant with it "
        "and the docstring's claim is wrong"
    )
    assert before, "vacuity: the walker returned no crossings at all"


# ── 4. No SIM module names the supplier's collection register ───────────────


def _sim_edges_into(target: str) -> list[tuple[str, str]]:
    return sorted(
        (src, dst) for (src, dst) in live_crossings()
        if dst == target and src.split(".")[0] in {"sim", "simulation"}
    )


def test_no_sim_module_names_the_companys_collection_register():
    """Asked of the WALKER, never of the text — the docstrings explaining this cut
    contain the module's own name, so a substring scan would fail on its own subject.
    """
    assert _sim_edges_into("company.billing.direct_debit") == [], (
        "a SIM module imports the supplier's DD register module directly; B4's last "
        "edge has been re-crossed"
    )


def test_mutation_reinjecting_the_import_is_caught():
    """PERFORM the re-crossing on the real world-side file. The mutation is the exact
    import line the cut deleted."""
    with _MutantOnDisk(
        WORLD_SOURCE,
        "from company.interfaces.dd_collection_instructions import open_collections_desk",
        "from company.billing.direct_debit import DirectDebitBook  # noqa: F401\n"
        "from company.interfaces.dd_collection_instructions import open_collections_desk",
    ):
        assert _sim_edges_into("company.billing.direct_debit") == [
            ("simulation.dd_collection_book", "company.billing.direct_debit")
        ], "the re-injected crossing was not seen — the control cannot fail"
    assert _sim_edges_into("company.billing.direct_debit") == []
