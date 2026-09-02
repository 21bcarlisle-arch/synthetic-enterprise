"""R15 control for the DD-REVIEW-OUTCOME seam (KNIFE pass 3, B4).

WHAT THIS SUITE IS FOR — the properties NO other instrument in the tree can see
-------------------------------------------------------------------------------
`B4_billing_mechanics_reached_directly` replaced `simulation/dd_balance_book.py`'s
import of the company's PRIVATE `dd_review._recommended_monthly` with a question
asked at `company/interfaces/dd_review_outcome.py`. Two properties that cut rests on
are invisible to everything already watching, and each is mutation-proven below by
PERFORMING the defect rather than asserting it impossible.

  1. THE DOOR COULD BE WIDENED WITHOUT MOVING A SINGLE WALL EDGE. Re-exporting
     `_recommended_monthly`, or handing back a whole `DDReviewResult`, would give the
     world the review ROUTINE again — the very thing the cut removed — and the
     epistemic ratchet would stay GREEN, because the SIM's import still terminates on
     the exempt seam package. The ratchet is blind to this by construction; tests 1
     and 2 are what is not.

  2. THE PUBLISHED NUMBER COULD DRIFT FROM THE ONE ON THE CUSTOMER'S LETTER, SILENTLY.
     The amount this door returns sizes every level-DD collection, which sizes the
     portfolio held-credit liability the annual report publishes and the closing
     credit balance SLC 14 refunds are raised on. A door that returned a plausible
     but different number — unrounded, or a stub — would move a published financial
     figure while every test that does not compute a balance stayed green. That is
     FAIL-SILENT. Test 3 pins the door to the company's own review OUTCOME; test 4
     proves the number is load-bearing by mutating it and watching the liability move.

THE LINEAGE LIMIT, STATED RATHER THAN GLOSSED (R15, "agreeing sources share lineage")
-------------------------------------------------------------------------------------
Test 3's oracle is `dd_review.review(...)`, the company's PUBLIC review API, whose
`recommended_monthly_gbp` field is what a customer is actually told. That is not a
fully independent computation — both it and the door reach the same private helper —
and pretending otherwise would be the tautology R15 names. The property it CAN prove
is the one that matters here: the door publishes the same number the company's own
review result carries, so the door cannot drift away from the letter. If the company
later changes its review routine, both move together — and that is correct, not a
defect: the world is meant to follow what the supplier decides. A test pinning the
door to a hard-coded arithmetic rule would instead freeze the company's policy from
the world's side, restoring in the suite exactly the coupling the cut removed.
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys
from datetime import date
from pathlib import Path

import pytest

import company.interfaces.dd_review_outcome as seam
from company.billing import dd_review
from company.interfaces.dd_review_outcome import reviewed_monthly_amount
from simulation.dd_balance_book import build_dd_balance_book

REPO_ROOT = Path(__file__).resolve().parents[3]
SEAM_SOURCE = REPO_ROOT / "company" / "interfaces" / "dd_review_outcome.py"

# The company machinery a caller must not be able to reach through the door.
FORBIDDEN_AT_THE_DOOR = (
    "_recommended_monthly",
    "review",
    "DDReviewResult",
    "DDReviewBook",
    "DDAction",
    "_VARIANCE_THRESHOLD_PCT",
    "dd_review",
)


class _Mutant:
    """Perform a defect on the REAL source file, load THAT file as a throwaway
    module, then restore byte-for-byte and verify the restoration.

    Loaded under a fresh name rather than by `importlib.reload`: reload updates a
    namespace in place and never removes names, so a re-export mutation would survive
    its own restoration and leak into every later test in this file.
    """

    def __init__(self, path: Path, old: str, new: str, name: str):
        self.path, self.name = path, name
        self.original = path.read_text()
        assert old in self.original, "mutation target absent — the mutation is vacuous"
        self.mutated_text = self.original.replace(old, new, 1)
        assert self.mutated_text != self.original

    def __enter__(self):
        # Bytecode caching OFF for the duration, and the cached .pyc dropped after.
        # THIS IS NOT BELT-AND-BRACES -- it is the defect this harness hit on its first
        # run and the reason the guard is here. A mutation that changes no BYTES of
        # length (28 -> 31) leaves the restored file with the same size, and often the
        # same mtime second, so CPython considers the MUTANT's cached .pyc still valid
        # and every later import in the session silently gets the mutated module back.
        # A mutation harness that poisons the suite it protects is worse than none.
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


def _three_year_bills(cid="CUST0000", monthly=100.0, step=1.5):
    """36 monthly bills for one direct-debit customer, with a sustained step change
    in year 2 so the year-on-year review chain actually re-sizes the standing DD."""
    out = []
    for m in range(36):
        year, month = 2020 + m // 12, m % 12 + 1
        last = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]
        out.append({
            "customer_id": cid,
            "period_end": f"{year:04d}-{month:02d}-{last:02d}",
            "total_amount_gbp": round(monthly * (step if m >= 12 else 1.0), 2),
            "segment": "resi",
            "commodity": "electricity",
        })
    return out


def _dd_customer_bills():
    """A bill set whose customer really lands in the DD population — the balance book
    gates on `payment_method(...) == 'direct_debit'`, so an arbitrary id may be
    excluded and the whole suite would then measure nothing."""
    for i in range(200):
        bills = _three_year_bills(cid=f"CUST{i:04d}")
        opening = {bills[0]["customer_id"]: float(bills[0]["total_amount_gbp"])}
        if build_dd_balance_book(bills, opening).trajectories:
            return bills
    raise AssertionError("vacuity: no direct-debit customer found in 200 candidates")


# ── 1-2. The door exposes the amount and nothing else ───────────────────────


#: The doors this seam is SANCTIONED to publish -- both of them amounts a real
#: customer is told (the opening figure at sign-up, the reviewed figure after
#: each annual review), neither of them the routine that chose it. Kept a CLOSED
#: list so an accidental widening still trips; `opening_monthly_amount` joined it
#: on 2026-09-02 with atom `D_opening_dd_seasonal_sizing`, which gave the opening
#: DD an estimate to be set from. The load-bearing leg of this control is the
#: FORBIDDEN_AT_THE_DOOR reachability check below, not this list.
SANCTIONED_DOORS = ["opening_monthly_amount", "reviewed_monthly_amount"]


def test_the_door_exposes_only_the_reviewed_amount():
    assert sorted(seam.__all__) == SANCTIONED_DOORS
    reachable = [n for n in FORBIDDEN_AT_THE_DOOR if hasattr(seam, n)]
    assert reachable == [], (
        "the DD-review door hands the world back the company's own review machinery: "
        + ", ".join(reachable)
        + ". The epistemic ratchet cannot see this — the SIM's import still terminates "
        "on the exempt seam package — so the widening would be silent."
    )


@pytest.mark.parametrize("old,new,leaked", [
    # (a) The defect this control ACTUALLY CAUGHT on its first run: the door was
    # written with a module-level import, which put the private routine in the seam's
    # own namespace. This mutation restores that exact mistake.
    (
        '__all__ = ["opening_monthly_amount", "reviewed_monthly_amount"]',
        'from company.billing.dd_review import _recommended_monthly\n\n__all__ = ["opening_monthly_amount", "reviewed_monthly_amount"]',
        "_recommended_monthly",
    ),
    # (b) The convenience widening: hand back the whole review API.
    (
        '__all__ = ["opening_monthly_amount", "reviewed_monthly_amount"]',
        'from company.billing.dd_review import review\n\n__all__ = ["reviewed_monthly_amount", "review"]',
        "review",
    ),
])
def test_mutation_a_widened_door_is_caught(old, new, leaked):
    """PERFORM the widening on the real file. Each mutation restores machinery the cut
    removed, and each leaves the epistemic ratchet GREEN — which is the whole reason
    this control exists."""
    with _Mutant(SEAM_SOURCE, old, new, f"_mutant_ddreview_{leaked}") as mutant:
        assert hasattr(mutant, leaked), "vacuity: the mutation did not actually widen the door"
        # The live door must NOT have this name — that is the property under test.
        assert not hasattr(seam, leaked)


# ── 3. The door publishes the number on the customer's letter ───────────────


@pytest.mark.parametrize("annual", [0.0, 1.0, 1200.0, 2300.0, 2399.99, 18_000.0])
def test_the_door_returns_the_amount_the_company_review_records(annual):
    """The oracle is the company's PUBLIC review result — the number the customer is
    told. See the module docstring on why this shared lineage is the honest limit
    rather than a hidden tautology."""
    outcome = dd_review.review(
        customer_id="C_SEAM",
        review_date=date(2021, 1, 1),
        current_dd_gbp=100.0,
        actual_annual_spend_gbp=annual,
    )
    assert reviewed_monthly_amount(annual) == outcome.recommended_monthly_gbp


# ── 4. The number is load-bearing on a published figure ─────────────────────


def test_mutation_a_drifting_door_moves_the_published_held_credit_liability():
    """FAIL-SILENT proof. Change what the door returns and the portfolio held-credit
    liability moves — so a door that quietly returned a stub or an unrounded value
    would corrupt a published financial figure with no test failing on its own terms.
    The vacuity guard first asserts the un-mutated book actually re-sizes the standing
    DD across years; a single-year population would pass against any door at all."""
    bills = _dd_customer_bills()
    # An explicit opening amount: since 2026-09-02 the book refuses to open a
    # customer from their first issued bill, so a population with no opening
    # carries no trajectory at all and this control would measure nothing.
    opening = {bills[0]["customer_id"]: float(bills[0]["total_amount_gbp"])}
    book = build_dd_balance_book(bills, opening)
    standing = {p.collected_gbp for pts in book.trajectories.values() for p in pts}
    assert len(standing) > 1, (
        "vacuity: the standing DD never changed, so this population never asks the door"
    )
    baseline = book.serialise()

    with _Mutant(
        SEAM_SOURCE,
        "    return _recommended_monthly(actual_annual_spend_gbp)",
        "    return _recommended_monthly(actual_annual_spend_gbp) + 1.0",
        "_mutant_ddreview_drift",
    ) as mutant:
        import simulation.dd_balance_book as bb
        original = bb.reviewed_monthly_amount
        try:
            bb.reviewed_monthly_amount = mutant.reviewed_monthly_amount
            drifted = build_dd_balance_book(bills, opening).serialise()
        finally:
            bb.reviewed_monthly_amount = original

    assert drifted != baseline, (
        "the held-credit liability did not move when the reviewed amount changed — "
        "either the door is not load-bearing (so the cut moved nothing) or the book "
        "is not really asking it"
    )
    assert (
        build_dd_balance_book(bills, opening).serialise() == baseline
    ), "restoration failed"
