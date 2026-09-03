#!/usr/bin/env python3
"""THE CURTAINED VALIDATOR — rebuild the bills from raw facts, having never seen our billing code.

Director brief, 2026-09-02 (`DIRECTOR_BRIEF_INDEPENDENT_BILL_VALIDATION_2026-09-02`), work item 3:
a validator that *"cannot import billing code"*, with the curtain *"proved by mutation"*.

## WHAT THE CURTAIN IS FOR, AND WHAT IT IS NOT FOR

It is not about trust. It is that a reconstruction which imports the biller inherits the biller's
bugs for free: call `bill_generator`'s own rounding, or its own rate lookup, and the two agree by
construction and the agreement means nothing. The whole exercise is worth exactly as much as the
independence of the second computation, so the independence is a *structural* property here and not
a promise — see `imports_into_the_company` below, and the test that mutates an import in.

**Stdlib only.** Not "no billing imports" but no repository imports at all, because a chain three
modules long ends up back at `saas.money` and nobody notices. That makes the curtain checkable by
reading one file's AST rather than by walking a graph, which is the difference between a control
that is verified and one that is believed.

## WHAT IT CAN REBUILD, AND WHAT IT HONESTLY CANNOT

    Energy            volume x unit rate            RECONSTRUCTED
    Standing charge   days x daily rate             RECONSTRUCTED
    Network & policy  volume x levy rate            NOT RECONSTRUCTIBLE -- no rate, see below
    VAT               rate x (the three above)      AMOUNT not reconstructible; RATE is checked
    Total             the sum                       NOT RECONSTRUCTIBLE -- it contains the above

**And the volume itself is recomputed, which only became possible this evening.** The raw export
used to put `consumption_kwh` in a field declaring "what the register said"; it now exports the two
boundary READINGS, so the validator subtracts them itself. A validator handed a volume cannot check
a volume.

THE TWO IT CANNOT DO, stated here rather than discovered by a reader who trusted the output:

  * **the levy rate is not on the bill and not fully published.** `docs/domain_artefact_library/
    regulatory/` carries the Renewables Obligation and the Climate Change Levy, but the exported
    figure bundles DUoS, TNUoS, BSUoS, RO, FiT, CfD, CM and smart metering. Our own source cites
    *"Ofgem Retail Market Monitoring / Cornwall Insight"* — a named source, not a fetchable
    artefact. So this line is UNCHECKABLE, and calling it anything else would be the pretence the
    brief exists to remove.
  * **VAT's base includes that line**, so the VAT AMOUNT is unreconstructible for the same reason.
    Its RATE is not: `uk_vat_rates.json` and `vat_fuel_and_power_de_minimis.json` are the published
    law, so the validator derives which rate ought to apply and can disagree with us about it. That
    is the one place in this design where a RATE of ours is checked rather than reused — brief §3's
    shared-error hole, narrowed by exactly one term.

## AND THE FULL LIST OF WHAT THIS CANNOT CATCH IS WRITTEN DOWN

`docs/design/WHAT_THE_BILL_VALIDATION_CANNOT_CATCH.md` — work item 6, written the same day as this
module and deliberately before anyone had time to over-read the result. The short version: the
rates are still ours, so a wrong RATE reconstructs perfectly; the largest pass-through line is not
checked at all; and the curtain proves the second computation does not inherit the first one's
implementation, not that it does not share its beliefs. Read it before quoting "11,549 of 11,549".

## ROUNDING IS A DECISION, SO IT IS DECLARED

Every figure is returned BOTH unrounded and rounded to the penny. A penny of difference between two
correct computations that rounded in a different order is not a defect, and a comparison that
cannot tell that apart will report hundreds of them on its first run and be switched off.
"""
from __future__ import annotations

import ast
import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
COMMONS = PROJECT_DIR / "docs" / "domain_artefact_library" / "regulatory"

RECONSTRUCTED = "RECONSTRUCTED"
#: The bill does not record the rate and no published artefact supplies it. Not a failure of this
#: module and not a pass either -- a third answer, which is the only honest one.
UNCHECKABLE = "UNCHECKABLE"
#: The amount cannot be rebuilt, but the RATE it should have used is published and was checked.
RATE_CHECKED = "RATE_CHECKED"

PENNY = 0.005

