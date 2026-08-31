"""Dual-Fuel Unified Billing Engine.

A UK energy supplier manages one customer account with up to two fuel legs:
electricity (MPAN, BSC-settled) and gas (MPRN, UNC-settled). The customer
sees one bill showing both fuels, with a combined balance.

Market-type differences:
  resi  -- monthly billing, 5% VAT, price cap applies
  SME   -- quarterly billing, reduced-rate VAT below that FUEL's published de minimis
           (electricity 33 kWh/day, gas 145 kWh/day -- VAT Notice 701/19) else standard rate
  I&C   -- monthly/HH-settled, 20% VAT, pass-through levy visibility
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

BILLING_CALENDAR: dict[str, str] = {
    "resi": "monthly",
    "SME": "quarterly",
    "I&C": "monthly",
}

_VAT_DE_MINIMIS_COMMONS = (
    Path(__file__).resolve().parents[2]
    / "docs" / "domain_artefact_library" / "regulatory"
    / "vat_fuel_and_power_de_minimis.json"
)


def _load_de_minimis() -> dict[str, float]:
    """`{fuel: kWh per day}` from the regulation commons, at import.

    WHY READING THE COMMONS IS NOT A WALL CROSSING. `docs/domain_artefact_library/` is the
    regulation commons: the published record, readable by every lane, because it is published in
    reality. Same doctrine and same shape as `company/crm/market_conditions._load_published_rate_pct`
    and `company/regulatory/ro_commons`. What stays owned per lane is the READING -- here, that a
    supply AT the limit is reduced-rated and only one ABOVE it is standard-rated.

    RAISES ON EVERY FAILED READ, and never returns a default. A VAT threshold that quietly falls
    back to a hard-coded number is the exact defect this replaces: the fallback is what let one
    fuel's limit stand in for both for as long as nobody looked.
    """
    if not _VAT_DE_MINIMIS_COMMONS.exists():
        raise FileNotFoundError(
            f"VAT de minimis commons missing: {_VAT_DE_MINIMIS_COMMONS}. VAT Notice 701/19 is "
            "required to decide a business supply's rate; there is no invented default."
        )
    raw = json.loads(_VAT_DE_MINIMIS_COMMONS.read_text())
    table = raw.get("de_minimis_by_fuel")
    if not isinstance(table, dict) or not table:
        raise ValueError(f"{_VAT_DE_MINIMIS_COMMONS} publishes no `de_minimis_by_fuel`")
    out = {}
    for fuel, entry in table.items():
        limit = entry.get("kwh_per_day") if isinstance(entry, dict) else None
        if not isinstance(limit, (int, float)) or limit <= 0:
            raise ValueError(
                f"{_VAT_DE_MINIMIS_COMMONS} carries no usable `kwh_per_day` for {fuel!r}"
            )
        out[fuel] = float(limit)
    return out


VAT_RATE_BY_MARKET: dict[str, float] = {
    "resi": 0.05,
    "SME": 0.05,
    "I&C": 0.20,
}

#: THE VAT DE MINIMIS, PER FUEL, AND THE TWO FUELS ARE NOT THE SAME NUMBER.
#: Source: VAT Notice 701/19 (HMRC), electricity §5.2 "not more than an average rate of 33
#: kilowatt hours per day", gas §4.2 "not more than an average rate of 5 therms or 145 kilowatt
#: hours per day". Filed in the commons at
#: `docs/domain_artefact_library/regulatory/vat_fuel_and_power_de_minimis.json`, which is the
#: authority; these are read from it at import so the two cannot drift apart.
#:
#: THIS USED TO BE ONE NUMBER, 33.0, APPLIED TO BOTH FUELS. Gas is 145 kWh/day -- 4.39x higher --
#: so every SME gas leg between 33 and 145 kWh/day was charged the standard rate where the law
#: says reduced. A supplier under-charging VAT owes HMRC the difference; a supplier OVER-charging
#: it has taken money from a customer it was not entitled to, which is the direction this was
#: wrong in.
SME_VAT_DE_MINIMIS_KWH_PER_DAY: dict[str, float] = _load_de_minimis()

#: Kept as the electricity figure under its old name because it is imported elsewhere, and
#: DERIVED from the table above rather than restated, so it cannot become a second answer.
SME_VAT_THRESHOLD_KWH_PER_DAY = SME_VAT_DE_MINIMIS_KWH_PER_DAY["electricity"]


@dataclass(frozen=True)
class FuelBillSection:
    """One fuel leg within a billing statement."""
    fuel: str
    period_start: str
    period_end: str
    days_in_period: int
    consumption_kwh: float
    unit_rate_pence: float
    standing_charge_pence_per_day: float
    standing_charge_gbp: float
    energy_charge_gbp: float
    levies_gbp: float
    subtotal_gbp: float
    vat_rate: float
    vat_gbp: float
    total_gbp: float
    invoice_number: Optional[int]
    payment_status: str

    @property
    def is_paid(self) -> bool:
        return self.payment_status == "paid"

    @property
    def effective_rate_pence(self) -> float:
        if self.consumption_kwh <= 0:
            return 0.0
        return round((self.total_gbp * 100) / self.consumption_kwh, 4)


@dataclass(frozen=True)
class DualFuelBill:
    """Unified billing statement for one period, covering all fuel legs."""
    account_id: str
    market_type: str
    billing_period_start: str
    billing_period_end: str
    electricity: Optional[FuelBillSection]
    gas: Optional[FuelBillSection]
    total_billed_gbp: float
    total_paid_gbp: float

    @property
    def is_dual_fuel(self) -> bool:
        return self.electricity is not None and self.gas is not None

    @property
    def is_electricity_only(self) -> bool:
        return self.electricity is not None and self.gas is None

    @property
    def is_gas_only(self) -> bool:
        return self.gas is not None and self.electricity is None

    @property
    def balance_gbp(self) -> float:
        return round(self.total_paid_gbp - self.total_billed_gbp, 2)

    @property
    def amount_owing_gbp(self) -> float:
        return round(-self.balance_gbp, 2) if self.balance_gbp < 0 else 0.0

    @property
    def in_credit(self) -> bool:
        return self.balance_gbp > 0

    @property
    def billing_calendar(self) -> str:
        return BILLING_CALENDAR.get(self.market_type, "monthly")

    @property
    def all_paid(self) -> bool:
        sections = [s for s in (self.electricity, self.gas) if s]
        return all(s.is_paid for s in sections)


def _period_key(period_end: str) -> str:
    try:
        d = date.fromisoformat(period_end)
        return f"{d.year}-{d.month:02d}"
    except (ValueError, TypeError):
        return period_end[:7] if len(period_end) >= 7 else ""


def _days_in_period(start: str, end: str) -> int:
    try:
        return max(1, (date.fromisoformat(end) - date.fromisoformat(start)).days)
    except (ValueError, TypeError):
        return 30


def _sme_vat_rate(daily_kwh: float, fuel: str) -> float:
    """The VAT rate for one business fuel leg, on that FUEL's own de minimis limit.

    `fuel` is required and has no default. A default would re-create the defect this replaces --
    a gas leg silently tested against electricity's 33 kWh/day when the law says 145 -- and the
    caller already knows which fuel it is holding, so there is nothing to infer.

    REFUSES AN UNKNOWN FUEL rather than falling back. Refusing to bill is safe; billing a supply
    at a rate no published limit supports is a legal error either way it lands, and the guard is
    keyed to the commons rather than to a list written here, so a fuel added to the artefact
    becomes billable without this function changing.
    """
    limit = SME_VAT_DE_MINIMIS_KWH_PER_DAY.get(fuel)
    if limit is None:
        raise ValueError(
            f"no VAT de minimis limit published for fuel {fuel!r}: "
            f"{sorted(SME_VAT_DE_MINIMIS_KWH_PER_DAY)} are the fuels VAT Notice 701/19 carries in "
            f"{_VAT_DE_MINIMIS_COMMONS.name}. Refusing to choose a rate rather than defaulting to "
            "another fuel's threshold."
        )
    # AT the limit is reduced-rated: the notice says "not more than an average rate of", so the
    # comparison is strictly-greater and this is the lane's reading of the published words, stated
    # rather than left in an operator.
    return VAT_RATE_BY_MARKET["I&C"] if daily_kwh > limit else VAT_RATE_BY_MARKET["resi"]


def _invoice_to_section(inv: dict, fuel: str, market_type: str) -> FuelBillSection:
    start = inv.get("billing_period_start", "")
    end = inv.get("billing_period_end", "")
    days = _days_in_period(start, end)
    kwh = float(inv.get("consumption_kwh", 0.0))
    unit_p = float(inv.get("unit_rate_p_per_kwh", 0.0))
    sc_gbp = float(inv.get("standing_charge_gbp", 0.0))
    sc_ppd = round((sc_gbp * 100) / days, 4) if days > 0 and sc_gbp > 0 else 0.0
    energy = float(inv.get("commodity_amount_gbp", 0.0))
    levies = float(inv.get("non_commodity_amount_gbp", 0.0))

    if energy or sc_gbp:
        subtotal = round(energy + levies + sc_gbp, 2)
    else:
        subtotal = float(inv.get("subtotal_gbp", inv.get("total_amount_gbp", 0.0)))
        energy = subtotal

    stored_vat = float(inv.get("vat_gbp", 0.0))
    if stored_vat:
        vat = stored_vat
        vat_rate = round(vat / subtotal, 4) if subtotal > 0 else 0.05
    else:
        if market_type == "SME" and days > 0:
            vat_rate = _sme_vat_rate(kwh / days, fuel)
        else:
            vat_rate = VAT_RATE_BY_MARKET.get(market_type, 0.05)
        vat = round(subtotal * vat_rate, 2)

    total = float(inv.get("total_gbp", round(subtotal + vat, 2)))

    return FuelBillSection(
        fuel=fuel,
        period_start=start,
        period_end=end,
        days_in_period=days,
        consumption_kwh=kwh,
        unit_rate_pence=unit_p,
        standing_charge_pence_per_day=sc_ppd,
        standing_charge_gbp=sc_gbp,
        energy_charge_gbp=energy,
        levies_gbp=levies,
        subtotal_gbp=subtotal,
        vat_rate=vat_rate,
        vat_gbp=vat,
        total_gbp=total,
        invoice_number=inv.get("invoice_number"),
        payment_status=inv.get("payment_status", "unpaid"),
    )


class DualFuelBillBook:
    """Aggregates per-fuel invoices into unified DualFuelBill statements."""

    def gas_account_id(self, account_id: str) -> str:
        return account_id + "g"

    def build_bills(
        self,
        account_id: str,
        market_type: str,
        elec_invoices: list[dict],
        gas_invoices: list[dict],
    ) -> list[DualFuelBill]:
        """Pair electricity + gas invoices by billing period month."""
        elec_by_period: dict[str, dict] = {}
        for inv in elec_invoices:
            key = _period_key(inv.get("billing_period_end", ""))
            if key:
                elec_by_period[key] = inv

        gas_by_period: dict[str, dict] = {}
        for inv in gas_invoices:
            key = _period_key(inv.get("billing_period_end", ""))
            if key:
                gas_by_period[key] = inv

        all_keys = sorted(set(elec_by_period) | set(gas_by_period))
        bills: list[DualFuelBill] = []
        for key in all_keys:
            elec_inv = elec_by_period.get(key)
            gas_inv = gas_by_period.get(key)

            elec_sec = _invoice_to_section(elec_inv, "electricity", market_type) if elec_inv else None
            gas_sec = _invoice_to_section(gas_inv, "gas", market_type) if gas_inv else None

            starts = [s.period_start for s in (elec_sec, gas_sec) if s and s.period_start]
            ends = [s.period_end for s in (elec_sec, gas_sec) if s and s.period_end]
            period_start = min(starts) if starts else ""
            period_end = max(ends) if ends else ""

            billed = round(sum(s.total_gbp for s in (elec_sec, gas_sec) if s), 2)
            paid = round(sum(s.total_gbp for s in (elec_sec, gas_sec) if s and s.is_paid), 2)

            bills.append(DualFuelBill(
                account_id=account_id,
                market_type=market_type,
                billing_period_start=period_start,
                billing_period_end=period_end,
                electricity=elec_sec,
                gas=gas_sec,
                total_billed_gbp=billed,
                total_paid_gbp=paid,
            ))
        return bills

    def cumulative_balance_gbp(self, all_invoices: list[dict]) -> float:
        """Combined account balance. Positive = in credit; negative = owes."""
        paid = sum(
            float(i.get("total_gbp", 0.0))
            for i in all_invoices
            if i.get("payment_status") == "paid"
        )
        billed = sum(float(i.get("total_gbp", 0.0)) for i in all_invoices)
        return round(paid - billed, 2)

    def outstanding_invoices(self, all_invoices: list[dict]) -> list[dict]:
        return [
            i for i in all_invoices
            if i.get("payment_status") in ("unpaid", "partially_paid")
        ]
