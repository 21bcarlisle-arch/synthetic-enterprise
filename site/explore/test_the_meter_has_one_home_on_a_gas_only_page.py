"""The meter a household page prints has one home, on a gas-only page too (N8).

Fourth cold read on the 209c3350ab book (2026-10-29), objection O26 on OCC-2f64fad94fe7, a gas-only
account: "Meter Smart" in the Chosen stage beside "This household's meter type is not on the
supplier's record" in the day clock. N8 was marked fixed on 28 Oct (`d575b53d2b`), which pointed
the day clock at the household's ELECTRICITY record. The "Meter" row prints `CUR.detail`, which is
the gas leg when there is no electricity, so on a gas-only page the day clock read a record that
does not exist and called the meter unknown. Its "Supply point —" had the same shape: the row read
`mpan` alone, and the account's MPRN is on record.

This drives the page's own `stageChosen()` and `hhDayPanels()` in node, as `selectCustomer` sets
them up, over OCC-2f64fad94fe7 and over every household of a page book. On each it grades:
  1. a printed meter type is never beside "not on the supplier's record";
  2. a printed "Smart" is never beside "no meter that can report half-hourly", nor
     "Traditional" beside "has a smart meter";
  3. a page with a supply point number on record never prints "Supply point —".
The book defaults to the published feed; EXPLORE_PAGES_DIR grades another one (the 209c rebuild is
/var/tmp/fourth-read/tree/site/data).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
DATA = Path(os.environ.get("EXPLORE_PAGES_DIR") or HERE.parent / "data")

_DRIVER = r"""
import fs from "node:fs";
import vm from "node:vm";
const html = fs.readFileSync(process.argv[2], "utf8");
const households = JSON.parse(fs.readFileSync(0, "utf8"));
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
for (const f of ["stageChosen", "hhDayPanels"]) {
  if (typeof sb[f] !== "function") { console.error(f + "() is gone from the page"); process.exit(3); }
}
const out = households.map((byFuel) => {
  // As selectCustomer sets it: the detail is the electricity leg, else the gas leg.
  const d = byFuel.electricity || byFuel.gas;
  const fuels = Object.keys(byFuel);
  vm.runInContext("HH_DAYS = {}; HH_META = {};", sb);
  sb.CUR = { index: { customer_group: null, fuels }, detail: d, fuels: byFuel };
  return { chosen: sb.stageChosen(d, { fuels }), clock: sb.hhDayPanels() };
});
process.stdout.write(JSON.stringify(out));
"""

_TEXT = re.compile(r"<[^>]+>")
METER = re.compile(r"<td>Meter</td><td class=\"n\">([^<]*)</td>")
SUPPLY = re.compile(r"<td>Supply point</td><td class=\"n\">([^<]*)</td>")

#: OCC-2f64fad94fe7 on the 209c3350ab book, the fields the two panels read.
OCC_2F64 = {"gas": {"account_id": "OCC-2f64fad94fe7", "commodity": "gas", "segment": "resi",
                    "acquisition_date": "2024-02-22", "meter_type": "Smart", "mpan": None,
                    "mprn": "1305736345", "timeline": [], "invoices": []}}


def _render(households: list[dict], tmp: Path) -> list[dict]:
    driver = tmp / "driver.mjs"
    driver.write_text(_DRIVER)
    proc = subprocess.run(["node", str(driver), str(INDEX)], input=json.dumps(households),
                          capture_output=True, text=True, timeout=300)
    assert proc.returncode == 0, proc.stderr[:800]
    return json.loads(proc.stdout)


def grade(byfuel: dict, rendered: dict) -> list[str]:
    """Every way the page states a meter fact twice and disagrees with itself; [] when it does not."""
    d = byfuel.get("electricity") or byfuel.get("gas")
    meter = METER.search(rendered["chosen"])
    printed = (meter.group(1).strip() if meter else "").lower()
    clock = _TEXT.sub(" ", rendered["clock"])
    out = []
    if printed not in ("", "—") and "not on the supplier's record" in clock:
        out.append(f"leg 1: 'Meter {printed}' beside 'not on the supplier's record'")
    if printed == "smart" and "no meter that can report half-hourly" in clock:
        out.append("leg 2: 'Meter Smart' beside 'no meter that can report half-hourly'")
    if printed == "traditional" and "has a smart meter" in clock:
        out.append("leg 2: 'Meter Traditional' beside 'has a smart meter'")
    supply = SUPPLY.search(rendered["chosen"])
    on_record = (d.get("mpan") or {}).get("bottom_line") if isinstance(d.get("mpan"), dict) else None
    if (on_record or d.get("mprn")) and supply and supply.group(1).strip() == "—":
        out.append("leg 3: 'Supply point —' with a supply point number on record")
    return out


def test_a_gas_only_page_states_its_meter_once(tmp_path):
    # Red on 90b330d09d: "Meter Smart" beside "meter type is not on the supplier's record", and
    # "Supply point —" with MPRN 1305736345 on record.
    [r] = _render([OCC_2F64], tmp_path)
    assert grade(OCC_2F64, r) == []
    assert "Smart" in r["chosen"] and "1305736345" in r["chosen"]


def test_the_grader_reaches_each_leg(tmp_path):
    # A grader that finds nothing passes every page; show each leg can fire.
    broken = {"chosen": '<td>Meter</td><td class="n">Smart</td><td>Supply point</td><td class="n">—</td>',
              "clock": "This household's meter type is not on the supplier's record, and it has no meter "
                       "that can report half-hourly."}
    legs = {w.split(":")[0] for w in grade(OCC_2F64, broken)}
    assert legs == {"leg 1", "leg 2", "leg 3"}, legs
    trad = {"chosen": '<td>Meter</td><td class="n">Traditional</td>', "clock": "This household has a smart meter"}
    assert grade(OCC_2F64, trad)


def test_every_household_in_the_book_states_its_meter_once(tmp_path):
    pages_dir = DATA / "customers"
    if not pages_dir.is_dir():
        pytest.skip(f"no per-customer pages at {pages_dir}")
    pages = {}
    for f in sorted(pages_dir.glob("*.json")):
        d = json.loads(f.read_text())
        if isinstance(d, dict) and d.get("account_id") and d.get("commodity") in ("electricity", "gas"):
            pages[d["account_id"]] = d
    assert len(pages) > 100, "the book read is too small to say anything"
    # One household per base account, both legs where it has both, as the picker pairs them.
    households: dict[str, dict] = {}
    for d in pages.values():
        households.setdefault(d.get("base_account_id") or d["account_id"], {})[d["commodity"]] = d
    hh = list(households.values())
    breaches = [(next(iter(h.values()))["account_id"], w)
                for h, r in zip(hh, _render(hh, tmp_path)) for w in grade(h, r)]
    gas_only = sum(1 for h in hh if "electricity" not in h)
    print(f"METER_ONE_HOME households={len(hh)} gas_only={gas_only} breaches={len(breaches)}")
    assert gas_only, "no gas-only household in the book, so the N8 leg was never reached"
    assert not breaches, f"{len(breaches)} of {len(hh)} households: {breaches[:5]}"