#: HOW MONEY IS ROUNDED, DECLARED, because the comparison found that neither side had declared it
#: and they differed (2026-09-03).
#:
#: WHAT WAS MEASURED. The first full comparison filed 310 differences over 11,549 bills. Every one
#: was exactly ONE PENNY, and the 15 on the two reconstructible money lines were 15 out of 15 in
#: the biller's favour -- a one-sidedness that reads like a systematic overcharge and is not one.
#: Every single instance sits on an exact half-penny (38.735, 11.625, ...), where Python's builtin
#: `round()` applies BANKER'S rounding and goes to the even penny. The validator was wrong, not the
#: biller: `saas/money.quantize_gbp` states ROUND_HALF_UP in `Decimal` and gives the reason --
#: *"Python's builtin round() is banker's rounding"* -- and it was right.
#:
#: THIS IS THE §4.4 CASE THE BRIEF ANTICIPATED: *"Where the validator is shown to be wrong, that is
#: itself a finding -- about the published rules, the export's completeness, or an ambiguity in a
#: concept."* The concept is HOW MONEY IS ROUNDED. **No published artefact in the commons states
#: one**, and the raw export carries no rounding rule either, so each side silently inherited
#: whatever its language did. That is a gap in the knowledge layer and it is filed as one.
#:
#: AND THE CONVENTION IS DECLARED HERE RATHER THAN IMPORTED, which is the curtain doing its job in
#: the awkward direction. `saas/money` has exactly this function and this module may not import it.
#: Copying the RULE (half-up to the penny, the ordinary commercial convention) is legitimate;
#: importing the implementation would make the reconstruction agree with the biller by construction
#: on every boundary, which is the tautology the whole exercise exists to avoid. If the rule itself
#: is wrong, both sides are wrong together and this module cannot catch it -- see
#: `docs/design/WHAT_THE_BILL_VALIDATION_CANNOT_CATCH.md`.
ROUNDING = "ROUND_HALF_UP to the penny"
ROUNDING_SOURCE = (
    "DECLARED BY THIS MODULE, NOT READ FROM A PUBLISHED RECORD. No artefact in "
    "docs/domain_artefact_library/regulatory/ states a rounding convention for a domestic energy "
    "bill, so this is the ordinary commercial half-up rule written down rather than a rule "
    "fetched. It is the one input to this reconstruction that is a convention of ours."
)


def _dec(value) -> Decimal:
    """A decimal number as the decimal number a human sees, never as its binary approximation.

    `Decimal(0.1)` is 0.1000000000000000055511151231257827021181583404541015625; `Decimal("0.1")`
    is 0.1. Every quantity on a bill -- a meter reading, a unit rate, a daily standing charge --
    is a decimal printed to a stated number of places, so `str()` is the faithful reading and the
    float constructor is the lossy one.
    """
    return Decimal(str(value))


def round_money(value: float) -> float:
    """Quantize GBP to the penny, ROUND_HALF_UP -- see `ROUNDING` for why not `round()`.

    Via `Decimal(str(value))` and not `Decimal(value)`: the latter reads the binary float's exact
    value, so 38.735 arrives as 38.73499999999999943... and rounds DOWN under half-up too,
    reproducing the banker's-rounding answer through a different door. `str()` reads the decimal
    number a human sees, which is what a printed bill is.
    """
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


class CurtainBreached(Exception):
    """This module reached into the code it exists to check independently."""


# ── THE CURTAIN, as a property of this file rather than a promise about it ───────────────────
def imports_into_the_repository(module_path: Path | None = None) -> list[str]:
    """Every import in this module that resolves to repository code. `[]` is the curtain intact.

    Reads its own AST, including imports nested inside functions -- a local `import` is the obvious
    way this rots, and a module-header check would never see it. Any name whose first segment
    matches a top-level package of this repository counts, not just the billing ones: a chain three
    modules long ends up back at `saas.money` and nobody notices.
    """
    path = module_path or Path(__file__)
    roots = {p.name for p in PROJECT_DIR.iterdir()
             if p.is_dir() and (p / "__init__.py").exists()} | {
        "company", "saas", "simulation", "tools", "background", "site"}
    tree = ast.parse(path.read_text(encoding="utf-8"))
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in roots:
                    hits.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            # `from . import x` (level > 0) is a repository import by definition.
            if node.level:
                hits.append("." * node.level + (node.module or ""))
            elif node.module and node.module.split(".")[0] in roots:
                hits.append(node.module)
    return sorted(set(hits))


def assert_curtain(module_path: Path | None = None) -> None:
    breaches = imports_into_the_repository(module_path)
    if breaches:
        raise CurtainBreached(
            "this validator imports repository code, so its agreement with the biller would be "
            "worth nothing: {}".format(", ".join(breaches)))


