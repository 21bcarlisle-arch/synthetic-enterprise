"""The Billed stage's "Meter reads behind it" prints a two-rate meter's reads register by register,
never the sum of them (sixth cold read, N12;
docs/market_research/a_multi_register_meters_bands_add_up_to_its_total.md).

Drives the page's own `gasReadRows()` in node with the gas door test's driver, so the control is the
rendered text. The defects named: a profile class 2 bill printing a read equal to the sum of two
register reads (PROS-2017-0233's 3,622.7 = Day 1,978.5 + Night 1,644.2); a register's pair missing
from the panel; a single-register bill losing its one pair; a book without per-register reads
falling back to the sum instead of saying so.
"""
from __future__ import annotations

import importlib.util
import itertools
import re
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "_gas_read_door", Path(__file__).with_name("test_a_gas_bill_prints_its_volume_cv_and_correction_factor.py"))
_gas = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_gas)

#: PROS-2017-0233's Aug 2018 bill INV12356 on the 85b044be54 book, as the ledger printed it.
PC2 = {"opening_read_kwh": 3622.7, "closing_read_kwh": 3806.8, "consumption_kwh": 184.1,
       "registers": [
           {"register_id": "4", "label": "Day", "consumption_kwh": 131.8, "unit_rate_p_per_kwh": 13.13,
            "opening_read_kwh": 1978.5, "closing_read_kwh": 2110.3},
           {"register_id": "5", "label": "Night", "consumption_kwh": 52.3, "unit_rate_p_per_kwh": 3.37,
            "opening_read_kwh": 1644.2, "closing_read_kwh": 1696.5}]}
SINGLE = {"opening_read_kwh": 4289.3, "closing_read_kwh": 5013.1, "consumption_kwh": 723.8,
          "registers": [{"label": "Anytime", "consumption_kwh": 723.8}]}
UNREAD = {**PC2, "registers": [{k: v for k, v in r.items() if "read" not in k} for r in PC2["registers"]]}


def _printed_reads(text):
    return [float(x.replace(",", "")) for x in re.findall(r"read[^\d]*?\)?\s+([\d,]+\.\d)", text)]


def test_a_two_rate_bill_prints_each_registers_pair_and_no_sum(tmp_path):
    pc2, single, unread = _gas._rows(PC2, SINGLE, UNREAD, tmp_path=tmp_path)
    # Every leg reached: the two-register pair, the single-register pair, the unread refusal.
    for label, opening, closing in (("Day", "1,978.5", "2,110.3"), ("Night", "1,644.2", "1,696.5")):
        assert re.search(r"Opening read \({}\)\s+{}".format(label, opening), pc2), pc2
        assert re.search(r"Closing read \({}\)\s+{}".format(label, closing), pc2), pc2
    assert "4,289.3" in single and "5,013.1" in single
    assert "reads are not recorded in this book" in unread
    regs = PC2["registers"]
    sums = {round(a[k] + b[k], 1) for a, b in itertools.combinations(regs, 2)
            for k in ("opening_read_kwh", "closing_read_kwh")}
    printed = _printed_reads(pc2) + _printed_reads(unread)
    assert len(_printed_reads(pc2)) == 4, pc2
    assert not sums & set(printed), "a printed read is the sum of two registers: {}".format(sums & set(printed))
