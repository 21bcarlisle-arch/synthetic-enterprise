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
import difflib
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

#: Suffixes whose document unit is the LINE, read for the same reason `DATA_SUFFIXES` is and kept
#: out of `READABLE` for the same reason too. These are the map, the knowledge layer, the
#: simplification notes and the staging record -- the population `clock_judge` was built to reach,
#: and the one population the 2026-09-22 door-grading repair did not close. That repair built a
#: GRADER for a mis-named door and left the door shut: measured on the shared tree 2026-09-23,
#: 7 of 18 census rows named `refresh_to_head` and got `refused_no_reader` back, which it answers
#: for these suffixes BY CONSTRUCTION and can never answer anything else. An honest refusal that
#: refuses everything is still a door nobody can walk through.
#:
#: THE UNIT IS THE LINE AND NOT THE LEAF, including for YAML, which `_json_leaves` could parse.
#: A leaf reading says two documents differ when a VALUE changed; a line reading says so when any
#: non-trivial line did. For prose the line is what a reader recognises as "mine" and what
#: `isolate_hunks --survey` selects over, so it is the unit a remedy can be stated in. It is also
#: the conservative direction: a reformat reads as content, so the copy is REFUSED rather than
#: waved through, and a reformat is not a thing prose does without a person doing it.
PROSE_SUFFIXES = (".md", ".yaml", ".yml")

#: A prose line short enough that its presence in two documents is coincidence rather than
#: evidence. The same floor `_trivial` uses, by the same argument -- stated once and shared so the
#: two readings of "this line carries nothing" cannot drift apart.
PROSE_LINE_FLOOR = 12


def prose_lines(text: str) -> frozenset[str]:
    """The non-trivial stripped lines of a prose document -- its `symbols()`.

    NO COMMENT FILTER, AND THAT IS THE DIFFERENCE FROM `_trivial` BESIDE IT. `_trivial` drops a
    line beginning `#` because in Python source a comment is commentary. In Markdown `#` is a
    HEADING and in YAML it is the only place a row's reasoning lives, so reusing that filter here
    would drop precisely the lines that carry the document's structure -- `## What is still owed`
    is 19 characters, it is one of the four lines a live census row supplies over HEAD, and a
    filter that took it would have emptied the evidence for that row and read the copy as clean.
    Filtering to nothing is a silent fail-open; see `distinctive_lines` for the same trap costing
    the suite.

    A FROZENSET AND NOT A LIST, so a line moved within a document is not read as content gained
    and lost. Order in prose is real, but this reader's whole question is whether the copy HOLDS
    something the base does not, and a re-ordering holds nothing new."""
    return frozenset(s for s in (ln.strip() for ln in text.splitlines())
                     if len(s) >= PROSE_LINE_FLOOR)


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
#: The clock was asked and COULD NOT ANSWER -- a git call its verdict rests on failed. Its own
#: rule, never folded into "no complaint": see `ClockUnanswered`.
UNANSWERED = "clock_could_not_answer"
#: Rule 1b: the copy carries the landing's CODE and has dropped the whole COMMENT BLOCK that landing
#: wrote -- the one loss no other rule in this module can see. See `reverted_comment_block`.
REVERTS_COMMENT = "reverts_a_landed_comment_block"
#: Rule 2's KEY-LEVEL half: the copy drops declared string keys the base binds and adds none, while
#: `symbols()` calls the two sides equal. See `declared_key_delta` -- one population, both
#: directions, so the reading that REFUSES a refresh and the reading that names a LOSS cannot drift.
KEY_SUBSET = "strict_declared_key_subset"


#: THE ONLY RULES THAT LICENSE `refresh_to_head --base-wins`, and the point is that the CLOCK returned them rather
#: than the operator. Both say the copy contains not one of its own landing's distinctive lines, so
#: it cannot have been derived from that landing -- which is what makes "these names are the older
#: draft" a measurement instead of a preference. Every other rule is excluded on purpose: `SUBSET`
#: never reaches here (a strict subset supplies nothing, so `REPLACEMENT` cannot be its verdict),
#: `PARTIAL` says the copy carries SOME of the landing and therefore may be built on it, and
#: `UNPARSEABLE` is a failed check. `None` -- no complaint at all -- is the one this must refuse
#: hardest: that is an ordinary edit, and admitting it makes the flag `git checkout <path>`.
BASE_WINS_RULES = (PREDATES, CLOCK)
#: AND THE SAME SET PLUS `PARTIAL` FOR A DOCUMENT WHOSE LINES ARE VALUES -- see `base_wins_rules`,
#: which is where the measurement that licenses the difference is written down.
BASE_WINS_DATA_RULES = BASE_WINS_RULES + (PARTIAL,)
def base_wins_rules(path: str) -> tuple[str, ...]:
    """Which clock verdicts license `--base-wins` on THIS path. `PARTIAL` is admitted for a data
    document and refused for code, and the difference is measured rather than argued.

    WHAT `PARTIAL` CLAIMS, AND WHY IT IS ONLY TRUE OF CODE. The verdict says the copy is older than
    its own last landing AND carries some of that landing's distinctive lines, and `BASE_WINS_RULES`
    excludes it because carrying some of the landing means the copy *may be built on it*. That is an
    argument about DERIVATION, and it holds only where a shared line is unlikely to arise any other
    way. For a `.py` a distinctive line is a STATEMENT and two lanes writing the same non-trivial
    statement independently is rare. For a generated `.json` a line is a KEY AND ITS VALUE, and two
    runs of one report share a line **whenever the figure did not move** -- which is arithmetic, not
    derivation.

    MEASURED 2026-09-23, pre-registered in `SEAT_PREREGISTRATION_WHETHER_A_CARRIED_LINE_IS_EVIDENCE_
    OF_DERIVATION_FOR_A_DATA_ARTEFACT_2026-09-23`. The coincidence rate of a line class = the share
    of one document's non-trivial, within-document-unique lines that also appear in a second
    document provably in NO derivation relation with it (a sibling report from the same generator
    over different inputs). Data arm 20.6% and 24.9%; `.py` control arm 0.3%-6.3% over four unrelated
    module pairs. And on the two live copies this was commissioned for, directly rather than by
    population: `ladder_churn_factors.json` carries 57 of its landing's 864 distinctive lines and
    **57 of those 57** appear verbatim in a sibling report that cannot have been derived from that
    landing; `ladder_churn_factors_svt_segment_decisions.json` carries 1060 of 4187 and 1032 of them
    do. The carry is coincidence, measured on the files themselves.

    THE CLOCK GUARD IS UNTOUCHED AND IS WHAT KEEPS THIS HONEST. `clock_judge` reaches `PARTIAL` only
    through `taken_before`, which requires the result blob to BE the file on disk and that file's
    mtime to predate the landing commit. Widening here does not admit one copy the clock has not
    already called older than the landing it would revert; it stops a coincidental line-share
    vouching for a document where the share means nothing. The leaf-level question -- what this copy
    supplies and drops -- is asked separately and in the document's own terms by `_json_leaf_names`,
    and it is unchanged.

    THE ORDERING THIS EXPOSES, which is the reason it reads better than it looked. `PREDATES`
    (carries ZERO of the landing) is admitted and always was; `PARTIAL` (carries a handful by
    coincidence) was refused. So the data copy sharing NOTHING with the landing was discardable and
    the one sharing 6.6% was protected -- and if the share is coincidence those are the same copy in
    two states, split by noise. Fixing it makes the door's behaviour monotone in the evidence."""
    return BASE_WINS_DATA_RULES if Path(path).suffix in DATA_SUFFIXES else BASE_WINS_RULES


class Unparseable(Exception):
    """The blob would not parse. FAIL-CLOSED: an unavailable check is a failed check, and a `.py`
    blob that will not parse is a finding in its own right, never a skip."""


