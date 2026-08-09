"""M3 -- Market data feed: the company receives forward prices through a
defined published feed interface, not by calling SIM functions directly.

The SIM pipeline publishes a price feed JSON file after each settlement run.
The company reads from this file only -- never from SIM modules.
This is the structural swap point for live Elexon market data.
"""

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

DEFAULT_FEED_PATH = Path("docs/market_data/price_feed.json")

FEED_MAX_AGE_HOURS = 24  # Feed is stale if older than this


@dataclass(frozen=True)
class SpotPrice:
    fuel: str        # electricity / gas
    period: str      # ISO datetime of HH period
    price_gbp_per_mwh: float


class PriceFeed:
    """Reads the published price feed file. No SIM modules accessed.

    Provides spot price history and forward price estimates based on
    recent published spot prices.
    """

    def __init__(self, feed_path: Path = DEFAULT_FEED_PATH):
        self._path = feed_path
        self._data: dict = {}
        self._prices: list[SpotPrice] = []
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return
        if not self._path.exists():
            self._data = {}
            self._prices = []
            self._loaded = True
            return
        with open(self._path) as f:
            self._data = json.load(f)
        self._prices = [
            SpotPrice(
                fuel=p["fuel"],
                period=p["period"],
                price_gbp_per_mwh=p["price_gbp_per_mwh"],
            )
            for p in self._data.get("prices", [])
        ]
        self._loaded = True

    def is_available(self) -> bool:
        return self._path.exists()

    def is_stale(self, max_age_hours: float = FEED_MAX_AGE_HOURS) -> bool:
        self._load()
        published_at = self._data.get("published_at")
        if not published_at:
            return True
        published = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - published).total_seconds() / 3600
        return age > max_age_hours

    def spot_prices(self, fuel: str = "electricity") -> list[SpotPrice]:
        self._load()
        return [p for p in self._prices if p.fuel == fuel]

    def get_latest_spot(self, fuel: str = "electricity") -> float | None:
        prices = self.spot_prices(fuel)
        if not prices:
            return None
        return sorted(prices, key=lambda p: p.period)[-1].price_gbp_per_mwh

    def get_forward_price_estimate(
        self,
        fuel: str = "electricity",
        lookback_periods: int = 48,
        premium_pct: float = 5.0,
    ) -> float | None:
        """Estimate forward price from recent spot average + risk premium.

        Uses the last `lookback_periods` spot records to compute a mean,
        then applies a percentage risk premium (forward > spot in expectation).
        """
        prices = self.spot_prices(fuel)
        if not prices:
            return None
        recent = sorted(prices, key=lambda p: p.period)[-lookback_periods:]
        base = mean(p.price_gbp_per_mwh for p in recent)
        return round(base * (1 + premium_pct / 100.0), 4)

    def summary(self) -> dict:
        self._load()
        elec = self.spot_prices("electricity")
        gas = self.spot_prices("gas")
        return {
            "published_at": self._data.get("published_at"),
            "electricity_price_count": len(elec),
            "gas_price_count": len(gas),
            "latest_electricity_period": sorted(elec, key=lambda p: p.period)[-1].period if elec else None,
            "latest_electricity_spot": self.get_latest_spot("electricity"),
            "forward_estimate_electricity": self.get_forward_price_estimate("electricity"),
        }


# `publish_feed` MOVED 2026-08-09 to `company/interfaces/market_feed_publication.py`
# (KNIFE pass 3, design B8_market_feed_is_the_observable). It is the world-facing
# INTAKE surface, so it belongs on the sanctioned seam where a legitimate
# world-publishes-to-company crossing is legible as such; this module is the
# company's own READER of the resulting file and keeps its two company-side
# consumers (market.rate_comparison, portal.app).
#
# Deliberately NOT re-exported from here. A re-export would leave the old
# non-seam import path working, so the crossing this pass cut could silently
# reappear at the surface that is not the seam — which is the whole defect.
