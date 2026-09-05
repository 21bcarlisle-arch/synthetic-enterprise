"""A derived file merged from two sides deadlocks unless the merge re-derives it.

Each test names the defect it exists to catch.

THE DEADLOCK, measured 2026-09-05. Two lanes each added one member to the same class register.
Git merged the two lists cleanly -- different lines, no conflict -- and took the printed count from
one side, so the merged tree read "printed 12, list holds 13" and the consolidation gate refused it.
There was no route through: `build_merge_tree` rule 1 refuses a resolution for a path that did not
conflict (rightly -- that rule is what stops `--merge --content` being a smuggling door), and
neither side could fix it alone, because naming the other's member requires the other's member FILE,
which arrives with the merge. Origin sat still for 88 minutes with every lane behind it.
"""
from __future__ import annotations

import subprocess
import sys

import pytest

from tools import surgical_land as sl


def _run(repo, *args, **kw):
    env = {"PATH": "/usr/bin:/bin", "HOME": str(repo),
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    done = subprocess.run(("git",) + args, cwd=str(repo), capture_output=True, text=True, env=env)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


@pytest.fixture()
def repo(tmp_path):
    """A real repo whose 'derived' file is a count over its own list, rendered by a real script."""
    r = tmp_path / "r"
    (r / "docs").mkdir(parents=True)
    (r / "background").mkdir()
    _run(tmp_path, "init", "-q", "-b", "main", str(r))
    # Written as a raw triple-quoted literal on purpose: the first draft built it by string
    # concatenation and `"\\\\d"` reached the file as `\\d`, so the renderer's regex matched a
    # literal backslash, never rewrote anything, and the test failed reporting that the tool
    # had not re-derived -- a fixture defect wearing the shape of the defect under test.
    (r / "background" / "render_count.py").write_text(r"""
import pathlib, re, sys
p = pathlib.Path('docs/COUNTED.md')
text = p.read_text()
rows = [l for l in text.splitlines() if l.startswith('- ')]
if '--check' in sys.argv:
    sys.exit(0 if int(re.search(r'count: (\d+)', text).group(1)) == len(rows) else 1)
p.write_text(re.sub(r'count: \d+', 'count: %d' % len(rows), text))
""")
    # Rows kept alphabetical and far apart, exactly as the real register's are: that is
    # WHY the two lanes' additions merge cleanly and produce no conflict to resolve.
    (r / "docs" / "COUNTED.md").write_text(
        "count: 3\n- alpha\n- mike\n- zulu\n")
    _run(r, "add", "-A")
    _run(r, "commit", "-q", "-m", "seed")
    return r


def _rederivers(monkeypatch):
    """Point the tool's renderer set at the fixture's script instead of the real repo's."""
    import background.derived_artefact_register as dar
    monkeypatch.setattr(dar, "renderers", lambda: [("background.render_count", "")])
    monkeypatch.setattr(dar, "rendered_paths", lambda: ["docs/COUNTED.md"])


def test_a_clean_merge_that_leaves_a_derived_count_inconsistent_is_RE_DERIVED(repo, monkeypatch):
    """THE DEFECT. Both sides append a row; git merges the list cleanly and the header comes from
    one side. Nothing conflicted, so nothing can be resolved -- and the tree is internally wrong."""
    _rederivers(monkeypatch)
    _run(repo, "checkout", "-q", "-b", "other")
    (repo / "docs" / "COUNTED.md").write_text(
        "count: 3\n- alpha\n- mike\n- yankee\n- zulu\n")   # inserts near the END
    _run(repo, "add", "-A")
    _run(repo, "commit", "-q", "-m", "other adds a row")
    _run(repo, "checkout", "-q", "main")
    (repo / "docs" / "COUNTED.md").write_text(
        "count: 3\n- alpha\n- bravo\n- mike\n- zulu\n")    # inserts near the START
    _run(repo, "add", "-A")
    _run(repo, "commit", "-q", "-m", "mine adds a row")

    parent = _run(repo, "rev-parse", "HEAD")
    other = _run(repo, "rev-parse", "other")
    merged = sl.build_merge_tree(repo, parent, other)          # no conflict: git merges the lists
    before = _run(repo, "show", f"{merged}:docs/COUNTED.md")
    assert "count: 3" in before and before.count("\n- ") == 5, (
        f"the fixture must reproduce the inconsistency (5 rows, header 3): {before!r}")

    checkout = repo.parent / "extract"
    checkout.mkdir()
    for rel in ("docs/COUNTED.md", "background/render_count.py"):
        (checkout / rel).parent.mkdir(parents=True, exist_ok=True)
        (checkout / rel).write_text(_run(repo, "show", f"{merged}:{rel}"))

    tree, rederived = sl.rederive_in(repo, checkout, merged)

    assert rederived == ["docs/COUNTED.md"]
    assert tree != merged, "the re-derivation must produce a NEW tree, not report success on the old"
    after = _run(repo, "show", f"{tree}:docs/COUNTED.md")
    assert "count: 5" in after, f"the count must be re-derived from the merged list: {after!r}"
    assert "bravo" in after and "yankee" in after, "neither side's row may be lost"


def test_a_consistent_tree_is_left_completely_alone(repo, monkeypatch):
    """REACHABILITY OF THE QUIET BRANCH, and the property that keeps this honest: a re-derive that
    changes nothing must return the SAME tree sha, or every ordinary landing would carry a
    gratuitous rewrite and the receipt would name paths nobody touched."""
    _rederivers(monkeypatch)
    head_tree = _run(repo, "rev-parse", "HEAD^{tree}")
    checkout = repo.parent / "clean"
    checkout.mkdir()
    for rel in ("docs/COUNTED.md", "background/render_count.py"):
        (checkout / rel).parent.mkdir(parents=True, exist_ok=True)
        (checkout / rel).write_text(_run(repo, "show", f"HEAD:{rel}"))

    tree, rederived = sl.rederive_in(repo, checkout, head_tree)

    assert rederived == []
    assert tree == head_tree


def test_a_renderer_that_EXITS_NON_ZERO_leaves_the_tree_alone(repo, monkeypatch):
    """NEVER TAKE A LANDING DOWN OVER A REPAIR. A renderer that crashes, times out or is missing
    must leave the artefact exactly as the merge left it, so the gate reds on the true state
    rather than on a half-applied repair. The opposite choice -- raising -- would convert every
    broken renderer into a tree-wide landing outage."""
    import background.derived_artefact_register as dar
    monkeypatch.setattr(dar, "renderers", lambda: [("background.no_such_module_at_all", "--write")])
    monkeypatch.setattr(dar, "rendered_paths", lambda: ["docs/COUNTED.md"])
    head_tree = _run(repo, "rev-parse", "HEAD^{tree}")
    checkout = repo.parent / "broken"
    checkout.mkdir()
    (checkout / "docs").mkdir()
    (checkout / "docs" / "COUNTED.md").write_text(_run(repo, "show", "HEAD:docs/COUNTED.md"))

    tree, rederived = sl.rederive_in(repo, checkout, head_tree)

    assert rederived == []
    assert tree == head_tree


def test_a_renderer_that_HANGS_is_stood_down_from_rather_than_taking_the_landing_with_it(
        repo, monkeypatch):
    """THE BRANCH THE SIBLING ABOVE CANNOT REACH, and mutation testing is what said so.

    A missing module makes python exit NON-ZERO; it does not raise, so narrowing the `except` to
    an unrelated error left that test green. The exception branch has one realistic trigger --
    a renderer that overruns `RENDER_TIMEOUT_S`, which for the class registers means walking a
    staging tree of a thousand documents. Driven by making the call raise `TimeoutExpired`, which
    is exactly what a hang produces.
    """
    import background.derived_artefact_register as dar
    monkeypatch.setattr(dar, "renderers", lambda: [("background.render_count", "")])
    monkeypatch.setattr(dar, "rendered_paths", lambda: ["docs/COUNTED.md"])

    # Everything that shells out is done BEFORE the patch: `subprocess.run` is global, so
    # patching it earlier makes this test's own git helper raise and the failure looks like the
    # tool's. (It did, on the first run.)
    head_tree = _run(repo, "rev-parse", "HEAD^{tree}")
    checkout = repo.parent / "hung"
    checkout.mkdir()
    (checkout / "docs").mkdir()
    (checkout / "docs" / "COUNTED.md").write_text(_run(repo, "show", "HEAD:docs/COUNTED.md"))

    def hang(*a, **kw):
        raise subprocess.TimeoutExpired(cmd="render", timeout=1)
    monkeypatch.setattr(sl.subprocess, "run", hang)

    tree, rederived = sl.rederive_in(repo, checkout, head_tree)

    assert rederived == []
    assert tree == head_tree


def test_the_receipt_names_what_was_re_derived():
    """The commit carries files THE CALLER DID NOT NAME. That is the shape this whole tool exists
    to prevent, and the only thing that makes it acceptable here is that the bytes are the repo's
    own renderer output AND the receipt says so."""
    r = sl.build_receipt("p" * 40, "t" * 40, ["docs/COUNTED.md"], 0, "1 passed",
                         rederived=["docs/COUNTED.md"])

    assert "re-derived: docs/COUNTED.md" in r


def test_the_receipt_omits_the_line_when_nothing_was_re_derived():
    """The negative leg: without it, a receipt that always claimed a re-derivation would pass the
    test above while saying nothing."""
    r = sl.build_receipt("p" * 40, "t" * 40, ["a.py"], 0, "1 passed")

    assert "re-derived:" not in r


def test_the_named_exemption_is_still_undiscoverable():
    """`EXTRA_RENDERERS` exists because `discover()` structurally cannot see `finding_classes` --
    its flag is `--render`, not `--write`, and its outputs are computed per class rather than held
    in a module-level constant. The exemption must not outlive its reason: if the module ever
    becomes discoverable it belongs in REGISTER, and carrying it in both places would render it
    twice and hide a real registration gap behind a hand-kept line.
    """
    from background import derived_artefact_register as dar

    discovered = {m for m, _ in dar.discover()}
    for module, _flag in dar.EXTRA_RENDERERS:
        assert module not in discovered, (
            f"{module} is now discoverable -- move it into REGISTER and drop the exemption"
        )


def test_every_extra_renderer_actually_exists():
    """FAIL-CLOSED on a rename. A hand-kept line naming a module that has moved would silently
    stop re-deriving, and the deadlock would return with nothing to say why."""
    from background import derived_artefact_register as dar

    for module, flag in dar.EXTRA_RENDERERS:
        done = subprocess.run([sys.executable, "-m", module, "--help"],
                              cwd=str(sl.ROOT), capture_output=True, text=True, timeout=120)
        assert done.returncode == 0, f"{module} is not runnable: {done.stderr[-300:]}"
        assert flag in done.stdout, f"{module} does not offer {flag}"
