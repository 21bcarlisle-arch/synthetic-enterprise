"""§5 (DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE 2026-07-27, RESTATED by amendment):
"everything named-and-not-done must be ENUMERABLE and CHECKABLE ... derive from PRIMARY
state, never from the tick's own enumeration" (LAW C wall).

These prove `primary_state_scan.named_but_unminted`:
  - R15 BOTH WAYS: a named-but-unminted deliverable APPEARS; minting it makes it DISAPPEAR.
  - The two coverage signals (mint-doc Source line; the ruling's own MINT COVERAGE MAP banner).
  - The §0 failure class (a deliverable named in a block, never minted) is caught.
  - LAW C INDEPENDENCE: no supervisor import; no tick/enumeration argument; a primary-source
    mutation changes the output (so it cannot be a restatement of the tick's own belief).
  - DRIFT GUARD: the local §4 parser agrees with supervisor's on fixtures (they cannot diverge
    silently — the whole point of the deliberate re-implementation).
"""
from __future__ import annotations

from pathlib import Path

import background.primary_state_scan as pss


def _ruling(dir_: Path, name: str, deliverables: list[str], *, banner: str = "") -> Path:
    dir_.mkdir(parents=True, exist_ok=True)
    block = "\n".join(f"{i}. {d}" for i, d in enumerate(deliverables, start=1))
    body = (
        (f"<!--\n{banner}\n-->\n" if banner else "")
        + f"# [DIRECTOR-RULING] — {name}\n\nbody\n\n## WORK THIS CREATES\n\n{block}\n"
    )
    p = dir_ / name
    p.write_text(body, encoding="utf-8")
    return p


def _mint(dir_: Path, slug: str, source_ruling: str, index: int) -> Path:
    dir_.mkdir(parents=True, exist_ok=True)
    p = dir_ / f"PLANNER_MINTED_{slug}.md"
    p.write_text(
        "<!-- SUPERVISOR_DRAW: self-drawable -->\n"
        f"# Mint for {slug}\n\n"
        f"Source: `{source_ruling}`, deliverable **{index}** (some description)\n",
        encoding="utf-8",
    )
    return p


def _dirs(tmp_path: Path):
    return tmp_path / "root", tmp_path / "in_progress", tmp_path / "done"


# --------------------------------------------------------------------------- #
# R15 both ways + the §0 failure class
# --------------------------------------------------------------------------- #
def test_unminted_deliverable_appears_then_disappears_when_minted(tmp_path):
    root, ip, done = _dirs(tmp_path)
    _ruling(root, "DIRECTOR_RULING_X_2026-07-27.md", ["Do the first thing", "Do the second thing"])

    # DIRECTION A — nothing minted yet: both deliverables are named-but-unminted.
    res = pss.named_but_unminted(root, ip, done)
    idx = sorted(r["index"] for r in res)
    assert idx == [1, 2], res
    assert all(r["ruling"] == "DIRECTOR_RULING_X_2026-07-27.md" for r in res)
    assert res[0]["deliverable"] == "Do the first thing"

    # DIRECTION B — mint deliverable 1 (a real mint doc, in done/): only #2 remains.
    _mint(done, "first_thing", "DIRECTOR_RULING_X_2026-07-27.md", 1)
    res = pss.named_but_unminted(root, ip, done)
    assert sorted(r["index"] for r in res) == [2], res

    # Mint the second too -> residue EMPTY = the checkable proof "no named work sits unminted".
    _mint(ip, "second_thing", "DIRECTOR_RULING_X_2026-07-27.md", 2)
    assert pss.named_but_unminted(root, ip, done) == []


def test_coverage_signal_2_banner_landed_covers_a_deliverable_with_no_mint_doc(tmp_path):
    """The landed-as-code-without-a-mint-doc case (§2 of the real WORK_DEFINITION ruling): the
    ruling's own MINT COVERAGE MAP banner marks the index LANDED -> not residue."""
    root, ip, done = _dirs(tmp_path)
    _ruling(
        root, "DIRECTOR_RULING_Y_2026-07-27.md", ["Landed in code directly", "Never touched"],
        banner="MINT COVERAGE MAP:\n  [1] first — ALREADY COVERED (LANDED abc1234)\n",
    )
    res = pss.named_but_unminted(root, ip, done)
    # #1 covered by the banner; #2 has NO mint doc and NO banner entry -> residue.
    assert sorted(r["index"] for r in res) == [2], res


