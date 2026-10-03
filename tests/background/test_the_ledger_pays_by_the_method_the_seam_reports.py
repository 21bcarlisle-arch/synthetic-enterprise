"""The company's ledger is paid by the method the seam tells the company it holds.

A household's payment method had two homes in the world. `LivePaymentTriad` paid the company's
ledger by `payment_behaviour_source.generate_payment_method`'s own draw, while
`SimInterface.get_payment_method` reported `household_segments.payment_channel_for_customer`'s.
On the live book they agreed on 112 of 178 resi supply points -- chance at a 72% DD share -- so a
per-method belief learned from the ledger was keyed by a method that had not produced the debt.

One leg: over the run's own resi book, the triad's method mapped to the seam's vocabulary equals
the seam's answer for every supply point, on that supply point's own fuel. The partition control
comes first, because an all-direct-debit world would agree everywhere and prove nothing.
"""
from __future__ import annotations

from background.live_payment_triad import LivePaymentTriad
from company.interfaces.sim_interface import LiveSimInterface
from company.interfaces.supply_book import successor_supply_points
from simulation.household import household_of
from simulation.live_population import live_population
from simulation.payment_behaviour_source import SEAM_CHANNEL_FOR_METHOD


def _resi_book() -> list[tuple[str, str]]:
    return [(c["customer_id"], c["commodity"])
            for c in live_population() + successor_supply_points()
            if c.get("segment") == "resi"]


def test_the_ledger_and_the_seam_name_one_method_for_every_household_on_the_book():
    book = _resi_book()
    triad, seam = LivePaymentTriad(), LiveSimInterface()
    paid = {(cid, fuel): SEAM_CHANNEL_FOR_METHOD[triad._method_for(cid, fuel)] for cid, fuel in book}
    told = {(cid, fuel): seam.get_payment_method(household_of(cid), fuel) for cid, fuel in book}

    assert {"direct_debit", "standard_credit", "prepayment"} <= set(told.values()), (
        f"the book does not carry all three channels ({sorted(set(told.values()))}), so agreement "
        "would be trivial")
    assert any(fuel == "gas" and not cid.endswith("g") for cid, fuel in book), (
        "no gas-only household on the book, so the fuel the triad is handed is never tested")

    disagree = sorted(k for k in book if paid[k] != told[k])
    assert not disagree, (
        f"{len(disagree)} of {len(book)} supply points are paid into the ledger by one method and "
        f"reported to the company as another, e.g. {[(k, paid[k], told[k]) for k in disagree[:5]]}")
