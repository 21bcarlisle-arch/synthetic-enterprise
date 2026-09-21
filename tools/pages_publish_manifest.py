#!/usr/bin/env python3
"""THE ONE HOME for what the GitHub Pages root publishes.

WHAT THIS REPLACES, AND WHY IT IS A LIST RATHER THAN A FILTER
-------------------------------------------------------------
The Pages workflow used to upload `path: docs` -- the whole tree. `docs/` holds far more than
anything a reader was meant to see: 8,600 internal findings under `docs/staging/` (including
BLOCKING ones naming defects in our own published figures), 909 design documents, 282 observability
logs. All of it was served at `https://21bcarlisle-arch.github.io/synthetic-enterprise/`.

Nobody decided that. It was inherited from the day the site was one folder, and it survived because
the workflow ALSO carried a `paths-ignore:` list naming most of those directories -- which three
places in the repo then read as if it decided what was published. It does not. `paths-ignore` is a
TRIGGER filter: it decides whether the workflow RUNS on a given push, never what the run uploads.
That misreading is why `docs/shadow/` served a frozen 1.5m-pound internal P&L at a public root for a
month before anyone looked (80e363721, and docs/staging/SEAT_DECISION_THE_PAGES_ROOT_PUBLISHES_A_
NAMED_MANIFEST_NOT_THE_DOCS_TREE_2026-09-20.md for this landing).

So the artefact is no longer a directory. It is built from `PUBLISHED` below, and the workflow's
`paths:` trigger is derived from the same tuple by `trigger_paths()`. Trigger and publish are one
list, and `tests/tools/test_the_pages_artifact_is_the_manifest_not_the_docs_tree.py` reds if the
workflow's copy drifts from this one.

THE DIRECTION THIS FAILS IN, which is the point
------------------------------------------------
A path is published IF AND ONLY IF this tuple names it. A directory added to `docs/` tomorrow is not
published, and nothing has to notice it to keep it private. The old arrangement failed the other way
-- everything was published and a directory had to be noticed to be kept back -- and a surface that
grows silently is exactly what it produced.

HOW THE CONTENT WAS CHOSEN, and it was derived rather than picked
------------------------------------------------------------------
Every `https://21bcarlisle-arch.github.io/synthetic-enterprise/...` URL in the tracked tree was
enumerated first; `PUBLISHED` covers all of them and nothing else. `test_every_published_link_is_in
_the_manifest` re-derives that from the repo on every run, so an anchor added to PROJECT_OVERVIEW.md
without a manifest entry fails at commit time rather than 404-ing for a reader.

`docs/reports/` is named FILE BY FILE rather than as a directory, deliberately. Two of its 33 files
are the reports (`ANNUAL_REPORT.md`, `SEGMENT_REPORT.md`, 0.8 MB); the other 31 are raw run
outputs -- `run_output_latest.json` alone is 26 MB -- which nothing links to and which are working
artefacts of the simulation, not published material.

THE ONE-SIDEDNESS, stated here rather than left for the next reader to discover
-------------------------------------------------------------------------------
The URL-coverage control reads ABSOLUTE Pages URLs. A RELATIVE markdown link inside a published
`.md` can still point at an unpublished path; `test_every_relative_link_in_a_published_markdown_
resolves` covers that, but only for `[text](target)` syntax -- a bare reference-style link or an
HTML `<a href>` in a published markdown would not be seen. Measured at the time of writing: one such
relative link existed in the whole published set (`PROJECT_OVERVIEW.md` -> `design/ONE_FRAMEWORK.md`),
which is why that single file is named below while the rest of `docs/design/` is not.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

#: The Pages site root. The artefact's root IS `docs/`, so `docs/status/LATEST.md` is served at
#: `PAGES_ROOT + "status/LATEST.md"` -- `build()` strips this prefix.
DOCS_PREFIX = "docs/"

#: Everything the GitHub Pages root publishes. Repo-relative. A trailing "/" means the whole
#: directory; anything else is a single file. Every entry must live under `docs/`.
#:
#: Each entry carries WHO SENDS A READER HERE, because an entry nobody links to is a surface that
#: will rot unwatched -- which is the defect this module exists because of.
PUBLISHED = (
    "docs/PROJECT_OVERVIEW.md",          # the front door; the anchor block itself
    "docs/status/",                      # LATEST.md, PROJECT_STATE.txt, STARTUP_ANCHORS.md,
                                         #   SEAT_STRETCH_LOG.md -- four anchors on that block
    "docs/state/",                       # the advisor's state mirror (tools/mirror_github_pages.py)
    "docs/reports/ANNUAL_REPORT.md",     # the anchor block; tools/publish_report_gist.py; STATUS.md
    "docs/reports/SEGMENT_REPORT.md",    # cited beside the annual report
    "docs/market_research/",             # ASSUMPTIONS.md is an anchor; the sourced record behind it
    "docs/retrospectives/",              # tools/generate_method_data.py links each one by filename
    "docs/institutional/",               # knowledge_map.md is an anchor
    "docs/operations/",                  # MAINTENANCE.md is an anchor
    "docs/direction/",                   # DIRECTION.yaml + decisions.jsonl are anchors
    "docs/design/ONE_FRAMEWORK.md",      # the only relative link out of a published markdown
)

#: Files that change the ARTEFACT without being in it. They belong in the workflow trigger and
#: nowhere else: editing either can change what a reader gets, so a push touching one must deploy.
_TRIGGER_EXTRAS = (
    ".github/workflows/github-pages.yml",
    "tools/pages_publish_manifest.py",
)


def is_published(rel: str) -> bool:
    """Is this repo-relative path served at the Pages root?

    The predicate every other module should ask, instead of carrying its own copy of the list.
    """
    rel = rel.replace("\\", "/")
    for entry in PUBLISHED:
        if entry.endswith("/"):
            if rel.startswith(entry):
                return True
        elif rel == entry:
            return True
    return False


def trigger_paths() -> list[str]:
    """The workflow's `on.push.paths` list, derived from `PUBLISHED`.

    An INCLUSIVE filter, which is the whole correction: `paths-ignore` named only `docs/`
    subdirectories, so every push touching `company/`, `tools/` or `tests/` -- measured, 70% of the
    last 408 commits -- passed it and deployed a byte-identical artefact.
    """
    out = [f"{e}**" if e.endswith("/") else e for e in PUBLISHED]
    return out + list(_TRIGGER_EXTRAS)


def build(dest: Path, root: Path | None = None) -> list[str]:
    """Materialise the Pages artefact under `dest`. Returns the artefact-relative paths written.

    `dest` is created if absent and is NOT cleared -- callers pass a fresh directory. A manifest
    entry that does not exist in `root` is skipped rather than raising: the entry is a statement
    about what is published, and a generated report that has not been generated yet is not a
    publish failure. The URL-coverage control is what stops an entry going permanently missing.
    """
    root = Path(root) if root is not None else PROJECT
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    for entry in PUBLISHED:
        assert entry.startswith(DOCS_PREFIX), f"manifest entry outside docs/: {entry}"
        rel = entry[len(DOCS_PREFIX):]
        src = root / entry.rstrip("/")
        if not src.exists():
            continue
        if entry.endswith("/"):
            shutil.copytree(src, dest / rel.rstrip("/"), dirs_exist_ok=True)
            for p in sorted((dest / rel.rstrip("/")).rglob("*")):
                if p.is_file():
                    written.append(str(p.relative_to(dest)))
        else:
            (dest / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest / rel)
            written.append(rel)

    # Without this GitHub Pages runs Jekyll over the artefact, which drops underscore-prefixed
    # paths and rewrites markdown. The old arrangement got it from a committed `docs/.nojekyll`;
    # the artefact is built now, so it is written here.
    (dest / ".nojekyll").write_text("", encoding="utf-8")
    written.append(".nojekyll")
    return sorted(written)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python3 -m tools.pages_publish_manifest <dest-dir>", file=sys.stderr)
        raise SystemExit(2)
    paths = build(Path(sys.argv[1]))
    print(f"{len(paths)} file(s) -> {sys.argv[1]}")
