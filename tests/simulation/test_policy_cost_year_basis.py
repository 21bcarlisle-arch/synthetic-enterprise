"""Every year-keyed rate table's reader must derive its key on the table's own basis.

Class control for the defect found 2026-08-13 (R10: the CLASS fails automatically, not
the instance). `get_electricity_network_cost_per_mwh` keyed `_NETWORK_COST_RESI_SME_BY_YEAR`
and `_DUOS_IC_BY_YEAR` on the calendar year while both tables state an Apr-Mar charging
year, so every Jan-Mar date was charged the FOLLOWING charging year's rate — forward-looking,
and worth £62.4k over the 2016-2025 run (31% of 2022's network line alone: Jan-Mar 2022 paid
the post-BSUoS-reform rate that commenced in April).

The naive version of this control — "every reader must call `_ro_oy_start_year`" — would be
WRONG. Four tables here (CfD interim levy, mutualization levy, both standing charges) are
genuinely published per calendar year, and their readers are correct to key them that way.
So the subject is not "same helper everywhere"; it is "reader agrees with the table's OWN
declared basis". That declaration is `policy_costs.YEAR_KEY_BASIS`.

Three independent legs, so that neither adding a table nor mis-declaring one is silent:
  (a) census      — every year-keyed table in the module is registered.
  (b) behavioural — each reader's OBSERVED output at a January date matches its declared
                    basis. January is the discriminating probe: under "apr_mar" the key is
                    the prior year, under "calendar" it is the date's own year.
  (c) documentary — a table whose value comments carry "YYYY/YY" charging years cannot be
                    declared "calendar". This leg reads the source comments, so it does not
                    depend on the registry it is checking.
"""

import re
from pathlib import Path

import pytest

from simulation import policy_costs
from simulation.policy_costs import YEAR_KEY_BASIS, year_key_for_basis

_AQ_KWH = 10_000.0

# table name -> (reader, kwargs, rate -> expected reader output, earliest usable probe year)
_READERS: dict[str, tuple] = {
    "_RO_COST_BY_OY_START": (policy_costs.get_ro_cost_per_mwh, {}, lambda r: r, None),
    "_CFD_LEVY_BY_YEAR": (policy_costs.get_cfd_levy_per_mwh, {}, lambda r: r, None),
    "_CCL_ELECTRICITY_RATE_BY_YEAR": (
        policy_costs.get_ccl_per_mwh, {"segment": "SME"}, lambda r: r, None,
    ),
    "_NETWORK_COST_RESI_SME_BY_YEAR": (
        policy_costs.get_electricity_network_cost_per_mwh, {"segment": "resi"}, lambda r: r, None,
    ),
    "_DUOS_IC_BY_YEAR": (
        policy_costs.get_electricity_network_cost_per_mwh, {"segment": "I&C"}, lambda r: r, None,
    ),
    "_CM_LEVY_BY_YEAR": (policy_costs.get_cm_levy_per_mwh, {}, lambda r: r, None),
    "_FIT_LEVY_BY_YEAR": (policy_costs.get_fit_levy_per_mwh, {}, lambda r: r, None),
    "_MUTUALIZATION_LEVY_BY_YEAR": (
        policy_costs.get_mutualization_levy_per_mwh, {}, lambda r: r, None,
    ),
    "_GAS_CCL_RATE_BY_YEAR": (
        policy_costs.get_gas_ccl_per_mwh, {"segment": "SME"}, lambda r: r, None,
    ),
    "_GAS_NETWORK_COST_BY_YEAR": (
        policy_costs.get_gas_network_cost_per_mwh, {}, lambda r: r, None,
    ),
    # GGL is a per-meter annual rate normalised by AQ, and returns 0 before 30 Nov 2021.
    "_GGL_RATE_GBP_PER_METER_YEAR": (
        policy_costs.get_ggl_per_mwh, {"aq_kwh": _AQ_KWH}, lambda r: r / (_AQ_KWH / 1000.0), 2022,
    ),
    # Standing charges are held in pence/day and returned in £/day.
    "_ELEC_SC_PENCE_PER_DAY_BY_YEAR": (
        policy_costs.get_electricity_standing_charge_per_day,
        {"segment": "resi"}, lambda r: r / 100.0, None,
    ),
    "_GAS_SC_PENCE_PER_DAY_BY_YEAR": (
        policy_costs.get_gas_standing_charge_per_day,
        {"segment": "resi"}, lambda r: r / 100.0, None,
    ),
}


def _year_keyed_tables() -> dict[str, dict]:
    """Every module-level table keyed by year, discovered from the live module."""
    found = {}
    for name, value in vars(policy_costs).items():
        if not isinstance(value, dict) or not value:
            continue
        if all(isinstance(k, int) and 1990 <= k <= 2100 for k in value):
            found[name] = value
    return found


