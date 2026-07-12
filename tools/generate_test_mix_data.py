#!/usr/bin/env python3
"""Generate site/data/test_mix.json — the test-suite composition breakdown.

Director page comments (/project/, 2026-07-12): "I'm really not a fan of
these graphs as I've said. What is the so what?... about velocity and
depth?" followed by "Would it help to show the mix of tests? The scope of
what we are testing each time?" The existing Test Count Growth / Build
Cadence charts show VELOCITY (how fast); this shows DEPTH (how much of the
real business is actually under test) -- a real, mechanically-derived
breakdown by test directory, not a hand-curated narrative grouping (same
R-A discipline as tools/generate_phases_json.py: nothing hand-written,
everything derives or dies).

Areas are exactly the real `tests/` directory tree, one level deep, except
`tests/company/` which is expanded a second level -- it holds ~70% of the
whole suite (billing/compliance/crm/finance/market/pricing/regulatory/risk/
trading/etc.), and collapsing it to one "company" bucket would hide the
exact scope-of-domains-modelled story this was asked for. No other
directory gets this treatment; it is not a hand-picked exception, it is the
one directory disproportionate enough that a flat listing would erase the
signal being asked for.
"""
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
TESTS_DIR = PROJECT / "tests"
OUT_PATH = PROJECT / "site" / "data" / "test_mix.json"

# tests/company/ is expanded one level deeper; every other top-level tests/
# subdirectory (plus the loose *.py files directly in tests/) is one area.
_EXPAND_ONE_LEVEL_DEEPER = {"company"}


def _collect_count(path: Path) -> int:
    """Real pytest collection count for `path` -- not a text-mined estimate,
    the actual number pytest would run. Returns 0 on any collection failure
    (e.g. an empty directory) rather than raising, since a missing/renamed
    area should degrade to "not shown", not break the whole generator."""
    try:
        result = subprocess.run(
            ["python3", "-m", "pytest", str(path), "--collect-only", "-q"],
            cwd=str(PROJECT), capture_output=True, text=True, timeout=120,
        )
    except Exception:
        return 0
    for line in reversed(result.stdout.splitlines()):
        line = line.strip()
        if "collected" in line or "test" in line:
            for token in line.split():
                if token.isdigit():
                    return int(token)
            break
    return 0


def _loose_file_count(directory: Path, subdir_areas_total: int) -> int:
    """Tests contributed by *.py files directly in `directory` (not inside
    any of its own subdirectories) -- collecting `directory` as a single
    pytest target is inclusive of every subdirectory beneath it, so
    subtracting the already-counted subdirectory total leaves exactly the
    loose files' own tests. Exact, not an estimate.

    Real bug this fixes (found while building this, 2026-07-12): a first
    version of this function only ever iterated a directory's SUBDIRECTORIES
    when expanding it one level deeper, silently dropping every loose *.py
    file directly inside it. tests/company/ alone has 60+ such files
    (test_phase_XX_coverage_expansion.py etc.) totalling 1,927 tests --
    entirely uncounted, no error, no warning, just a wrong number. Caught by
    cross-checking the per-area sum against a real whole-tree collect-only
    count rather than trusting either figure alone."""
    return max(0, _collect_count(directory) - subdir_areas_total)


def compute_test_mix() -> dict:
    areas = []
    total = 0

    for entry in sorted(TESTS_DIR.iterdir()):
        if not entry.is_dir() or entry.name == "__pycache__":
            continue
        if entry.name in _EXPAND_ONE_LEVEL_DEEPER:
            subdir_total = 0
            for sub in sorted(entry.iterdir()):
                if not sub.is_dir() or sub.name == "__pycache__":
                    continue
                count = _collect_count(sub)
                if count == 0:
                    continue
                areas.append({"name": entry.name + "/" + sub.name, "count": count})
                total += count
                subdir_total += count
            loose = _loose_file_count(entry, subdir_total)
            if loose > 0:
                # "general" not "root files" -- this label renders directly
                # on a director-facing chart, and every other area name here
                # is a real business domain (billing, crm, market...);
                # a bare filesystem term would read oddly next to them.
                areas.append({"name": entry.name + " (general)", "count": loose})
                total += loose
        else:
            count = _collect_count(entry)
            if count == 0:
                continue
            areas.append({"name": entry.name, "count": count})
            total += count

    loose_root = _loose_file_count(TESTS_DIR, total)
    if loose_root > 0:
        areas.append({"name": "top-level (general)", "count": loose_root})
        total += loose_root

    areas.sort(key=lambda a: -a["count"])
    return {"total": total, "areas": areas}


def generate() -> dict:
    data = compute_test_mix()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, indent=2))
    print("Written: {} (total={}, areas={})".format(OUT_PATH, data["total"], len(data["areas"])))
    return data


if __name__ == "__main__":
    generate()
