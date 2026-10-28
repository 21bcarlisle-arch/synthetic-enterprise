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
    Unit charge       volume x CONTRACTED rate      CONTRACT_CHECKED, per printed rate line across a
                                                      price change; BOUNDED where none is printed
    Default-tariff    term rate <= Ofgem cap        CAP_CHECKED; UNCHECKABLE where the commons has
      term rate         (ex-VAT, per window)          no level; NOT_APPLICABLE off a domestic default
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
from datetime import date, timedelta
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

#: The unit charge was priced against the rate in the account's TERM RECORD, not the printed rate.
CONTRACT_CHECKED = "CONTRACT_CHECKED"
#: The period crosses a price change and the bill prints one rate, so only a range can be checked:
#: the charge must sit between every covering term's rate times the volume.
BOUNDED = "BOUNDED"

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
    # An actual bill after an estimated run opens on the last estimated reading: the reads also
    # span its catch-up line, which is priced as the correction it prints, not at this period's rate.
    if period.get("catchup_kwh") is not None:
        volume -= Decimal(str(period["catchup_kwh"]))
    return float(volume), ""


def _energy_per_register(period: dict) -> tuple[dict, float | None]:
    """A multi-rate period's energy line: each register's own advance at its own rate.

    The bill prints one line per register at a penny, and its energy total is their sum, so each
    register is quantized before summing. Every register must have exactly two readings and a
    rate; one missing makes the whole line uncheckable rather than a partial sum, which would
    report the missing band as a shortfall in the biller.
    """
    rates = {r.get("register_id"): r.get("unit_rate_p_per_kwh")
             for r in period.get("registers") or []}
    if period.get("volume_basis") != "reads":
        return ({"label": "Energy", "status": UNCHECKABLE,
                 "why": "the raw export could not supply readings for this period ({})".format(
                     period.get("volume_basis"))}, None)
    by_register: dict = {}
    for read in period.get("reads") or []:
        by_register.setdefault(read.get("register_id"), []).append(read.get("read_kwh"))
    if set(by_register) != set(rates):
        return ({"label": "Energy", "status": UNCHECKABLE,
                 "why": "readings for registers {} but rates for {}".format(
                     sorted(map(str, by_register)), sorted(map(str, rates)))}, None)
    total_kwh, total_gbp, hows = Decimal(0), 0.0, []
    for reg_id, reads in by_register.items():
        rate_p = rates[reg_id]
        if len(reads) != 2 or None in reads or rate_p is None:
            return ({"label": "Energy", "status": UNCHECKABLE,
                     "why": "register {} has {} reading(s) and rate {}".format(
                         reg_id, len(reads), rate_p)}, None)
        kwh = Decimal(str(reads[1])) - Decimal(str(reads[0]))
        total_kwh += kwh
        total_gbp += round_money(float(kwh * _dec(rate_p) / 100))
        hows.append("({} - {}) kWh x {} p/kWh / 100".format(reads[1], reads[0], rate_p))
    amount = round_money(total_gbp)
    return ({"label": "Energy", "status": RECONSTRUCTED, "amount_gbp": amount,
             "amount_gbp_unrounded": amount, "volume_kwh": float(total_kwh),
             "how": " + ".join(hows)}, float(total_kwh))


def _volume_by_label(period: dict) -> tuple[dict | None, str]:
    """Each register's advance from its own two readings, keyed by the label the bill prints."""
    registers = period.get("registers") or []
    if len(registers) <= 1:
        volume, why = _volume_from_reads(period)
        if volume is None:
            return None, why
        label = (registers[0].get("register_label") if registers else None) or \
            ((period.get("reads") or [{}])[0].get("register_label")) or "Anytime"
        return {label: Decimal(str(volume))}, ""
    if period.get("volume_basis") != "reads":
        return None, "the raw export could not supply readings ({})".format(
            period.get("volume_basis"))
    label_of = {r.get("register_id"): r.get("register_label") for r in registers}
    by_register: dict = {}
    for read in period.get("reads") or []:
        by_register.setdefault(read.get("register_id"), []).append(read.get("read_kwh"))
    out = {}
    for reg_id, reads in by_register.items():
        if len(reads) != 2 or None in reads or label_of.get(reg_id) is None:
            return None, "register {} has {} reading(s) and no usable label".format(
                reg_id, len(reads))
        out[label_of[reg_id]] = Decimal(str(reads[1])) - Decimal(str(reads[0]))
    return out, ""


