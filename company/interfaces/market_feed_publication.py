"""The company's MARKET-FEED INTAKE surface — the one place the world may publish prices to.

WHY THIS MODULE EXISTS (KNIFE pass 3, design B8_market_feed_is_the_observable)
------------------------------------------------------------------------------
This is the only wall crossing in the disposition register whose DIRECTION was
already right. The world publishes market prices and the company then observes
them, which is exactly how a real UK supplier learns prices: it does not read a
generator's internals, it reads a feed.

The defect was FILING, not direction. The publication entry point sat in
`company/market/price_feed.py` alongside the company's own reader, so
`simulation.publish_market_feed -> company.market.price_feed` was indistinguishable,
to the ratchet and to a reader, from an illegitimate world-reads-company-brain
crossing. Moving the entry point here makes the legitimate crossing legible: it
lands on the published seam (`company.interfaces`), which the ratchet exempts by
its stated SEAM_PACKAGE rule.

**This is a cut, not laundering.** The seam package is WALKED by
`tools/epistemic_wall.py` exactly as `company/market/` is — nothing moved out of
the instrument's reach. The edge is exempt because it terminates on the sanctioned
crossing surface, which is the rule the wall doctrine publishes, not a hole in the
measurement. Contrast `docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` §2b,
where relocating a composition root to `tools/` was REFUSED for precisely the
reason that does not apply here.

WHAT STAYED BEHIND, AND WHY
---------------------------
`company/market/price_feed.py` keeps `PriceFeed` (the READING side) and its two
company-side consumers, `market.rate_comparison` and `portal.app`. Only the
world-facing publication surface relocated. The company reads the FILE this
writes; it still never calls a SIM function.

THE HONEST LIMIT
----------------
This narrows WHERE the crossing happens, not WHAT crosses: the same price records
pass through, at one reviewable chokepoint instead of an interior module. Typing
the payload as a versioned message (the typed-flow seam preference, and what an
Epoch-3 Elexon adapter would need) is owed to EP7_adapter_elexon_insights, which
is level 0 / idle at the time of this cut. Stated here so a later reader cannot
mistake the relocation for a finished adapter.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from company.market.price_feed import DEFAULT_FEED_PATH

__all__ = ["DEFAULT_FEED_PATH", "publish_feed"]


def publish_feed(
    prices: list[dict],
    output_path: Path = DEFAULT_FEED_PATH,
    published_at: str | None = None,
) -> None:
    """Write a price feed JSON file. Called by the SIM pipeline after each run.

    prices: list of {"fuel": str, "period": str, "price_gbp_per_mwh": float}
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ts = published_at or datetime.now(timezone.utc).isoformat()
    payload = {"published_at": ts, "prices": prices}
    with open(output_path, "w") as f:
        json.dump(payload, f, indent=2)
