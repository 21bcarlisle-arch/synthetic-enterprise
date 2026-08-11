"""The statutory-obligations seam's contract — and the ways this cut could rot silently.

WHY THIS FILE EXISTS (R15: a control must be able to FAIL on its own named defect)
---------------------------------------------------------------------------------
KNIFE pass 3, `A_composition_lift` step 17, moved the supplier's annual statutory
return out of `simulation/run_phase2b.py::main()` into
`company/regulatory/statutory_obligations.py` behind
`company/interfaces/statutory_obligations.py` — three wall crossings
(`company.regulatory.roc_ledger`, `company.regulatory.fit_book`,
`company.regulatory.ccl_ledger`).

The epistemic-wall ratchet polices the STATIC half: a module-scope
`company.regulatory.statutory_obligations -> simulation.*` import is a new
class-(a) edge, the forbidden direction, and reds the suite. Three things it
cannot see:

1. **A lazy import.** The ratchet covers static imports only; an in-function
   `import simulation.…` escapes it. The natural convenience change here is for
   the builder to reach for the run's own customer roster rather than be handed
   the two id sets — `ELEC_CUSTOMERS` and `GAS_CUSTOMERS` are module globals in
   the world file, one import away. So control 1 is BEHAVIOURAL: it builds a
   real `StatutoryObligations` in a clean interpreter and asks which modules the
   import system actually loaded. Its mutation performs the defect on a COPY of
   the real source and re-runs the same detector, so the control is tried rather
   than trusted (and no repo file is edited mid-run, which would corrupt
   `inspect.getsource` for every other test in the session).

2. **A silently reordered, dropped or re-rounded block.** The claim this cut
   rests on is that the three blocks compute what the inlined code computed.
   Nothing static sees a `round()` move or an accumulator drop, and the effect is
   not a crash — it is a different buy-out cost. Control 2 replicates the PRE-CUT
   inlined sequence, transcribed from the source it was lifted out of (not from
   the module under test, which would be a mirror), and asserts all three
   summaries are identical.

3. **THE ARGUMENT SWAP, and it is the one this cut actually introduces.** Before
   the cut, CCL read `ELEC_CUSTOMERS` and `GAS_CUSTOMERS` directly at the point
   of use, so the elec set could not arrive where the gas set belonged. Now both
   are computed at the call site and passed positionally-by-keyword into one
   signature. Swapping them, or dropping the `segment == "I&C"` filter from one,
   changes every CCL figure — and every test in this file that exercises the impl
   module directly would stay green, because the impl would be given exactly what
   the caller chose to give it. Control 3 is an AST check over the real call site
   in `run_phase2b.py`, with a vacuity guard (a source with no such call would
   make it pass for free) and a mutation that performs the swap.

Each `test_mutation_*` performs the named defect rather than asserting it is
impossible.

VACUITY, stated once for the whole file. The fixture years are 2017 and 2018,
chosen because the RO obligation level, the FiT levelisation rate and BOTH CCL
rates are non-zero there, and the CCL elec and gas rates DIFFER (0.568 vs 0.198
p/kWh in 2017). A fixture in, say, 2020 would have a zero FiT rate and control 2
would pass with the FiT block deleted; a fixture where elec and gas rates matched
would pass with control 3's swap performed. The guards below assert both
properties of the fixture rather than leaving them to the reader.
"""

from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
from collections import defaultdict

import pytest

from company.interfaces import statutory_obligations as door
from company.regulatory import statutory_obligations as impl
from company.regulatory.ccl_ledger import CCLFuel, CCLLedger
from company.regulatory.fit_book import _FIT_LEVELISATION_RATE_PER_MWH, FITBook
from company.regulatory.roc_ledger import (
    _ROC_BUY_OUT_PRICE_GBP,
    _ROC_OBLIGATION_LEVEL,
    ROCLedger,
)

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RUN_MODULE_PATH = os.path.join(REPO_ROOT, "simulation", "run_phase2b.py")
IMPL_PATH = os.path.join(REPO_ROOT, "company", "regulatory", "statutory_obligations.py")

FIXTURE_YEARS = ["2017", "2018"]


# ---------------------------------------------------------------------------
# Fixtures — the smallest book that exercises all three blocks in both fuels.
# ---------------------------------------------------------------------------


