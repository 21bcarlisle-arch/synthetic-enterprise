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


# --------------------------------------------------------------------------
# The timeout names WHICH world it is in.
#
# THE DEFECT THESE OWN. Between 2026-09-01 and 2026-09-04 ten Cloudflare Pages
# runs went red. In all ten `wrangler pages deploy` had already succeeded and
# only this assertion failed, and all ten printed the same sentence -- "are
# still not what poesys.net serves" -- for a case where the bytes were in fact
# served correctly minutes later. That sentence asserts something about the
# READER that the control had not established, on the one signal that is
# supposed to mean the figures stopped reaching them. One sentence for two
# worlds is what made the reds unreadable.
# --------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _no_edge_probe(monkeypatch):
    """`edge` opens a socket to the live site; the tests here stub it."""
    monkeypatch.setattr(A, "edge", lambda path: "edge: stub")


def test_a_route_serving_neither_names_which_past_commit_it_is_serving(monkeypatch):
    """The front door went STALE on four pushes of 2026-10-22 and nobody could say what it was
    serving instead. The two outcomes, an older page of ours and a page we never published, need
    different remedies, so both must be reachable and must not read the same.
    MUTATION: drop the match loop and the first leg reds; match unconditionally and the second
    does."""
    want = hashlib.sha256(b"<html>today</html>").hexdigest()
    monkeypatch.setattr(A, "fetch", lambda url, nonce: b"<html>three back</html>")
    monkeypatch.setattr(A, "recent_commits", lambda path: ["aaa", "bbb", "ccc", "ddd"])
    history = {"aaa": b"<html>today</html>", "bbb": b"<html>yesterday</html>",
               "ccc": b"<html>two back</html>", "ddd": b"<html>three back</html>"}
    monkeypatch.setattr(A, "bytes_at", lambda ref, path: history.get(ref))
    older = A.classify("https://poesys.net/", want, "site/index.html", "bbb", True)
    monkeypatch.setattr(A, "fetch", lambda url, nonce: b"<html>an error page</html>")
    foreign = A.classify("https://poesys.net/", want, "site/index.html", "bbb", True)
    assert ("committed at ddd, 3 commit(s) back" in older and "edge: stub" in older
            and "matches none of this path's last 4 commits" in foreign), (older, foreign)
    # 22 Oct, LAX: the right page by title, and a hash matching no commit, so "not a page we
    # published" was a claim the evidence contradicted. Fires if that wording comes back.
    assert "not a page we published" not in foreign and "differ from the commit's" in foreign


_PAGE = (b"<!doctype html><html><head><title>Poesys - The code</title></head><body>"
         + b"<p>every module a star</p>" * 20 + b"</body></html>")


def _at_the_edge(monkeypatch, served):
    """classify, with the served body and the deployed file both given: the shape is computed
    from the two bodies, so neither may come from the network or the checkout."""
    monkeypatch.setattr(A, "fetch", lambda url, nonce: served)
    monkeypatch.setattr(A, "bytes_at", lambda ref, path: None)
    monkeypatch.setattr(A, "recent_commits", lambda path: [])
    monkeypatch.setattr(A, "deployed_bytes", lambda path: _PAGE)
    return A.classify("https://poesys.net/code/", hashlib.sha256(_PAGE).hexdigest(),
                      "site/code/index.html", "BASE", True)


def test_a_TRUNCATED_body_is_named_with_both_lengths_and_where_it_stops(monkeypatch):
    """Explanation 2 of the 22 Oct finding: a short read by fetch(). Fires if the shape is not
    computed, or if a truncation is reported as something else."""
    verdict = _at_the_edge(monkeypatch, _PAGE[:200])
    assert verdict.startswith("STALE"), verdict
    assert (f"served 200 bytes, deployed {len(_PAGE)}, first difference at byte 200" in verdict
            and "TRUNCATED" in verdict and "INSERTED" not in verdict), verdict


def test_an_INJECTED_script_is_named_with_its_offset_and_the_bytes_around_it(monkeypatch):
    """Explanation 1: an edge transform. The file must read as intact with a block added, and
    the block itself must be in the log, because the bytes say whose script it is."""
    at = _PAGE.index(b"</head>")
    script = b'<script src="/cdn-cgi/challenge-platform/x.js"></script>'
    verdict = _at_the_edge(monkeypatch, _PAGE[:at] + script + _PAGE[at:])
    first = at + 1      # the script and </head> share their opening "<"
    assert (f"first difference at byte {first}" in verdict
            and f"INSERTED: {len(script)} bytes added at offset {first}" in verdict
            and "challenge-platform" in verdict and "TRUNCATED" not in verdict), verdict
    # ...and the bytes BEFORE it, which say where in the page the edge put it.
    assert verdict.count("</title></head>") == 1 and "The code</title><script" in verdict, verdict


