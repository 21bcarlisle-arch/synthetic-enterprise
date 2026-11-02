"""The Billed stage's "Meter reads behind it" prints a gas meter's register in its own unit, and the
CV and correction factor that turn it into the kWh charged (fifth cold read, N11; C3 of
docs/market_research/a_gas_read_is_a_volume_and_the_bill_converts_it.md).

Drives the page's own `gasReadRows()` in node, so the control is the rendered text. The defects
named: a gas bill printing a kWh register no gas meter reads; the arithmetic shown not producing
the kWh printed; a fixed CV printed as if it were the period's published average; an electricity
bill, or a gas bill from a book built before the meter read volume, losing its reads.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"

_DRIVER = r"""
import fs from "node:fs";
import vm from "node:vm";
const html = fs.readFileSync(process.argv[2], "utf8");
const invs = JSON.parse(fs.readFileSync(0, "utf8"));
const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)]
  .map((m) => m[1]).filter((s) => s.trim());
function stub(id) {
  const e = { id, _inner: "", style: {}, dataset: {}, classList: { add() {}, remove() {} },
    setAttribute() {}, appendChild() {}, scrollIntoView() {}, focus() {}, getContext() { return {}; } };
  Object.defineProperty(e, "innerHTML", { get() { return e._inner; }, set(v) { e._inner = String(v); } });
  Object.defineProperty(e, "textContent", { get() { return e._inner; }, set(v) { e._inner = String(v); } });
  return e;
}
const els = {};
const document = { readyState: "complete", getElementById(id) { return (els[id] ||= stub(id)); },
  querySelector() { return stub("qs"); }, querySelectorAll() { return []; },
  createElement() { return stub("ce"); }, addEventListener() {} };
const inert = { then() { return inert; }, catch() { return inert; } };
const sb = { document, console, Date, Number, String, Object, Math, JSON, Array, isNaN, isFinite,
  fetch: () => inert, setTimeout() {}, alert() {}, location: { search: "", hash: "" },
  history: { replaceState() {} }, URLSearchParams: globalThis.URLSearchParams, Promise };
sb.window = sb;
vm.createContext(sb);
for (const s of scripts) vm.runInContext(s, sb);
if (typeof sb.gasReadRows !== "function") { console.error("gasReadRows() is gone from the page"); process.exit(3); }
process.stdout.write(JSON.stringify(invs.map((i) => sb.gasReadRows(i))));
"""

#: SYN-2016-001g's Feb 2017 actual bill after an estimated run, as the replayed ledger printed it.
GAS = {"read_unit": "m3", "opening_read_volume": 616.856, "closing_read_volume": 639.714,
       "volume_advance": 22.858, "calorific_value_mj_per_m3": 39.5,
       "calorific_value_basis": "fixed_stand_in", "correction_factor": 1.02264,
       "consumption_kwh": 643.6, "catchup_kwh": -387.1,
       "opening_read_kwh": 6921.5, "closing_read_kwh": 7178.0}
#: An imperial meter's bill: 40 hundred cubic feet, over a thousand kWh, so the printed kWh has a comma.
IMPERIAL = dict(GAS, read_unit="hcf", opening_read_volume=100.0, closing_read_volume=140.0,
                volume_advance=40.0, consumption_kwh=1271.0, catchup_kwh=0.0)
ELEC = {"opening_read_kwh": 4289.3, "closing_read_kwh": 5013.1, "consumption_kwh": 723.8}


def _shown_kwh(text):
    """The kWh the page prints after "÷ 3.6 MJ per kWh", read with its thousands separator."""
    return float(re.search(r"÷ 3.6 MJ per kWh\s*([\d,.]+) kWh", text).group(1).replace(",", ""))


def _print_tol(volume, factor_printed):
    """What the printed digits allow: half the kWh's 1dp, half the volume's 3dp at each end, and
    half the 4th decimal of the imperial factor where one is printed (1.0 prints none)."""
    per_unit = factor_printed * 1.02264 * 39.5 / 3.6
    factor_half_unit = 0.0 if factor_printed == 1.0 else 0.00005 * 1.02264 * 39.5 / 3.6 * volume
    return 0.05 + 2 * 0.0005 * per_unit + factor_half_unit


def _rows(*invs, tmp_path):
    driver = tmp_path / "driver.mjs"
    driver.write_text(_DRIVER)
    out = subprocess.run(["node", str(driver), str(INDEX)], input=json.dumps(list(invs)),
                         capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    return [re.sub(r"<[^>]+>", " ", h) for h in json.loads(out.stdout)]


def test_a_gas_bill_prints_volume_cv_and_factor_and_they_produce_the_kwh(tmp_path):
    gas, elec, old_gas = _rows(GAS, ELEC, {k: GAS[k] for k in ("opening_read_kwh", "closing_read_kwh")},
                               tmp_path=tmp_path)
    # Every leg reached first: a volume bill, an electricity bill, a gas bill from an older book.
    assert "m³" in gas and "m³" not in elec and "m³" not in old_gas
    assert "616.856 m³" in gas and "639.714 m³" in gas and "22.858 m³" in gas
    assert "× 1.02264" in gas and "× 39.5 MJ/m³" in gas
    assert "a fixed figure, not the period's published average" in gas
    # The arithmetic the page shows produces the kWh it prints, within the printed digits.
    assert abs(22.858 * 1.02264 * 39.5 / 3.6 - _shown_kwh(gas)) <= _print_tol(22.858, 1.0)
    assert "4,289.3" in elec or "4289.3" in elec


def test_an_imperial_bill_prints_the_factor_the_conversion_uses_and_it_produces_the_kwh(tmp_path):
    """The hcf leg. Defects: the page printing 2.832 while the conversion uses 100 x 0.3048^3 (2.8317),
    and a kWh over a thousand read as its digits before the comma."""
    from company.billing.gas_volume_conversion import M3_PER_HUNDRED_CUBIC_FEET, kwh_from_volume

    (imperial,) = _rows(IMPERIAL, tmp_path=tmp_path)
    assert "hundred cubic feet" in imperial and "40.000 hundred cubic feet" in imperial
    printed = float(re.search(r"Imperial meter: × ([\d.]+) to cubic metres", imperial).group(1))
    assert printed == round(M3_PER_HUNDRED_CUBIC_FEET, 4)
    shown = _shown_kwh(imperial)
    assert shown == 1271.0
    assert abs(40.0 * printed * 1.02264 * 39.5 / 3.6 - shown) <= _print_tol(40.0, printed)
    assert abs(kwh_from_volume(40.0, "hcf", 39.5) - shown) <= _print_tol(40.0, printed)
