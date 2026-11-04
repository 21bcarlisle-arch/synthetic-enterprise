"""THE DEFECT (2026-11-04): `build_properties` gave every home without a gas account with us
`electric_storage` heating, whatever the world drew. 88 of 124 drawn electricity-only homes heat by
gas bought elsewhere, oil, communal heat or a heat pump, and each carried 3 kWh per degree day of
storage heating on its electricity on top of a LOW-band EAC. Once 7ec8b1030d gave those premises a
sky, their meters read about ten times their EAC, and INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER
went from 4 to 53 (SYN-2016-566: EAC 1,410.5 kWh, 13,452 kWh metered in 2018, oil-heated).

ONE control over the partition. A rule that gives no home electric heating passes the oil leg and
reds the storage leg; the old rule (storage for every home without gas) passes the storage leg and
reds the oil leg. On origin before this fix the oil leg is red.
"""

from simulation.demand_model import ELEC_HEATING_KWH_PER_DEGREE_DAY, build_demand_shape
from simulation.dwelling_records import GAS_HEATING_SYSTEM, build_properties

_DWELLING = {"property_type": "semi_detached", "epc_rating": "D", "bedrooms": 3, "output_area": None}


def _home(cid, commodity="electricity"):
    return {"customer_id": cid, "segment": "resi", "commodity": commodity}


def test_a_drawn_home_takes_electric_heating_only_where_the_world_drew_it():
    oil, storage, direct, pump, dual = "SYN-T-OIL", "SYN-T-STORAGE", "SYN-T-DIRECT", "SYN-T-ASHP", "SYN-T-DUAL"
    drawn = {oil: "non_mains_fuel_boiler", storage: "electric_storage", direct: "electric_direct",
             pump: "heat_pump_air", dual: "gas_boiler_combi"}
    props = build_properties(
        [_home(oil), _home(storage), _home(direct), _home(pump), _home(dual), _home(dual + "g", "gas")],
        dwellings={cid: {**_DWELLING, "drawn_heating_system": h} for cid, h in drawn.items()})
    heats = {cid: props[cid]["heating_system"] in ELEC_HEATING_KWH_PER_DEGREE_DAY for cid in drawn}

    assert heats[storage] and heats[direct], f"resistive electric heating must stay on the meter: {heats}"
    assert not heats[oil], f"an oil-heated home was given {props[oil]['heating_system']!r} heating on its electricity"
    # A heat pump's electricity is the ASHP overlay's, added once; a legacy term here would add it twice.
    assert not heats[pump], props[pump]["heating_system"]
    assert props[dual]["heating_system"] == GAS_HEATING_SYSTEM


def test_on_a_cold_day_only_the_electrically_heated_home_draws_heating():
    """The number the meter sees: the same day, base shape and dwelling, two heating systems."""
    props = build_properties([_home("SYN-T-OIL"), _home("SYN-T-STORAGE")], dwellings={
        "SYN-T-OIL": {**_DWELLING, "drawn_heating_system": "non_mains_fuel_boiler"},
        "SYN-T-STORAGE": {**_DWELLING, "drawn_heating_system": "electric_storage"}})
    base = [0.2] * 48
    oil = sum(build_demand_shape(base, 2.0, "electricity", props["SYN-T-OIL"], None))
    storage = sum(build_demand_shape(base, 2.0, "electricity", props["SYN-T-STORAGE"], None))
    assert storage > oil + 30, (oil, storage)  # ~13.5 HDD x 3 kWh, before occupancy