def test_every_shape_of_difference_is_reachable(monkeypatch):
    """The partition, not a leg per branch: a classifier that always said one shape would pass
    a test of that shape and read exactly like the mechanism working."""
    at = _PAGE.index(b"<p>")
    shapes = {A.where_bytes_differ(served, _PAGE).split("; ")[1].split(":")[0] for served in (
        _PAGE[:100], _PAGE[:at] + b"<script></script>" + _PAGE[at:],
        _PAGE[:at] + _PAGE[at + 10:], _PAGE.replace(b"The code", b"The c0de"))}
    assert shapes == {"TRUNCATED", "INSERTED", "REMOVED", "REPLACED"}, shapes
    assert "could not be read" in A.where_bytes_differ(b"x", None)


def _classify(monkeypatch, served, want_body, previous=None, base="BASE", live=False):
    monkeypatch.setattr(A, "fetch", lambda url, nonce: served)
    monkeypatch.setattr(A, "bytes_at", lambda ref, path: previous)
    want = hashlib.sha256(want_body).hexdigest()
    return A.classify("https://poesys.net/x/", want, "site/x/index.html", base, live)


def test_the_timeout_says_REPLACED_when_the_reader_still_has_the_overwritten_page(monkeypatch):
    """The defect this control exists for: the deploy landed and readers kept the old page.
    Naming it is what separates a real incident from an unproven one."""
    old = b"<html>YESTERDAY</html>"
    verdict = _classify(monkeypatch, served=old, want_body=b"<html>today</html>", previous=old)
    assert verdict.startswith("REPLACED"), verdict


def test_the_timeout_says_UNCONFIRMED_when_it_cannot_tell(monkeypatch):
    """'We cannot tell' is a result and belongs on the surface. Serving neither the new
    bytes nor the overwritten ones is NOT evidence the reader has stale content."""
    verdict = _classify(monkeypatch, served=b"<html>third thing</html>",
                        want_body=b"<html>today</html>", previous=b"<html>YESTERDAY</html>")
    assert verdict.startswith("UNCONFIRMED"), verdict


def test_an_unreadable_base_is_UNCONFIRMED_and_never_REPLACED(monkeypatch):
    """FAIL-OPEN in the other direction: if the overwritten bytes cannot be read, the
    control must not conclude the reader has them. `bytes_at` returning None is honest,
    and treating None as 'matches' would manufacture an incident out of a missing ref."""
    verdict = _classify(monkeypatch, served=b"<html>anything</html>",
                        want_body=b"<html>today</html>", previous=None)
    assert verdict.startswith("UNCONFIRMED"), verdict
    assert "REPLACED" not in verdict


def test_a_late_arrival_is_named_as_the_window_being_short_not_the_deploy_being_broken(monkeypatch):
    """The 2026-09-04 case: 0 of 462 confirmed observations was a directory URL, so the
    clock is the suspect and the deploy is not. Blaming the deploy hides that."""
    body = b"<html>today</html>"
    verdict = _classify(monkeypatch, served=body, want_body=body, previous=b"old")
    assert verdict.startswith("RESOLVED"), verdict


def test_a_confirmed_sibling_turns_cannot_tell_into_a_statement_about_the_reader(monkeypatch):
    """MEASURED 2026-09-04 from red run 33858118312 (head `b0bceffae`): two assets of that
    push were served NEW on the FIRST attempt -- `after 0s` -- and `/harness/` never arrived
    in 467s. One push, one deployment, one edge. New bytes cannot come from a copy stored
    before they existed, so a confirmed sibling PROVES this push is live at this edge, and a
    route not serving it is then stale rather than unproven.

    MUTATION: ignore `deployment_is_live` and this fires -- which is exactly what the code
    did for ten reds, while holding the evidence."""
    verdict = _classify(monkeypatch, served=b"<html>third thing</html>",
                        want_body=b"<html>today</html>", previous=None, live=True)
    assert verdict.startswith("STALE"), verdict


def test_the_same_bytes_stay_UNCONFIRMED_when_no_sibling_was_confirmed(monkeypatch):
    """The FAIL-CLOSED half, and the reason the pair is written together: identical served
    bytes, and only the sibling evidence differs. Without it the control cannot separate
    'the deploy has not arrived' from 'this route is stale', and must claim neither.

    A `deployment_is_live` wired to a constant True passes the test above and fails here."""
    verdict = _classify(monkeypatch, served=b"<html>third thing</html>",
                        want_body=b"<html>today</html>", previous=None, live=False)
    assert verdict.startswith("UNCONFIRMED"), verdict
    assert "STALE" not in verdict


