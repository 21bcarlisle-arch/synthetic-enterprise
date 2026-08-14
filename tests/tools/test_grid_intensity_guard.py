"""R15 proof for `tools/grid_intensity_guard.py` -- the one-annual-grid-intensity-series control.

The guard is the R10 class closure for
`WORKER_FINDING_THREE_LIVE_GRID_INTENSITY_SERIES_DISAGREE_BY_HALF_2026-08-14.md` (BLOCKING,
`F_risk_compliance`). R15: it counts as evidence only if a mutation proves it fires on its own
named defect, and only if it is shown NOT to fire on the near misses -- a control that always
fires is as useless as one that never does.

THE STRONGEST TEST HERE IS NOT SYNTHETIC. `test_it_catches_all_three_real_deleted_series` runs the
arms over the three tables as they actually stood in the tree before this repair, one per arm,
including the one that hid as a local inside a function body. That is the defect, not a model of it.
"""

from __future__ import annotations

import shutil

import pytest

from tools import grid_intensity_guard as guard

OWNER_STUB = (
    "UK_GRID_FUEL_MIX = {}\n"
    "def grid_intensity_g_co2e_per_kwh(year):\n"
    "    return 0.0\n"
)

# Verbatim from `company/billing/carbon_footprint.py:14` before 2026-08-14.
REAL_FOOTPRINT_TABLE = """
_ELECTRICITY_INTENSITY_G_CO2E_PER_KWH = {
    2016: 266,
    2017: 246,
    2018: 233,
    2019: 214,
    2020: 181,
    2021: 190,
    2022: 165,
    2023: 141,
    2024: 126,
    2025: 115,
}
"""

# Verbatim from `company/sustainability/carbon_intensity_register.py:57` before 2026-08-14.
REAL_REGISTER_TABLE = """
_GRID_AVERAGE_INTENSITY = {
    2016: 350.0,
    2017: 312.0,
    2018: 283.0,
    2019: 256.0,
    2020: 228.0,
    2021: 233.0,
    2022: 210.0,
    2023: 196.0,
    2024: 181.0,
    2025: 165.0,
}
"""

# Shape-verbatim from `saas/reporting/annual_report.py:5414` before 2026-08-14 -- note the indent:
# it was a LOCAL inside `_section_carbon_emissions`, which is why the guard walks function bodies.
REAL_PUBLISHED_TABLE = """
def _section_carbon_emissions(data):
    from company.regulatory.carbon_emissions import FuelMixRecord
    _UK_FUEL_MIX = {
        2016: FuelMixRecord(2016, coal_pct=9.0, gas_pct=42.0, nuclear_pct=21.0, wind_pct=11.0, solar_pct=3.0, hydro_pct=2.0, biomass_pct=8.0, imports_pct=4.0),
        2017: FuelMixRecord(2017, coal_pct=7.0, gas_pct=40.0, nuclear_pct=21.0, wind_pct=15.0, solar_pct=3.0, hydro_pct=2.0, biomass_pct=8.0, imports_pct=4.0),
        2018: FuelMixRecord(2018, coal_pct=5.0, gas_pct=39.0, nuclear_pct=20.0, wind_pct=17.0, solar_pct=3.0, hydro_pct=2.0, biomass_pct=9.0, imports_pct=5.0),
    }
    return _UK_FUEL_MIX
"""


def _make_tree(tmp_path, extra=None, owner_source=OWNER_STUB, with_owner=True):
    """A minimal two-package tree: the owner, plus whatever the test plants beside it."""
    regulatory = tmp_path / "company" / "regulatory"
    regulatory.mkdir(parents=True)
    (tmp_path / "saas").mkdir()
    (tmp_path / "saas" / "__init__.py").write_text("")
    if with_owner:
        (regulatory / "carbon_emissions.py").write_text(owner_source)
    else:
        (regulatory / "placeholder.py").write_text("")
    for rel, source in (extra or {}).items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source)
    return tmp_path


# --------------------------------------------------------------------------------------------
# The live tree
# --------------------------------------------------------------------------------------------

def test_the_real_tree_carries_exactly_one_series():
    """The whole point. company/ and saas/ declare no second annual grid-intensity series."""
    violations = guard.scan_tree()
    assert violations == [], "\n".join(v.render() for v in violations)


def test_the_owner_still_owns_it():
    """Reading the guard's own subject. A moved owner is rc=2, not a quiet pass."""
    from company.regulatory import carbon_emissions

    assert (guard.ROOT / guard.OWNER_REL_PATH).is_file()
    assert carbon_emissions.UK_GRID_FUEL_MIX, "owner declares an empty mix"
    assert callable(carbon_emissions.grid_intensity_g_co2e_per_kwh)


