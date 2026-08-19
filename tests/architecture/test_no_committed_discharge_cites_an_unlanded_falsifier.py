"""A committed record that says DISCHARGED must name a falsifier the repository has.

THE `tests/` HALF of the class H27 Expert Hour #35 opened and deliberately left open
(`site/test_the_site_lane_runs_no_untracked_control.py` is the SITE half; the finding is
`docs/staging/done/WORKER_FINDING_THE_SITE_GATE_COUNTS_AN_UNTRACKED_CONTROL_IN_ITS_OWN_GREEN_2026-08-18.md`).

WHY THE SUBJECT IS NOT "UNTRACKED `tests/**/test_*.py`". #35 measured 10 untracked test
modules on disk and refused to make them the population: on a shared working tree with
several lanes live, untracked-at-this-instant is normal and transient, and a repo-wide
census of it would be born red on another lane's in-flight editor. That refusal was right
and it still is. The honest subject #35 named instead, and this file implements, is

    a path that a COMMITTED record cites on its `**Discharged:**` line
    and that the repository does not contain.

That is not a race. A discharge is a CLOSED CLAIM, already committed: it asserts, in a
document any clone can read, that the named falsifier exists and pins the defect. Whether
some other lane is mid-edit has no bearing on whether a claim already made is true.

WHAT THIS FOUND ON ITS FIRST RUN, and it is worse in kind than the site instance rather
than merely a second copy of it (measured 2026-08-18 against the real tree, HEAD 19b56a53e):

    tests/saas/test_clv_margin_basis.py
    tests/tools/test_derived_basis_parentage_gate.py
        <- docs/staging/done/WORKER_FINDING_THE_BOOK_IS_VALUED_ON_A_MARGIN_
           THAT_EXCLUDES_THREE_QUARTERS_OF_THE_COST_STACK_2026-08-17.md
    tests/simulation/test_the_worlds_dwelling_is_drawn_not_believed.py
        <- docs/staging/done/WORKER_FINDING_THE_WORLDS_DWELLING_FOR_A_DRAWN_
           HOME_IS_THE_COMPANYS_OWN_ESTIMATE_2026-08-17.md

All three are on disk, none is ignored, and `git log --all` on each is empty. The SITE
instance was one untracked test whose SUBJECT was committed, so the repair was a one-line
`git add`. These are not: each of the three fails to even IMPORT against HEAD, because the
repair it certifies is uncommitted too --

    tools.generate_dashboard_data.UNKNOWN_COST_BASIS          HEAD 0 / worktree 5
    tools.generate_dashboard_data._check_derived_basis_parentage  HEAD 0 / worktree 3
    saas.clv_model.CLV_MARGIN_BASIS                          HEAD 0 / worktree 3
    saas.property_model.BASIS_SAAS_APPROXIMATION             HEAD 0 / worktree 2

(measured by `git show HEAD:<file>` against the working copy, and by running all three in a
detached worktree at HEAD: 3 errors during collection, ImportError on each of those names).
So the record does not merely cite a missing test -- the whole repaired mechanism it
declares closed exists on one machine. #35's own assumption, that "cited by a committed
record" would be a subject free of the sequencing problem, is FALSE, and that is this
control's finding: the sequencing problem is not avoided by picking a better population,
it is what the population is made of.

WHY THIS IS A RATCHET AND NOT A BARE ASSERTION. The three above cannot be greened from
here. Landing them means landing another lane's uncommitted repair to `saas/clv_model.py`,
`saas/property_model.py`, `tools/generate_dashboard_data.py` and the new untracked
`simulation/dwelling_records.py` -- sweeping a live lane's work into this commit, which is
the thing the shared-tree rules forbid outright. Deleting them to go green is worse. So the
three are DECLARED below, dated, with the change set each waits on, and everything else
fails immediately. The list is checked in BOTH directions (see the stale-entry test): an
entry that stops being a violation must be deleted, so the ratchet cannot rot into a
permanent exemption.

R15, THE THREE KILLER PATTERNS, each given a mutation test below that performs the named
defect and is asserted to PASS on it:
  TAUTOLOGY   -- resolving cited paths against the FILESYSTEM (`Path.exists()`) instead of
                 the index. All three violations are on disk, so that checker is green on
                 the shipped defect. This is not hypothetical: it is the exact shape that
                 already let 77 dead evidence paths sit unnoticed across 84 atoms.
  FAIL-OPEN   -- a marker that matches nothing (population 0) with the vacuity floor
                 removed: nothing to check, so nothing fails.
  FAIL-SILENT -- `git` unavailable or exiting non-zero, swallowed into an empty set. An
                 unavailable check is a FAILED check, so both raise here.

WHY THE INDEX AND NOT `HEAD`, on both sides. At pre-commit time the honest question is
"will the commit about to be made contain this", and that is the index. A record and its
falsifier added together in one commit are legitimately present. Post-commit the index
matches HEAD and the two readings coincide.

── THE SUBJECT IS THE CITATION, NOT THE FILE (2026-08-18, rung-1c BLOCKING draw) ──

`WORKER_FINDING_THE_DISCHARGE_RELEASE_READS_THE_NODE_FROM_THE_WORKING_TREE_AND_ITS_CONTROL_
READS_ONLY_THE_FILE_2026-08-18` measured what fell between this control and the parser it
keeps honest. Each checked the half the other did not: `parse_discharge` checked the NODE
against the WORKING TREE, this file checked the FILE against the index. Nothing checked the
node against the index, so a discharge citing a long-committed test file and a node that
existed only in its author's editor was released to RECORDED by the parser and passed clean
here. Measured over every committed record: 195 node-bearing citations, 15 absent at HEAD,
5 of them file-level (this control's original subject) and **10 node-level and invisible to
everything**.

Three changes, and each closes one of the ways the pair stayed blind:
  * the citation, `<file>` or `<file>::<node>`, is the unit — a node is looked up in the
    index's copy of its file, never on disk (`_index_blob`);
  * the record is read WHOLE from the index rather than through `git grep`'s matched line,
    because a discharge is a comma-continued list and six of these citations sat on
    continuation lines the line-based read never saw (§4 of the same finding);
  * `_KNOWN_UNLANDED` may declare a citation that is WAITING TO LAND; it may not absorb one
    that is in no tree at all (`test_no_exemption_absorbs_a_citation_that_is_in_no_tree`).

WHY THE CONTINUATION PARSE IS DUPLICATED HERE rather than imported from
`background.finding_severity`: this control's whole purpose is to disagree with that parser
when the parser is wrong. Sharing the extraction would make the two agree by construction
about what the claim even is, which is the independence half of R15's TAUTOLOGY pattern —
the same reason the token filter below is not the module's `_ARTEFACT_RE`.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[2]

# The marker a finding uses to close itself. Anchored at line start: a discharge is its own
# line in this project's finding format, and an unanchored match would pull in prose that
# merely discusses discharges.
_DISCHARGE_MARKER = r"^\*\*Discharged:\*\*"

# A discharge line reads every backtick as a path unless it is filtered, and these documents
# use backticks for symbols, prose emphasis and pytest node ids as well. A token counts as a
# repo path only if it is relative, contains a separator and ends in an extension the repo
# actually stores.
_BACKTICKED = re.compile(r"`([^`]+)`")
_PATH_EXT = (
    ".py", ".mjs", ".mts", ".ts", ".js",
    ".json", ".yaml", ".yml", ".md", ".html", ".sh",
)

# Vacuity floors. Re-measured 2026-08-18 after the subject became the CITATION: 75 records
# carrying a discharge, 244 distinct citations (it was 88 when node ids were discarded). A
# broken marker, a moved root or a stricter token filter would empty the population and this
# control would then pass forever with nothing in it. Floors sit well below the measurement
# so ordinary archiving does not trip them -- they catch the mechanism breaking, not the
# corpus shrinking.
#
# THE CITATION FLOOR IS SET ABOVE 88 ON PURPOSE. That is what this population collapses to
# if the node id is ever dropped again, and a floor of 40 would have sat green through
# exactly the regression this control was just repaired for -- a floor that cannot fail on
# its own named defect is decoration (R15).
_MIN_RECORDS = 30
_MIN_CITED_PATHS = 120

# THE RATCHET. Declared violations, each with the date it was measured and the uncommitted
# change set it waits on. Adding a line here is a deliberate, reviewable act; the stale-entry
# test below deletes the incentive to leave one behind.
#
# A key is either a PATH (covering every citation of a file the index does not carry at all —
# one file, one debt) or a full `file::node` CITATION (for a file the index HAS and a node it
# does not). A path key deliberately cannot cover a node violation: that is the exact hole
# this control was blind to, and letting one line re-open it would be the ratchet absorbing
# its own subject.
_WEDGE_DRAW_REPAIR = (
    "2026-08-18, H27 rung-1c. Waits on the uncommitted wedge-draw repair "
    "(`background/publish_gate_wedge.py`); the file is committed and carries 20 nodes at "
    "HEAD, the working tree 29. Node present on disk here, in no commit."
)
_KNOWN_UNLANDED: dict[str, str] = {
    "tests/saas/test_clv_margin_basis.py": (
        "2026-08-18, H27 Hour #36. Waits on the uncommitted CLV margin-basis repair "
        "(`saas/clv_model.py::CLV_MARGIN_BASIS`, absent at HEAD). Owning lane must land "
        "the repair and this falsifier together."
    ),
    "tests/tools/test_derived_basis_parentage_gate.py": (
        "2026-08-18, H27 Hour #36. Waits on the uncommitted R14 parentage gate "
        "(`tools/generate_dashboard_data.py::_check_derived_basis_parentage` and "
        "`UNKNOWN_COST_BASIS`, both absent at HEAD)."
    ),
    **{
        f"tests/background/test_publish_gate_wedge_draw.py::{node}": _WEDGE_DRAW_REPAIR
        for node in (
            "test_superseded_clause_fires_when_every_failure_predates_head",
            "test_superseded_clause_is_silent_when_failures_are_at_head",
            "test_superseded_clause_is_silent_on_a_mixed_hash_set",
            "test_superseded_clause_is_silent_without_a_usable_hash",
            "test_superseded_clause_is_silent_when_git_cannot_answer",
            "test_in_flight_clause_fires_and_suspends_the_enumerate_instruction",
            "test_in_flight_clause_is_silent_when_no_gate_is_running",
            "test_live_gate_runs_parses_ps_and_ignores_grep_and_junk",
            "test_live_gate_runs_is_empty_when_ps_is_unavailable",
        )
    },
    # LANDED 2026-08-19 by H27 Expert Hour #39, all six entries deleted the same day. They
    # read: "Waits on the uncommitted D30 belief-axis floor repair
    # (`tools/couple_w2_11_d5.py::measure_belief_axis_null_control_floor`, absent at HEAD).
    # Node present on disk here, in no commit." The repair is now at the index (3
    # occurrences) and all six nodes with it, landed by the SYMBOL half of this class --
    # `tests/architecture/test_no_committed_store_claims_an_unlanded_symbol.py`, whose first
    # run named the same uncommitted change set from the other direction: H27's committed
    # store note credited `door_only` and `dimension_caveats` while the index carried
    # neither. One landing discharged both, so `_BELIEF_AXIS_REPAIR` went with them.
    # LANDED 2026-08-18 by KNIFE3 step 38 (register §3ag), entry deleted the same
    # day by step 39. It read: "Waits on the uncommitted KNIFE3 B12 dwelling
    # split -- `simulation/dwelling_records.py` is in no commit on any ref and
    # `saas/property_model.py::BASIS_SAAS_APPROXIMATION` is absent at HEAD."
    # Step 38 committed the split, so the falsifier and its repair are both at
    # HEAD and the exemption stopped describing a violation. This control went
    # red at HEAD the moment that landing succeeded -- which is the list working
    # as designed ("the list only ever shrinks"), not a regression: it refuses to
    # let a waiver outlive the wait. Step 39 was the next commit to run the gate
    # and so was the one that had to clear it.
}


def _git(*args: str) -> str:
    """Run git, or FAIL. R15 fail-silent: an unavailable subject is a failed check.

    Returning an empty string on error would make every cited path look untracked (loud,
    but for the wrong reason) or -- worse, depending on which side swallowed it -- make the
    comparison vacuous and green.
    """
    try:
        r = subprocess.run(
            ["git", *args], cwd=str(PROJECT),
            capture_output=True, text=True, timeout=180,
        )
    except (OSError, subprocess.SubprocessError) as exc:  # pragma: no cover - environment
        raise AssertionError(
            f"could not run `git {' '.join(args)}` ({exc!r}) -- this control's subject is "
            "unavailable, so it cannot say anything. An unavailable check is a FAILED "
            "check (R15 fail-silent), never a pass"
        ) from exc
    if r.returncode not in (0, 1):  # git grep exits 1 for "no matches", which is not an error
        raise AssertionError(
            f"`git {' '.join(args)}` exited {r.returncode}: {r.stderr.strip()!r}. An "
            "unavailable check is a FAILED check"
        )
    return r.stdout


def _paths_the_repository_has() -> set[str]:
    """Subject B: the index -- what the commit being made will carry."""
    tracked = {ln.strip() for ln in _git("ls-files").splitlines() if ln.strip()}
    assert tracked, (
        "`git ls-files` listed NOTHING. Either this is not a git work tree or the index is "
        "empty -- in both cases the comparison below would be vacuous"
    )
    return tracked


def _claim_text(record_text: str, marker: str) -> str:
    """The whole `**Discharged:**` value of one record, continuation lines included.

    A line that ends in a comma is continued by the next one — the shape a list of artefacts
    has, and the shape six of the ten node-level violations were hiding behind when this
    control read only `git grep`'s matched line.
    """
    lines = record_text.splitlines()
    pattern = re.compile(marker)
    for i, line in enumerate(lines):
        if not pattern.search(line):
            continue
        claim = [line]
        for nxt in lines[i + 1:]:
            if not claim[-1].rstrip().endswith(","):
                break
            claim.append(nxt)
        return "\n".join(claim)
    return ""


def _citations_in(text: str) -> set[str]:
    """Every backticked token in a claim that this repository would store as a path.

    The node id is KEPT (`file::name`): a discharge names a falsifier, and a falsifier is a
    node. Dropping it here is what made 10 violations unseeable.
    """
    out: set[str] = set()
    for token in _BACKTICKED.findall(text):
        token = token.strip()
        path = token.split("::")[0].strip()
        if "/" not in path or not path.endswith(_PATH_EXT):
            continue
        if path.startswith(("http", "/", "~", ".")):
            continue
        out.add(token)
    return out


def _discharge_citations(marker: str = _DISCHARGE_MARKER) -> tuple[dict[str, set[str]], int]:
    """Subject A: what committed records CLAIM. Read from the index, not the working tree.

    Returns (citation -> set of citing records, number of discharging records seen). The
    records are read from git rather than from disk on purpose: the claim's authority comes
    from being committed, and a working-tree read would both admit an uncommitted record's
    claim and miss a committed record whose working copy has been moved or archived.
    """
    listed = _git("grep", "-l", "--cached", "-e", marker, "--", "*.md")
    cited: dict[str, set[str]] = {}
    records = 0
    for record in (ln.strip() for ln in listed.splitlines()):
        if not record:
            continue
        records += 1
        for citation in _citations_in(_claim_text(_git("show", f":{record}"), marker)):
            cited.setdefault(citation, set()).add(record)
    return cited, records


def _index_defines(citation: str, have: set[str]) -> bool:
    """Does the INDEX carry this citation — the file, and the node inside the file?"""
    path, _, node = citation.partition("::")
    if path not in have:
        return False
    if not node:
        return True
    return node in _git("show", f":{path}")


def _violations(
    cited: dict[str, set[str]] | None = None,
    have: set[str] | None = None,
) -> dict[str, set[str]]:
    if cited is None:
        cited, _ = _discharge_citations()
    if have is None:
        have = _paths_the_repository_has()
    return {c: srcs for c, srcs in cited.items() if not _index_defines(c, have)}


def _exemption_key(citation: str, have: set[str]) -> str | None:
    """The `_KNOWN_UNLANDED` KEY that declares this citation, or None.

    A PATH entry covers a citation only when the index has no such file at all: one missing
    file is one debt. When the file IS in the index and only the node is missing, the debt is
    node-level and must be declared as one — a path entry that covered it would re-open
    precisely the hole this control was blind to.
    """
    if citation in _KNOWN_UNLANDED:
        return citation
    path = citation.partition("::")[0]
    if path not in have and path in _KNOWN_UNLANDED:
        return path
    return None


def _describe(citation: str, srcs: set[str]) -> str:
    path, _, node = citation.partition("::")
    on_disk = (PROJECT / path).exists()
    if node and on_disk:
        on_disk = node in (PROJECT / path).read_text(encoding="utf-8", errors="replace")
    where = "on disk here only" if on_disk else "in no tree at all"
    return f"{citation}  ({where})\n" + "".join(
        f"        cited as DISCHARGED by: {s}\n" for s in sorted(srcs)
    )


# --------------------------------------------------------------------------------------
# The population must be real before any verdict about it means anything.
# --------------------------------------------------------------------------------------

def test_the_citation_population_is_not_vacuous():
    """VACUITY GUARD. A green verdict over an empty population is not a green verdict."""
    cited, records = _discharge_citations()
    assert records >= _MIN_RECORDS, (
        f"only {records} committed records carry a `**Discharged:**` line (floor "
        f"{_MIN_RECORDS}); 75 were measured on 2026-08-18. The marker, the pathspec or the "
        "index read is what changed -- fix the mechanism, do not lower the floor"
    )
    assert len(cited) >= _MIN_CITED_PATHS, (
        f"only {len(cited)} distinct citations are made across those records (floor "
        f"{_MIN_CITED_PATHS}); 244 were measured on 2026-08-18. The token filter is what "
        "changed -- fix it, do not lower the floor"
    )


# --------------------------------------------------------------------------------------
# The tripwire.
# --------------------------------------------------------------------------------------

def test_no_committed_discharge_cites_a_falsifier_the_repository_does_not_have():
    """THE TRIPWIRE. A discharge naming a file no clone contains is a claim, not a closure.

    `tools/pre_commit_test_gate.py` and every `pytest` run collect from the WORKING TREE,
    so such a falsifier is collected, passes, and is counted in the green -- while the
    assurance the committed record advertises exists on exactly one machine.
    """
    have = _paths_the_repository_has()
    unexpected = {
        c: s for c, s in _violations(have=have).items()
        if _exemption_key(c, have) is None
    }
    assert not unexpected, (
        "a COMMITTED record says DISCHARGED and names a falsifier that is in no commit:\n"
        "    " + "    ".join(_describe(p, s) for p, s in sorted(unexpected.items()))
        + "\nRepair: land the falsifier AND the repair it certifies, in the same commit as "
        "the record that claims them. If the repair belongs to another lane and cannot be "
        "landed from here, do not delete the falsifier and do not weaken this control -- "
        "add the path to _KNOWN_UNLANDED with the date and the change set it waits on, so "
        "the debt is declared instead of invisible."
    )


def test_every_declared_exemption_is_still_a_real_violation():
    """THE RATCHET'S SECOND DIRECTION -- without this it rots into a permanent exemption.

    An entry that has been landed must be DELETED from the list. Left behind, it would
    silently re-exempt the same path if it were ever un-landed again, which is precisely how
    a ratchet stops being one.
    """
    have = _paths_the_repository_has()
    used = {
        key for key in (_exemption_key(c, have) for c in _violations(have=have))
        if key is not None
    }
    stale = sorted(set(_KNOWN_UNLANDED) - used)
    assert not stale, (
        "these paths are declared in _KNOWN_UNLANDED but are no longer violations -- they "
        "have been landed, which is the good outcome:\n  - " + "\n  - ".join(stale)
        + "\nDelete each from _KNOWN_UNLANDED. The list only ever shrinks."
    )


#: Named once so the arm-1 citation below cannot drift away from the test it names.
_THIS_TEST = "test_no_exemption_absorbs_a_citation_that_is_in_no_tree"


def _on_disk_here(citation: str) -> bool:
    """Is this citation present in THIS working tree — file, and node inside it?"""
    path, _, node = citation.partition("::")
    target = PROJECT / path
    if not target.is_file():
        return False
    if not node:
        return True
    return node in target.read_text(encoding="utf-8", errors="replace")


def test_no_exemption_absorbs_a_citation_that_is_in_no_tree():
    """THE RATCHET'S BOUND. A declared exemption says "this is written and waiting to land".
    An exemption for something that exists NOWHERE is not a wait, it is an amnesty, and it
    would let a typo'd node id be declared instead of corrected.

    TWO ARMS, and the split is forced by the same thing that forced it on the mutation test
    below: "waiting to land" is by definition a fact about an UNCOMMITTED tree, and the
    pre-commit gate runs this in an isolated worktree built from the index, where no
    uncommitted work exists. So:
      ARM 1 (structural, runs everywhere) proves the guard REFUSES such a citation.
      ARM 2 (real history) checks the live list wherever this tree can see the evidence, and
            says plainly when it cannot rather than reporting a pass it did not earn.
    """
    # ARM 1: the guard DISCRIMINATES, and both directions are asserted -- a guard that said
    # False to everything would pass the first half alone and forbid every honest exemption.
    fiction = "tests/architecture/test_nothing_defines_this.py::test_typo"
    real = f"{Path(__file__).relative_to(PROJECT).as_posix()}::{_THIS_TEST}"
    assert not _on_disk_here(fiction), (
        "the guard must REFUSE a citation no tree contains -- that is the amnesty it exists "
        "to stop"
    )
    assert _on_disk_here(real), (
        "and it must ADMIT one this tree really carries, or it forbids the declared waits "
        "the ratchet is for"
    )

    # ARM 2: every declared entry, against this tree.
    #
    # THE PRECONDITION IS `git diff`, NOT `git status`, and the difference is what refused a
    # first draft of this test at the gate. `surgical_land` materialises the tree the commit
    # WOULD create and reads its index from the parent, so its checkout has untracked
    # leftovers (which `status` reports) but no tracked file that differs from its index. In
    # that tree "written and waiting to land" cannot exist by construction, so the question
    # has no answer there and a verdict would be invented rather than measured.
    if not _git("diff", "--name-only").strip():
        pytest.skip(
            "this tree's tracked files all match its index (a clean clone, or the gate's "
            "materialised would-be tree), so 'written and waiting to land' is unobservable "
            "here -- arm 1 is the proof, and it ran"
        )
    nowhere = sorted(key for key in _KNOWN_UNLANDED if not _on_disk_here(key))
    assert not nowhere, (
        "these _KNOWN_UNLANDED entries name something that is in NO tree -- not the index, "
        "and not this working tree either:\n  - " + "\n  - ".join(nowhere)
        + "\nAn exemption is a declared WAIT, not an amnesty. If the citation is a typo, fix "
        "the record that made it; if the work truly exists elsewhere, it is not this tree's "
        "to declare."
    )


def test_every_exemption_is_dated_and_names_what_it_waits_on():
    """Shape, checkable in every tree: an undated exemption cannot be reviewed, and one that
    does not name its change set cannot be discharged by anyone but its author."""
    bad = sorted(
        key for key, why in _KNOWN_UNLANDED.items()
        if not re.match(r"^\d{4}-\d{2}-\d{2},", why) or "`" not in why
    )
    assert not bad, (
        "every _KNOWN_UNLANDED entry must start `YYYY-MM-DD,` and name the change set it "
        "waits on in backticks:\n  - " + "\n  - ".join(bad)
    )


# --------------------------------------------------------------------------------------
# R15 -- each mutation performs a named defect and is asserted to PASS on it, which is what
# makes the control above evidence rather than decoration.
# --------------------------------------------------------------------------------------


def test_MUTATION_taking_the_file_as_the_subject_goes_blind_to_the_node():
    """WRONG-SUBJECT, and it is this control's own shipped defect (2026-08-18).

    The file-level checker is green on a citation whose file is committed and whose NODE is
    not -- 10 live citations were in exactly that state when this was written.
    """
    have = _paths_the_repository_has()
    tracked_file = next(iter(sorted(p for p in have if p.startswith("tests/"))))
    citation = f"{tracked_file}::test_a_node_no_file_defines_ffffff"
    cited = {citation: {"docs/staging/done/EXAMPLE.md"}}

    control_sees = _violations(cited=cited, have=have)
    mutant_sees = {c for c in cited if c.partition("::")[0] not in have}

    assert control_sees, "the node-level control must see a node the index's copy lacks"
    assert not mutant_sees, (
        "the file-level mutant was expected to be BLIND to it -- if it is not, this control "
        "is not distinguishable from the one that passed clean on 10 live violations"
    )


def test_MUTATION_reading_only_the_matched_line_loses_continuation_citations():
    """The multi-line half (§4). A discharge is a comma-continued list, and `git grep`'s
    matched line is one line of it -- six of the ten violations were on continuation lines.
    """
    record = (
        "**Discharged:** `tests/a/test_one.py::test_x`,\n"
        "`tests/a/test_two.py::test_y`\n"
        "— a reason.\n"
    )
    whole = _citations_in(_claim_text(record, _DISCHARGE_MARKER))
    first_line_only = _citations_in(record.splitlines()[0])
    assert len(whole) == 2, whole
    assert first_line_only == {"tests/a/test_one.py::test_x"}, (
        "the line-based mutant was expected to MISS the continuation citation"
    )

def test_MUTATION_resolving_citations_against_the_filesystem_goes_blind():
    """TAUTOLOGY/wrong-subject: `Path.exists()` instead of the index passes on the defect.

    The shipped defect is 'the repository does not have it', not 'nobody has it'. A checker
    that asks the local filesystem is answering a question the defect never fails.

    TWO ARMS, and the split is not cosmetic -- the pre-commit gate taught it. The gate builds
    the tree this commit WOULD create in an isolated worktree, where the three declared
    violations are absent from disk (they are untracked, so a clean tree does not have them).
    A first draft of this test asserted "at least one live violation is present on this
    machine" as a precondition and was REFUSED there: a control about machine-local state
    that itself depended on machine-local state. The structural arm below runs everywhere and
    is the actual proof; the real-history arm runs additionally wherever the defect is
    physically present, and says so when it is not.
    """
    # ARM 1, structural and deterministic: the two subjects disagree exactly where the defect
    # lives -- a path the filesystem has and the index does not.
    cited = {"tests/example_falsifier.py": {"docs/staging/done/EXAMPLE.md"}}
    filesystem_has = {"tests/example_falsifier.py"}
    index_has: set[str] = set()

    control_sees = _violations(cited=cited, have=index_has)
    mutant_sees = {p for p in cited if p not in filesystem_has}

    assert control_sees, "the control must see a cited path the index does not carry"
    assert not mutant_sees, (
        "the filesystem-resolving mutant was expected to be BLIND to it -- if it is not, the "
        "control above is not distinguishable from the checker this project already knows "
        "fails (77 dead evidence paths across 84 atoms went unnoticed behind exactly it)"
    )

    # ARM 2, the same claim against real history wherever the tree actually carries it.
    real = _violations()
    on_disk = {c for c in real if _on_disk_here(c)}
    if not on_disk:
        pytest.skip(
            "no live violation is present on disk here (expected in a clean tree or the "
            "gate's isolated worktree) -- arm 1 above is the proof, and it ran"
        )
    mutant_on_real = {c for c in _discharge_citations()[0] if not _on_disk_here(c)}
    assert not (on_disk & mutant_on_real), (
        "the filesystem-resolving mutant was expected to be BLIND to the on-disk violations "
        f"{sorted(on_disk)} and it saw some of them"
    )


def test_MUTATION_a_marker_that_matches_nothing_passes_without_the_vacuity_floor():
    """FAIL-OPEN: an empty population has no violations in it.

    The floor in `test_the_citation_population_is_not_vacuous` is the only thing standing
    between a broken marker and a permanent green.
    """
    cited, records = _discharge_citations(marker=r"^\*\*Dischargd:\*\*")  # typo'd on purpose
    assert records == 0 and not cited, "precondition: the mutated marker must match nothing"
    assert not _violations(cited=cited), (
        "the empty-population mutant was expected to PASS -- that is the fail-open this "
        "control's vacuity floor exists to close"
    )
    with pytest.raises(AssertionError):
        assert records >= _MIN_RECORDS, "the floor fires on the mutant"


def test_MUTATION_git_unavailable_fails_rather_than_passing_quietly(monkeypatch):
    """FAIL-SILENT: an unavailable subject must FAIL, never be read as 'nothing wrong'."""
    def _boom(*_a, **_k):
        raise OSError("git not on PATH")

    monkeypatch.setattr(subprocess, "run", _boom)
    with pytest.raises(AssertionError, match="unavailable check is a FAILED check"):
        _paths_the_repository_has()


def test_MUTATION_a_non_zero_git_exit_fails_rather_than_passing_quietly(monkeypatch):
    """FAIL-SILENT, second door: git present but refusing (not a work tree, corrupt index)."""
    class _Res:
        returncode = 128
        stdout = ""
        stderr = "fatal: not a git repository"

    monkeypatch.setattr(subprocess, "run", lambda *_a, **_k: _Res())
    with pytest.raises(AssertionError, match="unavailable check is a FAILED check"):
        _paths_the_repository_has()


def test_MUTATION_an_empty_index_listing_is_not_read_as_a_clean_repository(monkeypatch):
    """FAIL-SILENT, third door: git succeeds and says nothing.

    An empty tracked set would make EVERY cited path a violation, not zero -- but the
    diagnosis would be wrong and the message useless, so it is refused at the source.
    """
    class _Res:
        returncode = 0
        stdout = "\n  \n"
        stderr = ""

    monkeypatch.setattr(subprocess, "run", lambda *_a, **_k: _Res())
    with pytest.raises(AssertionError, match="listed NOTHING"):
        _paths_the_repository_has()