def test_REPLACED_outranks_STALE_because_it_says_more_about_the_reader(monkeypatch):
    """PRECEDENCE, not composition. Both premises hold here -- a sibling is live AND the
    edge is serving exactly the overwritten bytes -- and the more specific verdict is the
    one worth printing: it names WHICH page the reader has, not merely that it is wrong."""
    old = b"<html>YESTERDAY</html>"
    verdict = _classify(monkeypatch, served=old, want_body=b"<html>today</html>",
                        previous=old, live=True)
    assert verdict.startswith("REPLACED"), verdict


def test_all_four_verdicts_are_reachable(monkeypatch):
    """REACHABILITY, over the whole partition rather than a leg per branch. A classifier
    that returned UNCONFIRMED unconditionally would pass every test above except this one,
    and would read exactly like the mechanism working."""
    today, old = b"<html>today</html>", b"<html>YESTERDAY</html>"
    verdicts = {
        _classify(monkeypatch, served=old, want_body=today, previous=old).split()[0],
        _classify(monkeypatch, served=b"other", want_body=today, previous=old).split()[0],
        _classify(monkeypatch, served=today, want_body=today, previous=old).split()[0],
        _classify(monkeypatch, served=b"other", want_body=today, previous=None,
                  live=True).split()[0],
    }
    assert verdicts == {"REPLACED", "UNCONFIRMED", "RESOLVED", "STALE"}, verdicts


def test_the_failure_message_carries_the_reason_not_just_the_url(monkeypatch, tmp_path, capsys):
    """The whole point: a red deploy must arrive with its cause attached. Ten reds arrived
    without one, and the cause had to be reconstructed from run logs three days later."""
    monkeypatch.setattr(A, "bytes_at", lambda ref, path: b"<html>YESTERDAY</html>")
    monkeypatch.setenv("DEPLOY_BASE_REF", "BASE")
    rc, _ = _run(monkeypatch, tmp_path,
                 {"site/index.html": b"<html>current</html>"},
                 {"https://poesys.net/": b"<html>YESTERDAY</html>"})
    assert rc == 1, "an unproven deploy must still be red"
    assert "REPLACED" in capsys.readouterr().err


def test_the_live_deployment_premise_is_DERIVED_from_a_confirmed_sibling(monkeypatch, tmp_path,
                                                                        capsys):
    """The classify tests above all HAND the premise in, so every one of them would pass with
    `deployment_is_live` wired to a constant at the call site. This is the only leg that
    exercises the derivation, and it injects the branch through `main()` on the exact shape
    that has gone red ten times: a mixed push where one route confirms and another does not.

    MUTATION: pass a literal `False` at the call site and this fires while the four verdict
    tests stay green."""
    new_a, new_b = b"<html>A-today</html>", b"<html>B-today</html>"
    rc, _ = _run(monkeypatch, tmp_path,
                 {"site/index.html": new_a, "site/x/index.html": new_b},
                 {"https://poesys.net/": new_a,                    # the sibling, live at 0s
                  "https://poesys.net/x/": b"<html>SOMETHING ELSE</html>"})
    assert rc == 1, "a route not serving this push must still be red"
    assert "STALE" in capsys.readouterr().err


def test_a_push_where_NOTHING_reached_the_edge_claims_nothing_about_the_reader(monkeypatch,
                                                                               tmp_path, capsys):
    """The partner injection, and the fail-closed direction of the derivation: same
    unconfirmed route, but no sibling ever confirmed, so the deploy itself may simply not
    have arrived. Claiming staleness here would manufacture a reader incident out of a
    deploy that never landed -- and a constant-True premise does exactly that."""
    rc, _ = _run(monkeypatch, tmp_path,
                 {"site/index.html": b"<html>A-today</html>",
                  "site/x/index.html": b"<html>B-today</html>"},
                 {"https://poesys.net/x/": b"<html>SOMETHING ELSE</html>"})
    err = capsys.readouterr().err
    assert rc == 1
    assert "STALE" not in err, err
    assert "UNCONFIRMED" in err, err


