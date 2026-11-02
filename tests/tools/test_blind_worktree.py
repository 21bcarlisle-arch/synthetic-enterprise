"""The cold reader's tree holds no code, no tests and no run results, and the check can say so.

Defect each test names: a blind tree that a reader can argue from the code in. The control over
the partition comes first — a check that refuses everything would pass every refusal test.
"""
import pytest

from tools import blind_worktree as bw


def _book(tmp_path):
    book = tmp_path / "fresh-run-out-abc"
    book.mkdir()
    (book / "DONE.json").write_text("{}")
    (book / "p2b__all_records.pkl.gz").write_bytes(b"x")
    (book / "arm.json").write_text("{}")
    return book


def _site(tmp_path):
    site = tmp_path / "built" / "site"
    for rel in bw.COLD_READER_SITE:
        p = site / rel
        if p.suffix:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("x")
        else:
            (p / "SYN-2016-001.json").parent.mkdir(parents=True, exist_ok=True)
            (p / "SYN-2016-001.json").write_text("{}")
    # What a built site carries beside the pages, none of which the reader may have.
    (site / "explore" / "test_explore_cast_door.py").write_text("")
    (site / "explore" / "__pycache__").mkdir()
    (site / "data" / "customers" / "_render.mjs").write_text("")
    (site.parent / "company").mkdir()
    (site.parent / "company" / "billing.py").write_text("")
    return site


def _made(tmp_path):
    book, site = _book(tmp_path), _site(tmp_path)
    brief = tmp_path / "brief.md"
    brief.write_text("read the pages")
    ruling = tmp_path / "ruling.md"
    ruling.write_text("the ruling")
    dest = tmp_path / "blind"
    bw.make_cold_reader(book, site, brief, dest, ruling)
    return book, dest


def test_a_made_tree_is_clean_and_every_forbidden_shape_can_be_refused(tmp_path):
    """Both sides of the partition: the made tree passes, and each forbidden shape fails it."""
    book, dest = _made(tmp_path)
    assert bw.check(dest, book) == []
    assert (dest / "RULING.md").exists() and (dest / "BRIEF.md").exists()
    assert (dest / "site" / "data" / "explore_cast.json").exists()
    assert (dest / "site" / "data" / "customers" / "SYN-2016-001.json").exists()

    plants = [f"{d}/x.txt" for d in ("company", "saas", "sim", "simulation", "tools", "tests")]
    plants += ["site/data/tests/nested.json", ".git/HEAD", "site/a.py", "site/b.pyc",
               "site/c.pkl.gz", "DONE.json", "run_output_latest.json", "site/arm.json",
               "site/__pycache__/cached.txt"]
    before = set(dest.rglob("*"))
    for rel in plants:
        p = dest / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x")
        assert bw.check(dest, book), f"planting {rel} was not refused"
        for q in sorted(set(dest.rglob("*")) - before, reverse=True):
            q.unlink() if q.is_file() else q.rmdir()
        assert bw.check(dest, book) == [], f"removing {rel} did not clear the check"


def test_a_symlink_out_of_the_tree_is_refused(tmp_path):
    book, dest = _made(tmp_path)
    (dest / "code").symlink_to(bw.ROOT / "company")
    assert any("symlink" in leak for leak in bw.check(dest, book))


def test_the_made_tree_never_carries_the_sites_tests_or_harness(tmp_path):
    book, dest = _made(tmp_path)
    names = {p.name for p in dest.rglob("*")}
    assert not names & {"test_explore_cast_door.py", "__pycache__", "_render.mjs", "billing.py"}


def test_an_unfinished_book_and_an_existing_tree_are_refused_by_name(tmp_path):
    book, dest = _made(tmp_path)
    with pytest.raises(SystemExit, match="exists"):
        bw.make_cold_reader(book, tmp_path / "built" / "site", dest / "BRIEF.md", dest,
                            dest / "RULING.md")
    (book / "DONE.json").unlink()
    with pytest.raises(SystemExit, match="not a finished book"):
        bw.make_cold_reader(book, tmp_path / "built" / "site", dest / "BRIEF.md",
                            tmp_path / "other", dest / "RULING.md")


