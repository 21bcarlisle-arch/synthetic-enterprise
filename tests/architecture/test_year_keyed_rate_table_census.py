"""Every year-keyed rate table in the repo is classified — discovered by AST, not by `vars()`.

THE DEFECT THIS EXISTS FOR (2026-08-19,
WORKER_FINDING_THE_REPORTS_RO_OBSERVATORY_PUBLISHES_TEN_YEARS_OF_RATES_THAT_MATCH_NO_PUBLICATION).
`docs/reports/ANNUAL_REPORT.md`'s "RO Cost Observatory" published ten years of obligation
levels and buy-out prices that matched no publication on either column, understating the RO
line by GBP486,458.88 (27.74%) against the RO cost the same run charged. Two R10 class
controls already governed exactly that defect family — `test_policy_cost_year_basis.py`
(discovers via `vars(policy_costs)`) and `test_policy_cost_values_vs_source.py` (classifies
everything in `policy_costs.YEAR_KEY_BASIS`). Neither could name the offending tables, not by
omission but BY CONSTRUCTION: they live in `company/regulatory/`, and both enumerators are
scoped to one module.

    A register of unverified constants inherits the blindness of its own enumerator.

So the register said of `_RO_COST_BY_OY_START` "GBP1.72M, the largest line" — and that table
is RIGHT — while the table that was wrong by GBP486k was out of scope and unaddable by any
mutation of either control. The class was scoped as "tables in this module" rather than
"year-keyed rate tables"; this file is the enumerator both controls should have had.

WHAT THE CENSUS MEASURED ON ITS FIRST RUN. 61 year-keyed rate tables across `simulation/`,
`company/` and `saas/` — against a register that enumerated 13, one module's worth. The
finding said the unregistered population was "unknown and at least two". It is 47. Among
them: a THIRD RO obligation-level table (`company/regulatory/renewable_obligation.py`)
carrying levels around 0.09 ROC/MWh against a published 0.47-0.49, three separate readings
of the TNUoS residual, three of the Green Gas Levy, and three of the Capacity Market auction
results — each pair of which is two tables of the same law with different numbers.

DISCOVERY IS THE CONTROL, and it must not be narrower than the thing it governs:
  * module-level dict literals, found by walking the AST of every `.py` file in scope —
    NOT `vars()` of a module, which requires someone to have thought of that module.
  * int keys inside a plausible year range, numeric values, 3+ entries.
  * the value may be spelled as a negative or as arithmetic — see `_is_numeric_literal`,
    which carries the two fail-open shapes this walker's first draft actually had.

STATUSES. Every discovered table carries one:
  * `pinned`             — asserted EQUAL to the regulation commons by leg (a) below. The
                           commons holds the publisher's own units and this file performs the
                           conversion, so the derivation is under test rather than assumed.
  * `published_unpinned` — a real published figure with no commons pin yet. RATCHETED: this
                           count may only go DOWN.
  * `not_published`      — nothing publishes a figure of this table's shape (the company's
                           own tariff, a modelling probability, a representative blend).
                           Requires a reason. NOT ratcheted, and that is a named hole, not an
                           oversight: see `test_the_unratcheted_bucket_is_declared_as_a_hole`.

WHAT THIS FILE DOES NOT CLOSE. `published_unpinned` is 40 tables and only shrinks when
someone fetches a publication; the census makes the gap visible and monotone, it does not
make it closed. And a table whose values are LOADED from the commons (the repaired RO pair)
vanishes from this census entirely, because it is no longer a literal — leg (e) exists so
that "absent" cannot be confused with "unchecked".
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCOPE = ("simulation", "company", "saas")
COMMONS_DIR = ROOT / "docs" / "domain_artefact_library" / "regulatory"
CCL_COMMONS = COMMONS_DIR / "ccl_main_rates.json"
RO_COMMONS = COMMONS_DIR / "ro_obligation_and_buyout.json"

_MIN_YEAR, _MAX_YEAR = 1990, 2100
_MIN_ENTRIES = 3


# ═══════════════════════════════════════════════════════════════════════════════════════════
# DISCOVERY — repo-wide, by AST. The leg the two predecessors could not have.
# ═══════════════════════════════════════════════════════════════════════════════════════════

def _is_numeric_literal(node: ast.AST) -> bool:
    """A numeric value written out in the source, however it is spelled.

    TWO FAIL-OPEN SHAPES LIVE HERE, both found by running the census against the real tree
    rather than against an idea of it, and both pinned by their own mutation below:

      * a NEGATIVE rate is an `ast.UnaryOp`, not an `ast.Constant`. A walk that checks only
        for `Constant` silently skips `_CFD_LEVY_BY_YEAR` (2022: -5.0, the crisis rebate) —
        a table already IN the register the census replaces.
      * a rate written as ARITHMETIC is an `ast.BinOp`. `_GGL_RATE_GBP_PER_METER_YEAR`
        spells every entry `0.576 * 365 / 100`, showing its p/day working. Skipping it would
        drop a whole published levy from the population while the ratchet read green.

    A census that silently drops rows is worse than no census, because its own count is what
    later readers trust.
    """
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        return _is_numeric_literal(node.operand)
    if isinstance(node, ast.BinOp) and isinstance(
        node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)
    ):
        return _is_numeric_literal(node.left) and _is_numeric_literal(node.right)
    return (
        isinstance(node, ast.Constant)
        and isinstance(node.value, (int, float))
        and not isinstance(node.value, bool)
    )


def _is_year_key(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Constant)
        and isinstance(node.value, int)
        and not isinstance(node.value, bool)
        and _MIN_YEAR <= node.value <= _MAX_YEAR
    )


def discover_year_keyed_tables(root: Path = ROOT, scope=SCOPE) -> dict[str, int]:
    """Every module-level year-keyed numeric dict literal in scope.

    Returns {"<repo-relative module>::<NAME>": entry_count}. The key carries the MODULE
    because two tables can share a name — `_GGL_RATE_GBP_PER_METER_YEAR` exists in both
    `simulation/policy_costs.py` and `company/market/gas_network_ledger.py` with different
    values. A bare-name register, which is what `YEAR_KEY_BASIS` is, cannot tell them apart.
    """
    found: dict[str, int] = {}
    for package in scope:
        for path in sorted((root / package).rglob("*.py")):
            try:
                tree = ast.parse(path.read_text())
            except (SyntaxError, UnicodeDecodeError):  # pragma: no cover - none in scope
                continue
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    targets, value = node.targets, node.value
                elif isinstance(node, ast.AnnAssign) and node.value is not None:
                    targets, value = [node.target], node.value
                else:
                    continue
                if not isinstance(value, ast.Dict) or len(value.keys) < _MIN_ENTRIES:
                    continue
                if not all(k is not None and _is_year_key(k) for k in value.keys):
                    continue
                if not all(_is_numeric_literal(v) for v in value.values):
                    continue
                rel = path.relative_to(root).as_posix()
                for target in targets:
                    if isinstance(target, ast.Name):
                        found[f"{rel}::{target.id}"] = len(value.keys)
    return found


# ═══════════════════════════════════════════════════════════════════════════════════════════
# THE REGISTER
# ═══════════════════════════════════════════════════════════════════════════════════════════

# status "pinned": (commons artefact, the conversion this file performs to compare).
# The conversion is NOT in the commons on purpose — see the artefacts' `why_native_units`.
_PINNED: dict[str, str] = {
    "simulation/policy_costs.py::_CCL_ELECTRICITY_RATE_BY_YEAR": "ccl_electricity_gbp_per_mwh",
    "simulation/policy_costs.py::_GAS_CCL_RATE_BY_YEAR": "ccl_gas_gbp_per_mwh",
    "company/regulatory/ccl_ledger.py::_CCL_ELECTRICITY_P_KWH": "ccl_electricity_pence_per_kwh",
    "company/regulatory/ccl_ledger.py::_CCL_GAS_P_KWH": "ccl_gas_pence_per_kwh",
    "simulation/policy_costs.py::_RO_COST_BY_OY_START": "ro_effective_gbp_per_mwh_1dp",
}

# status "published_unpinned": a real publication exists; no commons pin yet. RATCHETED DOWN.
_PUBLISHED_UNPINNED: dict[str, str] = {
    "simulation/policy_costs.py::_CFD_LEVY_BY_YEAR":
        "LCCC/EMRS publish the interim levy rate per quarter; the table is an annual average, "
        "so the pin must carry the averaging as a stated reading.",
    "simulation/policy_costs.py::_NETWORK_COST_RESI_SME_BY_YEAR":
        "GBP869k, the largest unpinned line. DUoS+TNUoS combined across 14 DNO regions; the "
        "tabulated figure is a national blend and no single publication states it.",
    "simulation/policy_costs.py::_DUOS_IC_BY_YEAR":
        "the I&C-connected variant: HV/EHV DUoS tariffs are published per DNO with red/amber/"
        "green time bands, so no published figure has this table's single annual GBP/MWh shape.",
    "simulation/policy_costs.py::_CM_LEVY_BY_YEAR":
        "cites Ofgem Annex 9 v1.8 as GBP/customer/year divided by 3.1 MWh; the divisor is a "
        "reading, so the pin is the Annex 9 row and not the quotient.",
    "simulation/policy_costs.py::_FIT_LEVY_BY_YEAR":
        "Ofgem FIT annual levelisation; published per levelisation period, not per obligation "
        "year, so the pin must carry the period-to-year mapping as a stated reading.",
    "simulation/policy_costs.py::_MUTUALIZATION_LEVY_BY_YEAR":
        "SoLR mutualisation recovery totals are published per event; the table is an allocated "
        "per-MWh figure, so the pin is the event total and the allocation is the reading.",
    "simulation/policy_costs.py::_GAS_NETWORK_COST_BY_YEAR":
        "transportation charges vary by LDZ and exit point; national blend, same shape as the "
        "electricity network tables.",
    "simulation/policy_costs.py::_GGL_RATE_GBP_PER_METER_YEAR":
        "Green Gas Levy is published GBP/meter/DAY by DESNZ in statutory instruments; this "
        "table spells the annualisation in its own values (0.576 * 365 / 100), which is why "
        "discovery has to read arithmetic. A genuinely cheap pin, and the next one to do.",
    "simulation/policy_costs.py::_ELEC_SC_PENCE_PER_DAY_BY_YEAR":
        "Ofgem cap standing charges are published per cap period and per region; the table is a "
        "calendar-year blend, so the pin is the cap-period rows and the blend is the reading.",
    "simulation/policy_costs.py::_GAS_SC_PENCE_PER_DAY_BY_YEAR":
        "the gas half of the above: published per cap period and per region, against a table "
        "keyed by calendar year, so the pin must carry the blending as a stated reading.",
    "simulation/triad.py::_TNUOS_TRIAD_TARIFF_BY_YEAR":
        "NGESO/NESO publish TNUoS Triad tariffs per zone; this table names Zone 14 (London) as "
        "representative, so the pin is the zone row and the representativeness is the reading.",
    "company/market/triad_notification_book.py::_TNUOS_TRIAD_RATE_GBP_PER_KW":
        "the same NESO Transmission Charges statements at a 'representative midlands zone'; two "
        "tables reading one publication at two different zones, neither pinned.",
    "company/market/tnuos_ledger.py::_TNUOS_RESIDUAL_P_PER_KWH":
        "TNUoS residual tariff is published GBP/kW/year per zone; this table is a national "
        "average in p/kWh, so the pin needs the zone rows plus a stated averaging.",
    "company/market/network_charges.py::_TNUOS_PENCE_PER_KWH":
        "a THIRD reading of the TNUoS residual, flat across segments; pinning the publication "
        "once would collapse this and the two above onto one source.",
    "company/market/duos_ledger.py::_DUOS_UNIT_RATE_P_PER_KWH":
        "DUoS charging statements are published per DNO and voltage level; the table's own "
        "comment says 'representative values', which is a reading of 14 published sets.",
    "company/market/bsuos_ledger.py::_BSUOS_RATE_GBP_PER_MWH":
        "NESO publishes BSUoS daily/half-hourly and, from April 2023, as a fixed tariff; the "
        "table is an annual average, so the pin is the tariff rows plus the averaging.",
    "company/market/gas_network_ledger.py::_NTS_RATE_P_PER_KWH":
        "National Gas Transmission publishes NTS entry/exit capacity and commodity charges; the "
        "table is a single blended p/kWh, so the pin needs the charge components named.",
    "company/market/gas_network_ledger.py::_LDZ_RATE_P_PER_KWH":
        "LDZ transportation charges are published per distribution network and load band; this "
        "is a national blend of thirteen published sets.",
    "company/market/gas_network_ledger.py::_GGL_RATE_GBP_PER_METER_YEAR":
        "the SAME Green Gas Levy series as policy_costs' table of the identical name, in a "
        "different module with its own values — the duplicate a bare-name register cannot see.",
    "company/regulatory/green_gas_levy_register.py::_GGL_RATE_GBP_PER_METER_PER_DAY":
        "a THIRD reading of the Green Gas Levy, in GBP/meter/DAY against a Nov-Oct levy year; "
        "its own comment says 'approximate rates calibrated to' the statutory instruments.",
    "company/regulatory/capacity_market.py::_CM_OBLIGATION_RATE_BY_YEAR":
        "NESO publishes CM auction clearing prices per delivery year; the supplier obligation "
        "rate is a derived allocation of those, so the pin is the auction results.",
    "company/market/capacity_market.py::_CM_CLEARING_PRICE_GBP_PER_KW_PER_YEAR":
        "the auction clearing prices themselves, published by NESO per T-4/T-1 auction; "
        "unpinned, and the cheapest CM pin of the three because it is the raw publication.",
    "company/market/ic_flexibility_revenue.py::_CM_DELIVERY_GBP_PER_KW_YR":
        "the same NESO auction results keyed by delivery-year start; a third CM table reading "
        "one publication, which is what pinning it once would collapse.",
    "company/regulatory/fit_book.py::_FIT_LEVELISATION_RATE_PER_MWH":
        "Ofgem FIT levelisation, the company-side twin of policy_costs' _FIT_LEVY_BY_YEAR; "
        "published per levelisation period, so the pin carries the period-to-year mapping.",
    "company/regulatory/warm_home_discount.py::_CORE_DISCOUNT":
        "the WHD core group rebate is set in the Warm Home Discount Regulations each scheme "
        "year; a single statutory GBP figure per year and a cheap pin once the SIs are fetched.",
    "company/regulatory/warm_home_discount.py::_BROADER_DISCOUNT":
        "the broader group rebate from the same Regulations; supplier-set within a statutory "
        "floor before 2022, so the pin must state which of the two regimes each year is under.",
    "company/regulatory/compliance.py::_SMART_METER_TARGETS":
        "Ofgem/DESNZ publish smart meter rollout targets per supplier per year under the "
        "framework licence condition; the table is a market-wide percentage.",
    "company/market/smart_meter_rollout.py::_ANNUAL_TARGETS":
        "the second reading of the same rollout targets, in a different module and unit; both "
        "would collapse onto one pin of the published tolerance levels.",
    "company/finance/corporation_tax.py::_CT_RATE_BY_YEAR":
        "HMRC publishes the CT main rate per financial year in the Finance Acts; a single "
        "statutory rate per year, and the table's own comment admits it excludes the small "
        "profits rate and marginal relief, which is a reading.",
    "company/regulatory/ets_registry.py::_UKETS_PRICE_GBP_PER_TONNE":
        "UK ETS auction clearing prices are published per auction by ICE Futures Europe; the "
        "table is an annual average of those, so the pin is the auction series.",
    "company/regulatory/solr_exposure.py::_SOLR_LEVY_HISTORY_GBP_PER_MWH":
        "Ofgem publishes SoLR levy claim determinations per failed supplier; the table is an "
        "allocated per-MWh figure across all of them, so the pin is the determinations.",
    "company/market/gas_imbalance_ledger.py::_NBP_ANNUAL_GBP_PER_MWH":
        "NBP day-ahead settlement prices are published daily by ICE/Heren; the table is an "
        "annual average, so the pin is the daily series plus the stated averaging.",
    "company/pricing/ofgem_price_cap.py::_ELEC_CAP_GBP_PER_MWH":
        "the published cap WINDOWS are already pinned in ofgem_default_tariff_cap_windows.json; "
        "this table is an annual average of them and should be derived from the pin, not "
        "restated beside it. The nearest thing here to an already-solved pin.",
    "company/pricing/ofgem_price_cap.py::_GAS_CAP_GBP_PER_MWH":
        "the gas half of the above, and the same repair: derive the annual average from the "
        "already-pinned cap windows rather than tabulating it separately.",
    "company/market/market_report.py::_UK_AVG_ELEC_UNIT_RATE_P_KWH":
        "DESNZ Quarterly Energy Prices publishes average domestic unit rates; published "
        "statistic rather than law, but a real publication with a real number.",
    "company/market/market_report.py::_UK_AVG_GAS_UNIT_RATE_P_KWH":
        "the gas half of the same DESNZ Quarterly Energy Prices tables; unpinned.",
    "company/market/market_report.py::_UK_DOMESTIC_ACCOUNTS_M":
        "Ofgem's Retail Market Indicators publish domestic account counts; the table is a "
        "market total in millions and is a straightforward pin once the series is fetched.",
    "saas/non_commodity.py::_NON_COMMODITY_ELEC_RESI_BY_YEAR":
        "an aggregate of DUoS, TNUoS, BSUoS, RO, FiT, CfD, CM and metering. No publication "
        "states the aggregate; the pin is each component, which is most of this register.",
    "saas/non_commodity.py::_NON_COMMODITY_GAS_RESI_BY_YEAR":
        "the gas aggregate of GDN transportation, NTS and metering; same shape, same repair.",
}

# status "not_published": nothing publishes a figure of this shape.
_NOT_PUBLISHED: dict[str, str] = {
    "simulation/life_events.py::_SOLAR_INSTALL_PROB_BY_YEAR":
        "a marginal annual install PROBABILITY the world draws against, derived from DESNZ "
        "cumulative installs over a household count. The derivation is a modelling choice.",
    "simulation/life_events.py::_EV_ACQUIRED_PROB_BY_YEAR":
        "same shape: an annual acquisition hazard derived from a published stock series. The "
        "stock is published; this hazard is the model's own reading of it.",
    "simulation/life_events.py::_HEAT_PUMP_INSTALL_PROB_BY_YEAR":
        "an annual install hazard for a gas-heated home, derived from published install counts; "
        "the hazard is a modelling construct, not a published figure.",
    "simulation/life_events.py::_BATTERY_INSTALL_PROB_WITH_SOLAR_BY_YEAR":
        "a CONDITIONAL probability (battery given solar). No publication states a conditional; "
        "the BEIS penetration figure it cites is a stock share, which is a different quantity.",
    "simulation/market_switching_propensity.py::_POST_BAN_STRUCTURAL_FACTOR":
        "a structural multiplier the model applies after the 2023 fairer-pricing rule; a "
        "modelling assumption about behaviour, with no published counterpart of this shape.",
    "simulation/market_switching_propensity.py::MARKET_SAVINGS_BY_YEAR":
        "the modelled saving available from switching, used to drive propensity. Published "
        "switching SAVINGS estimates exist but are computed differently; this is the world's.",
    # `company/crm/market_conditions.py::MARKET_SWITCHING_MULTIPLIER_BY_YEAR` was classified here
    # until 2026-08-31, on the reason "the company's own belief multiplier on market switching
    # intensity — a belief the epistemic wall specifically ALLOWS to be wrong. Pinning it would
    # be the violation." THAT REASON WAS THE DEFECT, not a mitigation of it. DESNZ and Ofgem
    # publish GB domestic switching; a supplier can look it up; so being wrong about it is an
    # ordinary defect and not the wall doing its job. The classification bought the table six
    # weeks of silence while it asserted 31.0% for 2016 against a published 17.0-17.6% and
    # inverted the record's shape across 2016-2021. The table now loads from the commons and is
    # held in `_MUST_NOT_BE_LITERALS_SWITCHING` below.
    "company/crm/css_tracker.py::_INDUSTRY_AVERAGE_OVERALL":
        "an internal benchmark score for customer service comparison; no regulator publishes a "
        "single industry-average CSS score on this scale.",
    "company/billing/cot.py::_SVT_ELEC_PENCE":
        "the COMPANY'S OWN standard variable tariff. A supplier sets its own prices; there is "
        "no publication to be wrong about, and a pin would be a category error.",
    "company/billing/cot.py::_CAP_ELEC_PENCE":
        "the company's own capped-tariff price point. Constrained BY the published cap, which "
        "is separately pinned, but the price itself is the company's commercial decision.",
    "company/billing/economy7.py::_E7_DAY_RATE_PPM":
        "the company's own Economy 7 day rate; a commercial price, not a published figure.",
    "company/billing/economy7.py::_E7_NIGHT_RATE_PPM":
        "the company's own Economy 7 night rate; same reasoning as the day rate above.",
    "company/billing/seg_portfolio.py::_SEG_RATE_HISTORY_PENCE_PER_KWH":
        "the company's own Smart Export Guarantee export rate. SEG obliges suppliers to offer a "
        "tariff above zero; the LEVEL is set by each supplier, so there is nothing to pin.",
    "company/billing/smart_export.py::_SEG_RATES_PPM":
        "the second module carrying the company's own SEG offer rates; a duplicate worth "
        "collapsing, but not a published-law pin.",
    "company/regulatory/seg_book.py::_SEG_RATE_P_PER_KWH_BY_YEAR":
        "its own comment says 'illustrative competitive rates ... based on publicly available "
        "SEG rate comparisons' — a survey of other suppliers' offers, not a publication.",
    "company/market/rego_portfolio.py::_REGO_PRICE_BY_YEAR":
        "REGO certificate prices are traded bilaterally and OTC; no official publication states "
        "an annual REGO price, which is why brokers' marks differ from each other.",
}


# status "band_pinned": a commons artefact states a BAND rather than a scalar, and a control holds
# the table inside it year by year. Added 2026-08-30.
#
# WHY A FOURTH BUCKET EXISTS. Three buckets could not describe a table that IS pinned but not by
# equality, so the only home for one was `_PUBLISHED_UNPINNED` with a paragraph explaining that it
# was not really unpinned — which is how that bucket reached its own ratchet ceiling. The register
# was mis-describing its best-evidenced entries as its weakest.
#
# The distinction is real and not bookkeeping. `_PINNED` asserts EQUALITY against a published
# scalar. A switching record states COUNTS, and a count over an account total that drifts is a
# RANGE; forcing a scalar out of it would mean choosing a point inside the band and then asserting
# the world equals the choice. Band-pinning asserts the weaker, true thing — the table lies inside
# what the record supports — and it is falsifiable in both directions, which is what makes it a pin
# rather than a note.
_BAND_PINNED: dict[str, str] = {
    "company/market/market_report.py::_UK_SWITCHING_RATE_PCT":
        "gb_domestic_switching_rate.json holds the band; "
        "tests/architecture/test_switching_rate_commons.py holds this table inside it year by "
        "year with three mutation legs. Nine of its ten values were outside the published band "
        "before that control existed. MOVED here from _PUBLISHED_UNPINNED on 2026-08-30: it was "
        "never unpinned, and parking it there is what took that bucket to its ratchet.",
    "simulation/departure_level_anchor.py::YEAR_LEVEL_ANCHOR":
        "the world's own departure LEVEL, derived from the same commons band by "
        "tools/fit_year_level_anchor.py and held inside it by "
        "test_switching_rate_commons.py::test_the_worlds_realised_departure_rate_is_inside_the_"
        "published_band, whose mutation leg halves any one year's entry and fires on that year. "
        "Band and not scalar for the same reason as the row above: the record states counts.",
}

# Ratchet. May only be LOWERED. Raising it to make a red test green is the goal-seeking R12
# forbids, applied to a control — and is exactly how a register stops shrinking.
#
# LOWERED 40 -> 39 on 2026-08-30, by moving `_UK_SWITCHING_RATE_PCT` to `_BAND_PINNED` where it
# always belonged. A ratchet paid down by pinning something, which is the only move it permits.
_MAX_PUBLISHED_UNPINNED = 39

# The named hole. `not_published` carries no ratchet, so it is the one bucket that could grow
# into a dumping ground. Declared here rather than left implicit; see the test of that name.
_UNRATCHETED_BUCKET = "_NOT_PUBLISHED"


def _register() -> dict[str, str]:
    out = {k: "pinned" for k in _PINNED}
    out.update({k: "published_unpinned" for k in _PUBLISHED_UNPINNED})
    out.update({k: "band_pinned" for k in _BAND_PINNED})
    out.update({k: "not_published" for k in _NOT_PUBLISHED})
    return out


def _load_commons(path: Path, key: str) -> list[dict]:
    """NO FAIL-OPEN PATH (R15). Missing, empty or malformed RAISES.

    Returning `[]` would make the equality leg iterate over nothing and pass — the
    fail-silent shape that lets a control report green while checking nothing.
    """
    if not path.exists():
        raise FileNotFoundError(f"regulation commons artefact missing: {path}")
    raw = json.loads(path.read_text())
    entries = raw.get(key)
    if not entries:
        raise ValueError(f"regulation commons artefact has no {key}: {path}")
    return entries


def _module_attr(dotted_key: str):
    """Import the module named in a register key and return the named table."""
    import importlib

    rel, name = dotted_key.split("::")
    module = importlib.import_module(rel[:-3].replace("/", "."))
    return getattr(module, name)


# ═══════════════════════════════════════════════════════════════════════════════════════════
# (a) EQUALITY — a pinned table equals the publication, after a conversion done HERE
# ═══════════════════════════════════════════════════════════════════════════════════════════

def _ccl_pins(commodity: str, asserted_only: bool = True) -> dict[int, float]:
    """CCL rates by obligation year.

    `asserted_only` is the provenance gate. Equality asserts `primary`/`bracketed` ONLY —
    a figure nobody fetched must not be served as the published law. COVERAGE asks a
    different question ("is this year in the register at all?") and so counts `recalled`
    too; conflating the two would report an honestly-declared recalled year as a hole.
    """
    pins = _load_commons(CCL_COMMONS, "rates")
    return {
        int(p["from"][:4]): p["gbp_per_kwh"]
        for p in pins
        if p["commodity"] == commodity
        and (not asserted_only or p["provenance"] in ("primary", "bracketed"))
    }


def _ro_pins() -> dict[int, float]:
    """The RO effective cost, MULTIPLIED HERE from two separately published series.

    This is the whole point of splitting the commons into level and price. Had the artefact
    carried the GBP/MWh product, this comparison would be a tautology, and worse, a wrong
    level could be cancelled by a wrong price and still land on a plausible product.
    """
    levels = {
        int(e["obligation_year"]): e["roc_per_mwh"]
        for e in _load_commons(RO_COMMONS, "obligation_levels")
        if e["provenance"] in ("primary", "secondary")
    }
    prices = {
        int(e["obligation_year"]): e["gbp_per_roc"]
        for e in _load_commons(RO_COMMONS, "buy_out_prices")
        if e["provenance"] in ("primary", "secondary")
    }
    return {y: levels[y] * prices[y] for y in sorted(set(levels) & set(prices))}


def _expected_for(conversion: str, asserted_only: bool = True) -> tuple[dict[int, float], float]:
    """(published value per year, absolute tolerance) under a named conversion."""
    if conversion == "ccl_electricity_gbp_per_mwh":
        return {y: v * 1000.0 for y, v in _ccl_pins("electricity", asserted_only).items()}, 0.005
    if conversion == "ccl_gas_gbp_per_mwh":
        return {y: v * 1000.0 for y, v in _ccl_pins("gas", asserted_only).items()}, 0.005
    if conversion == "ccl_electricity_pence_per_kwh":
        return {y: v * 100.0 for y, v in _ccl_pins("electricity", asserted_only).items()}, 0.0005
    if conversion == "ccl_gas_pence_per_kwh":
        return {y: v * 100.0 for y, v in _ccl_pins("gas", asserted_only).items()}, 0.0005
    if conversion == "ro_effective_gbp_per_mwh_1dp":
        # The table's stated reading is the product tabulated to 1dp. The tolerance IS that
        # reading, declared: 0.05 is the widest a 1dp rounding can be, and nothing wider is
        # admitted. The shipped table's worst residual under it is 0.023.
        return _ro_pins(), 0.05
    raise ValueError(f"unknown conversion: {conversion!r}")


def test_every_pinned_table_equals_its_publication():
    """The leg a citation census cannot be: it reads the PUBLICATION, not the comment."""
    checked = 0
    for key, conversion in _PINNED.items():
        table = _module_attr(key)
        expected, tol = _expected_for(conversion)
        for year, value in expected.items():
            if year not in table:
                continue          # out of window; leg (b) owns absence
            assert table[year] == pytest.approx(value, abs=tol), (
                f"{key}[{year}] = {table[year]} but the regulation commons publishes "
                f"{value} under conversion {conversion}"
            )
            checked += 1
    # NON-VACUITY: this leg must actually have compared something. 44 pairs at the time of
    # writing; the floor sits just under it so a shrinking register is loud.
    assert checked >= 44, f"only {checked} (table, year) pairs compared — did the register shrink?"


# ═══════════════════════════════════════════════════════════════════════════════════════════
# (b) COVERAGE — a pinned table's year with no pin is a hole, not a pass
# ═══════════════════════════════════════════════════════════════════════════════════════════

def _years_outside_commons_window(key: str, conversion: str) -> list[int]:
    """Table years that fall before the first, or after the last, year the commons pins."""
    table = _module_attr(key)
    expected, _ = _expected_for(conversion, asserted_only=False)
    lo, hi = min(expected), max(expected)
    return sorted(y for y in table if y < lo or y > hi)


def test_every_year_of_a_pinned_table_has_a_pin_inside_the_commons_window():
    """A HOLE inside the covered window is a defect; a year before the window is a different
    question, owned by the leg below.

    ANY provenance counts here, `recalled` included: a declared-unfetched year is a known hole
    the sibling control already ratchets, not an unknown one.
    """
    for key, conversion in _PINNED.items():
        table = _module_attr(key)
        expected, _ = _expected_for(conversion, asserted_only=False)
        lo, hi = min(expected), max(expected)
        missing = sorted(y for y in table if lo <= y <= hi and y not in expected)
        assert not missing, (
            f"{key} tabulates {missing} with no entry in the regulation commons — "
            "an unpinned year INSIDE the pinned window is invisible to the equality leg"
        )


# Table years that predate the commons' own coverage. `_CCL_*_P_KWH` tabulate back to 2001;
# `ccl_main_rates.json` starts at 2016 because that is what the CCL pass fetched. Declared
# and ratcheted rather than skipped, so "the commons does not go back that far" stays a
# visible, shrinking number instead of a silent exemption inside the equality leg.
_MAX_YEARS_OUTSIDE_COMMONS_WINDOW = 20


def test_the_out_of_window_year_count_only_goes_down():
    outside = {
        key: _years_outside_commons_window(key, conversion)
        for key, conversion in _PINNED.items()
    }
    total = sum(len(v) for v in outside.values())
    assert total <= _MAX_YEARS_OUTSIDE_COMMONS_WINDOW, (
        f"{total} tabulated years sit outside the commons' pinned window "
        f"{ {k: v for k, v in outside.items() if v} } against a ratchet of "
        f"{_MAX_YEARS_OUTSIDE_COMMONS_WINDOW}. Extend the commons; do not raise the ratchet."
    )


# ═══════════════════════════════════════════════════════════════════════════════════════════
# (c) SCOPE — the census population, discovered repo-wide, must equal the register
# ═══════════════════════════════════════════════════════════════════════════════════════════

def test_every_discovered_table_is_classified():
    """THE LEG THAT WAS MISSING. A table in any module in scope must be classified here.

    The predecessors asked this question of one module's `vars()`, so a rate table in
    `company/regulatory/` was outside the question rather than answered by it.
    """
    discovered = set(discover_year_keyed_tables())
    registered = set(_register())
    unclassified = sorted(discovered - registered)
    assert not unclassified, (
        "year-keyed rate tables discovered in simulation/, company/ or saas/ and classified "
        f"in none of the four buckets: {unclassified}"
    )
    stale = sorted(registered - discovered)
    assert not stale, (
        f"classified here but no longer discoverable (renamed, deleted, or moved behind a "
        f"loader?): {stale}"
    )


def test_every_unpinned_entry_states_a_reason():
    """"Unpinned" with no reason is a TODO; with a reason it is a decision someone can audit."""
    for bucket in (_PUBLISHED_UNPINNED, _NOT_PUBLISHED, _BAND_PINNED):
        for key, reason in bucket.items():
            assert len(reason) >= 40, f"{key}'s reason is too thin to audit: {reason!r}"


def test_a_table_is_in_exactly_one_bucket():
    keys = list(_PINNED) + list(_PUBLISHED_UNPINNED) + list(_NOT_PUBLISHED) + list(_BAND_PINNED)
    dupes = sorted({k for k in keys if keys.count(k) > 1})
    assert not dupes, f"classified in more than one bucket: {dupes}"


# ═══════════════════════════════════════════════════════════════════════════════════════════
# (d) RATCHET — the unpinned published surface may only shrink
# ═══════════════════════════════════════════════════════════════════════════════════════════

def test_the_published_unpinned_count_only_goes_down():
    assert len(_PUBLISHED_UNPINNED) <= _MAX_PUBLISHED_UNPINNED, (
        f"{len(_PUBLISHED_UNPINNED)} published-but-unpinned tables against a ratchet of "
        f"{_MAX_PUBLISHED_UNPINNED}. Pin one; do not raise the ratchet."
    )


def test_the_unratcheted_bucket_is_declared_as_a_hole():
    """`not_published` has no ratchet and could become a dumping ground.

    Naming it here is not a fix. What makes it survivable is that each entry must argue, in
    40+ characters, that NO publication has the table's shape — an argument a reviewer can
    reject. This test exists so a later reader cannot mistake the absence of a ratchet for
    the absence of a decision.
    """
    assert _UNRATCHETED_BUCKET == "_NOT_PUBLISHED"
    assert _NOT_PUBLISHED, "the declared hole is empty — has the bucket been renamed?"


# ═══════════════════════════════════════════════════════════════════════════════════════════
# (e) NO-RELAPSE — a table repaired by LOADING from the commons must not become a literal again
# ═══════════════════════════════════════════════════════════════════════════════════════════

# These names carried the GBP486k defect. They are gone from the census because they are no
# longer literals — `company/regulatory/ro_commons.py` loads them. "Absent" and "unchecked"
# look identical to a census, so this leg makes absence load-bearing.
_MUST_NOT_BE_LITERALS = (
    "company/regulatory/roc_ledger.py::_ROC_OBLIGATION_LEVEL",
    "company/regulatory/roc_ledger.py::_ROC_BUY_OUT_PRICE_GBP",
    "company/regulatory/renewable_obligation.py::_OBLIGATION_LEVEL_ROC_PER_MWH",
    "company/regulatory/renewable_obligation.py::_BUYOUT_PRICE_GBP_PER_ROC",
)


def test_the_ro_tables_have_not_been_re_inlined():
    discovered = set(discover_year_keyed_tables())
    relapsed = sorted(set(_MUST_NOT_BE_LITERALS) & discovered)
    assert not relapsed, (
        f"{relapsed} is a literal table again. These four names carried ten years of "
        "obligation levels and buy-out prices that matched no publication and understated "
        "the report's RO line by GBP486,458.88. They load from the commons; keep it that way."
    )


# The company's reading of the GB domestic switching record, same repair one series along
# (2026-08-31). Held separately from the RO names because the evidence is different and a
# relapse message that cited the wrong incident would send the next reader to the wrong file.
_MUST_NOT_BE_LITERALS_SWITCHING = (
    "company/crm/market_conditions.py::MARKET_SWITCHING_RATE_PCT_BY_YEAR",
    "company/crm/market_conditions.py::MARKET_SWITCHING_MULTIPLIER_BY_YEAR",
)


def test_the_switching_reading_has_not_been_re_inlined():
    """MUTATION: paste either table back as a dict literal and this fires on that name.

    `MARKET_SWITCHING_MULTIPLIER_BY_YEAR` was ten hand-authored numbers under a docstring
    claiming they were derived from the published series. They were not: 2.17 for 2016 implies
    31.0% switching against a published 17.0-17.6%, and the table correlated with the record at
    MINUS 0.47 across 2016-2021 -- falling to 2022 while the record rose to its 2020 peak. Both
    names now derive from `docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json`.
    "Absent from the census" and "unchecked" look identical to a census, so this leg makes the
    absence load-bearing.
    """
    discovered = set(discover_year_keyed_tables())
    relapsed = sorted(set(_MUST_NOT_BE_LITERALS_SWITCHING) & discovered)
    assert not relapsed, (
        f"{relapsed} is a literal table again. It loads from the commons; keep it that way, and "
        "see tests/architecture/test_switching_rate_commons.py for the band it answers to."
    )


def test_the_ro_readers_agree_with_the_commons():
    """The company's two RO readers serve the published series, not a restatement of it."""
    from company.regulatory import renewable_obligation, roc_ledger

    levels = {
        int(e["obligation_year"]): e["roc_per_mwh"]
        for e in _load_commons(RO_COMMONS, "obligation_levels")
    }
    prices = {
        int(e["obligation_year"]): e["gbp_per_roc"]
        for e in _load_commons(RO_COMMONS, "buy_out_prices")
    }
    assert roc_ledger._ROC_OBLIGATION_LEVEL == levels
    assert roc_ledger._ROC_BUY_OUT_PRICE_GBP == prices
    assert renewable_obligation._OBLIGATION_LEVEL_ROC_PER_MWH == levels
    assert renewable_obligation._BUYOUT_PRICE_GBP_PER_ROC == prices