def _contracted_rate(term: dict, label: str):
    """The rate a register is contracted at: its band's rate on a Peak or Off-peak register of a
    term that carries a pair, else the term's flat rate."""
    for band in term.get("tou_unit_rates") or []:
        if band.get("register_label") == label:
            return band.get("unit_rate_p_per_kwh")
    return term.get("unit_rate_p_per_kwh")


def unit_charge_at_contract(period: dict) -> dict:
    """The unit charge the TARIFF says this period costs: volume x the term record's rate.

    The energy line above prices with the rate the bill printed, which is fitted to the printed
    pair, so it proves the arithmetic and cannot see a bill that charged the wrong tariff. This is
    the second computation that can. It is ALL-IN, because the rate a term is sold at is: the bill
    prints its network-and-policy share (and, in an EPG window, the Treasury's share) as separate
    lines, so the comparison sets this against those lines summed with the energy line.

    One covering term: each register at its contracted rate, with a tolerance for what printing
    rounds (0.05 kWh a register, a penny a money line). Two or more: the bill crosses a price change
    and, where it prints a line per rate, each line's own advance is priced at its own term's rate
    (`_unit_charge_per_rate_line`). Where it prints one rate it is BOUNDED by the lowest and highest
    contracted rate times the volume, which is weaker and says so. A term with no single rate is
    UNCHECKABLE.
    """
    label = "Unit charge at the contracted tariff"
    terms = period.get("contracted_terms")
    if terms is None:
        return {"label": label, "status": UNCHECKABLE,
                "why": "the raw export carries no term record for this period"}
    if not terms:
        return {"label": label, "status": UNCHECKABLE,
                "why": "no recorded term covers this period"}
    volumes, why = _volume_by_label(period)
    if volumes is None:
        return {"label": label, "status": UNCHECKABLE, "why": why}
    unrated = [t.get("tariff_type") for t in terms if t.get("unit_rate_p_per_kwh") is None]
    if unrated:
        return {"label": label, "status": UNCHECKABLE,
                "why": "a covering term ({}) was sold at no single rate".format(", ".join(
                    map(str, unrated)))}
    per_term = []
    for term in terms:
        amount, hows = Decimal(0), []
        for reg_label, kwh in volumes.items():
            rate = _contracted_rate(term, reg_label)
            amount += kwh * _dec(rate) / 100
            hows.append("{} kWh {} x {} p/kWh".format(kwh, reg_label, rate))
        per_term.append((float(amount), hows, term))
    # Print rounding: each register's kWh is the difference of two cumulative reads printed to
    # 0.1 kWh, so it sits up to 0.1 kWh from the volume charged (0.05 allowed 3 Jan 2023 bills at
    # 64p to fail by 7p on an exact rate); the energy, levy and EPG lines are each half a penny.
    rates = [_dec(r) for t in terms for r in [t.get("unit_rate_p_per_kwh")] + [
        b.get("unit_rate_p_per_kwh") for b in t.get("tou_unit_rates") or []]]
    tolerance = round(float(Decimal("0.1") * len(volumes) * max(rates) / 100) + 3 * PENNY, 4)
    if len(per_term) == 1:
        amount, hows, term = per_term[0]
        return {"label": label, "status": CONTRACT_CHECKED, "amount_gbp": round_money(amount),
                "amount_gbp_unrounded": amount, "tolerance_gbp": tolerance,
                "how": "{} ({} term from {})".format(" + ".join(hows), term.get("tariff_type"),
                                                    term.get("tariff_effective_from"))}
    volume = sum(volumes.values())
    checked, why_bounded = _unit_charge_per_rate_line(label, period.get("rate_lines"), terms,
                                                      volume, rates)
    if checked is not None:
        return checked
    # Across a price change the bill prints one register, so a ToU term's share could have been
    # charged anywhere between its off-peak and peak rates: the bound spans every rate any
    # covering term carries.
    low, high = float(volume * min(rates) / 100), float(volume * max(rates) / 100)
    return {"label": label, "status": BOUNDED, "low_gbp": round_money(low),
            "high_gbp": round_money(high), "tolerance_gbp": tolerance,
            "how": "the period crosses {} terms ({}) and {}".format(
                len(terms), ", ".join("{} from {}".format(t.get("tariff_type"),
                                                         t.get("tariff_effective_from"))
                                      for t in terms), why_bounded)}


