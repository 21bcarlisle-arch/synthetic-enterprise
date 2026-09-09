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
    own belief, so it can never be a restatement of it (the LAW-C independence wall, structural).

    KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. This asserted the literal set
    {staging_dir, in_progress_dir, done_dir} until 2026-09-09, when `map_files` was added so
    signal 1 could check a cited atom against the map. The maturity map is primary state — LAW C's
    own text names it — so that addition is exactly what this wall permits, and the literal-set
    form went red for a change that made the module MORE independent, not less. That is the
    backwards direction CLAUDE.md warns about. The property is: every parameter is path-typed and
    defaults to None, so nothing that is not a primary-state location can be injected at all."""
    import inspect
    sig = inspect.signature(pss.named_but_unminted)
    assert sig.parameters, "the derivation must still be redirectable at fixture primary state"
    for name, prm in sig.parameters.items():
        assert "Path" in str(prm.annotation), f"{name} is not path-typed: {prm.annotation}"
        assert prm.default is None, f"{name} carries a non-None default: {prm.default!r}"
        assert not any(w in name for w in ("tick", "enum", "status", "verdict", "belief")), name


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
        # THE SHAPE THIS GUARD WAS BLIND TO (added 2026-09-07). Every fixture above heads the
        # block with the bare phrase, so the guard stayed green through the two days when the
        # supervisor carried the numbered-heading repair and this module's mirror did not.
        # The director numbers his sections; both staged rulings on 2026-09-06/07 used this
        # shape, and the mirror returned [] for both while the supervisor returned 4 and 5.
        "# [DIRECTOR-RULING] — t\n\n## 5. WORK THIS CREATES\n\n- alpha\n- beta\n",
        "## 2.1 WORK THIS CREATES\n\n1. alpha\n",
        "## 3) WORK THIS CREATES (canonical)\n\n1. alpha\n2. beta\n",
    ]
    for f in fixtures:
        assert pss._work_this_creates_deliverables(f) == sup(f), f"parser drift on:\n{f[:80]}"


def test_the_director_doc_vocabulary_agrees_with_the_supervisors():
    """The drift above happened TWICE in one module — the heading parser, and the vocabulary that
    decides which docs are a mint source at all. Both were widened in `supervisor` and left narrow
    here, and the sibling drift guard could not see the second one because it only feeds the two
    parsers text, never asks which FILENAMES and HEADERS each side admits.

    MUTATION that must red this: drop `"DIRECTOR_CANON_"` (or `CANON` in the header regex) from
    this module's constants. Keyed to the PROPERTY — the two vocabularies are equal — not to
    today's four members, so admitting a fifth doc class in `supervisor` alone reds here."""
    from background import supervisor as sup

    assert set(pss._RULING_STEER_PREFIXES) == set(sup._DIRECTOR_DOC_PREFIXES)
    assert pss._RULING_STEER_HEADER_RE.pattern == sup._DIRECTOR_RULING_STEER_HEADER_RE.pattern
    # And the property that matters at the seam: the two predicates agree on real doc shapes.
    for name, head in [
        ("DIRECTOR_CANON_X_2026-09-07.md", "# [DIRECTOR-CANON] — a canon\n"),
        ("SEAT_FINDING_X.md", "# [DIRECTOR-CANON] — header only, no prefix\n"),
        ("DIRECTOR_RULING_X.md", "# [DIRECTOR-RULING] — r\n"),
        ("SEAT_RESULT_X.md", "# a plain result, neither\n"),
    ]:
        assert pss._is_ruling_or_steer(name, head) == sup._is_ruling_or_steer(name, head), name