# ═══════════════════════════════════════════════════════════════════════════════════════════
# (f) MUTATION — R15: every leg above is proven to FIRE on its own named defect
# ═══════════════════════════════════════════════════════════════════════════════════════════

def test_mutation_a_the_shipped_ramp_on_either_column_is_caught(monkeypatch, tmp_path):
    """THE NAMED DEFECT, replayed on the level column and then the price column.

    Restore the invented ramp in the commons and the RO equality leg must fire on both.
    """
    for field, key, shipped in (
        ("roc_per_mwh", "obligation_levels", {2016: 0.317, 2023: 0.376}),
        ("gbp_per_roc", "buy_out_prices", {2016: 43.30, 2023: 54.35}),
    ):
        raw = json.loads(RO_COMMONS.read_text())
        for entry in raw[key]:
            if entry["obligation_year"] in shipped:
                entry[field] = shipped[entry["obligation_year"]]
        mutated = tmp_path / f"ro_{key}.json"
        mutated.write_text(json.dumps(raw))
        monkeypatch.setattr(
            "tests.architecture.test_year_keyed_rate_table_census.RO_COMMONS", mutated
        )
        with pytest.raises(AssertionError, match="regulation commons publishes"):
            test_every_pinned_table_equals_its_publication()


def test_mutation_b_a_drifting_pin_is_caught(monkeypatch, tmp_path):
    """The COMMONS is not privileged either. Move the pin instead of the table and the same
    leg fires, so neither side can be quietly edited to make the other green."""
    raw = json.loads(CCL_COMMONS.read_text())
    for entry in raw["rates"]:
        if entry["commodity"] == "gas" and entry["from"] == "2019-04-01":
            entry["gbp_per_kwh"] = 0.00999
    mutated = tmp_path / "ccl.json"
    mutated.write_text(json.dumps(raw))
    monkeypatch.setattr(
        "tests.architecture.test_year_keyed_rate_table_census.CCL_COMMONS", mutated
    )
    with pytest.raises(AssertionError, match="regulation commons publishes"):
        test_every_pinned_table_equals_its_publication()


