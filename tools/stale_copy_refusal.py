"""A commit whose copy of a file PREDATES the last landing to that file is refused, by path.

THE DEFECT THIS OWNS, and it is a class with three BLOCKING findings already banked
(`A_REWRITE_DELETED_THE_BINDING_REPAIR`,
`TWO_LANES_EACH_BUILT_R1S_UNBIASED_MAGNITUDE_ESTIMATOR_AND_A_PATHSPEC_LAND_DELETES_NINE_OF_HEADS_SYMBOLS`,
`TWO_LANES_BUILT_W1_14S_ARTEFACT_CUT_TWICE`). `CLAUDE.md` tells every lane to commit by pathspec,
never `-A`, and that is right -- but it protects only against OTHER FILES. **A pathspec stages the
WORKING-TREE copy**, so a lane that opened a file before another lane landed work in it, and then
names that path, silently reverts the landed commit. Nothing downstream can tell: the reverted tree
was a valid tree an hour ago, so it parses, its imports resolve, and its own tests pass.

WHY `tools/symbol_landing_check.py` IS GREEN ON THIS AND ALWAYS WILL BE. That control asks the
opposite question -- *does every first-party reference RESOLVE in the tree the commit creates* --
and a stale copy is INTERNALLY CONSISTENT by construction: the symbol and its callers revert
together, so every reference resolves. Not a gap in its reach; outside its subject. This one asks
the only question that can see a revert: *does this copy show any trace of the last landing?*

TWO RULES, AND THE ORDER THEY WERE ARRIVED AT IS EVIDENCE, SO IT IS RECORDED HERE.

  1. PREDATES-THE-LANDING (the one that fires). Take C, the last commit touching this path. Take
     the lines C ADDED that are DISTINCTIVE -- non-trivial, and appearing exactly once in C's
     version of the file. If the copy about to be committed contains **not one** of them, that copy
     was taken before C landed and committing it reverts C.

     1a. AND WHERE THE CLOCK ALREADY SAYS THE COPY IS OLDER THAN C, the vouch is **all** of them
     rather than any, because there a shared line is coincidence and not derivation. A copy that
     predates C cannot have been built on C, so a single line it LACKS is proof it does not have
     it. This is the fail-open that let a 1-of-53 revert of `tools/generate_value_arms_data.py`
     past the census; see `judge` for the measurement and for why no threshold between the two
     extremes is used.

  2. STRICT SYMBOL SUBSET. Refuse when the copy supplies strictly fewer names than HEAD and adds
     not one. Cheap, exact, and it catches a deletion that rule 1 misses because the deleted name
     came from an older commit than C.

  4. PREDATES-BY-CLOCK (`clock_judge`, added 2026-09-22). Rules 1 and 2 have NO READER outside
     `READABLE`, so `violations()` skipped `.md`, `.yaml` and `.json` in silence -- which is where
     the maturity map, the knowledge layer, the simplification notes and the staging record live.
     There, rule 1's line evidence is applied ONLY to a copy whose own mtime predates C. The clock
     is a TRIGGER, not a verdict: measured on the live tree, a clock-only rule refuses 13.1% of
     tracked-modified paths and rule 1 positively vouches for nineteen of them, because
     `surgical_land` never writes the working tree and clock-staleness is therefore the normal
     resting state of a shared checkout. What the clock buys is the `.json` exclusion this module
     rejected widening `READABLE` for: a regenerated artefact has a mtime NEWER than the landing, so
     it never enters. See `clock_judge` for the full measurement. (Rule 3 is `index_residue`, a
     different subject on the same door; the numbering is historical and left alone.)

WHICH DOOR THE REFUSAL NAMES IS A THIRD QUESTION, AND IT HAS THREE ANSWERS, NOT TWO. A copy that
supplies a name the base lacks was called HOLDER WORK and sent to `surgical_land --content`. That is
a set difference, and a set difference cannot tell a name the base NEVER HAD from one it CUT ON
PURPOSE -- so the remedy told a lane to land back a forbidden import that had closed every lane's
publish for 33 hours. `cut_of` asks git instead, per name, and a name whose binding stopped at a
commit is a CUT: the verdict says so, names that commit, and never names the land-it door.

**RULE 2 WAS THE ONE SPECIFIED, AND MEASURING IT REFUTED IT AS THE PRIMARY.** Pre-registered in
`docs/staging/PREREG_THE_STALE_COPY_CENSUS_IS_A_DIFFERENT_QUESTION_FROM_THE_MTIME_CENSUS_2026-09-08.md`:
I predicted rule 2 would fire on 2-8 of the sixteen mtime-stale paths in the shared tree. It fired
on **zero**, and a poison round proved that was reachability, not blindness -- the control fires on
a hand-made strict subset of the same file. The reason is that `surgical_land` **never writes the
working tree** (by design -- that is what makes it safe for a two-lane file), so a landed commit
leaves every other lane's copy stale-by-mtime while its symbol set stays a SUPERSET of HEAD: the
lane's own additions are still there, the other lane's are simply missing. Symbol-set granularity
cannot see that. Rule 1 fires on 8 of the same 59 paths, including
`tools/promote_worktree_landing.py`, which was missing all fourteen lines of `_bind_to_claim` --
the binding repair, about to be deleted a second time by exactly the mechanism the first finding
named.

WHY "NOT ONE PRESENT" AND NOT A FRACTION. A threshold here would be fitted to today's tree, which
is `feedback_a_synthetic_fixture_you_keep_retuning_until_it_agrees` wearing a constant. "Contains no
trace of that commit at all" is a QUALITATIVE state -- your copy predates it -- and it needs no
number. The DISTINCTIVE filter is what makes the qualitative version hold up: without it, one
coincidentally-repeated line (`return None`, a duplicated assert) reads as "the copy has some of
it" and two genuinely-stale files escaped. Uniqueness in C's own version of the file is a property
of the evidence, not a dial: measured, it moved the population from 5 to 8 and every one of the
three additions is a copy with no trace of the landing.

WHAT THIS DOES NOT CATCH, said plainly so a green result is not read as stronger than it is. A lane
that has ALREADY pulled the landing and then rewrites over it is invisible to rule 1 (it has the
lines) and to rule 2 (it adds names). That is the wider half of
`A_REWRITE_DELETED_THE_BINDING_REPAIR`, and this control **narrows** that class rather than closing
it. The wider rule -- refuse on ANY lost line -- was considered and rejected: deleting code is an
ordinary edit, so it would refuse a large fraction of honest commits through the ONE legal landing
door, and a door that refuses honest work is the pressure toward bypass that `tools/surgical_land.py`
exists to remove. Narrow-and-armed beats wide-and-turned-off.

THE SUBJECT IS THE TREE THE COMMIT WOULD CREATE, never the working tree -- the same subject
`tools/symbol_landing_check.py` and `tools/surgical_land.py` already gate on, and for the same
reason: a `--content` landing supplies bytes that are on no disk anywhere, so a working-tree read
would judge a file the commit is not making.

VACUOUS EXTRACTION IS A REPORTED STATE, NOT A PASS. A path this control has no reader for yields
`None`, and `None` never reaches a comparison. Folded to an empty set instead, both sides would be
empty, the sets equal, and the path waved through **while looking checked** -- a coverage measure
that is useless without ever being fail-open. `--census` prints the no-opinion population in its own
section so what the control cannot see is on the surface rather than absent from it.

BOTH DOORS, SINCE 2026-09-08. `tools/surgical_land.py` calls `violations()` in-process, and
`tools/git-hooks/pre-commit` calls `--staged` -- so a plain `git commit -- <path>` faces this too.
It did not until that date, and the asymmetry was the wrong way round: the careful door was guarded
and the cheap, commoner one was not. See `staged()` for why the hook's subject is `git write-tree`
and why running inside `surgical_land`'s own extract is a paired SKIP rather than a second ask.

Run standalone:

    python3 -m tools.stale_copy_refusal --census        # working tree vs HEAD, both rules
    python3 -m tools.stale_copy_refusal --staged        # the tree this index would commit
    python3 -m tools.stale_copy_refusal --at-tree T --since-tree P

Exit 0 = clean, 1 = a path would revert a landing or lose names.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

# REUSED rather than re-cut: `_base_state` already answers "how far is local HEAD from the trunk"
# with the three-answer shape this surface needs -- read, no-remote-base, and a REFUSAL when the ref
# exists but git cannot answer. Re-cutting it here would have given this module a second opinion
# about the trunk, which is the one-question-several-implementations shape the census exists to
# catch in everybody else.
from background.tree_divergence import REMOTE_BASE, _base_state

# REUSED rather than re-cut: `_bound_names` is the import-time binding walker whose conditional and
# try-guarded cases (`try: from x import y / except ImportError: y = None` supplies `y`) were
# learned by that control reddening on this repo's own compatibility shims. Its batch blob reader
# is deliberately NOT reused -- see `blob_at`.
from tools.symbol_landing_check import _bound_names

ROOT = Path(__file__).resolve().parent.parent

#: Suffixes the CONTENT rules (1 and 2) have an opinion about. Anything else falls to `clock_judge`,
#: which reaches a strict subset of it, and whatever that declines is reported as no-opinion.
#: Generated artefacts are deliberately absent here: `site/data/*.json` is REWRITTEN whole on every
#: publish, so "lost a line" is its normal operation and not a finding. That reason is why widening
#: this tuple is still the wrong move -- `clock_judge` excludes the same population by the file's
#: own mtime instead, which is a property of the artefact rather than a list that rots.
PY_SUFFIXES = (".py",)
PAGE_SUFFIXES = (".html", ".js")
READABLE = PY_SUFFIXES + PAGE_SUFFIXES

#: Suffixes `symbols()` can read but `READABLE` deliberately does NOT include, so the COMMIT guard
#: is unchanged by their arrival. The distinction is the whole of this addition: `violations()` and
#: `judge()` gate on `READABLE` and run on every commit in a tree three lanes write, where a daemon
#: rewriting a `.json` ledger between two commits is ordinary operation -- widening READABLE would
#: red every lane for a carrier's normal churn. The ADVANCE's losslessness door has the opposite
#: problem and is where this is consumed: `tools/refresh_to_head.judge_copy` answered every `.json`
#: blocker "this control has no reader for .json files, so it CANNOT establish that the copy has
#: nothing to lose", which is fail-closed and correct and ALSO permanently unresolvable -- and under
#: `origin_reconcile.advance_shared_tree`'s all-or-nothing rule ONE permanently unresolvable path is
#: fatal to every class beside it. Measured on the shared tree 2026-09-21: of 11 paths holding the
#: fast-forward, 6 got this answer and only the generated-output oracle rescued 5 of them.
DATA_SUFFIXES = (".json",)


def _json_leaves(text: str, path: str) -> dict[str, str]:
    """A JSON document as `key path -> a token standing for the value at it`.

    THE ONE WALK BOTH READINGS COME FROM. `_json_leaf_names` welds the two halves together and
    `json_leaf_delta` holds them apart; deriving either by splitting the other's strings would be a
    second implementation of this naming, and the first thing to rot would be a key that contains
    an `=` sign.

    LIST POSITION IS PART OF THE PATH, so a reordering or an insertion reads as a changed document.
    Conservative on purpose: this decides whether a file is written over, and an ordering nobody
    proved irrelevant is not one this control may flatten.
    """
    try:
        doc = json.loads(text)
    except ValueError as exc:
        raise Unparseable("{} does not parse as JSON: {}".format(path, exc)) from exc
    leaves: dict[str, str] = {}

    def walk(node, trail: str) -> None:
        if isinstance(node, dict):
            if not node:
                leaves[trail] = "{}"
            for key, value in node.items():
                walk(value, "{}.{}".format(trail, key) if trail else str(key))
        elif isinstance(node, list):
            if not node:
                leaves[trail] = "[]"
            for index, value in enumerate(node):
                walk(value, "{}[{}]".format(trail, index))
        else:
            leaves[trail] = hashlib.sha256(
                json.dumps(node, sort_keys=True).encode("utf-8")).hexdigest()[:16]

    walk(doc, "")
    return leaves


def _json_leaf_names(text: str, path: str) -> frozenset[str]:
    """A JSON document's leaves as `key.path=<digest of value>` names.

    THE VALUE IS IN THE NAME, AND THAT IS THE FAIL-OPEN THIS AVOIDS. Keyed on the key-path alone,
    a copy that REWROTE every value while keeping the shape supplies no name the base lacks and
    would be cleared as "superseded" -- destroying an edit while looking checked. That is exactly
    the collapse `_PAGE_ANCHORS` warns about one class over. With the value digested into the name,
    any changed leaf reads as BOTH a name supplied and a name dropped, so the copy refuses; only a
    copy whose every leaf is present AND equal in the base can be strictly superseded by it.

    AND THAT IS ALSO WHY IT MAY NOT BE THE ONLY READING -- use `json_leaf_delta` to say WHY a copy
    refuses. A set difference over these names answers "are the two documents the same?" correctly
    and answers "what does this copy supply that the base lacks?" wrongly, because a key whose
    NUMBER MOVED lands in the difference beside a key the base never had. Every value in a
    regenerated artefact is edited, so that second reading grades every regeneration as work to
    land -- structurally, whichever document is genuinely newer. Measured on the shared tree
    2026-09-23: `docs/observability/self_clearing_alarm_census.json` read as 1,778 "leaves HEAD
    does not have" and holds 7; `docs/market_research/domestic_shift_response_arc.json` read as 5
    and holds none at all.
    """
    return frozenset("{}={}".format(trail, token)
                     for trail, token in _json_leaves(text, path).items())


@dataclass(frozen=True)
class LeafDelta:
    """The three ways two JSON documents can differ, told apart. `_json_leaf_names` cannot: a leaf
    name carries its own value, so `novel` and `edited` arrive in one undifferentiated set there.

    `novel` is the only one of the three that is CONTENT THE BASE DOES NOT HOLD. `edited` is a
    disagreement about a value at a key both documents bind -- which is a decision between two
    drafts, never a supply of anything, and no `--keep` selection can take it without the revert.
    `dropped` is what the base holds and the copy does not."""
    novel: tuple[str, ...]
    edited: tuple[str, ...]
    dropped: tuple[str, ...]


def json_leaf_delta(head_text: str, work_text: str, path: str) -> LeafDelta:
    """Which key paths the copy ADDS, which it EDITS, and which it DROPS -- separately.

    THE DISTINCTION THIS EXISTS FOR is the one `_json_leaf_names` structurally cannot make, and the
    honest refusal built on it had been refusing every regenerated artefact in the tree while
    naming a door -- `isolate_hunks --keep N` -- that has nothing to select on a document whose
    every line is a value. An honest refusal that refuses everything is still a door nobody can
    walk through.

    Raises `Unparseable` from either side, which is the same fail-closed contract as `symbols`."""
    before, after = _json_leaves(head_text, path), _json_leaves(work_text, path)
    return LeafDelta(
        novel=tuple(sorted(k for k in after if k not in before)),
        edited=tuple(sorted(k for k in after if k in before and after[k] != before[k])),
        dropped=tuple(sorted(k for k in before if k not in after)),
    )

#: The name-bearing anchors of a page. NOT "every symbol" -- an id and a function declaration are
#: what another lane's landed work adds to a page and a stale copy silently removes. Narrow on
#: purpose: a looser reader (CSS class names, arbitrary object keys) makes the set churn on
#: reformatting, and churn that ADDS a name defeats the strict-subset rule outright.
_PAGE_ANCHORS = (
    re.compile(r"""\bid\s*=\s*["']([A-Za-z_][\w-]*)["']"""),
    re.compile(r"\bfunction\s+([A-Za-z_$][\w$]*)\s*\("),
    re.compile(r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*="),
)

PREDATES = "predates_landing"
SUBSET = "strict_symbol_subset"
UNPARSEABLE = "unparseable"
CLOCK = "predates_landing_by_clock"
PARTIAL = "predates_landing_carrying_some"


class Unparseable(Exception):
    """The blob would not parse. FAIL-CLOSED: an unavailable check is a failed check, and a `.py`
    blob that will not parse is a finding in its own right, never a skip."""


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True,
                          check=False)


