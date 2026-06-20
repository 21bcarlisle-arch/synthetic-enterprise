"""Segment customer model — Phase 10a.

Replaces the 9 named individual accounts with 5 population segments:
  resi_standard, resi_smart, sme_standard, sme_smart, gas_resi

Each segment is a cohort of customers with:
  - avg_kwh_per_customer: mean annual consumption per customer
  - headcount: number of customers (evolves annually)
  - total_eac_kwh: headcount × avg_kwh_per_customer (aggregate hedging volume)

Non→Smart flow: each year, a fraction of Standard-segment headcount upgrades
to the Smart variant (resi_standard → resi_smart, sme_standard → sme_smart),
modelling the UK smart meter rollout trajectory.

Shape calibration: PC1 integrates to ~3,933 kWh/yr per average customer;
PC3 to ~13,610 kWh/yr. Scaling factors (avg_kwh / calibration_kwh) ensure
the per-customer shape matches the segment's avg_kwh_per_customer.
"""

from dataclasses import dataclass, field

# Reference year (2020) calibration of raw PC shapes — kWh/year per average customer.
PC1_CALIBRATION_KWH: float = 3_933.0
PC3_CALIBRATION_KWH: float = 13_610.0

LONDON = {"lat": 51.5074, "lon": -0.1278, "region": "London"}
MANCHESTER = {"lat": 53.4808, "lon": -2.2426, "region": "Manchester"}

_RESI_UPGRADE_RATES: dict[str, float] = {
    "2016": 0.03, "2017": 0.03, "2018": 0.03,
    "2019": 0.05, "2020": 0.05,
    "2021": 0.08, "2022": 0.08, "2023": 0.08,
    "2024": 0.10, "2025": 0.10,
}
_SME_UPGRADE_RATES: dict[str, float] = {
    "2016": 0.02, "2017": 0.02, "2018": 0.03,
    "2019": 0.05, "2020": 0.05,
    "2021": 0.07, "2022": 0.07, "2023": 0.08,
    "2024": 0.10, "2025": 0.10,
}


@dataclass
class CustomerSegment:
    segment_id: str
    label: str
    commodity: str              # "electricity" | "gas"
    profile_class: int          # 1=domestic, 3=SME (used for both shape fn and pricing)
    avg_kwh_per_customer: float # mean annual consumption per customer in the cohort
    headcount: int              # number of customers currently in segment
    acquisition_date: str       # simulation start date (same for all initial segments)
    location: dict              # {lat, lon, region} — representative for weather scaling

    upgrades_to: str | None = None              # segment_id that Standard upgrades into
    smart_upgrade_rates: dict = field(default_factory=dict)  # year → fraction upgrading
    base_churn_rate: float = 0.15               # annual churn as fraction of headcount
    acquisition_win_rate: float = 0.35          # fraction of replacement attempts won

    @property
    def total_eac_kwh(self) -> float:
        """Aggregate annual volume = headcount × per-customer mean consumption."""
        return float(self.avg_kwh_per_customer * self.headcount)

    @property
    def shape_scale(self) -> float:
        """Scaling factor to calibrate PC shape to this segment's avg_kwh_per_customer."""
        calibration = PC1_CALIBRATION_KWH if self.profile_class == 1 else PC3_CALIBRATION_KWH
        return self.avg_kwh_per_customer / calibration

    def as_weather_customer(self) -> dict:
        """Minimal dict accepted by weather_means_for_customer()."""
        return {
            "customer_id": self.segment_id,
            "location": self.location,
            "commodity": self.commodity,
        }


SEGMENTS: list[CustomerSegment] = [
    CustomerSegment(
        segment_id="resi_standard",
        label="Residential Standard",
        commodity="electricity",
        profile_class=1,
        avg_kwh_per_customer=3_100.0,
        headcount=150,
        acquisition_date="2016-01-01",
        location=LONDON,
        upgrades_to="resi_smart",
        smart_upgrade_rates=_RESI_UPGRADE_RATES,
        base_churn_rate=0.15,
        acquisition_win_rate=0.35,
    ),
    CustomerSegment(
        segment_id="resi_smart",
        label="Residential Smart",
        commodity="electricity",
        profile_class=1,
        avg_kwh_per_customer=2_800.0,
        headcount=20,
        acquisition_date="2016-01-01",
        location=LONDON,
        base_churn_rate=0.10,
        acquisition_win_rate=0.30,
    ),
    CustomerSegment(
        segment_id="sme_standard",
        label="SME Standard",
        commodity="electricity",
        profile_class=3,
        avg_kwh_per_customer=35_000.0,
        headcount=40,
        acquisition_date="2016-01-01",
        location=MANCHESTER,
        upgrades_to="sme_smart",
        smart_upgrade_rates=_SME_UPGRADE_RATES,
        base_churn_rate=0.20,
        acquisition_win_rate=0.40,
    ),
    CustomerSegment(
        segment_id="sme_smart",
        label="SME Smart",
        commodity="electricity",
        profile_class=3,
        avg_kwh_per_customer=32_000.0,
        headcount=5,
        acquisition_date="2016-01-01",
        location=MANCHESTER,
        base_churn_rate=0.12,
        acquisition_win_rate=0.35,
    ),
    CustomerSegment(
        segment_id="gas_resi",
        label="Gas Residential",
        commodity="gas",
        profile_class=1,
        avg_kwh_per_customer=13_250.0,
        headcount=80,
        acquisition_date="2016-01-01",
        location=LONDON,
        base_churn_rate=0.15,
        acquisition_win_rate=0.30,
    ),
]

ELEC_SEGMENTS: list[CustomerSegment] = [s for s in SEGMENTS if s.commodity == "electricity"]
GAS_SEGMENTS: list[CustomerSegment] = [s for s in SEGMENTS if s.commodity == "gas"]
SEGMENT_BY_ID: dict[str, CustomerSegment] = {s.segment_id: s for s in SEGMENTS}


def apply_annual_headcount_changes(
    headcounts: dict[str, int],
    year: str,
) -> dict[str, int]:
    """Apply one year of churn, smart upgrades, and acquisition to headcounts.

    Returns a new headcounts dict (does not mutate the input).
    Order of operations: upgrades first, then churn on the reduced count,
    then acquisition to partially replace churned customers.
    """
    updated = dict(headcounts)

    for seg in SEGMENTS:
        sid = seg.segment_id
        count = updated[sid]

        # 1. Smart upgrades (Standard → Smart segment)
        if seg.upgrades_to:
            rate = seg.smart_upgrade_rates.get(year, 0.0)
            upgrades = round(count * rate)
            upgrades = min(upgrades, max(0, count - 1))  # keep at least 1 in source
            updated[sid] = count - upgrades
            updated[seg.upgrades_to] = updated.get(seg.upgrades_to, 0) + upgrades
            count = updated[sid]

        # 2. Churn — deterministic expected churn
        churned = round(count * seg.base_churn_rate)
        updated[sid] = max(1, count - churned)
        count = updated[sid]

        # 3. Acquisition — deterministic win rate on replacement attempts
        # Attempt to replace churned customers + 5% organic growth
        attempts = max(5, churned + round(count * 0.05))
        won = round(attempts * seg.acquisition_win_rate)
        updated[sid] = count + won

    return updated
