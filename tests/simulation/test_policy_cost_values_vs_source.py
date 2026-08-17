"""A rate constant must EQUAL the publication it cites, not merely name one.

CLASS CONTROL (R10) for the defect found 2026-08-17
(WORKER_FINDING_THE_ELECTRICITY_LEVY_TABLE_DIVERGES_FROM_THE_STATUTE_ITS_GAS_TWIN_MATCHES).
`_CCL_ELECTRICITY_RATE_BY_YEAR` cited "HMRC Climate Change Levy rates tables" and was
£43,074.89 (9.4% of the published electricity CCL line) away from them on 9 of 11 years,
always understating, while `_GAS_CCL_RATE_BY_YEAR` — transcribed from the SAME statutory rows,
the same Acts, the same sections — was exact on 10 of 10.

WHY THE EXISTING CONTROLS COULD NOT CATCH IT, and why this file is not a fourth leg of them:

  * `test_policy_cost_year_basis.py` checks each table's YEAR BASIS against its own comment.
    Right subject for its own defect; says nothing about values.
  * `test_policy_cost_coverage.py` checks that a rate served from outside its window SAYS SO.
    Also about the instrument, not the numbers.
  * The scope brief's B5 — "every constant traces to a published artefact" — scored 12/13 and
    PASSED this table. B5 as run asked *does a comment NAME a publication*; B5 as meant asks
    *is the constant the published number*. A census of citations is FAIL-OPEN on a
    mis-transcribed constant by construction: it reads the same comment the author wrote, so
    the only defect available to it is a MISSING citation, never a FALSE one.

THE INDEPENDENCE THAT MAKES THIS NOT A TAUTOLOGY (R15). The pinned figures live in the
regulation commons — `docs/domain_artefact_library/regulatory/ccl_main_rates.json` — in the
STATUTE'S OWN UNIT (GBP per kWh), with the legislation.gov.uk / gov.uk URL per year. The
commons never carries the model's GBP/MWh figure. This module performs the conversion, so the
unit convention (p/kWh x 10) is itself under test rather than assumed. Had the commons carried
GBP/MWh, the checked value would have been derived from the source it checks — the exact
tautology shape R15 names, and the shape that let a citation census score this table green.

Provenance is load-bearing. Only `primary` (fetched from the publisher this pass) and
`bracketed` (both adjacent years primary AND equal) entries are asserted as equalities.
`recalled` entries are EXCLUDED and counted against a ratchet, so an unverified year is
visible rather than silently trusted — an unavailable input served as a plausible value is the
fail-open shape, and the honest move is to declare it.

Five independent legs, so that neither a drifting constant, a drifting pin, a new table, nor a
quietly emptied register is silent:
  (a) equality   — every pinned primary/bracketed year converts to the tabulated figure.
  (b) coverage   — every in-window year of a verified table HAS a pin (any provenance).
  (c) scope      — every table in `YEAR_KEY_BASIS` is classified verified or unverified-with-
                   reason. A new table cannot be silently unchecked.
  (d) ratchets   — the unverified-table count and the recalled-pin count can only go DOWN.
  (e) mutation   — R15: each leg above is proven to FIRE on its own named defect. A control
                   that cannot fail is worse than none.

NOT CLOSED BY THIS FILE, and stated so the green is not read as wider than it is: 11 of the 13
year-keyed tables have never been source-checked at all, including the two largest lines by
money (electricity network £869k, RO £1.72M). They are declared in `_UNVERIFIED_TABLES` with
reasons and ratcheted, which makes the gap visible and shrinking; it does not make it closed.
The stronger move — the model LOADING these rates from the commons instead of duplicating them,
so drift becomes impossible rather than merely detected — is EP14's own adapter work, where an
ingest adapter makes it nearly free.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from simulation import policy_costs
from simulation.policy_costs import YEAR_KEY_BASIS

ROOT = Path(__file__).resolve().parents[2]
COMMONS = ROOT / "docs" / "domain_artefact_library" / "regulatory" / "ccl_main_rates.json"

# Provenances whose figures this control asserts as equalities. `recalled` is deliberately absent.
_ASSERTED = ("primary", "bracketed")

# module table name -> the commons commodity whose published rate it must equal
_VERIFIED_TABLES: dict[str, str] = {
    "_CCL_ELECTRICITY_RATE_BY_YEAR": "electricity",
    "_GAS_CCL_RATE_BY_YEAR": "gas",
}

# Tables with NO values-vs-source pin yet, each with the reason. Declared rather than omitted:
# an unchecked table that is merely absent is indistinguishable from a checked one.
# THE RATCHET BELOW ONLY MOVES DOWN — pin a table, delete its line here.
_UNVERIFIED_TABLES: dict[str, str] = {
    "_RO_COST_BY_OY_START": "£1.72M, the largest line. Ofgem publishes the RO buy-out price and "
                            "obligation level separately; the tabulated £/MWh is a DERIVED product "
                            "of both, so pinning it needs the two inputs pinned, not one figure.",
    "_CFD_LEVY_BY_YEAR": "LCCC/EMRS publish the interim levy rate per quarter; the table is an "
                         "annual average, so the pin must carry the averaging as a stated reading.",
    "_NETWORK_COST_RESI_SME_BY_YEAR": "£869k. DUoS+TNUoS combined across 14 DNO regions; the "
                                      "tabulated figure is a national blend and no single "
                                      "publication states it.",
    "_DUOS_IC_BY_YEAR": "the I&C-connected variant of the above: HV/EHV DUoS tariffs are published "
                        "per DNO with red/amber/green time bands, so no published figure has the "
                        "shape of this table's single annual £/MWh.",
    "_CM_LEVY_BY_YEAR": "cites Ofgem Annex 9 v1.8 as £/customer/year ÷ 3.1 MWh; the divisor is a "
                        "reading, so the pin is the Annex 9 row and not the quotient.",
    "_FIT_LEVY_BY_YEAR": "Ofgem FIT annual levelisation; published per levelisation period, not "
                         "per obligation year.",
    "_MUTUALIZATION_LEVY_BY_YEAR": "SoLR mutualisation recovery totals are published per event; "
                                   "the table is an allocated per-MWh figure.",
    "_GAS_NETWORK_COST_BY_YEAR": "transportation charges vary by LDZ and exit point; national "
                                 "blend, same shape as the electricity network tables.",
    "_GGL_RATE_GBP_PER_METER_YEAR": "Green Gas Levy is published £/meter/year by BEIS/DESNZ; this "
                                    "one is a genuinely single-figure pin and is the cheapest "
                                    "next one to do.",
    "_ELEC_SC_PENCE_PER_DAY_BY_YEAR": "Ofgem cap standing charges are published per cap period "
                                      "and per region; the table is a calendar-year blend.",
    "_GAS_SC_PENCE_PER_DAY_BY_YEAR": "the gas half of the above: published per cap period and per "
                                     "region, against a table keyed by calendar year, so the pin "
                                     "must carry the blending as a stated reading.",
}

# Ratchets. Both may only be LOWERED. Raising either to make a red test green is the
# goal-seeking R12 forbids, applied to a control.
_MAX_UNVERIFIED_TABLES = 11
_MAX_RECALLED_PINS = 3   # elec 2016, gas 2016, gas 2022 — each an open item in the commons


def _load_pins() -> list[dict]:
    """Read the published CCL rates from the regulation commons.

    NO FAIL-OPEN PATH (R15). A missing, empty or malformed artefact RAISES. The tempting
    alternative — return `[]` and let the equality leg iterate over nothing — would make every
    assertion below vacuously true, which is precisely the fail-silent shape that lets a
    control report green while checking nothing.
    """
    if not COMMONS.exists():
        raise FileNotFoundError(f"CCL rates commons artefact missing: {COMMONS}")
    raw = json.loads(COMMONS.read_text())
    pins = raw.get("rates")
    if not pins:
        raise ValueError(f"CCL rates commons artefact has no rates: {COMMONS}")
    return pins


def _obligation_year(pin: dict) -> int:
    """The year the rate COMMENCES. Every pin commences on 1 April, per the commons basis."""
    assert pin["from"].endswith("-04-01"), f"CCL rates commence on 1 April: {pin['from']}"
    return int(pin["from"][:4])


def _published_gbp_per_mwh(pin: dict) -> float:
    """Convert the statute's GBP/kWh to the model's GBP/MWh.

    THIS CONVERSION IS THE POINT. The commons holds the statute's unit; performing the
    conversion here is what keeps the checked value independent of the value it checks.
    """
    return round(pin["gbp_per_kwh"] * 1000.0, 2)


# ═══════════════════════════════════════════════════════════════════════════════════════════
# (a) EQUALITY — the constant equals the publication it cites
# ═══════════════════════════════════════════════════════════════════════════════════════════

def test_every_pinned_rate_equals_the_tabulated_constant():
    """The leg that fails on a mis-transcription. This is the one the citation census could not be."""
    pins = _load_pins()
    checked = 0
    for table_name, commodity in _VERIFIED_TABLES.items():
        table = getattr(policy_costs, table_name)
        for pin in pins:
            if pin["commodity"] != commodity or pin["provenance"] not in _ASSERTED:
                continue
            year = _obligation_year(pin)
            if year not in table:
                continue          # out of window; leg (b) owns absence, not this leg
            expected = _published_gbp_per_mwh(pin)
            assert table[year] == pytest.approx(expected, abs=0.005), (
                f"{table_name}[{year}] = {table[year]} £/MWh but "
                f"{pin['source_label']} publishes {pin['gbp_per_kwh']} £/kWh = {expected} £/MWh"
            )
            checked += 1
    # NON-VACUITY: this leg must actually have compared something.
    assert checked >= 15, f"only {checked} pinned (table, year) pairs compared — register shrank?"


def test_the_asserted_set_excludes_recalled_figures():
    """A figure nobody fetched must not be asserted as published. Provenance is load-bearing."""
    assert "recalled" not in _ASSERTED
    recalled = [p for p in _load_pins() if p["provenance"] == "recalled"]
    for pin in recalled:
        assert pin["source"] is None, (
            f"{pin['from']} {pin['commodity']} is marked recalled but carries a source URL — "
            "if it was fetched, promote it to primary"
        )


# ═══════════════════════════════════════════════════════════════════════════════════════════
# (b) COVERAGE — an in-window year without a pin is a hole
# ═══════════════════════════════════════════════════════════════════════════════════════════

def test_every_in_window_year_of_a_verified_table_has_a_pin():
    """Otherwise a table could add or keep an unpinned year and the equality leg would skip it."""
    pins = _load_pins()
    for table_name, commodity in _VERIFIED_TABLES.items():
        table = getattr(policy_costs, table_name)
        pinned_years = {
            _obligation_year(p) for p in pins if p["commodity"] == commodity
        }
        missing = sorted(set(table) - pinned_years)
        assert not missing, (
            f"{table_name} tabulates {missing} with no entry in {COMMONS.name} — "
            "an unpinned year is invisible to the equality leg"
        )


# ═══════════════════════════════════════════════════════════════════════════════════════════
# (c) SCOPE — a new table cannot be silently unchecked
# ═══════════════════════════════════════════════════════════════════════════════════════════

def test_every_year_keyed_table_is_classified():
    """The leg that stops this control's population from quietly drifting away from the module's.

    A table added to the module and to neither dict here would be unchecked AND uncounted, so
    the ratchet would read green while coverage fell. Same census leg the year-basis control
    runs, for the same reason.
    """
    classified = set(_VERIFIED_TABLES) | set(_UNVERIFIED_TABLES)
    registered = set(YEAR_KEY_BASIS)
    assert not (registered - classified), (
        f"year-keyed tables classified neither verified nor unverified: "
        f"{sorted(registered - classified)}"
    )
    assert not (classified - registered), (
        f"classified here but absent from YEAR_KEY_BASIS (renamed or deleted?): "
        f"{sorted(classified - registered)}"
    )


def test_every_unverified_table_states_a_reason():
    """"Unverified" with no reason is a TODO; with a reason it is a decision someone can audit."""
    for name, reason in _UNVERIFIED_TABLES.items():
        assert len(reason) >= 40, f"{name}'s unverified reason is too thin to audit: {reason!r}"


# ═══════════════════════════════════════════════════════════════════════════════════════════
# (d) RATCHETS — the unchecked surface may only shrink
# ═══════════════════════════════════════════════════════════════════════════════════════════

def test_the_unverified_table_count_only_goes_down():
    assert len(_UNVERIFIED_TABLES) <= _MAX_UNVERIFIED_TABLES, (
        f"{len(_UNVERIFIED_TABLES)} unverified tables against a ratchet of "
        f"{_MAX_UNVERIFIED_TABLES}. Pin the table; do not raise the ratchet."
    )


def test_the_recalled_pin_count_only_goes_down():
    recalled = [p for p in _load_pins() if p["provenance"] == "recalled"]
    assert len(recalled) <= _MAX_RECALLED_PINS, (
        f"{len(recalled)} recalled pins against a ratchet of {_MAX_RECALLED_PINS}: "
        f"{[(p['from'], p['commodity']) for p in recalled]}. Fetch them; do not raise the ratchet."
    )


# ═══════════════════════════════════════════════════════════════════════════════════════════
# (e) MUTATION — R15: every leg above is proven to FIRE
# ═══════════════════════════════════════════════════════════════════════════════════════════
#
# These are not decoration. The defect this file exists for survived a green suite for months
# because the control that "covered" it could not express the failure. Each test below breaks
# one thing and asserts the corresponding leg goes red.

def test_mutation_a_drifting_constant_is_caught(monkeypatch):
    """THE NAMED DEFECT, replayed: restore the old 2019 figure and the equality leg must fire."""
    mutated = dict(policy_costs._CCL_ELECTRICITY_RATE_BY_YEAR)
    mutated[2019] = 6.11        # the pre-repair value, £18,274.68 of the £43,074.89
    monkeypatch.setattr(policy_costs, "_CCL_ELECTRICITY_RATE_BY_YEAR", mutated)
    with pytest.raises(AssertionError, match="publishes"):
        test_every_pinned_rate_equals_the_tabulated_constant()


def test_mutation_a_drifting_pin_is_caught(monkeypatch):
    """The other direction: the COMMONS is not privileged either. If someone edits a pinned
    figure away from the statute, the same leg fires — so the pair must agree, and neither side
    can be quietly moved to make the other green."""
    pins = _load_pins()
    for pin in pins:
        if pin["commodity"] == "electricity" and pin["from"] == "2019-04-01":
            pin["gbp_per_kwh"] = 0.00611
    monkeypatch.setitem(globals(), "_load_pins", lambda: pins)
    with pytest.raises(AssertionError, match="publishes"):
        test_every_pinned_rate_equals_the_tabulated_constant()


def test_mutation_an_unpinned_year_is_caught(monkeypatch):
    """A table year with no pin must fail leg (b) rather than being skipped by leg (a)."""
    mutated = dict(policy_costs._CCL_ELECTRICITY_RATE_BY_YEAR)
    mutated[2015] = 5.54        # a year the commons does not pin
    monkeypatch.setattr(policy_costs, "_CCL_ELECTRICITY_RATE_BY_YEAR", mutated)
    with pytest.raises(AssertionError, match="no entry in"):
        test_every_in_window_year_of_a_verified_table_has_a_pin()


def test_mutation_an_unclassified_new_table_is_caught(monkeypatch):
    """The fail-open shape that would matter most in six months: a new table nobody pinned."""
    mutated = dict(YEAR_KEY_BASIS)
    mutated["_SOME_NEW_LEVY_BY_YEAR"] = "apr_mar"
    monkeypatch.setattr(policy_costs, "YEAR_KEY_BASIS", mutated)
    monkeypatch.setitem(globals(), "YEAR_KEY_BASIS", mutated)
    with pytest.raises(AssertionError, match="classified neither"):
        test_every_year_keyed_table_is_classified()


def test_mutation_an_emptied_register_cannot_read_green(monkeypatch):
    """FAIL-SILENT guard. An empty register would make leg (a) iterate over nothing and pass.
    The loader raises instead, and the non-vacuity floor in leg (a) is the second net."""
    monkeypatch.setattr(Path, "read_text", lambda self, *a, **k: '{"rates": []}')
    with pytest.raises(ValueError, match="no rates"):
        _load_pins()


def test_mutation_a_missing_register_cannot_read_green(monkeypatch):
    """An unavailable check is a FAILED check, never a passed one."""
    monkeypatch.setattr(Path, "exists", lambda self: False)
    with pytest.raises(FileNotFoundError, match="commons artefact missing"):
        _load_pins()
