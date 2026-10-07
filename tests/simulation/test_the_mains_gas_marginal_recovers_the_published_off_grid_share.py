"""W2_20's exit, held: the drawn mains-gas supply recovers the published off-grid share.

THE BRACKET IS TWO SOURCES, NOT TODAY'S ANSWER.

  * FLOOR -- DESNZ, *Subnational electricity and gas consumption statistics 2023*, section 3.4:
    "Across Great Britain in 2023, an estimated 16 per cent of domestic properties were not
    connected to the gas grid". DESNZ counts it as properties minus domestic gas meters, so it is
    a METER fact, the same kind of fact `has_mains_gas_supply` is. DESNZ also says it is an
    UNDERESTIMATE: small commercial meters under 73,200 kWh are counted as domestic.
  * CEILING -- NEED `anon2026_50k`, `MAIN_HEAT_FUEL` = not gas on 19.1% of 50,000 dwellings
    (`docs/market_research/mains_gas_is_a_meter_fact_not_a_grid_fact_need_2026.md`). That
    figure also counts connected homes using under 1,000 kWh and meters NEED could not match to
    an address, so it OVERSTATES the homes with no supply.

The two sources share their meter lineage, so the bracket checks that the joint did not drift
from the meter data. It cannot validate the joint against an independent source. Written up
beside the NEED page, under "The published comparator".
"""
from __future__ import annotations

import datetime as dt
import math

from simulation import premise_population as pp
from simulation.household import HeatingSystem

DESNZ_2023_NOT_CONNECTED_SHARE = 0.16   # floor: DESNZ subnational 2023 s3.4, an underestimate
NEED_2026_NOT_GAS_SHARE = 0.191          # ceiling: NEED anon2026_50k MAIN_HEAT_FUEL != gas

N = 4000
SEED = 20261007
AS_OF = dt.date(2023, 6, 1)


def _stock():
    return [pp.draw_premise_from_joint(f"PSTK-W220-{i:05d}", base_seed=SEED, as_of=AS_OF)
            for i in range(N)]


def _inside_bracket(share: float) -> bool:
    slack = 2.0 * math.sqrt(share * (1.0 - share) / N)
    return DESNZ_2023_NOT_CONNECTED_SHARE - slack <= share <= NEED_2026_NOT_GAS_SHARE + slack


def test_the_drawn_supply_lands_between_the_published_floor_and_need_s_ceiling():
    """The drawn share must sit in the bracket. Inferring supply from the unconditioned heating
    weights (the rule this atom replaces) must fall OUTSIDE it, which shows the bracket can refuse.

    Since 2026-10-07 the drawn heating is conditioned on the supply, so inferring from the DRAWN
    heating lands near the supply by construction and can no longer play the refused arm."""
    stock = _stock()
    drawn = sum(p.household.has_mains_gas_supply is False for p in stock) / N

    gas = (HeatingSystem.GAS_BOILER_COMBI, HeatingSystem.GAS_BOILER_SYSTEM)
    inferred = 1.0 - sum(w for s, w in pp.published_heating_weights().items() if s in gas)

    assert not _inside_bracket(inferred), (
        f"inferring supply from the heating system gives {inferred:.3f}, inside the bracket -- "
        "the bracket no longer separates a drawn supply from an inferred one")
    assert _inside_bracket(drawn), (
        f"drawn share without a gas supply {drawn:.3f} is outside "
        f"[{DESNZ_2023_NOT_CONNECTED_SHARE}, {NEED_2026_NOT_GAS_SHARE}] at n={N}")