# --------------------------------------------------------------------------------------------
# The ratchet -- it may only shrink, and a stale entry is a failure
# --------------------------------------------------------------------------------------------

def test_the_ratchet_has_no_stale_entries():
    """Removing the instance FORCES removing the entry. Without this, a fixed instance leaves a
    permanent hole that the next copy can be dropped into for free."""
    live = {v.key for v in guard.scan_tree(include_known=True)}
    stale = sorted(set(guard.KNOWN_SECOND_SERIES) - live)
    assert not stale, (
        f"ratchet entries that no longer violate -- delete them from KNOWN_SECOND_SERIES: {stale}"
    )


def test_the_ratchet_is_exactly_the_one_known_instance():
    """A ratchet that can grow silently is the fail-open shape. Growing it must red HERE first."""
    assert set(guard.KNOWN_SECOND_SERIES) == {
        "company/billing/fuel_mix.py::_FUEL_MIX_BY_YEAR",
    }


def test_the_ratcheted_instance_is_still_detected_by_an_arm():
    """The exemption is a decision about a KNOWN violation, not a blind spot in the arms."""
    everything = guard.scan_tree(include_known=True)
    known = [v for v in everything if v.key == "company/billing/fuel_mix.py::_FUEL_MIX_BY_YEAR"]
    assert len(known) == 1, [v.render() for v in everything]
    assert known[0].arm.startswith("ARM 3")


def test_a_ratchet_key_ignores_the_line_number(tmp_path):
    """Keyed on path+name. A key carrying a line number expires on the first edit above it."""
    tree = _make_tree(tmp_path, {
        "company/x.py": "\n\n\n_CO2_INTENSITY = {2020: 1.0, 2021: 2.0, 2022: 3.0}\n",
    })
    violation = guard.scan_tree(root=tree)[0]
    assert violation.key == "company/x.py::_CO2_INTENSITY"
    assert str(violation.line) not in violation.key


# --------------------------------------------------------------------------------------------
# R15 -- it fires (mutation), on the REAL defect
# --------------------------------------------------------------------------------------------

def test_arm_three_catches_a_year_keyed_table_of_per_bucket_numbers(tmp_path):
    """The shape arms 1 and 2 both missed: `{2016: {"renewable": 24.6, "gas": 42.6}}`."""
    tree = _make_tree(tmp_path, {
        "saas/reporting/mix.py":
            "_FUEL_MIX_BY_YEAR = {\n"
            "    2016: {'renewable': 24.6, 'nuclear': 20.9, 'gas': 42.6},\n"
            "    2017: {'renewable': 29.3, 'nuclear': 20.4, 'gas': 40.7},\n"
            "    2018: {'renewable': 33.0, 'nuclear': 19.3, 'gas': 39.4},\n"
            "}\n",
    })
    violations = guard.scan_tree(root=tree)
    assert len(violations) == 1
    assert violations[0].arm.startswith("ARM 3")


def test_it_catches_all_three_real_deleted_series(tmp_path):
    """The three tables exactly as they stood before the repair: three hits, both arms used."""
    tree = _make_tree(tmp_path, {
        "company/billing/carbon_footprint.py": REAL_FOOTPRINT_TABLE,
        "company/sustainability/carbon_intensity_register.py": REAL_REGISTER_TABLE,
        "saas/reporting/annual_report.py": REAL_PUBLISHED_TABLE,
    })
    violations = guard.scan_tree(root=tree)
    names = sorted(v.name for v in violations)
    assert names == [
        "_ELECTRICITY_INTENSITY_G_CO2E_PER_KWH",
        "_GRID_AVERAGE_INTENSITY",
        "_UK_FUEL_MIX",
    ], [v.render() for v in violations]
    arms = {v.name: v.arm for v in violations}
    assert arms["_UK_FUEL_MIX"].startswith("ARM 2"), "the function-body copy needs the shape arm"
    assert arms["_GRID_AVERAGE_INTENSITY"].startswith("ARM 1")


def test_a_second_series_under_a_new_name_is_still_caught(tmp_path):
    """Arm 1 is keyed on the QUANTITY word, not on the exact deleted identifier."""
    tree = _make_tree(tmp_path, {
        "saas/reporting/whatever.py":
            "ANNUAL_CARBON_INTENSITY = {2030: 150.0, 2031: 140.0, 2032: 130.0}\n",
    })
    violations = guard.scan_tree(root=tree)
    assert len(violations) == 1
    assert violations[0].name == "ANNUAL_CARBON_INTENSITY"