def _discriminating_year(table: dict, min_year: int | None) -> int:
    """A year Y where table[Y] != table[Y-1], so a January probe separates the two bases."""
    for year in sorted(table):
        if year - 1 not in table or (min_year is not None and year < min_year):
            continue
        if table[year] != table[year - 1]:
            return year
    pytest.fail("no adjacent differing years: a January probe cannot discriminate the basis")


# ── (a) census ───────────────────────────────────────────────────────────────

def test_every_year_keyed_table_declares_its_basis():
    """Add a rate table without declaring its basis and this fails — the fail-closed leg."""
    discovered = set(_year_keyed_tables())
    assert discovered, "discovery found no year-keyed tables — the census would pass vacuously"
    undeclared = discovered - set(YEAR_KEY_BASIS)
    assert not undeclared, (
        f"year-keyed table(s) with no declared basis: {sorted(undeclared)}. "
        "Add them to policy_costs.YEAR_KEY_BASIS."
    )
    stale = set(YEAR_KEY_BASIS) - discovered
    assert not stale, f"YEAR_KEY_BASIS names table(s) that no longer exist: {sorted(stale)}"


def test_every_declared_table_has_a_reader_probe():
    """A table with no probe would silently skip leg (b) — that is the fail-open shape."""
    unprobed = set(YEAR_KEY_BASIS) - set(_READERS)
    assert not unprobed, f"table(s) declared but never behaviourally probed: {sorted(unprobed)}"


def test_declared_bases_are_known_values():
    unknown = {n: b for n, b in YEAR_KEY_BASIS.items() if b not in ("apr_mar", "calendar")}
    assert not unknown, f"unknown basis value(s): {unknown}"


# ── (b) behavioural: the reader's observed key derivation ────────────────────

@pytest.mark.parametrize("table_name", sorted(_READERS))
def test_reader_keys_january_on_its_declared_basis(table_name):
    """January is where the two bases disagree — the probe that caught the network defect."""
    table = _year_keyed_tables()[table_name]
    reader, kwargs, to_output, min_year = _READERS[table_name]
    basis = YEAR_KEY_BASIS[table_name]

    year = _discriminating_year(table, min_year)
    date_str = f"{year}-01-15"
    expected_key = year_key_for_basis(date_str, basis)
    expected = to_output(table[expected_key])
    wrong_basis = "calendar" if basis == "apr_mar" else "apr_mar"
    wrong = to_output(table[year_key_for_basis(date_str, wrong_basis)])

    assert expected != pytest.approx(wrong), (
        f"{table_name}: probe year {year} is not discriminating"
    )
    assert reader(date_str, **kwargs) == pytest.approx(expected), (
        f"{table_name} is declared '{basis}' but its reader disagrees at {date_str}. "
        f"Expected {expected} (key {expected_key}); a '{wrong_basis}'-keyed reader gives {wrong}."
    )


@pytest.mark.parametrize("table_name", sorted(_READERS))
def test_reader_agrees_with_its_table_mid_year(table_name):
    """April: both bases agree, so this guards the lookup itself rather than the key."""
    table = _year_keyed_tables()[table_name]
    reader, kwargs, to_output, min_year = _READERS[table_name]
    year = _discriminating_year(table, min_year)
    date_str = f"{year}-06-15"
    assert reader(date_str, **kwargs) == pytest.approx(to_output(table[year]))


# ── (c) documentary: the table's own comments ────────────────────────────────

_SLASH_YEAR = re.compile(r"\b20\d{2}/\d{2}\b")

_ROOT = Path(__file__).resolve().parents[2]

# Tables that are no longer dict literals here: they LOAD from the regulation commons, so their
# documentary evidence is the artefact's own basis statement rather than a row comment.
#
# WHY A REGISTER AND NOT A SKIP (2026-09-07, when `_CM_LEVY_BY_YEAR` became a load). The obvious
# repair — return early when the source block is absent — retires leg (c) for that table
# silently, and "loaded" and "renamed out from under this control" look identical to a regex.
# So the register is RESOLVED below: the named artefact must exist, and the module must actually
# be seen loading the table. A table in `YEAR_KEY_BASIS` with neither a literal block nor an
# entry here FAILS, which is the fail-closed leg the skip would have thrown away.
_LOADED_FROM_COMMONS: dict[str, str] = {
    "_CM_LEVY_BY_YEAR":
        "docs/domain_artefact_library/regulatory/capacity_market_supplier_levy.json",
}


