"""One legal rule, two fuels, two limits — and the code applied one of them to both.

Commons: `docs/domain_artefact_library/regulatory/vat_fuel_and_power_de_minimis.json`
(VAT Notice 701/19, electricity §5.2 = 33 kWh/day, gas §4.2 = 145 kWh/day).
Finding: `docs/staging/WORKER_FINDING_THE_VAT_DE_MINIMIS_WAS_ONE_FUELS_LIMIT_APPLIED_TO_BOTH_2026-08-31.md`.

`_sme_vat_rate(daily_kwh)` took no fuel argument and tested every leg against 33.0. Gas's published
limit is 4.39x higher, so every SME gas leg between 33 and 145 kWh/day was charged the standard rate
where the law says reduced — the supplier taking money from a customer it was not entitled to.

KEYED TO THE PUBLISHED RULE, NOT TO 33 AND 145. Nothing here writes either figure down. The limits
come from the commons, and if HMRC moves one, the artefact changes and these legs still pass — what
they hold is that the two fuels are read SEPARATELY, that the boundary falls where the notice's
words put it, and that an unknown fuel is refused rather than handed another fuel's threshold.
"""
from __future__ import annotations

import json

import pytest

from company.billing import dual_fuel_bill as dfb

REDUCED = dfb.VAT_RATE_BY_MARKET["resi"]
STANDARD = dfb.VAT_RATE_BY_MARKET["I&C"]


def _commons() -> dict:
    return json.loads(dfb._VAT_DE_MINIMIS_COMMONS.read_text())


def test_the_two_fuels_carry_DIFFERENT_limits_and_neither_is_written_in_the_code():
    """The defect in one line: one number cannot be both fuels' limit.

    MUTATION: collapse the table to a single value, or restate either limit as a literal in
    `dual_fuel_bill`, and this fires.
    """
    table = dfb.SME_VAT_DE_MINIMIS_KWH_PER_DAY
    assert set(table) >= {"electricity", "gas"}
    assert table["electricity"] != table["gas"], (
        "electricity and gas have been given the same VAT de minimis limit. VAT Notice 701/19 "
        "§5.2 and §4.2 publish two different figures, and applying one to both fuels mis-rates "
        "every business supply in the gap between them."
    )
    published = _commons()["de_minimis_by_fuel"]
    for fuel, limit in table.items():
        assert limit == published[fuel]["kwh_per_day"], (
            f"the module's limit for {fuel} has drifted from the commons — the artefact is the "
            "authority and the module must read it, never restate it"
        )


def test_a_supply_AT_the_limit_is_reduced_rated_and_one_ABOVE_it_is_not(fuel_limits=None):
    """The notice says "not more than an average rate of", so the boundary is strictly-greater.

    MUTATION: change `>` to `>=` in `_sme_vat_rate` and this fires on the at-the-limit case.
    """
    for fuel, limit in dfb.SME_VAT_DE_MINIMIS_KWH_PER_DAY.items():
        assert dfb._sme_vat_rate(limit, fuel) == REDUCED, (
            f"a {fuel} supply at exactly {limit} kWh/day was standard-rated; the notice's words "
            'are "not more than an average rate of", so the limit itself qualifies'
        )
        assert dfb._sme_vat_rate(limit * 1.0001, fuel) == STANDARD
        assert dfb._sme_vat_rate(limit * 0.5, fuel) == REDUCED