class ClockUnanswered(Exception):
    """A git call THIS VERDICT RESTS ON failed, so the clock has no answer -- which is a THIRD
    state, and until 2026-09-23 it was folded into the second and read as the flattering one.

    THE DEFECT THIS OWNS. `_git` is `check=False` everywhere in this module and that default is
    right where it was chosen: absence is the ORDINARY answer at both ends of `blob_at`, and a
    non-zero rc from `git show` is how a tree says "no such path". The cost was paid one function
    further up, where a FAILING git call prints nothing on stdout and every reader turned "nothing"
    into the same falsy value a real negative produces:

      * `last_commit_touching` -> `None`, which also means *no commit has ever touched this path*;
      * `committed_at`         -> `None`, DECLARED as "git will not answer" and indistinguishable
                                  from a `%ct` that came back unparseable;
      * `distinctive_lines`    -> `()`, which also means *this landing added no evidence*.

    All three collapse into `clock_judge`'s single bare `None`, `judge`'s single bare `None`, and
    `refresh_to_head.judge_copy` reads that `None` as NO COMPLAINT -- then prints a CONTENT verdict
    with a clause saying the clock has no objection to the copy.

    THAT WAS LIVE AND IT CHANGED OPERATOR BEHAVIOUR (2026-09-22, the hand-off this exists for). The
    base-wins door refused the same enactment twice, HEAD stable either side and the files
    byte-identical, naming `isolate_hunks --keep N` at a regenerated data artefact -- the one door
    that cannot help. The seat could not attribute those two refusals and did not pretend to. What
    a control DID establish is that `committed_at`'s declared `None` and `distinctive_lines`'
    silent `()` both produce output byte-identical to what was seen, so the cause was not merely
    unknown, it was UNKNOWABLE FROM THE OUTPUT. One deliberate invocation became a volley of three,
    which is why the permanent preservation ref from that stretch is named `probe-a`.

    Fail-closed on bytes, fail-SILENT on cause, on a door whose whole job is discarding bytes.

    SO THE CAUSE IS CARRIED, NOT INFERRED. Every git call the clock's verdict rests on now goes
    through `_git_answer`, which raises this with the argv and the stderr that failed, and the
    three-answer shape is `Opinion`. `judge` and `clock_judge` keep their two-answer signatures and
    let this PROPAGATE rather than catching it, so no existing caller silently acquires a third
    state it does not handle -- `violations()` renders it as rule `UNANSWERED` and
    `refresh_to_head.judge_copy` as its own refusal.

    WHAT THIS IS NOT. It is not a claim that the two live refusals had this cause -- that remains
    unattributed, and a prediction filed after the answer is not a prediction. It is the narrower
    and checkable claim that the OUTPUT could not have told you either way, and now can.
    """


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True,
                          check=False)


def _git_answer(root: Path, *args: str) -> str:
    """`git args`' stdout -- or `ClockUnanswered`, NEVER an empty string standing in for a failure.

    THE EXCEPTION TYPE IS THE WHOLE DIFFERENCE from `_git_text` beside it, and it is not tidying.
    `RuntimeError` says *this tool is broken*; a caller that sees one has nothing to print but a
    traceback. `ClockUnanswered` says *the QUESTION is unanswered*, which is a verdict a door can
    render, a reader can act on, and a re-run can clear. The same failure, told apart by what the
    receiver can do about it.

    THE ARGV GOES IN THE MESSAGE IN FULL, not `args[:2]`. `_git_text`'s two-word form is fine for
    "the tool is broken"; here the whole point is that the reader can RUN the failing call again
    and see the failure for themselves, and `git log` is not a call anyone can re-run.

    AND THE STDERR IS KEPT FROM THE FRONT, where `_git_text` keeps the last 300 characters. Git
    prints the CAUSE first and the consequence last: `error: unable to open loose object <sha>:
    Permission denied` / `error: Could not read <sha>` / `fatal: cannot simplify commit <sha>`.
    Tailing that keeps the sentence naming a commit nobody asked about and drops the one naming the
    object and the reason -- which is the only line anyone can act on. Caught by a leg asserting
    the cause survives, which the first draft of this failed."""
    out = _git(root, *args)
    if out.returncode != 0:
        raise ClockUnanswered("`git {}` rc={}: {}".format(
            " ".join(args)[:200], out.returncode,
            " / ".join(ln.strip() for ln in out.stderr.strip().splitlines() if ln.strip())[:240]))
    return out.stdout


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


def blob_ids(root: Path, revs: list[str]) -> list[str | None]:
    """Each `<rev>:<path>`'s object id in order, `None` where that tree has no such path.

    ONE FORK FOR THE WHOLE LIST, which is why this exists beside `blob_at` rather than being spelled
    as a loop over it. `blob_at`'s own docstring states the case for per-path: absence is ordinary
    and the subject is the handful of paths one commit stages. The subject HERE is the opposite
    shape -- one path against every stash this repository can name -- and it is asked once per path
    of a whole-tree census, so a fork per candidate multiplies out to thousands. Batching the inner
    loop and leaving the outer one alone is the cheap half of the same reasoning.

    IDS AND NOT TEXT, and that is a correctness point rather than a saving. `blob_at` returns
    `git show`'s stdout decoded strictly, and the only use this reader has is an IDENTITY test
    against a file on disk. Comparing object ids asks git's own question -- are these the same blob
    -- so a file the locale cannot decode is answered rather than raising, and any `clean` filter or
    CRLF conversion in `.gitattributes` is applied to both sides by git instead of by us."""
    if not revs:
        return []
    out = subprocess.run(["git", "cat-file", "--batch-check"], cwd=str(root), check=False,
                         capture_output=True, text=True, input="\n".join(revs) + "\n")
    if out.returncode != 0:
        raise ClockUnanswered("`git cat-file --batch-check` over {} rev(s) rc={}: {}".format(
            len(revs), out.returncode, out.stderr.strip()[:240]))
    # `<oid> <type> <size>` when it resolves, `<query> missing` when it does not -- one line per
    # input line, in order, which is what lets the caller zip this back onto its own list.
    read = [None if ln.split()[-1:] == ["missing"] else ln.split()[0]
            for ln in out.stdout.splitlines() if ln.strip()]
    if len(read) != len(revs):
        raise ClockUnanswered("`git cat-file --batch-check` answered {} of {} rev(s)".format(
            len(read), len(revs)))
    return read


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
    """The last commit in `upto` touching `path`, or `None` when NO commit ever has.

    `None` NOW MEANS ONLY THAT. It used to mean that OR "the `git log` failed", because a failing
    log prints nothing and `"" or None` is `None` either way -- and `upto` is caller-supplied, so a
    ref that does not resolve took the same exit as a brand-new file. See `ClockUnanswered`."""
    sha = _git_answer(root, "log", "-1", "--format=%H", upto, "--", path).strip()
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
    # THE REV ITSELF IS VERIFIED BEFORE ITS PARENTAGE IS, and that ordering is the repair rather
    # than a nicety. `rev-parse --verify <commit>^` fails with the same rc for "this is a ROOT
    # commit" and for "this is not a commit at all", so the `return ()` below -- which says *there
    # was no before, so there is no evidence* -- was also the answer for a sha git could not
    # resolve. That is the same collapse `ClockUnanswered` exists for, one rev deeper: an honest
    # "no evidence" and an unasked question sharing an exit.
    _git_answer(root, "rev-parse", "--verify", "{}^{{commit}}".format(commit))
    parent = _git(root, "rev-parse", "--verify", "{}^".format(commit))
    if parent.returncode != 0:
        # The commit that CREATED the file. There is no "before" to have landed over, and a copy
        # containing none of a file's creating commit is a file you have not got at all.
        return ()
    diff = _git_answer(root, "diff", "--unified=0", "{}^".format(commit), commit, "--", path)
    added = [ln[1:].strip() for ln in diff.splitlines()
             if ln.startswith("+") and not ln.startswith("+++")]
    version = blob_at(root, commit, path)
    if version is None and added:
        # The commit ADDED lines to this path and its own blob will not read. A commit that DELETED
        # the path legitimately has no blob here -- and adds no lines either, so it never reaches
        # this. Anything else is a read that failed, and `or ""` made the frequency table empty,
        # which drops every added line for `freq[ln] == 1` and returns the same `()` an
        # evidence-free landing does.
        raise ClockUnanswered(
            "`git show {}:{}` gave no blob for a commit that added {} line(s) to it".format(
                commit[:9], path, len(added)))
    freq = Counter(ln.strip() for ln in (version or "").splitlines())
    strong = tuple(ln for ln in added if not _trivial(ln) and freq[ln] == 1)
    if strong:
        return strong
    return tuple(ln for ln in added
                 if not _trivial(ln, comments_are_evidence=True) and freq[ln] == 1)