def _unit_charge_per_rate_line(label, lines, terms, volume, rates):
    """A bill across a price change that prints a line per rate: each line's own advance, from its
    own two readings, at the rate of the term it names. Returns (result, None), or (None, why) where
    only the bound can be checked.

    This is what makes the check a CONTRACT_CHECK and not a range: a bill that charged the whole
    period at either rate, or split the kWh wrongly between them, disagrees, where the bound let any
    charge between the two rates through. A line whose term carries a peak/off-peak pair is still
    bounded, because the bill does not print that line's band split.
    """
    if not lines:
        return None, "the bill prints one rate"
    by_start = {t.get("tariff_effective_from"): t for t in terms}
    amount, line_volume, hows = Decimal(0), Decimal(0), []
    for line in lines:
        term = by_start.get(line.get("tariff_effective_from"))
        if term is None:
            return ({"label": label, "status": UNCHECKABLE,
                     "why": "a printed rate line names a term from {} that no recorded term "
                            "starts on".format(line.get("tariff_effective_from"))}, None)
        if term.get("tou_unit_rates"):
            return None, ("the line from {} is on a time-of-use term and the bill does not print "
                          "its band split".format(line.get("tariff_effective_from")))
        reads = [r.get("read_kwh") for r in line.get("reads") or []]
        if len(reads) != 2 or None in reads:
            return ({"label": label, "status": UNCHECKABLE,
                     "why": "the rate line from {} has {} usable reading(s)".format(
                         line.get("tariff_effective_from"), len([r for r in reads if r is not None]))},
                    None)
        kwh = Decimal(str(reads[1])) - Decimal(str(reads[0]))
        line_volume += kwh
        amount += kwh * _dec(term.get("unit_rate_p_per_kwh")) / 100
        hows.append("{} kWh x {} p/kWh ({} from {})".format(
            kwh, term.get("unit_rate_p_per_kwh"), term.get("tariff_type"),
            term.get("tariff_effective_from")))
    # The lines must account for the period's whole advance, or the check prices part of it.
    if abs(line_volume - Decimal(str(volume))) > Decimal("0.05"):
        return ({"label": label, "status": UNCHECKABLE,
                 "why": "the rate lines advance {} kWh and the period's readings {}".format(
                     line_volume, volume)}, None)
    tolerance = round(float(Decimal("0.1") * len(lines) * max(rates) / 100) + 3 * PENNY, 4)
    return ({"label": label, "status": CONTRACT_CHECKED, "amount_gbp": round_money(float(amount)),
             "amount_gbp_unrounded": float(amount), "tolerance_gbp": tolerance,
             "how": " + ".join(hows)}, None)


#: Default tariffs, which SLC 28AD caps. A fixed or chosen term may lawfully sit above the cap.
DEFAULT_TARIFF_TYPES = ("svt", "deemed")
#: The term rate is printed to 4 dp from a GBP/MWh strike, so one struck exactly at the cap reads
#: up to half that place above it.
CAP_RATE_TOLERANCE_P = 0.0001
CAP_CHECKED = "CAP_CHECKED"
#: Fixed term, non-domestic account, or a date before the cap existed: no claim, not a pass.
NOT_APPLICABLE = "NOT_APPLICABLE"


def _vat_on(commodity: str, day: str) -> float:
    """The domestic VAT rate on `day` for the fuel: reduced, unless a dated exception covers it."""
    law = _published("uk_vat_rates.json")
    for exc in law.get("dated_exceptions") or []:
        if exc.get("fuel") == commodity and exc["from"] <= day <= exc["to"]:
            return law["rates"][exc["rate_band"]]["rate"]
    return law["rates"]["reduced"]["rate"]


def published_cap_ceilings(commodity: str, first: str, last: str, *, multi_register: bool):
    """Every Ofgem level in force between two dates, ex-VAT p/kWh, as (from, to, ceiling, how).

    The Ofgem level, never the EPG: the cap bounded what the supplier charged, and the EPG was the
    Treasury's discount on top, so a term struck at the cap with the receipt inside it is lawful.
    A day after the last published window has no level, and carrying the last one forward is the
    company's reading, not the law; that day comes back with ceiling None and the reason.
    """
    windows = _published("ofgem_default_tariff_cap_windows.json")["windows"]
    if multi_register:
        if commodity != "electricity":
            return [(first, last, None, "no multi-register cap is published for {}".format(
                commodity))]
        rows = [(p["from"], p["to"], p["multi_register_p_per_kwh_ex_vat"],
                 "multi-register {} p/kWh ex-VAT, cap level model".format(
                     p["multi_register_p_per_kwh_ex_vat"]))
                for p in _published("ofgem_cap_multi_register_unit_rates.json")["periods"]]
    else:
        key = "elec" if commodity == "electricity" else "gas"
        rows = []
        for w in windows:
            vat = _vat_on(commodity, w["from"])
            rows.append((w["from"], w["to"], float(_dec(w[key]) / 10 / (1 + _dec(vat))),
                         "{} GBP/MWh inc {:.0%} VAT".format(w[key], vat)))
    out = [r for r in sorted(rows) if r[0] <= last and first <= r[1]]
    covered_to = max([r[1] for r in out], default=None)
    if covered_to is None or covered_to < last:
        why = ("the commons carries no multi-register level after {} (P15b changed the benchmark "
               "and the model does not state it)".format(covered_to) if multi_register else
               "no published cap window covers {} onwards".format(covered_to or first))
        out.append((covered_to or first, last, None, why))
    return out