# ── the published law, read as DATA ──────────────────────────────────────────────────────────
def _published(name: str) -> dict:
    """One commons artefact. Raises rather than defaulting: a validator that silently fell back to
    a built-in rate would be checking us against ourselves while reporting that it had not."""
    path = COMMONS / name
    if not path.exists():
        raise FileNotFoundError(
            "the published artefact {} is not in the commons, so the rate it carries cannot be "
            "obtained independently -- refusing to substitute one".format(path))
    return json.loads(path.read_text(encoding="utf-8"))


def statutory_vat_rate(*, segment: str, commodity: str, kwh: float, days: float) -> dict:
    """The VAT rate the published law says applies — derived from the record, never from us.

    Two artefacts and they do different jobs, which their own text is careful about: `uk_vat_rates`
    is THE LAW (the three rates), `vat_fuel_and_power_de_minimis` is the rule for WHICH one a fuel
    and power supply attracts. Reading either alone gives a confident wrong answer.

    The reading, in one line from the notice: a supply to BUSINESS premises at or below the fuel's
    de minimis rate is reduced-rated; above it, standard. DOMESTIC supply is reduced-rated whatever
    the quantity.

    Returns the rate with the reason it applies, because a validator that says "5%" and not "5%
    because domestic supply is reduced-rated regardless of quantity" cannot be argued with.
    """
    rates = _published("uk_vat_rates.json")["rates"]
    reduced, standard = rates["reduced"]["rate"], rates["standard"]["rate"]
    if segment == "resi":
        return {"rate": reduced, "why": "domestic supply is reduced-rated regardless of quantity",
                "source": "vat_fuel_and_power_de_minimis.json / uk_vat_rates.json"}
    limits = _published("vat_fuel_and_power_de_minimis.json")["de_minimis_by_fuel"]
    fuel = limits.get(commodity)
    if fuel is None or not days:
        return {"rate": None, "why": "no published de minimis for commodity {!r}".format(commodity),
                "source": "vat_fuel_and_power_de_minimis.json"}
    per_day = kwh / days
    limit = fuel["kwh_per_day"]
    if per_day <= limit:
        return {"rate": reduced,
                "why": "business supply averaging {:.1f} kWh/day is at or below the published "
                       "de minimis of {} kWh/day".format(per_day, limit),
                "source": "vat_fuel_and_power_de_minimis.json"}
    return {"rate": standard,
            "why": "business supply averaging {:.1f} kWh/day exceeds the published de minimis of "
                   "{} kWh/day".format(per_day, limit),
            "source": "vat_fuel_and_power_de_minimis.json"}


# ── the reconstruction ───────────────────────────────────────────────────────────────────────
def _volume_from_reads(period: dict) -> tuple[float | None, str]:
    """The period's volume, SUBTRACTED by this module from the two exported readings.

    `volume_basis` is the raw export's own declaration of whether that is possible, so this never
    has to infer it. Where it says the readings are absent, our figure is all anyone has and using
    it is not a reconstruction -- it is being told the answer, and it is reported as such.
    """
    basis = period.get("volume_basis")
    if basis != "reads":
        return None, "the raw export could not supply readings for this period ({})".format(basis)
    reads = period.get("reads") or []
    if len(reads) != 2:
        return None, "expected an opening and a closing reading, got {}".format(len(reads))
    opening, closing = reads[0].get("read_kwh"), reads[1].get("read_kwh")
    if opening is None or closing is None:
        return None, "a reading has no value"
    # SUBTRACTED IN DECIMAL, AND THE COMPARISON IS WHAT FOUND OUT WHY (2026-09-03). A meter
    # reading is a decimal number printed on a bill, and `8303.3 - 8090.8` is exactly 212.5 kWh.
    # In binary float it is 212.4999999999991, which at 19.08p/kWh makes the energy line
    # GBP 40.544999999999824 instead of exactly GBP 40.545 -- so it falls a hair BELOW the
    # half-penny boundary and rounds down, against a biller that gets 40.55. One bill in 11,549
    # differed for that reason and for no other, and no test in this tree would ever have found
    # it: the inputs are ordinary, the arithmetic is right, and the answer is a penny out.
    #
    # `Decimal(str(x))` reads the number a human sees rather than the binary approximation, which
    # is the same reason `round_money` uses it. The float is returned because every caller wants a
    # float; what must not happen in float is the SUBTRACTION.
    volume = Decimal(str(closing)) - Decimal(str(opening))
    return float(volume), ""