def test_a_GAS_supply_between_the_two_limits_is_reduced_rated__the_defect_itself():
    """The regression, stated as the money it moves rather than as a threshold.

    Every SME gas leg in this band was standard-rated. Derived from the commons rather than
    written as 33 and 145, so it follows the law if the law moves.

    MUTATION: drop the `fuel` argument and test everything against electricity's limit, and this
    fires across the whole band.
    """
    elec = dfb.SME_VAT_DE_MINIMIS_KWH_PER_DAY["electricity"]
    gas = dfb.SME_VAT_DE_MINIMIS_KWH_PER_DAY["gas"]
    assert gas > elec, "this test's band is empty; the fixture it was written against has moved"
    for daily in (elec + 0.5, (elec + gas) / 2, gas):
        assert dfb._sme_vat_rate(daily, "gas") == REDUCED, (
            f"an SME gas supply at {daily:.1f} kWh/day was charged the standard rate. It is below "
            f"gas's published de minimis of {gas} kWh/day and the reduced rate is what the law "
            "requires; charging standard takes money from the customer that is not owed."
        )
        assert dfb._sme_vat_rate(daily, "electricity") == STANDARD, (
            "the same consumption on the ELECTRICITY leg must still be standard-rated — if both "
            "fuels now agree, the fuels have been collapsed again in the other direction"
        )


def test_an_UNKNOWN_fuel_is_REFUSED_rather_than_given_another_fuels_threshold():
    """Refusing to bill is safe. Billing at a rate no published limit supports is not.

    MUTATION: return a default rate, or fall back to `SME_VAT_THRESHOLD_KWH_PER_DAY`, instead of
    raising, and this fires.
    """
    with pytest.raises(ValueError) as exc:
        dfb._sme_vat_rate(50.0, "heat")
    message = str(exc.value)
    assert "heat" in message
    assert "electricity" in message and "gas" in message, (
        "the refusal must name the fuels that ARE published, so a reader can tell a missing "
        "artefact entry from a typo at the call site"
    )


def test_the_fuel_argument_is_REQUIRED_so_a_caller_cannot_silently_get_electricity():
    """A default would re-create the defect the moment someone adds a third call site.

    MUTATION: give `fuel` a default of "electricity" and this fires.
    """
    with pytest.raises(TypeError):
        dfb._sme_vat_rate(50.0)


def test_the_commons_is_the_AUTHORITY_and_the_module_follows_it(tmp_path, monkeypatch):
    """If HMRC moves a limit, changing the artefact must be the whole of the change.

    MUTATION: hard-code either figure in `dual_fuel_bill` and this fires — the module would keep
    the old limit while the commons carried the new one.
    """
    moved = _commons()
    moved["de_minimis_by_fuel"]["gas"]["kwh_per_day"] = 200.0
    artefact = tmp_path / "moved.json"
    artefact.write_text(json.dumps(moved))
    monkeypatch.setattr(dfb, "_VAT_DE_MINIMIS_COMMONS", artefact)
    assert dfb._load_de_minimis()["gas"] == 200.0


def test_the_loader_REFUSES_a_commons_it_cannot_read_rather_than_defaulting(tmp_path, monkeypatch):
    """FAIL CLOSED. A VAT threshold that falls back to a hard-coded number is the original defect.

    MUTATION: return a default dict on a missing or malformed artefact and this fires.
    """
    monkeypatch.setattr(dfb, "_VAT_DE_MINIMIS_COMMONS", tmp_path / "absent.json")
    with pytest.raises(FileNotFoundError):
        dfb._load_de_minimis()

    empty = tmp_path / "empty.json"
    empty.write_text("{}")
    monkeypatch.setattr(dfb, "_VAT_DE_MINIMIS_COMMONS", empty)
    with pytest.raises(ValueError):
        dfb._load_de_minimis()

    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"de_minimis_by_fuel": {"gas": {"kwh_per_day": 0}}}))
    monkeypatch.setattr(dfb, "_VAT_DE_MINIMIS_COMMONS", bad)
    with pytest.raises(ValueError):
        dfb._load_de_minimis()


