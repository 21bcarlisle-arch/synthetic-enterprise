"""Permanent consistency-gate test for site/sim/index.html Customers sub-tab."""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parents[2] / "site"
SIM_HTML = SITE / "sim" / "index.html"

_IIFE_RE = re.compile(r"<script>\n\(function \(\) \{\n(.*)\n\}\(\)\);\n</script>", re.S)

_HARNESS_PREFIX = """
"use strict";
function makeEl() {
  return {
    _innerHTML: "",
    get innerHTML() { return this._innerHTML; },
    set innerHTML(v) { this._innerHTML = v; },
    classList: { add() {}, remove() {}, contains() { return false; } },
    style: {},
    addEventListener() {},
    querySelector() { return null; },
    querySelectorAll() { return []; },
  };
}
var _elements = {};
global.document = {
  getElementById: function (id) {
    if (!_elements[id]) _elements[id] = makeEl();
    return _elements[id];
  },
  querySelectorAll: function () { return []; },
  querySelector: function () { return null; },
  addEventListener: function () {},
};
global.window = global;
global.fetch = function () {
  return Promise.resolve({ json: function () { return Promise.resolve({}); } });
};
global.Chart = function () { return { destroy: function () {}, update: function () {} }; };
global.Chart.register = function () {};

// ---- extracted site/sim/index.html page body below ----
"""


def _extract_iife_body():
    html = SIM_HTML.read_text()
    m = _IIFE_RE.search(html)
    assert m, "site/sim/index.html inline <script> IIFE structure changed -- update _IIFE_RE"
    return m.group(1)


def _run_harness(customers, tmp_path):
    footer = (
        "\nvar testCusts = " + json.dumps(customers) + ";\n"
        "buildCustKpis({ customers: testCusts });\n"
        "buildCustTable({ customers: testCusts });\n"
        "console.log(JSON.stringify({\n"
        "  kpiHtml: document.getElementById('cust-kpi-grid').innerHTML,\n"
        "  tableHtml: document.getElementById('cust-tbody').innerHTML\n"
        "}));\n"
    )
    script = _HARNESS_PREFIX + _extract_iife_body() + footer
    js_path = tmp_path / "sim_harness.js"
    js_path.write_text(script)
    result = subprocess.run(
        ["node", str(js_path)], capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, "Node harness failed:\n" + result.stderr
    return json.loads(result.stdout)


def _kpi_value(kpi_html, label):
    m = re.search(
        re.escape(label) + r'</div><div class="kpi-value[^"]*">(\d+)</div>',
        kpi_html,
    )
    assert m, "KPI card '{}' not found in rendered output".format(label)
    return int(m.group(1))


pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="node not available")


def _customer(stress_points):
    return {"income_stress_trajectory": [{"stress": s} for s in stress_points]}


def test_stress_kpi_counts_case_insensitive(tmp_path):
    """buildCustKpis must bucket by the LATEST trajectory point regardless of
    the case SIM emits it in (SIM emits lowercase; QT found one call site
    comparing against uppercase literals and silently miscounting)."""
    customers = {
        "C1": _customer(["low", "HIGH"]),
        "C2": _customer(["Moderate"]),
        "C3": _customer(["MODERATE"]),
        "C4": _customer([]),
        "C_IC1": _customer(["high"]),
    }
    out = _run_harness(customers, tmp_path)
    kpi = out["kpiHtml"]
    assert _kpi_value(kpi, "Total Customers") == 5
    assert _kpi_value(kpi, "High Stress") == 2
    assert _kpi_value(kpi, "Moderate Stress") == 2
    assert _kpi_value(kpi, "Low Stress") == 1


def test_stress_table_matches_kpi_normalization(tmp_path):
    """The per-customer table must render the same normalized (uppercase)
    stress label the KPI header counted that customer under -- this is the
    exact cross-surface check the QT bug violated (header disagreed with
    table for the same underlying field)."""
    customers = {
        "C1": _customer(["high"]),
        "C2": _customer(["Moderate"]),
        "C3": _customer(["LOW"]),
    }
    out = _run_harness(customers, tmp_path)
    kpi, table = out["kpiHtml"], out["tableHtml"]
    assert _kpi_value(kpi, "High Stress") == 1
    assert _kpi_value(kpi, "Moderate Stress") == 1
    assert _kpi_value(kpi, "Low Stress") == 1
    assert ">HIGH<" in table
    assert ">MODERATE<" in table
    assert ">LOW<" in table


def test_missing_trajectory_defaults_low(tmp_path):
    customers = {"C1": _customer([])}
    out = _run_harness(customers, tmp_path)
    assert _kpi_value(out["kpiHtml"], "Low Stress") == 1
    assert _kpi_value(out["kpiHtml"], "High Stress") == 0