def default_tariff_rate_against_cap(period: dict, *, segment: str) -> dict:
    """Each default-tariff term's contracted rate, against Ofgem's published cap for its window.

    The contract check above proves the bill charges the term record's rate, and the term record is
    ours, so a mis-set default rate passes it. The cap is the outside source that bounds that rate.
    Only the days of the term inside this period are graded, against every window they touch.
    Multi-register when the period prints more than one register (SLC 28AD.4 grades every
    multi-register tariff against that benchmark).
    """
    label = "Default-tariff rate against the published cap"
    terms = [t for t in period.get("contracted_terms") or []
             if t.get("tariff_type") in DEFAULT_TARIFF_TYPES]
    if segment != "resi" or not terms:
        return {"label": label, "status": NOT_APPLICABLE,
                "why": "the cap binds a domestic default tariff only"}
    commodity = period.get("commodity") or "electricity"
    multi = len(period.get("registers") or []) > 1
    p_start, p_end = str(period.get("period_start"))[:10], str(period.get("period_end"))[:10]
    cap_began = min(w["from"] for w in _published("ofgem_default_tariff_cap_windows.json")["windows"])
    graded, blind = [], []
    for term in terms:
        rate = term.get("unit_rate_p_per_kwh")
        first = max(p_start, str(term.get("tariff_effective_from"))[:10], cap_began)
        # A term's `tariff_effective_to` is the next term's first day, so its own last day is the one before.
        last = min(p_end, (date.fromisoformat(str(term.get("tariff_effective_to"))[:10])
                           - timedelta(days=1)).isoformat())
        if first > last:
            continue
        if rate is None:
            blind.append("a {} term carries no single rate".format(term.get("tariff_type")))
            continue
        for w_from, w_to, ceiling, how in published_cap_ceilings(
                commodity, first, last, multi_register=multi):
            if ceiling is None:
                blind.append(how)
                continue
            graded.append({"tariff_effective_from": term.get("tariff_effective_from"),
                           "rate_p_per_kwh": rate, "ceiling_p_per_kwh": round(ceiling, 4),
                           "window": "{}..{}".format(w_from, w_to), "how": how,
                           "within": float(rate) <= ceiling + CAP_RATE_TOLERANCE_P})
    if blind:
        return {"label": label, "status": UNCHECKABLE, "why": "; ".join(sorted(set(blind))),
                "graded": graded}
    if not graded:
        return {"label": label, "status": NOT_APPLICABLE,
                "why": "the default term's days in this period predate the cap ({})".format(cap_began)}
    return {"label": label, "status": CAP_CHECKED, "graded": graded,
            "within": all(g["within"] for g in graded),
            "worst_ratio": max(float(g["rate_p_per_kwh"]) / g["ceiling_p_per_kwh"]
                               for g in graded)}


def published_cost_floors(commodity: str, first: str, last: str, *, multi_register: bool):
    """Each cap window between two dates, as (from, to, floor p/kWh ex-VAT or None, how).

    The floor is the cost the cap passes through per unit in Ofgem's own cap model for that window:
    commodity (DF + CM), network (NC) and policy (PC), benchmark minus nil over the benchmark kWh.
    It is the LOWEST over the three payment methods and the fifteen region rows, so a rate under it
    is under that cost in every region and method. Operating cost, EBIT and headroom are not in it.
    Single-rate electricity and gas. Multi-register is a GAP: a per-register rate against a blended
    benchmark floor is not a quantity, since an off-peak rate is lawfully under it.
    """
    windows = _published("ofgem_default_tariff_cap_windows.json")["windows"]
    if multi_register:
        return [(first, last, None,
                 "the commons carries no per-register cost floor for multi-register electricity")]
    artefact = _published("ofgem_cap_unit_rate_composition.json")
    by_method = artefact["by_payment_method" if commodity == "electricity"
                         else "gas_by_payment_method"]
    out = []
    for w in windows:
        if not (w["from"] <= last and first <= w["to"]):
            continue
        figures = []
        for method in by_method.values():
            row = next((p for p in method["periods"] if p["starts"] == w["from"]), None)
            if row is not None and row.get("pass_through_p_per_kwh_ex_vat_min") is not None:
                figures.append(row["pass_through_p_per_kwh_ex_vat_min"])
        out.append((w["from"], w["to"], min(figures) if len(figures) == len(by_method) else None,
                    "lowest DF+CM+NC+PC unit-rate allowance, ex-VAT, over payment methods and "
                    "regions" if len(figures) == len(by_method) else
                    "the cap model carries no {} cost floor for the window from {}".format(
                        commodity, w["from"])))
    covered_to = max([r[1] for r in out], default=None)
    if covered_to is None or covered_to < last:
        out.append((covered_to or first, last, None,
                    "no published cap window covers {} onwards".format(covered_to or first)))
    return out


