"""KNIFE3 step 28 — the control on `B10_household_identity_is_the_worlds`.

WHY THIS FILE EXISTS, AND WHY THE RATCHET IS NOT ENOUGH (R15)
--------------------------------------------------------------
The cut in register §3w removes two edges to `saas.customer_reaction`, both
carrying one private name: `_billing_account_id`. The world used it to decide
WHICH SUPPLY POINTS CHURN TOGETHER (`simulation.run_phase2b`) and which share a
lifecycle roll and its RNG seed (`simulation.customer_events`). Deleting the two
ratchet tuples proves the import is gone, and that is all it proves. Three
things it cannot see:

  1. **Behaviour.** The answers must not move: `churned_billing_accounts` is a
     published key of the run record and `f"{billing_account}_{term_start}"` is
     an RNG seed, so a single changed answer re-rolls a customer's whole life.
     The pre-cut answers over the WHOLE published book are pinned below as
     literals, transcribed from a run against `saas.customer_reaction.
     _billing_account_id` BEFORE either call site was switched.

  2. **That the world is actually asking itself.** A revert to the company
     import would leave every pinned value green — the two functions agree
     today, which is exactly why this cut is safe and exactly why a value test
     cannot police it. `test_no_sim_side_importer_of_the_suppliers_mapper`
     names the import, not the number.

  3. **That the two are FREE TO DISAGREE.** This is the point of the cut and
     the one thing a test pinning them equal would destroy (B3's and B7's
     recorded refusal — see register §3g). There is no assertion anywhere in
     this file that `household_of(x) == _billing_account_id(x)`. The proof runs
     the other way: `test_the_worlds_answer_does_not_route_through_the_supplier`
     replaces the supplier's mapper at runtime and the world's answer is
     unchanged.

WHY THE CUT, IN ONE PARAGRAPH
------------------------------
Whether `C1` and `C1g` are one household is a fact about a physical property.
Whether they are one BILLING ACCOUNT is a supplier decision, and a real supplier
gets it wrong routinely — a dual-fuel customer billed as two unlinked accounts
is an ordinary complaint, not an exotic failure. While the world took the
supplier's grouping as its ground truth, that mistake was structurally
impossible to make and therefore impossible for the COUPLED TRIAD to score.

THE THREE KILLER PATTERNS, ANSWERED
------------------------------------
TAUTOLOGY   — the expected ids are literals transcribed from the PRE-CUT
              function. Nothing in this file derives them from `household_of`,
              and nothing compares the two implementations to each other.
FAIL-OPEN   — the book pin asserts the roster it walks is non-empty AND that it
              still contains a gas leg (a book with no dual-fuel point makes
              every grouping assertion vacuously true, which is the shape that
              would survive a silent roster change).
FAIL-SILENT — `household_of` and the two call-site modules are checked by AST
              against the real files; a missing file or an unparsable module is
              a failure here, never a skip.

MUTATION EVIDENCE (performed 2026-08-14, both directions, each against the
module SOURCE and restored from a copy; 35 pass on the unmutated tree, so every
count below is a real kill)
  - `household_of` stops stripping the suffix (`return supply_point_id`)
                                                  -> 7 failed, 28 passed.
  - `GAS_LEG_ID_SUFFIX` "g" -> "G"                 -> 8 failed, 27 passed —
    one more than the above, because the vacuity guard is keyed on the same
    constant and correctly reports it can no longer find a gas leg.
  - the `len(...) > 1` guard removed               -> 1 failed, 34 passed —
    the bare `"g"` case, the only input that distinguishes them, and the
    reason it is pinned rather than dismissed as unreachable.
  - `from saas.customer_reaction import _billing_account_id` re-added to
    `simulation/customer_events.py`                -> 1 failed, 34 passed:
    `test_no_sim_side_importer_of_the_suppliers_mapper` and nothing else. THE
    MUTATION THAT MATTERS MOST — every value in this file still agrees, so
    every other test passes while the defect is fully restored.
  - `saas.customer_reaction._billing_account_id` mutated at SOURCE to the
    identity function (the supplier stops linking dual fuel) -> 0 failed, here
    and across `tests/simulation/test_customer_events.py` and
    `tests/simulation/test_home_move_undeliverable_win.py` (65 passed). The
    supplier's own answer really did change under the mutation — the name
    `simulation/customer_events.py` imported at HEAD returned `"C1g"` for
    `"C1g"` — so on the pre-cut tree the world's grouping, its event
    `customer_id` and its lifecycle RNG seed all moved with it.
"""

