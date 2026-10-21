"""The published run carries the company's SLC 21B.4 read instruction when the policy asks, and the
standing policy asks (2026-10-21, with each visit charged: `read_access_and_theft_duties.md` s.2.9).

Defect this guards (2026-10-18, direction item `wire-the-read-instruction-into-the-published-run`):
6e9dc90f8 put `instruct_reads` on the company's bill assembly, but the run's own billing door
(`run_phase4c_on_phase2b.build_monthly_bills`, which `main` calls) never passed it, so no published
figure could show a read instruction however the policy was set.

The world's read feed is replaced by a scripted one, because whether eleven estimates in a row
happen on the real feed is a draw: one account is read in its first month and never again on its
own, and an instructed visit reads.

Mutations, each run and reverted: `main` dropping `instruct_reads=` from its call, the wrapper
dropping it before `assemble_monthly_bills`, and the wrapper's None resolving to True. The first
two red the chain test, the last reds the off-path test. The off path is read under a standing
policy patched off, so it stays one variable now that the standing policy is on.
"""

from __future__ import annotations

import calendar
import dataclasses
import json
from dataclasses import dataclass

import pytest

import simulation.run_phase2b as run_phase2b
import simulation.run_phase4c_on_phase2b as run4c
from company.billing.monthly_bill_assembly import build_monthly_bills as company_bills

MONTHS = [(2023, m) for m in range(1, 13)] + [(2024, m) for m in range(1, 7)]
ACCOUNT = "C1"  # a founder on direct debit: the assembly prices from its customer record


def _records():
    out = []
    for yr, mo in MONTHS:
        out.extend({
            "customer_id": ACCOUNT,
            "settlement_date": f"{yr}-{mo:02d}-{d:02d}",
            "settlement_period": 1,
            "consumption_kwh": 10.0,
            "unit_rate_gbp_per_mwh": 200.0,
            "revenue_gbp": 0.01 * 200.0 + 0.5,
            "standing_charge_gbp": 0.5,
            "wholesale_cost_gbp": 0.0,
            "margin_gbp": 0.0,
        } for d in range(1, calendar.monthrange(yr, mo)[1] + 1))
    return out


@dataclass
class _Read:
    status: str
    estimated_consumption_kwh: float | None
    consecutive_estimated_count: int


class _Feed:
    def __init__(self, must_read_arm="register", instructed_read_arm="register"):
        self.instructed_read_arm = instructed_read_arm

    def meter_type_for(self, customer):
        return "traditional"

    def read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        if period_end.startswith("2023-01"):
            return _Read("actual", None, 0)
        return _Read("estimated", None, consecutive + 1)

    final_read_for = read_for

    def instructed_read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        return _Read("actual", None, 0)


@pytest.fixture
def scripted_world(monkeypatch):
    monkeypatch.setattr(run4c, "SimulatedReadFeed", _Feed)


def _on(policy):
    return dataclasses.replace(policy, instruct_reads_in_billing_run=True)


def _off(policy):
    return dataclasses.replace(policy, instruct_reads_in_billing_run=False)


def _instructions(bills):
    return [b["period_end"] for b in bills if "read_instruction_raised" in b]


def test_off_the_run_bills_byte_for_byte_as_the_company_does_without_the_switch(scripted_world,
                                                                                monkeypatch):
    """Defect: the off path moves, or the wrapper's None stops reading the standing policy."""
    monkeypatch.setattr(run_phase2b, "CURRENT_POLICY", _off(run_phase2b.CURRENT_POLICY))

    def dump(bills):
        return json.dumps(bills, sort_keys=True, default=str)

    unswitched = company_bills(_records(), _Feed(), payment_channel_feed=run4c.simulated_payment_channel,
                               premise_listing_feed=run4c.simulated_council_tax_listing)
    assert (run4c.read_instruction_request(None), dump(run4c.build_monthly_bills(_records()))) == (
        False, dump(unswitched))


def test_the_switch_reaches_the_seam_from_main_and_from_the_standing_policy(scripted_world, monkeypatch):
    """Defect: the switch is dropped between the policy and the company's bill assembly, so it is on
    and the published bills carry no instruction. The partition: off asks none; on asks one, at the
    11th estimate in a row (December 2023), its visit on the January 2024 bill."""
    seen = {}

    def capture(*args, **kwargs):
        seen["instruct_reads"] = kwargs.get("instruct_reads")
        seen["arm"] = args[1].instructed_read_arm
        raise StopIteration

    def run_main(policy, arm="register"):
        seen.clear()
        with monkeypatch.context() as m:
            m.setattr(run4c, "run_phase2b", lambda **_: {"all_records": []})
            m.setattr(run4c, "assemble_monthly_bills", capture)
            with pytest.raises(StopIteration):
                run4c.main(policy=policy, instructed_read_arm=arm)
        return dict(seen)

    standing = run_phase2b.CURRENT_POLICY
    standing_on_bills = run4c.build_monthly_bills(_records())
    monkeypatch.setattr(run_phase2b, "CURRENT_POLICY", _off(standing))
    off_bills = run4c.build_monthly_bills(_records())
    assert (
        standing.instruct_reads_in_billing_run,
        run_main(_off(standing)), run_main(standing), run_main(_on(standing), "ceiling"),
        _instructions(off_bills), _instructions(standing_on_bills),
    ) == (
        True,
        {"instruct_reads": False, "arm": "register"}, {"instruct_reads": True, "arm": "register"},
        {"instruct_reads": True, "arm": "ceiling"},
        [], ["2024-01-31"],
    )