# --------------------------------------------- rule 1b: reverts a comment block the landing added


#: The comment openers this module reads. `*` is a continuation line inside a `/* */` block, which is
#: why it is here and not only `#`/`//`: `PAGE_SUFFIXES` are in `READABLE` and their prose is mostly
#: written that way.
_COMMENT_OPENERS = ("#", "//", "*")


def _is_comment_line(line: str) -> bool:
    """A comment line carrying enough text to identify WHICH commit wrote it.

    THE FLOOR IS `_trivial`'S OWN AND NOT A SECOND COPY OF IT. `_trivial(..., comments_are_evidence=
    True)` is exactly "the length and bracket-noise floors, without the comment exclusion" -- see its
    docstring -- so asking it here reuses the one definition of "too short to be evidence". A
    re-derived floor beside it is the one-requirement-two-implementations shape that costs this
    repository most, and the two would drift the first time either was tuned."""
    s = line.strip()
    return s.startswith(_COMMENT_OPENERS) and not _trivial(s, comments_are_evidence=True)


def _landing_hunks(diff: str) -> tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]:
    """`(removed, added)` per hunk of a `--unified=0` diff, in file order.

    PER HUNK AND NOT PER FILE, because the question rule 1b asks is about ONE block of prose and its
    replacement. At `--unified=0` there is no context line, so a hunk's added lines are exactly a
    contiguous run in the new file and its removed lines are the run they displaced -- which is what
    lets "this block" and "the prose this block superseded" be the same question. Read file-wide, a
    comment deleted in one place and an unrelated one added in another would answer it as a revert."""
    out: list[tuple[tuple[str, ...], tuple[str, ...]]] = []
    removed: list[str] = []
    added: list[str] = []
    started = False
    for line in diff.splitlines():
        if line.startswith("@@"):
            if started:
                out.append((tuple(removed), tuple(added)))
            removed, added, started = [], [], True
        elif not started or line.startswith(("---", "+++")):
            continue
        elif line.startswith("-"):
            removed.append(line[1:].strip())
        elif line.startswith("+"):
            added.append(line[1:].strip())
    if started:
        out.append((tuple(removed), tuple(added)))
    return tuple(out)


def _dict_string_keys(text: str, path: str) -> frozenset[str] | None:
    """Every STRING key bound in a dict literal anywhere in `text`, or `None` if it does not parse.

    NOT PART OF `symbols()`, DELIBERATELY. `symbols()` answers "what names does this module BIND",
    and a dict key binds nothing -- adding one to a set compared for strict subset would let a
    `{"a": 1}` written in a docstring example argue a copy supplies work. This population answers a
    different question, is consulted at exactly one site, and only ever REFUSES.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for key in node.keys:
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    out.add(key.value)
    return frozenset(out)


@dataclass(frozen=True)
class KeyDelta:
    """Which declared string keys the copy BINDS that the base does not, and which it DROPS.

    BOTH DIRECTIONS OUT OF ONE READING, which is the whole reason this is a dataclass and not two
    functions. The gain half landed alone at `19f340e65` and the loss half did not, and for a day
    the same instrument answered "no complaint" about a copy deleting two publication-whitelist
    keys while refusing a refresh on the copy that had added them. Two functions over one population
    drift the first time either is tuned; a caller that wants one direction takes one field."""
    gained: tuple[str, ...]
    dropped: tuple[str, ...]


def declared_key_delta(head_text: str, new_text: str, path: str) -> KeyDelta | None:
    """The key-level supersession term, beside `symbols()`/`gains_over`. `None` if a side will not
    parse -- which is not "no keys", for this module's usual reason.

    THE POPULATION IS DICT-LITERAL STRING KEYS AND THE WIDER ONE WAS PRICED AND REFUSED. The
    direction this was built to says a string literal in a list, a decorator and an `__all__` entry
    are the same shape as a dict key and must not each earn a clause -- and they do not: there is
    one clause here, and widening it is a change to `_dict_string_keys` alone. Widening it was
    measured rather than argued, pre-registered in `SEAT_PREREG_HOW_WIDE_IS_A_KEY_LEVEL_LOSS_TERM_
    BESIDE_THE_SYMBOL_LEVEL_ONE_2026-09-24`: adding `list`/`set`/`tuple` display elements to the
    population withdraws **10 additional `REFRESHABLE` verdicts** across the shared tree's 77 dirty
    `.py` paths of 2026-09-24, against a decision rule of 3, and the copies it newly catches are
    things like a test's expected-strings list `['os', 'p', "pathlib.Path('x')"]` -- not a
    whitelist. It buys ONE extra loss verdict for ten extra refusals. The narrow population is
    therefore the measured answer and not a first draft.

    `dropped` IS THE HALF THAT WAS OPEN, and `judge` is where it is spent. A key inside a function
    body is not a module binding, a class member or an import, so a copy that deletes one leaves
    `symbols()` returning the same set for both sides -- "supplies no name" and "deletes no name"
    are then both true of SYMBOLS and the second is false of the artefact. That was live on
    `saas/reporting/annual_report.py`, which drops `gas_shape_provider_by_customer` and
    `gas_shape_refusals` from the dict `extract_report_data` returns while `judge` returned `None`.

    NOT `symbols()`, FOR THE REASON `_dict_string_keys` STATES: a dict key binds nothing, and
    folding it into the set `gains_over` differences would let a `{"a": 1}` in a docstring example
    argue that a copy supplies work. This is a second reading over the same text, consulted
    separately, and each direction of it only ever REFUSES."""
    if Path(path).suffix not in PY_SUFFIXES:
        return KeyDelta((), ())
    before, after = _dict_string_keys(head_text, path), _dict_string_keys(new_text, path)
    if before is None or after is None:
        return None
    return KeyDelta(tuple(sorted(after - before)), tuple(sorted(before - after)))


def supplied_comment_lines(head_text: str, new_text: str) -> tuple[str, ...]:
    """The comment lines this copy holds that the base does not, in file order.

    THE GUARD THAT STOPS A KEY-LEVEL COMPLAINT BECOMING A DAEMON'S LICENCE TO OVERWRITE PROSE, and
    it is here rather than at the door because it is a statement about the bytes. `judge` returning
    ANY loss for a path is what `refresh_to_head._judge_copy` turns into `REFRESHABLE`, and
    `background.origin_reconcile` calls `refresh` on that grade WITHOUT a person -- so a verdict
    whose own words are "supplies nothing" must be true of prose too, or the leg that makes the
    control honest destroys writing on its first live application.

    IT IS NOT A HYPOTHETICAL. The copy this term was commissioned for drops two whitelist keys AND
    adds a six-line comment the base lacks, explaining why `covers_svt_route: false` is live. Graded
    `REFRESHABLE`, those six lines go to a preserved ref nothing points at.

    `_is_comment_line`'s FLOOR AND NOT A SECOND COPY OF IT -- same reason that function gives for
    reusing `_trivial`'s. A lone `# noqa` is not writing and must not wedge a refresh."""
    diff = difflib.unified_diff(head_text.splitlines(), new_text.splitlines(), n=0, lineterm="")
    return tuple(ln[1:].strip() for ln in diff
                 if ln.startswith("+") and not ln.startswith("+++")
                 and _is_comment_line(ln[1:]))


