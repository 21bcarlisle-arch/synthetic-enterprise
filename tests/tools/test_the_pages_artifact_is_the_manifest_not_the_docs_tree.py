"""THE DEFECT: the GitHub Pages workflow uploaded `path: docs` -- the whole tree -- while three
places in the repo reasoned as if a `paths-ignore:` list decided what was published. It does not:
`paths-ignore` is a TRIGGER filter. 8,600 internal findings, 909 design documents and 282
observability logs were served at a public root, and `docs/shadow/` sat there with a frozen
1.5m-pound internal P&L on it for a month (80e363721) before anyone looked.

Landing: docs/staging/SEAT_DECISION_THE_PAGES_ROOT_PUBLISHES_A_NAMED_MANIFEST_NOT_THE_DOCS_TREE_
2026-09-20.md.

WHAT THESE LEGS ARE KEYED TO, and it is not today's answer
-----------------------------------------------------------
Not "docs/staging is absent from the artefact" -- that is an instance, and the same defect lands
under a new directory next week. The property is **the artefact is exactly the manifest, in both
directions, and every surface the repo points a reader at is in it**:

  * UNDER-PUBLISHING -- an anchor added to PROJECT_OVERVIEW.md with no manifest entry 404s for a
    reader. `test_every_published_link_is_in_the_manifest` derives its subject from the repo's own
    URLs, so it cannot be satisfied by editing the list it grades.
  * OVER-PUBLISHING -- `test_the_builder_omits_a_directory_the_manifest_does_not_name` is the leg
    that can actually fail, and it is where the non-vacuity lives.
  * DRIFT -- the workflow holds a second copy of the list (GitHub Actions cannot call Python to
    decide a trigger). `test_the_workflow_trigger_is_the_manifest` is why the copy cannot rot.

NON-VACUITY, stated because the sibling control in 80e363721 SHIPPED GREEN TWICE before a real page
could fail it. The URL-coverage leg passed on the first draft and proves nothing on its own; it is
kept because it fails in the under-publishing direction, which nothing else covers. The leg that
proves the mechanism is the builder run over a fixture tree holding an unlisted directory, asserting
the directory is ABSENT from the output -- and the same fixture asserts a listed one is PRESENT, so
a builder that copied nothing at all could not pass either.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest
import yaml

from tools import pages_publish_manifest as M
from tools.python_code_text import searchable

PROJECT = Path(__file__).resolve().parents[2]
WORKFLOW = PROJECT / ".github" / "workflows" / "github-pages.yml"
PAGES_ROOT = "https://21bcarlisle-arch.github.io/synthetic-enterprise/"


def _tracked() -> list[str]:
    done = subprocess.run(("git", "ls-files"), cwd=str(PROJECT),
                          capture_output=True, text=True, timeout=120)
    assert done.returncode == 0, f"git ls-files failed: {done.stderr[:200]}"
    return [p for p in done.stdout.split("\n") if p.strip()]


def _referenced_pages_urls() -> dict[str, set[str]]:
    """Pages-root URLs the repo sends a reader to -> the files that send them.

    The subject is derived from the tree, never from `PUBLISHED`. Observability logs and archived
    snapshots are skipped as SOURCES: they record what a URL used to be, so a dead link in an
    append-only log is history, not a broken promise. They are not skipped as TARGETS.

    LAUNDERED THROUGH `searchable()`, and it makes this leg truer rather than merely compliant. A
    Pages URL inside a Python COMMENT is not a promise to a reader -- `tools/couple_w2_11_d5.py`
    has one in a tombstone about a page that no longer exists -- and counting it would let prose
    about a dead link demand that the link be published. It is the same fail-open that silenced the
    sibling control in 80e363721, where a log sentence describing a copy that had stopped happening
    counted as a live writer. `searchable()` returns the original text unchanged for anything that
    does not parse as Python, so markdown, HTML and JSON are read exactly as before.

    Measured after the change: 34 URLs, unchanged coverage. The retrospective links survive because
    `site/data/method.json` -- a generated feed, not source -- carries them, even though the
    generator's own f-string that builds them is now correctly read as code.
    """
    pat = re.compile(re.escape(PAGES_ROOT) + r"([A-Za-z0-9._/-]*)")
    out: dict[str, set[str]] = {}
    for rel in _tracked():
        if rel.startswith(("docs/observability/", "docs/snapshots/", "docs/staging/")):
            continue
        try:
            text = searchable((PROJECT / rel).read_text(encoding="utf-8", errors="replace"))
        except (OSError, UnicodeError):
            continue
        if PAGES_ROOT not in text:
            continue
        for tail in pat.findall(text):
            tail = tail.rstrip(".,);:'\"")
            if not tail or tail.endswith("/"):
                continue  # a directory listing, not a file this manifest can carry
            out.setdefault(f"docs/{tail}", set()).add(rel)
    return out


# --------------------------------------------------------------------------------------------
# UNDER-PUBLISHING: the manifest must cover what the repo already points at.
# --------------------------------------------------------------------------------------------

def test_every_published_link_is_in_the_manifest():
    refs = _referenced_pages_urls()
    # The floor is the non-vacuity guard for THIS leg: an empty scan (a moved URL constant, a
    # broken regex) would otherwise read as "no complaint", which is the fail-open R15 names.
    # Nine is the anchor block's own count at the time of writing; a tenth raises nothing.
    assert len(refs) >= 9, f"only {len(refs)} Pages URLs found in the tree -- the scan is broken"

    missing = {u: sorted(src) for u, src in refs.items() if not M.is_published(u)}
    assert not missing, (
        "these paths are linked at the Pages root but the manifest does not publish them, so a "
        f"reader following the link gets a 404: {missing}")


def test_every_relative_link_in_a_published_markdown_resolves():
    """The absolute-URL scan is blind to `[text](design/ONE_FRAMEWORK.md)` inside a published file.

    That single link is why `docs/design/ONE_FRAMEWORK.md` is named in the manifest while the rest
    of `docs/design/` is not -- measured, it was the only one in all 146 published markdowns.
    """
    import posixpath

    link = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
    published_md = [p for p in _tracked() if p.endswith(".md") and M.is_published(p)]
    assert len(published_md) >= 20, f"only {len(published_md)} published markdowns -- scan broken"

    escapes = []
    for rel in published_md:
        for target in link.findall((PROJECT / rel).read_text(encoding="utf-8", errors="replace")):
            if re.match(r"^(https?:|mailto:|#)", target):
                continue
            resolved = posixpath.normpath(
                posixpath.join(posixpath.dirname(rel), target.split("#")[0]))
            if not M.is_published(resolved):
                escapes.append((rel, target, resolved))
    assert not escapes, (
        f"relative links in published markdown pointing outside the artefact: {escapes}")


# --------------------------------------------------------------------------------------------
# OVER-PUBLISHING: the leg that can fail, and the only one that proves the mechanism.
# --------------------------------------------------------------------------------------------

def test_the_builder_omits_a_directory_the_manifest_does_not_name(tmp_path, monkeypatch):
    """THE LEG WITH THE TEETH. Both halves are asserted: a builder that copied nothing would pass
    the omission half on its own, and one that copied everything would pass the inclusion half."""
    root = tmp_path / "repo"
    (root / "docs" / "status").mkdir(parents=True)
    (root / "docs" / "status" / "LATEST.md").write_text("live", encoding="utf-8")
    (root / "docs" / "staging").mkdir(parents=True)
    (root / "docs" / "staging" / "SEAT_FINDING_INTERNAL.md").write_text(
        "BLOCKING: our published figure is wrong", encoding="utf-8")
    (root / "docs" / "design").mkdir(parents=True)
    (root / "docs" / "design" / "SECRET.md").write_text("internal", encoding="utf-8")

    out = tmp_path / "artefact"
    written = M.build(out, root=root)

    assert "status/LATEST.md" in written, "a manifest entry that exists was not published"
    assert (out / "status" / "LATEST.md").read_text(encoding="utf-8") == "live"

    assert not (out / "staging").exists(), (
        "docs/staging/ reached the artefact -- the builder is publishing the tree, not the list")
    assert not (out / "design").exists(), "docs/design/ reached the artefact"
    assert not any(w.startswith(("staging/", "design/")) for w in written)


def test_the_builder_writes_nojekyll():
    """Without it Pages runs Jekyll over the artefact, which drops underscore paths and rewrites
    markdown. It came from a committed `docs/.nojekyll` when the artefact was a directory; the
    artefact is built now, so nothing else can supply it."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        assert ".nojekyll" in M.build(Path(td))
        assert (Path(td) / ".nojekyll").exists()