def test_a_series_hidden_in_a_function_body_is_caught(tmp_path):
    """Module-scope-only scanning is exactly how the published copy stayed invisible."""
    tree = _make_tree(tmp_path, {
        "company/reporting/section.py":
            "def render():\n"
            "    _LOCAL_CO2_INTENSITY = {2021: 233.0, 2022: 210.0, 2023: 196.0}\n"
            "    return _LOCAL_CO2_INTENSITY\n",
    })
    violations = guard.scan_tree(root=tree)
    assert len(violations) == 1
    assert violations[0].line == 2


def test_main_returns_one_when_a_second_series_exists(monkeypatch, tmp_path):
    tree = _make_tree(tmp_path, {
        "company/x.py": "GRID_INTENSITY_BY_YEAR = {2020: 228.0, 2021: 233.0, 2022: 210.0}\n",
    })
    monkeypatch.setattr(guard, "ROOT", tree)
    assert guard.main([]) == 1


# --------------------------------------------------------------------------------------------
# R15 -- it does NOT fire on the near misses (a control that always fires proves nothing)
# --------------------------------------------------------------------------------------------

def test_the_owner_alone_is_clean(tmp_path):
    assert guard.scan_tree(root=_make_tree(tmp_path)) == []


def test_a_year_keyed_table_that_is_not_about_carbon_is_left_alone(tmp_path):
    """Year-keyed numeric dicts are everywhere in this repo. Only intensity ones are the subject."""
    tree = _make_tree(tmp_path, {
        "saas/pricing/tariffs.py":
            "_STANDING_CHARGE_BY_YEAR = {2020: 22.5, 2021: 24.1, 2022: 45.3, 2023: 53.0}\n"
            "_CUSTOMER_COUNT = {2020: 1200, 2021: 4300, 2022: 9100}\n",
    })
    assert guard.scan_tree(root=tree) == []


def test_two_years_is_not_a_series(tmp_path):
    tree = _make_tree(tmp_path, {
        "company/x.py": "_CO2_INTENSITY = {2024: 196.0, 2025: 175.0}\n",
    })
    assert guard.scan_tree(root=tree) == []


def test_a_carbon_dict_keyed_by_something_other_than_years_is_left_alone(tmp_path):
    """Per-fuel factor tables are a DIFFERENT class, named as out of scope in the guard docstring."""
    tree = _make_tree(tmp_path, {
        "company/x.py":
            "_CARBON_INTENSITY = {'gas': 394.0, 'coal': 820.0, 'wind': 11.0, 'nuclear': 12.0}\n",
    })
    assert guard.scan_tree(root=tree) == []


def test_the_scanned_packages_exclude_the_world_side(tmp_path):
    """sim/ carries generation factors as world physics; reading them from company/ is a breach."""
    assert "sim" not in guard.SCANNED_PACKAGES
    assert "simulation" not in guard.SCANNED_PACKAGES
    tree = _make_tree(tmp_path)
    (tree / "sim").mkdir()
    (tree / "sim" / "merit.py").write_text(
        "EF_GAS_TCO2_PER_MWH_E_BY_YEAR = {2020: 0.36, 2021: 0.37, 2022: 0.38}\n"
    )
    assert guard.scan_tree(root=tree) == []


# --------------------------------------------------------------------------------------------
# R15 killers 2 and 3 -- FAIL-OPEN and FAIL-SILENT. Losing the subject is rc=2, never rc=0.
# --------------------------------------------------------------------------------------------

def test_a_missing_owner_is_a_coverage_hole_not_a_pass(tmp_path):
    tree = _make_tree(tmp_path, with_owner=False)
    with pytest.raises(guard.CoverageError, match="missing"):
        guard.scan_tree(root=tree)


def test_an_owner_that_stopped_declaring_the_series_is_a_coverage_hole(tmp_path):
    tree = _make_tree(tmp_path, owner_source="# the table moved somewhere else\n")
    with pytest.raises(guard.CoverageError, match="no longer declares"):
        guard.scan_tree(root=tree)


def test_a_missing_scanned_package_is_a_coverage_hole(tmp_path):
    tree = _make_tree(tmp_path)
    shutil.rmtree(tree / "saas")
    with pytest.raises(guard.CoverageError, match="does not exist"):
        guard.scan_tree(root=tree)


def test_an_unparseable_module_is_a_coverage_hole(tmp_path):
    tree = _make_tree(tmp_path, {"company/broken.py": "def (:\n"})
    with pytest.raises(guard.CoverageError, match="does not parse"):
        guard.scan_tree(root=tree)


def test_main_returns_two_on_a_coverage_hole(monkeypatch, tmp_path):
    tree = _make_tree(tmp_path, with_owner=False)
    monkeypatch.setattr(guard, "ROOT", tree)
    assert guard.main([]) == 2


def test_main_returns_zero_on_a_clean_tree(monkeypatch, tmp_path):
    monkeypatch.setattr(guard, "ROOT", _make_tree(tmp_path))
    assert guard.main([]) == 0
