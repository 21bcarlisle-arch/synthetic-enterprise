#!/usr/bin/env python3
"""R15 proof for the STEM-keyed third of the generated-path oracle.

THE DEFECT IT NAMES (2026-09-24). The two oracles beside this one are keyed to a generated TREE and
to a whole STATIC PATH, and both assume the artefact has a name a parser can read.
`background/alarm_repetition.finding_path` composes its destination from the alarm instead --
`STAGING_DIR / f"WORKER_FINDING_REPEATING_ALARM_{_family_slug(key, message)}_{today}.md"` -- so
there is no literal to resolve and there never will be. Measured on the live shared tree that day:
ELEVEN of the THIRTEEN paths holding the checkout behind origin/main were that one family, nine of
them tracked-and-modified, and `_split_generated` called every one AUTHORED. So
`generated_output_verdicts` -- the fifth blocker class, whose whole subject is a producer's output --
never reached them, and under `advance_shared_tree`'s all-or-nothing rule those nine were fatal to
the four blockers beside them that the other classes had already proven safe. What the checkout could
not carry included `alarm_repetition.py`'s own repair: the producer's exhaust was blocking the
producer's fix.

THE BOUNDARY IS A PREFIX INSIDE A SHARED DIRECTORY, AND THAT IS WHAT MAKES IT DANGEROUS.
`docs/staging/` is also where the seat files SEAT_FINDING and PLANNER_MINTED documents by hand -- the
largest source of authored documents in this repository. The remedy a consumer applies to a GENERATED
path is REVERT. So declaring the TREE would have offered a revert on a seat's unlanded finding, which
is a worse failure than the one being fixed, and every leg below that proves a stem-matched document
IS found has a partner proving its authored neighbour is NOT.

THE THIRD FAILURE DIRECTION IS STALENESS, and it is the one a prefix has and a path does not. A
declared stem outlives the producer that justified it. When the producer goes, the documents stop
being regenerated -- and that is the exact moment reverting one stops being free -- so the stem must
go quiet with it, not keep classifying a family nobody remakes.
"""
from __future__ import annotations

from pathlib import Path

from tools import file_scope_generated_paths as fs

STEM = "WORKER_FINDING_REPEATING_ALARM_"
PRODUCER = "background/alarm_repetition.py"

#: THE SECOND DECLARED FAMILY (2026-09-24), and the legs for it are at the foot of this file.
#: `background/finding_classes._write_class_documents` rewrites every class register on every run
#: and composes the name from `CLASS_DOC_PREFIX`, so it is the alarm family's shape from the same
#: module family. What is DIFFERENT, and what its own legs are about, is that its producer can write
#: to two directories and only one of them is declared.
CLASS_STEM = "CLASS_"
CLASS_PRODUCER = "background/finding_classes.py"
CLASS_DIRECTORY = "docs/staging/reference"
CLASS_PRODUCER_LITERAL = "CLASS_DOC_PREFIX"


def _live_members() -> set[str]:
    """Whatever the family holds RIGHT NOW, which is the only honest subject for a real-tree leg.

    NO NAMED MEMBER AND NO COUNT FLOOR, and the reason is this file's own subject. An earlier draft
    pinned `..._SEAT_CLAIM_2026-09-15.md` by name and asserted `len(...) > 1`. Both are controls
    keyed to today's answer, and the answer moves by design: `alarm_repetition.reask(apply=True)`
    writes each cleared document into `done/` and then UNLINKS the staging-root copy, so an emptying
    family is the mechanism SUCCEEDING. Those legs would have gone red across every lane at exactly
    the moment the repair this oracle exists to unblock did its job -- and red on a file the
    offending commit never touched.

    An empty return is therefore a legitimate state, not a failure, and the legs below say so.
    What stops that from being fail-open is that the question "is this declaration worth anything"
    is answered WITHOUT tree state by
    `test_every_declared_stem_is_REACHED_BY_ITS_PRODUCER_in_the_real_tree`: a stem whose producer is
    gone or no longer spells it fails there whether the family is empty or not.
    """
    return fs.stem_written_artefacts()