def test_a_manifest_entry_outside_docs_is_refused(tmp_path, monkeypatch):
    """The artefact root IS `docs/`, so `build` strips that prefix. An entry that does not carry
    it would be published at a path nobody can predict."""
    monkeypatch.setattr(M, "PUBLISHED", ("site/index.html",))
    with pytest.raises(AssertionError, match="outside docs/"):
        M.build(tmp_path / "out", root=PROJECT)


def test_the_internal_directories_that_were_served_are_not_published():
    """The instance, kept as a named regression beside the property legs above. These are the
    directories that were actually on the public root on 2026-09-20."""
    for served in ("docs/staging/SEAT_FINDING_X.md", "docs/design/ANY.md",
                   "docs/observability/session-watchdog-log.md", "docs/instructions/X.md",
                   "docs/review_gates/X.md", "docs/claude/phase-history.md",
                   "docs/context-handshake-latest.md", "docs/shadow/index.html"):
        assert not M.is_published(served), f"{served} is still published"


# --------------------------------------------------------------------------------------------
# DRIFT: the workflow's second copy of the list.
# --------------------------------------------------------------------------------------------

def _spec() -> dict:
    """The workflow, parsed. THE ONLY READER IN THIS FILE -- `tests/architecture/
    test_a_control_reads_python_as_code.py` censuses a scope that names a file and reads it, and
    two scopes doing the same read is two rows saying one thing."""
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _on_push() -> dict:
    spec = _spec()
    # PyYAML 1.1 resolves the bare key `on:` to the boolean True.
    return (spec[True] if True in spec else spec["on"])["push"]