def dict_key_gains(head_text: str, new_text: str, path: str) -> tuple[str, ...] | None:
    """The dict-literal STRING KEYS this copy binds that the base does not -- `None` if unreadable.

    THE POPULATION THAT LICENSED A DESTRUCTION, and the reason it is read is a measurement and not a
    worry. Surveying all 430 dirty paths of the shared tree on 2026-09-24 produced exactly ONE
    `refreshable` grade -- `saas/reporting/annual_report.py` -- and that grade was wrong. The copy
    adds `svt_departures` and `svt_decisions` to the dict `extract_report_data` returns. That dict
    is a PUBLICATION WHITELIST: a key absent from it is not published however fully the runner
    computes it. `origin/main` carries `svt_departures` nowhere in `saas/`, and seven `tools/`
    modules already consume `svt_decisions` -- `covers_svt_route: false` is live on the site
    because the producer does not emit it. So the copy was the repair, and the door offered to
    discard it with the words "origin/main strictly supersedes it".

    IT IS INVISIBLE TO EVERY READING THAT RAN. A string key inside a function body is not a
    module-level binding, not a class member and not an import, so `symbols()` returns the same set
    for both sides and `gains_over` returns `()`. Empty is the door's licence to overwrite. Rule 1b
    cannot see it either: the lines are code, not a comment block. The clock agreed with the
    destructive reading, so nothing downstream was going to catch it.

    THE CLASS IS ALREADY PAID FOR, FOUR TIMES, IN THAT ONE DICT. Its own landed comments count them,
    and `971e3680c` -- the commit this copy partly reverts -- is called "the fourth instance of a
    class this dict already counts" in its own message. What was missing was never the knowledge; it
    was a reader that could see a whitelist as a population.

    ONE-DIRECTIONAL BY CONSTRUCTION. The caller may only turn `REFRESHABLE` into a refusal on a
    non-empty answer. It can never admit a copy, so the worst a false positive costs is a refresh
    somebody has to argue for by hand -- which is the affordable direction for a door that destroys
    bytes. `None` is not `()`, for this module's usual reason: an unparseable side establishes
    nothing, and the caller must refuse rather than read it as "no keys gained".

    ONE FIELD OF `declared_key_delta` AND NOT A SECOND READING OF THE TEXT. This kept its name and
    its caller because `refresh_to_head` asks exactly this question and its refusal quotes it; what
    changed is that the loss direction is now the other field of the same set difference in the same
    pass, so no tuning of the population can move one direction without moving the other.
    """
    delta = declared_key_delta(head_text, new_text, path)
    return None if delta is None else delta.gained


#: How many contiguous comment lines make a BLOCK. The narrowness argument rests on this: a landing
#: that adds a lone lint-suppression pragma or a one-line licence header has written nothing a reader
#: would miss, and `tests/tools/test_stale_copy_refusal.py`'s own
#: `test_the_comment_fallback_does_not_displace_code_evidence` names that churn as the reason comments
#: must not become flat evidence. MEASURED AND NOT LOAD-BEARING ON TODAY'S TREE, which is said here
#: rather than left for the reader to assume: across the 52 tracked-modified `.py` paths of
#: 2026-09-24 the fire count is 7 at EVERY floor from 1 to 6, so this guard changes no live verdict
#: and is kept for the population it is aimed at rather than for the one that happened to be there.
#: `test_a_single_landed_comment_line_is_not_a_block` is the constructed proof that it bites.
COMMENT_BLOCK_FLOOR = 2


def reverted_comment_block(root: Path, path: str, commit: str, new_text: str,
                           floor: int = COMMENT_BLOCK_FLOOR) -> tuple[str, ...]:
    """The contiguous comment BLOCK `commit` added to `path` that this copy holds NOT ONE LINE OF,
    or `()`. The narrow THIRD reading, and the whole of what rules 1, 1a, 2 and 4 cannot see.

    THE POPULATION THIS OWNS. `distinctive_lines` filters comments out of its strong set, so a copy
    that carries every code line a landing added and has dropped that landing's entire written
    explanation gives `missing == 0`; rule 1's refusal leg needs `missing == len(distinctive)` and
    its clock leg needs `missing` at all, so neither is asked. Rule 2 sees no symbol change -- prose
    declares no name. Rule 4 returns at its first line, because `.py` is in `READABLE` and therefore
    rule 1's. The copy is vouched for by construction and `refresh_to_head` printed "it deletes no
    name ... an ordinary edit", which is a positive claim about a reading nothing made.

    THE LIVE INSTANCE THIS IS WRITTEN FOR. `8d84c67b5` landed a six-line comment on
    `tests/background/test_a_swept_row_names_the_sibling_that_holds_its_windows_commit.py` saying why
    the stub in it was RED AT HEAD -- a BLOCKING finding's entire written record. A working copy
    twelve minutes older carried both of that commit's distinctive code lines and reverted the block,
    and no rule in this module could say so.

    WHY THIS AND NOT `comments_are_evidence=True` AT RULE 1's CALL SITE, which is one character. It
    was measured on the live shared tree, 52 tracked-modified `.py` paths against `origin/main`, and
    the flat flip moves exactly ONE verdict -- so on width alone the flip wins. It is refused
    anyway, for two reasons the verdict count hides:

      * The flip loads the evidence set of **42 of 51** paths with prose, and the only thing holding
        it to one verdict is that `taken_before` is true for **4**. The clock is doing all the
        narrowing, so the flip is quiet exactly while the tree's copies are fresh and noisy on 9 the
        day they are old -- which is the day this control matters. A guard whose width is bounded by
        how lucky the tree is, is not narrow; it is untested.
      * `test_the_comment_fallback_does_not_displace_code_evidence` already refuses the flip in
        terms -- "the fallback must be reachable ONLY where the strong set is empty, or it is a
        widening wearing a fallback's name" -- on the argument that comments travel with
        cherry-picks, rewraps and reverts. That control is right, and the way to honour it is to ask
        the comment question SEPARATELY rather than to delete the control that forbids mixing it in.

    This reading's own content half fires on **7 of 52**, and 2 with the clock, of which 1 already
    complains -- one net new verdict, the target, from a reading that leaves rules 1 and 2 untouched.

    TWO GUARDS MAKE IT NARROW, AND THEY ARE DIFFERENT GUARDS.
      1. **Wholesale.** `any(present)` disqualifies the block. A copy holding part of the prose is
         editing it, and an edit to a comment is not this rule's business at any age.
      2. **Not a rewrite.** Where the landing's hunk also REMOVED prose, this copy must hold ALL of
         it -- the superseded draft, back. A rewrap supplies its own third text, which is neither the
         landing's lines nor the ones it displaced, so it satisfies neither half. Where the landing
         added prose over nothing, there is no superseded draft to check and the wholesale guard is
         the whole test: a copy older than that landing which holds none of its new prose has not got
         it. Measured on the live tree, all 7 firing paths are of that second shape, so the
         revert-versus-rewrite half is NOT what makes today's count small -- said here because the
         flattering reading is that both guards are earning their keep and only one of them is.

    IT IS A FLOOR ROW IN `substring_source_scan_baseline.json`, AND `searchable()` IS THE WRONG
    REMEDY HERE -- uniquely so in this repository, which is why the reason is written at the scan site
    rather than left to the row. `tests/architecture/test_a_control_reads_python_as_code.py` offers
    two exits: route the scan through `tools/python_code_text.searchable`, or freeze the row with a
    stated reason. `searchable()` BLANKS COMMENTS -- that is its whole purpose, so that a control
    cannot mistake prose describing a thing for code doing it. THIS FUNCTION'S SUBJECT IS THAT PROSE.
    Routing it would erase the only evidence it reads and return `()` for every copy: a fail-silent
    of exactly the class that rule exists to prevent, installed by obeying the rule. The row joins
    `judge` and `clock_judge`, frozen for the same underlying cause -- the census fails closed when a
    scope's only path evidence is a SUFFIX tuple rather than a tree path -- and carries their schema
    unchanged, so a future `--freeze` cannot drop this reason the way it would drop a per-row field."""
    _git_answer(root, "rev-parse", "--verify", "{}^{{commit}}".format(commit))
    if _git(root, "rev-parse", "--verify", "{}^".format(commit)).returncode != 0:
        return ()  # the commit that CREATED the file -- no landing to have reverted
    diff = _git_answer(root, "diff", "--unified=0", "{}^".format(commit), commit, "--", path)
    version = blob_at(root, commit, path)
    if version is None:
        # The same collapse `distinctive_lines` raises for one rev deeper: a failed blob read makes
        # `freq` empty, every added line fails `freq[ln] == 1`, and the honest "no blob" returns the
        # same `()` an evidence-free landing does. A deletion commit adds no line and never gets
        # here, so anything that does is a read that failed.
        raise ClockUnanswered("`git show {}:{}` gave no blob while reading its comment blocks".format(
            commit[:9], path))
    freq = Counter(ln.strip() for ln in version.splitlines())
    present = {ln.strip() for ln in new_text.splitlines()}
    for removed, added in _landing_hunks(diff):
        block = tuple(ln for ln in added if _is_comment_line(ln) and freq[ln] == 1)
        if len(block) < floor or any(ln in present for ln in block):
            continue
        superseded = tuple(ln for ln in removed if _is_comment_line(ln))
        if superseded and not all(ln in present for ln in superseded):
            continue  # a REWRITE: neither the landing's prose nor the prose it replaced
        return block
    return ()


