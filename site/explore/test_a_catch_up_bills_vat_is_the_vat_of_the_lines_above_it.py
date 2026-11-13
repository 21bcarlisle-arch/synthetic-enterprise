"""A printed bill's VAT line is the VAT on the lines printed above it (N31, twelfth cold read O15).

The ledger charges VAT on the whole net, catch-up adjustment included. The Explore bill printed the
catch-up BELOW the VAT line, so a reader checking VAT against the lines above it found it wrong on
every catch-up bill: OCC-a097d0031a9f-INV5940 (April 2023) printed £74.73 + £8.32 + £14.53 = £97.58
above a VAT line of £5.96, which is 5% of £97.58 + £21.57, with the £21.57 catch-up below it.

Drives the page's own `billEquationHtml()` through `_bill_render_harness.mjs` over the committed
per-customer ledger extract, so the control is the rendered text, not the record. The defect named:
any charge line that VAT is charged on printing below the VAT line.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from decimal import Decimal
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
PAGE = HERE / "index.html"
HARNESS = HERE / "_bill_render_harness.mjs"
CUSTOMERS = HERE.parent / "data" / "customers"
NODE = shutil.which("node")
ROW = re.compile(r'<div class="row"[^>]*><span class="rl">(.*?)</span><span>(.*?)</span></div>', re.S)
MONEY = re.compile(r"-?£[\d,]+\.\d{2}")
PENNY = Decimal("0.01")

pytestmark = pytest.mark.skipif(NODE is None, reason="node is not installed; the page cannot be driven")


def _rows(screen: str) -> list[tuple[str, Decimal]]:
    out = []
    for label, cell in ROW.findall(screen):
        tokens = MONEY.findall(cell)
        if tokens:
            out.append((label, Decimal(tokens[-1].replace("£", "").replace(",", ""))))
    return out


def _render(paths: list[Path]) -> dict[str, tuple[dict, list[tuple[str, Decimal]]]]:
    proc = subprocess.run([NODE, str(HARNESS), str(PAGE), *map(str, paths)],
                          capture_output=True, text=True, timeout=300)
    assert proc.returncode == 0, proc.stderr[-2000:]
    records = {i["id"]: i for p in paths for i in json.loads(p.read_text())["invoices"]}
    return {inv["id"]: (records[inv["id"]], _rows(inv["screen"]))
            for acct in json.loads(proc.stdout)["accounts"] for inv in acct["invoices"]}


def _vat_and_lines_above(rows):
    labels = [label for label, _ in rows]
    assert labels.count("+ VAT") == 1, labels
    at = labels.index("+ VAT")
    return rows[at][1], sum((amount for _, amount in rows[:at]), Decimal("0")), labels[at + 1:]


def test_inv5940_prints_its_catch_up_above_a_vat_line_that_is_5pc_of_the_lines_above_it():
    bills = _render([CUSTOMERS / "OCC-a097d0031a9f.json"])
    record, rows = bills["OCC-a097d0031a9f-INV5940"]
    assert Decimal(str(record["catchup_adjustment_gbp"])) == Decimal("21.57"), record
    vat, above, below = _vat_and_lines_above(rows)
    assert vat == Decimal("5.96")
    assert above == Decimal("97.58") + Decimal("21.57"), rows
    assert (above * Decimal("0.05")).quantize(PENNY) == vat
    assert below == ["= Total"], f"a line printed between VAT and the total: {below}"


def test_every_catch_up_bills_vat_line_is_the_vat_on_the_lines_above_it():
    files = [p for p in sorted(CUSTOMERS.glob("*.json"))
             if isinstance(d := json.loads(p.read_text()), dict) and d.get("segment") == "resi"
             and any(i.get("catchup_adjustment_gbp") for i in d.get("invoices") or [])]
    bills = _render(files)
    caught = {k: v for k, v in bills.items() if Decimal(str(v[0].get("catchup_adjustment_gbp") or 0))
              and Decimal(str(v[0].get("vat_gbp") or 0))}
    # The branch this control is about must be reachable, or every assertion below is vacuous.
    assert len(caught) >= 100, f"only {len(caught)} catch-up bills with VAT rendered"
    wrong = []
    for inv_id, (record, rows) in caught.items():
        vat, above, below = _vat_and_lines_above(rows)
        # Domestic fuel is VAT at 5% (VATA 1994 Sch 7A). Business accounts are left out on purpose:
        # an SME bill can carry 5% de minimis on this period and 20% on the period its catch-up
        # corrects, so one rate times the lines above it is not the identity there.
        rate = Decimal("0.05")
        # Each line is rounded to the penny before it prints, so a few pence of drift is rounding;
        # the defect is the whole catch-up's VAT (5% of a catch-up of £1 or more) missing.
        if abs((above * rate) - vat) > Decimal("0.03") or below != ["= Total"]:
            wrong.append((inv_id, str(vat), str(above), below))
    assert not wrong, f"{len(wrong)} of {len(caught)} catch-up bills: VAT not the VAT on the lines above it, e.g. {wrong[:5]}"
