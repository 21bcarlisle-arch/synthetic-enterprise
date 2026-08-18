"""A committed atom STORE that credits a falsifier must name one the repository has.

THE `docs/design/simplifications/` HALF of the class. The other two halves are

    tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py  (markdown)
    site/test_the_site_lane_runs_no_untracked_control.py                           (SITE)

and the finding that opened this one is
`docs/staging/WORKER_FINDING_THE_DISCHARGE_CONTROL_READS_MARKDOWN_ONLY_SO_THE_REGISTER_LEVELS_ARE_ARGUED_IN_IS_INVISIBLE_2026-08-18.md`.

WHY A THIRD HALF EXISTS. The markdown control's population is one marker:

    _DISCHARGE_MARKER = r"^\\*\\*Discharged:\\*\\*"

Measured over the real corpus on 2026-08-18, that marker appears in **0** of the 353 committed
atom stores, while those stores cite **281** distinct `tests/**.py` paths across **200** files.
The register in which levels are argued, passes are recorded and promotions are justified was
invisible to the control built for exactly this defect. The markdown control is not wrong; its
subject is one of the three places a closure is claimed, and it is the one place the atom Hours
do not use.

WHY THE POPULATION IS NOT "EVERY `tests/**.py` A STORE MENTIONS", and this is the whole design.
Run that naive widening and it returns 10 stores citing a path the index does not carry. NINE OF
THE TEN ARE HONEST. Measured this tick, clause by clause:

    tests/**/test_*.py                        H27   a GLOB, not a path
    tests/background/test_x.py                H28   an EXAMPLE, quoted: pytest "receives target
                                                    paths RELATIVE to cwd=ROOT"
    tests/controls/test_meta_control_mutation.py
                                              H18   a FUTURE deliverable: "L1->L2 DoD specified:
                                                    a new tests/controls/..."
    tests/background/test_tournament_harness.py
                                              B11   an ABSENCE, asserted: "still absent --
                                                    confirmed"
    tests/saas/test_collateral_death_loop.py  B6    an ABSENCE: "this atom declares ... and
                                                    NEITHER EXISTS"
    tests/background/test_run_marker_sweep.py OPS   an off-main RESCUE inventory: "exists nowhere
                                                    else ... NEITHER IS MERGED AND THAT IS
                                                    DELIBERATE"
    tests/saas/test_clv_margin_basis.py       EP1   "are UNTRACKED (`??`)"
    tests/tools/test_derived_basis_parentage_gate.py
                                              EP1   the same clause
    (both again)                              H27   quoted as the markdown half's declared debt:
                                                    "Three violations, all on disk, ... `git log
                                                    --all` empty on each"

A store register is DISCOVER/FRAME-heavy: naming a file that does not exist yet is what design
work IS. A control keyed on mere mention is born ~90% red, and a control born red is a control
someone disables. So the subject here is narrower and it is the one that matters:

    a clause in a COMMITTED store that credits a falsifier WITHOUT locating it
    outside the index, naming a path or node the index does not carry.

THE BURDEN OF PROOF SITS THE RIGHT WAY ROUND. Silence is a claim. The record must SAY the artefact
is untracked / absent / owed / still to be written; if it says nothing about where the artefact
lives, it is asserting the artefact is there. That direction is chosen deliberately, because the
finding's §4 measured the failure mode and it is one-directional: three independent records agreed
about Hour #37 and all three were wrong the same way. Recording is cheap and landing is not, so
records over-claim; no record has ever been found understating what landed.

THE LEXICON IS NOT THE CONTROL — `_DECLARED_HONEST_ABSENCE` IS. A disclaim vocabulary is a
fail-open shape by nature: widen it far enough and it silences everything (R15). So it is not
trusted to make the verdict. Every mention it silences whose FILE the index does not carry must
appear, by name, in the enumeration below. A new absent-file mention that the lexicon happens to
cover therefore does NOT go quiet — it fails until someone declares it and says why it is honest.
The lexicon only keeps the noise down; the list is what cannot fail open.

WHAT IT FOUND ON ITS FIRST RUN, 2026-08-18, HEAD e844ee864: exactly one affirmative claim of a
path in no commit --

    D36_bill_render_footing_and_pence
        "Fixed at the lifecycle instead: _retire_departed_artefacts() plus the R10 class guard
         tests/tools/test_no_orphan_published_customer_artefacts.py."

    `_retire_departed_artefacts` IS at HEAD (tools/generate_customer_data.py, 2 occurrences). The
    R10 class guard the same sentence credits was on disk for five days, 8,433 bytes, `git log
    --all` empty, 6 tests green. The repair landed and the control that keeps it honest did not.
    Landed in this control's own commit rather than ratcheted: it waits on nothing, and a ratchet
    entry that names no wait is the dishonest shape the markdown half's stale-entry test exists to
    delete.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[2]

STORE_DIR = "docs/design/simplifications/"

# A store path token. The trailing node id is KEPT (`file::name`) for the same reason the markdown
# half keeps it: a falsifier is a node, and dropping it made 10 violations unseeable there.
_TOKEN = re.compile(r"(?<![\w/.-])tests/[A-Za-z0-9_./-]*\.py(?:::[A-Za-z0-9_\[\]-]+)?")

# Not a path: a glob, a placeholder, or the illustrative stand-in name. `test_x.py` is listed
# because H28 uses it as prose ("pytest receives target paths RELATIVE to cwd=ROOT") and a
# stand-in name is not a citation in any lane.
_NOT_A_PATH = re.compile(r"[*?<>]|/test_x\.py(?:::|$)")

# THE DISCLAIM LEXICON. Three ways a clause locates an artefact somewhere other than the index:
#   (a) OUTSIDE IT -- untracked, uncommitted, on an unmerged branch, absent, in no commit;
#   (b) IN THE FUTURE -- a new one, a DoD, something that must/will/would be written;
#   (c) AS A KNOWN DEBT -- named as a violation, owed, ratcheted, still open.
# Searched in the CLAUSE ONLY, never the note. A store note is a single multi-kilobyte YAML
# scalar; a whole-note window would find "absent" somewhere in almost all of them and silence the
# population wholesale. The clause is the smallest unit that still carries the sentence's subject.
_DISCLAIMS = re.compile(
    r"\b("
    # (a) located outside the index
    r"untracked|uncommitted|unmerged|un-?landed|absent|absence|missing|"
    r"does not exist|do not exist|neither exists?|never exist(?:s|ed)?|"
    r"no commit|not (?:yet )?(?:committed|merged|landed|written)|nowhere else|"
    r"off-?main|rescued?|working tree|on disk|git log --all|"
    # (b) located in the future
    r"a new |to be written|will be|would be|must be|should be|"
    r"dod|specified|planned|proposed|for build|not written here|"
    # (c) named as a debt
    r"violations?|owed|ratchet|still open|residual"
    r")\b",
    re.I,
)

# A store note is one YAML scalar; `.` and `;` end a clause, and a literal `\n` inside a
# double-quoted scalar is a wrap, not a boundary.
#
# `:` IS DELIBERATELY NOT A BOUNDARY. This project's notes put the finding on the left of the
# colon and the artefacts on the right -- "Three violations, all on disk, `git log --all` empty on
# each (28 passed): `tests/saas/test_clv_margin_basis.py` and ...". Splitting there severs every
# disclaimer from the paths it disclaims, and H27's honest debt report reads as a bare credit.
_CLAUSE_SPLIT = re.compile(r"(?<=[.;])\s+")

# A literal `\n` that falls INSIDE a path is a wrap, and rejoining it is the difference between a
# real tracked citation and a broken one the index appears not to carry (OPS2's build_note wraps
# `test_publish_gate_subject_\nis_head.py` mid-token). Anchored on a path prefix so ordinary
# wrapped prose -- "has\nnever been timed" -- is not glued into a new word the lexicon cannot read.
_WRAPPED_PATH = re.compile(r"(?<=tests/)([A-Za-z0-9_./-]*)\\n(?=[A-Za-z0-9_./-])")

# Vacuity floors, measured 2026-08-18 over 353 committed stores: 200 stores carry a `tests/**.py`
# mention, 281 distinct tokens. A broken tokeniser, a moved store root or an index read that
# silently empties would make this control pass forever over nothing. Floors sit below the
# measurement so ordinary churn does not trip them -- they catch the MECHANISM breaking.
#
# THE CLAIM FLOOR IS SEPARATE FROM THE MENTION FLOOR ON PURPOSE. If the lexicon ever widens to
# swallow the corpus, mentions stay high while affirmative claims collapse -- and that is the
# fail-open this control is most exposed to, so it gets its own floor rather than being covered
# by the mention count.
_MIN_STORES = 80
_MIN_MENTIONS = 150
_MIN_CLAIMS = 90

# THE RATCHET. Affirmative claims of a citation the index does not carry, each dated and naming
# the uncommitted change set it waits on. Empty is the correct steady state: the one NEVER-LANDED
# violation this control found on its first run waited on nothing and was landed instead of
# declared.
_KNOWN_UNLANDED: dict[str, str] = {}

# THE OTHER SHAPE, and it is not the same defect. A store note is a DATED LOG: an entry can have
# been exactly true when written and be describing a node that a later commit deliberately renamed
# or retired. That is a broken citation -- a reader cannot follow it -- but it is not the
# over-claim this control's verdict is about, and being born red on it would make the control the
# thing someone disables.
#
# THE DISCIPLINE IS STRICTER THAN THE RATCHET'S, NOT LOOSER: an entry must name the COMMIT that
# retired the node, and `test_every_stale_citation_names_a_commit_that_really_retired_it` resolves
# that SHA and re-checks the absence. "It was renamed at some point" is not an excuse anyone can
# check; "it was renamed at 7d01fffba" is. This is the lesson the no-route control learned the
# expensive way -- a control that red-lists deliberate retirements gets switched off.
_STALE_CITATION: dict[str, str] = {
    "tests/tools/test_couple_fabric.py::test_the_LAST_RED_CELL_closed_by_the_BAND_being_conditioned_not_moved": (
        "2026-08-18. W1_12's dated entry narrates this control going red when the cold-appliance "
        "coupling moved D7 from 0.1804 to 0.1782 -- true when written. The next commit, "
        "6828f999f ('W1_12: land the cold-appliance coupling the map already claimed, and un-pin "
        "the control it broke'), deliberately UN-PINNED it. The narration is honest history; the "
        "node is intentionally gone."
    ),
    "tests/tools/test_couple_supply_start.py::test_the_metering_observable_is_present_and_the_derivation_ignores_it": (
        "2026-08-18. C15's entry says the contradiction 'is PINNED so it cannot quietly persist' "
        "by this node. Commit 7d01fffba ('C15: floor derive_supply_start at the account's own "
        "first observable') FIXED the derivation and renamed the pin to "
        "`test_the_metering_observable_is_present_and_the_derivation_honours_it`, which the index "
        "carries. The pin still exists; only the name in the log entry is stale."
    ),
}

# THE ENUMERATION. Every mention the lexicon silences whose FILE the index does not carry, with
# the reason it is honest. This is the control the lexicon cannot fail open past: a mention that
# is absent and silenced and NOT listed here fails `test_no_silenced_absence_is_undeclared`.
#
# Keys are `<atom store stem>::<token>`. Deleting an entry when the file lands is the same
# shrink-only discipline the markdown half's stale-entry test enforces.
_DECLARED_HONEST_ABSENCE: dict[str, str] = {
    "B11_evolutionary_tournament_harness::tests/background/test_tournament_harness.py": (
        "2026-08-18. FRAME re-verification asserting the file's ABSENCE -- 'background/"
        "tournament_harness.py and tests/background/test_tournament_harness.py still absent -- "
        "confirmed'. B11 is epoch-4 gated; the note is reporting what BUILD must produce."
    ),
    "B6_collateral_cash_death_loop::tests/saas/test_collateral_death_loop.py": (
        "2026-08-18. A FRAME open-question (Q5) reporting the atom's own file_scope is wrong: "
        "'this atom declares saas/treasury and tests/saas/test_collateral_death_loop.py and "
        "NEITHER EXISTS'. The record is correcting itself, not claiming a build."
    ),
    "H18_harness_self_mutation_audit::tests/controls/test_meta_control_mutation.py": (
        "2026-08-18. A future deliverable in an L1->L2 Definition of Done -- 'a new tests/"
        "controls/test_meta_control_mutation.py with both-directions (fire AND quiet) "
        "assertions per organ'. Doc-only FRAME turn, level held at 0."
    ),
    "OPS_run_marker_sweep_livelock::tests/background/test_run_marker_sweep.py": (
        "2026-08-18. An inventory of two rival implementations preserved as RESCUE commits on "
        "their own branches -- 'a NEW 423-line tests/background/test_run_marker_sweep.py that "
        "exists nowhere else ... NEITHER IS MERGED AND THAT IS DELIBERATE'. The record states "
        "the non-landing as the decision."
    ),
    "EP1_clv_three_horizon::tests/saas/test_clv_margin_basis.py": (
        "2026-08-18. A DISCOVER re-measurement at HEAD reporting the files are 'UNTRACKED "
        "(`??`)' and that 'EVERY LEG STILL HOLDS and none of it has landed'. Waits on the "
        "B_commercial lane's CLV margin-basis repair; declared in the markdown half's ratchet."
    ),
    "EP1_clv_three_horizon::tests/tools/test_derived_basis_parentage_gate.py": (
        "2026-08-18. The same EP1 clause and the same repair."
    ),
    "H27_payment_belief_gap::tests/saas/test_clv_margin_basis.py": (
        "2026-08-18. Hour #36 QUOTING its own declared ratchet -- 'Three violations, all on "
        "disk, none ignored, `git log --all` empty on each'. A record correctly reporting a "
        "known debt is the opposite of an over-claim."
    ),
    "H27_payment_belief_gap::tests/tools/test_derived_basis_parentage_gate.py": (
        "2026-08-18. The same Hour #36 clause."
    ),
}


def _git(*args: str) -> str:
    """Run git, or FAIL. R15 fail-silent: an unavailable subject is a failed check."""
    try:
        r = subprocess.run(
            ["git", *args], cwd=str(PROJECT),
            capture_output=True, text=True, timeout=180,
        )
    except (OSError, subprocess.SubprocessError) as exc:  # pragma: no cover - environment
        raise AssertionError(
            f"could not run `git {' '.join(args)}` ({exc!r}) -- this control's subject is "
            "unavailable, so it cannot say anything. An unavailable check is a FAILED check "
            "(R15 fail-silent), never a pass"
        ) from exc
    if r.returncode not in (0, 1):
        raise AssertionError(
            f"`git {' '.join(args)}` exited {r.returncode}: {r.stderr.strip()!r}. An "
            "unavailable check is a FAILED check"
        )
    return r.stdout


def _index() -> set[str]:
    """Subject B: the index -- what the commit being made will carry."""
    tracked = {ln.strip() for ln in _git("ls-files").splitlines() if ln.strip()}
    assert tracked, (
        "`git ls-files` listed NOTHING. Either this is not a git work tree or the index is "
        "empty -- in both cases every comparison below would be vacuous"
    )
    return tracked


def _stores(have: set[str]) -> list[str]:
    return sorted(p for p in have if p.startswith(STORE_DIR) and p.endswith(".yaml"))


def _clauses(store_text: str) -> list[str]:
    """One store's prose, unwrapped, split into clauses.

    The literal two-character `\\n` inside a double-quoted YAML scalar is a WRAP: it can fall in
    the middle of a path (`test_publish_gate_subject_\\nis_head.py` is one real token in OPS2) and
    joining it back is what keeps a real citation from being read as a broken one.
    """
    joined = _WRAPPED_PATH.sub(r"\1", store_text)
    flat = joined.replace("\\n", " ").replace("\n", " ")
    return [c for c in _CLAUSE_SPLIT.split(flat) if c.strip()]


def _tokens_in(clause: str) -> set[str]:
    return {
        t for t in _TOKEN.findall(clause)
        if not _NOT_A_PATH.search(t)
    }


def _read() -> tuple[dict[str, set[str]], dict[str, set[str]], int]:
    """(affirmative claims, silenced mentions, store count), read from the INDEX not from disk.

    A claim's authority comes from being committed. Reading the working tree would admit an
    uncommitted note's claim and miss a committed note whose working copy has been edited -- the
    precise confusion this class is about.
    """
    have = _index()
    claims: dict[str, set[str]] = {}
    silenced: dict[str, set[str]] = {}
    stores = _stores(have)
    for store in stores:
        stem = store[len(STORE_DIR):-len(".yaml")]
        for clause in _clauses(_git("show", f":{store}")):
            disclaimed = _DISCLAIMS.search(clause) is not None
            for token in _tokens_in(clause):
                (silenced if disclaimed else claims).setdefault(token, set()).add(stem)
    return claims, silenced, len(stores)


def _index_defines(citation: str, have: set[str]) -> bool:
    """Does the INDEX carry this citation -- the file, and the node inside the file?"""
    path, _, node = citation.partition("::")
    if path not in have:
        return False
    if not node:
        return True
    return node in _git("show", f":{path}")


def _violations(claims: dict[str, set[str]], have: set[str]) -> dict[str, set[str]]:
    return {c: s for c, s in claims.items() if not _index_defines(c, have)}


def _describe(citation: str, stems: set[str]) -> str:
    path, _, node = citation.partition("::")
    on_disk = (PROJECT / path).exists()
    if node and on_disk:
        on_disk = node in (PROJECT / path).read_text(encoding="utf-8", errors="replace")
    where = "on disk here only" if on_disk else "in no tree at all"
    return f"{citation}  ({where})\n" + "".join(
        f"        credited as BUILT by: {STORE_DIR}{s}.yaml\n" for s in sorted(stems)
    )


# --------------------------------------------------------------------------------------
# The population must be real before any verdict about it means anything.
# --------------------------------------------------------------------------------------

def test_the_store_population_is_not_vacuous():
    """VACUITY GUARD. A green verdict over an empty population is not a green verdict."""
    claims, silenced, stores = _read()
    mentions = set(claims) | set(silenced)
    assert stores >= _MIN_STORES, (
        f"only {stores} committed atom stores under {STORE_DIR} (floor {_MIN_STORES}); 353 were "
        "measured on 2026-08-18. The store root or the index read is what changed -- fix the "
        "mechanism, do not lower the floor"
    )
    assert len(mentions) >= _MIN_MENTIONS, (
        f"only {len(mentions)} distinct `tests/**.py` tokens across the stores (floor "
        f"{_MIN_MENTIONS}); 281 were measured on 2026-08-18. The tokeniser or the unwrap is what "
        "changed"
    )
    assert len(claims) >= _MIN_CLAIMS, (
        f"only {len(claims)} of {len(mentions)} mentions survive the disclaim lexicon as "
        f"affirmative claims (floor {_MIN_CLAIMS}); 205 were measured on 2026-08-18. THIS IS THE "
        "FAIL-OPEN FLOOR: a lexicon that widened until it silenced the corpus would leave the "
        "mention count untouched and empty this one. Narrow the lexicon, do not lower the floor"
    )


# --------------------------------------------------------------------------------------
# The verdict.
# --------------------------------------------------------------------------------------

def test_no_committed_store_credits_a_falsifier_the_repository_does_not_have():
    claims, _, _ = _read()
    have = _index()
    violations = _violations(claims, have)
    declared = set(_KNOWN_UNLANDED) | set(_STALE_CITATION)
    undeclared = {c: s for c, s in violations.items() if c not in declared}
    assert not undeclared, (
        "A COMMITTED atom store credits a falsifier the index does not carry. The store note is "
        "the register in which levels are argued and passes are recorded, so this is a level "
        "resting on a control that is in no commit:\n\n"
        + "".join(f"    {_describe(c, s)}" for c, s in sorted(undeclared.items()))
        + "\n    Land the falsifier with the repair it certifies, or -- if it genuinely waits on "
        "an uncommitted change set -- declare it in _KNOWN_UNLANDED with the date and the wait."
    )


def test_every_declared_exemption_is_still_a_real_violation():
    """Both registers only ever shrink. A waiver that outlives its subject is a lie in the file."""
    claims, _, _ = _read()
    have = _index()
    violations = _violations(claims, have)
    stale = sorted((set(_KNOWN_UNLANDED) | set(_STALE_CITATION)) - set(violations))
    assert not stale, (
        "An exemption declares a violation that no longer exists -- the falsifier landed, or the "
        "claim was rewritten. DELETE the entry:\n"
        + "".join(f"    {c}\n" for c in stale)
    )


def test_no_citation_is_declared_in_both_registers():
    """The two registers mean opposite things: 'not built yet' and 'deliberately retired'. A
    citation in both is a disposition nobody made."""
    both = sorted(set(_KNOWN_UNLANDED) & set(_STALE_CITATION))
    assert not both, (
        "declared as BOTH awaiting a landing and already retired:\n"
        + "".join(f"    {c}\n" for c in both)
    )


def test_every_stale_citation_names_a_commit_that_really_retired_it():
    """THE DISCIPLINE THAT MAKES THE SECOND REGISTER CHECKABLE.

    'It was renamed at some point' excuses anything. This resolves the named commit and re-checks
    that the node is genuinely absent from the index, so an entry cannot excuse a citation that
    was simply never written.
    """
    have = _index()
    for citation, reason in sorted(_STALE_CITATION.items()):
        assert re.search(r"\b20\d\d-\d\d-\d\d\b", reason), (
            f"_STALE_CITATION[{citation!r}] carries no measurement date"
        )
        shas = re.findall(r"\b([0-9a-f]{7,40})\b", reason)
        assert shas, (
            f"_STALE_CITATION[{citation!r}] names no commit. A retirement nobody can look up is "
            "indistinguishable from a citation that was never true -- name the SHA that did it"
        )
        for sha in shas:
            kind = _git("cat-file", "-t", sha).strip()
            assert kind == "commit", (
                f"_STALE_CITATION[{citation!r}] names {sha!r}, which this repository resolves to "
                f"{kind or 'nothing'} rather than a commit"
            )
        assert not _index_defines(citation, have), (
            f"_STALE_CITATION[{citation!r}] excuses a citation the index DOES carry -- the entry "
            "is describing nothing. DELETE it"
        )


def test_every_exemption_is_dated_and_names_what_it_waits_on():
    for citation, reason in sorted(_KNOWN_UNLANDED.items()):
        assert re.search(r"\b20\d\d-\d\d-\d\d\b", reason), (
            f"_KNOWN_UNLANDED[{citation!r}] carries no measurement date -- an undated waiver "
            "cannot be told from a permanent one"
        )
        assert re.search(r"\bwaits? on\b", reason, re.I), (
            f"_KNOWN_UNLANDED[{citation!r}] does not name what it waits on. An entry that waits "
            "on nothing is not a ratchet entry; land the falsifier instead"
        )


# --------------------------------------------------------------------------------------
# The lexicon cannot fail open past this.
# --------------------------------------------------------------------------------------

def test_no_silenced_absence_is_undeclared():
    """THE CONTROL ON THE CONTROL.

    A disclaim lexicon is a fail-open shape (R15): widen it and the verdict above empties
    quietly. So nothing absent may be silenced anonymously. Every mention the lexicon covers
    whose FILE the index does not carry must be declared by name with the reason it is honest.
    """
    _, silenced, _ = _read()
    have = _index()
    undeclared = sorted(
        f"{stem}::{token}"
        for token, stems in silenced.items()
        if token.partition("::")[0] not in have
        for stem in stems
        if f"{stem}::{token}" not in _DECLARED_HONEST_ABSENCE
    )
    assert not undeclared, (
        "The disclaim lexicon silenced a mention of a path the index does not carry, and nothing "
        "declares why that is honest. Either the clause really does locate the artefact outside "
        "the index -- then add it to _DECLARED_HONEST_ABSENCE with the quote -- or the lexicon "
        "has widened onto a real claim and must be narrowed:\n"
        + "".join(f"    {k}\n" for k in undeclared)
    )


def test_every_declared_honest_absence_is_still_absent_and_still_silenced():
    """Shrink-only, both ways: a declaration whose file landed, or whose clause stopped
    disclaiming, has stopped describing anything and must go."""
    _, silenced, _ = _read()
    have = _index()
    live = {
        f"{stem}::{token}"
        for token, stems in silenced.items()
        if token.partition("::")[0] not in have
        for stem in stems
    }
    stale = sorted(set(_DECLARED_HONEST_ABSENCE) - live)
    assert not stale, (
        "_DECLARED_HONEST_ABSENCE declares a mention that is no longer both absent and silenced "
        "-- the file landed, or the note was rewritten. DELETE the entry:\n"
        + "".join(f"    {k}\n" for k in stale)
    )


def test_every_honest_absence_declaration_is_dated_and_quotes_the_clause():
    for key, reason in sorted(_DECLARED_HONEST_ABSENCE.items()):
        assert re.search(r"\b20\d\d-\d\d-\d\d\b", reason), (
            f"_DECLARED_HONEST_ABSENCE[{key!r}] carries no measurement date"
        )
        assert "'" in reason or "the same" in reason.lower(), (
            f"_DECLARED_HONEST_ABSENCE[{key!r}] quotes nothing from the clause it excuses. The "
            "quote is what lets a reader check the excuse without re-deriving it"
        )


# --------------------------------------------------------------------------------------
# R15 mutation tests. Each names the defect it must fire on.
# --------------------------------------------------------------------------------------

def test_MUTATION_a_bare_credit_with_no_disclaimer_is_a_violation():
    """THE DEFECT: D36's shape -- a note crediting a guard, saying nothing about where it lives."""
    have = _index() | {"docs/design/simplifications/FAKE.yaml"}
    clause = (
        "Fixed at the lifecycle instead: _retire_departed_artefacts() plus the R10 class guard "
        "tests/tools/test_never_written_at_all.py."
    )
    assert not _DISCLAIMS.search(clause), (
        "the lexicon covers a bare credit -- it has widened onto exactly the claim shape this "
        "control exists to catch"
    )
    tokens = _tokens_in(clause)
    assert tokens == {"tests/tools/test_never_written_at_all.py"}
    assert _violations({t: {"FAKE"} for t in tokens}, have), (
        "a bare credit of a path in no tree produced NO violation -- the verdict cannot fire on "
        "its own named defect"
    )


