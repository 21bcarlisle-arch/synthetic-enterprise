"""The report's two `Low Carbon %` columns are two sourced quantities, and each section says so.

History. On 2026-08-14 the two tables were undated hand tables up to 3.4pp apart, and the report
said "at most one is right" rather than pick a winner without a source. On 2026-10-19 both were
fetched (`docs/market_research/two_uk_electricity_fuel_mixes_generation_and_disclosure.md`). The
Observatory now carries the DUKES 5.6.C generation mix, and the FMD section carries DESNZ's FMD UK
mix (supply basis, imports, April-March). DESNZ says the two differ by construction, so the note
names each basis rather than calling one of them wrong. The values themselves are controlled
against the page in `test_the_two_fuel_mixes_are_their_published_sources.py`.

R15. The note must stay DERIVED. A constant sentence carrying today's gap would be a third copy
that goes false on the next edition. So the mutation tests move a table and assert that the
rendered figure moves with it.
"""

from __future__ import annotations

import pytest

from company.regulatory.fuel_mix_reconciliation import (
    DISCLOSURE_SECTION,
    OBSERVATORY_SECTION,
    divergence_note,
    reconcile_low_carbon,
    worst_divergence,
)

#: Measured 2026-10-19 on the fetched tables: Observatory (generation) minus Disclosure (FMD).
MEASURED_DIFFERENCE = {2019: -0.8, 2020: 2.8, 2021: 0.0, 2022: 1.6, 2023: 4.6, 2024: 6.4, 2025: 2.6}


def test_the_difference_is_what_the_page_publishes():
    """Red here means an edition moved; the page's §4 table needs re-reading with it."""
    assert {r.year: r.diff_pp for r in reconcile_low_carbon()} == MEASURED_DIFFERENCE


def test_the_worst_year_is_2024():
    worst = worst_divergence()
    assert (worst.year, worst.abs_diff_pp) == (2024, 6.4)
    assert (worst.observatory_pct, worst.disclosure_pct) == (64.7, 58.3)


def test_the_note_names_both_bases_and_does_not_call_either_wrong():
    for section in (OBSERVATORY_SECTION, DISCLOSURE_SECTION):
        note = divergence_note(section)
        assert OBSERVATORY_SECTION in note and DISCLOSURE_SECTION in note
        assert "DUKES Table 5.6.C" in note and "Fuel mix disclosure data table" in note
        assert "two different quantities" in note
        assert "6.4pp" in note and "2024" in note
        assert "at most one" not in note.lower()
        assert "NESO's published series" in note


def test_an_unknown_section_is_refused_not_rendered_blank():
    """A typo'd section name returning "" would delete the statement silently."""
    with pytest.raises(ValueError):
        divergence_note("Some Other Section")


# --- mutation proofs: the note is derived, so it must move when the data moves ----------------


@pytest.fixture
def patched_disclosure(monkeypatch):
    """Swap `_FUEL_MIX_BY_YEAR` on its OWNER, which the function-local import actually reads."""

    def _apply(table):
        import company.billing.fuel_mix as fm

        monkeypatch.setattr(fm, "_FUEL_MIX_BY_YEAR", table, raising=True)

    return _apply


def _disclosure_copy():
    from company.billing.fuel_mix import _FUEL_MIX_BY_YEAR

    return {y: dict(m) for y, m in _FUEL_MIX_BY_YEAR.items()}


def test_the_note_is_read_from_the_tables_not_narrated(patched_disclosure):
    """MUTATION. Widen 2020's gap past 2024's; the published worst year and figure must follow."""
    before = divergence_note(OBSERVATORY_SECTION)
    table = _disclosure_copy()
    table[2020]["renewable"] -= 9.0
    table[2020]["gas"] += 9.0
    patched_disclosure(table)

    after = divergence_note(OBSERVATORY_SECTION)
    assert after != before
    assert "2020" in after and "11.8pp" in after
    assert "6.4pp" not in after, "a note that still says 6.4pp after the data moved is a third copy"


def test_agreement_is_said_as_agreement_and_the_bases_still_render(patched_disclosure):
    """MUTATION. Make the figures agree: the gap clause must say so, and the basis statement,
    which is true whatever the numbers, must remain."""
    from company.regulatory.carbon_emissions import UK_GRID_FUEL_MIX

    table = _disclosure_copy()
    for year, mix in table.items():
        drift = round(UK_GRID_FUEL_MIX[year].low_carbon_pct - (mix["renewable"] + mix["nuclear"]), 1)
        mix["renewable"] = round(mix["renewable"] + drift, 1)
        mix["other"] = round(mix["other"] - drift, 1)
    patched_disclosure(table)

    assert worst_divergence().abs_diff_pp == 0.0
    note = divergence_note(DISCLOSURE_SECTION)
    assert "happen to agree" in note and "differ by up to" not in note
    assert "two different quantities" in note


def test_no_overlapping_years_is_silence_not_a_crash(patched_disclosure):
    patched_disclosure({})
    assert reconcile_low_carbon() == []
    assert worst_divergence() is None
    assert divergence_note(DISCLOSURE_SECTION) == ""


# --- the wiring: the note has to reach the rendered report ------------------------------------


def _render(section_fn, data):
    from saas.reporting import annual_report

    return getattr(annual_report, section_fn)(data)


def test_both_sections_carry_it():
    ma = {str(y): {"income_statement": {"revenue_gbp": 1_500_000.0}} for y in range(2016, 2026)}
    observatory = _render("_section_carbon_emissions", {"management_accounts": ma})
    disclosure = _render("_section_fuel_mix_disclosure", {"years": {str(y): {} for y in range(2016, 2026)}})

    for rendered in (observatory, disclosure):
        assert "Not the same figure as the" in rendered
        assert "two different quantities" in rendered
    assert "DUKES" in observatory and "unsourced vintage" not in observatory


def test_removing_the_wiring_is_caught(monkeypatch):
    """MUTATION on the WIRING. Dropping the `divergence_note` call must drop the statement, which
    proves the assertion above is not passing on some other sentence."""
    from saas.reporting import annual_report

    monkeypatch.setattr(annual_report, "_fuel_mix_divergence_note", lambda section: "")
    disclosure = _render("_section_fuel_mix_disclosure", {"years": {str(y): {} for y in range(2016, 2026)}})
    assert "Not the same figure as the" not in disclosure


def test_the_ratchet_entry_names_the_page_that_sourced_both():
    """The `grid_intensity_guard` exemption stays (the FMD mix is a different quantity, and a third
    mix must still red), and it now points at the page that sourced both."""
    from tools.grid_intensity_guard import KNOWN_SECOND_SERIES

    reason = KNOWN_SECOND_SERIES["company/billing/fuel_mix.py::_FUEL_MIX_BY_YEAR"]
    assert "two_uk_electricity_fuel_mixes_generation_and_disclosure" in reason