def _producer_tree(root: Path, *, spells: str = STEM, present: bool = True) -> Path:
    """A tmp tree carrying the producer shape, copied from the real `finding_path` idiom.

    The f-string is reproduced rather than simplified to a literal, because a fixture that spelled
    the whole path would be testing the STATIC scan and passing for the wrong reason -- the property
    under test is that the tail is never read.
    """
    (root / "background").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "staging").mkdir(parents=True, exist_ok=True)
    if present:
        (root / PRODUCER).write_text(
            "from pathlib import Path\n"
            'STAGING_DIR = Path(__file__).resolve().parents[1] / "docs" / "staging"\n'
            "def finding_path(message, *, today, key):\n"
            f'    return STAGING_DIR / f"{spells}{{key}}_{{today}}.md"\n',
            encoding="utf-8")
    return root


def _doc(root: Path, relative: str) -> None:
    p = root / relative
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("# a document\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# The claim, and its partner on the authored side of the same directory
# ---------------------------------------------------------------------------
def test_MUTATION_a_document_whose_filename_the_producer_COMPOSES_is_found(tmp_path):
    """The whole defect in one fixture. No frame of the static scan can reach this destination --
    the f-string tail is a call, the value is returned rather than written, and the write is a
    second frame down -- and the document must still classify as a producer's output."""
    _producer_tree(tmp_path)
    _doc(tmp_path, f"docs/staging/{STEM}TREE_DIVERGENCE_2026-09-15.md")
    assert fs.stem_written_artefacts(tmp_path) == {
        f"docs/staging/{STEM}TREE_DIVERGENCE_2026-09-15.md"}


def test_MUTATION_an_AUTHORED_SIBLING_in_the_same_directory_is_never_reported(tmp_path):
    """The partner leg, and the more expensive failure. A seat's finding sits in the same directory
    as the producer's output and is unlanded work; classifying it generated offers the reconciler a
    REVERT on it. A stem that matched the DIRECTORY rather than the prefix passes the leg above and
    destroys a lane's work here."""
    _producer_tree(tmp_path)
    _doc(tmp_path, f"docs/staging/{STEM}SEAT_CLAIM_2026-09-15.md")
    _doc(tmp_path, "docs/staging/SEAT_FINDING_THE_HEADER_IS_STAMPED_ONCE_2026-09-24.md")
    _doc(tmp_path, "docs/staging/PLANNER_MINTED_reversibility_action_and_act_2026-07-29.md")
    found = fs.stem_written_artefacts(tmp_path)
    assert found == {f"docs/staging/{STEM}SEAT_CLAIM_2026-09-15.md"}, found


def test_MUTATION_a_member_a_ROOM_MOVE_has_taken_custody_of_is_not_reported(tmp_path):
    """NON-RECURSIVE, and this is the leg that holds it. `background/staging_rooms.py` moves a
    document into `in_progress/` or `done/` when a lane takes custody, and the copy in a room has
    been read, ranked and often annotated by whoever moved it. The producer writes to the staging
    ROOT and nowhere else, so that is the whole extent of its claim. An `rglob` here passes every
    other leg in this file and reverts a lane's annotation."""
    _producer_tree(tmp_path)
    _doc(tmp_path, f"docs/staging/{STEM}SEAT_CLAIM_2026-09-15.md")
    _doc(tmp_path, f"docs/staging/in_progress/{STEM}VALUE_ARM_WAS_CLAIMED_2026-08-25.md")
    _doc(tmp_path, f"docs/staging/done/{STEM}DELIVERY_LANE_STRANDED_2026-09-18.md")
    found = fs.stem_written_artefacts(tmp_path)
    assert found == {f"docs/staging/{STEM}SEAT_CLAIM_2026-09-15.md"}, found


def test_MUTATION_a_PREFIX_MATCH_is_not_a_SUBSTRING_match(tmp_path):
    """The stem is what the producer puts at the FRONT of the name. A document merely MENTIONING the
    family in its own filename -- which is exactly what a seat's finding about the alarm family does,
    and there are several in this tree -- is authored work."""
    _producer_tree(tmp_path)
    _doc(tmp_path, f"docs/staging/SEAT_FINDING_THE_{STEM}FAMILY_FILES_EIGHT_NAMES_2026-09-23.md")
    assert fs.stem_written_artefacts(tmp_path) == set()


def test_MUTATION_a_non_artefact_SUFFIX_is_not_reported(tmp_path):
    """`ARTEFACT_SUFFIXES` is the shared answer to "what kind of thing is a producer's output", and
    the stem half must ask it too rather than taking anything the glob returns -- an editor's swap
    file or a `.bak` beside the document is nobody's photograph of a run."""
    _producer_tree(tmp_path)
    _doc(tmp_path, f"docs/staging/{STEM}SEAT_CLAIM_2026-09-15.md.bak")
    _doc(tmp_path, f"docs/staging/{STEM}SEAT_CLAIM_2026-09-15.md.swp")
    assert fs.stem_written_artefacts(tmp_path) == set()


# ---------------------------------------------------------------------------
# Staleness: the failure direction a prefix has and a path does not
# ---------------------------------------------------------------------------
def test_MUTATION_a_stem_whose_PRODUCER_IS_GONE_classifies_nothing(tmp_path):
    """SELF-DISABLING, in the safe direction. With no producer the documents are not regenerated, so
    a revert stops being free at exactly that moment. Going quiet means the reconciler offers a
    LANDING again -- where this module started, and never destructive. Staying loud over a dead
    producer reverts something nobody remakes."""
    _producer_tree(tmp_path, present=False)
    _doc(tmp_path, f"docs/staging/{STEM}SEAT_CLAIM_2026-09-15.md")
    assert fs.stem_written_artefacts(tmp_path) == set()


def test_MUTATION_a_stem_the_producer_NO_LONGER_SPELLS_classifies_nothing(tmp_path):
    """The same failure arriving by rename rather than deletion, and the one a file-existence check
    alone would miss. The producer is present and writes documents; it just does not write THESE
    any more. Positive evidence of generation is the admission rule, so the evidence has to be
    re-read rather than remembered from the day the stem was declared."""
    _producer_tree(tmp_path, spells="WORKER_FINDING_RENAMED_ALARM_")
    _doc(tmp_path, f"docs/staging/{STEM}SEAT_CLAIM_2026-09-15.md")
    assert fs.stem_written_artefacts(tmp_path) == set()
    # ONE VARIABLE, AND IT IS THE PRODUCER'S LITERAL. The empty set above is worthless on its own --
    # a fixture that simply failed to produce a match reads identically. So the SAME tree, the SAME
    # document, with only the spelling in the producer restored, must classify. Note what this also
    # refutes: the oracle globs the DECLARED stem, so renaming the producer does not silently move
    # the family's identity to whatever it now spells; it makes the declaration quiet and the new
    # family unclassified until somebody declares it. That is the direction that cannot destroy work.
    _producer_tree(tmp_path, spells=STEM)
    assert fs.stem_written_artefacts(tmp_path) == {
        f"docs/staging/{STEM}SEAT_CLAIM_2026-09-15.md"}


def test_MUTATION_an_UNPARSEABLE_producer_is_an_absent_one(tmp_path):
    """A producer mid-edit must not make the stem louder. The evidence is read from source, so a
    file that will not parse yields no evidence -- and no evidence is the quiet direction, matching
    the deletion leg above rather than defaulting to the last known answer."""
    (tmp_path / "background").mkdir(parents=True)
    (tmp_path / PRODUCER).write_text(f'def broken(\n    "{STEM}"\n', encoding="utf-8")
    _doc(tmp_path, f"docs/staging/{STEM}SEAT_CLAIM_2026-09-15.md")
    assert fs.stem_written_artefacts(tmp_path) == set()


# ---------------------------------------------------------------------------
# The real tree: is the declaration worth anything, and does it reach its consumer
# ---------------------------------------------------------------------------
def test_every_declared_stem_is_REACHED_BY_ITS_PRODUCER_in_the_real_tree():
    """FURNITURE CONTROL. A declaration whose producer no longer spells it classifies nothing (the
    legs above), so it would sit here reading like a live rule while being inert. This is the leg
    that notices, and it is keyed to the property -- every member, not the one member declared
    today."""
    assert fs.GENERATED_STEMS, "the declaration list is empty; every leg below is vacuous"
    for producer, directory, stem in fs.GENERATED_STEMS:
        assert (fs.PROJECT_DIR / producer).is_file(), f"{producer} is gone; {stem} classifies nothing"
        assert fs._producer_spells_stem(fs.PROJECT_DIR, producer, stem), (
            f"{producer} no longer spells {stem!r}, so the declaration is inert furniture")
        assert (fs.PROJECT_DIR / directory).is_dir(), f"{directory} does not exist"


def test_the_stem_declaration_is_LOAD_BEARING_in_the_real_tree():
    """Worth something, measured rather than assumed: the stem must be the ONLY thing that reaches
    these paths. That is the claim the whole mechanism rests on -- if either neighbouring oracle
    already had them, nothing needed building -- and it is a property of every member rather than of
    a member picked on the day this was written."""
    members = _live_members()
    tree_keyed = fs.generated_artefacts()
    static_scan = fs._write_reached_paths()
    for member in sorted(members):
        assert member not in tree_keyed, (
            f"{member}: the TREE-keyed oracle already has it, so the stem is not what classifies it")
        assert member not in static_scan, (
            f"{member}: the STATIC write scan already has it, so no stem was needed")


def test_the_stem_reaches_the_UNION_its_consumer_actually_reads():
    """CONTROL THE CHAIN. `origin_reconcile` iterates a hard-coded pair of oracle NAMES, so a third
    function correct in isolation reaches no production caller and the wedge does not move. This
    asserts the fold, not the function -- over every live member, so it neither needs a family to be
    non-empty nor cares which documents are in it."""
    members = _live_members()
    union = fs.written_artefacts()
    missing = sorted(members - union)
    assert not missing, (
        "the stem half is not folded into `written_artefacts`, which is the name the reconciler "
        f"asks: {missing}")


def test_the_stem_does_NOT_reach_the_COMMIT_GATE_or_the_frozen_census():
    """BLAST RADIUS, and the reason this went in the write-keyed half. `generated_artefacts` feeds
    the fail-CLOSED `file_scope` starvation gate and the `FROZEN` debt list was measured against
    exactly that set. A stem leaking into it would refuse every lane's commit whose atom declares a
    staging path, and the freeze would be stale the moment it landed."""
    assert not (fs.stem_written_artefacts() & fs.generated_artefacts()), (
        "a stem-matched path is in the TREE-keyed oracle, so the commit gate's population moved")
    assert fs.gate_violations() == [], (
        "the starvation gate refuses a `file_scope` entry it did not refuse before the stem landed")


def test_an_AUTHORED_staging_document_in_the_real_tree_is_never_classified():
    """The live version of the authored-sibling leg, keyed to the property rather than to a fixture.
    A tmp tree proves the matcher; this proves the DECLARED stem, against the real directory the seat
    actually files into, where the neighbours are real unlanded findings."""
    staging = fs.PROJECT_DIR / "docs" / "staging"
    authored = [p for p in staging.glob("*.md") if not p.name.startswith(STEM)]
    assert authored, "no authored document in docs/staging/; this leg cannot fail"
    known = fs.written_artefacts()
    offenders = [p.name for p in authored if p.relative_to(fs.PROJECT_DIR).as_posix() in known]
    assert not offenders, f"authored staging documents classified as a producer's output: {offenders}"


def test_the_NOT_REPRODUCIBLE_carve_out_reaches_the_stem_half_too(monkeypatch):
    """The hatch must be ONE hatch. `WRITTEN_BUT_NOT_REPRODUCIBLE` asks whether a revert loses
    content no run can recompute -- a question about the artefact, not about how its path was
    spelled. Without this, the next person to find a stem-matched document that accumulates
    something irreproducible has to build a second carve-out.

    THE SUBJECT IS INJECTED RATHER THAN NAMED FROM THE LIVE FAMILY, so the leg asks about the ORDER
    of the two operations and nothing else. Pinning a real document here would have made a leg about
    set algebra fail whenever the daemon archived that document -- and the order is what can
    actually break: `(scan | stems) - carve` carves both halves, `(scan - carve) | stems` re-admits
    a stem-matched path the hatch had just excluded, and only the injected member distinguishes
    them regardless of what the tree holds today."""
    subject = f"docs/staging/{STEM}INJECTED_FOR_THE_ORDER_OF_TWO_OPERATIONS_2026-09-24.md"
    monkeypatch.setattr(fs, "stem_written_artefacts", lambda root=None: {subject})
    assert subject in fs.written_artefacts(), "the stem half is not unioned in at all"
    monkeypatch.setattr(fs, "WRITTEN_BUT_NOT_REPRODUCIBLE", frozenset({subject}))
    assert subject not in fs.written_artefacts(), (
        "the carve-out is applied before the stems are unioned in, so it cannot reach them")


# ---------------------------------------------------------------------------
# The SECOND declared family: `CLASS_` registers, whose producer writes to TWO rooms
# ---------------------------------------------------------------------------
#
# WHAT IS NEW HERE AND WHY IT NEEDS ITS OWN LEGS RATHER THAN A SECOND PARAMETRISATION.
# The alarm family's producer writes to exactly one directory, so declaring that directory claims
# precisely the producer's reach. `background/finding_classes._class_doc_path` delegates to
# `staging_rooms.class_document_path`, which returns the REFERENCE ROOM for a register that is
# there, the staging ROOT for one that is there, and the reference room for a register that is in
# neither. The producer's reach is therefore genuinely WIDER than what `GENERATED_STEMS` declares,
# and the gap is deliberate: the staging root is where the seat hand-files SEAT_FINDING and
# PLANNER_MINTED documents, and the remedy a consumer applies to a generated path is REVERT. The
# legs below hold the under-claim in place, because the obvious "fix" -- widening the declaration to
# the root so the clear is bigger -- is the one change that could destroy a lane's unlanded work.


def _class_producer_tree(root: Path, *, spells: str = CLASS_STEM, present: bool = True) -> Path:
    """A tmp tree carrying `finding_classes`' own idiom: a prefix constant spent in an f-string.

    Reproduced rather than flattened to a literal for the same reason as `_producer_tree` above --
    a fixture that spelled the whole filename would be exercising the static write-site scan and
    passing for the wrong reason. The property under test is that the composed tail is never read.
    """
    (root / "background").mkdir(parents=True, exist_ok=True)
    (root / CLASS_DIRECTORY).mkdir(parents=True, exist_ok=True)
    if present:
        (root / CLASS_PRODUCER).write_text(
            "from pathlib import Path\n"
            f'{CLASS_PRODUCER_LITERAL} = "{spells}"\n'
            "def document_name(class_id, registered):\n"
            f'    return f"{{{CLASS_PRODUCER_LITERAL}}}{{class_id.upper()}}_{{registered}}.md"\n',
            encoding="utf-8")
    return root


def test_MUTATION_a_CLASS_register_in_the_REFERENCE_ROOM_is_found(tmp_path):
    """The positive direction for the second family, in a tree whose contents are known."""
    _class_producer_tree(tmp_path)
    _doc(tmp_path, f"{CLASS_DIRECTORY}/{CLASS_STEM}CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md")
    assert fs.stem_written_artefacts(tmp_path) == {
        f"{CLASS_DIRECTORY}/{CLASS_STEM}CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md"}


def test_MUTATION_a_CLASS_register_in_the_STAGING_ROOT_is_NOT_claimed(tmp_path):
    """THE DECISION THIS FAMILY EXISTS TO PIN, and the leg that fails if someone widens the
    declaration to `docs/staging` for a bigger clear.

    `class_document_path` really does write a register to the root when one lives there, so this
    document IS the producer's output and calling it authored is, strictly, a false negative. It is
    the CHEAP false negative: the consumer offers a LANDING on an unclassified path, which is where
    the module started and is never destructive. The false positive it buys off is a REVERT offered
    on whatever else sits in that root -- and what sits there is every SEAT_FINDING the seat has not
    landed yet. Under-claim here; the asymmetry is not close.
    """
    _class_producer_tree(tmp_path)
    _doc(tmp_path, f"docs/staging/{CLASS_STEM}MEASUREMENTS_THAT_MIRROR_2026-08-12.md")
    _doc(tmp_path, "docs/staging/SEAT_FINDING_THE_HEADER_IS_STAMPED_ONCE_2026-09-24.md")
    found = fs.stem_written_artefacts(tmp_path)
    assert found == set(), f"the root is claimed, so a seat's unlanded finding is one glob away: {found}"


def test_MUTATION_the_CLASS_stem_goes_quiet_when_the_producer_STOPS_SPELLING_IT(tmp_path):
    """Staleness, one variable, and the variable is the producer's own literal.

    `CLASS_DOC_PREFIX` is spelled by EXACTLY ONE string constant in the real
    `background/finding_classes.py` -- verified by walking its AST -- so this is a live dependency
    and not a formality: change that value and the registers stop being regenerated under the old
    name, which is the moment reverting one stops being free.
    """
    _class_producer_tree(tmp_path, spells="REGISTER_")
    _doc(tmp_path, f"{CLASS_DIRECTORY}/{CLASS_STEM}NO_CALLER_AND_NEVER_RUNS_2026-08-12.md")
    assert fs.stem_written_artefacts(tmp_path) == set()
    # THE CONTROL ARM. An empty set above is worthless alone -- a fixture that simply failed to
    # match reads identically. Same tree, same document, only the producer's literal restored.
    _class_producer_tree(tmp_path, spells=CLASS_STEM)
    assert fs.stem_written_artefacts(tmp_path) == {
        f"{CLASS_DIRECTORY}/{CLASS_STEM}NO_CALLER_AND_NEVER_RUNS_2026-08-12.md"}


def test_MUTATION_the_CLASS_stem_goes_quiet_when_the_PRODUCER_IS_GONE(tmp_path):
    """The same failure arriving by deletion rather than rename. Nobody remakes these now, so the
    quiet direction -- offer a landing -- is the only one that cannot lose the bytes."""
    _class_producer_tree(tmp_path, present=False)
    _doc(tmp_path, f"{CLASS_DIRECTORY}/{CLASS_STEM}PUBLISH_GATE_AND_WEDGE_2026-08-12.md")
    assert fs.stem_written_artefacts(tmp_path) == set()


def test_the_CLASS_family_IS_CLASSIFIED_in_the_real_tree():
    """The live-tree positive direction, keyed to whatever the family holds RIGHT NOW.

    NO NAMED MEMBER AND NO COUNT, for the reason `_live_members` gives: the population moves by
    design as classes are registered and retired, and the drawn item that commissioned this stem
    asserted `eight` documents when the tree held six. A leg pinned to either number would have gone
    red on a tree doing exactly what it should.

    Vacuity is covered elsewhere rather than here:
    `test_every_declared_stem_is_REACHED_BY_ITS_PRODUCER_in_the_real_tree` already fails if this
    declaration is inert furniture, whatever the directory holds today.
    """
    directory = fs.PROJECT_DIR / CLASS_DIRECTORY
    on_disk = {p.relative_to(fs.PROJECT_DIR).as_posix()
               for p in directory.glob(f"{CLASS_STEM}*")
               if p.is_file() and p.suffix in fs.ARTEFACT_SUFFIXES}
    missing = sorted(on_disk - fs.stem_written_artefacts())
    assert not missing, f"a CLASS register the producer rewrites is still graded authored: {missing}"


def test_the_CLASS_stem_claims_NOTHING_OUTSIDE_THE_REFERENCE_ROOM_in_the_real_tree():
    """The live partner of the root leg above. Asked of the whole classified set rather than of the
    CLASS_ family, so it also catches a widening that arrived through some OTHER declaration.

    THIS LEG IS VACUOUS TODAY AND THAT IS RECORDED RATHER THAN GLOSSED. Both mutations run when the
    stem landed (2026-09-24) -- deleting the declaration, and widening its directory to
    `docs/staging` -- were caught by the tmp-tree legs and NOT by this one, because the live staging
    root holds no `CLASS_` document for it to find. So it is a standing guard against a future root
    copy, not a proof of anything now; the widening proof is
    `test_MUTATION_a_CLASS_register_in_the_STAGING_ROOT_is_NOT_claimed`, which builds the population
    it needs. Left in deliberately: `class_document_path` WILL write to the root for a register that
    lands there, so the day this stops being vacuous is the day it matters.
    """
    offenders = sorted(p for p in fs.stem_written_artefacts()
                       if Path(p).name.startswith(CLASS_STEM)
                       and not p.startswith(f"{CLASS_DIRECTORY}/"))
    assert not offenders, f"a CLASS register outside the declared room is classified: {offenders}"
