"""Elexon Market Index Data (MID) — the traded WHOLESALE price, per settlement period.

Historical Ground Truth law: this hits the real Elexon Insights Solution API
(data.elexon.co.uk) — no synthetic data, no gap-filling, no interpolation.

WHY THIS EXISTS (W1_6b exit criterion 3a, validity)
---------------------------------------------------
`simulation/run_merit_order_reconstructibility.py` grades a merit-order SRMC stack
against **SSP** (`systemSellPrice`). SSP is the imbalance **cash-out** price: what a
party pays for being short of its contracted position. It is set by the balancing
mechanism's marginal actions plus the cash-out machinery (PAR tagging, the
reverse-price rule, the de-minimis threshold), and only loosely tracks the price at
which electricity actually traded.

An SRMC merit-order stack reconstructs the price at which the **marginal generator
was willing to sell** — which is the WHOLESALE price. MID is Elexon's own measure of
that: the volume-weighted average price of short-term wholesale trades reported by
the power exchanges. So MID is the target the engine is actually a model of, and SSP
is a different instrument that happens to be denominated in the same units.

This module does NOT replace the SSP measurement. It ADDS an independent target so
the question "is the reconstruction wrong, or is it being graded against the wrong
price?" can be answered with a measurement instead of an argument. Both are reported
side by side, always. See `docs/fidelity/W1_6b_merit_order_reconstructibility_evidence.md`.

TWO FAIL-OPENS OBSERVED IN THE LIVE API, GUARDED HERE (R15)
------------------------------------------------------------
1. **A too-wide range returns HTTP 200 with an EMPTY `data` list.** Observed
   2026-08-03: a 31-day window returned `{"data": []}` with a 200, while the same
   window fetched in 7-day chunks returned ~1,490 records/week. Silently treating
   that as "no trades occurred" would zero out arbitrary stretches of history and
   every downstream mean would be computed on a subset nobody declared. An empty
   response for a window inside the coverage period is therefore an ERROR here, never
   an absence of trading. `MAX_RANGE_DAYS` is set to the widest width actually proven
   to return data.
2. **A reporting provider can publish price 0.00 on volume 0.00.** Observed across
   the whole 2016-2020 window: `N2EXMIDP` reports 0.0/0.0 in every period sampled,
   while `APXMIDP` carries the real trades. A naive mean across providers would halve
   every wholesale price in the series. The join is VOLUME-WEIGHTED and drops
   zero/non-finite-volume records, so a non-reporting provider contributes nothing
   rather than dragging the price toward zero.

COVERAGE IS A NAMED GAP, NOT A ZERO
------------------------------------
MID begins **2016-09-12** (bisected against the live API 2026-08-03: 2016-09-10
returns 0 records, 2016-09-12 returns a partial 40, 2016-09-13 a full 96). The calm
window opens 2016-03-01, so **the 2016 cell is only ~30% covered by MID and is not
like-for-like with the SSP-measured 2016 cell.** Callers must read
`MID_COVERAGE_START` and say so rather than comparing a part-year against a full one.
"""

import json
import math
from datetime import datetime, timedelta
from pathlib import Path

import requests

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"
MARKET_INDEX_ENDPOINT = "/balancing/pricing/market-index"

CACHE_DIR = Path("sim/cache")
CACHE_FILE = "elexon_mid_full.json"

# First settlement date for which Elexon returns MID records. Bisected against the
# live API, not assumed — see the module docstring. Asking for a date before this is
# a NAMED GAP (the data does not exist), which is why it raises rather than returning
# an empty list that a caller could average into a passing verdict.
MID_COVERAGE_START = "2016-09-12"

# The widest window proven to return data. 7 days returns ~1,490 records; 10, 14, 16
# and 20 all silently returned ZERO with a 200 (measured 2026-08-03). This is a
# property of the live endpoint, so it is pinned as a constant with its evidence
# rather than discovered per-run.
MAX_RANGE_DAYS = 7

_session = requests.Session()


