"""The two published `Low Carbon %` tables disagree, and the report must SAY SO (2026-08-14).

Discharges `WORKER_FINDING_TWO_PUBLISHED_FUEL_MIX_TABLES_DISAGREE_ON_LOW_CARBON_2026-08-14.md`
(BLOCKING, `F_risk_compliance`) by its own clause 2 — record and accept the limitation explicitly —
because clause 1 needs a fetched source and this tick has none. Nothing published is revalued.

R15. The control this file has to be is not "a note is present". A constant string containing the
number 3.4 would satisfy that and would be a THIRD copy of the same disagreement, silently false
the first time either table moves — the fail-open shape. So every test below mutates a table and
asserts the RENDERED SENTENCE MOVED WITH IT:

* `test_the_note_is_read_from_the_tables_not_narrated` — change the disclosure table, the published
  worst-year figure changes.
* `test_making_the_tables_agree_silences_the_note` — the note must be able to go away, or a future
  reconciliation leaves a permanently false paragraph behind.
* `test_a_constant_offset_is_not_described_as_two_series` — the sign-flip clause is measured, so it
  cannot survive a world where it stopped being true.
* `test_both_sections_carry_it` / `test_removing_the_wiring_is_caught` — the note reaching the file
  is the R11 half; the reader who lands on only one of the two tables is the one being misled.
"""

from __future__ import annotations

import pytest

from company.regulatory import fuel_mix_reconciliation as recon
from company.regulatory.fuel_mix_reconciliation import (
    DISCLOSURE_SECTION,
    OBSERVATORY_SECTION,
    divergence_note,
    reconcile_low_carbon,
    sign_flips,
    worst_divergence,
)

#: Measured at HEAD by executing the shipped code, and recorded verbatim in the finding's table.
#: Observatory `low_carbon_pct` minus Disclosure `renewable + nuclear`, signed, percentage points.
MEASURED_DIVERGENCE = {
    2016: -0.5, 2017: -0.7, 2018: -1.3, 2019: 2.7, 2020: 0.1,
    2021: 1.7, 2022: 2.0, 2023: -3.4, 2024: -1.5, 2025: -0.5,
}


def test_the_divergence_is_still_what_the_finding_measured():
    """The finding's table, re-derived. Red here means a table moved and the note's claims,
    the ratchet entry in `grid_intensity_guard` and the finding all need re-reading."""
    assert {r.year: r.diff_pp for r in reconcile_low_carbon()} == MEASURED_DIVERGENCE


def test_the_worst_year_is_2023_and_the_sign_flips():
    worst = worst_divergence()
    assert worst is not None
    assert (worst.year, worst.abs_diff_pp) == (2023, 3.4)
    assert (worst.observatory_pct, worst.disclosure_pct) == (59.0, 62.4)
    assert sign_flips(), "an alternating difference is the reason this is two series, not one basis"


def test_the_note_names_both_sections_and_asserts_no_winner():
    for section in (OBSERVATORY_SECTION, DISCLOSURE_SECTION):
        note = divergence_note(section)
        assert OBSERVATORY_SECTION in note and DISCLOSURE_SECTION in note
        assert "3.4pp" in note and "2023" in note
        assert "does not assert which" in note
        # The intensity series is NOT part of this residue and the note must not imply it is.
        assert "single owner" in note


def test_an_unknown_section_is_refused_not_rendered_blank():
    """A typo'd section name returning "" would delete the disclosure silently."""
    with pytest.raises(ValueError):
        divergence_note("Some Other Section")


# --- mutation proofs: the note is derived, so it must move when the data moves ----------------


@pytest.fixture
def patched_disclosure(monkeypatch):
    """Swap `_FUEL_MIX_BY_YEAR` for the duration of one test.

    The module reads it through a function-local import, so patching the OWNER is what the
    renderer actually sees — patching a name in `fuel_mix_reconciliation` would test nothing.
    """

    def _apply(table):
        import company.billing.fuel_mix as fm

        monkeypatch.setattr(fm, "_FUEL_MIX_BY_YEAR", table, raising=True)

    return _apply


def _disclosure_copy():
    from company.billing.fuel_mix import _FUEL_MIX_BY_YEAR

    return {y: dict(m) for y, m in _FUEL_MIX_BY_YEAR.items()}


def test_the_note_is_read_from_the_tables_not_narrated(patched_disclosure):
    """MUTATION. Widen 2020's gap past 2023's; the published worst year and figure must follow."""
    before = divergence_note(OBSERVATORY_SECTION)
    assert "2023" in before and "3.4pp" in before

    table = _disclosure_copy()
    table[2020]["renewable"] = table[2020]["renewable"] - 9.0
    table[2020]["gas"] = table[2020]["gas"] + 9.0  # keep the mix summing to 100
    patched_disclosure(table)

    after = divergence_note(OBSERVATORY_SECTION)
    assert after != before
    assert "2020" in after and "9.1pp" in after
    assert "3.4pp" not in after, "a note that still says 3.4pp after the data moved is a third copy"


