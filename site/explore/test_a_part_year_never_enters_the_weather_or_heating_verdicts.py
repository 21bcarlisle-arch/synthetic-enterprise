"""Explore's "Gas against the weather" correlation and its "this home heats with electricity" verdict
read whole months on supply only (ninth cold read, N24;
docs/staging/done/SEAT_FINDING_THE_NINTH_COLD_READ_FINDS_HOUSEHOLD_DIAGNOSTICS_COMPUTED_OVER_PART_YEARS_SO_GAS_RUNS_AGAINST_THE_WEATHER_ON_MOST_PAGES_2026-11-08.md).

Drives the page's own `hddPanel()` and `seasonalSwing()` in node. The defects named: a part year
(SYN-2016-250's 2016 at 7,240 kWh and 2021 at 11,594 kWh against ~16,500 in full years) entering the
correlation and printing "weaker than the heating story predicts"; a series' stub first or last
month counted as a whole month; a 7-day June stub (PROS-2024-0335) read as a summer.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

INDEX = Path(__file__).resolve().parent / "index.html"

_DRIVER = r"""
import fs from "node:fs";
import vm from "node:vm";
const html = fs.readFileSync(process.argv[2], "utf8");
const job = JSON.parse(fs.readFileSync(0, "utf8"));
const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)]
  .map((m) => m[1]).filter((s) => s.trim());
const stub = () => ({ style: {}, dataset: {}, classList: { add() {}, remove() {} },
  setAttribute() {}, appendChild() {}, addEventListener() {} });
const inert = { then() { return inert; }, catch() { return inert; } };
const sb = { document: { readyState: "complete", getElementById: stub, querySelector: stub,
  querySelectorAll: () => [], createElement: stub, addEventListener() {} },
  console, Date, Number, String, Object, Math, JSON, Array, isNaN, isFinite, fetch: () => inert,
  setTimeout() {}, alert() {}, location: { search: "", hash: "" }, history: { replaceState() {} },
  URLSearchParams, Promise };
sb.window = sb;
vm.createContext(sb);
for (const s of scripts) vm.runInContext(s, sb);
vm.runInContext("HDD_META = {};", sb);
sb.HDD_BY_YEAR = job.hdd;
process.stdout.write(JSON.stringify({
  panels: job.gas.map((m) => sb.hddPanel({ gas: { consumption: { monthly: m } } })),
  swings: job.elec.map((m) => sb.seasonalSwing(m)),
}));
"""

#: Real degree-day totals from site/data/weather.json, 2016-2021.
HDD = {"2016": 1958, "2017": 1799, "2018": 1842, "2019": 1857, "2020": 1688, "2021": 1943}
#: A month's share of a year's heating, roughly the GB gas profile.
SHAPE = [0.15, 0.13, 0.11, 0.08, 0.05, 0.03, 0.03, 0.03, 0.05, 0.08, 0.12, 0.14]


def _gas_year(year, k_per_hdd, months=range(1, 13)):
    return [{"month": f"{year}-{mm:02d}", "kwh": round(HDD[year] * k_per_hdd * SHAPE[mm - 1], 1)}
            for mm in months]


def _drive(tmp_path, gas=(), elec=()):
    driver = tmp_path / "driver.mjs"
    driver.write_text(_DRIVER)
    out = subprocess.run(["node", str(driver), str(INDEX)],
                         input=json.dumps({"hdd": HDD, "gas": list(gas), "elec": list(elec)}),
                         capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    res = json.loads(out.stdout)
    return [re.sub(r"<[^>]+>", " ", p) for p in res["panels"]], res["swings"]


def _r(text):
    m = re.search(r"r = (-?\d\.\d\d)", text)
    return None if m is None else float(m.group(1))


def test_a_part_year_is_left_out_of_the_weather_correlation_and_named(tmp_path):
    # A gas-heated home that follows the weather exactly, supplied from 20 May 2016 (May a stub)
    # to mid-Sep 2021. Its full years 2017-2020 track degree days; 2016 and 2021 enter at a
    # fraction of a year, which is what put SYN-2016-250 at r = -0.78.
    series = ([{"month": "2016-05", "kwh": 40.0}] + _gas_year("2016", 8.5, range(6, 13))
              + [row for y in ("2017", "2018", "2019", "2020") for row in _gas_year(y, 8.5)]
              + _gas_year("2021", 8.5, range(1, 9)) + [{"month": "2021-09", "kwh": 60.0}])
    # The same home with its first and last months whole and on 1 Jan / 31 Dec boundaries
    # except that the stub-at-each-end rule drops them: 2017-2020 whole, 2016 and 2021 part.
    whole_ends = [row for y in ("2016", "2017", "2018", "2019", "2020", "2021") for row in _gas_year(y, 8.5)]
    (partial, ends), _ = _drive(tmp_path, gas=[series, whole_ends])

    assert _r(partial) is not None and _r(partial) > 0.99, partial
    assert "Across these 4 years" in partial
    assert "part years" in partial and "2016, 2021" in partial
    # The rows printed are the full years: no part-year kWh in the table.
    assert re.search(r"2017\s+1,799", partial), partial
    assert not re.search(r"2016\s+1,958", partial) and not re.search(r"2021\s+1,943", partial)
    # A series whose first month is January still loses that January (it may be a stub), so
    # 2016 and 2021 are part years there too: the safe direction, said on the page.
    assert "2016, 2021" in ends and "Across these 4 years" in ends


def test_too_few_full_years_says_so_and_prints_no_r(tmp_path):
    series = ([{"month": "2016-05", "kwh": 40.0}] + _gas_year("2016", 8.5, range(6, 13))
              + _gas_year("2017", 8.5) + _gas_year("2018", 8.5) + _gas_year("2019", 8.5, range(1, 4)))
    (panel,), _ = _drive(tmp_path, gas=[series])
    assert _r(panel) is None
    assert "Too few full years" in panel and "2016, 2019" in panel


def test_the_heating_verdict_needs_a_whole_winter_and_a_whole_summer(tmp_path):
    winter = [{"month": m, "kwh": 900.0} for m in ("2024-11", "2024-12", "2025-01", "2025-02",
                                                       "2025-03", "2025-04", "2025-05")]
    # PROS-2024-0335's shape: its only summer is a 7-day June stub at the end of the series.
    stub_june = winter + [{"month": "2025-06", "kwh": 30.0}]
    # Every winter and summer month whole and interior: the branch CAN be taken, and the
    # verdict is a number (the partition control -- a rule that nulls everything passes the rest).
    year = [{"month": f"2024-{mm:02d}", "kwh": (900.0 if mm in (1, 2, 12) else 150.0)}
            for mm in range(1, 13)]
    full = [{"month": "2023-12", "kwh": 900.0}] + year + [{"month": "2025-01", "kwh": 900.0}]
    # Whole June and July, then a stub August: a summer with a month missing is not a summer.
    two_months = winter + [{"month": "2025-06", "kwh": 150.0}, {"month": "2025-07", "kwh": 150.0},
                           {"month": "2025-08", "kwh": 20.0}]
    _, (stubbed, short_summer, whole) = _drive(tmp_path, elec=[stub_june, two_months, full])
    assert stubbed is None and short_summer is None
    assert whole is not None and abs(whole - 6.0) < 1e-9