def test_a_numbered_heading_ruling_reaches_the_residue(tmp_path):
    """The DEFECT this names, at the level that matters: not "the parsers agree" but "LAW C's
    independent read can SEE a numbered ruling's unminted work at all". With the mirror's regex
    missing its section-number group, `named_but_unminted` returned [] for a ruling naming two
    unminted deliverables — the §0 failure class, silent, in the one source built to catch it.

    MUTATION that must red this: drop `(?:\\d+(?:\\.\\d+)*[.)]?\\s+)?` from the module's
    `_WORK_THIS_CREATES_RE`. The sibling drift guard above is necessary but not sufficient —
    it proves the two parsers match, never that the residue is non-empty."""
    root, ip, done = _dirs(tmp_path)
    root.mkdir(parents=True, exist_ok=True)
    (root / "DIRECTOR_RULING_NUMBERED_2026-09-07.md").write_text(
        "# [DIRECTOR-RULING] — numbered sections\n\n## 5. WORK THIS CREATES\n\n"
        "- the first named deliverable\n- the second named deliverable\n",
        encoding="utf-8",
    )
    res = pss.named_but_unminted(root, ip, done)
    assert sorted(r["index"] for r in res) == [1, 2], res


def test_real_repo_work_definition_ruling_fully_covered():
    """Exit-criterion 2 (verify this mint tick's own output): over the REAL repo, the
    WORK_DEFINITION ruling's six deliverables are all covered — residue carries none of them."""
    res = pss.named_but_unminted()  # real repo dirs
    wd = [r for r in res if "WORK_DEFINITION_AND_COHERENCE" in r["ruling"]]
    assert wd == [], f"WORK_DEFINITION deliverables unexpectedly unminted: {wd}"


# --------------------------------------------------------------------------- #
# THE REFERENT, NOT THE CLAIM — signal 1 used to believe a mint doc's sentence
# about itself. Defect: PLANNER_MINTED_..._seven_eighths_minted_2026-09-07 wrote
# "deliverable 1 — MINTED here as `A50`" and, three paragraphs later, "Did not:
# write A50/A51 into docs/design/maturity_map.yaml". Both were true. LAW C's
# independent read — the source built to CONTRADICT a false claim — reported the
# ruling's deliverables 1 and 4 covered for two days on the strength of the first
# sentence, while the ruling re-drew in every tick's doorbell.
# --------------------------------------------------------------------------- #
def _map(dir_: Path, *atom_ids: str) -> tuple[Path, ...]:
    """A three-file maturity map carrying exactly these atom ids. Returns the map_files tuple."""
    dir_.mkdir(parents=True, exist_ok=True)
    live = dir_ / "maturity_map.yaml"
    live.write_text(
        "".join(f"- id: {a}\n  lane: X\n  level_current: 0\n" for a in atom_ids), encoding="utf-8")
    closed = dir_ / "maturity_map_closed.yaml"
    closed.write_text("", encoding="utf-8")
    retired = dir_ / "maturity_map_retired.yaml"
    retired.write_text("", encoding="utf-8")
    return (live, closed, retired)


def _mint_citing(dir_: Path, slug: str, source_ruling: str, index: int, cited: str) -> Path:
    dir_.mkdir(parents=True, exist_ok=True)
    p = dir_ / f"PLANNER_MINTED_{slug}.md"
    p.write_text(
        "<!-- SUPERVISOR_DRAW: self-drawable -->\n"
        f"# Mint for {slug}\n\n"
        f"- Source: `{source_ruling}`, deliverable {index} — MINTED here as `{cited}`\n",
        encoding="utf-8",
    )
    return p


def test_a_mint_doc_citing_an_atom_that_is_on_no_map_covers_nothing(tmp_path):
    """THE DEFECT ITSELF. The mint doc's Source line is well-formed and names the right ruling and
    the right deliverable index — and the atom it rests on was never written to the map. The
    deliverable is NOT done, so it must stay in the residue."""
    root, ip, done = _dirs(tmp_path)
    _ruling(root, "DIRECTOR_RULING_R_2026-09-06.md", ["publish the register"])
    _mint_citing(done, "claims_a50", "DIRECTOR_RULING_R_2026-09-06.md", 1, "A50")
    residue = pss.named_but_unminted(root, ip, done, map_files=_map(tmp_path / "map", "Z9_other"))
    assert [r["index"] for r in residue] == [1], residue