def is_finite_number(value) -> bool:
    """True only for a real, finite int/float. Mirrors the guard family in
    `sim/merit_order_reconstruction.py` — bool is deliberately excluded."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


class MarketIndexUnavailable(RuntimeError):
    """Raised when MID cannot be measured — an empty in-coverage window, or a request
    before `MID_COVERAGE_START`. Deliberately an exception and not an empty list: the
    whole point of this module is that "no data" must never be silently readable as
    "no trades" (R15 fail-open pattern #2)."""


def _fetch_window(from_iso: str, to_iso: str) -> list[dict]:
    url = f"{BASE_URL}{MARKET_INDEX_ENDPOINT}?from={from_iso}&to={to_iso}&format=json"
    response = _session.get(url, timeout=120)
    if response.status_code != 200:
        raise MarketIndexUnavailable(
            f"Elexon MID returned HTTP {response.status_code} for {from_iso}..{to_iso}"
        )
    return response.json().get("data", [])


def get_market_index_range(start_date: str, end_date: str) -> list[dict]:
    """Raw MID records for [start_date, end_date] inclusive ('YYYY-MM-DD').

    Fetched in `MAX_RANGE_DAYS` chunks because wider windows silently return empty.
    An empty chunk inside the coverage period raises `MarketIndexUnavailable` rather
    than contributing zero records — see the module docstring.
    """
    if start_date < MID_COVERAGE_START:
        raise MarketIndexUnavailable(
            f"MID coverage begins {MID_COVERAGE_START}; {start_date} predates it. "
            "This is a NAMED GAP in the source, not an absence of trading — "
            "measure the covered sub-window and state the bound."
        )

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    records: list[dict] = []
    current = start
    while current <= end:
        chunk_end = min(current + timedelta(days=MAX_RANGE_DAYS), end + timedelta(days=1))
        chunk = _fetch_window(
            current.strftime("%Y-%m-%dT00:00Z"), chunk_end.strftime("%Y-%m-%dT00:00Z")
        )
        if not chunk:
            raise MarketIndexUnavailable(
                f"Elexon MID returned ZERO records for the in-coverage window "
                f"{current:%Y-%m-%d}..{chunk_end:%Y-%m-%d}. An empty 200 is the known "
                "too-wide-range failure mode, NOT an absence of trading — refusing to "
                "record a silent hole in the series."
            )
        records.extend(chunk)
        current = chunk_end

    return records


def volume_weighted_mid(records: list[dict]) -> dict[tuple[str, int], float]:
    """Collapse raw provider records to ONE volume-weighted wholesale price per
    (settlementDate, settlementPeriod).

    Zero-volume and non-finite records are DROPPED, not averaged: a provider that
    reports 0.00 on 0.00 volume (N2EXMIDP, throughout 2016-2020) is not quoting a
    price of zero, it is not quoting. A period whose every provider is zero-volume is
    omitted entirely rather than recorded as a £0 trade.
    """
    numerator: dict[tuple[str, int], float] = {}
    weight: dict[tuple[str, int], float] = {}

    for record in records:
        price = record.get("price")
        volume = record.get("volume")
        date_str = record.get("settlementDate")
        period = record.get("settlementPeriod")
        if not isinstance(date_str, str) or not isinstance(period, int):
            continue
        if not is_finite_number(price) or not is_finite_number(volume):
            continue
        if volume <= 0:
            continue
        key = (date_str, period)
        numerator[key] = numerator.get(key, 0.0) + price * volume
        weight[key] = weight.get(key, 0.0) + volume

    return {key: numerator[key] / weight[key] for key in numerator if weight[key] > 0}


def cache_path() -> Path:
    return CACHE_DIR / CACHE_FILE


def cache_present() -> bool:
    return cache_path().exists()


def write_cached_market_index(records: list[dict]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path().write_text(json.dumps(records))


def load_cached_market_index() -> list[dict]:
    """Raw cached MID records. Raises if the cache is absent — callers that can run
    without MID must check `cache_present()` first and say what they skipped."""
    if not cache_present():
        raise MarketIndexUnavailable(
            f"{cache_path()} absent — run `python3 -m sim.market_index_history` to build it."
        )
    return json.loads(cache_path().read_text())


if __name__ == "__main__":
    import sys

    start = sys.argv[1] if len(sys.argv) > 1 else MID_COVERAGE_START
    end = sys.argv[2] if len(sys.argv) > 2 else "2020-12-31"
    print(f"Fetching Elexon MID {start} .. {end} in {MAX_RANGE_DAYS}-day chunks…")
    raw = get_market_index_range(start, end)
    write_cached_market_index(raw)
    joined = volume_weighted_mid(raw)
    providers = sorted({r.get("dataProvider") for r in raw})
    print(f"{len(raw):,} raw records -> {len(joined):,} volume-weighted periods")
    print(f"providers seen: {providers}")
    print(f"cached to {cache_path()}")