def test_a_lying_free_prose_number_does_not_over_cover(tmp_path):
    """Signal-1 keys ONLY off a `Source:` line, and signal-2 ONLY off the leading comment banner —
    a bare `[1] done` in the ruling BODY (not the banner) must NOT mark #1 covered."""
    root, ip, done = _dirs(tmp_path)
    p = _ruling(root, "DIRECTOR_RULING_Z_2026-07-27.md", ["Real work"])
    p.write_text(p.read_text() + "\n\nSome prose mentioning [1] done elsewhere.\n", encoding="utf-8")
    res = pss.named_but_unminted(root, ip, done)
    assert sorted(r["index"] for r in res) == [1], res


def test_ruling_without_work_block_yields_no_residue_here(tmp_path):
    """A ruling with NO WORK THIS CREATES block is the §4 missing-block DEFECT (a separate surface),
    not a §5 named-but-unminted item — 0 deliverables to diff, so nothing lands here."""
    root, ip, done = _dirs(tmp_path)
    root.mkdir(parents=True)
    (root / "DIRECTOR_RULING_NOBLOCK_2026-07-27.md").write_text(
        "# [DIRECTOR-RULING] — no block\n\njust prose, no deliverables\n", encoding="utf-8")
    assert pss.named_but_unminted(root, ip, done) == []


def test_done_rulings_are_not_sources_but_are_coverage(tmp_path):
    """A ruling archived to done/ is discharged — its deliverables are no longer 'not done', so it
    is NOT a source. A mint archived to done/ still COUNTS as coverage."""
    root, ip, done = _dirs(tmp_path)
    _ruling(done, "DIRECTOR_RULING_ARCHIVED_2026-07-27.md", ["Discharged work"])  # in done/
    assert pss.named_but_unminted(root, ip, done) == []


# --------------------------------------------------------------------------- #
# LAW C — independence
# --------------------------------------------------------------------------- #
def test_law_c_no_supervisor_import():
    src = Path(pss.__file__).read_text(encoding="utf-8")
    offenders = [ln.strip() for ln in src.splitlines()
                 if ln.strip().startswith(("import ", "from ")) and "supervisor" in ln]
    assert not offenders, f"LAW C breach: primary_state_scan imports supervisor: {offenders}"


def test_law_c_takes_no_tick_or_enumeration_argument():
    """The derivation's signature accepts ONLY primary-state paths — it cannot be handed the tick's
    own belief, so it can never be a restatement of it (the LAW-C independence wall, structural)."""
    import inspect
    params = set(inspect.signature(pss.named_but_unminted).parameters)
    assert params == {"staging_dir", "in_progress_dir", "done_dir"}, params


def test_law_c_output_derives_from_primary_state_mutation(tmp_path):
    """A mutation of a PRIMARY source (add an unminted deliverable to a ruling's block) MUST change
    the output — proving the enumeration re-derives from disk, not from a cached tick verdict."""
    root, ip, done = _dirs(tmp_path)
    p = _ruling(root, "DIRECTOR_RULING_M_2026-07-27.md", ["only one"])
    before = pss.named_but_unminted(root, ip, done)
    assert sorted(r["index"] for r in before) == [1]
    # Mutate primary state: append a second, unminted deliverable.
    p.write_text(p.read_text().replace("1. only one", "1. only one\n2. a newly named second"),
                 encoding="utf-8")
    after = pss.named_but_unminted(root, ip, done)
    assert sorted(r["index"] for r in after) == [1, 2], after


# --------------------------------------------------------------------------- #
# DRIFT GUARD — the deliberate re-implementation must not diverge from §4's parser
# --------------------------------------------------------------------------- #
def test_local_parser_agrees_with_supervisor_parser():
    """The two parsers are kept identical by intent; this test imports BOTH (the module itself
    imports neither) and asserts they agree, so a silent drift reds here rather than in production."""
    from background.supervisor import work_this_creates_deliverables as sup
    fixtures = [
        "# [DIRECTOR-RULING] — t\n\n## WORK THIS CREATES\n\n1. alpha\n2. beta\n- gamma\n",
        "no block at all here",
        "## Work This Creates\n\n1. **bold** item\n2. `code` item\n\n## Next section\n\n3. not counted\n",
        "### WORK THIS CREATES (per §4)\n\n1. only one\n",
        "prose\n\n#### work this creates\n- a\n- b\n" + "x" * 400 + "\n",
    ]
    for f in fixtures:
        assert pss._work_this_creates_deliverables(f) == sup(f), f"parser drift on:\n{f[:80]}"


def test_real_repo_work_definition_ruling_fully_covered():
    """Exit-criterion 2 (verify this mint tick's own output): over the REAL repo, the
    WORK_DEFINITION ruling's six deliverables are all covered — residue carries none of them."""
    res = pss.named_but_unminted()  # real repo dirs
    wd = [r for r in res if "WORK_DEFINITION_AND_COHERENCE" in r["ruling"]]
    assert wd == [], f"WORK_DEFINITION deliverables unexpectedly unminted: {wd}"
