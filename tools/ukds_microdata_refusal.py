"""A commit that stages UK Data Service microdata is refused, by path.

The director's ruling of 2 Nov 2026 (`docs/staging/advisor/done/DIRECTOR_RULING_YES_TO_THE_VALUE_TEST_REDESIGN_
AND_REGISTER_WITH_UKDS_NON_COMMERCIAL_2026-11-02.md`) lets licensed survey files sit in `~/ukds/`, outside this
public repository, and asks for "a pre-commit guard that refuses any file from that path or with a UKDS dataset
signature". Only aggregates may leave that directory, and they leave as files written fresh inside the repo.

What counts as a signature, and why each one:

- the path resolves into `~/ukds/` (a symlink, or a copy the hook can trace back);
- a path component of the shape a UKDS download unpacks to: `UKDA-6614-tab`, `UKDA-7215-stata`, and so on;
- a UKDS study information page, `UKDA_Study_<n>_Information.htm`, which ships inside every bundle;
- a statistical-package microdata file (`.dta`, `.sav`, `.por`, `.sas7bdat`). Nothing in this tree is one, and a
  published aggregate is never shipped in those formats here.

A DOI or a study number in prose (`UKDA-SN-9315`, `SN 6614`) is not a signature: the registration pack and the
knowledge pages cite them as the licence requires.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

UKDS_HOME = Path(os.path.expanduser("~/ukds"))

_BUNDLE_DIR = re.compile(r"^UKDA-\d{4}-(tab|stata|spss|sas)$", re.IGNORECASE)
_STUDY_PAGE = re.compile(r"^UKDA_Study_\d+_Information\.html?$", re.IGNORECASE)
_MICRODATA_SUFFIXES = {".dta", ".sav", ".por", ".sas7bdat"}


def reason(path: str, repo: Path) -> str | None:
    """The named reason `path` is UKDS microdata, or None."""
    parts = Path(path).parts
    for part in parts[:-1]:
        if _BUNDLE_DIR.match(part):
            return f"a directory named like a UKDS download bundle ({part})"
    name = parts[-1] if parts else path
    if _STUDY_PAGE.match(name):
        return "a UKDS study information page, which ships inside a download bundle"
    if Path(name).suffix.lower() in _MICRODATA_SUFFIXES:
        return f"a statistical-package microdata file ({Path(name).suffix})"
    try:
        real = (repo / path).resolve()
    except OSError:
        return None
    if real == UKDS_HOME.resolve() or UKDS_HOME.resolve() in real.parents:
        return f"it resolves into {UKDS_HOME}"
    return None


def staged(repo: Path) -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        cwd=repo, capture_output=True, text=True, check=True,
    ).stdout
    return [line for line in out.splitlines() if line]


def violations(paths: list[str], repo: Path) -> list[tuple[str, str]]:
    return [(p, r) for p in paths if (r := reason(p, repo))]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--staged", action="store_true", help="check the paths this index would commit")
    ap.add_argument("paths", nargs="*", help="check these paths instead")
    args = ap.parse_args(argv)
    repo = Path.cwd()
    paths = staged(repo) if args.staged else args.paths
    found = violations(paths, repo)
    if not found:
        return 0
    print("[ukds-microdata] COMMIT REFUSED: UK Data Service microdata never enters this public repository.")
    for path, why in found:
        print(f"    {path}: {why}")
    print(f"Licensed files live in {UKDS_HOME} (dir 700, files 600). Only aggregates leave it, written fresh into")
    print("the repo: fitted loadings, and cross-tabs that meet the depositor's cell-size rules.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