def default_tariff_rate_against_wholesale_floor(period: dict, *, segment: str) -> dict:
    """Each default-tariff term's contracted rate, against the commodity cost its cap window allows.

    `default_tariff_rate_against_cap` bounds the rate from above; a rate set too low passed it. A
    default tariff priced under the energy, network and policy cost the cap itself passes through
    is a loss before any operating cost, so it is flagged (see `published_cost_floors`). Fails
    closed (UNCHECKABLE, naming the gap) wherever the commons carries no floor.
    """
    label = "Default-tariff rate against the wholesale floor"
    terms = [t for t in period.get("contracted_terms") or []
             if t.get("tariff_type") in DEFAULT_TARIFF_TYPES]
    if segment != "resi" or not terms:
        return {"label": label, "status": NOT_APPLICABLE,
                "why": "the cap binds a domestic default tariff only"}
    commodity = period.get("commodity") or "electricity"
    multi = len(period.get("registers") or []) > 1
    p_start, p_end = str(period.get("period_start"))[:10], str(period.get("period_end"))[:10]
    cap_began = min(w["from"] for w in _published("ofgem_default_tariff_cap_windows.json")["windows"])
    graded, blind = [], []
    for term in terms:
        rate = term.get("unit_rate_p_per_kwh")
        first = max(p_start, str(term.get("tariff_effective_from"))[:10], cap_began)
        last = min(p_end, (date.fromisoformat(str(term.get("tariff_effective_to"))[:10])
                           - timedelta(days=1)).isoformat())
        if first > last:
            continue
        if rate is None:
            blind.append("a {} term carries no single rate".format(term.get("tariff_type")))
            continue
        for w_from, w_to, floor, how in published_cost_floors(
                commodity, first, last, multi_register=multi):
            if floor is None:
                blind.append(how)
                continue
            graded.append({"tariff_effective_from": term.get("tariff_effective_from"),
                           "rate_p_per_kwh": rate, "floor_p_per_kwh": round(floor, 4),
                           "window": "{}..{}".format(w_from, w_to), "how": how,
                           "above": float(rate) >= floor})
    if blind:
        return {"label": label, "status": UNCHECKABLE, "why": "; ".join(sorted(set(blind))),
                "graded": graded}
    if not graded:
        return {"label": label, "status": NOT_APPLICABLE,
                "why": "the default term's days in this period predate the cap ({})".format(cap_began)}
    return {"label": label, "status": CAP_CHECKED, "graded": graded,
            "above": all(g["above"] for g in graded),
            "lowest_ratio": min(float(g["rate_p_per_kwh"]) / g["floor_p_per_kwh"] for g in graded)}


def rebuild_period(period: dict, *, segment: str) -> dict:
    """One period rebuilt from raw facts alone. Never raises; every line says what it is."""
    days = period.get("days_in_period")
    rate_p = period.get("unit_rate_p_per_kwh")
    sc_day = period.get("standing_charge_gbp_per_day")

    lines: list[dict] = []
    if len(period.get("registers") or []) > 1:
        energy, volume = _energy_per_register(period)
        lines.append(energy)
    elif (single := _volume_from_reads(period))[0] is None or rate_p is None:
        volume, why_not = single
        lines.append({"label": "Energy", "status": UNCHECKABLE,
                      "why": why_not or "no unit rate in the raw export"})
    else:
        volume = single[0]
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

    lines.append(unit_charge_at_contract(period))
    lines.append(default_tariff_rate_against_cap(period, segment=segment))
    lines.append(default_tariff_rate_against_wholesale_floor(period, segment=segment))

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
