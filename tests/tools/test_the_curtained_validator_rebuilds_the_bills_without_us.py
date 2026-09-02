"""BRIEF ITEM 3: the curtained validator — *"cannot import billing code, curtain proved by mutation"*.

Director brief, 2026-09-02. The point of the curtain is not trust: a reconstruction that imports
the biller inherits the biller's bugs for free. Call `bill_generator`'s own rounding or its own rate
lookup and the two agree by construction, and the agreement means nothing. The exercise is worth
exactly as much as the independence of the second computation.

So the curtain is **stdlib only** — not "no billing imports", because a chain three modules long
ends up back at `saas.money` and nobody notices — and it is a property of the file's own AST rather
than a promise in its docstring.

WHAT THE FIRST FULL RUN FOUND, on the real book (2026-09-02):

  * **11,549 of 11,549** periods: energy and standing charge rebuilt from the meter readings and
    the contracted rates, agreeing with our bills to the penny.
  * **11,549 of 11,549** bills: VAT amount matches the rate the PUBLISHED LAW says applies —
    derived from `uk_vat_rates.json` and `vat_fuel_and_power_de_minimis.json`, not from us.
  * network and policy costs: **uncheckable**, and named as such rather than passed.

That is the first time this project's billing arithmetic has been checked against anything outside
itself, and its limit is in the same breath: two of five lines are rebuilt, one rate is externally
confirmed, and the largest pass-through term is not checked at all.
"""
from __future__ import annotations

import json
import textwrap

import pytest

from tools import independent_bill_validator as v


def _period(**over):
    base = {"period_start": "2016-02-01", "period_end": "2016-02-29", "days_in_period": 29,
            "commodity": "electricity", "unit_rate_p_per_kwh": 2.446,
            "standing_charge_gbp_per_day": 0.22, "volume_basis": "reads",
            "reads": [{"read_kwh": 1937.9, "read_type": "carried_forward"},
                      {"read_kwh": 3826.2, "read_type": "A"}]}
    base.update(over)
    return base


# ── THE CURTAIN ─────────────────────────────────────────────────────────────────────────────
def test_the_validator_imports_no_repository_code_at_all():
    """THE PROPERTY THE WHOLE EXERCISE RESTS ON."""
    assert v.imports_into_the_repository() == []


def test_a_repository_import_BREACHES_the_curtain(tmp_path):
    """MUTATION, and it is the brief's own acceptance test: *"curtain proved by mutation"*.

    A module that imports the biller and then agrees with it has proven nothing, so the control
    must fire on the import itself and not on some downstream disagreement.
    """
    breached = tmp_path / "breached.py"
    breached.write_text("import company.billing.raw_account_export\n")
    assert v.imports_into_the_repository(breached) == ["company.billing.raw_account_export"]
    with pytest.raises(v.CurtainBreached) as e:
        v.assert_curtain(breached)
    assert "worth nothing" in str(e.value)


def test_a_FUNCTION_LOCAL_import_is_caught_too(tmp_path):
    """The obvious way this rots. A module-header check would never see it, and a local import is
    exactly what someone adds when they want "just the rounding helper"."""
    sneaky = tmp_path / "sneaky.py"
    sneaky.write_text(textwrap.dedent("""
        def rebuild():
            from saas import money      # noqa
            return money
    """))
    # The MODULE, not the symbol: `from saas import money` has `node.module == "saas"`, and
    # reporting what the AST actually says beats reporting a prettier string that is not in the
    # file. My first assertion here expected "saas.money" and was wrong about the breach it was
    # describing, which is its own small lesson about naming a thing before asserting on it.
    assert v.imports_into_the_repository(sneaky) == ["saas"]


def test_a_relative_import_is_a_repository_import_by_definition(tmp_path):
    p = tmp_path / "rel.py"
    p.write_text("from . import bill_generator\n")
    assert v.imports_into_the_repository(p) == [".", ]


def test_stdlib_imports_are_not_a_breach(tmp_path):
    p = tmp_path / "fine.py"
    p.write_text("import json\nfrom pathlib import Path\nfrom decimal import Decimal\n")
    assert v.imports_into_the_repository(p) == []


def test_the_curtain_is_asserted_at_the_ENTRY_POINT_not_only_in_a_test():
    """A validator whose independence is checked by a test somebody remembers to run is a validator
    whose independence is checked when it does not matter.

    MUTATION: delete `assert_curtain()` from `rebuild` and this fails.
    """
    import inspect
    assert "assert_curtain()" in inspect.getsource(v.rebuild)


