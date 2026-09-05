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
import os
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

# How often the receipt is rewritten mid-pull. The pull is hours long and is killed
# routinely -- by a bounded tick's cgroup, by a reboot, by the archive going away -- and
# a receipt written only on the last line means a killed pull leaves the record of the
# pull BEFORE it, however many GB it bought. That is what happened on 2026-09-05: 120 of
# 315 files on disk, and a committed receipt still declaring three normals and 124 MB.
# Five files is about two minutes of daily-tier wall clock; the cost is one 300 KB write.
CHECKPOINT_EVERY = 5

# A file the pull has not reached yet. It is a row rather than an absence so that
# `complete == requested` cannot come true by the manifest shrinking to what is done --
# a partial receipt whose counts balance reads exactly like a finished one.
PENDING = "pending"
ON_DISK_STATUSES = ("fetched", "present")


LOCK = CACHE_ROOT / ".pull.lock"


class PullRefused(RuntimeError):
    """Raised with a reason a human can act on. Never raised bare."""


def _process_identity(pid: int) -> str | None:
    """A pid PLUS the boot-clock tick it started at, or None if it is not running.

    The pid alone is not an identity. Linux recycles them, and a lock naming a recycled
    number reads as held forever -- the pull would refuse itself for the rest of the
    machine's uptime, which is a worse failure than the concurrency it guards. Field 22
    of /proc/<pid>/stat is the start time in clock ticks; a different process wearing the
    same number has a different one.
    """
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return None
    # The comm field is parenthesised and may itself contain spaces and brackets, so the
    # fields are counted from the LAST ')' rather than by splitting the whole line.
    fields = stat[stat.rfind(")") + 1:].split()
    return f"{pid}:{fields[19]}" if len(fields) > 19 else None


def acquire_lock(*, lock: Path = LOCK) -> str | None:
    """Refuse a second pull while one is running. Returns the identity written.

    Two pullers share the cache and append to the same `.part` file. The result is not a
    crash: it is a grid of the right name and the wrong bytes, which fails the size check
    and is written into the receipt as a failed row -- a gap the analysis would read as
    "the archive did not have this month". Fabricated evidence, from two processes each
    behaving correctly.

    This became reachable on 2026-09-05: the lane-0 claim for the pull was not held, so
    `--landed` bound nothing and the item stays drawable while its runner is still going.
    """
    if lock.exists():
        held = _process_identity_in(lock)
        if held:
            raise PullRefused(
                f"a pull is already running ({held}); {lock} holds it. Two pullers append "
                "to the same .part file and produce a grid of the right name and the "
                "wrong bytes. Wait for it, or stop that process first"
            )
    mine = _process_identity(os.getpid())
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text(f"{mine}\n" if mine else f"{os.getpid()}\n")
    return mine


def _process_identity_in(lock: Path) -> str | None:
    """The identity a lock file names, if that exact process is still alive."""
    try:
        written = lock.read_text().strip()
    except OSError:
        return None
    pid_text = written.split(":")[0]
    if not pid_text.isdigit():
        return None
    live = _process_identity(int(pid_text))
    # A bare pid from an older lock format cannot be told from a recycled one, so it is
    # honoured only as a pid. Anything carrying a start time must match it exactly.
    if ":" not in written:
        return written if live else None
    return written if live == written else None


def release_lock(identity: str | None, *, lock: Path = LOCK) -> None:
    """Drop the lock only if it is still OURS.

    A run that took the lock, was killed, and had it replaced by a later run must not
    delete the later run's lock on the way out.
    """
    if _process_identity_in(lock) == (identity or _process_identity(os.getpid())):
        lock.unlink(missing_ok=True)


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


def _walk_cache(root: Path = CACHE_ROOT) -> dict:
    """Count and size the grids actually on disk, without consulting the receipt.

    The receipt's `bytes_on_disk` is the sum of what each fetch REPORTED. This is a
    second route to the same quantity -- stat() over the tree -- so the two can be made
    to disagree. A receipt that sums its own rows and calls that agreement with the disk
    is the tautology this exists to avoid: it would balance perfectly while the cache was
    empty.

    `.part` files are excluded deliberately. A half-written grid is bytes on the disk and
    is not a file the analysis may read.
    """
    if not root.exists():
        return {"files": 0, "bytes": 0, "partials": 0}
    files = bytes_ = partials = 0
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.name.endswith(".part"):
            partials += 1
        elif path.suffix == ".nc":
            files += 1
            bytes_ += path.stat().st_size
    return {"files": files, "bytes": bytes_, "partials": partials}


