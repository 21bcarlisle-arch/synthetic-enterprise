"""R15 control for the CREDIT-REFUND seam (KNIFE pass 3, B4).

WHAT THIS SUITE IS FOR — the properties NO other instrument in the tree can see
-------------------------------------------------------------------------------
`B4_billing_mechanics_reached_directly` stopped `simulation/credit_refund_events.py`
opening the company's refund compliance book (GSoP reg 6D; "SLC 14" until 2026-10-25,
the wrong locus). The world now reports a final bill's issue date and its credit to
`company/interfaces/credit_refund_requests.py`, and logs what comes back. Three
properties that cut rests on are invisible to everything already watching, and each
is mutation-proven below by PERFORMING the defect rather than asserting it impossible.

  1. THE DOOR COULD BE WIDENED WITHOUT MOVING A SINGLE WALL EDGE. Re-exporting
     `RefundTrigger`, or handing back the `CreditRefundRecord` "for convenience",
     would give the world the compliance taxonomy and the record type again — and
     the epistemic ratchet would stay GREEN, because the SIM's import still
     terminates on the exempt seam package. Tests 1 and 2 are what is not blind.

  2. THE TAXONOMY COULD DRIFT BACK ACROSS THE WALL THROUGH AN ARGUMENT. A
     `trigger=` parameter would look like a harmless convenience and would leave the
     classification — which of the four refund triggers this is — in the world's hands,
     making the door a spelling change rather than a cut. Test 3 pins the signature.

  3. THE BREACH VERDICT COULD GO PERMANENTLY FALSE, SILENTLY. Since 2026-10-25 the
     company sets the day it pays, on the reg 6D deadline, so the published log holds no
     late refund. A verdict hard-wired to "not breached" would read identically. Test 4
     forces the verdict and its compensation both ways on the book; test 5 makes the
     company's schedule late and proves the world's log carries every breach with its
     guaranteed-standard payment.
"""

from __future__ import annotations

import datetime as dt
import importlib
import importlib.util
import inspect
import os
import sys
from pathlib import Path

import pytest

import company.interfaces.credit_refund_requests as seam
from company.compliance.working_days import add_working_days
from company.interfaces.credit_refund_requests import refund_on_account_closure
from simulation.credit_refund_events import generate_credit_refund_log

REPO_ROOT = Path(__file__).resolve().parents[3]
SEAM_SOURCE = REPO_ROOT / "company" / "interfaces" / "credit_refund_requests.py"

# The company machinery a caller must not be able to reach through the door.
FORBIDDEN_AT_THE_DOOR = (
    "CreditRefundBook",
    "CreditRefundRecord",
    "RefundTrigger",
    "RefundStatus",
    "_REFUND_DEADLINE_WORKING_DAYS",
    "_working_days_between",
    "credit_refund",
)


class _Mutant:
    """Perform a defect on the REAL source file, load THAT file as a throwaway module,
    then restore byte-for-byte and verify the restoration. Loaded under a fresh name
    rather than by `importlib.reload`, which updates a namespace in place and never
    removes names — a re-export mutation would survive its own restoration."""

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


def _add_working_days(start: dt.date, n: int) -> dt.date:
    # The company's own calendar (bank holidays out), so a paid date n working days on reads
    # back as n. A weekend-only copy lived here until 2026-10-03 and disagreed with the door
    # once the door stopped counting Good Friday 2021 as a working day.
    return add_working_days(start, n)


# ── 1-2. The door exposes the outcome and nothing else ──────────────────────


def test_the_door_exposes_only_the_refund_request():
    assert seam.__all__ == ["refund_on_account_closure"]
    reachable = [n for n in FORBIDDEN_AT_THE_DOOR if hasattr(seam, n)]
    assert reachable == [], (
        "the credit-refund door hands the world back the company's own compliance "
        "machinery: " + ", ".join(reachable) + ". The epistemic ratchet cannot see "
        "this — the SIM's import still terminates on the exempt seam package — so the "
        "widening would be silent."
    )


@pytest.mark.parametrize("leaked", ["RefundTrigger", "CreditRefundBook"])
def test_mutation_a_widened_door_is_caught(leaked):
    """PERFORM the widening on the real file: hoist the in-function import to module
    level, which is all it takes to put the taxonomy back in the world's reach."""
    with _Mutant(
        SEAM_SOURCE,
        '__all__ = ["refund_on_account_closure"]',
        f'from company.billing.credit_refund import {leaked}\n\n'
        '__all__ = ["refund_on_account_closure"]',
        f"_mutant_refund_{leaked}",
    ) as mutant:
        assert hasattr(mutant, leaked), "vacuity: the mutation did not widen the door"
        assert not hasattr(seam, leaked)


# ── 3. The trigger is classified company-side, not passed in ────────────────


