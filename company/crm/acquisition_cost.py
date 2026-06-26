"""Customer Acquisition Cost (CAC) model.

UK energy suppliers acquire customers through multiple channels:
- PCW (Price Comparison Website): uSwitch, MoneySupermarket etc. (GBP 48-72)
- Direct: own website/advertising (GBP 28-33)
- Broker: 3rd Party Intermediary for I&C customers (GBP 140-200)
- Referral: existing customer referral (GBP 15-25)
- Winback: former customer returned (GBP 35-42)

CAC is a key input to CLV analysis. CAC > CLV means the acquisition channel
is loss-making at that margin/tenure combination.

Data: Ofgem consumer awareness surveys, CMA energy review, industry benchmarks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Channel = Literal["pcw", "direct", "broker", "referral", "winback"]

_CAC_BY_CHANNEL_YEAR: dict[str, dict[int, float]] = {
    "pcw":      {2016: 45.0, 2017: 52.0, 2018: 58.0, 2019: 62.0, 2020: 60.0,
                 2021: 65.0, 2022: 72.0, 2023: 55.0, 2024: 50.0, 2025: 48.0},
    "direct":   {2016: 30.0, 2017: 30.0, 2018: 32.0, 2019: 33.0, 2020: 28.0,
                 2021: 29.0, 2022: 31.0, 2023: 30.0, 2024: 30.0, 2025: 30.0},
    "broker":   {2016: 150.0, 2017: 155.0, 2018: 160.0, 2019: 165.0, 2020: 140.0,
                 2021: 145.0, 2022: 200.0, 2023: 175.0, 2024: 160.0, 2025: 155.0},
    "referral": {2016: 15.0, 2017: 15.0, 2018: 15.0, 2019: 20.0, 2020: 20.0,
                 2021: 20.0, 2022: 25.0, 2023: 20.0, 2024: 20.0, 2025: 20.0},
    "winback":  {2016: 35.0, 2017: 35.0, 2018: 38.0, 2019: 40.0, 2020: 35.0,
                 2021: 38.0, 2022: 42.0, 2023: 38.0, 2024: 36.0, 2025: 35.0},
}


@dataclass
class AcquisitionRecord:
    customer_id: str
    channel: str
    year: int
    cac_gbp: float
    notes: str = ""


def get_cac(channel: str, year: int) -> float:
    ch_data = _CAC_BY_CHANNEL_YEAR.get(channel)
    if ch_data is None:
        return 0.0
    if year in ch_data:
        return ch_data[year]
    if year < 2016:
        return ch_data[2016]
    return ch_data[2025]


def cac_summary(year: int) -> dict:
    return {ch: get_cac(ch, year) for ch in _CAC_BY_CHANNEL_YEAR}


def clv_vs_cac(annual_margin_gbp: float, avg_tenure_years: float, channel: str, year: int) -> dict:
    clv = annual_margin_gbp * avg_tenure_years
    cac = get_cac(channel, year)
    ratio = clv / cac if cac > 0 else 0.0
    return {
        "clv_gbp": round(clv, 2),
        "cac_gbp": cac,
        "clv_cac_ratio": round(ratio, 2),
        "channel": channel,
        "year": year,
        "status": "HEALTHY" if ratio >= 3.0 else "MARGINAL" if ratio >= 1.5 else "LOSS_MAKING",
    }