def _season_label(start_year: int) -> str:
    return f"{start_year}/{(start_year + 1) % 100:02d}"


def daily_season_coverage(rows: list[dict]) -> dict:
    """State the heating seasons the daily tier covers as a COUNT, with named gaps.

    A heating season straddles the new year -- October to March, source document section
    3.4 -- so a file list ordered by calendar year cannot be read for it. Fifteen daily
    files is 'two and a half winters', not 'fifteen months of winter', and the difference
    is the whole persistence question: a cold spell that starts in December and ends in
    January is one spell, and it is invisible in a season that has only one of them.

    Every season the window touches is either counted complete or given a gap row with a
    reason. The two ends are always gaps and always will be: the pull starts in January
    1991, so 1990/91 can never have its October, and it ends in December 2025, so 2025/26
    cannot have its March until the archive publishes 2026. Naming them beats a count
    that quietly starts a year late.
    """
    have, absent = {}, {}
    for row in rows:
        year, month = row.get("year"), row.get("month")
        if row.get("frequency") != "day" or year is None or month is None:
            continue
        start = year if month >= 10 else year - 1
        bucket = have if row.get("status") in ON_DISK_STATUSES else absent
        bucket.setdefault(start, {})[month] = row.get("status")

    seasons = sorted({*have, *absent})
    complete, gaps = [], []
    for start in seasons:
        held = have.get(start, {})
        missing = []
        for year, month in ((start, 10), (start, 11), (start, 12),
                            (start + 1, 1), (start + 1, 2), (start + 1, 3)):
            if month in held:
                continue
            if not SERIES_FIRST_YEAR <= year <= SERIES_LAST_YEAR:
                reason = (
                    f"outside the pulled window "
                    f"{SERIES_FIRST_YEAR}-{SERIES_LAST_YEAR}"
                )
            else:
                reason = absent.get(start, {}).get(month) or "absent from the receipt"
            missing.append({"month": f"{year}-{month:02d}", "reason": reason})
        if missing:
            gaps.append(
                {
                    "season": _season_label(start),
                    "months_held": len(held),
                    "missing": missing,
                }
            )
        else:
            complete.append(_season_label(start))

    return {
        "definition": "October-March, source document section 3.4",
        "complete_seasons": len(complete),
        "first_complete": complete[0] if complete else None,
        "last_complete": complete[-1] if complete else None,
        "gaps": gaps,
    }


def finalise_receipt(merged: dict, *, walk: dict | None = None) -> dict:
    """Add the two things a reader cannot get from the rows alone.

    Kept out of `merge_into_receipt` so the merge stays pure and testable without a
    filesystem, and so the walk happens once at write time rather than per merge.
    """
    walk = _walk_cache() if walk is None else walk
    return {
        **merged,
        "cache_walk": {
            **walk,
            "receipt_bytes": merged["bytes_on_disk"],
            "reconciles": walk["bytes"] == merged["bytes_on_disk"],
        },
        "daily_heating_seasons": daily_season_coverage(merged.get("files", [])),
    }


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
    for row in summary["files"]:
        # A `pending` row is this run saying "not reached yet", which is weaker evidence
        # than a previous receipt saying "fetched, 74 MB, sha256 ...". Letting it win
        # would make every checkpoint erase the tiers already recorded -- the defect
        # merging was introduced to fix, arriving through the door the fix opened.
        held = rows.get(row["path"])
        if row["status"] == PENDING and held and held.get("status") != PENDING:
            continue
        rows[row["path"]] = row
    merged = sorted(rows.values(), key=lambda row: row["path"])

    failed = [row for row in merged if row["status"] == "failed"]
    pending = [row for row in merged if row["status"] == PENDING]
    on_disk = [row for row in merged if row["status"] in ON_DISK_STATUSES]
    return {
        **summary,
        "tiers": sorted({*previous.get("tiers", []), *summary["tiers"]}),
        "requested": len(merged),
        # Counted from the rows' own statuses, not `len(merged) - failed`: with pending
        # rows in the set that subtraction counts a file nobody has fetched as complete.
        "complete": len(on_disk),
        "failed": len(failed),
        "pending": len(pending),
        "pull_status": "complete" if not pending and not failed else "incomplete",
        "bytes_on_disk": sum(row.get("bytes", 0) for row in merged),
        "files": merged,
    }


