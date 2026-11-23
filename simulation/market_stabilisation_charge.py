"""The Market Stabilisation Charge (SLC 24A), 14 April 2022 to 31 March 2024: what the world charges
the GAINING supplier on a domestic win, per fuel, by lookup of Ofgem's published weekly rate.

Knowledge (K8): `docs/market_research/the_market_stabilisation_charge_2022_2024.md` -- section 7 is
the series below, section 10 the route chosen here (lookup, not a rebuild of wc and wpc: the
forward-price source behind wc is not public, and the published rate already contains x, l, t, c).

WHY THE WORLD HOLDS THIS. Real acquirers paid it on every domestic switch-in while it was in force,
fixed or default, and the simulation omitted it -- so a first-term strike that ignores it wins on a
missing rule, which is value transferred, not created (finding
`seat-finding-the-first-term-quote-needs-the-markets-price-not-the-cap-...`, increment 6). The
company sees the CHARGE on its own settlement; it never reads this table as a pricing input.

THE CHARGE IS GROSS PER WIN. Ofgem's rate times the customer's own EAC (electricity) or AQ (gas), at
the rate in force on the switch's effective date (the Wednesday-from week; guidance v4 para 2.32).
RECCo settled the NET of gains and losses per billing period (para 2.30); a world that also credits
the company for customers it loses can net them, and the billing period is a GAP on the page.

WHAT IS NOT ESTABLISHED, carried rather than guessed (page section 11):
  * whether house moves, new connections and SoLR transfers were in scope -- the licence names a
    customer who "switches from a Losing Supplier", so `charge_gbp` is for switches only and the
    caller decides; a move-in is not charged here.
  * the billing period and payment terms -- the charge is dated on the switch, not on a settlement
    cycle.
"""
from __future__ import annotations

import bisect
import datetime as dt

#: Ofgem MSC dashboard, page dated 8 April 2024, retrieved 2026-11-23; copied from the knowledge
#: page section 7 and held equal to it by `tests/simulation/test_market_stabilisation_charge.py`.
#: (effective_from, gas GBP/MWh, electricity GBP/MWh). A week whose trigger was "No" is zero in both.
WEEKLY_RATES_GBP_PER_MWH: tuple[tuple[str, float, float], ...] = (
    ("2022-04-14", 0.00, 0.00),
    ("2022-04-21", 0.00, 0.00),
    ("2022-04-27", 0.00, 0.00),
    ("2022-05-05", 0.00, 0.00),
    ("2022-05-11", 0.00, 0.00),
    ("2022-05-18", 0.00, 0.00),
    ("2022-05-25", 0.00, 0.00),
    ("2022-06-01", 0.00, 0.00),
    ("2022-06-08", 0.00, 0.00),
    ("2022-06-15", 0.00, 0.00),
    ("2022-06-22", 0.00, 0.00),
    ("2022-06-29", 0.00, 0.00),
    ("2022-07-06", 0.00, 0.00),
    ("2022-07-13", 0.00, 0.00),
    ("2022-07-27", 0.00, 0.00),
    ("2022-08-03", 0.00, 0.00),
    ("2022-08-10", 0.00, 0.00),
    ("2022-08-17", 0.00, 0.00),
    ("2022-08-24", 0.00, 0.00),
    ("2022-09-01", 0.00, 0.00),
    ("2022-09-07", 0.00, 0.00),
    ("2022-09-14", 0.00, 0.00),
    ("2022-09-22", 0.00, 0.00),
    ("2022-09-28", 0.00, 0.00),
    ("2022-10-05", 0.00, 0.00),
    ("2022-10-12", 0.00, 0.00),
    ("2022-10-19", 0.00, 0.00),
    ("2022-10-26", 0.00, 0.00),
    ("2022-11-02", 0.00, 0.00),
    ("2022-11-09", 0.00, 0.00),
    ("2022-11-16", 3.56, 0.00),
    ("2022-11-23", 2.04, 0.00),
    ("2022-11-30", 0.49, 0.00),
    ("2022-12-07", 0.00, 0.00),
    ("2022-12-14", 0.00, 0.00),
    ("2022-12-21", 0.00, 12.03),
    ("2022-12-30", 11.57, 37.63),
    ("2023-01-05", 19.61, 63.62),
    ("2023-01-11", 23.37, 73.84),
    ("2023-01-18", 21.99, 70.60),
    ("2023-01-25", 23.39, 71.38),
    ("2023-02-01", 18.09, 64.48),
    ("2023-02-08", 16.99, 57.56),
    ("2023-02-15", 16.78, 53.80),
    ("2023-02-22", 16.42, 49.69),
    ("2023-03-01", 11.60, 42.69),
    ("2023-03-08", 11.14, 39.29),
    ("2023-03-15", 10.22, 34.02),
    ("2023-03-22", 9.08, 28.59),
    ("2023-03-29", 8.18, 24.31),
    ("2023-04-05", 5.26, 21.17),
    ("2023-04-13", 4.10, 16.08),
    ("2023-04-19", 4.48, 17.36),
    ("2023-04-26", 4.41, 17.19),
    ("2023-05-04", 3.20, 16.87),
    ("2023-05-11", 3.33, 17.13),
    ("2023-05-17", 3.22, 15.79),
    ("2023-05-24", 3.26, 15.38),
    ("2023-06-01", 2.89, 15.54),
    ("2023-06-07", 2.43, 14.92),
    ("2023-06-14", 1.54, 10.51),
    ("2023-06-21", 0.28, 2.98),
    ("2023-06-28", 0.00, 2.07),
    ("2023-07-05", 0.00, 2.30),
    ("2023-07-12", 0.00, 2.10),
    ("2023-07-19", 0.22, 4.97),
    ("2023-07-26", 0.00, 4.30),
    ("2023-08-02", 0.00, 3.61),
    ("2023-08-09", 0.00, 4.00),
    ("2023-08-16", 0.00, 1.29),
    ("2023-08-23", 0.00, 0.00),
    ("2023-08-31", 0.00, 0.00),
    ("2023-09-06", 0.00, 0.52),
    ("2023-09-13", 0.00, 2.84),
    ("2023-09-20", 0.00, 1.74),
    ("2023-09-27", 0.00, 2.03),
    ("2023-10-04", 0.00, 2.19),
    ("2023-10-11", 0.30, 4.03),
    ("2023-10-18", 0.00, 0.00),
    ("2023-10-25", 0.00, 0.00),
    ("2023-11-01", 0.00, 0.00),
    ("2023-11-08", 0.00, 0.00),
    ("2023-11-15", 0.00, 1.02),
    ("2023-11-22", 0.00, 1.10),
    ("2023-11-29", 0.00, 1.37),
    ("2023-12-06", 1.46, 3.82),
    ("2023-12-13", 3.37, 6.80),
    ("2023-12-20", 5.34, 9.92),
    ("2023-12-29", 5.77, 9.03),
    ("2024-01-04", 5.07, 6.97),
    ("2024-01-10", 5.49, 8.14),
    ("2024-01-17", 5.89, 10.00),
    ("2024-01-24", 6.67, 12.27),
    ("2024-01-31", 6.64, 12.11),
    ("2024-02-07", 4.44, 9.50),
    ("2024-02-14", 4.55, 9.46),
    ("2024-02-21", 5.04, 10.36),
    ("2024-02-28", 5.16, 10.41),
    ("2024-03-06", 3.11, 7.42),
    ("2024-03-13", 2.37, 5.38),
    ("2024-03-20", 2.24, 4.77),
    ("2024-03-27", 1.18, 2.29),
)