def unread_populations(root: Path, path: str, new_text: str, parent: str = "HEAD") -> tuple[str, ...]:
    """The evidence populations this control did NOT read for `path`, each naming why.

    A "NO COMPLAINT" IS ONLY AS HONEST AS THE LIST OF QUESTIONS BEHIND IT, and this module has now
    banked the same fail-silent three times: `committed_at`'s declared `None`, `distinctive_lines`'
    silent `()`, and -- the reason this function exists -- a whole population excluded at parse time
    and reported to the operator as an answer. `refresh_to_head` said "it deletes no name ... an
    ordinary edit" about a copy whose only loss was prose, and every word of that was true and the
    sentence was not.

    So the readings that DID NOT RUN are returned rather than assumed empty. `()` is a real claim
    here -- everything this control can read, it read -- and it is reachable: for a copy the clock
    calls older, rule 1b runs and this is empty.

    NOT A REGISTER OF ITSELF. It names populations, not rules, and it is consulted at the one site
    that makes a positive claim to an operator about to discard bytes. A second caller wanting a
    general "what did you check" list is the shape CLAUDE.md warns about; there is one."""
    if Path(path).suffix not in READABLE:
        return ()
    commit = last_commit_touching(root, path, parent)
    if not commit:
        return ()
    if not taken_before(root, path, new_text, commit):
        return ("the COMMENT BLOCK {} added here: rule 1b is gated on the file's own clock, and "
                "these bytes are NOT older than that landing -- where deleting prose that has gone "
                "stale is ordinary work, and refusing it would refuse every honest edit to a "
                "comment. So whether this copy drops that landing's written record is UNREAD, not "
                "answered.".format(commit[:9]),)
    return ()


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