def test_making_the_tables_agree_silences_the_note(patched_disclosure):
    """MUTATION. The instance can be FIXED, and fixing it must remove the paragraph — otherwise
    the reconciliation leaves a false disclosure behind for the next reader."""
    from company.regulatory.carbon_emissions import UK_GRID_FUEL_MIX

    table = _disclosure_copy()
    for year, mix in table.items():
        if year not in UK_GRID_FUEL_MIX:
            continue
        target = UK_GRID_FUEL_MIX[year].low_carbon_pct
        drift = round(target - (mix["renewable"] + mix["nuclear"]), 1)
        mix["renewable"] = round(mix["renewable"] + drift, 1)
        mix["other"] = round(mix["other"] - drift, 1)
    patched_disclosure(table)

    assert worst_divergence().abs_diff_pp == 0.0
    assert divergence_note(OBSERVATORY_SECTION) == ""
    assert divergence_note(DISCLOSURE_SECTION) == ""


def test_a_constant_offset_is_not_described_as_two_series(patched_disclosure):
    """MUTATION. Make the Observatory uniformly higher; the sign-flip clause must retract."""
    from company.regulatory.carbon_emissions import UK_GRID_FUEL_MIX

    table = _disclosure_copy()
    for year, mix in table.items():
        if year not in UK_GRID_FUEL_MIX:
            continue
        target = UK_GRID_FUEL_MIX[year].low_carbon_pct - 2.0
        drift = round(target - (mix["renewable"] + mix["nuclear"]), 1)
        mix["renewable"] = round(mix["renewable"] + drift, 1)
        mix["other"] = round(mix["other"] - drift, 1)
    patched_disclosure(table)

    assert not sign_flips()
    note = divergence_note(OBSERVATORY_SECTION)
    assert "in the same direction in every year" in note
    assert "rather than one definitional difference" not in note


def test_no_overlapping_years_is_silence_not_a_crash(monkeypatch):
    """FAIL-OPEN check on the other side: an empty intersection must not raise, and must not
    render a note claiming a divergence it cannot see."""
    import company.billing.fuel_mix as fm

    monkeypatch.setattr(fm, "_FUEL_MIX_BY_YEAR", {}, raising=True)
    assert reconcile_low_carbon() == []
    assert worst_divergence() is None
    assert divergence_note(DISCLOSURE_SECTION) == ""


# --- the wiring: the note has to reach the rendered report ------------------------------------


def _render(section_fn, data):
    from saas.reporting import annual_report

    return getattr(annual_report, section_fn)(data)


def test_both_sections_carry_it():
    """R11's code-side half: both rendered sections contain the disclosure. The live-file
    assertion is `tests/saas/reporting`'s published-report check plus the regenerated
    `docs/reports/ANNUAL_REPORT.md`."""
    ma = {str(y): {"income_statement": {"revenue_gbp": 1_500_000.0}} for y in range(2016, 2026)}
    observatory = _render("_section_carbon_emissions", {"management_accounts": ma})
    disclosure = _render("_section_fuel_mix_disclosure", {"years": {str(y): {} for y in range(2016, 2026)}})

    for rendered in (observatory, disclosure):
        assert "Unreconciled with the" in rendered
        assert "3.4pp" in rendered
        assert "does not assert which" in rendered


def test_removing_the_wiring_is_caught(monkeypatch):
    """MUTATION on the WIRING, not the data. If a future edit drops the `divergence_note` call
    from a section, that section stops carrying the disclosure — this proves the assertion above
    is load-bearing rather than passing on some other sentence."""
    from saas.reporting import annual_report

    monkeypatch.setattr(annual_report, "_fuel_mix_divergence_note", lambda section: "")
    disclosure = _render("_section_fuel_mix_disclosure", {"years": {str(y): {} for y in range(2016, 2026)}})
    assert "Unreconciled with the" not in disclosure


def test_the_ratchet_entry_still_points_at_this_finding():
    """Clause 2 does NOT delete the instance — there are still two tables — so the
    `grid_intensity_guard` exemption must remain, and must still name this finding. If someone
    reconciles the tables for real, `test_the_ratchet_has_no_stale_entries` forces its removal."""
    from tools.grid_intensity_guard import KNOWN_SECOND_SERIES

    key = "company/billing/fuel_mix.py::_FUEL_MIX_BY_YEAR"
    assert key in KNOWN_SECOND_SERIES
    assert "TWO_PUBLISHED_FUEL_MIX_TABLES_DISAGREE" in KNOWN_SECOND_SERIES[key].replace("_\n", "_")