import ast
from pathlib import Path

import pytest

from simulation.household import GAS_LEG_ID_SUFFIX, household_of

REPO_ROOT = Path(__file__).resolve().parents[2]
HOUSEHOLD_PATH = REPO_ROOT / "simulation" / "household.py"

# The two call sites this step switched, and the private company-side name they
# used to import. Both are named as PATHS so a module rename reds this control
# rather than silently exempting the file.
SWITCHED_CALL_SITES = (
    REPO_ROOT / "simulation" / "run_phase2b.py",
    REPO_ROOT / "simulation" / "customer_events.py",
)
SUPPLIERS_MAPPER_MODULE = "saas.customer_reaction"

# ---------------------------------------------------------------------------
# The pin. Transcribed from a run of `saas.customer_reaction._billing_account_id`
# over the live published book BEFORE either call site was switched, plus the
# four edge cases `tests/saas/test_customer_reaction.py` already pinned on the
# supplier's side. Literals on purpose: rewriting `household_of` cannot move
# them, and neither can rewriting the supplier's mapper.
# ---------------------------------------------------------------------------
PRE_CUT_HOUSEHOLD_OF = {
    # electricity points, resi — their own household
    "C1": "C1", "C2": "C2", "C3": "C3", "C4": "C4", "C5": "C5",
    "C6": "C6", "C7": "C7", "C8": "C8", "C9": "C9",
    # I&C sites
    "C_IC1": "C_IC1", "C_IC2": "C_IC2", "C_IC3": "C_IC3", "C_IC4": "C_IC4",
    # gas legs — the SAME household as their electricity point
    "C1g": "C1", "C2g": "C2", "C3g": "C3", "C4g": "C4", "C_IC3g": "C_IC3",
    # successor registrations after a home-move win — a new household at the
    # same property, and deliberately NOT folded into the predecessor
    "C1_2": "C1_2", "C2_2": "C2_2", "C3_2": "C3_2",
    "C4_2": "C4_2", "C5_2": "C5_2", "C6_2": "C6_2",
    # drawn points (SE_DRAW_POPULATION=1) — no gas leg, own household
    "SYN-2021-001": "SYN-2021-001", "SYN-2025-001": "SYN-2025-001",
    # the edge cases: a bare suffix is a point id, not a leg of something
    "g": "g",
    "": "",
}


@pytest.mark.parametrize("point_id", sorted(PRE_CUT_HOUSEHOLD_OF))
def test_household_of_matches_the_pre_cut_answer(point_id):
    assert household_of(point_id) == PRE_CUT_HOUSEHOLD_OF[point_id], (
        f"the cut changed which household {point_id!r} belongs to — "
        "churn grouping and the lifecycle RNG seed both move with this"
    )


def test_the_pin_covers_the_whole_published_book():
    """FAIL-OPEN guard: a book with no dual-fuel point proves nothing.

    Every grouping assertion above is vacuously true over an all-electricity
    roster, so the population the pin claims to cover is asserted rather than
    assumed.
    """
    from company.interfaces.supply_book import (
        registered_supply_points,
        successor_supply_points,
    )

    book = [c["customer_id"] for c in registered_supply_points()]
    book += [c["customer_id"] for c in successor_supply_points()]

    assert len(book) > 10, f"walked only {len(book)} supply points — sweep broken"
    gas_legs = [i for i in book if i.endswith(GAS_LEG_ID_SUFFIX) and len(i) > 1]
    assert gas_legs, "the book carries no gas leg — the grouping pin is vacuous"

    unpinned = sorted(set(book) - set(PRE_CUT_HOUSEHOLD_OF))
    assert unpinned == [], (
        f"the book grew supply points this pin has never seen: {unpinned}"
    )


