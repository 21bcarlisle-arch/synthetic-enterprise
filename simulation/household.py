"""Phase A — Household physical model.

Each simulated customer has a physical home with attributes that drive:
- Base energy consumption (calibrated to EPC rating and property type)
- Seasonal consumption shape (better-insulated = flatter curve)
- ToU eligibility (smart meter required)
- EV charging load (if has_ev, adds overnight demand)
- Solar export (if has_solar, reduces net consumption)

Source calibration: docs/market_research/HUMAN_SIMULATION_RESEARCH.md
UK benchmarks: English Housing Survey 2022, EPC register (MHCLG),
               BEIS heat pump statistics, DfT EV statistics, DUKES Table 3.4

Epistemic constraint: The company layer does not read Household records
directly from the SIM. It observes consumption patterns and infers
physical characteristics from HH meter data, EPC lookups, and customer
interactions. The SIM's ground truth is never exposed to company code.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PropertyType(str, Enum):
    TERRACED = "terraced"
    SEMI_DETACHED = "semi_detached"
    DETACHED = "detached"
    FLAT = "flat"
    COMMERCIAL_OFFICE = "commercial_office"
    COMMERCIAL_WAREHOUSE = "commercial_warehouse"
    INDUSTRIAL = "industrial"


class BuildEra(str, Enum):
    PRE_1919 = "pre_1919"
    ERA_1919_1944 = "1919_1944"
    ERA_1945_1964 = "1945_1964"
    ERA_1965_1980 = "1965_1980"
    ERA_1981_2000 = "1981_2000"
    POST_2000 = "post_2000"


class HeatingSystem(str, Enum):
    GAS_BOILER_COMBI = "gas_boiler_combi"
    GAS_BOILER_SYSTEM = "gas_boiler_system"
    HEAT_PUMP_AIR = "heat_pump_air"
    HEAT_PUMP_GROUND = "heat_pump_ground"
    ELECTRIC_STORAGE = "electric_storage"
    ELECTRIC_DIRECT = "electric_direct"
    DISTRICT_HEAT = "district_heat"
    NONE = "none"


class BoilerAge(str, Enum):
    NEW = "new"        # 0-5 years
    MID = "mid"        # 5-12 years
    OLD = "old"        # 12+ years
    NA = "na"          # no boiler (heat pump or electric)


class InsulationLevel(str, Enum):
    FULL = "full"           # loft + cavity/solid wall
    PARTIAL = "partial"     # loft only, or partial wall
    POOR = "poor"           # uninsulated
    NA = "na"               # commercial / no roof


@dataclass(frozen=True)
class Household:
    """Physical attributes of a customer's premises.

    Frozen — assigned once at simulation start and does not change
    (except via life events: boiler replacement, solar install, EV acquisition).
    """

    customer_id: str
    property_type: PropertyType
    build_era: BuildEra
    epc_rating: str            # A/B/C/D/E/F/G
    bedrooms: int | None       # None for commercial
    heating_system: HeatingSystem
    boiler_age: BoilerAge

    # Solar generation
    has_solar: bool
    solar_kwp: float           # 0.0 if no solar
    solar_install_year: int | None

    # Battery storage
    has_battery: bool
    battery_kwh: float         # 0.0 if no battery

    # Electric vehicle
    has_ev: bool
    ev_charger_kw: float       # 0.0 if no EV (3.7 / 7.0 / 22.0 common)

    # Smart meter
    has_smart_meter: bool
    smart_meter_install_year: int | None

    # Insulation
    insulation: InsulationLevel

    @property
    def is_residential(self) -> bool:
        return self.property_type in (
            PropertyType.TERRACED,
            PropertyType.SEMI_DETACHED,
            PropertyType.DETACHED,
            PropertyType.FLAT,
        )

    @property
    def is_gas_heated(self) -> bool:
        return self.heating_system in (
            HeatingSystem.GAS_BOILER_COMBI,
            HeatingSystem.GAS_BOILER_SYSTEM,
        )

    @property
    def is_heat_pump(self) -> bool:
        return self.heating_system in (
            HeatingSystem.HEAT_PUMP_AIR,
            HeatingSystem.HEAT_PUMP_GROUND,
        )

    def epc_consumption_multiplier(self) -> float:
        """Multiplier on segment-average EAC based on EPC rating.

        Calibrated to English Housing Survey 2022 mean energy use by EPC band.
        Relative to D (=1.0, the most common band for existing UK stock).
        Source: MHCLG EPC statistics Table C3.
        """
        return {
            "A": 0.50,
            "B": 0.65,
            "C": 0.82,
            "D": 1.00,
            "E": 1.25,
            "F": 1.55,
            "G": 1.90,
        }.get(self.epc_rating.upper(), 1.0)

    def seasonal_flatness_factor(self) -> float:
        """Higher value = flatter winter/summer ratio for electricity demand.

        Better-insulated homes maintain temperature more easily, reducing
        the winter heating electricity spike (relevant for heat pumps) and
        summer cooling demand. Gas seasonality is separately modelled.
        Scale: 0.0 (very peaked seasonal demand) to 1.0 (perfectly flat).
        """
        base = {
            "A": 0.85,
            "B": 0.75,
            "C": 0.60,
            "D": 0.45,
            "E": 0.30,
            "F": 0.20,
            "G": 0.10,
        }.get(self.epc_rating.upper(), 0.45)
        # Insulation uplift
        if self.insulation == InsulationLevel.FULL:
            base = min(1.0, base + 0.10)
        elif self.insulation == InsulationLevel.POOR:
            base = max(0.0, base - 0.10)
        return base

    def ev_annual_kwh(self) -> float:
        """Estimated additional annual electricity demand from EV charging.

        UK average EV driver travels ~7,500 miles/year at ~3.5 miles/kWh.
        Source: DfT EV statistics / National Grid ESO.
        """
        if not self.has_ev:
            return 0.0
        return 7500 / 3.5  # ~2,143 kWh/year

    def solar_annual_generation_kwh(self) -> float:
        """Estimated annual solar generation (kWh) from panels.

        UK average yield: ~850 kWh per kWp per year (SAP 10.2 / MCS data).
        Source: BEIS solar photovoltaics deployment statistics.
        """
        if not self.has_solar:
            return 0.0
        return self.solar_kwp * 850.0


# ---------------------------------------------------------------------------
# Home-type to property-type mapping (for existing CUSTOMERS records)
# ---------------------------------------------------------------------------

_HOME_TYPE_TO_PROPERTY: dict[str, PropertyType] = {
    "urban_flat": PropertyType.FLAT,
    "tenement_flat": PropertyType.FLAT,
    "suburban_semi": PropertyType.SEMI_DETACHED,
    "rural_detached": PropertyType.DETACHED,
    "small_office": PropertyType.COMMERCIAL_OFFICE,
    "warehouse_unit": PropertyType.COMMERCIAL_WAREHOUSE,
    "office_building": PropertyType.COMMERCIAL_OFFICE,
    "chemical_plant": PropertyType.INDUSTRIAL,
    "supermarket": PropertyType.COMMERCIAL_WAREHOUSE,
}

# Representative build eras for each home type
# Source: English Housing Survey 2022 — stock profile by dwelling type
_HOME_TYPE_TO_ERA: dict[str, BuildEra] = {
    "urban_flat": BuildEra.ERA_1965_1980,          # London flats: 60s-70s council/private
    "tenement_flat": BuildEra.PRE_1919,             # Scottish tenements: Victorian
    "suburban_semi": BuildEra.ERA_1945_1964,        # Post-war semi boom
    "rural_detached": BuildEra.PRE_1919,            # Rural stock tends to be older
    "small_office": BuildEra.ERA_1965_1980,
    "warehouse_unit": BuildEra.ERA_1981_2000,
    "office_building": BuildEra.ERA_1981_2000,
    "chemical_plant": BuildEra.ERA_1965_1980,
    "supermarket": BuildEra.ERA_1981_2000,
}

# Representative heating systems by segment and home type (2016 baseline)
# UK 2016: ~85% gas-heated resi homes, ~9% electric, ~1% heat pump (rising)
# Source: BEIS DUKES Table 4.8
_HEATING_SYSTEM: dict[str, HeatingSystem] = {
    "urban_flat": HeatingSystem.GAS_BOILER_COMBI,
    "tenement_flat": HeatingSystem.GAS_BOILER_SYSTEM,
    "suburban_semi": HeatingSystem.GAS_BOILER_COMBI,
    "rural_detached": HeatingSystem.GAS_BOILER_SYSTEM,   # older system boiler, larger home
    "small_office": HeatingSystem.GAS_BOILER_SYSTEM,
    "warehouse_unit": HeatingSystem.DISTRICT_HEAT,
    "office_building": HeatingSystem.GAS_BOILER_SYSTEM,
    "chemical_plant": HeatingSystem.NONE,                  # process heat via gas, not domestic boiler
    "supermarket": HeatingSystem.NONE,
}

# Insulation levels by EPC rating
# Source: English Housing Survey — insulation rates by EPC band
_EPC_TO_INSULATION: dict[str, InsulationLevel] = {
    "A": InsulationLevel.FULL,
    "B": InsulationLevel.FULL,
    "C": InsulationLevel.PARTIAL,
    "D": InsulationLevel.PARTIAL,
    "E": InsulationLevel.POOR,
    "F": InsulationLevel.POOR,
    "G": InsulationLevel.POOR,
}


def make_household(customer: dict) -> Household:
    """Build a Household for a customer record from simulation/run_phase2b.py.

    Assigns representative attributes based on home_type, epc_rating, and
    segment. Solar, battery, and EV defaulted to False at 2016 baseline
    — upgrade events (solar install, EV acquisition) layer in over time
    via the life events engine (Phase B).
    """
    home_type = customer.get("home_type", "suburban_semi")
    epc = customer.get("epc_rating", "D")
    segment = customer.get("segment", "resi")
    cid = customer["customer_id"]

    property_type = _HOME_TYPE_TO_PROPERTY.get(home_type, PropertyType.SEMI_DETACHED)
    build_era = _HOME_TYPE_TO_ERA.get(home_type, BuildEra.ERA_1945_1964)
    heating = _HEATING_SYSTEM.get(home_type, HeatingSystem.GAS_BOILER_COMBI)

    # Boiler age: older build eras tend to have older boilers
    if heating in (HeatingSystem.GAS_BOILER_COMBI, HeatingSystem.GAS_BOILER_SYSTEM):
        boiler_age = {
            BuildEra.PRE_1919: BoilerAge.OLD,
            BuildEra.ERA_1919_1944: BoilerAge.OLD,
            BuildEra.ERA_1945_1964: BoilerAge.MID,
            BuildEra.ERA_1965_1980: BoilerAge.MID,
            BuildEra.ERA_1981_2000: BoilerAge.NEW,
            BuildEra.POST_2000: BoilerAge.NEW,
        }.get(build_era, BoilerAge.MID)
    else:
        boiler_age = BoilerAge.NA

    # Smart meter: use existing smart_meter field if present
    has_smart = bool(customer.get("smart_meter") or customer.get("metering") == "HH")
    smart_year = 2016 if has_smart else None

    # Solar PV: resi only; rural detached homes more likely (garden, south-facing roof)
    # 2016 UK baseline: ~2.8% of homes had solar (BEIS REPD)
    has_solar = (home_type == "rural_detached" and segment == "resi")
    solar_kwp = 3.8 if has_solar else 0.0
    solar_year = 2014 if has_solar else None  # early adopter

    insulation = _EPC_TO_INSULATION.get(epc, InsulationLevel.PARTIAL)

    return Household(
        customer_id=cid,
        property_type=property_type,
        build_era=build_era,
        epc_rating=epc,
        bedrooms=customer.get("bedrooms"),
        heating_system=heating,
        boiler_age=boiler_age,
        has_solar=has_solar,
        solar_kwp=solar_kwp,
        solar_install_year=solar_year,
        has_battery=False,
        battery_kwh=0.0,
        has_ev=False,
        ev_charger_kw=0.0,
        has_smart_meter=has_smart,
        smart_meter_install_year=smart_year,
        insulation=insulation,
    )


def build_household_register(customers: list[dict]) -> dict[str, Household]:
    """Build a {customer_id: Household} lookup for all customers."""
    return {c["customer_id"]: make_household(c) for c in customers}