def test_MUTATION_an_absence_report_is_not_a_violation():
    """THE OPPOSITE DEFECT: born red on the nine honest records, so the control gets disabled."""
    for clause in (
        "background/tournament_harness.py and tests/background/test_tournament_harness.py still "
        "absent -- confirmed",
        "this atom declares saas/treasury and tests/saas/test_collateral_death_loop.py and "
        "NEITHER EXISTS",
        "L1->L2 DoD specified: a new tests/controls/test_meta_control_mutation.py with "
        "both-directions assertions per organ",
        "a NEW 423-line tests/background/test_run_marker_sweep.py that exists nowhere else",
        "tests/saas/test_clv_margin_basis.py is UNTRACKED (`??`)",
        "Three violations, all on disk, none ignored, `git log --all` empty on each: "
        "tests/tools/test_derived_basis_parentage_gate.py",
    ):
        assert _DISCLAIMS.search(clause), (
            f"the lexicon does NOT cover an honest absence report, so this control would be born "
            f"red on a record that is telling the truth: {clause!r}"
        )


def test_MUTATION_a_whole_note_window_would_silence_the_real_violation():
    """THE WINDOW IS LOAD-BEARING. Widening it from the clause to the note is the cheap-looking
    change that empties this control, and it is measured here rather than asserted."""
    have = _index()
    store = f"{STORE_DIR}D36_bill_render_footing_and_pence.yaml"
    if store not in have:  # pragma: no cover - the atom would have to be deleted
        pytest.skip("D36 store not in the index")
    text = _git("show", f":{store}")
    assert _DISCLAIMS.search(text.replace("\\n", " ")), (
        "the D36 note as a WHOLE contains no disclaim vocabulary, so this mutation proves "
        "nothing -- pick a note that does"
    )
    landed = "tests/tools/test_no_orphan_published_customer_artefacts.py"
    assert landed in text, "D36 no longer credits the guard; this mutation needs a new subject"
    # Clause-level, the crediting clause is affirmative; note-level, the note disclaims elsewhere.
    crediting = [c for c in _clauses(text) if landed in c and not _DISCLAIMS.search(c)]
    assert crediting, (
        "no affirmative crediting clause survives in D36 -- if the note was rewritten, re-point "
        "this mutation; the claim being tested is that a note-wide window is strictly weaker"
    )