def test_mutation_c_an_unclassified_new_table_is_caught(monkeypatch):
    """A year-keyed rate table added anywhere in scope, in no bucket, must fail the scope leg."""
    real = discover_year_keyed_tables()
    monkeypatch.setattr(
        "tests.architecture.test_year_keyed_rate_table_census.discover_year_keyed_tables",
        lambda *a, **k: {**real, "company/market/new_levy.py::_NEW_LEVY_BY_YEAR": 5},
    )
    with pytest.raises(AssertionError, match="classified in none of the four buckets"):
        test_every_discovered_table_is_classified()


def test_mutation_d_a_table_moved_out_of_simulation_is_still_discovered(tmp_path):
    """THE MUTATION THIS WHOLE FILE EXISTS BECAUSE NOTHING COULD FAIL ON.

    Put the same table in `simulation/` and in `company/` and the enumerator must find BOTH.
    A `vars(one_module)` enumerator finds neither unless someone thought of that module —
    which is exactly how two wrong RO tables in `company/regulatory/` stayed unregistered
    while the register named the RIGHT table in `simulation/` as its largest unchecked line.
    """
    body = "_MOVED_RATE_BY_YEAR = {2016: 1.0, 2017: 2.0, 2018: 3.0}\n"
    for package in ("simulation", "company/regulatory", "saas"):
        (tmp_path / package).mkdir(parents=True, exist_ok=True)
        (tmp_path / package / "moved.py").write_text(body)
    found = discover_year_keyed_tables(root=tmp_path, scope=("simulation", "company", "saas"))
    assert set(found) == {
        "simulation/moved.py::_MOVED_RATE_BY_YEAR",
        "company/regulatory/moved.py::_MOVED_RATE_BY_YEAR",
        "saas/moved.py::_MOVED_RATE_BY_YEAR",
    }, f"the enumerator is not repo-wide: {sorted(found)}"