# ── it recomputes the volume rather than being handed one ───────────────────────────────────
def test_the_volume_is_SUBTRACTED_from_the_two_readings():
    """Only possible since the raw export stopped putting `consumption_kwh` in `read_kwh`. A
    validator handed a volume cannot check a volume.

    MUTATION: return the period's `consumption_kwh` instead and this fails -- the raw export does
    not carry it when readings exist, so the line goes UNCHECKABLE.
    """
    line = v.rebuild_period(_period(), segment="resi")["lines"][0]
    assert line["status"] == v.RECONSTRUCTED
    assert line["volume_kwh"] == pytest.approx(1888.3)
    assert line["amount_gbp"] == pytest.approx(46.19, abs=0.01)


def test_a_period_with_no_readings_is_UNCHECKABLE_and_not_guessed():
    """Where the raw export says it could not supply readings, our figure is all anyone has, and
    using it is not a reconstruction -- it is being told the answer."""
    line = v.rebuild_period(
        _period(volume_basis="consumption_only", reads=[], consumption_kwh=1888.3),
        segment="resi")["lines"][0]
    assert line["status"] == v.UNCHECKABLE
    assert "could not supply readings" in line["why"]


def test_the_standing_charge_is_days_times_the_daily_rate():
    line = v.rebuild_period(_period(), segment="resi")["lines"][1]
    assert line["status"] == v.RECONSTRUCTED
    assert line["amount_gbp"] == pytest.approx(6.38, abs=0.01)


# ── the rate it gets from the LAW, and can disagree with us about ───────────────────────────
def test_domestic_supply_is_reduced_rated_whatever_the_quantity():
    got = v.statutory_vat_rate(segment="resi", commodity="electricity", kwh=99_999.0, days=30.0)
    assert got["rate"] == 0.05
    assert "regardless of quantity" in got["why"]


def test_a_business_supply_ABOVE_the_de_minimis_is_standard_rated():
    """33 kWh/day for electricity, from VAT Notice 701/19 §5.2 as carried in the commons. Measured
    on the real book: all 72 SME electricity bills are above it and all 72 are charged 20%."""
    got = v.statutory_vat_rate(segment="SME", commodity="electricity", kwh=3400.0, days=30.0)
    assert got["rate"] == 0.20 and "exceeds the published de minimis" in got["why"]


def test_a_business_supply_BELOW_the_de_minimis_is_reduced_rated():
    """The branch that makes this a reading of the law and not a segment lookup. Without it the
    validator would simply restate 'SME means 20%', which is our rule, not the notice's."""
    got = v.statutory_vat_rate(segment="SME", commodity="electricity", kwh=300.0, days=30.0)
    assert got["rate"] == 0.05 and "at or below the published de minimis" in got["why"]


def test_the_rate_always_carries_the_reason_and_the_source():
    """A validator that says "5%" and not "5% because domestic supply is reduced-rated regardless
    of quantity" cannot be argued with, and a disagreement it raises cannot be adjudicated."""
    got = v.statutory_vat_rate(segment="resi", commodity="gas", kwh=100.0, days=30.0)
    assert got["why"] and got["source"].endswith(".json")


def test_a_missing_published_artefact_RAISES_rather_than_defaulting(monkeypatch, tmp_path):
    """A validator that silently fell back to a built-in rate would be checking us against
    ourselves while reporting that it had not -- the worst of the available failures, because it
    reports a pass."""
    monkeypatch.setattr(v, "COMMONS", tmp_path)
    with pytest.raises(FileNotFoundError) as e:
        v.statutory_vat_rate(segment="resi", commodity="electricity", kwh=1.0, days=1.0)
    assert "refusing to substitute one" in str(e.value)


# ── what it will not pretend to have done ──────────────────────────────────────────────────
def test_the_levy_line_is_UNCHECKABLE_and_says_exactly_why():
    """Not a pass and not a failure: a third answer. The bill does not record the rate, and the
    commons carries only the Renewables Obligation and the Climate Change Levy while the figure
    bundles DUoS, TNUoS, BSUoS, RO, FiT, CfD, CM and smart metering."""
    line = [ln for ln in v.rebuild_period(_period(), segment="resi")["lines"]
            if ln["label"] == "Network and policy costs"][0]
    assert line["status"] == v.UNCHECKABLE
    assert "does not record the levy rate" in line["why"] and "commons" in line["why"]
    assert "amount_gbp" not in line, "an uncheckable line must not carry a number"