def _git_text(root: Path, *args: str) -> str:
    out = _git(root, *args)
    if out.returncode != 0:
        raise RuntimeError("git {} rc={}: {}".format(
            " ".join(args[:2]), out.returncode, out.stderr.strip()[-300:]))
    return out.stdout


def blob_at(root: Path, tree: str, path: str) -> str | None:
    """`tree:path`'s text, or `None` when the tree has no such path.

    PER-PATH ON PURPOSE, where `symbol_landing_check._read_blobs` batches. That reader exists to
    keep a ~700-file whole-tree census off one fork per file, and it treats absence as an ERROR
    because at whole-tree scale absence cannot happen. Here absence is the ORDINARY answer at both
    ends -- a new file has no parent blob, a deletion has no result blob -- and the subject is the
    handful of paths one commit stages, where the fork cost is not the bill."""
    out = _git(root, "show", "{}:{}".format(tree, path))
    return out.stdout if out.returncode == 0 else None


# ------------------------------------------------------------------ rule 1: predates the landing


def _trivial(line: str, *, comments_are_evidence: bool = False) -> bool:
    """Lines that carry no evidence of WHICH commit they came from. A bare `return None` or a
    closing bracket appears in a thousand files, so its absence proves nothing about staleness and
    its presence proves nothing about freshness.

    COMMENTS ARE WEAK EVIDENCE, NOT NO EVIDENCE, and the difference is the whole of `distinctive_
    lines`' fallback. A comment is excluded by default because a licence header or a `# noqa` says
    nothing about provenance -- but that is a reason to prefer code, not a reason to throw the
    evidence away when there is no code to prefer. `comments_are_evidence=True` keeps the length and
    bracket-noise floors and drops only the comment-prefix exclusion."""
    s = line.strip()
    if len(s) < 5 or set(s) <= set("{}()[],:\"'"):
        return True
    return not comments_are_evidence and s.startswith(("#", "//", "*"))


def last_commit_touching(root: Path, path: str, upto: str = "HEAD") -> str | None:
    sha = _git(root, "log", "-1", "--format=%H", upto, "--", path).stdout.strip()
    return sha or None


def distinctive_lines(root: Path, path: str, commit: str) -> tuple[str, ...]:
    """The stripped lines `commit` ADDED to `path` that are non-trivial and appear exactly once in
    `commit`'s own version of the file.

    UNIQUENESS IS A PROPERTY OF THE EVIDENCE, NOT A DIAL. A line the commit added twice cannot
    distinguish "your copy has the landing" from "your copy happens to contain that line already",
    so it is not evidence either way and is dropped before the question is asked -- not weighted.

    AN EMPTY EVIDENCE SET IS "CANNOT TELL", AND `judge` READS IT AS "NO COMPLAINT" -- so it must
    never be empty while any evidence survives at all. `judge` guards rule 1 with `if distinctive:`,
    which means every filter here is also a silent fail-open: filter the set to nothing and the
    staleness question is not asked, the copy falls through to the symbol-subset leg, and a copy
    that changes only a CALL SITE keeps every module-level name and passes clean.

    THAT WAS LIVE, AND IT COST THE SUITE. `dcb8c6d10` added exactly five lines to
    `simulation/renewals.py`: three comments, and `fuel="electricity",` twice. The comment filter
    took the three, the uniqueness filter took the other two, and the working copy -- twelve days
    older than the landing, and dropping the argument that `build_svt_schedule` had just made
    required -- was graded CLEAN by the census while `test_svt_product.py` died on a `TypeError`.
    Eight siblings from the same landing were caught; the ninth, the only one that reddened
    anything, was the one the filters emptied.

    So the comment filter is a PREFERENCE, applied only while it leaves something behind. It never
    gets to be the reason there is nothing to ask. This is narrow by construction: the fallback is
    reachable only where the strong set is already empty, so it cannot change a verdict that has
    evidence -- measured over the 47 modified readable files on the tree of 2026-09-16, it moves
    two, and both genuinely predate their own landing by mtime."""
    parent = _git(root, "rev-parse", "--verify", "{}^".format(commit))
    if parent.returncode != 0:
        # The commit that CREATED the file. There is no "before" to have landed over, and a copy
        # containing none of a file's creating commit is a file you have not got at all.
        return ()
    diff = _git(root, "diff", "--unified=0", "{}^".format(commit), commit, "--", path).stdout
    added = [ln[1:].strip() for ln in diff.splitlines()
             if ln.startswith("+") and not ln.startswith("+++")]
    version = blob_at(root, commit, path) or ""
    freq = Counter(ln.strip() for ln in version.splitlines())
    strong = tuple(ln for ln in added if not _trivial(ln) and freq[ln] == 1)
    if strong:
        return strong
    return tuple(ln for ln in added
                 if not _trivial(ln, comments_are_evidence=True) and freq[ln] == 1)


# ------------------------------------------------------------------ rule 2: strict symbol subset