def test_mutation_e2_a_rate_written_as_arithmetic_is_still_discovered(tmp_path):
    """The second discovery hole, found by running the census against the real tree.

    `_GGL_RATE_GBP_PER_METER_YEAR` writes every entry as `0.576 * 365 / 100` — the p/day
    working, left in the source. That is an `ast.BinOp`, so a constants-only walk drops a
    whole published levy from the population while reporting a green ratchet.
    """
    (tmp_path / "simulation").mkdir(parents=True)
    (tmp_path / "simulation" / "arith.py").write_text(
        "_LEVY_BY_YEAR = {2021: 0.576 * 365 / 100, 2022: 0.576 * 365 / 100, 2023: 0.122 * 365 / 100}\n"
    )
    found = discover_year_keyed_tables(root=tmp_path, scope=("simulation",))
    assert "simulation/arith.py::_LEVY_BY_YEAR" in found, (
        "a table whose rates are written as arithmetic was not discovered"
    )
    # and the real one, in the real tree
    assert "simulation/policy_costs.py::_GGL_RATE_GBP_PER_METER_YEAR" in discover_year_keyed_tables()


def test_mutation_e_a_negative_rate_is_still_discovered(tmp_path):
    """Discovery's own fail-open shape: unary minus is not `ast.Constant`.

    A naive walk skips `_CFD_LEVY_BY_YEAR` (2022: -5.0, the crisis rebate) — a table already
    IN the old register. A census that silently drops rows is worse than no census, because
    its ratchet reads green while coverage falls.
    """
    (tmp_path / "simulation").mkdir(parents=True)
    (tmp_path / "simulation" / "neg.py").write_text(
        "_REBATE_BY_YEAR = {2021: 1.5, 2022: -5.0, 2023: 6.5}\n"
    )
    found = discover_year_keyed_tables(root=tmp_path, scope=("simulation",))
    assert "simulation/neg.py::_REBATE_BY_YEAR" in found, (
        "a table containing a negative rate was not discovered"
    )
    # and the real one, in the real tree
    assert "simulation/policy_costs.py::_CFD_LEVY_BY_YEAR" in discover_year_keyed_tables()