def test_the_cli_check_exits_nonzero_on_a_leak(tmp_path, capsys):
    book, dest = _made(tmp_path)
    assert bw.main(["--check", str(dest)]) == 0
    (dest / "tools").mkdir()
    (dest / "tools" / "x.json").write_text("{}")
    assert bw.main(["--check", str(dest)]) == 1
    assert "tools/x.json" in capsys.readouterr().out


def test_the_manifest_names_the_book_and_the_ruling_and_holds_no_path(tmp_path):
    """Defect: MANIFEST.json carrying absolute paths hands the reader the repository root."""
    book, site = _book(tmp_path), _site(tmp_path)
    brief = tmp_path / "brief.md"
    brief.write_text("read the pages")
    dest = tmp_path / "blind"
    manifest = bw.make_cold_reader(book, site, brief, dest)  # the ruling defaults to ROOT's
    text = (dest / "MANIFEST.json").read_text()
    assert manifest["book"] == book.name and manifest["ruling"].startswith("DIRECTOR_RULING_")
    assert str(bw.ROOT) not in text and str(tmp_path) not in text and "/" not in text


def test_only_the_types_the_pages_read_are_copied(tmp_path):
    """Defect: a deny-list copy lets a build script or an unlisted result format in."""
    site = _site(tmp_path)
    customers = site / "data" / "customers"
    strays = ["build.sh", "_render.js", "x.ipynb", "x.pyi", "x.parquet", "x.npz", "a.py",
              "b.pyc", "README"]
    for name in strays:
        (customers / name).write_text("")
    (customers / "__pycache__").mkdir()
    (customers / "__pycache__" / "c.json").write_text("{}")
    book, brief = _book(tmp_path), tmp_path / "brief.md"
    brief.write_text("read the pages")
    dest = tmp_path / "blind"
    bw.make_cold_reader(book, site, brief, dest, brief)
    names = {p.name for p in dest.rglob("*")}
    assert "SYN-2016-001.json" in names and not names & (set(strays) | {"__pycache__"})
    for name in ("build.sh", "x.parquet", "README"):
        (dest / "site" / name).write_text("")
        assert any(name in leak for leak in bw.check(dest, book)), f"{name} was not refused"
        (dest / "site" / name).unlink()
    assert bw.check(dest, book) == []


def test_a_symlink_in_the_source_site_is_refused_not_followed(tmp_path):
    """Defect: copying through a symlink brings in what it points at as an ordinary file."""
    site = _site(tmp_path)
    (site / "data" / "customers" / "x.json").symlink_to(site.parent / "company" / "billing.py")
    book, brief = _book(tmp_path), tmp_path / "brief.md"
    brief.write_text("read the pages")
    with pytest.raises(SystemExit, match="symlink"):
        bw.make_cold_reader(book, site, brief, tmp_path / "blind", brief)
    assert not (tmp_path / "blind").exists()


def test_the_check_is_case_insensitive(tmp_path):
    """Defect: `Company/`, `Tests/` and `DONE.JSON` pass a case-sensitive check."""
    book, dest = _made(tmp_path)
    for rel in ("Company/x.json", "site/Tests/x.json", "Done.JSON", "site/__PyCache__/x.json",
                "site/RUN_OUTPUT.json", "site/ARM.JSON"):
        p = dest / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("{}")
        assert bw.check(dest, book), f"planting {rel} was not refused"
        p.unlink()
        if p.parent != dest and p.parent.name != "site":
            p.parent.rmdir()
    assert bw.check(dest, book) == []


def test_the_book_is_read_to_any_depth_for_its_names(tmp_path):
    """Defect: reading only the book's top level lets a nested run result in by name."""
    book, dest = _made(tmp_path)
    (book / "digests").mkdir()
    (book / "digests" / "period_ledger.json").write_text("{}")
    (dest / "site" / "period_ledger.json").write_text("{}")
    assert any("named like a file of the book" in leak for leak in bw.check(dest, book))