def test_the_same_mint_doc_covers_once_the_atom_reaches_the_map(tmp_path):
    """R15 THE OTHER WAY, and the leg that makes the one above a control rather than a refusal:
    nothing about the DOCUMENT changes — only the map gains the row — and the deliverable clears.
    Without this leg a check that refused every citation would pass the test above."""
    root, ip, done = _dirs(tmp_path)
    _ruling(root, "DIRECTOR_RULING_R_2026-09-06.md", ["publish the register"])
    _mint_citing(done, "claims_a50", "DIRECTOR_RULING_R_2026-09-06.md", 1, "A50")
    minted_map = _map(tmp_path / "map2", "A50_the_register_is_published_with_a_status_per_item")
    assert pss.named_but_unminted(root, ip, done, map_files=minted_map) == []


def test_a_short_citation_resolves_the_full_slug_and_a_near_miss_does_not(tmp_path):
    """Docs cite `G14`; the map stores `G14_half_hourly_...`. The prefix rule is what makes the
    check usable — and it must not degenerate into a substring match, or `A5` would resolve `A50`
    and every two-character citation would cover something."""
    root, ip, done = _dirs(tmp_path)
    _ruling(root, "DIRECTOR_RULING_R_2026-09-06.md", ["one", "two"])
    _mint_citing(done, "short", "DIRECTOR_RULING_R_2026-09-06.md", 1, "G14")
    _mint_citing(done, "near", "DIRECTOR_RULING_R_2026-09-06.md", 2, "G1")
    m = _map(tmp_path / "map3", "G14_half_hourly_grid_carbon_intensity_aligned_to_settlement")
    residue = pss.named_but_unminted(root, ip, done, map_files=m)
    assert [r["index"] for r in residue] == [2], residue


def test_a_coverage_line_naming_no_atom_is_untouched(tmp_path):
    """THE STATED LIMIT, held by a control so it cannot be quietly tightened. 18 of the 28 live
    coverage lines name no atom at all — the older one-mint-doc-per-deliverable form, where the
    DOC is the mint record. Requiring an id on every line would fabricate residue for 18 correct
    mints, which is the opposite failure. This test reds if someone closes that hole blind."""
    root, ip, done = _dirs(tmp_path)
    _ruling(root, "DIRECTOR_RULING_R_2026-09-06.md", ["one"])
    _mint(done, "no_atom_named", "DIRECTOR_RULING_R_2026-09-06.md", 1)
    assert pss.named_but_unminted(root, ip, done, map_files=_map(tmp_path / "map4")) == []


def test_an_unreadable_map_accepts_the_claim_rather_than_fabricating_residue(tmp_path):
    """FAIL-SAFE DIRECTION, matching this module's declared positive-detection contract: it may
    fail to ADD work it cannot substantiate, never invent work that is not on disk. No map file
    readable => 'cannot check' => the citation is accepted exactly as it was before this change.
    Distinct from an EMPTY map, which is a readable statement that the atom is absent."""
    root, ip, done = _dirs(tmp_path)
    _ruling(root, "DIRECTOR_RULING_R_2026-09-06.md", ["one"])
    _mint_citing(done, "claims_a50", "DIRECTOR_RULING_R_2026-09-06.md", 1, "A50")
    assert pss._map_atom_prefixes(tmp_path / "nothing_here.yaml") is None
    assert pss.named_but_unminted(root, ip, done, map_files=(tmp_path / "nothing_here.yaml",)) == []
    # ...and the empty-but-readable map is the opposite verdict, on the same input.
    empty = _map(tmp_path / "map5")
    assert pss._map_atom_prefixes(*empty) == set()
    assert [r["index"] for r in pss.named_but_unminted(root, ip, done, map_files=empty)] == [1]


def test_the_two_atoms_the_defect_lost_are_on_the_real_map_now():
    """Keyed to the PROPERTY (the ruling's two uncovered deliverables have map rows), not to the
    residue count, which moves whenever any ruling is filed. Reds if A50/A51 are ever swept out
    of the map again — which is exactly how they were lost the first time."""
    from tools import maturity_map_store as store
    ids = {a["id"] for a in store.load_atoms()}
    for want in ("A50_the_supplier_use_case_register_is_published_with_a_status_per_item",
                 "A51_the_plain_english_report_on_the_use_case_register_reaches_the_director"):
        assert want in ids, f"{want} is not on the maturity map"
