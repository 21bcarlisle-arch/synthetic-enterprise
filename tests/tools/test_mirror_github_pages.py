"""Tests for tools/mirror_github_pages.py (Phase QG, docs/staging/ADVISOR_GITHUBIO_MIRROR.md):
poesys.net proven persistently stale to the advisor's own fetch path (independent of
any CD incident); shadow pages + state JSONs must also be mirrored onto docs/ so
GitHub Pages serves them, matching the pattern already proven reliable for
docs/status/PROJECT_STATE.txt."""
import json
from pathlib import Path

import tools.mirror_github_pages as mirror_mod


def test_mirror_copies_shadow_pages(tmp_path, monkeypatch):
    site_shadow = tmp_path / "site" / "shadow"
    (site_shadow / "customers").mkdir(parents=True)
    (site_shadow / "index.html").write_text("<html>overview</html>")
    (site_shadow / "customers" / "index.html").write_text("<html>customers</html>")

    monkeypatch.setattr(mirror_mod, "SITE_SHADOW", site_shadow)
    monkeypatch.setattr(mirror_mod, "DOCS_SHADOW", tmp_path / "docs" / "shadow")
    monkeypatch.setattr(mirror_mod, "DOCS_STATE", tmp_path / "docs" / "state")
    monkeypatch.setattr(mirror_mod, "_STATE_JSON_FILES", [])

    written = mirror_mod.mirror()

    dest = tmp_path / "docs" / "shadow"
    assert (dest / "index.html").read_text() == "<html>overview</html>"
    assert (dest / "customers" / "index.html").read_text() == "<html>customers</html>"
    assert len(written) == 2


def test_mirror_copies_state_jsons(tmp_path, monkeypatch):
    src = tmp_path / "site" / "state" / "customer_sample.json"
    src.parent.mkdir(parents=True)
    src.write_text(json.dumps({"a": 1}))

    monkeypatch.setattr(mirror_mod, "SITE_SHADOW", tmp_path / "no_such_shadow")
    monkeypatch.setattr(mirror_mod, "DOCS_SHADOW", tmp_path / "docs" / "shadow")
    monkeypatch.setattr(mirror_mod, "DOCS_STATE", tmp_path / "docs" / "state")
    monkeypatch.setattr(mirror_mod, "_STATE_JSON_FILES", [(src, "customer_sample.json")])

    written = mirror_mod.mirror()

    dest = tmp_path / "docs" / "state" / "customer_sample.json"
    assert json.loads(dest.read_text()) == {"a": 1}
    assert str(dest) in written


def test_mirror_skips_missing_source_files_without_error(tmp_path, monkeypatch):
    monkeypatch.setattr(mirror_mod, "SITE_SHADOW", tmp_path / "no_such_shadow")
    monkeypatch.setattr(mirror_mod, "DOCS_SHADOW", tmp_path / "docs" / "shadow")
    monkeypatch.setattr(mirror_mod, "DOCS_STATE", tmp_path / "docs" / "state")
    monkeypatch.setattr(mirror_mod, "_STATE_JSON_FILES", [
        (tmp_path / "does_not_exist.json", "does_not_exist.json"),
    ])

    written = mirror_mod.mirror()

    assert written == []
    assert not (tmp_path / "docs" / "shadow").exists()


def test_mirror_overwrites_stale_docs_shadow_tree(tmp_path, monkeypatch):
    """A page removed from site/shadow/ (or renamed) must not linger as a
    stale copy under docs/shadow/ -- the mirror replaces the whole tree."""
    site_shadow = tmp_path / "site" / "shadow"
    site_shadow.mkdir(parents=True)
    (site_shadow / "index.html").write_text("new content")

    docs_shadow = tmp_path / "docs" / "shadow"
    docs_shadow.mkdir(parents=True)
    (docs_shadow / "stale_page.html").write_text("should be removed")

    monkeypatch.setattr(mirror_mod, "SITE_SHADOW", site_shadow)
    monkeypatch.setattr(mirror_mod, "DOCS_SHADOW", docs_shadow)
    monkeypatch.setattr(mirror_mod, "DOCS_STATE", tmp_path / "docs" / "state")
    monkeypatch.setattr(mirror_mod, "_STATE_JSON_FILES", [])

    mirror_mod.mirror()

    assert not (docs_shadow / "stale_page.html").exists()
    assert (docs_shadow / "index.html").read_text() == "new content"