def rebuild_period(period: dict, *, segment: str) -> dict:
    """One period rebuilt from raw facts alone. Never raises; every line says what it is."""
    volume, why_not = _volume_from_reads(period)
    days = period.get("days_in_period")
    rate_p = period.get("unit_rate_p_per_kwh")
    sc_day = period.get("standing_charge_gbp_per_day")

    lines: list[dict] = []
    if volume is None or rate_p is None:
        lines.append({"label": "Energy", "status": UNCHECKABLE,
                      "why": why_not or "no unit rate in the raw export"})
    else:
        # IN DECIMAL ALL THE WAY TO THE PENNY, and fixing only the subtraction was not enough --
        # measured, twice, on the same run. `212.5 * 19.08 / 100` in float is
        # 40.544999999999995, a hair BELOW the exact 40.545, so it rounds down and disagrees by a
        # penny; and repairing the subtraction alone moved a SECOND bill from agreeing-by-luck
        # (its float volume happened to land ABOVE its boundary) to disagreeing. A decimal
        # quantity times a decimal rate has to stay decimal until it is quantized, or
        # `Decimal(str(...))` faithfully reads back the error the float multiply just introduced.
        amount = float(_dec(volume) * _dec(rate_p) / 100)
        lines.append({"label": "Energy", "status": RECONSTRUCTED,
                      "amount_gbp": round_money(amount), "amount_gbp_unrounded": amount,
                      "volume_kwh": volume,
                      "how": "({} - {}) kWh x {} p/kWh / 100".format(
                          (period.get("reads") or [{}])[-1].get("read_kwh"),
                          (period.get("reads") or [{}])[0].get("read_kwh"), rate_p)})

    if days is None or sc_day is None:
        lines.append({"label": "Standing charge", "status": UNCHECKABLE,
                      "why": "the raw export carries no day count or no daily rate"})
    else:
        amount = float(_dec(days) * _dec(sc_day))
        lines.append({"label": "Standing charge", "status": RECONSTRUCTED,
                      "amount_gbp": round_money(amount), "amount_gbp_unrounded": amount,
                      "how": "{} days x GBP {}/day".format(days, sc_day)})

    lines.append({
        "label": "Network and policy costs", "status": UNCHECKABLE,
        "why": "the issued bill does not record the levy rate, and the commons carries only the "
               "Renewables Obligation and the Climate Change Levy while this figure bundles DUoS, "
               "TNUoS, BSUoS, RO, FiT, CfD, CM and smart metering. There is no published artefact "
               "to rebuild it from, so it is not rebuilt."})

    vat = statutory_vat_rate(segment=segment, commodity=period.get("commodity") or "electricity",
                             kwh=volume or 0.0, days=days or 0.0)
    lines.append({
        "label": "VAT", "status": RATE_CHECKED if vat["rate"] is not None else UNCHECKABLE,
        "statutory_rate": vat["rate"], "why": vat["why"], "source": vat["source"],
        "amount_note": "the AMOUNT is not rebuilt: its base includes the network and policy line "
                       "above, which is uncheckable. The RATE is derived from the published law "
                       "and can disagree with the rate the bill used."})

    return {"period_start": period.get("period_start"), "period_end": period.get("period_end"),
            "lines": lines,
            "rounding": ROUNDING,
            "reconstructed_subtotal_gbp": round_money(sum(
                ln.get("amount_gbp_unrounded", 0.0) for ln in lines
                if ln["status"] == RECONSTRUCTED))}


def rebuild(raw_export: dict) -> dict:
    """The whole account, rebuilt from the raw export and the published record, and nothing else.

    The curtain is asserted HERE, at the entry point, and not only in a test. A validator whose
    independence is checked by a test somebody remembers to run is a validator whose independence
    is checked when it does not matter.
    """
    assert_curtain()
    segment = raw_export.get("segment") or "resi"
    return {
        "customer_id": raw_export.get("customer_id"),
        "segment": segment,
        "periods": [rebuild_period(p, segment=segment) for p in raw_export.get("periods") or []],
        "curtain": "no repository imports; the published record read as data from {}".format(
            COMMONS.relative_to(PROJECT_DIR)),
    }


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("raw_export", type=Path, help="a raw export JSON file (never a ledger)")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
    built = rebuild(json.loads(args.raw_export.read_text()))
    text = json.dumps(built, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
        print("wrote {} ({} period(s))".format(args.out, len(built["periods"])))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
