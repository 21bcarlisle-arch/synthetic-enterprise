"""R15 control for the DD-payment-day MOVE (KNIFE pass 3, B4).

WHAT THIS SUITE IS FOR — the property NO other instrument in the tree can see
-----------------------------------------------------------------------------
`staggered_payment_day` moved from `company/billing/direct_debit.py` to
`simulation/dd_payment_day.py`: the customer PICKS their collection day, so it is a
fact about the customer, and the supplier learns it when the mandate is set up.

The move leaves the 1–28 Bacs range stated on BOTH sides — the world assigns within
it, the company validates against it — and that duplication is the one thing this cut
could get wrong. Two ways to get it wrong, and only one of them is available:

  * PINNING THE TWO CONSTANTS EQUAL would restore in the suite exactly the coupling
    the cut removed from the code. It is the trap `B3_world_needs_its_own_cap_physics`
    already recorded for the price cap, and it is deliberately NOT what this suite
    does. Neither side may be made to import the other's number to satisfy a test.
  * LEAVING IT UNCONTROLLED would be `one name, two numbers`: two readings of the same
    convention drifting apart with nobody watching.

So the control pins the RELATIONSHIP instead: every day the world can emit is a day
the company's mandate register accepts. That is the property that actually matters,
it holds under any consistent pair of readings, and it fails loudly the moment either
side drifts. Test 3 proves it can fail, by drifting each side in turn on the real
source and watching mandate setup raise.

The move itself needs no test here: `tests/architecture/test_epistemic_wall_ratchet.py`
already fails on any company-side import of `simulation.*`, so a re-export from the
old home is caught by the gate, not by this file.
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys
from pathlib import Path

import pytest

from company.billing import direct_debit
from company.billing.direct_debit import DirectDebitBook
from simulation import dd_payment_day
from simulation.dd_payment_day import staggered_payment_day

REPO_ROOT = Path(__file__).resolve().parents[2]
WORLD_SOURCE = REPO_ROOT / "simulation" / "dd_payment_day.py"

# A wide, deterministic id sample -- the same shape the DD books draw on.
SAMPLE_IDS = [f"CUST{i:04d}" for i in range(500)]


def _set_up_mandate(book: DirectDebitBook, customer_id: str, payment_day: int):
    return book.create_mandate(
        customer_id=customer_id,
        sort_code="00-00-**",
        account_last4="0000",
        monthly_amount_gbp=80.0,
        setup_date="2021-01-01",
        payment_day=payment_day,
    )


# ── 1. The world holds a real customer attribute ────────────────────────────


def test_the_day_is_deterministic_and_draws_no_shared_randomness():
    """C-S2: a pure per-customer digest consumes no RNG, so adding this call can never
    shift another subsystem's stream."""
    first = [staggered_payment_day(cid) for cid in SAMPLE_IDS]
    second = [staggered_payment_day(cid) for cid in SAMPLE_IDS]
    assert first == second


def test_the_days_actually_stagger():
    """VACUITY GUARD for everything below: a function returning one constant day would
    satisfy every acceptance assertion in this file while modelling nothing."""
    assert len(set(staggered_payment_day(cid) for cid in SAMPLE_IDS)) > 20


# ── 2. The relationship: what the world assigns, the company accepts ────────


def test_every_day_the_world_assigns_is_accepted_by_the_company_mandate_register():
    """The control the duplication rests on. NOT `world.bounds == company.bounds` —
    that would re-couple the two readings in the suite."""
    book = DirectDebitBook()
    for cid in SAMPLE_IDS:
        mandate = _set_up_mandate(book, cid, staggered_payment_day(cid))
        assert mandate.payment_day == staggered_payment_day(cid)


# ── 3. …and drift on EITHER side is loud, not silent ────────────────────────


class _Mutant:
    """Perform a defect on the REAL source file, load THAT file as a throwaway module,
    restore byte-for-byte, and verify the restoration."""

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


def test_mutation_world_side_drift_is_rejected_at_the_mandate():
    """Widen the world's range past the Bacs cap and the company's register refuses the
    day. The divergence surfaces as a raised error at the seam — never as two books
    quietly disagreeing."""
    with _Mutant(WORLD_SOURCE, "_MAX_PAYMENT_DAY = 28", "_MAX_PAYMENT_DAY = 31",
                 "_mutant_payment_day_wide") as mutant:
        drifted = [cid for cid in SAMPLE_IDS if mutant.staggered_payment_day(cid) > 28]
        assert drifted, "vacuity: widening the range produced no out-of-range day"
        book = DirectDebitBook()
        with pytest.raises(ValueError):
            _set_up_mandate(book, drifted[0], mutant.staggered_payment_day(drifted[0]))


def test_mutation_company_side_drift_is_rejected_at_the_mandate(monkeypatch):
    """The symmetric half: narrow the COMPANY's accepted range and days the world
    legitimately assigns start being refused. Without this, the control would only
    watch one of the two readings."""
    book = DirectDebitBook()
    # VACUITY GUARD: on the real bounds these same ids are all accepted.
    for cid in SAMPLE_IDS[:50]:
        _set_up_mandate(book, cid, staggered_payment_day(cid))

    monkeypatch.setattr(direct_debit, "_MAX_PAYMENT_DAY", 15)
    refused = 0
    for cid in SAMPLE_IDS[:50]:
        if staggered_payment_day(cid) > 15:
            with pytest.raises(ValueError):
                _set_up_mandate(DirectDebitBook(), cid, staggered_payment_day(cid))
            refused += 1
    assert refused, "vacuity: no id in the sample exceeded the narrowed company bound"


def test_the_two_readings_are_not_wired_to_each_other():
    """The cut's own wall: neither side may satisfy the relationship by importing the
    other's number, which would re-couple in code what the relationship control
    deliberately does not couple in the suite.

    Measured with the SHARED crossing definition (`tools/epistemic_wall.py`) rather
    than a private grep — that module is the one place this repo defines what an
    import crossing IS, and a second, hand-rolled reader here would be the very defect
    this pass's first step existed to remove.
    """
    from tools.epistemic_wall import REPO_ROOT as WALL_ROOT
    from tools.epistemic_wall import WALL_DIRS, build_edges

    edges = build_edges(WALL_ROOT, WALL_DIRS)
    wired = [
        (e.src, e.dst, e.lineno) for e in edges
        if (e.src == "simulation.dd_payment_day" and e.dst.split(".")[0] in ("company", "saas"))
        or (e.src == "company.billing.direct_debit" and e.dst.split(".")[0] in ("simulation", "sim"))
    ]
    assert wired == [], (
        "the two readings of the 1-28 Bacs range are wired to each other: "
        f"{wired}. The world assigning a day and the company validating one are meant "
        "to be independent readings of a published convention."
    )
    # VACUITY GUARD: the walker really did see this module.
    assert any(e.src == "simulation.dd_payment_day" or e.dst == "simulation.dd_payment_day"
               for e in edges), "the walker never visited simulation/dd_payment_day.py"
