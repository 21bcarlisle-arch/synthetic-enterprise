"""Tests for tools/mirror_github_pages.py (Phase QG, docs/staging/ADVISOR_GITHUBIO_MIRROR.md):
poesys.net proven persistently stale to the advisor's own fetch path (independent of
any CD incident); the state JSONs must also be mirrored onto docs/ so GitHub Pages
serves them, matching the pattern already proven reliable for
docs/status/PROJECT_STATE.txt.

THE SHADOW CASES ARE GONE, 2026-09-20 (docs/staging/SEAT_FINDING_THE_PAGES_ROOT_SERVES_A_
RETIRED_MIRROR_AND_PATHS_IGNORE_IS_NOT_A_PUBLISH_FILTER_2026-09-20.md). Two cases here drove
the `site/shadow/` -> `docs/shadow/` copy and a third asserted it replaced a stale tree. That
copy is deleted, not disabled, so the cases are deleted with it rather than being adjusted to
assert the no-op: a test that pins "the copy does nothing" would go red the day someone made it
do something again, which is backwards -- the refusal that matters now lives in
`test_a_stamped_page_at_the_pages_root_has_a_live_writer.py`, keyed to the property (a generated
page must not outlive its generator) rather than to this module's shape.

`test_mirror_skips_missing_source_files_without_error` is kept and is now a pure state-JSON
case; it was never about the shadow tree.
"""
import json

import tools.mirror_github_pages as mirror_mod


def test_mirror_copies_state_jsons(tmp_path, monkeypatch):
    src = tmp_path / "site" / "state" / "customer_sample.json"
    src.parent.mkdir(parents=True)
    src.write_text(json.dumps({"a": 1}))

    monkeypatch.setattr(mirror_mod, "DOCS_STATE", tmp_path / "docs" / "state")
    monkeypatch.setattr(mirror_mod, "_STATE_JSON_FILES", [(src, "customer_sample.json")])

    written = mirror_mod.mirror()

    dest = tmp_path / "docs" / "state" / "customer_sample.json"
    assert json.loads(dest.read_text()) == {"a": 1}
    assert str(dest) in written


def test_mirror_skips_missing_source_files_without_error(tmp_path, monkeypatch):
    monkeypatch.setattr(mirror_mod, "DOCS_STATE", tmp_path / "docs" / "state")
    monkeypatch.setattr(mirror_mod, "_STATE_JSON_FILES", [
        (tmp_path / "does_not_exist.json", "does_not_exist.json"),
    ])

    written = mirror_mod.mirror()

    assert written == []


def test_the_shadow_copy_is_gone_not_merely_unused():
    """The deleted `site/shadow/` -> `docs/shadow/` copy must not come back as a no-op.

    THE DEFECT THIS NAMES, and it is the reason the copy was removed rather than left
    inert: the copy was already a no-op for a month (its source was deleted by the
    2026-08-20 five-tab ruling) and that is exactly what made it dangerous. A no-op copy
    step is not harmless machinery, it is a mechanism waiting for its input -- anything
    that recreates `site/shadow/` would have had it mirrored onto the PUBLIC Pages root on
    the next publish cycle, silently, with nobody having decided to publish anything.

    Keyed to the module's surface rather than to a line of its source, so it survives
    reformatting and still fires on a reintroduction under any of the old names.
    """
    assert not hasattr(mirror_mod, "SITE_SHADOW")
    assert not hasattr(mirror_mod, "DOCS_SHADOW")
    assert "shadow" not in mirror_mod.mirror.__doc__.lower()
    assert all("shadow" not in str(src).lower() and "shadow" not in name.lower()
               for src, name in mirror_mod._STATE_JSON_FILES)