def _table_documentary_source(source: str, name: str) -> str:
    """The text that documents a table's charging year — its own rows, or its artefact.

    THE ANNOTATION IS MATCHED WITH `[^\\n]*?`, NOT `.*?`. Under re.S a `.*?` crosses newlines, so
    the header pattern for a name that is NO LONGER a dict literal walks down the file and pairs
    that name with the NEXT table's opening brace — which is not a miss, it is a silent
    substitution. Found 2026-09-07 the moment `_CM_LEVY_BY_YEAR` became a load: leg (c) went on
    reading a block, and the block was `_FIT_LEVY_BY_YEAR`'s. Its own mutation leg is what
    surfaced it, by not firing.
    """
    match = re.search(
        rf"^{re.escape(name)}: dict\[[^\n]*?\] = \{{$(.*?)^\}}$", source, re.M | re.S
    )
    if match:
        return match.group(1)
    artefact = _LOADED_FROM_COMMONS.get(name)
    assert artefact, (
        f"could not locate the source block for {name}, and it is not registered in "
        "_LOADED_FROM_COMMONS. Leg (c) reads a table's own documentation; a table with no "
        "documentary source is UNCHECKED, not exempt."
    )
    assert re.search(rf"^{re.escape(name)}\b.*=\s*_load", source, re.M), (
        f"{name} is registered as loaded from {artefact}, but policy_costs.py contains no "
        "load assignment for it. A register entry is a claim; this resolves it."
    )
    path = _ROOT / artefact
    assert path.exists(), (
        f"{name} is registered as loaded from {artefact}, which does not exist. An "
        "unavailable documentary source is a FAILED check, not an absent one."
    )
    return path.read_text()


def test_a_table_documenting_charging_years_is_not_declared_calendar():
    """Independent of the registry: 'YYYY/YY' in a table's rows means an Apr-Mar year.

    This is the leg that would have caught the original defect from the source alone --
    _NETWORK_COST_RESI_SME_BY_YEAR's rows read '2022/23: £66.24/MWh'.

    For a table loaded from the commons the documentary source is the ARTEFACT, which states
    its own year key ("2023 is obligation year 2023/24"). Same question, same regex, one file
    further out — see `_table_documentary_source`.
    """
    source = Path(policy_costs.__file__).read_text()
    checked = 0
    for name, basis in sorted(YEAR_KEY_BASIS.items()):
        block = _table_documentary_source(source, name)
        if not _SLASH_YEAR.search(block):
            continue
        checked += 1
        assert basis == "apr_mar", (
            f"{name} documents charging years ({_SLASH_YEAR.search(block).group()}) in its own "
            f"rows but is declared '{basis}'."
        )
    assert checked >= 3, (
        f"only {checked} table(s) carried a 'YYYY/YY' comment — this leg has gone blind"
    )


# ── (c) mutation: the resolver's three fail-closed branches actually fire ─────
#
# R15. `_LOADED_FROM_COMMONS` was added on 2026-09-07 so that a table leaving the source as a
# literal does not leave leg (c) as well. A register that lets a table out of a control is worth
# exactly what its resolution is worth, so each of the three ways that resolution can be false
# is broken here and asserted to go red.

def test_mutation_an_unregistered_non_literal_table_is_caught():
    """The fail-open shape the load introduced: no block, no register entry, no complaint.

    This is the shape the obvious repair would have had — return early when the regex misses.
    A table renamed out of the module reaches this branch too, and must fail the same way.
    """
    source = Path(policy_costs.__file__).read_text()
    with pytest.raises(AssertionError, match="UNCHECKED, not exempt"):
        _table_documentary_source(source, "_A_TABLE_NO_LONGER_IN_THIS_MODULE")


def test_mutation_a_register_entry_the_module_never_loads_is_caught(monkeypatch):
    """"Loaded from the commons" claimed for a table nothing loads pins nothing."""
    monkeypatch.setitem(
        _LOADED_FROM_COMMONS,
        "_A_TABLE_NO_LONGER_IN_THIS_MODULE",
        "docs/domain_artefact_library/regulatory/capacity_market_supplier_levy.json",
    )
    source = Path(policy_costs.__file__).read_text()
    with pytest.raises(AssertionError, match="no load assignment"):
        _table_documentary_source(source, "_A_TABLE_NO_LONGER_IN_THIS_MODULE")


def test_mutation_a_register_entry_naming_a_missing_artefact_is_caught(monkeypatch):
    """An unavailable documentary source is a FAILED check, never a skipped one."""
    monkeypatch.setitem(_LOADED_FROM_COMMONS, "_CM_LEVY_BY_YEAR", "docs/no/such/artefact.json")
    source = Path(policy_costs.__file__).read_text()
    with pytest.raises(AssertionError, match="does not exist"):
        _table_documentary_source(source, "_CM_LEVY_BY_YEAR")


# ── the instance, pinned ─────────────────────────────────────────────────────

def test_january_2022_network_charge_predates_the_bsuos_reform():
    """The defect's own worst case: Jan-Mar 2022 must not pay the Apr-2022 reform rate."""
    assert policy_costs.get_electricity_network_cost_per_mwh("2022-01-05") == pytest.approx(49.0)
    assert policy_costs.get_electricity_network_cost_per_mwh("2022-04-05") == pytest.approx(66.0)
    assert policy_costs.get_electricity_network_cost_per_mwh("2021-12-01") == pytest.approx(49.0)