def test_a_gas_leg_and_its_electricity_point_are_one_household():
    """The property the whole cut is about, stated once as a property."""
    for elec, gas in (("C1", "C1g"), ("C4", "C4g"), ("C_IC3", "C_IC3g")):
        assert household_of(gas) == household_of(elec) == elec


def test_two_different_households_are_never_merged():
    """The counter-direction a suffix-stripper could get wrong.

    A successor registration (`C1_2`) shares a PROPERTY with `C1` but is a
    different household — the previous occupants left. Folding it back would
    make a home-move win look like a customer who never churned.
    """
    assert household_of("C1_2") != household_of("C1")
    assert household_of("C2") != household_of("C1")


# ---------------------------------------------------------------------------
# The direction the cut exists to protect
# ---------------------------------------------------------------------------


def _imported_module_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module)
    return names


def _sim_side_files() -> list[Path]:
    found: list[Path] = []
    for d in ("sim", "simulation"):
        root = REPO_ROOT / d
        if not root.is_dir():
            continue
        found.extend(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)
    return found


def test_no_sim_side_importer_of_the_suppliers_mapper():
    """THE control. Values cannot police this, because the values agree."""
    files = _sim_side_files()
    # FAIL-OPEN guard: an empty sweep is a broken sweep, never a pass.
    assert len(files) > 50, (
        f"scanned only {len(files)} sim-side files — the sweep is broken, "
        "and a broken sweep passes this test for free"
    )

    offenders = sorted(
        str(p.relative_to(REPO_ROOT))
        for p in files
        if SUPPLIERS_MAPPER_MODULE in _imported_module_names(p)
    )
    assert offenders == [], (
        "the world is taking the supplier's billing-account grouping as its "
        "ground truth about who lives where, which makes a mis-linked dual-fuel "
        f"account structurally impossible and unscoreable: {offenders}"
    )


def test_the_two_switched_call_sites_still_ask_the_world():
    """A silent revert would leave every value green. This names the import."""
    for path in SWITCHED_CALL_SITES:
        assert path.is_file(), f"{path} is gone — re-point this control"
        imported = _imported_module_names(path)
        assert "simulation.household" in imported, (
            f"{path.name} no longer imports the world's household identity"
        )
        assert "household_of" in path.read_text(encoding="utf-8"), (
            f"{path.name} imports the module but no longer calls household_of"
        )


def test_the_worlds_household_module_reads_no_company_module():
    """The other direction: this must never grow a sim -> company edge.

    The second half of the B1 safety measurement, kept live rather than left in
    a commit message.
    """
    company_side = sorted(
        m for m in _imported_module_names(HOUSEHOLD_PATH)
        if m.split(".")[0] in {"company", "saas"}
    )
    assert company_side == [], (
        f"simulation/household.py grew a company-side import: {company_side}"
    )


def test_the_worlds_answer_does_not_route_through_the_supplier(monkeypatch):
    """Free to disagree — proven by making them disagree, not by pinning equal.

    The supplier stops linking dual fuel (an ordinary real-world billing
    failure). The world's answer must not notice.
    """
    import saas.customer_reaction as cr

    monkeypatch.setattr(cr, "_billing_account_id", lambda cid: cid)
    assert cr._billing_account_id("C1g") == "C1g"  # the mutation is live

    assert household_of("C1g") == "C1", (
        "the world's household identity moved when the supplier changed its "
        "billing arrangements — the cut did not take"
    )
