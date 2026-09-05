"""Pull Met Office HadUK-Grid 1km grids from the CEDA archive onto this machine.

Phase 1 of the weather-cells ruling (docs/staging/DIRECTOR_RULING_WEATHER_CELLS_
HEAT_LOAD_SEGMENTATION_PHASE1_2026-09-05.md): the authoritative source for the three
phase-1 heat-load drivers is HadUK-Grid at 1km, Open Government Licence.

Raw grids NEVER enter the repo -- they are several GB and the ruling forbids it. They
land under ~/.cache/synthetic-enterprise/haduk_grid/. What is committed is the receipt
this writes: what was pulled, from where, at what version, how big, and its sha256.

On the token. The ruling recorded CEDA's token-minting API returning 500 for this
account and told us to fall back to the hand-made CEDA_TOKEN and to page the director
when it expired. As of 2026-09-05 that API answers 200, so this module mints its own and
re-mints mid-pull when the current one is nearly spent. A ~20GB pull outlives any single
3-day token, so minting is not a convenience here -- without it the pull cannot finish.
CEDA_TOKEN remains the fallback for the day minting breaks again, and a refusal names
which of the two failed so the director is asked for a fresh token only when that is
actually the missing thing.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

CEDA_ENV = Path.home() / ".config" / "synthetic-enterprise" / ".env.ceda"
CACHE_ROOT = Path.home() / ".cache" / "synthetic-enterprise" / "haduk_grid"
RECEIPT = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "market_research"
    / "haduk_grid_pull_receipt.json"
)

MINT_URL = "https://services.ceda.ac.uk/api/token/create/"
ARCHIVE_ROOT = (
    "https://dap.ceda.ac.uk/badc/ukmo-hadobs/data/insitu/MOHC/HadOBS/"
    "HadUK-Grid/v1.3.2.ceda/1km"
)
DATASET_VERSION = "v1.3.2.ceda"
LICENCE = "Open Government Licence v3.0"

# HadUK-Grid publishes each variable under a dated release directory. Pinned rather than
# resolved at run time so a re-pull months later is provably the same data, and so the
# receipt's version means something. HadUK is a once-a-year release; when the next one
# lands this constant moves and the whole pull is re-run.
RELEASE = "v20260512"

# The three phase-1 drivers, ruling section 2.1. `sun` is sunshine DURATION, not
# irradiance -- HadUK publishes no irradiance product. The duration-to-irradiance
# conversion is a separate Choice the ruling requires us to state on the page; it is
# deliberately not made here, because a pull that quietly converts is a pull that
# fabricates.
PHASE1_VARIABLES = ("tas", "sfcWind", "sun")

# WMO standard normal. All three variables publish it; sfcWind's record starts in 1969,
# so 1991-2020 is also the newest normal every variable can support.
NORMAL_PERIOD = "199101-202012"

# The series window. Starts at 1991 to match the normal above, ends at the archive's last
# complete year. Nothing here is a climate claim -- it is the span the analysis may read.
SERIES_FIRST_YEAR = 1991
SERIES_LAST_YEAR = 2025

# Persistence (ruling section 2.4) is a cold-spell property, so daily temperature is
# pulled for the heating season only. This is a stated Choice, not a silent economy: it
# cuts the daily pull by half and forecloses summer-persistence questions, which are
# phase 2's (summer load) rather than phase 1's.
HEATING_SEASON_MONTHS = (1, 2, 3, 10, 11, 12)

TOKEN_REFRESH_MARGIN_S = 600
CHUNK = 1 << 20


class PullRefused(RuntimeError):
    """Raised with a reason a human can act on. Never raised bare."""


def _load_credentials() -> dict:
    if not CEDA_ENV.exists():
        raise PullRefused(
            f"no CEDA credentials at {CEDA_ENV} -- cannot authenticate to the archive"
        )
    env = {}
    for line in CEDA_ENV.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def _jwt_expiry(token: str) -> float | None:
    """Seconds-since-epoch this token dies, or None if it does not say.

    A token whose expiry cannot be read is not treated as fresh -- callers refresh on
    None -- because assuming an unreadable token is good is how a pull dies at hour six.
    """
    parts = token.split(".")
    if len(parts) != 3:
        return None
    payload = parts[1]
    payload += "=" * (-len(payload) % 4)
    try:
        claims = json.loads(base64.urlsafe_b64decode(payload))
    except (ValueError, json.JSONDecodeError):
        return None
    exp = claims.get("exp")
    return float(exp) if isinstance(exp, (int, float)) else None


class Token:
    """A CEDA bearer token that re-mints itself before it expires.

    Holds the mint failure rather than swallowing it: if minting is broken AND the
    fallback token is spent, the refusal has to name both, or the director gets asked for
    a token that would not have helped.
    """

    def __init__(self, env: dict):
        self._env = env
        self._value = None
        self._expires_at = 0.0
        self._mint_error = None
        self._source = None

    def _try_mint(self) -> str | None:
        user = self._env.get("CEDA_USERNAME")
        password = self._env.get("CEDA_PASSWORD")
        if not user or not password:
            self._mint_error = "CEDA_USERNAME/CEDA_PASSWORD absent from the env file"
            return None
        basic = base64.b64encode(f"{user}:{password}".encode()).decode()
        request = urllib.request.Request(
            MINT_URL, data=b"", headers={"Authorization": f"Basic {basic}"}
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                minted = json.loads(response.read().decode())["access_token"]
        except (urllib.error.URLError, OSError, ValueError, KeyError) as exc:
            self._mint_error = f"{type(exc).__name__}: {exc}"
            return None
        self._mint_error = None
        return minted

    def value(self) -> str:
        if self._value and time.time() < self._expires_at - TOKEN_REFRESH_MARGIN_S:
            return self._value

        minted = self._try_mint()
        if minted:
            self._value = minted
            self._source = "minted"
            expiry = _jwt_expiry(minted)
            # An unreadable expiry means re-mint every call rather than trust it.
            self._expires_at = expiry if expiry else 0.0
            return self._value

        fallback = self._env.get("CEDA_TOKEN")
        if fallback:
            expiry = _jwt_expiry(fallback)
            if expiry is None or time.time() < expiry - TOKEN_REFRESH_MARGIN_S:
                self._value = fallback
                self._source = "env CEDA_TOKEN (minting unavailable)"
                self._expires_at = expiry if expiry else time.time() + 300
                return self._value
            raise PullRefused(
                "cannot authenticate: minting the token failed "
                f"({self._mint_error}) AND the fallback CEDA_TOKEN expired at "
                f"{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(expiry))}. "
                "NTFY the director for a fresh token -- this is the case the ruling "
                "reserved for him."
            )
        raise PullRefused(
            f"cannot authenticate: minting failed ({self._mint_error}) and no "
            "CEDA_TOKEN fallback is set in the env file"
        )

    @property
    def source(self) -> str | None:
        return self._source


def build_manifest(tiers: tuple[str, ...]) -> list[dict]:
    """The declared list of files this pull is for. Pure -- no network, so it is
    readable and testable without credentials."""
    entries: list[dict] = []

    if "normals" in tiers:
        for variable in PHASE1_VARIABLES:
            name = f"{variable}_hadukgrid_uk_1km_mon-30y_{NORMAL_PERIOD}.nc"
            entries.append(
                {
                    "tier": "normals",
                    "variable": variable,
                    "frequency": "mon-30y",
                    "url": f"{ARCHIVE_ROOT}/{variable}/mon-30y/{RELEASE}/{name}",
                    "path": f"{variable}/mon-30y/{name}",
                }
            )

    if "monthly" in tiers:
        for variable in PHASE1_VARIABLES:
            for year in range(SERIES_FIRST_YEAR, SERIES_LAST_YEAR + 1):
                name = (
                    f"{variable}_hadukgrid_uk_1km_mon_{year}01-{year}12.nc"
                )
                entries.append(
                    {
                        "tier": "monthly",
                        "variable": variable,
                        "frequency": "mon",
                        "year": year,
                        "url": f"{ARCHIVE_ROOT}/{variable}/mon/{RELEASE}/{name}",
                        "path": f"{variable}/mon/{name}",
                    }
                )

    if "daily" in tiers:
        for year in range(SERIES_FIRST_YEAR, SERIES_LAST_YEAR + 1):
            for month in HEATING_SEASON_MONTHS:
                last = _last_day(year, month)
                name = (
                    f"tas_hadukgrid_uk_1km_day_"
                    f"{year}{month:02d}01-{year}{month:02d}{last}.nc"
                )
                entries.append(
                    {
                        "tier": "daily",
                        "variable": "tas",
                        "frequency": "day",
                        "year": year,
                        "month": month,
                        "url": f"{ARCHIVE_ROOT}/tas/day/{RELEASE}/{name}",
                        "path": f"tas/day/{name}",
                    }
                )

    return entries


def _last_day(year: int, month: int) -> str:
    if month == 2:
        leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
        return "29" if leap else "28"
    return "30" if month in (4, 6, 9, 11) else "31"


def _remote_size(url: str, token: Token) -> int | None:
    request = urllib.request.Request(url, method="HEAD")
    request.add_header("Authorization", f"Bearer {token.value()}")
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            length = response.headers.get("Content-Length")
            return int(length) if length else None
    except (urllib.error.URLError, OSError, ValueError):
        return None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch_one(entry: dict, token: Token, *, verify: bool) -> dict:
    """Download one file if it is not already here, whole, on disk.

    'Already here' means the byte count matches the archive's, not merely that a file
    exists -- a truncated grid left by a killed pull reads as present to every other
    check and poisons the analysis silently.
    """
    target = CACHE_ROOT / entry["path"]
    target.parent.mkdir(parents=True, exist_ok=True)

    expected = _remote_size(entry["url"], token)
    if target.exists() and expected is not None and target.stat().st_size == expected:
        result = {**entry, "status": "present", "bytes": expected}
        if verify:
            result["sha256"] = _sha256(target)
        return result

    partial = target.with_suffix(target.suffix + ".part")
    resume_from = partial.stat().st_size if partial.exists() else 0
    if expected is not None and resume_from >= expected:
        resume_from = 0

    request = urllib.request.Request(entry["url"])
    request.add_header("Authorization", f"Bearer {token.value()}")
    if resume_from:
        request.add_header("Range", f"bytes={resume_from}-")

    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            append = resume_from and response.status == 206
            with partial.open("ab" if append else "wb") as handle:
                while True:
                    block = response.read(CHUNK)
                    if not block:
                        break
                    handle.write(block)
    except (urllib.error.URLError, OSError) as exc:
        return {**entry, "status": "failed", "reason": f"{type(exc).__name__}: {exc}"}

    got = partial.stat().st_size
    if expected is not None and got != expected:
        return {
            **entry,
            "status": "failed",
            "reason": f"size mismatch: got {got} bytes, archive declares {expected}",
            "bytes": got,
        }

    partial.replace(target)
    result = {**entry, "status": "fetched", "bytes": got}
    if verify:
        result["sha256"] = _sha256(target)
    return result


def merge_into_receipt(summary: dict, previous: dict | None) -> dict:
    """Fold this run's results into whatever the receipt already recorded.

    The pull is run one tier at a time -- normals now, the 20GB of series overnight --
    so a receipt rebuilt from only the tiers THIS invocation asked for drops every file
    an earlier invocation fetched, while still reading as the complete record of what is
    on disk. Rows are keyed by archive path so a re-pull of the same file updates it
    rather than duplicating it, and the counts are recomputed from the merged set rather
    than added up, so re-running a tier cannot inflate them.
    """
    if not previous:
        return summary

    rows = {row["path"]: row for row in previous.get("files", [])}
    rows.update({row["path"]: row for row in summary["files"]})
    merged = sorted(rows.values(), key=lambda row: row["path"])

    failed = [row for row in merged if row["status"] == "failed"]
    return {
        **summary,
        "tiers": sorted({*previous.get("tiers", []), *summary["tiers"]}),
        "requested": len(merged),
        "complete": len(merged) - len(failed),
        "failed": len(failed),
        "bytes_on_disk": sum(row.get("bytes", 0) for row in merged),
        "files": merged,
    }


def run(tiers: tuple[str, ...], *, limit: int | None, verify: bool) -> dict:
    env = _load_credentials()
    token = Token(env)
    manifest = build_manifest(tiers)
    if limit is not None:
        manifest = manifest[:limit]

    results = []
    for index, entry in enumerate(manifest, start=1):
        outcome = fetch_one(entry, token, verify=verify)
        results.append(outcome)
        print(
            f"[{index}/{len(manifest)}] {outcome['status']:8s} {entry['path']}"
            + (f"  ({outcome.get('reason')})" if outcome.get("reason") else ""),
            flush=True,
        )

    failed = [r for r in results if r["status"] == "failed"]
    total_bytes = sum(r.get("bytes", 0) for r in results)
    return {
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "Met Office HadUK-Grid 1km, CEDA Archive",
        "dataset_version": DATASET_VERSION,
        "release_directory": RELEASE,
        "licence": LICENCE,
        "archive_root": ARCHIVE_ROOT,
        "cache_root": str(CACHE_ROOT),
        "token_source": token.source,
        "tiers": list(tiers),
        "requested": len(manifest),
        "complete": len(results) - len(failed),
        "failed": len(failed),
        "bytes_on_disk": total_bytes,
        "files": results,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tiers",
        default="normals",
        help="comma-separated: normals, monthly, daily (default: normals)",
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--verify",
        action="store_true",
        help="sha256 every file (slow; use when writing the committed receipt)",
    )
    parser.add_argument(
        "--receipt",
        action="store_true",
        help=f"write the receipt to {RECEIPT.relative_to(RECEIPT.parents[2])}",
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="print what would be pulled and exit, without credentials or network",
    )
    args = parser.parse_args(argv)

    tiers = tuple(t.strip() for t in args.tiers.split(",") if t.strip())
    known = {"normals", "monthly", "daily"}
    unknown = set(tiers) - known
    if unknown:
        print(f"unknown tier(s): {sorted(unknown)}; known: {sorted(known)}", file=sys.stderr)
        return 2

    if args.manifest_only:
        manifest = build_manifest(tiers)
        for entry in manifest:
            print(entry["path"])
        print(f"-- {len(manifest)} file(s)", file=sys.stderr)
        return 0

    try:
        summary = run(tiers, limit=args.limit, verify=args.verify)
    except PullRefused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1

    print(
        f"\n{summary['complete']}/{summary['requested']} complete, "
        f"{summary['failed']} failed, "
        f"{summary['bytes_on_disk'] / 1e9:.2f} GB on disk "
        f"(token: {summary['token_source']})"
    )

    if args.receipt:
        previous = None
        if RECEIPT.exists():
            try:
                previous = json.loads(RECEIPT.read_text())
            except (ValueError, json.JSONDecodeError):
                # An unreadable receipt is not an empty one. Refusing here rather than
                # starting fresh keeps a corrupt file from being laundered into a clean
                # record of a pull nobody can now account for.
                print(
                    f"REFUSED: {RECEIPT} exists but is not readable JSON; move it aside "
                    "before writing a new receipt",
                    file=sys.stderr,
                )
                return 1
        merged = merge_into_receipt(summary, previous)
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(merged, indent=2) + "\n")
        print(
            f"receipt: {RECEIPT} "
            f"({merged['complete']}/{merged['requested']} across tiers "
            f"{', '.join(merged['tiers'])})"
        )

    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