def test_the_commons_still_carries_its_SOURCE_and_its_declared_gaps():
    """An artefact that loses its citation becomes an invented number with a filename.

    MUTATION: strip `source` or `NOT_ESTABLISHED_declared_rather_than_assumed` and this fires.
    """
    raw = _commons()
    assert raw["source"]["document"].startswith("VAT Notice 701/19")
    assert raw["source"]["url"]
    for fuel in ("electricity", "gas"):
        assert raw["de_minimis_by_fuel"][fuel]["section"], f"{fuel} lost its section reference"
        assert raw["de_minimis_by_fuel"][fuel]["quoted"], f"{fuel} lost the words it is read from"
    assert raw["NOT_ESTABLISHED_declared_rather_than_assumed"], (
        "the artefact must keep saying what it does NOT establish — whether the limits moved "
        "across 2016-2025 is unchecked, and an artefact that drops its own gaps reads as complete"
    )


def _rates_commons() -> dict:
    return json.loads(dfb._VAT_RATES_COMMONS.read_text())


def test_the_RATES_come_from_their_own_artefact_and_the_segment_table_is_DERIVED():
    """The percentages are a second published document, and the segment map must not restate them.

    VAT Notice 701/19 names "the reduced rate" and "the standard rate" and states NEITHER figure —
    it points at gov.uk/vat-rates. Two documents, two artefacts. A module that reads the de minimis
    from the notice and then hard-codes 0.05 beside it has attached the notice's citation to a
    figure it never published.

    MUTATION: write `0.05` or `0.20` as a literal anywhere in `VAT_RATE_BY_MARKET`, and this fires.
    """
    published = _rates_commons()["rates"]
    assert dfb.VAT_RATES["reduced"] == published["reduced"]["rate"]
    assert dfb.VAT_RATES["standard"] == published["standard"]["rate"]

    assert dfb.VAT_RATE_BY_MARKET["resi"] == dfb.VAT_RATES["reduced"], (
        "domestic supply is reduced-rated unconditionally and must be DERIVED from the published "
        "band, not restated"
    )
    assert dfb.VAT_RATE_BY_MARKET["I&C"] == dfb.VAT_RATES["standard"]
    assert REDUCED < STANDARD, "the reduced band is not below the standard band"


def test_the_rates_loader_REFUSES_rather_than_defaulting(tmp_path, monkeypatch):
    """There is no invented default for a tax rate.

    MUTATION: return `{"reduced": 0.05, "standard": 0.20}` on a failed read and this fires.
    """
    monkeypatch.setattr(dfb, "_VAT_RATES_COMMONS", tmp_path / "absent.json")
    with pytest.raises(FileNotFoundError):
        dfb._load_vat_rates()

    partial = tmp_path / "partial.json"
    partial.write_text(json.dumps({"rates": {"reduced": {"rate": 0.05}}}))
    monkeypatch.setattr(dfb, "_VAT_RATES_COMMONS", partial)
    with pytest.raises(ValueError):
        dfb._load_vat_rates()

    impossible = tmp_path / "impossible.json"
    impossible.write_text(json.dumps({"rates": {"reduced": {"rate": 0.05}, "standard": {"rate": 7}}}))
    monkeypatch.setattr(dfb, "_VAT_RATES_COMMONS", impossible)
    with pytest.raises(ValueError):
        dfb._load_vat_rates()


def test_the_rates_artefact_keeps_its_SOURCE_and_says_what_it_does_not_establish():
    """Including the one gap that matters: nobody has checked these rates held across 2016-2025.

    MUTATION: strip `source` or the NOT_ESTABLISHED list and this fires.
    """
    raw = _rates_commons()
    assert raw["source"]["url"].startswith("https://www.gov.uk/vat-rates")
    assert raw["source"]["fetched"]
    for band in ("reduced", "standard", "zero"):
        assert raw["rates"][band]["quoted"], f"{band} lost the words it was read from"
    gaps = raw["NOT_ESTABLISHED_declared_rather_than_assumed"]
    assert gaps and any("2016" in g for g in gaps), (
        "the artefact must keep declaring that WHEN these rates last changed is unchecked — "
        "today's rates are being used for every modelled year on an unverified assumption"
    )