def test_the_stage_leaves_out_ONLY_the_file_pages_would_refuse(monkeypatch, tmp_path, capsys):
    """Run 38474007478: one 57.7 MiB ledger made wrangler refuse the whole upload, so every
    page stayed a week old. The stage must drop that file AND keep its siblings -- a stage
    that drops everything passes an "oversized file is absent" check too."""
    monkeypatch.setattr(A, "PROJECT", str(tmp_path))
    monkeypatch.setattr(A, "PAGES_MAX_FILE_BYTES", 10)
    (tmp_path / "site" / "state").mkdir(parents=True)
    (tmp_path / "site" / "index.html").write_bytes(b"small")
    (tmp_path / "site" / "state" / "ledger.json").write_bytes(b"x" * 11)
    (tmp_path / "site" / "state" / "edge.json").write_bytes(b"x" * 10)   # AT the limit: kept
    dest = tmp_path / "out"
    assert A.stage(str(dest)) == 0
    assert (dest / "index.html").read_bytes() == b"small"
    assert (dest / "state" / "edge.json").exists()
    assert not (dest / "state" / "ledger.json").exists()
    assert "::warning::NOT DEPLOYED -- site/state/ledger.json" in capsys.readouterr().out


def test_an_unsent_oversized_file_is_reported_and_not_waited_on(monkeypatch, tmp_path, capsys):
    """Its bytes were never uploaded, so polling for them would red every deploy for eight
    minutes on a fact already known. The small sibling is still asserted."""
    monkeypatch.setattr(A, "PAGES_MAX_FILE_BYTES", 10)
    rc, seen = _run(monkeypatch, tmp_path,
                    {"site/index.html": b"a", "site/state/ledger.json": b"x" * 11},
                    {"https://poesys.net/": b"a"})
    assert rc == 0
    out = capsys.readouterr().out
    assert "NOT DEPLOYED" in out and "https://poesys.net/state/ledger.json" in out
    assert not any(url.endswith("ledger.json") for url, _ in seen)
    assert any(url == "https://poesys.net/" for url, _ in seen)


# --------------------------------------------------------------------------
# Build-only scripts stay off the deploy (director's front-door steer, item 9, 2026-10-22).
# --------------------------------------------------------------------------
@pytest.mark.parametrize("path", [
    "site/test_home_door.py", "site/ia_register.py", "site/knowledge/review_state.py",
    "site/_live_harness.mjs", "site/harness/_render_harness.mjs",
])
def test_a_build_only_script_is_never_awaited_after_the_deploy(path):
    """It is never staged, so polling for it would red every deploy that touches a test."""
    assert A.url_for(path) is None


def test_the_real_site_stages_with_no_build_only_file_and_keeps_its_pages(tmp_path, capsys):
    """Over the real `site/`: the stage passes, ships none of the ~70 scripts, and still ships
    the front door and its scripts -- a stage that drops everything also ships no `.py`."""
    dest = tmp_path / "out"
    assert A.stage(str(dest)) == 0, capsys.readouterr().err
    # Read by suffix here, not through `A.is_build_only`: a predicate that went blind would
    # also blind a read-back made through it.
    shipped = [p for p in dest.rglob("*") if p.suffix in (".py", ".pyc")
               or (p.name.startswith("_") and p.suffix == ".mjs")]
    assert shipped == []
    assert A.shipped_build_only(str(dest)) == []
    assert (dest / "index.html").is_file()
    assert any(p.suffix == ".js" for p in dest.rglob("*.js"))
    assert "left out" in capsys.readouterr().out


def test_the_stage_FAILS_when_a_build_only_file_reaches_the_staged_tree(monkeypatch, tmp_path,
                                                                       capsys):
    """The read-back is the check, not the ignore rule: break the copy so it ignores nothing
    and the stage must refuse, naming the file."""
    monkeypatch.setattr(A, "PROJECT", str(tmp_path))
    (tmp_path / "site").mkdir()
    (tmp_path / "site" / "index.html").write_bytes(b"page")
    (tmp_path / "site" / "test_door.py").write_bytes(b"def test(): pass")
    real_copytree = A.shutil.copytree
    monkeypatch.setattr(A.shutil, "copytree",
                        lambda src, dest, ignore=None: real_copytree(src, dest))
    assert A.stage(str(tmp_path / "out")) == 1
    assert "test_door.py" in capsys.readouterr().err


def test_the_github_pages_manifest_publishes_no_script_either():
    """The steer named "the Pages manifest" too. GitHub Pages serves `docs/` by a named list,
    never `site/`; this keeps a script from being added to that list."""
    from tools import pages_publish_manifest as manifest
    assert manifest.PUBLISHED
    assert [p for p in manifest.PUBLISHED if p.endswith((".py", ".mjs"))] == []