def _elec_customers() -> list[dict]:
    return [
        {"customer_id": "E-IC-1", "commodity": "electricity", "segment": "I&C"},
        {"customer_id": "E-RESI-1", "commodity": "electricity", "segment": "resi"},
    ]


def _gas_customers() -> list[dict]:
    return [
        {"customer_id": "G-IC-1", "commodity": "gas", "segment": "I&C"},
        {"customer_id": "G-RESI-1", "commodity": "gas", "segment": "resi"},
    ]


def _settled_records() -> list[dict]:
    """Monthly records for both fuels and both segments, across both years."""
    records = []
    for year in FIXTURE_YEARS:
        for month in range(1, 13):
            date = f"{year}-{month:02d}-01"
            records.append(
                {
                    "customer_id": "E-IC-1",
                    "settlement_date": date,
                    "consumption_kwh": 40_000.0 + month * 100,
                    "commodity": "elec",
                }
            )
            records.append(
                {
                    "customer_id": "E-RESI-1",
                    "settlement_date": date,
                    "consumption_kwh": 250.0 + month,
                    "commodity": "elec",
                }
            )
            records.append(
                {
                    "customer_id": "G-IC-1",
                    "settlement_date": date,
                    "consumption_kwh": 90_000.0 + month * 250,
                    "commodity": "gas",
                }
            )
            records.append(
                {
                    "customer_id": "G-RESI-1",
                    "settlement_date": date,
                    "consumption_kwh": 900.0 + month,
                    "commodity": "gas",
                }
            )
    return records


def _ic_ids(customers: list[dict]) -> set[str]:
    return {c["customer_id"] for c in customers if c.get("segment") == "I&C"}


def _build() -> impl.StatutoryObligations:
    return impl.build_statutory_obligations(
        settled_records=_settled_records(),
        report_years=FIXTURE_YEARS,
        ic_elec_customer_ids=_ic_ids(_elec_customers()),
        ic_gas_customer_ids=_ic_ids(_gas_customers()),
    )


# ---------------------------------------------------------------------------
# The fixture's own properties — the vacuity guards the file's docstring names.
# ---------------------------------------------------------------------------


def test_fixture_is_not_vacuous_every_rate_is_live_and_the_two_fuels_differ():
    for year in FIXTURE_YEARS:
        y = int(year)
        assert _ROC_OBLIGATION_LEVEL.get(y, 0.0) > 0, f"RO level zero in {y}"
        assert _FIT_LEVELISATION_RATE_PER_MWH.get(y, 0.0) > 0, f"FiT rate zero in {y}"
        elec = CCLLedger.rate_for_year(y, CCLFuel.ELECTRICITY)
        gas = CCLLedger.rate_for_year(y, CCLFuel.GAS)
        assert elec > 0 and gas > 0, f"a CCL rate is zero in {y}"
        assert elec != gas, (
            f"CCL elec and gas rates are equal in {y} — control 3's swap "
            "mutation would be undetectable on this fixture"
        )

    built = _build()
    assert built.roc_summary["total_buy_out_cost_gbp"] > 0
    assert built.fit_summary["total_fit_levy_gbp"] > 0
    assert built.ccl_summary["total_ccl_gbp"] > 0
    assert set(built.ccl_summary["per_year"]) == set(FIXTURE_YEARS)


def test_the_door_re_exports_the_implementation():
    assert door.build_statutory_obligations is impl.build_statutory_obligations
    assert door.StatutoryObligations is impl.StatutoryObligations


# ---------------------------------------------------------------------------
# CONTROL 1 — the company module must not reach back into the world, statically
# OR lazily. Behavioural: what did the import system actually load?
# ---------------------------------------------------------------------------