def summarise(
    tiers: tuple[str, ...], manifest: list[dict], results: list[dict], token_source
) -> dict:
    """The receipt this run would write if it stopped right now.

    Manifest entries the run has not reached carry a `pending` row rather than being
    left out, so a summary taken mid-pull states the size of the job it is part way
    through instead of the size of the part it has done.
    """
    rows = results + [
        {**entry, "status": PENDING} for entry in manifest[len(results):]
    ]
    failed = [r for r in rows if r["status"] == "failed"]
    pending = [r for r in rows if r["status"] == PENDING]
    return {
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "Met Office HadUK-Grid 1km, CEDA Archive",
        "dataset_version": DATASET_VERSION,
        "release_directory": RELEASE,
        "licence": LICENCE,
        "archive_root": ARCHIVE_ROOT,
        "cache_root": str(CACHE_ROOT),
        "token_source": token_source,
        "tiers": list(tiers),
        "requested": len(rows),
        "complete": len([r for r in rows if r["status"] in ON_DISK_STATUSES]),
        "failed": len(failed),
        "pending": len(pending),
        "pull_status": "complete" if not pending and not failed else "incomplete",
        "bytes_on_disk": sum(r.get("bytes", 0) for r in rows),
        "files": rows,
    }


def run(
    tiers: tuple[str, ...], *, limit: int | None, verify: bool, checkpoint=None
) -> dict:
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
        if checkpoint and index % CHECKPOINT_EVERY == 0:
            checkpoint(summarise(tiers, manifest, results, token.source))

    return summarise(tiers, manifest, results, token.source)


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

    def write_receipt(summary: dict) -> dict:
        previous = None
        if RECEIPT.exists():
            try:
                previous = json.loads(RECEIPT.read_text())
            except (ValueError, json.JSONDecodeError) as exc:
                # An unreadable receipt is not an empty one. Refusing here rather than
                # starting fresh keeps a corrupt file from being laundered into a clean
                # record of a pull nobody can now account for.
                raise PullRefused(
                    f"{RECEIPT} exists but is not readable JSON ({exc}); move it aside "
                    "before writing a new receipt"
                ) from exc
        merged = finalise_receipt(merge_into_receipt(summary, previous))
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(merged, indent=2) + "\n")
        return merged

    try:
        identity = acquire_lock()
    except PullRefused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1

    # The lock is held across the FINAL receipt write, not just the fetching. A second
    # puller starting in the gap between the last file and the last write would merge
    # against a receipt this run is still holding in memory.
    try:
        return _pull(args, tiers, write_receipt)
    finally:
        release_lock(identity)


def _pull(args, tiers: tuple[str, ...], write_receipt) -> int:
    try:
        summary = run(
            tiers,
            limit=args.limit,
            verify=args.verify,
            checkpoint=write_receipt if args.receipt else None,
        )
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
        try:
            merged = write_receipt(summary)
        except PullRefused as exc:
            print(f"REFUSED: {exc}", file=sys.stderr)
            return 1
        seasons = merged["daily_heating_seasons"]
        walk = merged["cache_walk"]
        print(
            f"receipt: {RECEIPT} "
            f"({merged['complete']}/{merged['requested']} across tiers "
            f"{', '.join(merged['tiers'])}, {merged['pull_status']})\n"
            f"  heating seasons complete: {seasons['complete_seasons']} "
            f"({seasons['first_complete']}..{seasons['last_complete']}), "
            f"{len(seasons['gaps'])} with gaps\n"
            f"  cache walk: {walk['files']} files, {walk['bytes'] / 1e9:.2f} GB, "
            f"reconciles={walk['reconciles']}"
        )

    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