#: In force from 14 April 2022 (licence notice, 16 Feb 2022); lapsed at 23:59 on 31 March 2024
#: (Ofgem, "Future of Market Stabilisation Charge after March 2024", 12 Oct 2023).
IN_FORCE_FROM = dt.date(2022, 4, 14)
IN_FORCE_TO = dt.date(2024, 3, 31)

_EFFECTIVE_FROM = [dt.date.fromisoformat(r[0]) for r in WEEKLY_RATES_GBP_PER_MWH]
_FUEL_COLUMN = {"gas": 1, "electricity": 2}


def rate_gbp_per_mwh(on: dt.date, fuel: str) -> float:
    """The published MSC rate in force on `on` for `fuel`; 0.0 outside 14 Apr 2022 - 31 Mar 2024.

    Zero outside the window is the rule, not a default: no licence condition charged it then.
    """
    column = _FUEL_COLUMN[fuel]  # KeyError names an unknown fuel rather than charging it nothing
    if on < IN_FORCE_FROM or on > IN_FORCE_TO:
        return 0.0
    week = bisect.bisect_right(_EFFECTIVE_FROM, on) - 1
    return float(WEEKLY_RATES_GBP_PER_MWH[week][column])


def charge_gbp(switch_effective: dt.date, fuel: str, annual_kwh: float) -> dict:
    """What the gaining supplier owes on one fuel of one switch-in, with its basis.

    `annual_kwh` is the customer's EAC (electricity) or AQ (gas): the world's own annual volume for
    that meter, never a typical-consumption stand-in chosen here.
    """
    if annual_kwh < 0:
        raise ValueError(f"annual consumption cannot be negative: {annual_kwh}")
    rate = rate_gbp_per_mwh(switch_effective, fuel)
    return {
        "event_type": "market_stabilisation_charge",
        "fuel": fuel,
        "switch_effective": switch_effective.isoformat(),
        "rate_gbp_per_mwh": rate,
        "annual_kwh": float(annual_kwh),
        "amount_gbp": round(rate * annual_kwh / 1000.0, 2),
        "payer": "gaining_supplier",
        "data_regime": "historical",
    }