def test_the_vat_AMOUNT_is_not_claimed_to_be_rebuilt():
    """Its base includes the uncheckable line, so the amount cannot be rebuilt however much one
    would like a total. Saying so is the difference between a partial result and a false one."""
    line = [ln for ln in v.rebuild_period(_period(), segment="resi")["lines"]
            if ln["label"] == "VAT"][0]
    assert line["status"] == v.RATE_CHECKED
    assert "amount_gbp" not in line
    assert "the AMOUNT is not rebuilt" in line["amount_note"]


def test_the_subtotal_sums_only_what_was_actually_rebuilt():
    """MUTATION: include the uncheckable lines as zero and this fails -- and every bill acquires a
    silent shortfall equal to its levies and VAT, which a comparison would report as a defect in
    the biller."""
    built = v.rebuild_period(_period(), segment="resi")
    assert built["reconstructed_subtotal_gbp"] == pytest.approx(52.57, abs=0.01)


# ── against the real book ──────────────────────────────────────────────────────────────────
def _real():
    from company.billing import raw_account_export as rx  # the HARNESS may import it
    if not rx.LEDGER_PATH.exists():
        pytest.skip("no billing ledger on this box")
    return rx, json.loads(rx.LEDGER_PATH.read_text())


def test_every_period_in_the_book_rebuilds_to_our_own_energy_and_standing_charge():
    """THE RESULT, with a dated population floor. 11,549 of 11,549 on 2026-09-02.

    The harness imports the raw export to PRODUCE the input; the validator itself imports nothing —
    that is the curtain, and it is unaffected by what builds its input file. In item 5 this arrives
    as JSON on disk.
    """
    rx, ledger = _real()
    periods = 0
    differ = []
    for cid, rec in (ledger.get("customers") or {}).items():
        built = v.rebuild(rx.raw_account(cid, rec))
        for inv, p in zip(rec.get("invoices") or [], built["periods"]):
            periods += 1
            ours = (inv.get("commodity_amount_gbp") or 0.0) + (inv.get("standing_charge_gbp") or 0.0)
            if abs(ours - p["reconstructed_subtotal_gbp"]) > 0.011:
                differ.append("{}/{}: ours {:.2f}, rebuilt {:.2f}".format(
                    cid, inv.get("invoice_number"), ours, p["reconstructed_subtotal_gbp"]))
    assert periods >= 11_000, "only {} periods: an emptied ledger would pass".format(periods)
    assert not differ, "{} of {} periods disagree: {}".format(len(differ), periods, differ[:5])


def test_every_bills_vat_matches_the_rate_the_PUBLISHED_LAW_says_applies():
    """AND THE COMPARISON IS ON THE AMOUNT, NOT THE RATIO — which is not a detail.

    The first draft of this measurement compared `vat_gbp / subtotal` against the statutory rate
    with an absolute tolerance, and reported FOUR bills out of 11,549 as wrong. All four were
    correct: 1-2 day periods with subtotals of £1.47 to £2.11, where a penny of ordinary rounding
    is 0.5% of the ratio. Every one of them was exactly `round(0.05 x subtotal, 2)`.

    **A tolerance stated on a ratio produces false positives at small denominators**, and item 4
    shipping with that test would have filed four false findings on its first run. The quantity is
    the amount; the ratio is not a quantity (`two_true_numbers_whose_ratio_is_not_a_quantity`).
    """
    rx, ledger = _real()
    checked = 0
    differ = []
    for cid, rec in (ledger.get("customers") or {}).items():
        built = v.rebuild(rx.raw_account(cid, rec))
        for inv, p in zip(rec.get("invoices") or [], built["periods"]):
            law = [ln for ln in p["lines"] if ln["label"] == "VAT"][0]["statutory_rate"]
            if law is None:
                continue
            subtotal = sum((inv.get(k) or 0.0) for k in (
                "commodity_amount_gbp", "non_commodity_amount_gbp", "standing_charge_gbp"))
            checked += 1
            if abs((inv.get("vat_gbp") or 0.0) - round(law * subtotal, 2)) > 0.0101:
                differ.append("{}/{}: charged {}, the law gives {:.2f} at {}".format(
                    cid, inv.get("invoice_number"), inv.get("vat_gbp"),
                    round(law * subtotal, 2), law))
    assert checked >= 11_000, "only {} bills: an emptied ledger would pass".format(checked)
    assert not differ, "{} of {} bills: {}".format(len(differ), checked, differ[:5])