def test_the_door_does_not_accept_a_trigger_argument():
    """A `trigger=` convenience would leave the four-way refund classification in the
    world's hands and make this door a spelling change rather than a cut. A `paid_date=`
    would hand the world the supplier's payment speed again, the draw that made 10 of
    100 refunds late at b2bc3d8da5."""
    params = set(inspect.signature(refund_on_account_closure).parameters)
    assert params == {"account_id", "final_bill_issued", "credit_amount_gbp"}, (
        f"the door's signature changed: {sorted(params)}. Anything naming a trigger, a "
        "deadline, a status, a payment date or a record type moves a company decision back "
        "across the wall."
    )
    out = refund_on_account_closure("C1", dt.date(2021, 3, 1), 42.0)
    assert out["trigger"] == "account_closure"
    assert set(out) == {
        "trigger", "request_date", "credit_amount_gbp", "paid_date",
        "working_days_to_pay", "breached_reg_6d_deadline", "reg_6d_payment_owed",
    }
    assert all(isinstance(v, (str, float, int, bool)) for v in out.values()), (
        "the door returned a live object, not plain JSON-serialisable facts"
    )


# ── 4. The deadline is the company's, and it fires both ways ────────────────


def _paid_after(issued: dt.date, working_days: int):
    from company.billing.credit_refund import CreditRefundBook, CreditRefundRecord, RefundTrigger

    book = CreditRefundBook()
    book.raise_refund(CreditRefundRecord("C1", issued, RefundTrigger.ACCOUNT_CLOSURE, 42.0))
    return book.pay("C1", _add_working_days(issued, working_days))


@pytest.mark.parametrize("issued,working_days,expect_breach,expect_gbp", [
    (dt.date(2021, 3, 1), 1, False, 0.0),
    (dt.date(2021, 3, 1), 10, False, 0.0),
    (dt.date(2021, 3, 1), 11, True, 30.0),
    (dt.date(2024, 12, 2), 25, True, 30.0),   # failed 17 Dec 2024: before the uplift
    (dt.date(2025, 1, 10), 11, True, 40.0),   # failed after 2 Jan 2025: £40
    (dt.date(2018, 6, 1), 25, False, 0.0),    # reg 6D not yet in force (1 May 2019)
])
def test_a_late_refund_can_occur_and_is_then_compensated(issued, working_days, expect_breach, expect_gbp):
    """VACUITY GUARD BY CONSTRUCTION: a book hard-wired to "on time" passes every compliant
    case. The late arm is asserted reachable, and each late one carries the payment in force
    the day it failed, from SI 2019/218 and Ofgem's 2025 uplift (home_moves.md s.8.8)."""
    record = _paid_after(issued, working_days)
    assert record.working_days_to_pay() == working_days
    assert record.breached_deadline() is expect_breach
    assert record.reg_6d_payment() == expect_gbp


def test_the_company_pays_every_refund_on_or_before_its_deadline():
    """Across 2016-2025, every final-bill day of the year: the scheduled day is never late on
    the company's own calendar, bank holidays included (Christmas, Easter)."""
    from company.billing.credit_refund import refund_due_date, scheduled_refund_date

    day, worst = dt.date(2016, 1, 1), 0
    while day <= dt.date(2025, 12, 31):
        paid = scheduled_refund_date(day)
        out = refund_on_account_closure("C1", day, 5.0)
        assert paid <= refund_due_date(day)
        assert out["breached_reg_6d_deadline"] is False and out["reg_6d_payment_owed"] == 0.0
        worst = max(worst, out["working_days_to_pay"])
        day += dt.timedelta(days=1)
    assert worst == 10


# ── 5. The world's published log really follows the company's schedule ─────


def _refund_population():
    """Closures in credit across the uplift and reg 6D's commencement. The third item is the
    run's closing balances: each closes in credit on the ledger."""
    bills, closing = [], {}
    for i in range(120):
        cid = f"CUST{i:04d}"
        closing[cid] = -round(5.0 + i % 17, 2)
        year, month = 2017 + i // 15, i % 12 + 1
        last = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]
        bills.append({
            "customer_id": cid,
            "period_end": f"{year:04d}-{month:02d}-{last:02d}",
            "total_amount_gbp": 120.0,
            "segment": "resi",
            "commodity": "electricity",
        })
    return bills, {b["customer_id"]: "resi" for b in bills}, closing


def test_mutation_a_late_schedule_reaches_the_published_log_with_its_compensation(monkeypatch):
    """FAIL-SILENT proof. Make the company pay one working day after the deadline: the world's
    published log must show the breaches, each with its payment, and none before 1 May 2019.
    If the log were unchanged, the world would not be reading the company's schedule."""
    import company.billing.credit_refund as book

    bills, segments, closing = _refund_population()
    baseline = generate_credit_refund_log(bills, segments, closing)
    assert baseline and not any(r["breached_reg_6d_deadline"] for r in baseline)

    monkeypatch.setattr(book, "scheduled_refund_date",
                        lambda issued: _add_working_days(book.refund_due_date(issued), 1))
    mutated = generate_credit_refund_log(bills, segments, closing)
    late = [r for r in mutated if r["breached_reg_6d_deadline"]]
    pre = [r for r in mutated if r["request_date"] < "2019-04-17"]
    assert late and pre and not any(r["breached_reg_6d_deadline"] for r in pre)
    assert {r["reg_6d_payment_owed"] for r in late} == {30.0, 40.0}
    assert all(r["reg_6d_payment_owed"] == 0.0 for r in mutated if not r["breached_reg_6d_deadline"])