def _class_members(body: list[ast.stmt], prefix: str = "") -> set[str]:
    """`Class.method` for every class in the body, nesting included.

    METHODS ARE THE POINT, not an extra. `_bound_names` is module-level only, and the landed work a
    stale copy most often drops is a METHOD added to an existing class -- every top-level name
    survives, so a module-level-only reader calls the sets equal and passes it."""
    out: set[str] = set()
    for node in body:
        if isinstance(node, ast.ClassDef):
            qual = prefix + node.name
            for inner in node.body:
                if isinstance(inner, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    out.add("{}.{}".format(qual, inner.name))
            out |= _class_members(node.body, qual + ".")
        elif isinstance(node, (ast.If, ast.Try, ast.With)):
            out |= _class_members(node.body, prefix)
            out |= _class_members(getattr(node, "orelse", []), prefix)
            out |= _class_members(getattr(node, "finalbody", []), prefix)
            for handler in getattr(node, "handlers", []):
                out |= _class_members(handler.body, prefix)
    return out


def symbols(text: str, path: str) -> frozenset[str] | None:
    """The names `path`'s content supplies, or `None` when this control has no reader for it.

    `None` IS NOT THE EMPTY SET and the difference is the whole of the vacuity argument: an empty
    set compares equal to an empty set and passes, a `None` refuses to be compared at all."""
    suffix = Path(path).suffix
    if suffix in PY_SUFFIXES:
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            raise Unparseable("{} does not parse: {}".format(path, exc)) from exc
        return frozenset(_bound_names(tree.body) | _class_members(tree.body))
    if suffix in PAGE_SUFFIXES:
        found: set[str] = set()
        for pattern in _PAGE_ANCHORS:
            found.update(pattern.findall(text))
        return frozenset(found)
    if suffix in DATA_SUFFIXES:
        return _json_leaf_names(text, path)
    return None


# ------------------------------------------------------------------------------- the judgement


def gains_over(head_text: str, new_text: str, path: str) -> tuple[str, ...] | None:
    """The names this copy supplies that HEAD does not -- or `None` when it cannot be told.

    THIS IS WHICH DOOR THE REFUSED LANE SHOULD WALK THROUGH, and until 2026-09-08 the refusal
    guessed. It named `isolate_hunks --keep N` for every path, and
    `SEAT_FINDING_THE_STALE_COPY_REMEDY_HAS_NO_MOVE_FOR_A_RIVAL_COPY_HEAD_ALREADY_SUPERSEDES` is
    what that costs: two of the eight copies on the shared tree supply NO name HEAD lacks, so
    `isolate_hunks` refuses them at both ends -- select a hunk and you land a revert, select none
    and it refuses the empty change -- and the lane is sent somewhere with no move. Empty here
    means the copy is a rival HEAD strictly supersedes and `tools/refresh_to_head.py` is the door;
    non-empty means it is holder work and `isolate_hunks` is.

    `None` IS NOT EMPTY, for the reason the rest of this module keeps saying: an unreadable or
    unparseable side cannot establish "supplies nothing", and printing the Kind-A door on a guess
    would send a lane to a tool that overwrites bytes."""
    try:
        before, after = symbols(head_text, path), symbols(new_text, path)
    except Unparseable:
        return None
    if before is None or after is None:
        return None
    return tuple(sorted(after - before))


@dataclass(frozen=True)
class Cut:
    """A name the copy supplies that the base ONCE HAD AND DELIBERATELY REMOVED, with the commit
    that removed it. Not holder work by any reading: landing it re-creates a decision."""
    name: str
    commit: str


def _supplied_at(root: Path, path: str, commit: str) -> frozenset[str] | None:
    """The names `path` BOUND at `commit`, or `None` when that cannot be established there."""
    blob = blob_at(root, commit, path)
    if blob is None:
        return frozenset()  # the path did not exist there, so it bound nothing -- an answer.
    try:
        return symbols(blob, path)
    except Unparseable:
        return None


def cut_of(root: Path, path: str, name: str, parent: str = "HEAD") -> Cut | None:
    """The commit in `parent`'s history that REMOVED `name` from `path` -- or `None` when that
    history never bound it, or when the removal cannot be attributed to one commit.

    THE DEFECT THIS OWNS, banked as `THE_HOLDER_WORK_VERDICT_NAMED_A_FORBIDDEN_IMPORT_AS_WORK_TO_
    LAND_AND_IT_WAS_RED_ON_THE_TREE` (2026-09-16). `gains_over` is a SET DIFFERENCE, and a set
    difference cannot tell a name the base NEVER HAD from a name the base CUT ON PURPOSE. The two
    need opposite treatment and the verdict gave them the same one: *"so it is HOLDER WORK"*,
    followed by `surgical_land --content`, which lands the cut back. The live instance was an import
    HEAD forbids in a fourteen-line comment naming the 33-hour outage it caused, and the control
    beside it was red on the shared tree while the census called the copy an asset.

    ASK GIT, BECAUSE GIT IS WHERE THE DECISION IS RECORDED. `-S` is the candidate finder -- the
    commits where this token's OCCURRENCE COUNT moved in this path -- and `symbols()` is the oracle,
    the same reader that produced the verdict. Using the pickaxe as the oracle too would attribute a
    cut to a later comment edit that merely mentions the name (the live instance's own docstring at
    HEAD says in words that the test is deleted), and would read `Class.method` by its last
    component and call a same-named method of another class the same name.

    THE ERROR DIRECTION IS DELIBERATE AND IT IS NOT THE FLATTERING ONE. Every `None` here means
    *"not established as a cut"*, which leaves the copy reading as holder work -- today's verdict.
    That matters because the cut door OVERWRITES BYTES (`refresh_to_head`), so a cut claimed on a
    guess destroys a lane's work through the repair for losing it. An unattributable removal, an
    unparseable historic blob and a name this history never bound all take that same exit.
    """
    token = name.rsplit(".", 1)[-1]
    log = _git(root, "log", "--format=%H", "--pickaxe-regex",
               "-S" + r"\b{}\b".format(re.escape(token)), parent, "--", path)
    removed_at: str | None = None
    for sha in (ln.strip() for ln in log.stdout.splitlines() if ln.strip()):  # newest first
        supplied = _supplied_at(root, path, sha)
        if supplied is None:
            return None
        if name in supplied:
            # The boundary: this commit still bound it, so the one after it is where it stopped.
            return Cut(name, removed_at) if removed_at is not None else None
        removed_at = sha
    return None


def cuts_among(root: Path, path: str, names: tuple[str, ...],
               parent: str = "HEAD") -> tuple[Cut, ...]:
    """Which of `names` the base cut on purpose. One `git log -S` per candidate, on a population of
    at most a handful per refusal -- and only ever on the REFUSAL path, never on a clean commit."""
    found = (cut_of(root, path, name, parent) for name in names)
    return tuple(cut for cut in found if cut is not None)


# ------------------------------------------- rule 1c: a name that is SUPPLIED but CANNOT RUN
#
# THE DEFECT THIS OWNS, and it is the second of the two 2026-09-08 findings that froze `H_harness`
# for nine days: `SEAT_FINDING_THE_R1_COPYS_MISSING_PARTNER_IS_IN_A_SALVAGE_COMMIT_AND_HEAD_
# SUPERSEDED_IT_UNDER_NEW_NAMES`. `cut_of` above widened the difference by one class -- a name the
# base DELETED is not holder work -- and that class is not this one. A name the base NEVER BOUND is
# still counted as work to land, and a draft written against an API that no longer exists supplies
# eleven such names and not one unit of landable work. The finding measured it by running the copy:
# 26 collected, 6 failed, every failure an `AttributeError` for an attribute HEAD's module does not
# define. Landing any hunk of it adds a red test to the suite.
#
# STATIC, WHERE THE FINDING PROPOSED RUNNING IT, and the trade is stated rather than hidden. The
# finding's predicate was "the file's own execution of it raises AttributeError"; executing a rival
# WORKING COPY to decide whether to overwrite it means importing an arbitrary lane's uncommitted
# module inside a control that then destroys bytes, and this repo has already banked what probing an
# unknown module costs (`probing_an_unknown_module_with_help_can_run_it_and_write_the_shared_tree`).
# The AST asks the same question of the same two facts -- does this name's own body reach for an
# attribute the base's module does not bind -- without being the thing that runs it. WHAT IT CANNOT
# SEE, said here because a blindness nobody wrote down is a fail-open: a reference built by
# `getattr(mod, name)` or through an alias this walker did not resolve reads as no reference at all,
# so the name stays HOLDER WORK. That is the safe direction and it is the only direction this
# discriminator is allowed to be wrong in, because the door it opens overwrites a lane's bytes.


@dataclass(frozen=True)
class Dead:
    """A name the copy supplies whose OWN BODY reaches for an attribute the base does not bind, on
    a first-party module the base DOES hold. Not holder work: landing it lands a red."""
    name: str
    #: repo-relative path of the module whose attribute is missing
    module: str
    attr: str
    #: a commit that DID bind `attr` there, or "". CONTEXT FOR THE READER, NEVER THE PREDICATE --
    #: the r1 instance's missing half was in a SALVAGE commit on no branch, which three documents
    #: read as "exists nowhere" because they asked branches instead of `--all`. Whether some
    #: unreachable commit once had it says nothing about whether the copy can land; it says a great
    #: deal to whoever is deciding if the module is worth reviving, so it goes on the surface.
    elsewhere: str = ""


def _dotted(node: ast.AST) -> str | None:
    """`a.b.c` as a string when the node is a pure dotted name, else `None`."""
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    parts.append(node.id)
    return ".".join(reversed(parts))


def _module_aliases(text: str) -> dict[str, str]:
    """Local name -> dotted module path, for every import shape this file uses.

    `from a.b import c` is included because `c` may be a MODULE rather than a symbol; whether it
    resolves to a file on disk is `_module_blob`'s question, and a name that resolves to nothing
    yields no verdict at all."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {}
    out: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out[alias.asname or alias.name] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            for alias in node.names:
                if alias.name != "*":
                    out[alias.asname or alias.name] = "{}.{}".format(node.module, alias.name)
    return out


def _module_blob(root: Path, dotted: str, parent: str) -> tuple[str, str] | None:
    """(repo-relative path, text) of the module `dotted` names IN THE BASE TREE, or `None`.

    `None` means "not a first-party module of this repository at `parent`" -- a stdlib or site-
    packages import, or a module the base does not hold. No opinion is the answer there: this
    control can only speak about attributes the base itself is supposed to supply."""
    stem = dotted.replace(".", "/")
    for candidate in ("{}.py".format(stem), "{}/__init__.py".format(stem)):
        text = blob_at(root, parent, candidate)
        if text is not None:
            return candidate, text
    return None


def _definition_of(text: str, name: str) -> ast.AST | None:
    """The top-level `def`/`class` that binds `name`, or `None` when it is bound some other way."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) \
                and node.name == name:
            return node
    return None


def dead_of(root: Path, path: str, name: str, text: str, parent: str = "HEAD") -> Dead | None:
    """`name`'s own body reaches for an attribute `parent`'s copy of a first-party module does not
    bind -- or `None`, which means NOT ESTABLISHED AS DEAD and leaves the name reading as work.

    Every early return here is that `None`. The error direction is deliberate and it is not the
    flattering one: the only consumer of a `Dead` is a door that OVERWRITES the copy, so a name
    called dead on a guess destroys a lane's work through the repair for losing it.

    THE FALSE POSITIVE THIS CANNOT RULE OUT, AND WHY IT IS NOT AUTOMATED ANYWHERE. A lane writing
    test-first -- the control before the module it will grade -- produces a file that is
    indistinguishable from this one by any static or dynamic reading: both name an attribute that
    does not exist yet. The difference is intent, and intent is not on disk. So `Dead` never clears
    a door by itself; `refresh_to_head` requires rule 2 (the base must already supersede the copy)
    AND an explicit `--superseded` typed by someone who has read these names printed out. Four
    conjunctive guards and a human, for a verdict whose honest confidence is "probably".
    """
    definition = _definition_of(text, name)
    if definition is None:
        return None
    aliases = _module_aliases(text)
    for node in ast.walk(definition):
        if not isinstance(node, ast.Attribute):
            continue
        dotted = _dotted(node.value)
        if dotted is None or dotted not in aliases:
            continue
        found = _module_blob(root, aliases[dotted], parent)
        if found is None:
            continue
        module, blob = found
        try:
            bound = symbols(blob, module)
        except Unparseable:
            continue
        if bound is None or node.attr in bound:
            continue
        where = _git(root, "log", "--all", "--max-count=1", "--format=%H",
                     "-S", node.attr, "--", module).stdout.strip()
        return Dead(name, module, node.attr, where)
    return None


def dead_among(root: Path, path: str, names: tuple[str, ...], text: str,
               parent: str = "HEAD") -> tuple[Dead, ...]:
    """Which of `names` cannot run against the base. Same shape and same cost model as
    `cuts_among`: refusal path only, a handful of candidates, and silence is "not established"."""
    found = (dead_of(root, path, name, text, parent) for name in names)
    return tuple(dead for dead in found if dead is not None)


# --------------------------------- the clause that separates HOLDER WORK from a REPLACEMENT
#
# THE DEFECT THIS OWNS is the FIRST of the two 2026-09-08 findings, `SEAT_FINDING_THE_HOLDER_WORK_
# RULE_COUNTS_NAMES_SO_A_RENAMED_DRAFT_READS_AS_WORK_TO_LAND`, and the direction it fails in is the
# expensive one: the verdict says LAND THIS, of a copy whose landing is a revert. A copy that
# renames a control HEAD already carries supplies a name and no work, and at the level of a symbol
# SET a rename and a genuine addition are identical -- so the set difference cannot be the test.
#
# The finding's clause, verbatim, and it is about HUNKS and not about the file:
#
#     holder work  <=>  exists a hunk H such that  symbols_added(H) - HEAD_symbols  is non-empty
#                       AND  symbols_deleted(H) & HEAD_symbols  is empty
#
# WHY IT MUST BE PER HUNK. `--keep N` is the remedy the verdict names, and it selects hunks. A copy
# that appends a function AND separately rewrites another one has a legal selection -- take the
# append, leave the rewrite -- so it IS holder work. A copy whose addition and deletion are THE SAME
# HUNK has none: the finding's live instance was `@@ -441,728 +440,81 @@`, 718 lines out and 70 in,
# indivisible, and `isolate_hunks` is right to have no `--keep` that splits it. A file-level test
# would collapse those two onto each other and refuse the first, which is the wrong answer in the
# direction that strands a lane's real work.
#
# COMPUTED ON THE ISOLATED OUTPUT, not on the +/- lines. The finding's own closing paragraph names
# this as the cheap step that turns the class up -- "checking the isolated output's symbol set
# against HEAD, rather than the copy's, and it is one AST parse". It is also exact where a line
# walk is approximate: `reconstruct` builds the bytes `--keep N` would actually hand to
# `surgical_land`, so what is graded is the thing that would land.


def landable_hunks(head_text: str, work_text: str, path: str) -> tuple[int, ...]:
    """The hunk indices `--keep` could take that ADD a name the base lacks and DROP none it has.

    Empty means there is NO legal `--keep` selection: every hunk carrying new work also deletes
    landed work, so the copy is a REPLACEMENT and the choice between the two implementations is a
    judgement neither door is allowed to make. Numbering is `isolate_hunks --survey`'s, so a caller
    can print an index a reader can then select.

    RETURNED IN `--keep`'s BASE, WHICH IS 1, AND THAT IS THE WHOLE POINT OF THE SENTENCE ABOVE.
    `group_opcodes` numbers its groups from 0 and `reconstruct` selects on those, but neither is a
    surface any reader types at: `isolate_hunks --survey` PRINTS `enumerate(groups, start=1)` and
    `--keep N` parses `int(sel) - 1`. This returned the 0-based gid for its whole life, so every
    verdict built on it cited an index shifted one below the only numbering a reader can select --
    which is exactly what the comment below says must never happen. On
    `simulation/premise_population.py` the refusal read *"land hunk(s) 0, 1"* and
    `isolate_hunks --keep 0 --keep 1` answered *"REFUSED: hunk 0 does not exist (4 in this file)"*,
    while the selection it meant was `--keep 1 --keep 2`. Drop the `+ 1` and the door's own remedy
    stops being runnable; `test_the_cited_hunks_are_selectable_by_the_tool_the_refusal_names` is
    the leg, and it goes through `--keep` rather than `reconstruct` because `reconstruct` is the
    0-based side and asking it agrees with itself is what hid this for the function's whole life.
    """
    # REUSED rather than re-cut: `group_opcodes`/`reconstruct` ARE the hunk map `--keep` selects
    # over, and they are pure. Re-deriving a second hunk numbering here would mean this verdict
    # cites an index that the tool it sends the reader to does not agree with.
    from tools.isolate_hunks import group_opcodes, reconstruct

    try:
        head_names = symbols(head_text, path)
    except Unparseable:
        return ()
    if head_names is None:
        return ()
    base = head_text.splitlines(keepends=True)
    work = work_text.splitlines(keepends=True)
    ops, groups = group_opcodes(base, work)
    out: list[int] = []
    for gid in range(len(groups)):
        isolated = "".join(reconstruct(base, work, ops, groups, {gid}))
        try:
            names = symbols(isolated, path)
        except Unparseable:
            continue  # an isolation that will not parse is not a route anyone can take
        if names is None:
            continue
        if names - head_names and not head_names - names:
            out.append(gid + 1)  # into `--keep`'s base -- see the docstring
    return tuple(out)


@dataclass(frozen=True)
class Loss:
    path: str
    rule: str
    detail: tuple[str, ...]
    commit: str = ""
    #: () = supplies nothing HEAD lacks; a tuple = holder work; None = could not be told.
    gains: tuple[str, ...] | None = None
    #: The subset of `gains` the base DELETED on purpose -- see `cut_of`. Never holder work.
    cuts: tuple[Cut, ...] = ()
    #: The file's own mtime established that it predates `commit`. Decides the remedy where no
    #: symbol reader can: a copy taken before a landing cannot be holder work OVER that landing.
    by_clock: bool = False
    #: How many of the landing's distinctive lines this copy DOES carry, when `detail` is the ones
    #: it lacks. Coincidence rather than derivation once `by_clock` is set -- printed so the reader
    #: can see the share the verdict was reached on rather than take the verdict's word for it.
    carried: int = 0

    @property
    def novel(self) -> tuple[str, ...]:
        """The gains that are genuinely new -- what the holder-work verdict was always claiming."""
        cut = {c.name for c in self.cuts}
        return tuple(n for n in (self.gains or ()) if n not in cut)

    @property
    def is_rival(self) -> bool:
        """True when this copy supplies the base NOTHING it does not already have BY CHOICE. A copy
        whose every "new" name is a re-creation of a deletion is a rival copy exactly as much as one
        with no new name at all -- which is why the door is the same and `gains == ()` is no longer
        the test."""
        return self.gains is not None and not self.novel

    @property
    def names_the_refresh_door(self) -> bool:
        """True when `remedy()` sends this path to `refresh_to_head` -- which is the ONLY thing
        `_door_check` may key its grading on.

        THE DEFECT THIS IS THE REPAIR FOR (2026-09-22). `_door_check` graded the named door for
        `is_rival` rows only, and `is_rival` is False whenever `gains is None` -- which is every
        `.md` and `.yaml` row, because no symbol reader reads them. Those rows reach the `by_clock`
        branch of `remedy()`, which names `refresh_to_head` just as loudly, and that tool answers
        `refused_no_reader` for those suffixes BY CONSTRUCTION and can never answer anything else.
        So the census printed a door that was permanently shut for 7 of 21 paths, and the grader
        built to catch exactly that was scoped past them. Measured on the shared tree the same day:
        27 rows, and the door the census named took ZERO of them.

        KEYED TO WHICH BRANCH `remedy()` TAKES, not to a suffix list. A suffix list here would rot
        the moment `READABLE` moves, and it would be a second implementation of the branch
        condition above it -- the one-requirement-two-implementations shape this repository pays
        for most. The two conditions are the two branches that print the tool's name; if a third is
        ever added, this returns False for it and the row goes ungraded rather than mis-graded."""
        return self.is_rival or (self.by_clock and self.gains is None)

    def _cut_lines(self) -> str:
        return "".join("        - {}  <- REMOVED by {}\n".format(c.name[:90], c.commit[:9])
                       for c in self.cuts)

    def remedy(self) -> str:
        if self.by_clock and self.gains is None:
            # The door is NOT in doubt here, which is why this branch precedes the `gains is None`
            # one that would otherwise claim it. `gains` is None for every CLOCK loss because these
            # are the paths no symbol reader can read -- but the clock has already established the
            # thing `gains` exists to guess at: this copy was taken before the landing, so it cannot
            # be holder work over it, and `isolate_hunks` has nothing legitimate to select.
            #
            # KEYED TO `by_clock` AND NOT TO `rule == CLOCK`, because PARTIAL is also a clock
            # verdict and a READABLE one, so it arrives here with `gains` READ rather than guessed
            # at. Where the names could be read they decide the door, and this branch must not
            # claim them: a copy can predate one landing and still hold work HEAD lacks from
            # before it.
            return ("      REMEDY: your copy of this file is OLDER than {} -- it was taken before "
                    "that\n      landing, so it cannot be carrying work built ON it. Re-open the "
                    "file at HEAD\n      (`python3 -m tools.refresh_to_head {}` surveys it; "
                    "`--write --slug NAME`\n      preserves these bytes and writes HEAD's over "
                    "them) and re-apply your edit.".format(self.commit[:9], self.path))
        if self.gains is None:
            return ("      REMEDY: cannot tell which door -- this copy's names could not be read, "
                    "so\n      neither `refresh_to_head` nor `isolate_hunks` is licensed until "
                    "that is fixed.")
        if self.cuts and not self.novel:
            return ("      REMEDY: every name HEAD \"lacks\" here is a RE-CREATION OF A DELIBERATE "
                    "DELETION, so\n      this copy is NOT holder work -- landing it puts back what "
                    "HEAD removed on purpose:\n{}"
                    "      It is a rival copy HEAD supersedes. `python3 -m tools.refresh_to_head "
                    "{}`\n      surveys it; `--write --slug NAME` preserves these bytes and writes "
                    "HEAD's over them.".format(self._cut_lines(), self.path))
        if self.cuts:
            return ("      REMEDY: this copy supplies {} name(s) HEAD lacks, but {} of them are "
                    "RE-CREATIONS\n      of deliberate deletions, so it must NEVER be landed whole:"
                    "\n{}"
                    "      `python3 -m tools.isolate_hunks --survey {}` and keep ONLY the hunks "
                    "carrying\n      {} -- NOT `--content {}=<file>`, which lands the file and the "
                    "cuts with it.".format(
                        len(self.gains), len(self.cuts), self._cut_lines(), self.path,
                        ", ".join(self.novel[:3]) + ("..." if len(self.novel) > 3 else ""),
                        self.path))
        if self.gains:
            return ("      REMEDY: this copy supplies {} name(s) HEAD lacks ({}), so it is HOLDER "
                    "WORK.\n      `python3 -m tools.isolate_hunks --survey {}`, `--keep N` builds "
                    "HEAD-plus-yours,\n      then `surgical_land --content {}=<file>`.".format(
                        len(self.gains), ", ".join(self.gains[:3])
                        + ("..." if len(self.gains) > 3 else ""), self.path, self.path))
        return ("      REMEDY: this copy supplies NO name HEAD lacks -- it is a rival copy HEAD "
                "supersedes,\n      and `isolate_hunks` has nothing legitimate to select. "
                "`python3 -m tools.refresh_to_head {}`\n      surveys it; `--write --slug NAME` "
                "preserves these bytes and writes HEAD's over them.".format(self.path))

    def render(self, merge: bool = False) -> str:
        """`merge=True` DROPS the per-path remedy, and that is not tidying. Both doors `remedy()`
        can name -- `--content` for holder work, `refresh_to_head` for a rival copy -- read a
        WORKING-TREE copy, and `--merge` has none and refuses both outright. On a merge the remedy
        is a property of the merge and not of the path, so `refusal_text` states it once; leaving
        this line in printed a door the tool would refuse, which is the pressure toward bypass this
        module exists to remove."""
        head = {
            PREDATES: "      your copy contains NOT ONE of the {} distinctive line(s) commit {} "
                      "added here,\n      so it was taken before that landing and this commit "
                      "reverts it:".format(len(self.detail), self.commit[:9]),
            SUBSET: "      would DELETE {} name(s) HEAD has, and adds none:".format(
                len(self.detail)),
            CLOCK: "      this file's mtime PREDATES commit {}, and your copy contains not one of "
                   "the {}\n      distinctive line(s) that commit added here -- so it was taken "
                   "before that landing\n      and this commit reverts it:".format(
                       self.commit[:9], len(self.detail)),
            PARTIAL: "      this file's mtime PREDATES commit {}, so it cannot have been built on "
                     "that\n      landing -- and it is MISSING {} of that commit's {} distinctive "
                     "line(s). The {}\n      it does carry are lines two lanes happened to write, "
                     "not evidence of the landing.\n      These are the landed lines this commit "
                     "would delete:".format(
                         self.commit[:9], len(self.detail),
                         len(self.detail) + self.carried, self.carried),
            UNPARSEABLE: "      {}".format(self.detail[0] if self.detail else "did not parse"),
        }[self.rule]
        shown = list(self.detail[:6]) if self.rule != UNPARSEABLE else []
        tail = "" if len(self.detail) <= 6 else "        (+{} more)\n".format(len(self.detail) - 6)
        remedy = "" if self.rule == UNPARSEABLE or merge else self.remedy() + "\n"
        return "  {}  [{}]\n{}\n{}{}{}".format(
            self.path, self.rule, head,
            "".join("        - {}\n".format(n[:110]) for n in shown), tail, remedy)


def taken_before(root: Path, path: str, new_text: str, commit: str) -> bool:
    """Whether the bytes in `new_text` are the file ON DISK and that file is OLDER than `commit`.

    THE SAME TWO GUARDS `clock_judge` CARRIES, lifted out so the readable leg can ask them too. An
    mtime is a fact about a file, so it says nothing about bytes supplied by `--content`; the
    identity check is what keeps this honest, and it is the only honest width."""
    try:
        if (root / path).read_text(encoding="utf-8", errors="replace") != new_text:
            return False
        mtime = (root / path).stat().st_mtime
    except OSError:
        return False
    landed = committed_at(root, commit)
    return landed is not None and landed > mtime


def judge(root: Path, path: str, head_text: str | None, new_text: str | None,
          parent: str = "HEAD") -> Loss | None:
    """The one judgement for one path. `None` on either side of the content means there is no base
    or no result -- a wholly new file is not contested, a deletion is explicit -- so neither is this
    control's business.

    TWO VOUCHES, NOT ONE, AND THE CLOCK IS WHAT PICKS BETWEEN THEM. Rule 1 asks "contains NOT ONE
    of the landing's distinctive lines", so ONE surviving line vouches the whole copy. That is
    right where the clock says nothing: a copy NEWER than the landing that carries some of it and
    edits the rest is ordinary work, and demanding all of them would refuse every honest edit to a
    line that landed. It is fail-open where the copy is OLDER than the landing, because there the
    vouch is arguing from coincidence: a file that predates a commit cannot have been derived from
    it, so a line they share is a line two lanes happened to write, and a line the copy LACKS is
    proof it does not have the landing.

    THAT WAS LIVE AND IT WAS THE FILE THIS RULE'S OWN `base_caveat` IS WRITTEN ABOUT. On this tree
    `tools/generate_value_arms_data.py` carried 1 of the 53 distinctive lines of `c3e2ba377` and
    the census graded it CLEAN, while the working copy reinstated "MEMORY IS NOT WHAT BINDS ...
    slack by 4.5x" and deleted the whole-run measurement that refuted it by 29.2x. The one survivor
    was `memory = settled_book_ceiling_customer_years()` -- a call the landing arrived at by
    DELETING an argument, which the reverting lane had independently deleted too. It is in the
    parent blob nowhere, so no "already there" filter could have taken it; only the share could.

    ALL-OR-NOTHING BOTH WAYS ROUND, AND NEITHER IS A DIAL. `any` vouches; the complement of
    "carries the landing" is "carries ALL of it", so the older-clock leg refuses on a single
    MISSING line. Measured on the live tree of 2026-09-22: 66 readable paths carry line evidence,
    the share is sharply bimodal -- 12 at exactly 0, 37 at exactly 1 -- and the older-clock leg
    newly names 5 of the 17 in between. All five are working copies whose mtime predates their own
    last landing by hours and whose diff is a net deletion, `test_year_keyed_rate_table_census.py`
    at -134 lines the largest. No threshold between the two extremes was needed and none is used."""
    if head_text is None or new_text is None or Path(path).suffix not in READABLE:
        return None
    partial: Loss | None = None
    commit = last_commit_touching(root, path, parent)
    if commit:
        distinctive = distinctive_lines(root, path, commit)
        if distinctive:
            present = {ln.strip() for ln in new_text.splitlines()}
            missing = tuple(d for d in distinctive if d not in present)
            if len(missing) == len(distinctive):
                gains = gains_over(head_text, new_text, path)
                return Loss(path, PREDATES, distinctive, commit, gains,
                            cuts_among(root, path, gains or (), parent))
            if missing and taken_before(root, path, new_text, commit):
                gains = gains_over(head_text, new_text, path)
                partial = Loss(path, PARTIAL, missing, commit, gains,
                               cuts_among(root, path, gains or (), parent),
                               by_clock=True, carried=len(distinctive) - len(missing))
    try:
        before, after = symbols(head_text, path), symbols(new_text, path)
    except Unparseable as exc:
        return Loss(path, UNPARSEABLE, (str(exc),))
    if before is None or after is None:
        return partial
    if after < before:  # STRICT subset: loses names and adds not one
        # A strict subset supplies nothing by definition, so the door is never in doubt here.
        # AND IT OUTRANKS A PARTIAL CARRY, which is why `partial` is held rather than returned.
        # Both verdicts refuse the same copy, so the choice between them is purely what the reader
        # is told: "would DELETE these 13 names" is a stronger and more actionable statement than
        # "is missing 1 of 45 lines", and `test_finding_classes.py` on the live tree is both.
        return Loss(path, SUBSET, tuple(sorted(before - after)), gains=())
    return partial


# --------------------------------------------- rule 4: predates the landing, by the file's own clock


def committed_at(root: Path, commit: str) -> int | None:
    """`commit`'s COMMITTER epoch seconds, or `None` if git will not answer.

    COMMITTER AND NOT AUTHOR, because the question is *when did these bytes appear in this
    repository* and not *when were they written*. A cherry-pick, a rebase and a `surgical_land`
    re-derivation all keep the author date of the original -- which can be days before a working
    copy that is nonetheless stale against the landing."""
    out = _git(root, "log", "-1", "--format=%ct", commit)
    text = out.stdout.strip()
    return int(text) if out.returncode == 0 and text.isdigit() else None


def clock_judge(root: Path, path: str, head_text: str | None, new_text: str | None,
                parent: str = "HEAD") -> Loss | None:
    """Rule 1's line evidence, carried to the paths rule 1 has NO READER FOR, and made safe there by
    the file's own mtime.

    THE GAP THIS OWNS, and it is not the one the direction that commissioned it named. The item said
    *nothing in the landing path asks whether the bytes are OLDER than HEAD*. That is false of
    `.py`/`.html`/`.js` and has been since 2026-09-08: measured on this tree on 2026-09-22, all five
    of the stale copies in the HDD pile that motivated the item are already refused by `judge`. What
    is true is that `violations()` skips every suffix outside `READABLE` in silence, and that is
    where the map, the knowledge layer, the simplification notes and the staging record live. On the
    same tree, `docs/design/simplifications/A49_...yaml` was a working copy that deletes the entire
    record of two landed ceiling instruments and the gating decision between them, and no control in
    this repository could see it.

    WHY THE CLOCK IS THE TRIGGER AND NOT THE VERDICT, measured rather than argued. The rule as
    commissioned -- refuse when the last commit is newer than the working copy -- fires on 47 of the
    358 tracked-modified paths on this tree, 13.1%. Nineteen of those are paths `judge` positively
    VOUCHES for: they carry the landing's own distinctive lines. The reason is structural and is
    this module's oldest recorded finding -- `surgical_land` **never writes the working tree**, by
    design, so every landing leaves every other lane's copy stale by mtime while its content is
    perfectly current. Clock-staleness is the NORMAL resting state of a shared checkout, so a clock
    verdict refuses honest work through the one legal door, which is the pressure toward bypass this
    module exists to remove. Narrow-and-armed beats wide-and-turned-off, again.

    WHY THE CLOCK IS NEEDED AT ALL, when the line evidence is already suffix-agnostic. Widening
    `READABLE` was considered when this module was written and rejected for a stated reason: a
    generated `.json` is REWRITTEN WHOLE on every publish, so "contains not one line of the last
    commit" is its ordinary operation and not a finding. The clock excludes that population BY
    CONSTRUCTION rather than by a suffix list that will rot -- a regenerated artefact has a mtime
    newer than the landing, so it never enters this rule at all. The clock is what makes the line
    evidence safe outside `READABLE`; the line evidence is what stops the clock refusing the honest
    nineteen. Neither leg is worth shipping without the other, and this is one rule, not two.

    THE BYTES MUST BE THE BYTES ON DISK. Everywhere else in this module the subject is the tree the
    commit would create, never the working tree, precisely because `surgical_land --content` supplies
    bytes that are on no disk anywhere. An mtime is a fact about a file, so it can say nothing about
    bytes that came from somewhere else -- and reading it as though it could would grade a `--content`
    landing by the clock of the file it is overwriting. So this rule asks whether the result blob IS
    the working copy, and yields no opinion when it is not. That is narrower than it could be and it
    is the only honest width.

    NO EVIDENCE IS NO OPINION, never a refusal -- the same discipline as `judge`'s `if distinctive:`
    guard. A commit whose every added line is trivial or repeated leaves nothing to ask, and a
    clock-only refusal is exactly the verdict the measurement above refuted.

    AND A PARTIAL CARRY IS NOT A VOUCH ONCE THE CLOCK HAS SPOKEN -- see `judge` for why, and for the
    file that was live. The two rules differ only in whether a symbol reader exists for the suffix,
    so they must not differ in what counts as carrying the landing. On the live tree of 2026-09-22
    this leg newly names two: `docs/data-sources/weather.md` (13 of 29) and
    `docs/observability/self_clearing_alarm_census.json` (440 of 739) -- a generated census
    regenerated BEFORE its own landing and never refreshed since, which is the population the
    `READABLE` note above says the clock excludes by construction, entering here legitimately
    because its mtime is on the wrong side of the landing."""
    if head_text is None or new_text is None or Path(path).suffix in READABLE:
        return None
    commit = last_commit_touching(root, path, parent)
    if not commit or not taken_before(root, path, new_text, commit):
        return None
    distinctive = distinctive_lines(root, path, commit)
    if not distinctive:
        return None
    present = {ln.strip() for ln in new_text.splitlines()}
    missing = tuple(d for d in distinctive if d not in present)
    if not missing:
        return None
    if len(missing) == len(distinctive):
        return Loss(path, CLOCK, distinctive, commit, by_clock=True)
    return Loss(path, PARTIAL, missing, commit, by_clock=True,
                carried=len(distinctive) - len(missing))


def adopted_from_merge(root: Path, parent: str, ref: str,
                       paths: list[str]) -> frozenset[str]:
    """The paths in `paths` a merge of `ref` into `parent` adopts WITHOUT this side losing anything:
    unchanged between `merge-base(parent, ref)` and `parent`, and changed by `ref`.

    THE PREDICATE IS ABOUT THIS SIDE'S HISTORY, NOT THE OTHER'S, and that is the whole of it. If
    this history has not touched a path since it diverged, then whatever the other history did to
    it cannot delete work of ours -- there is none to delete. Anything this side DID touch stays
    refused, which is the entire population the control was built for.

    THE OBVIOUS PREDICATE IS WRONG AND IS NOT USED HERE. "Exempt a path whose result blob equals
    the merged ref's blob" reopens the failure this repo has already paid for
    (`a_merge_that_adopts_one_sides_rewrite_silently_deletes_the_other_sides_purely_additive_work`):
    when `parent` carries names the ref does not, `result == ref` IS that deletion, so that
    predicate exempts exactly the case the control exists for.

    `--no-renames` ON PURPOSE. With rename detection on -- git's default -- a rename shows only the
    NEW path, so a file this side renamed reads as untouched at its old path and would be exempted.
    Off, both sides of a rename count as changed, and the error is toward refusing.

    NO MERGE-BASE, NO EXEMPTION. Unrelated histories have no divergence point, so nothing can be
    shown to be untouched since one, and fail-closed is the direction."""
    base = _git(root, "merge-base", parent, ref).stdout.strip()
    if not base:
        return frozenset()

    def _changed(a: str, b: str) -> set[str]:
        return {ln.strip() for ln
                in _git(root, "diff", "--no-renames", "--name-only", a, b).stdout.splitlines()
                if ln.strip()}

    ours, theirs = _changed(base, parent), _changed(base, ref)
    return frozenset(p for p in paths if p not in ours and p in theirs)


def violations(root: Path, parent: str, result: str, paths: list[str],
               allow: frozenset[str] = frozenset(),
               merge_ref: str | None = None) -> list[Loss]:
    """Every path in `paths` whose blob in `result` reverts a landing or loses names.

    Both blobs come out of git. `allow` is the declared-deletion escape hatch; an allowed path is
    dropped here and NAMED by the caller, because a silent exemption is how a control becomes a
    formality.

    `merge_ref` IS THE OTHER PARENT WHEN THIS RESULT IS A MERGE, and without it this control cannot
    tell "the other lane's landed, declared deletion" from "this lane's stale working copy" -- so
    on a merge it refused both, and the only route through was to declare the other lane's deletion
    with `--drops`, which is the guard's own attribution mechanism defeated by its own refusal
    (measured 2026-09-08, receipt `22df46614`). Passed, the merge-base predicate above exempts what
    this side never touched. Note also that every sentence of `refusal_text` is false of a merge
    unless it is told there is one: `--merge` opens no working-tree copy at all."""
    adopted = (adopted_from_merge(root, parent, merge_ref, paths)
               if merge_ref is not None else frozenset())
    out = []
    for path in sorted(set(paths)):
        if path in allow or path in adopted:
            continue
        before, after = blob_at(root, parent, path), blob_at(root, result, path)
        # `judge` owns READABLE and `clock_judge` owns everything else; each returns None outside
        # its own population, so the two can never hold a second opinion about one path.
        loss = (judge(root, path, before, after, parent=parent)
                if Path(path).suffix in READABLE
                else clock_judge(root, path, before, after, parent=parent))
        if loss is not None:
            out.append(loss)
    return out


def refusal_text(losses: list[Loss], merge_ref: str | None = None) -> str:
    """WHY THE MERGE WORDING IS ITS OWN BRANCH rather than one text hedged to cover both. The
    default text diagnoses the cause ("a pathspec stages the working-tree copy") and names the
    route out (`isolate_hunks` + `--content`). Both are FALSE of a merge: `--merge` reads no
    working-tree copy at all, and `--merge` takes no `--content` override -- so a lane refused on a
    merge was being told to do something the tool refuses. A refusal whose stated remedy does not
    exist is the pressure toward bypass this whole module was built to remove."""
    if merge_ref is not None:
        return (
            "\n[stale-copy] ❌ MERGE REFUSED -- {} path(s) THIS side has changed since the "
            "merge-base would\nlose names by adopting {}'s version.\n\nA path this side never "
            "touched since the merge-base is adopted without question -- there is\nnothing of "
            "yours to delete. These are not those: both histories changed them, so taking\nthe "
            "other side's version here deletes work of ours.\n\n{}\n"
            "  THE FIX: if git reported the path as CONFLICTED, settle it with the union bytes -- "
            "`surgical_land\n  --merge {} --resolve <path>=<file>`. If git merged it silently, "
            "the other history REWROTE what\n  this side also changed: rebase your side's hunks "
            "onto it (`isolate_hunks --survey <path>`) and\n  land them after the merge.\n\n"
            "  IF ADOPTING THE LOSS IS DELIBERATE AND YOURS, say so: `--drops <path>`. It is "
            "printed in the\n  landing output. Do NOT use it to wave through a deletion that "
            "belongs to the other history --\n  that is what this exemption is for, and a "
            "declared drop naming the wrong lane corrupts every\n  census of who deleted "
            "what.\n".format(
                len(losses), merge_ref[:9],
                "".join(loss.render(merge=True) for loss in losses), merge_ref))
    return (
        "\n[stale-copy] ❌ COMMIT REFUSED -- {} path(s) would revert work that has already "
        "landed.\n\nA pathspec stages the WORKING-TREE copy. If you opened one of these files "
        "before another\nlane landed in it, your copy is the OLD one and this commit deletes their "
        "work.\n\nTHE FIX IS PER PATH AND IS PRINTED WITH IT -- which door depends on whether YOUR "
        "copy supplies\nany name HEAD lacks, and naming one door for both shapes is what sent two "
        "lanes to a tool\nthat correctly refused them.\n\n{}\n"
        "  IF THE DELETION IS YOURS AND DELIBERATE, say so: `--drops <path>`. It is "
        "printed in the\n  landing output, because an exemption nobody can see is not an "
        "exemption, it is a hole.\n".format(
            len(losses), "".join(loss.render() for loss in losses)))


# ------------------------------------------------------------------------------------ the census


def behind_overlap(root: Path = ROOT) -> tuple[str, ...] | None:
    """The paths a behind base can actually mis-grade: census population ∩ what the trunk moved on.

    WHY THIS EXISTS, and it is `base_caveat`'s own blanket turning round and voiding readings its
    evidence vouches. A behind base inverts a verdict for ONE reason -- `last_commit_touching` and
    `blob_at` ask HEAD, so a path the trunk has landed on since reads against the older blob. That
    is a per-PATH condition, and `behind > 0` is a per-TREE one. When the commits HEAD lacks touch
    none of the paths the census is walking, every verdict below is computed against exactly the
    blob the trunk holds and the caveat is voiding nothing.

    MEASURED ON THE LIVE TREE 2026-09-22, which is why it is not a tidy-up. The class "finished work
    does not reach history" went three records ungraded -- 17, then 22, then 25 -- with each reading
    discarded as taken through a stale base. Re-run as a one-variable control (same working tree,
    base `3e4290bc0` at 4 behind against the advanced base) the count was 25 BOTH WAYS and the path
    sets were identical: those 4 commits touched 7 paths, and the census population was 453, and the
    intersection was EMPTY. The readings were comparable all along. Base sensitivity is real -- the
    same tree against a base 60 commits back reads 13, not 25 -- so the caveat keeps its full force
    exactly where the overlap says it has a subject.

    `None` IS NOT `()`. Unmeasurable overlap keeps the full-strength caveat: the empty tuple is a
    measurement saying no path is contested, and a git failure is the absence of one. Collapsing
    them would make an unreadable repo read as a vouched one, which is this repo's own recurring
    fail-open.
    """
    base = _git(root, "merge-base", "HEAD", REMOTE_BASE)
    if base.returncode != 0:
        return None
    moved = _git(root, "diff", "--name-only", base.stdout.strip(), REMOTE_BASE)
    walked = _git(root, "diff", "--name-only", "HEAD")
    if moved.returncode != 0 or walked.returncode != 0:
        return None
    population = {p for p in walked.stdout.splitlines() if p.strip()}
    return tuple(sorted(p for p in moved.stdout.splitlines() if p.strip() and p in population))


def base_caveat(root: Path = ROOT) -> str:
    """What the census owes its reader when its OWN base is not the trunk. `""` when nothing is owed.

    THE DEFECT THIS OWNS, and it is this module's own remedy turning round and pointing at a revert.
    Every verdict below is computed against `HEAD`, and `HEAD` in a shared checkout is routinely
    BEHIND `origin/main` -- seven commits behind, measured on the live tree on 2026-09-15. When it
    is, `gains_over` asks "which names does HEAD lack" and gets back names the TRUNK ALREADY HAS.
    The empty/non-empty split is which door the lane is sent through, so a stale base does not
    weaken the remedy, it INVERTS it: a copy the trunk strictly supersedes -- whose honest door is
    `refresh_to_head` -- is announced as HOLDER WORK, and the door named for holder work is
    `surgical_land --content`, which lands those bytes over the trunk. Measured that morning on
    `tools/generate_value_arms_data.py`: the census printed the 142 distinctive lines the copy
    reverts AND, three lines later, told the reader to land it.

    A STATED READING AND NOT A REFUSAL, deliberately. This module is wired into the pre-commit door;
    a refusal here reds every lane in the tree for a condition -- a behind base -- that is the normal
    resting state of a shared checkout and that no single lane's commit caused. The duty a wrong
    base creates is a duty to SAY SO where the remedy is read, which is what "fail closed, and say
    so on the surface" means when the surface is an instruction rather than a figure.

    Three answers, because `_base_state` has three and collapsing them would be the same error one
    layer down: a base that could not be READ is not a base known to be level.

    AN EQUIVALENCE, ESTABLISHED AND NOT LEFT TO THE READER (mutation run 2026-09-15). Replacing the
    `no_remote_base` early return with a fall-through does NOT red the suite, and it is an
    equivalence rather than a missing test: that dict has no `behind` key, so `.get("behind") or 0`
    is 0 and the next branch returns `""` anyway. It is kept explicit because the two states are
    different -- "no trunk to be stale against" and "level with the trunk" -- and a later reader
    adding a `behind` key to the no-remote case would otherwise get the caveat on every archive
    checkout silently. The control holds the BEHAVIOUR both ways round: mutating this branch to
    return a caveat reds it.
    """
    base, reason = _base_state(root)
    if base is None:
        return ("[stale-copy] THE BASE OF EVERY VERDICT BELOW COULD NOT BE READ: {}\n"
                "  {} exists and git would not answer, so whether HEAD is the trunk is UNKNOWN -- "
                "and\n  the REMEDY lines below name a door on the assumption that it is. Settle the "
                "base before\n  walking through any of them.".format(reason, REMOTE_BASE))
    if base.get("no_remote_base"):
        return ""
    behind = base.get("behind") or 0
    if not behind:
        return ""
    contested = behind_overlap(root)
    if contested == ():
        return ("[stale-copy] THE BASE IS BEHIND THE TRUNK AND THE READINGS BELOW STILL STAND: "
                "HEAD is\n  {} commit(s) behind {} (and {} ahead), and NOT ONE path those commits "
                "touched is\n  in the population below -- so no verdict here was computed against "
                "a blob the trunk has\n  moved on. The remedies are safe to walk. Re-check if you "
                "widen the population.".format(behind, REMOTE_BASE, base.get("ahead")))
    unknown = " (the overlap could not be measured)" if contested is None else (
        " The contested path(s): {}.".format(", ".join(contested[:6])
                                             + ("..." if len(contested) > 6 else "")))
    return ("[stale-copy] THE REMEDIES BELOW ARE COMPUTED AGAINST A BASE THE TRUNK HAS MOVED PAST: "
            "HEAD is\n  {} commit(s) behind {} (and {} ahead). Every \"supplies N name(s) HEAD "
            "lacks\"\n  reading below asks HEAD, not the trunk, so a copy the trunk ALREADY "
            "supersedes reads as\n  HOLDER WORK -- and the door that reading names, `surgical_land "
            "--content`, would land it OVER\n  the trunk. Advance the base and re-run before "
            "walking through any door named below.{}".format(
                behind, REMOTE_BASE, base.get("ahead"), unknown))


def census(root: Path = ROOT) -> tuple[list[Loss], list[str]]:
    """(losses, no_opinion) over everything the working tree changes vs HEAD."""
    changed = [p for p in _git_text(root, "diff", "--name-only", "HEAD").splitlines() if p.strip()]
    losses, no_opinion = [], []
    for path in sorted(changed):
        readable = Path(path).suffix in READABLE
        try:
            work = (root / path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            if not readable:
                no_opinion.append(path)
            continue
        loss = (judge(root, path, blob_at(root, "HEAD", path), work) if readable
                else clock_judge(root, path, blob_at(root, "HEAD", path), work))
        if loss is not None:
            losses.append(loss)
        elif not readable:
            # A CLOCK no-opinion is still a no-opinion, and it belongs in the section that says so.
            # This leg takes a BITE out of the unread population; it does not read it.
            no_opinion.append(path)
    return losses, no_opinion


# ----------------------------------------------- the OTHER half of the door: a producer about to RUN


class StaleProducer(Exception):
    """A module the publish path was about to import and run is a working copy that reverts its own
    last landing. Raised AT THE IMPORT, so the caller's step ledger records which artefact it did
    not refresh instead of refreshing it from the revert."""


def refused_to_run(paths: list[str], root: Path = ROOT) -> dict[str, Loss]:
    """The subset of `paths` this census refuses, keyed by path -- for a caller about to IMPORT and
    RUN them rather than commit them.

    THE HALF OF THE DOOR THAT WAS MISSING, and it is the same rule pointed the other way. Every
    other entry point here grades a COMMIT: `staged`, `violations`, `--at-tree`. The publisher never
    goes through any of them. It imports the WORKING-TREE copy of `tools/generate_*.py`, runs it,
    and writes `site/data/*.json` -- and those outputs carry the clock of the moment they were
    written, so `clock_judge` exempts them by construction and nothing downstream can tell a feed
    regenerated from HEAD from one regenerated from a revert. On 2026-09-22 the working copy of
    `tools/generate_value_arms_data.py` would have republished "MEMORY IS NOT WHAT BINDS ... slack
    by 4.5x" over the whole-run measurement that refuted it by 29.2x, and the only thing between
    the site and that paragraph was that nothing happened to run the generator first.

    THE SUBJECT IS THE COPY THAT WOULD RUN, so it reads the working tree and not a tree-ish. That is
    the opposite of every other reader in this module and it is deliberate: `import` resolves to the
    bytes on disk, and grading anything else here would be the `--content` mistake `taken_before`
    exists to refuse, in reverse."""
    out: dict[str, Loss] = {}
    for path in paths:
        try:
            work = (root / path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        head = blob_at(root, "HEAD", path)
        loss = (judge(root, path, head, work) if Path(path).suffix in READABLE
                else clock_judge(root, path, head, work))
        if loss is not None:
            out[path] = loss
    return out


def producer_refusal(loss: Loss) -> str:
    """The one sentence a refused producer owes its caller: WHICH path, and WHICH landing it
    predates. A refusal that names neither cannot be acted on and cannot be shown to be wrong."""
    return ("{} is a working copy that predates commit {} ({}), so regenerating from it would "
            "republish over that landing. It was NOT run and its artefact was NOT refreshed. "
            "Restore it first: `python3 -m tools.refresh_to_head {}`".format(
                loss.path, loss.commit[:9], loss.rule, loss.path))


# --------------------------------------------------------------------------- rule 3: index residue


def index_residue(root: Path = ROOT) -> list[str]:
    """Paths the INDEX would move away from HEAD that NO working copy is asking to move.

    THE DEFECT THIS OWNS, banked as `THE_SHARED_INDEX_STILL_HELD_THE_FAILED_CYCLES_PRE_LANDING_BLOBS`
    (2026-09-09). `surgical_land` builds and gates the tree the commit WOULD create; it never
    refreshes the shared index. So when a cycle fails and a later cycle lands the same paths by the
    surgical route, the shared index keeps the FAILED attempt's blobs -- indefinitely, and
    invisibly, because every working-tree reading agrees with HEAD. On the morning this was written
    the index held a `gate_authorizations.jsonl` three rows short of HEAD: a plain commit from it
    would have un-recorded a LEVEL_UP row and rebuilt the very promotion-gate refusal the lane was
    drawn to clear, with the whole tree green.

    WHY THIS IS A DIFFERENT QUESTION FROM THE CENSUS ABOVE, and not a widening of it. Rules 1 and 2
    take a WORKING COPY as their subject and ask whether it predates a landing. Their subject is a
    copy some lane is actually holding. This rule's subject is an index entry NO lane is holding --
    the working tree agrees with HEAD, so nobody is editing that path, and a staged difference can
    therefore only be a leftover. That asymmetry is the whole rule.

    THE ONE LEG, and it is deliberately one:

        the index differs from HEAD on this path, AND the bytes on disk equal HEAD's.

    KEYED TO THE PROPERTY, NOT TO THE PROXY, and the difference was measured rather than reasoned.
    The first draft did set arithmetic -- `git diff --cached` minus `git diff HEAD` -- which reads
    as the same question and is not. `git rm --cached` leaves the file UNTRACKED, and git then
    reports an untracked path as *deleted in the working tree* even though its bytes are sitting on
    disk unchanged. So the proxy scored that path as "the working tree disagrees with HEAD" and
    dropped it, which is exactly the `D ` beside `??` half-staged archive move -- a banked class
    that reds two rooms at once. Comparing HEAD's blob to `hash-object` on the disk copy asks the
    property itself and has no such blind spot. The test that caught this is
    `test_a_staged_deletion_with_the_file_still_on_disk_is_residue`.

    ABSENCE AT BOTH ENDS COUNTS AS AGREEMENT. A staged ADD of a path HEAD lacks and disk lacks is
    residue: no working copy is asking for it. Two of the five found live were pre-archive ROOT
    copies of documents HEAD already held under `done/` and `records/`, byte-identical to their
    archived twins, so committing them would have recreated the duplicate that reds the staging
    gate.

    WHY `git status` CANNOT SEE THIS, which is why it survived for as long as anyone looked. Residue
    renders as `MM` or `D `, and every lane here reads those as *"another lane has work in flight"*
    -- the one reading that makes you leave it alone. The state is indistinguishable from ordinary
    concurrency at a glance, and only the direction of the cached diff tells them apart.

    WHAT IT DOES NOT FLAG, stated so a green result is not read as stronger than it is:

      * a lane's real staged work -- staged AND on disk, so it is in both sets and cancels;
      * a genuine archive move (`git mv`) -- the root path is gone from disk as well as from the
        index, so the working tree does NOT agree with HEAD and the path is out of scope;
      * a rewrite by a lane that has already pulled the landing. That is rules 1 and 2's blind spot
        and it is still theirs.

    THE VERDICT IS A PHOTOGRAPH, not a standing fact: a path leaves this set the moment a lane
    starts genuinely editing it. That is correct rather than a weakness -- once a working copy
    exists the question becomes rule 1's -- but it means a stale answer must never be re-read as a
    current one. Measured twice four minutes apart on the shared tree while another lane's commit
    held the index lock, two paths left the set exactly this way.

    THE REPAIR IS `git reset HEAD -- <paths>`: path-limited and mixed, so it rewrites only those
    index entries to their HEAD blobs and does not touch the working tree. Never `git checkout` and
    never `git stash` -- both overwrite the working tree, which here is the only copy that is
    CORRECT."""
    staged = {p for p in _git_text(root, "diff", "--cached", "--name-only").splitlines() if p.strip()}
    residue = []
    for path in sorted(staged):
        head = _git(root, "rev-parse", "HEAD:{}".format(path))
        head_oid = head.stdout.strip() if head.returncode == 0 else None
        # `--path` so any clean filter git would apply is applied here too, and the two oids stay
        # comparable on a repo that gains a `.gitattributes` later.
        disk = _git(root, "hash-object", "--path", path, "--", str(root / path))
        disk_oid = disk.stdout.strip() if disk.returncode == 0 else None
        if head_oid == disk_oid:
            residue.append(path)
    return residue


def index_residue_text(paths: list[str]) -> str:
    """The refusal, naming its reason and the exact repair -- a refusal that says why is how you
    discover the refusal itself was wrong."""
    if not paths:
        return "[index-residue] none: every staged path is a path some working copy is asking for."
    return "\n".join([
        "[index-residue] {} path(s) the INDEX would move away from HEAD that NO working copy asks "
        "for.".format(len(paths)),
        "  These are a failed cycle's staging, frozen. A plain commit taken from this index reverts",
        "  HEAD on each of them while every working-tree check stays green.",
        "",
        *("  {}".format(p) for p in paths),
        "",
        "  REPAIR (path-limited, mixed -- does not touch the working tree):",
        "    git reset HEAD -- {}".format(" ".join(paths)),
        "",
        "  BUT CHECK FOR A TWIN FIRST on any path staged as a DELETION that is still on disk.",
        "  Two paths identical in `git status` take OPPOSITE doors, and only a twin tells them",
        "  apart: if an archived copy already exists under done/ or records/, the staged deletion",
        "  is a half-finished archive MOVE and the completion is to remove the root copy from disk",
        "  and land the move -- resetting abandons a move another lane correctly started. With no",
        "  twin anywhere, the same staged deletion would delete the document outright and reset is",
        "  the only correct door.",
    ])


#: The key `door_verdicts` returns its own failure under. NOT a path, and it cannot become one: a
#: git path is relative, never absolute, and `\0` is the one byte a filename may not contain -- so
#: no census row can ever collide with it and be silently rendered as the caveat, or vice versa.
#: In a mapping keyed by path, the alternative was a second return value every caller must
#: remember to check, and the caller that forgets gets today's silence back.
UNGRADED_DOORS = "\0ungraded-doors"


def door_verdicts(losses: list[Loss], root: Path = ROOT) -> dict[str, str]:
    """Ask each named door whether it would actually TAKE the path this census sends it.

    THE FINDING THIS EXISTS FOR IS A REMEDY THAT REFUSED. Naming a door is a claim, and the claim
    was wrong for two of eight copies for as long as anybody looked. So the census now runs the
    door it names: `refresh_to_head.judge_copy` for every path whose remedy names that tool
    (`Loss.names_the_refresh_door` -- and read its note, because scoping this to `is_rival` alone
    is the defect it was built from), and `landing_pair` for one that carries holder work --
    because that copy's isolated hunks may
    reference a name only another lane's UNCOMMITTED file supplies, which lands red for every lane
    and is invisible to the path-by-path route that sent you.

    IMPORTED HERE AND NOT AT MODULE SCOPE, and the reason is a real cycle rather than taste:
    `tools/refresh_to_head.py` imports this module's `judge`, `symbols` and `READABLE` -- it is
    this control's writing half and takes its definition of a stale copy from here. The census is
    the only caller in the other direction.

    AND A CENSUS THAT CANNOT IMPORT ITS OWN SIBLINGS SAYS SO RATHER THAN RAISING (2026-09-08, filed
    as `SEAT_FINDING_THE_STALE_COPY_CENSUS_CRASHES_IN_THE_SHARED_TREE_BECAUSE_ITS_OWN_SIBLING_
    MODULES_NEVER_REACHED_DISK`). The composition that did it: a lane landed `landing_pair` and
    `refresh_to_head` to origin through `surgical_land`, which NEVER writes the working tree --
    deliberately, and that is the property that makes it safe for a two-lane file; the shared tree
    then could not fast-forward, because three unrelated lanes held live bytes; so this module sat
    on disk importing two siblings the same tree had never received, and `--census` raised
    `ImportError` for EVERY lane. Every step is another lane's correct behaviour and no single
    control can see the composition -- which is exactly why the degradation has to be here, at the
    one frame that knows the siblings are optional to the ANSWER and not to the crash.

    THE PATHS ARE STILL THE ANSWER. Door grading is an enrichment of a verdict this function's
    caller already has; losing it costs the reader a column, and raising cost every lane the whole
    table. `fail closed, and say so on the surface`: the reason goes in the returned mapping under
    a key no path can collide with, so it renders beside the rows rather than in a log nobody
    reads, and the census never silently reports "no door is shut" because it could not ask.
    """
    try:
        from tools import landing_pair, refresh_to_head  # deferred: see the docstring
    except ImportError as e:
        return {UNGRADED_DOORS: (
            "      ⚠ DOORS NOT GRADED -- this census could not import its own siblings ({}). The "
            "paths above are the answer; the door column is MISSING, not clean.\n"
            "      The usual cause is that they landed to origin and this tree has not "
            "fast-forwarded (`python3 -m background.origin_reconcile --check`), so they are on no "
            "branch this checkout has.\n"
            "      THE MOVE THAT NEEDS NO FAST-FORWARD: run origin's code against this tree --\n"
            "      `git worktree add --detach /tmp/wt origin/main && cd /tmp/wt && python3 -m "
            "tools.stale_copy_refusal --census --root {}`\n"
            "      `--root` names the repository holding the rival copies and is independent of "
            "which checkout supplies the code.".format(e, root))}

    out: dict[str, str] = {}
    index = None
    for loss in losses:
        if loss.names_the_refresh_door:
            verdict = refresh_to_head.judge_copy(root, loss.path)
            out[loss.path] = (
                "      the door this refusal names IS OPEN: {}".format(verdict.state)
                if verdict.state == refresh_to_head.REFRESHABLE else
                "      ⚠ THE DOOR THIS REFUSAL NAMES IS SHUT [{}]: {}".format(
                    verdict.state, verdict.reason.split(".")[0]))
        elif loss.gains and Path(loss.path).suffix == ".py":
            if index is None:
                index = landing_pair.index_tree(root, "HEAD")
            try:
                work = (root / loss.path).read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            pairs = landing_pair.pairs_for(work, loss.path, index, root)
            if pairs:
                out[loss.path] = "\n".join(p.render() for p in pairs)
    return out


# --------------------------------------------------------------------------- the pre-commit door

#: Set by `tools/surgical_land.py` to the sha of the tree it has ALREADY judged, and read by
#: `--staged` running inside that tool's extract. It is the TREE and not a boolean for the reason
#: an allowlist row is never a name: a token that says "trust me" is a bypass, while a token that
#: says "the check already ran on exactly THIS tree" is a claim `--staged` re-derives for itself
#: and discards when it does not hold.
ALREADY_GATED_ENV = "STALE_COPY_ALREADY_GATED_TREE"


def staged(root: Path = ROOT, env: dict | None = None) -> tuple[int, str]:
    """Judge the tree a `git commit` from this index WOULD create. Returns (rc, what to print).

    THE HOLE THIS CLOSES, and it is the commoner half. Until 2026-09-08 this control was reachable
    only from `tools/surgical_land.py`, so it guarded the careful door and left the cheap one open:
    `CLAUDE.md` tells every lane to commit by pathspec, a pathspec stages the WORKING-TREE copy,
    and a plain `git commit -- <path>` reverted a landing with nothing anywhere able to notice. The
    eight copies the census found on the shared tree are what an unguarded cheap door costs.

    THE SUBJECT IS `git write-tree`, NOT THE WORKING TREE. During a pre-commit hook the index IS
    the resulting tree, so writing it out gives the same subject `surgical_land` builds by hand --
    which is what makes a partial commit judged on the half being committed rather than the half
    on disk. A working-tree read here would judge a file the commit is not making.

    FAIL-CLOSED ON AN UNWRITEABLE INDEX and open on NO HEAD. They are different states: an index
    that will not write out is a check that could not run (R15: an unavailable check is a failed
    check), while a repo with no HEAD has no landing to revert and nothing to be stale against.

    THE SKIP IS NOT FAIL-OPEN, and the argument is that it is PAIRED rather than trusted.
    `surgical_land._land_once` calls `violations()` on (parent, result_tree, files) BEFORE it
    materialises the extract and refuses on the result, so by the time the hook runs in there the
    identical question has been answered on the identical tree -- with the `--drops` exemptions the
    hook cannot see. Re-asking it would not add a check; it would silently DELETE the escape hatch,
    refusing a declared deletion at the only legal landing door. So the skip is keyed to the tree
    sha, re-derived here: a token naming any other tree is ignored and the check runs.

    AND THE HOOK CHAIN MOVES THE INDEX OUT FROM UNDER THAT TOKEN, which is the wedge this leg
    exists to close (measured 2026-09-21 on a 7-behind/9-ahead fork, eleven consecutive
    `commit_did_not_land` refusals and 36 hours with nothing published). The FIRST block of
    `tools/git-hooks/pre-commit` re-stamps `docs/status/LATEST.md` and `git add`s it whenever that
    path is staged -- so on any landing carrying LATEST.md the index the hook writes out is NOT the
    tree `surgical_land` judged, the sha comparison above fails, and the whole question is re-asked
    with none of the caller's context. On a MERGE that is not a stricter check, it is a WRONG one:
    `violations(merge_ref=...)` had already exempted 46 paths this side never touched since the
    merge-base, and the bare re-ask reads origin's own landed deletions
    (`count_run_history_total`, `DOCS_SHADOW`, `SITE_SHADOW`) as this lane reverting them. The
    printed remedy is then `refresh_to_head`, which refreshes to the HEAD that is itself behind --
    a closed loop, and the reason the fork could not be closed by either door.

    SO THE DELTA IS RE-ASKED, NOT THE WHOLE TREE, and the delta is exactly what no caller judged:
    the paths that differ between the tree the token names and the tree the index now writes out.
    Everything else has a verdict from a caller that knew the merge ref and the `--drops`. This
    does not widen the trust the token already carries -- a token naming a tree far from the result
    makes the delta the whole staged set, so the only way to shrink what is re-asked is to name
    very nearly the tree being committed, which is the claim the pairing rests on anyway. A token
    that does not resolve to a tree in this repo buys nothing and the full check runs.
    """
    env = os.environ if env is None else env
    if _git(root, "rev-parse", "--verify", "HEAD").returncode != 0:
        return 0, "[stale-copy] no HEAD yet -- a first commit reverts no landing."
    written = _git(root, "write-tree")
    if written.returncode != 0:
        return 1, ("[stale-copy] ❌ COMMIT REFUSED -- the index would not write out as a tree, so "
                   "the check could NOT RUN and an unavailable check is a failed one:\n  {}".format(
                       written.stderr.strip()[-300:]))
    result = written.stdout.strip()
    token = env.get(ALREADY_GATED_ENV) or ""
    if token == result:
        return 0, ("[stale-copy] already judged on this exact tree ({}) by tools/surgical_land.py, "
                   "which knows this landing's --drops; not re-asking.".format(result[:9]))
    # THE TOKEN MUST NAME A TREE OBJECT IN THIS REPO, and be that tree rather than a commit whose
    # tree it is. Anything else is a claim about a tree nobody here can look at, and it is ignored.
    resolved = _git(root, "rev-parse", "--verify", "--quiet", "{}^{{tree}}".format(token)
                    ).stdout.strip() if token else ""
    if resolved and resolved == token:
        moved = [ln.strip() for ln in _git(
            root, "diff-tree", "-r", "--name-only", token, result).stdout.splitlines()
            if ln.strip()]
        losses = violations(root, "HEAD", result, moved)
        if losses:
            return 1, refusal_text(losses)
        return 0, ("[stale-copy] judged on {} by tools/surgical_land.py, which knows this landing's "
                   "--drops; the hook chain has re-staged {} path(s) since, and THOSE were asked "
                   "here: {} -- none reverts a landing.".format(
                       token[:9], len(moved), ", ".join(moved[:4]) or "none"))
    changed = [ln.strip() for ln in _git(
        root, "diff-tree", "-r", "--name-only", "HEAD", result).stdout.splitlines() if ln.strip()]
    losses = violations(root, "HEAD", result, changed)
    if losses:
        return 1, refusal_text(losses)
    return 0, "[stale-copy] {} staged path(s) -- none reverts a landing.".format(len(changed))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--census", action="store_true", help="working tree vs HEAD")
    ap.add_argument("--staged", action="store_true",
                    help="judge the tree this index would commit (the pre-commit hook's door)")
    ap.add_argument("--index-residue", action="store_true",
                    help="index entries no working copy asks for (a failed cycle's frozen staging)")
    ap.add_argument("--at-tree", metavar="TREEISH", help="the tree the commit would create")
    ap.add_argument("--since-tree", metavar="TREEISH", default="HEAD")
    ap.add_argument("--root", default=str(ROOT), help="repository to judge (default: this one)")
    args = ap.parse_args(argv)
    root = Path(args.root)

    if args.index_residue:
        residue = index_residue(root)
        print(index_residue_text(residue))
        return 1 if residue else 0

    if args.staged:
        rc, text = staged(root)
        print(text)
        return rc

    if args.at_tree:
        changed = [ln.strip() for ln in _git_text(
            root, "diff-tree", "-r", "--name-only", args.since_tree, args.at_tree).splitlines()
            if ln.strip()]
        losses = violations(root, args.since_tree, args.at_tree, changed)
        if losses:
            print(refusal_text(losses))
            return 1
        return 0

    losses, no_opinion = census(root)
    verdicts = door_verdicts(losses, root)
    # AHEAD of the findings, not appended after them: the thing a stale base corrupts is the REMEDY
    # line under each path, and a caveat printed below several hundred lines of census is a caveat
    # nobody reads before acting on the first one.
    caveat = base_caveat(root)
    if caveat:
        print(caveat + "\n")
    # SAME PLACE AND SAME REASON as the base caveat above: a missing door column changes how every
    # REMEDY line below should be read, and a note printed after several hundred census lines is a
    # note nobody reads before acting on the first one.
    if UNGRADED_DOORS in verdicts:
        print(verdicts[UNGRADED_DOORS] + "\n")
    print("[stale-copy] WOULD REVERT A LANDING: {}".format(len(losses)))
    for loss in losses:
        print(loss.render(), end="")
        if loss.path in verdicts:
            print("{}".format(verdicts[loss.path]))
        print()
    print("\n[stale-copy] NO OPINION (no reader for this suffix -- NOT a clean verdict): {}".format(
        len(no_opinion)))
    for path in no_opinion[:15]:
        print("  {}".format(path))
    return 1 if losses else 0


if __name__ == "__main__":  # pragma: no cover -- entry point
    raise SystemExit(main())