def test_the_workflow_trigger_is_the_manifest():
    """GitHub Actions cannot call Python to decide a trigger, so the workflow holds a second copy
    of the list. This is what stops it rotting -- and it is the precise failure the old
    `paths-ignore` had, a list nobody could tell had stopped describing reality."""
    on_push = _on_push()
    assert on_push.get("paths-ignore") is None, (
        "paths-ignore is back. It is a TRIGGER filter and was read as a publish filter three "
        "times in this repo; the inclusive `paths:` list is what replaced it.")
    assert on_push["paths"] == M.trigger_paths(), (
        "the workflow trigger has drifted from tools.pages_publish_manifest.trigger_paths()")


def test_the_upload_step_ships_the_built_artefact_not_the_docs_tree():
    steps = _spec()["jobs"]["deploy"]["steps"]
    upload = [s for s in steps if "upload-pages-artifact" in str(s.get("uses", ""))]
    assert len(upload) == 1, f"expected exactly one upload step, found {len(upload)}"
    path = upload[0]["with"]["path"]
    assert path != "docs", "the workflow is uploading the whole docs/ tree again"

    builds = [s for s in steps if "pages_publish_manifest" in str(s.get("run", ""))]
    assert builds, "nothing in the workflow builds the artefact"
    assert path in str(builds[0]["run"]), (
        f"the upload path {path!r} is not what the build step writes: {builds[0]['run']!r}")