_PROBE = textwrap.dedent(
    """
    import json, sys
    sys.path.insert(0, {repo!r})
    sys.path.insert(0, {pkgdir!r})
    import {modname} as m

    m.build_statutory_obligations(
        settled_records=[
            {{"customer_id": "E-IC-1", "settlement_date": "2017-01-01",
              "consumption_kwh": 40000.0, "commodity": "elec"}},
            {{"customer_id": "G-IC-1", "settlement_date": "2017-01-01",
              "consumption_kwh": 90000.0, "commodity": "gas"}},
        ],
        report_years=["2017"],
        ic_elec_customer_ids={{"E-IC-1"}},
        ic_gas_customer_ids={{"G-IC-1"}},
    )

    walled = sorted(
        n for n in sys.modules
        if n in ("sim", "simulation") or n.startswith(("sim.", "simulation."))
    )
    print("WALLED_MODULES=" + json.dumps(walled))
    """
)


def _walled_modules_loaded_by(source: str) -> list[str]:
    """Run `source` as the impl module in a clean interpreter; report sim loads.

    THE detector, used unchanged by both the real test and its mutation.
    """
    with tempfile.TemporaryDirectory() as pkgdir:
        modname = "_knife3_step17_subject"
        with open(os.path.join(pkgdir, modname + ".py"), "w") as fh:
            fh.write(source)
        probe = _PROBE.format(repo=REPO_ROOT, pkgdir=pkgdir, modname=modname)
        proc = subprocess.run(
            [sys.executable, "-c", probe],
            cwd=pkgdir,
            capture_output=True,
            text=True,
            timeout=180,
        )
    assert proc.returncode == 0, (
        f"the probe itself failed — an unavailable check is a FAILED check, "
        f"never a skip.\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    marker = [ln for ln in proc.stdout.splitlines() if ln.startswith("WALLED_MODULES=")]
    assert len(marker) == 1, f"probe produced no verdict line:\n{proc.stdout}"
    return json.loads(marker[0].split("=", 1)[1])


def test_building_the_statutory_position_loads_no_world_module():
    with open(IMPL_PATH) as fh:
        real_source = fh.read()
    assert _walled_modules_loaded_by(real_source) == []


def test_mutation_a_lazy_world_import_is_caught_by_the_same_detector():
    """Perform the defect on a copy of the real source, same detector."""
    with open(IMPL_PATH) as fh:
        mutated = fh.read()
    anchor = "    all_years = sorted(report_years)"
    assert anchor in mutated, "anchor moved — this mutation is no longer the defect"
    mutated = mutated.replace(
        anchor,
        "    import simulation.reputation_index  # noqa: F401  <-- the defect\n" + anchor,
        1,
    )
    loaded = _walled_modules_loaded_by(mutated)
    assert "simulation.reputation_index" in loaded, (
        "control 1 did not fire on a lazy world import — it cannot fail, so it "
        "is not evidence"
    )


# ---------------------------------------------------------------------------
# CONTROL 2 — behaviour identity against the PRE-CUT sequence, transcribed from
# simulation/run_phase2b.py as it stood before step 17 (git 57cb9d872), NOT from
# the module under test.
# ---------------------------------------------------------------------------


def _pre_cut_summaries(
    all_records: list[dict],
    _all_years: list[str],
    ELEC_CUSTOMERS: list[dict],
    GAS_CUSTOMERS: list[dict],
) -> tuple[dict, dict, dict]:
    # Phase OG: Renewable Obligation (RO) cost.
    _roc_ledger = ROCLedger()
    _elec_mwh_by_year: dict = defaultdict(float)
    for _rec in all_records:
        if _rec.get("commodity", "elec") != "gas":
            _yr_roc = _rec.get("settlement_date", "")[:4]
            if _yr_roc:
                _elec_mwh_by_year[_yr_roc] += _rec.get("consumption_kwh", 0.0) / 1000.0
    _roc_per_year = {}
    for _yr_roc in sorted(_all_years):
        _mwh = _elec_mwh_by_year.get(_yr_roc, 0.0)
        _oblig = _roc_ledger.create_obligation(int(_yr_roc), round(_mwh, 1))
        _price = _ROC_BUY_OUT_PRICE_GBP.get(int(_yr_roc), 50.0)
        _level = _ROC_OBLIGATION_LEVEL.get(int(_yr_roc), 0.35)
        _roc_per_year[_yr_roc] = {
            "elec_mwh": round(_mwh, 1),
            "rocs_required": round(_oblig.rocs_required, 1),
            "obligation_level": _level,
            "buy_out_price_gbp": _price,
            "buy_out_cost_gbp": round(_oblig.rocs_required * _price, 0),
        }
    roc_summary = {
        "total_buy_out_cost_gbp": round(
            sum(v["buy_out_cost_gbp"] for v in _roc_per_year.values()), 0
        ),
        "per_year": _roc_per_year,
    }

    # Phase OH: FiT Levelisation Levy.
    _fit_book = FITBook()
    _fit_per_year = {}
    for _yr_fit in sorted(_all_years):
        _mwh_fit = _elec_mwh_by_year.get(_yr_fit, 0.0)
        _levy_rate = _FIT_LEVELISATION_RATE_PER_MWH.get(int(_yr_fit), 0.0)
        _levy_gbp = _fit_book.levelisation_charge_gbp(int(_yr_fit), _mwh_fit * 1000.0)
        _fit_per_year[_yr_fit] = {
            "elec_mwh": round(_mwh_fit, 1),
            "levy_rate_gbp_per_mwh": _levy_rate,
            "fit_levy_gbp": round(_levy_gbp, 2),
        }
    fit_summary = {
        "total_fit_levy_gbp": round(
            sum(v["fit_levy_gbp"] for v in _fit_per_year.values()), 2
        ),
        "per_year": _fit_per_year,
    }

    # Phase OI: Climate Change Levy (CCL) -- I&C elec + gas pass-through.
    _ccl_ledger = CCLLedger()
    _ic_ids_ = {c["customer_id"] for c in ELEC_CUSTOMERS if c.get("segment") == "I&C"}
    _ic_gas_ids = {c["customer_id"] for c in GAS_CUSTOMERS if c.get("segment") == "I&C"}
    _ccl_elec_by_year: dict = defaultdict(float)
    _ccl_gas_by_year: dict = defaultdict(float)
    for _rec in all_records:
        _yr_ccl = _rec.get("settlement_date", "")[:4]
        if not _yr_ccl:
            continue
        _cid_ccl = _rec.get("customer_id", "")
        if _cid_ccl in _ic_ids_ and _rec.get("commodity", "elec") != "gas":
            _ccl_elec_by_year[_yr_ccl] += _rec.get("consumption_kwh", 0.0)
        elif _cid_ccl in _ic_gas_ids and _rec.get("commodity") == "gas":
            _ccl_gas_by_year[_yr_ccl] += _rec.get("consumption_kwh", 0.0)
    _ccl_per_year = {}
    for _yr_ccl in sorted(_all_years):
        _yr_int_ccl = int(_yr_ccl)
        _elec_kwh = _ccl_elec_by_year.get(_yr_ccl, 0.0)
        _gas_kwh = _ccl_gas_by_year.get(_yr_ccl, 0.0)
        _elec_rate = _ccl_ledger.rate_for_year(_yr_int_ccl, CCLFuel.ELECTRICITY)
        _gas_rate = _ccl_ledger.rate_for_year(_yr_int_ccl, CCLFuel.GAS)
        _elec_ccl = round(_elec_kwh * _elec_rate / 100.0, 2)
        _gas_ccl = round(_gas_kwh * _gas_rate / 100.0, 2)
        _ccl_per_year[_yr_ccl] = {
            "elec_kwh": round(_elec_kwh, 0),
            "gas_kwh": round(_gas_kwh, 0),
            "elec_rate_p_per_kwh": _elec_rate,
            "gas_rate_p_per_kwh": _gas_rate,
            "ccl_elec_gbp": _elec_ccl,
            "ccl_gas_gbp": _gas_ccl,
            "ccl_total_gbp": round(_elec_ccl + _gas_ccl, 2),
        }
    ccl_summary = {
        "total_ccl_gbp": round(sum(v["ccl_total_gbp"] for v in _ccl_per_year.values()), 2),
        "per_year": _ccl_per_year,
    }
    return roc_summary, fit_summary, ccl_summary


def test_all_three_summaries_are_identical_to_the_pre_cut_inlined_sequence():
    roc, fit, ccl = _pre_cut_summaries(
        _settled_records(), FIXTURE_YEARS, _elec_customers(), _gas_customers()
    )
    built = _build()
    assert built.roc_summary == roc
    assert built.fit_summary == fit
    assert built.ccl_summary == ccl


def test_mutation_a_dropped_accumulator_breaks_the_identity():
    """The identity control fires when the moved code stops matching."""
    records = _settled_records()
    # The defect: the RO accumulator picks up gas volume too — one dropped
    # commodity filter, the shape of a transcription slip.
    mwh = defaultdict(float)
    for rec in records:
        yr = rec.get("settlement_date", "")[:4]
        if yr:
            mwh[yr] += rec.get("consumption_kwh", 0.0) / 1000.0
    ledger = ROCLedger()
    mutated_total = round(
        sum(
            round(
                ledger.create_obligation(int(y), round(mwh.get(y, 0.0), 1)).rocs_required
                * _ROC_BUY_OUT_PRICE_GBP.get(int(y), 50.0),
                0,
            )
            for y in sorted(FIXTURE_YEARS)
        ),
        0,
    )
    real_total = _build().roc_summary["total_buy_out_cost_gbp"]
    assert mutated_total != real_total, (
        "dropping the commodity filter did not move the RO figure — control 2 "
        "could not fail on this fixture"
    )


# ---------------------------------------------------------------------------
# CONTROL 3 — the call site hands the elec set to the elec parameter.
# ---------------------------------------------------------------------------

_CALL_NAME = "build_statutory_obligations"
_EXPECTED_ROSTER = {
    "ic_elec_customer_ids": "ELEC_CUSTOMERS",
    "ic_gas_customer_ids": "GAS_CUSTOMERS",
}


def _call_site_findings(source: str) -> tuple[list[str], int]:
    """Findings about the seam's call site. Returns (findings, calls_examined).

    THE checker, used unchanged by both the real test and its mutation. The
    second element is the vacuity guard's subject: zero calls examined means
    every finding list is empty for free.
    """
    findings: list[str] = []
    examined = 0
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
        if name != _CALL_NAME:
            continue
        examined += 1
        kwargs = {kw.arg: kw.value for kw in node.keywords if kw.arg}
        for param, expected_roster in _EXPECTED_ROSTER.items():
            if param not in kwargs:
                findings.append(f"{param} is not passed by keyword")
                continue
            expr = ast.dump(kwargs[param])
            if f"id='{expected_roster}'" not in expr:
                findings.append(
                    f"{param} does not read {expected_roster} — the rosters may "
                    "have been swapped"
                )
            if "'I&C'" not in expr:
                findings.append(
                    f"{param} does not filter on segment == 'I&C' — it would "
                    "carry the whole book"
                )
    return findings, examined


def test_the_call_site_hands_each_fuels_ic_roster_to_its_own_parameter():
    with open(RUN_MODULE_PATH) as fh:
        source = fh.read()
    findings, examined = _call_site_findings(source)
    assert examined == 1, (
        f"expected exactly one {_CALL_NAME} call site in run_phase2b.py, found "
        f"{examined} — with zero, this control passes for free"
    )
    assert findings == [], findings


def test_mutation_swapping_the_two_rosters_is_caught():
    with open(RUN_MODULE_PATH) as fh:
        source = fh.read()
    mutated = source.replace(
        "ic_elec_customer_ids={\n            c[\"customer_id\"] for c in ELEC_CUSTOMERS",
        "ic_elec_customer_ids={\n            c[\"customer_id\"] for c in GAS_CUSTOMERS",
        1,
    )
    assert mutated != source, "the swap mutation did not apply — anchor moved"
    findings, examined = _call_site_findings(mutated)
    assert examined == 1
    assert any("swapped" in f for f in findings), (
        f"control 3 did not fire on a swapped roster: {findings}"
    )


def test_mutation_dropping_the_ic_filter_is_caught():
    with open(RUN_MODULE_PATH) as fh:
        source = fh.read()
    mutated = source.replace(
        "c[\"customer_id\"] for c in GAS_CUSTOMERS if c.get(\"segment\") == \"I&C\"",
        "c[\"customer_id\"] for c in GAS_CUSTOMERS",
        1,
    )
    assert mutated != source, "the filter mutation did not apply — anchor moved"
    findings, examined = _call_site_findings(mutated)
    assert examined == 1
    assert any("I&C" in f for f in findings), (
        f"control 3 did not fire on a dropped segment filter: {findings}"
    )
