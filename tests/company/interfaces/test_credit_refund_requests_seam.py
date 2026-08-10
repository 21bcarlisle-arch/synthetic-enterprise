"""R15 control for the CREDIT-REFUND seam (KNIFE pass 3, B4).

WHAT THIS SUITE IS FOR — the properties NO other instrument in the tree can see
-------------------------------------------------------------------------------
`B4_billing_mechanics_reached_directly` stopped `simulation/credit_refund_events.py`
opening the company's SLC 14 compliance book. The world now reports a closure, a
credit balance and the date the money arrived to
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
     classification — which of SLC 14's four triggers this is — in the world's hands,
     making the door a spelling change rather than a cut. Test 3 pins the signature.

  3. THE BREACH VERDICT COULD GO PERMANENTLY FALSE, SILENTLY. `breached_slc14_deadline`
     is the only compliance output of this whole mechanic, and nothing else recomputes
     it. A door that always answered "not breached" would raise no error, break no
     schedule, move no cash figure, and quietly publish a zero SLC 14 breach count —
     FAIL-SILENT, and precisely the 2022 failure this mechanic exists to model. Tests
     4 and 5 force the verdict both ways and then mutate it to prove the world's log
     really follows it.
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
    cur, added = start, 0
    while added < n:
        cur += dt.timedelta(days=1)
        if cur.weekday() < 5:
            added += 1
    return cur


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
    """A `trigger=` convenience would leave SLC 14's four-way classification in the
    world's hands and make this door a spelling change rather than a cut."""
    params = set(inspect.signature(refund_on_account_closure).parameters)
    assert params == {"account_id", "closure_date", "credit_amount_gbp", "paid_date"}, (
        f"the door's signature changed: {sorted(params)}. Anything naming a trigger, a "
        "deadline, a status or a record type moves a company classification back across "
        "the wall."
    )
    out = refund_on_account_closure("C1", dt.date(2021, 3, 1), 42.0, dt.date(2021, 3, 5))
    assert out["trigger"] == "account_closure"
    assert set(out) == {
        "trigger", "request_date", "credit_amount_gbp", "paid_date",
        "working_days_to_pay", "breached_slc14_deadline",
    }
    assert all(isinstance(v, (str, float, int, bool)) for v in out.values()), (
        "the door returned a live object, not plain JSON-serialisable facts"
    )


# ── 4. The deadline is the company's, and it fires both ways ────────────────


@pytest.mark.parametrize("working_days,expect_breach", [(1, False), (10, False), (11, True), (25, True)])
def test_the_slc14_verdict_fires_both_ways(working_days, expect_breach):
    """VACUITY GUARD BY CONSTRUCTION: a control that only ever saw compliant refunds
    would pass against a door hard-wired to `False`. Both arms are asserted here."""
    closure = dt.date(2021, 3, 1)
    out = refund_on_account_closure(
        "C1", closure, 42.0, _add_working_days(closure, working_days)
    )
    assert out["working_days_to_pay"] == working_days
    assert out["breached_slc14_deadline"] is expect_breach


# ── 5. The world's published log really follows the company's verdict ───────


def _refund_population():
    """Enough churned DD closures that BOTH verdicts appear in the log — the on-time
    tail is ~10%, so a small sample lands on one arm only and would prove nothing."""
    bills, churned = [], set()
    for i in range(240):
        cid = f"CUST{i:04d}"
        churned.add(cid)
        for m in range(24):
            year, month = 2020 + m // 12, m % 12 + 1
            last = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]
            bills.append({
                "customer_id": cid,
                "period_end": f"{year:04d}-{month:02d}-{last:02d}",
                # Falling spend leaves a positive DD-smoothing credit at closure.
                "total_amount_gbp": round(120.0 - m * 2.5, 2),
                "segment": "resi",
                "commodity": "electricity",
            })
    return bills, {b["customer_id"]: "resi" for b in bills}, churned


def test_mutation_a_never_breaching_door_is_caught_in_the_published_log():
    """FAIL-SILENT proof. Force the verdict permanently False at the door and the
    world's published refund log must change — if it does not, the world is not really
    reading the company's compliance answer and the cut moved nothing."""
    bills, segments, churned = _refund_population()
    baseline = generate_credit_refund_log(bills, segments, churned)

    assert baseline, "vacuity: no refund events at all in this population"
    breaches = sum(1 for r in baseline if r["breached_slc14_deadline"])
    assert 0 < breaches < len(baseline), (
        f"vacuity: the population landed on ONE arm only ({breaches}/{len(baseline)} "
        "breached), so a hard-wired verdict would pass this test"
    )

    with _Mutant(
        SEAM_SOURCE,
        '"breached_slc14_deadline": record.breached_deadline(),',
        '"breached_slc14_deadline": False,',
        "_mutant_refund_never_breaches",
    ) as mutant:
        import simulation.credit_refund_events as events
        original = events.refund_on_account_closure
        try:
            events.refund_on_account_closure = mutant.refund_on_account_closure
            mutated = generate_credit_refund_log(bills, segments, churned)
        finally:
            events.refund_on_account_closure = original

    assert sum(1 for r in mutated if r["breached_slc14_deadline"]) == 0
    assert mutated != baseline, (
        "the published SLC 14 log was unchanged by a door that never reports a breach"
    )
    assert generate_credit_refund_log(bills, segments, churned) == baseline, "restoration failed"