def _imports_at_any_scope(body: list[ast.stmt]) -> set[str]:
    """Every name an `import` binds anywhere in the tree, function bodies included.

    WHERE AN IMPORT SITS IS A STYLE CHOICE, NOT ADDED CAPABILITY, and reading it as capability is
    how a pure revert was graded holder work. `_bound_names` answers "what does importing this
    module supply", so module scope is right for it and it must stay that way -- `symbol_landing_
    check` asks exactly that question. Rule 2 asks a different one: *does this copy supply a name
    the base lacks*, i.e. is there work here to keep. A base that imports `prc` inside each of the
    four functions that use it already HAS the name `prc`; a stale copy whose sole difference is
    spelling that import once at module scope supplies nothing, and must be graded a REPLACEMENT.

    MEASURED, and it was load-bearing on the publish path rather than latent (2026-09-24).
    `tests/background/test_publish_gate_wedge_draw.py` stood 49 insertions against 171 DELETIONS
    versus `origin/main` -- a draft from before two landings -- and was one of exactly two paths
    holding the shared checkout 33 commits behind. `gains_over` returned `('prc',)`, so `judge_copy`
    said `refused_supplies_names_head_lacks`: *"it is holder work ... land hunk(s) 1"*. Origin binds
    `prc` FOUR times, at function scope, at lines 838/1260/1282/1314. Walking that door would have
    committed a redundant module-level import and left the revert in the tree, and `--base-wins`
    excludes `SUPPLIES_NEW` on purpose, so the one copy with no real gain had no door at all.

    `cut_of` DOES NOT COVER THIS, which is why the false verdict reached the surface: it is the
    escape hatch for a name the base deleted deliberately, and it resolves the base's history
    through this same module-scope reader. Origin's history never bound `prc` at module scope, so
    `cut_of` honestly returned `None` and the copy fell through to holder work.

    IMPORTS ONLY, not every nested binding. The claim above is narrow and true of imports: an
    import's scope is placement. A local variable, or a function defined inside another, is not --
    counting those would let a base that happens to bind a matching name anywhere silence a real
    gain, and this set gates a door that DESTROYS BYTES. Genuine added work still surfaces: new
    top-level functions and methods come through `_bound_names`/`_class_members`, and the lines a
    refresh would discard are printed for the operator either way.
    """
    out: set[str] = set()
    for node in ast.walk(ast.Module(body=body, type_ignores=[])):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                # A star-import can supply anything; `_bound_names` records it as `*` and this
                # agrees rather than pretending the scope is empty.
                out.add("*" if alias.name == "*" else (alias.asname or alias.name))
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
        return frozenset(_bound_names(tree.body) | _class_members(tree.body)
                         | _imports_at_any_scope(tree.body))
    if suffix in PAGE_SUFFIXES:
        found: set[str] = set()
        for pattern in _PAGE_ANCHORS:
            found.update(pattern.findall(text))
        return frozenset(found)
    if suffix in DATA_SUFFIXES:
        return _json_leaf_names(text, path)
    if suffix in PROSE_SUFFIXES:
        return prose_lines(text)
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

        AND THE GRADER DID NOT CLOSE IT (2026-09-23, this edit). A day after that repair the same
        measurement read 7 of 18 -- the grader correctly printed "THE DOOR THIS REFUSAL NAMES IS
        SHUT" on every one of them and the remedy went on naming it. A control that only watches
        your own control is the thing CLAUDE.md says is usually not worth having; this was the
        instance. The close is upstream of here: `symbols()` reads prose, `clock_judge` reads the
        gains, and `remedy()` picks the door from the copy's content. This property shrinks to the
        rows where the door is genuinely open, and the grader above stays as the control that says
        so rather than as the repair.

        KEYED TO WHICH BRANCH `remedy()` TAKES, not to a suffix list. A suffix list here would rot
        the moment `READABLE` moves, and it would be a second implementation of the branch
        condition above it -- the one-requirement-two-implementations shape this repository pays
        for most. `is_rival` is now the ONE condition that prints the tool's name unqualified: the
        `by_clock` branches that used to reach it either supply content (and name
        `isolate_hunks`) or cannot be read at all (and name no door). If a third is ever added,
        this returns False for it and the row goes ungraded rather than mis-graded."""
        return self.is_rival

    def _cut_lines(self) -> str:
        return "".join("        - {}  <- REMOVED by {}\n".format(c.name[:90], c.commit[:9])
                       for c in self.cuts)

    def remedy(self) -> str:
        if self.rule == UNANSWERED:
            # NO DOOR IS NAMED, AND THAT IS THE POINT. Both doors this module can name are keyed to
            # evidence the clock was supposed to supply and did not, so printing either would be
            # the same guess the unanswered `None` was already making -- with the added cost that
            # one of them overwrites bytes. A refusal whose honest content is "ask again" says
            # that.
            return ("      REMEDY: none is licensed -- the clock was ASKED and could not answer, "
                    "so whether\n      this copy predates its own last landing is UNKNOWN. Re-run "
                    "the call above; if it\n      keeps failing, that is a finding about this "
                    "checkout and not about this path.")
        if self.by_clock and self.gains:
            # THE BRANCH THE SHUT DOOR USED TO TAKE, and the clock is why it is not the holder-work
            # one below. A copy whose mtime predates its own last landing CANNOT have been built on
            # it, so the lines it holds that HEAD lacks are the OLDER DRAFT of what that commit
            # replaced -- not work to land whole. `surgical_land --content` is therefore never
            # named here, where the `self.gains` branch below would name it: on a clock row that
            # door lands the revert along with the line.
            #
            # `isolate_hunks` IS NAMED BECAUSE IT REACHES PROSE, which was measured before this was
            # written rather than assumed: `--survey docs/institutional/knowledge_map.md` returns
            # 3 selectable hunks. Its `--keep` is the only door that can take one line without the
            # 32 the same copy reverts, and if the reader recognises none of them as theirs the
            # copy has nothing to keep and `--base-wins` enacts the base winning -- licensed by
            # THIS clock verdict (`BASE_WINS_RULES`) and not by anybody's word.
            # AND THE FALLBACK IS NAMED ONLY WHERE THE CLOCK LICENSES IT. `--base-wins` reads
            # `BASE_WINS_RULES`, which admits CLOCK and PREDATES and refuses PARTIAL -- a copy
            # carrying SOME of its landing may have been built on it, so nothing here may enact
            # the base winning over it. Printing the flag on a PARTIAL row would rebuild this
            # item's own defect one rule to the left: a named door that refuses by construction.
            fallback = (
                "If none are,\n      the copy has nothing to keep: `python3 -m "
                "tools.refresh_to_head --base-wins {}`.".format(self.path)
                if self.rule in base_wins_rules(self.path) else
                "If none are, this copy still\n      has NO automatic exit: it carries {} of "
                "{}'s distinctive lines, so it MAY have been\n      built on that landing and "
                "`--base-wins` refuses it. Decide it by hand.".format(
                    self.carried, self.commit[:9]))
            return ("      REMEDY: your copy is OLDER than {} and holds {} line(s)/name(s) HEAD "
                    "lacks ({}),\n      so those are the OLDER DRAFT of what that commit replaced, "
                    "NOT work built on it --\n      `surgical_land --content` would land the revert "
                    "with them. `python3 -m tools.isolate_hunks\n      --survey {}` and `--keep N` "
                    "ONLY the hunk(s) you recognise as yours. {}".format(
                        self.commit[:9], len(self.gains),
                        ", ".join(g[:48] for g in self.gains[:2])
                        + ("..." if len(self.gains) > 2 else ""), self.path, fallback))
        if self.gains is None:
            # NO DOOR IS NAMED WHERE NOTHING READ THE COPY, and that is the repair rather than a
            # loss of service. This branch used to be preceded by a `by_clock` one that named
            # `refresh_to_head` for every unreadable suffix -- a tool whose FIRST act is to answer
            # `refused_no_reader` for exactly those suffixes, so the remedy sent every reader to a
            # permanently shut door and the census's own grader printed "SHUT" beside it without
            # changing the sentence. Prose and JSON are read now; whatever is left here genuinely
            # is not, and the honest remedy is the manual survey and not a tool that overwrites
            # bytes on a guess.
            return ("      REMEDY: cannot tell which door -- this copy's content could not be read, "
                    "so\n      neither `refresh_to_head` (which will answer `refused_no_reader` "
                    "for this\n      suffix) nor `isolate_hunks` is licensed. "
                    "`git diff HEAD -- {}` is the survey;\n      decide by hand which copy "
                    "wins.".format(self.path))
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
            KEY_SUBSET: "      would DELETE {} declared string KEY(S) HEAD binds, and adds none -- "
                        "while supplying\n      no symbol either. A key inside a function body "
                        "declares no name, so `symbols()`\n      returns the same set for both "
                        "sides and rule 2 is blind to this by construction.\n      Where that dict "
                        "is a publication whitelist, the key IS the work:".format(
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
            REVERTS_COMMENT: "      this file's mtime PREDATES commit {}, and your copy holds NOT ONE "
                             "LINE of the {}-line\n      COMMENT BLOCK that commit wrote here -- while "
                             "carrying all {} of its distinctive\n      CODE line(s), which is why no "
                             "other rule here can see the loss. Prose declares\n      no symbol, so "
                             "rule 2 is blind to it by construction. These are the landed lines\n"
                             "      this copy would delete:".format(
                                 self.commit[:9], len(self.detail), self.carried),
            UNPARSEABLE: "      {}".format(self.detail[0] if self.detail else "did not parse"),
            UNANSWERED: "      the clock COULD NOT ANSWER for this path -- this call failed, so "
                        "whether your copy\n      predates its own last landing is unknown, and "
                        "unknown is not 'no complaint':\n      {}".format(
                            self.detail[0] if self.detail else "cause not recorded"),
        }[self.rule]
        shown = list(self.detail[:6]) if self.rule not in (UNPARSEABLE, UNANSWERED) else []
        tail = "" if len(self.detail) <= 6 else "        (+{} more)\n".format(len(self.detail) - 6)
        remedy = "" if self.rule == UNPARSEABLE or merge else self.remedy() + "\n"
        return "  {}  [{}]\n{}\n{}{}{}".format(
            self.path, self.rule, head,
            "".join("        - {}\n".format(n[:110]) for n in shown), tail, remedy)


#: A stash commit's subject, which git writes itself and nothing else in this repository produces:
#: `git stash` gives `WIP on <branch>: <sha> <subject>` and `git stash save "<msg>"` gives
#: `On <branch>: <msg>`. Both shapes are matched because both are stash objects and this tree holds
#: live examples of each -- ten `WIP on main:` under `refs/preserved/`, four `On main:` under
#: `refs/tags/salvage/`. THE SUBJECT IS A PRE-FILTER AND NOT THE EVIDENCE: what licenses a snapshot
#: to speak for a file is the blob identity below, so a commit that merely opens "On main:" by
#: coincidence still has to hold the exact bytes before its clock is read. The branch part is
#: `[^:]+` and not `[^ :]+` because git writes `WIP on (no branch):` from a detached HEAD, and this
#: tree's own stash reflog holds one -- a tighter pattern silently drops the population that gets
#: stashed during a rebase, which is when stashing on a shared tree happens most.
STASH_SUBJECT = re.compile(r"^(?:WIP on|On) [^:]+: ")


def stash_snapshots(root: Path) -> tuple[tuple[str, int], ...]:
    """Every stash-shaped commit this repository can still NAME, as `(sha, committer epoch)`,
    OLDEST FIRST.

    TWO SOURCES BECAUSE A STASH LIVES IN TWO PLACES AND ONLY ONE OF THEM IS A REF. `refs/stash` is
    the tip and `git reflog show refs/stash` is every entry under it, which is where a stash that
    has been pushed down by a later one still is. Neither exists at all once a stash is POPPED --
    the object goes unreachable and `git gc` will eventually take it -- so the third source is the
    ordinary ref namespace, because this repository's habit is to write `refs/preserved/<name>` at
    anything it is about to discard. That habit is what makes the repair reach the live case:
    `23e9917bc` survives its own pop only as `refs/preserved/shared-tree-stash-pop-2026-09-24`.

    A POPPED STASH NOBODY PRESERVED IS OUT OF REACH AND THAT IS STATED RATHER THAN HIDDEN. This
    reader will not find it, `taken_before` falls back to the mtime, and the verdict is exactly what
    it was before this repair -- fail-open in the same direction, no worse. `git fsck --unreachable`
    would find it and is not used: it walks the whole object store, it is asked once per path of a
    census, and it would make a control's answer depend on whether `gc` had run.

    THE REFLOG'S ABSENCE IS ORDINARY AND NOT A FAILURE, so it is read through `_git` and its
    non-zero rc discarded -- a repository that has never stashed has no `refs/stash` to show. The
    ref scan is read through `_git_answer` instead: `for-each-ref` cannot legitimately fail, so if
    it does the question is unanswered and the clock must say so rather than shrug."""
    found: dict[str, int] = {}
    # for-each-ref's escape is `%00`; git-log's (which `reflog show --format=` speaks) is `%x00`.
    rows = _git_answer(root, "for-each-ref",
                       "--format=%(objecttype)%00%(objectname)%00%(committerdate:unix)"
                       "%00%(contents:subject)").splitlines()
    reflog = _git(root, "reflog", "show", "--format=commit%x00%H%x00%ct%x00%s", "refs/stash")
    if reflog.returncode == 0:
        rows += reflog.stdout.splitlines()
    for row in rows:
        kind, _, rest = row.partition("\0")
        sha, _, rest = rest.partition("\0")
        when, _, subject = rest.partition("\0")
        if kind == "commit" and when.isdigit() and STASH_SUBJECT.match(subject):
            found[sha] = int(when)
    return tuple(sorted(found.items(), key=lambda pair: (pair[1], pair[0])))


def stashed_before(root: Path, path: str, before: int) -> int | None:
    """The committer date of the EARLIEST stash snapshot strictly older than `before` whose blob at
    `path` IS the file on disk -- or `None` when no such snapshot holds these bytes.

    WHY THIS EXISTS: AN MTIME SHARED BY HUNDREDS OF FILES IS A WRITE EVENT, NOT AN AUTHOR. A stash
    restore rewrites every file it touches and stamps them all with the instant of the restore, so
    the clock `taken_before` reads is the clock of the RESTORE and not of the content. Measured on
    the shared tree on 2026-09-24 and banked in
    `docs/staging/SEAT_FINDING_A_STASH_POP_RESTAMPED_321_FILES_AND_DEFEATED_THE_STALE_COPY_CLOCK_BY_38_SECONDS_2026-09-24.md`:
    the content was snapshotted at 14:01:09Z, `b3aa159dd` landed on origin at 14:01:53Z, the restore
    wrote 321 tracked files at 14:02:31Z -- so a draft made 44 seconds BEFORE the landing read as
    authored 38 seconds AFTER it, the older-clock leg did not fire, and no door would admit the copy.
    The honest clock for those bytes was in the object store the whole time.

    `before` IS A COST BOUND THAT CANNOT CHANGE THE VERDICT, which is why it is in the signature
    rather than applied by the caller afterwards. The only caller asks `landed > clock` and only
    reaches here when the mtime already answered no, so a snapshot at or after `landed` yields the
    same False either way; filtering first means the common case -- no stash older than the landing
    -- costs the ref scan alone and never touches the object store.

    THE EARLIEST MATCH AND NOT THE LATEST, because the question is *when can these bytes be shown to
    have existed*, and a snapshot containing them is positive evidence for that instant. A second,
    later snapshot of the SAME bytes is not evidence they were authored later -- it is evidence
    somebody stashed twice. The effect is `min(mtime, earliest snapshot)`, so this leg can only ever
    move the clock BACKWARDS and can therefore only ever ADD a complaint, never withdraw one. That
    is the direction worth being sure of: the failure this repairs is a control declining to fire.

    THE FILE ON DISK IS THE SUBJECT, so the only honest caller is one that has already established
    the bytes it is judging ARE that file. `taken_before` does exactly that, one line above, for the
    reason its own docstring gives about `--content`."""
    older = [(sha, when) for sha, when in stash_snapshots(root) if when < before]
    if not older:
        return None
    disk = _git_answer(root, "hash-object", "--", path).strip()
    held = blob_ids(root, ["{}:{}".format(sha, path) for sha, _ in older])
    return next((when for (_, when), oid in zip(older, held) if oid == disk), None)


def taken_before(root: Path, path: str, new_text: str, commit: str) -> bool:
    """Whether the bytes in `new_text` are the file ON DISK and that file is OLDER than `commit`.

    THE SAME TWO GUARDS `clock_judge` CARRIES, lifted out so the readable leg can ask them too. An
    mtime is a fact about a file, so it says nothing about bytes supplied by `--content`; the
    identity check is what keeps this honest, and it is the only honest width.

    THE `OSError` EXIT IS A MEASURED NO AND NOT AN UNANSWERED QUESTION, which is why it is still a
    bare `False` while `committed_at` below is not. Its commonest shape by far is that the path is
    not on disk at all -- a `--content` landing, a deletion, a path read out of a tree -- and that
    is precisely the case this rule declines to have an opinion about: these bytes are not the
    working copy, so no working copy's clock can speak for them. `committed_at`'s failure is the
    opposite: the question WAS this rule's to answer and git would not say, so it raises through.

    AND THE MTIME IS NOT THE ONLY CLOCK, because it is not always a clock at all. A `git stash`
    restore rewrites every file it touches with one fresh stamp, so for that population the mtime
    dates the RESTORE and says nothing about when the content was written -- see `stashed_before`
    for the live case, where it inverted the answer by 38 seconds on six paths at once. So the
    question asked here is *the earliest instant these bytes can be shown to have existed*, which
    is the mtime unless the object store can prove an earlier one. The stash leg can only move that
    instant backwards, so it can only ever ADD a complaint; it reaches exactly the copies that came
    out of a stash and not one copy some lane actually typed."""
    try:
        if (root / path).read_text(encoding="utf-8", errors="replace") != new_text:
            return False
        mtime = (root / path).stat().st_mtime
    except OSError:
        return False
    landed = committed_at(root, commit)
    return landed > mtime or stashed_before(root, path, landed) is not None


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
        # RULE 1b, AND IT IS REACHABLE ONLY WHERE RULE 1 HAS NOTHING TO SAY. `partial is None` after
        # the block above means the line evidence raised no clock complaint -- either the landing left
        # none, or this copy carries all of it -- so this can never displace a verdict rule 1 reached,
        # only speak where it was silent. The clock is asked FIRST because it is the sharper filter on
        # the measured population (4 of 51 paths against 7 of 52) and it saves the diff on the rest.
        if partial is None and taken_before(root, path, new_text, commit) \
                and (block := reverted_comment_block(root, path, commit, new_text)):
            gains = gains_over(head_text, new_text, path)
            partial = Loss(path, REVERTS_COMMENT, block, commit, gains,
                           cuts_among(root, path, gains or (), parent),
                           by_clock=True, carried=len(distinctive_lines(root, path, commit)))
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
    # RULE 2's KEY-LEVEL HALF, and it is the same sentence one population to the left: drops
    # declared keys the base binds, adds none. It is UNCONDITIONAL, exactly as `SUBSET` is and
    # unlike rule 1b -- and that is a measurement, not a symmetry argument. Pre-registered decision
    # rule: unconditional if the leg newly refuses <=5% of changed-`.py` path/commit pairs. Over the
    # last 200 commits of `origin/main`, 362 such pairs, it newly refuses **0** -- every real commit
    # that drops a key adds one, so a strict key subset is not a shape honest landings make. It is
    # also not keyed to the one file that commissioned it: 4 of the shared tree's 77 dirty `.py`
    # copies are in this state today and `judge` has no complaint about any of them.
    #
    # `after - before` EMPTY IS REQUIRED AND IS NOT REDUNDANT WITH THE BRANCH ABOVE. That branch is
    # `after < before` -- a STRICT symbol subset -- so a copy that GAINS symbols falls through to
    # here, and without this guard it would be handed a verdict whose own remedy reads "supplies NO
    # name HEAD lacks". The claim this leg makes is "supplies nothing at EITHER level and deletes
    # keys", so both levels are asked before it is made.
    #
    # AND THE PROSE GUARD IS THE THIRD LEVEL, WITHOUT WHICH THIS TERM DESTROYS WRITING. Any loss
    # here is what `refresh_to_head._judge_copy` turns into `REFRESHABLE`, and that grade is a
    # DAEMON'S -- `background.origin_reconcile` refreshes on it with no person in the loop. Measured
    # on the copy that commissioned this term: it drops two whitelist keys and adds a six-line
    # comment the base lacks, so an unguarded leg would have had a daemon overwrite the writing on
    # its first live application. A copy supplying prose is not one the base strictly supersedes,
    # and this leg says NOTHING about it -- the true statement it is owed is made where the operator
    # is, in `refresh_to_head`'s `NOT_SUPERSEDED` text, which now names the keys instead of
    # asserting "it deletes no name".
    #
    # IT OUTRANKS `partial` FOR THE REASON `SUBSET` DOES: two verdicts refusing the same copy, and
    # naming the two whitelist keys it deletes is more actionable than naming a line it is missing.
    keys = declared_key_delta(head_text, new_text, path)
    if keys is None:
        # A PROVEN EQUIVALENCE TODAY, KEPT AND SAID SO rather than left for a reader to assume it
        # bites. `symbols()` raised `Unparseable` above for any `.py` that will not parse, and
        # `declared_key_delta` answers an empty delta for every other suffix, so nothing reaching
        # here can return `None` unless the two readers disagree about one text. It is kept because
        # the alternative is falling through to `partial` -- reading "could not be told" as "no keys
        # dropped", which is the exact fail-silent `committed_at`, `distinctive_lines` and
        # `unread_populations` were each written to close. `test_an_unreadable_key_population_is_not_
        # no_keys_dropped` forces it rather than hoping for it.
        return Loss(path, UNPARSEABLE, ("{}: the declared-key population could not be read, so "
                                        "whether this copy drops a key is UNKNOWN".format(path),))
    if keys.dropped and not keys.gained and not (after - before) \
            and not supplied_comment_lines(head_text, new_text):
        return Loss(path, KEY_SUBSET, keys.dropped, gains=())
    return partial


# --------------------------------------------- rule 4: predates the landing, by the file's own clock


def committed_at(root: Path, commit: str) -> int:
    """`commit`'s COMMITTER epoch seconds. `ClockUnanswered` if git will not say.

    COMMITTER AND NOT AUTHOR, because the question is *when did these bytes appear in this
    repository* and not *when were they written*. A cherry-pick, a rebase and a `surgical_land`
    re-derivation all keep the author date of the original -- which can be days before a working
    copy that is nonetheless stale against the landing.

    THIS RETURNED `None` FOR "GIT WILL NOT ANSWER" AND THE DOCSTRING SAID SO, which is exactly why
    it is worth naming as the defect rather than filing as an oversight: the `None` was DECLARED,
    documented, and still fail-silent, because `taken_before` -- its only caller -- reads it as
    `landed is not None`, and the one thing a `False` from `taken_before` means downstream is *the
    copy is not older than the landing*. A declared "cannot tell" and a measured "no" collapse at
    the first `is not None` after them. See `ClockUnanswered`; the return type is now total, so
    there is no longer a falsy value here for a caller to misread."""
    text = _git_answer(root, "log", "-1", "--format=%ct", commit).strip()
    if not text.isdigit():
        raise ClockUnanswered("`git log -1 --format=%ct {}` returned {!r}, not an epoch".format(
            commit[:9], text[:60]))
    return int(text)


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
    # THE GAINS ARE READ WHERE A READER EXISTS, AND THAT IS WHAT DECIDES THE DOOR. `gains=None`
    # used to be unconditional here, and `remedy()`'s `by_clock` branch reads a bare `None` as
    # *nothing to keep*, so it named `refresh_to_head` -- which overwrites bytes -- for every one
    # of these rows, INCLUDING the ones holding content HEAD lacks and including the suffixes that
    # door refuses outright. `symbols()` now answers for JSON and for prose, so the copy's own
    # content decides which door is printed instead of the suffix's silence.
    #
    # `cuts_among` IS NOT ASKED OF THEM, for the reason `refresh_to_head`'s data branch states:
    # "was this name DELETED on purpose" is an argument about Python, and running it over a JSON
    # leaf or a prose line would dress a vacuous answer as a measured one. So a clock row's gains
    # carry no `cuts`, `novel` equals `gains`, and `is_rival` means exactly what it says.
    gains = gains_over(head_text, new_text, path)
    if len(missing) == len(distinctive):
        return Loss(path, CLOCK, distinctive, commit, gains, by_clock=True)
    return Loss(path, PARTIAL, missing, commit, gains, by_clock=True,
                carried=len(distinctive) - len(missing))


# ------------------------------------------ the THREE answers the two verdicts above can give
#
# `judge` and `clock_judge` each return `Loss | None`, which is two answers over three states, and
# the third has been silently taking the second's exit since both were written. `Opinion` is that
# third state given a name and a cause; `opinion()` is the only surface that produces it, so there
# is exactly one place where a failed git call becomes a verdict rather than a traceback.
#
# WHY THE TWO VERDICTS THEMSELVES ARE NOT CHANGED TO RETURN THIS. Every existing caller reads
# `Loss | None` and branches on `is None`. Widening their return type would put a THIRD value
# through code written for two, and the branch it would fall into is `is None` -- which is the
# flattering one, and the exact defect being repaired. Raising instead means a caller that has not
# been taught the third state CANNOT silently mis-read it: it gets an exception it must handle.

COMPLAINT = "complaint"
NO_COMPLAINT = "no_complaint"
COULD_NOT_ANSWER = "could_not_answer"


@dataclass(frozen=True)
class Opinion:
    """What the clock said, in three states, with the cause when it said nothing.

    `rule` IS WHAT A READER MAY BE TOLD, and the reason this property exists rather than each
    caller formatting its own is that every caller formatted the same wrong thing: `"no complaint"
    if clock is None else clock.rule`, three times in `refresh_to_head.judge_copy` alone. That
    expression is correct for two of the three states and silently wrong for the one it cannot
    see."""
    answer: str
    loss: Loss | None = None
    #: The failing git call, verbatim enough to re-run. Empty unless `answer` is COULD_NOT_ANSWER.
    cause: str = ""

    @property
    def unanswered(self) -> bool:
        return self.answer == COULD_NOT_ANSWER

    @property
    def rule(self) -> str:
        """The verdict name to print. Never "no complaint" unless the question was ASKED and
        ANSWERED -- which is the whole of this class."""
        if self.answer == COMPLAINT and self.loss is not None:
            return self.loss.rule
        return "no complaint" if self.answer == NO_COMPLAINT else UNANSWERED


def judgement_for(path: str):
    """Which of the two verdicts owns `path` -- `judge` for a suffix with a symbol reader, and
    `clock_judge` for everything else.

    THE SINGLE DISPATCH, CALLED AND NOT RE-CUT, and the reason is banked in this repository twice
    over. `violations()` has had this conditional since `clock_judge` was written;
    `refresh_to_head.judge_copy` grew a SECOND copy of it, spelled as two hard-coded call sites in
    two branches, and got it wrong in one of them -- it asked `judge` about a `.json` path, an
    oracle STRUCTURALLY unable to have a complaint about that suffix, so it agreed with every
    answer by returning `None` to all of them and shut `--base-wins` for the whole population it
    was built for. One question, one implementation."""
    return judge if Path(path).suffix in READABLE else clock_judge


def opinion(root: Path, path: str, head_text: str | None, new_text: str | None,
            parent: str = "HEAD") -> Opinion:
    """The clock's verdict on one path as THREE answers rather than two.

    THE ONLY PLACE `ClockUnanswered` IS CAUGHT. Everywhere else it propagates, so a caller that
    wants the third state has to ask for it here and a caller that has not been taught about it
    gets a traceback rather than the flattering branch. That asymmetry is deliberate: the failure
    mode being repaired is a `None` quietly meaning two things, and the repair is worth nothing if
    the new state can quietly become one of them somewhere else."""
    try:
        loss = judgement_for(path)(root, path, head_text, new_text, parent=parent)
    except ClockUnanswered as exc:
        return Opinion(COULD_NOT_ANSWER, cause=str(exc))
    return Opinion(COMPLAINT, loss) if loss is not None else Opinion(NO_COMPLAINT)


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
        # its own population, so the two can never hold a second opinion about one path. The
        # dispatch is `judgement_for`'s -- this site is where it was written and where the second
        # copy in `refresh_to_head` diverged from it.
        #
        # AND A GIT CALL THAT FAILED IS A REFUSAL HERE, not a clean path. This module's own
        # doctrine, stated for `Unparseable` and true for the same reason: an unavailable check is
        # a failed check. On a healthy repository this is unreachable -- every call `opinion()`
        # makes is either rc 0 or a `blob_at` absence that is an ANSWER -- so it costs no honest
        # commit anything; on a broken one it names the call instead of waving the path through.
        verdict = opinion(root, path, before, after, parent=parent)
        if verdict.unanswered:
            out.append(Loss(path, UNANSWERED, (verdict.cause,)))
        elif verdict.loss is not None:
            out.append(verdict.loss)
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
