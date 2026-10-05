"""The registry-EAC rewrite reaches the phase-4c DD opening.

Defect this catches (2026-10-01): `run_phase2b.main` re-sets a fabric premise's `eac_kwh` to
its own trailing-year reads by writing into the customer RECORD (3bf64c4e7). `run_phase4c`
sized the DD openings from a second `live_population()` call, which builds fresh dicts for
every drawn account, so the opening never saw the rewrite: PROS-2024-0082 opened at the drawn
2,602 kWh against 41,951 billed. Revert `CUSTOMERS = _PHASE2B_CUSTOMERS` to
`CUSTOMERS = live_population()` and both tests here red.
"""
from __future__ import annotations

import simulation.run_phase2b as p2b
import simulation.run_phase4c_on_phase2b as p4c


def test_every_record_phase_4c_reads_is_the_record_phase_2b_rewrites():
    rewritten = {c["customer_id"]: c for c in p2b.ELEC_CUSTOMERS + p2b.SUCCESSOR_ELEC_CUSTOMERS}
    read = {c["customer_id"]: c for c in p4c._get_all_customers()}
    # The partition must hold drawn accounts, or a static-only book would pass by identity alone.
    drawn = [cid for cid in rewritten if cid.startswith("PROS-")]
    assert drawn, "no drawn account in the book: this control would grade only the static roster"
    not_shared = [cid for cid in rewritten if cid in read and read[cid] is not rewritten[cid]]
    assert not not_shared, (
        f"{len(not_shared)} of {len(rewritten)} electricity records phase 4c reads are a "
        f"different object from the one phase 2b rewrites, e.g. {not_shared[:3]}")
    assert set(rewritten) <= set(read)


def test_a_rewritten_eac_moves_the_opening_phase_4c_sets(monkeypatch):
    # Any drawn account phase 4c opens. A named one (PROS-2024-0082, the account the defect was
    # seen on) left the book when the draw moved, and `next()` raised before the property was asked.
    drawn = [c for c in p2b.ELEC_CUSTOMERS if c["customer_id"].startswith("PROS-")]
    opened = p4c._opening_dd_by_customer(drawn)
    assert opened, "no drawn electricity account has an opening: nothing here can be moved"
    record = next(c for c in drawn if c["customer_id"] in opened)
    cid = record["customer_id"]
    before = p4c._opening_dd_by_customer(
        [c for c in p4c._get_all_customers() if c["customer_id"] == cid])[cid]
    # The rewrite's own write, done in place on phase 2b's record exactly as main() does.
    monkeypatch.setitem(record, "eac_kwh", record["eac_kwh"] * 16)
    after = p4c._opening_dd_by_customer(
        [c for c in p4c._get_all_customers() if c["customer_id"] == cid])[cid]
    assert after > before * 5, (cid, before, after)