def test_MUTATION_dropping_the_node_id_goes_blind_to_a_node_level_claim():
    have = _index()
    tracked_test = next(
        (p for p in sorted(have) if p.startswith("tests/") and p.endswith(".py")), None
    )
    assert tracked_test, "no tracked test module -- the index read is broken"
    citation = f"{tracked_test}::test_a_node_that_does_not_exist_anywhere"
    assert _tokens_in(f"proven by `{citation}`") == {citation}, (
        "the tokeniser dropped the node id -- a falsifier is a NODE, and a file-level subject "
        "cannot see a claim about a node the file does not define"
    )
    assert not _index_defines(citation, have), (
        "a node no file defines was reported as present in the index"
    )


def test_MUTATION_a_glob_is_not_read_as_a_path():
    assert not _tokens_in("Ten untracked `tests/**/test_*.py` were on disk"), (
        "a glob was read as a citation -- H27's `tests/**/test_*.py` would be a permanent false "
        "positive and this control would be born red on prose"
    )


def test_MUTATION_a_wrapped_path_is_rejoined_before_matching():
    """OPS2's evidence list wraps mid-token inside a double-quoted YAML scalar."""
    wrapped = (
        'build_note: "the instrument is pinned by '
        'tests/background/test_publish_gate_subject_\\nis_head.py at HEAD"'
    )
    tokens = set().union(*(_tokens_in(c) for c in _clauses(wrapped)))
    assert tokens == {"tests/background/test_publish_gate_subject_is_head.py"}, (
        "the wrap was not rejoined, so a real tracked citation reads as a broken path the index "
        "does not carry -- a false positive manufactured by the reader"
    )
    # The join must not run past the path and glue ordinary wrapped prose into a new word the
    # disclaim lexicon can no longer read.
    prose = _clauses('build_note: "`in_tree_baseline` has\\nnever been timed"')
    assert "has never been timed" in " ".join(prose), (
        "the wrap join reached beyond a path and welded two prose words together"
    )


def test_MUTATION_git_unavailable_fails_rather_than_passing_quietly(monkeypatch):
    def boom(*a, **k):
        raise OSError("git is gone")
    monkeypatch.setattr(subprocess, "run", boom)
    with pytest.raises(AssertionError, match="unavailable"):
        _index()


def test_MUTATION_a_non_zero_git_exit_fails_rather_than_passing_quietly(monkeypatch):
    class R:
        returncode = 128
        stdout = ""
        stderr = "fatal: not a git repository"
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: R())
    with pytest.raises(AssertionError, match="FAILED check"):
        _index()


def test_MUTATION_an_empty_index_listing_is_not_read_as_a_clean_repository(monkeypatch):
    class R:
        returncode = 0
        stdout = ""
        stderr = ""
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: R())
    with pytest.raises(AssertionError, match="listed NOTHING"):
        _index()
