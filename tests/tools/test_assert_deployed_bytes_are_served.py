"""R15 proof for the post-deploy freshness control.

The step this replaces (a zone cache purge) failed for its entire life while reporting
success, because nothing ever made it demonstrate that it COULD fail. These tests make
the replacement demonstrate it: each one names a defect the control exists to catch and
asserts the control fires on that defect.
"""
from __future__ import annotations

import hashlib

import pytest

from tools import assert_deployed_bytes_are_served as A


# --------------------------------------------------------------------------
# URL mapping. Measured live on 2026-08-20: `/proof/index.html` 404s while
# `/proof/` serves, so getting this backwards would fail every deploy.
# --------------------------------------------------------------------------
@pytest.mark.parametrize("path,expected", [
    ("site/index.html", "https://poesys.net/"),
    ("site/proof/index.html", "https://poesys.net/proof/"),
    ("site/data/dashboard.json", "https://poesys.net/data/dashboard.json"),
    ("site/brand/brand.css", "https://poesys.net/brand/brand.css"),
    ("site/_headers", None),          # config, not an asset -- fetching it 404s by design
    ("site/_redirects", None),
])
def test_repo_path_maps_to_the_url_a_reader_uses(path, expected):
    assert A.url_for(path) == expected


# --------------------------------------------------------------------------
# The control fires. Each helper below stands in for the network.
# --------------------------------------------------------------------------
def _run(monkeypatch, tmp_path, files, served, deleted=()):
    """files: {repo path -> bytes on disk}. served: {url -> bytes the edge returns}."""
    site = tmp_path / "site"
    for path, body in files.items():
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
    site.mkdir(exist_ok=True)
    monkeypatch.setattr(A, "PROJECT", str(tmp_path))
    monkeypatch.setattr(A, "ATTEMPTS", 2)
    monkeypatch.setattr(A, "GAP_SECONDS", 0)
    monkeypatch.setattr(
        A, "changed_files",
        lambda base: [("D", p) for p in deleted] + [("M", p) for p in files],
    )

    seen = []

    def fake_fetch(url, nonce):
        seen.append((url, nonce))
        if url not in served:
            raise OSError(f"404 {url}")
        return served[url]

    monkeypatch.setattr(A, "fetch", fake_fetch)
    return A.main(), seen


def test_passes_when_the_edge_serves_the_deployed_bytes(monkeypatch, tmp_path, capsys):
    body = b"<html>current</html>"
    rc, _ = _run(monkeypatch, tmp_path,
                 {"site/index.html": body},
                 {"https://poesys.net/": body})
    assert rc == 0
    assert "confirmed live" in capsys.readouterr().out


def test_FAILS_when_the_edge_serves_a_stale_copy(monkeypatch, tmp_path):
    """The named defect: a deploy succeeds and readers keep getting yesterday's page."""
    rc, _ = _run(monkeypatch, tmp_path,
                 {"site/index.html": b"<html>current</html>"},
                 {"https://poesys.net/": b"<html>YESTERDAY</html>"})
    assert rc == 1


def test_FAILS_when_the_asset_is_not_served_at_all(monkeypatch, tmp_path):
    """A deploy that silently dropped a file must not report success."""
    rc, _ = _run(monkeypatch, tmp_path, {"site/index.html": b"x"}, served={})
    assert rc == 1


def test_every_fetch_carries_a_distinct_cache_buster(monkeypatch, tmp_path):
    """Without a nonce the check can be answered by the cache it exists to see past --
    and a freshness check a stale copy can satisfy is theatre. A CONSTANT nonce is the
    same bug, so the nonces must also differ between retries."""
    _, seen = _run(monkeypatch, tmp_path,
                   {"site/index.html": b"a"},
                   {"https://poesys.net/": b"DIFFERENT"})   # forces both attempts
    assert seen, "the control never fetched anything"
    nonces = [nonce for _, nonce in seen]
    assert all(nonces), "a fetch went out with an empty cache-buster"
    assert len(set(nonces)) == len(nonces), f"retries reused a cache key: {nonces}"


def test_a_deleted_url_is_reported_but_never_asserted(monkeypatch, tmp_path, capsys):
    """Absence cannot be proven through an edge that serves last-known-good -- eight
    ghost pages were provably still being served on 2026-08-20 after eight deployments.
    Reporting that beats a check that quietly passes on it."""
    rc, seen = _run(monkeypatch, tmp_path,
                    {"site/index.html": b"a"},
                    {"https://poesys.net/": b"a"},
                    deleted=["site/proof/index.html"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "NOT ASSERTED" in out and "https://poesys.net/proof/" in out
    assert not any(url == "https://poesys.net/proof/" for url, _ in seen)


def test_an_uncomputable_diff_fails_closed(monkeypatch, tmp_path):
    """FAIL-OPEN, R15: deciding 'nothing changed, all good' when the diff itself broke is
    exactly how the purge step passed for its whole life."""
    monkeypatch.setattr(A, "PROJECT", str(tmp_path))     # not a git repo
    monkeypatch.setenv("GITHUB_SHA", "deadbeef")
    with pytest.raises(SystemExit):
        A.changed_files("cafebabe")