def test_mutation_f_an_emptied_register_cannot_read_green(monkeypatch, tmp_path):
    """FAIL-SILENT guard. An empty commons would make the equality leg iterate over nothing."""
    empty = tmp_path / "empty.json"
    empty.write_text('{"obligation_levels": [], "buy_out_prices": []}')
    monkeypatch.setattr(
        "tests.architecture.test_year_keyed_rate_table_census.RO_COMMONS", empty
    )
    with pytest.raises(ValueError, match="has no obligation_levels"):
        _ro_pins()


def test_mutation_g_a_missing_register_cannot_read_green(monkeypatch, tmp_path):
    """An unavailable check is a FAILED check, never a passed one."""
    monkeypatch.setattr(
        "tests.architecture.test_year_keyed_rate_table_census.RO_COMMONS",
        tmp_path / "does_not_exist.json",
    )
    with pytest.raises(FileNotFoundError, match="commons artefact missing"):
        _ro_pins()


def test_mutation_h_a_raised_ratchet_is_visible(monkeypatch):
    """The ratchet must actually bind: adding an unpinned table without pinning one fails."""
    monkeypatch.setattr(
        "tests.architecture.test_year_keyed_rate_table_census._PUBLISHED_UNPINNED",
        {**_PUBLISHED_UNPINNED, "company/market/extra.py::_EXTRA_BY_YEAR": "x" * 50},
    )
    with pytest.raises(AssertionError, match="do not raise the ratchet"):
        test_the_published_unpinned_count_only_goes_down()
