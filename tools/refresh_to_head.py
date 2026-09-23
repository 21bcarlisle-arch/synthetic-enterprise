"""Write HEAD's bytes over a RIVAL working copy HEAD strictly supersedes -- preserving it first.

THE GAP THIS FILLS, and it is a gap a rule left rather than a defect anyone wrote.
`SEAT_FINDING_THE_STALE_COPY_REMEDY_HAS_NO_MOVE_FOR_A_RIVAL_COPY_HEAD_ALREADY_SUPERSEDES_2026-09-08`:
`tools/stale_copy_refusal.py` names eight working copies that would revert a landing, and its
refusal text sends each of them to `tools/isolate_hunks.py --keep N` + `surgical_land --content`.
For two of the eight that remedy has **no legal application**, and `isolate_hunks` is right to
refuse it: they supply *zero* names HEAD does not have, so every hunk in them is either the same
code reworded or a strictly weaker version of what landed. Select a hunk and you land a revert.
Select none and the tool refuses -- *"landing HEAD's own bytes back over itself is an empty change
wearing a commit's clothes"*. Both branches correct; no third one.

The repair such a copy needs is **replace these bytes with HEAD's**, and nothing in the repo did it:
`surgical_land --content` never writes the working tree (deliberately -- that is what makes it safe
for a two-lane file), and `git checkout <path>` / `git stash` are forbidden by `CLAUDE.md` *for
exactly this class's sake*, because they discard the holder's work. The prohibition is right in
general. On a copy where the holder's work is provably nil it forbade the only move that helps, and
a rule that leaves no legal move evaporates -- the same argument that produced `surgical_land`.

WHAT STOPS THIS BEING `git checkout` WITH A NICER NAME. Three things, and they are conjunctive.

  1. THE COPY MUST SUPPLY NO NAME HEAD NEVER BOUND. Computed, never asserted:
     `stale_copy_refusal.symbols` over both blobs, and a single name on the copy's side is a REFUSAL
     that names it and sends the caller to `isolate_hunks`. This is the whole of the Kind-A/Kind-B
     split, made a precondition. NEVER BOUND and not merely ABSENT, since 2026-09-16: a name HEAD
     DELETED on purpose is a re-creation, not holder work, and reading it as holder work shut this
     door against exactly the copies the census sends here -- `stale_copy_refusal.cut_of` has that
     argument in full. And since 2026-09-17, NEVER BOUND *AND ABLE TO RUN*: a name whose own body
     reaches for an attribute the base's module does not bind is a draft against a dead API, not
     work -- `stale_copy_refusal.Dead`. That class needs an explicit `--superseded`, because a lane
     writing the control before the module it grades produces the identical file.

  1b. A COPY THAT SUPPLIES REAL WORK MAY STILL HAVE NO DOOR, and saying so is the repair rather
     than a gap. When every hunk carrying a new name also deletes a name the base has, `--keep`
     has no selection and `--content` lands a revert, so neither door applies: the verdict is
     `REPLACEMENT` and the choice between two implementations of one property goes back to a
     person. `stale_copy_refusal.landable_hunks` computes it on the bytes `--keep` would build.
     THE PERSON THEN HAD ONE ANSWER THEY COULD NOT ENACT. "The copy wins" is a landing; "the base
     wins" is a discard, and nothing legal here discarded anything, so a REPLACEMENT resolved for
     the base sat in the tree permanently and the stale-copy door refused every landing over it.
     `--base-wins` is that enactment, and it is gated on the CLOCK (`base_wins_rules`) and not on
     the person, because the person's word is what `git checkout <path>` already takes.
  2. HEAD MUST ACTUALLY SUPERSEDE IT. `stale_copy_refusal.judge` must have a complaint about this
     copy. Keyed to the PROPERTY (this copy would revert a landing), not to a path anyone listed:
     without it the tool reverts any edit you point it at, which IS `git checkout`.
  3. THE BYTES MUST BE RECOVERABLE BEFORE THEY ARE DESTROYED, and the recovery route is VERIFIED
     rather than claimed -- see `preserve`. The idiom is the repo's own (`e8f3a2618 preserved
     shared-tree worktree state before ff to origin/main`, and the twenty-odd `refs/preserved/*`
     refs that hand-made version left behind); what is new is that it runs before the write, on the
     exact bytes about to go, with the `git log --all -S` lookup RUN and not merely printed.

NOT A HOOK BYPASS, said here because the shape looks like one. `CLAUDE.md`'s wall is about commits
that enter the project's history without facing the gates -- `--no-verify`, hand-built
`commit-tree` merges onto a branch. The commit this writes is on **no branch**, has HEAD as its
parent, is never merged, never pushed and never fast-forwarded to; it exists so that
`git log --all -S` has something to find. It changes no tree any lane works from. A landing still
goes through `tools/surgical_land.py` and always did.

DEFAULT IS SURVEY. `--write` is required to touch a byte, because the discarded lines are printed
first and a reader who has not seen them cannot judge the one thing this tool cannot: whether a
reworded error string was worth keeping. Symbol-set granularity is blind to a value-level edit, so
the line-level losses go on the surface rather than in a footnote.

    python3 -m tools.refresh_to_head --root /home/rich/synthetic-enterprise tools/foo.py
    python3 -m tools.refresh_to_head --root ... --write --slug kind-a-repair tools/foo.py

Exit 0 = every named path is at HEAD or was refreshed; 1 = at least one refusal.
"""
from __future__ import annotations

import argparse
import difflib
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

# REUSED rather than re-cut: the whole judgement half of this tool is `stale_copy_refusal`'s. Its
# `symbols()` is the reader that returns `None` -- not an empty set -- for a suffix it cannot read,
# which is what lets refusal 1 fail closed instead of waving an unreadable file through; its
# `judge()` is refusal 2 entire. Re-deriving either would be a second opinion about what a stale
# copy is, and two answers to that question is the defect this class already banked.
from tools.stale_copy_refusal import (
    CLOCK,
    DATA_SUFFIXES,
    PARTIAL,
    PREDATES,
    READABLE,
    Dead,
    Unparseable,
    blob_at,
    clock_judge,
    cuts_among,
    dead_among,
    json_leaf_delta,
    judge,
    landable_hunks,
    symbols,
)

ROOT = Path(__file__).resolve().parent.parent

PRESERVED_PREFIX = "refs/preserved/refresh-to-head/"

#: The verdicts. Only REFRESHABLE may be written; everything else is a refusal or a no-op, and each
#: says which because a refusal that does not name its reason is how you never discover it was wrong.
REFRESHABLE = "refreshable"
AT_HEAD = "already_at_head"
NO_BASE = "refused_no_base"
NO_READER = "refused_no_reader"
UNPARSEABLE = "refused_unparseable"
SUPPLIES_NEW = "refused_supplies_names_head_lacks"
NOT_SUPERSEDED = "refused_head_does_not_supersede_it"
#: THE STATE `SUPPLIES_NEW` WAS ABSORBING FOR EVERY DATA DOCUMENT IN THE TREE. The copy binds no key
#: path the base lacks; it disagrees with the base about the VALUE at keys they both bind. That is a
#: choice between two drafts, not work to land -- there is no hunk that takes a changed number
#: without the revert -- so `isolate_hunks`, the door `SUPPLIES_NEW` names, has nothing to select.
#: Since a leaf name carries its own value, every regenerated artefact reached `SUPPLIES_NEW` by
#: construction: same schema, every figure moved, "supplies" every leaf it holds. The class could
#: not be got out of, whichever document was genuinely newer. Splitting the state does not move the
#: refusal -- a value-level rival is still refused, and `--base-wins` still reaches it on exactly
#: the same clock evidence -- it makes the refusal TRUE, which is the precondition for anyone
#: acting on it.
RIVAL_VALUES = "refused_rival_values_no_key_the_base_lacks"
STAGED = "refused_holder_has_it_staged"
#: THE THIRD STATE THE TWO DOORS DID NOT HAVE. The copy supplies names, AND every hunk that carries
#: one also deletes a name the base has -- so `--keep` has no legal selection and `--content` lands
#: a revert, while this tool refuses because the copy does supply names. Both existing doors are
#: keyed to the same name count and both are wrong here, which is the pair the two 2026-09-08
#: findings each named half of. Naming the state IS the repair: the choice between two
#: implementations of one property is a judgement, and a refusal that says so is worth more than a
#: verdict that picks the flattering side of it.
REPLACEMENT = "refused_replacement_no_landable_hunk"
#: THE ONLY RULES THAT LICENSE `--base-wins`, and the point is that the CLOCK returned them rather
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
#: Supplies names, but NOT ONE of them can run against the base -- see `stale_copy_refusal.Dead`.
#: A refusal by default and writable only under `--superseded`, because a test-first lane looks
#: exactly like this and the difference is intent, which is not on disk.
SUPERSEDED_DEAD = "refused_supplies_only_dead_names"


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


class RefreshError(RuntimeError):
    """The move could not be completed. FAIL-CLOSED: nothing is written after this is raised."""


def _git(root: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    full = dict(os.environ, **(env or {}))
    return subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True,
                          check=False, env=full)


def _git_ok(root: Path, *args: str, env: dict | None = None) -> str:
    out = _git(root, *args, env=env)
    if out.returncode != 0:
        raise RefreshError("git {} rc={}: {}".format(
            " ".join(args[:2]), out.returncode, out.stderr.strip()[-300:]))
    return out.stdout


def _blob_bytes(root: Path, tree: str, path: str) -> bytes:
    """HEAD's bytes, read as BYTES and never as text. The working copy is about to be replaced by
    these exactly; a text round-trip would normalise line endings and land a diff nobody chose."""
    out = subprocess.run(["git", "show", "{}:{}".format(tree, path)], cwd=str(root),
                         capture_output=True, check=False)
    if out.returncode != 0:
        raise RefreshError("{} is not in HEAD at {}".format(path, root))
    return out.stdout


def _trivial(line: str) -> bool:
    s = line.strip()
    return len(s) < 12 or s.startswith(("#", "//", "*"))


@dataclass(frozen=True)
class Verdict:
    path: str
    state: str
    reason: str
    gains: tuple[str, ...] = ()       # names the copy supplies that HEAD does not
    discarded: tuple[str, ...] = ()   # lines the copy has that HEAD does not
    dead: tuple[Dead, ...] = ()       # of `gains`, the ones that cannot run against the base
    drops: tuple[str, ...] = ()       # names HEAD has that the copy does not
    #: Key paths BOTH documents bind, disagreeing about the value. NOT a subset of `gains` and
    #: deliberately not rendered with the same marker: `gains` is content the base does not hold,
    #: and reading an edited figure as one is the whole of the defect this field was cut for.
    edited: tuple[str, ...] = ()

    @property
    def refused(self) -> bool:
        return self.state not in (REFRESHABLE, AT_HEAD)

    def render(self) -> str:
        body = "  {}  [{}]\n      {}\n".format(self.path, self.state, self.reason)
        for name in self.gains[:8]:
            body += "        + {}\n".format(name[:110])
        if len(self.gains) > 8:
            body += "        (+{} more name(s))\n".format(len(self.gains) - 8)
        # THE DEAD NAMES GO ON THE SURFACE WHETHER THEY ARE ADMITTED OR REFUSED, the way
        # `surgical_land --drops` prints a deliberate deletion: this is the one fact licensing a
        # write that destroys bytes, and an exemption nobody can see is a hole.
        for gone in self.dead[:8]:
            body += "        ✗ {} -> {}.{} is bound nowhere in HEAD's copy{}\n".format(
                gone.name[:60], Path(gone.module).stem, gone.attr,
                "" if not gone.elsewhere else
                " (but {} did bind it -- `git show {}:{}`)".format(
                    gone.elsewhere[:9], gone.elsewhere[:9], gone.module))
        for name in self.edited[:8]:
            body += "        ~ {}  <- BOTH BIND THIS KEY; THE VALUE DIFFERS\n".format(name[:90])
        if len(self.edited) > 8:
            body += "        (+{} more key(s) whose value differs)\n".format(len(self.edited) - 8)
        for name in self.drops[:8]:
            body += "        - {}  <- HEAD HAS THIS AND THE COPY DOES NOT\n".format(name[:96])
        if len(self.drops) > 8:
            body += "        (+{} more landed name(s) the copy drops)\n".format(len(self.drops) - 8)
        if self.state == REFRESHABLE:
            body += "      LINES THAT WILL BE DISCARDED ({}), recoverable from the preserved " \
                    "commit:\n".format(len(self.discarded))
            for line in self.discarded[:10]:
                body += "        - {}\n".format(line[:110])
            if len(self.discarded) > 10:
                body += "        (+{} more line(s))\n".format(len(self.discarded) - 10)
        return body


def _discarded_lines(head_text: str, work_text: str) -> tuple[str, ...]:
    """Every line the working copy has and HEAD does not, in file order.

    This is what the caller is being asked to sign off, and it is LINE granularity on purpose: the
    symbol-set test that licenses the refresh is blind to a reworded error string or a changed
    constant, so the thing it cannot see is printed rather than inferred to be absent."""
    diff = difflib.unified_diff(head_text.splitlines(), work_text.splitlines(), n=0, lineterm="")
    return tuple(ln[1:].strip() for ln in diff
                 if ln.startswith("+") and not ln.startswith("+++") and ln[1:].strip())


def _staged_paths(root: Path) -> frozenset[str]:
    out = _git(root, "diff", "--cached", "--name-only")
    return frozenset(p.strip() for p in out.stdout.splitlines() if p.strip())


def judge_copy(root: Path, path: str, staged: frozenset[str] | None = None,
               base: str = "HEAD", superseded: bool = False, base_wins: bool = False) -> Verdict:
    """The whole precondition for one path. Reads; writes nothing, ever.

    `base` IS THE TREE THAT MUST SUPERSEDE THE COPY, AND IT IS NOT ALWAYS `HEAD`. On a tree that is
    BEHIND origin -- which is every tree this is called from by `background.origin_reconcile`, since
    that module has already established `ahead == 0` before it asks -- HEAD is itself a stale base,
    and `tools/stale_copy_refusal.py`'s own banner says its verdicts are unsafe there. Asking
    "does HEAD supersede this copy" of a path origin has moved since HEAD gets the wrong answer
    twice over: `last_commit_touching(..., "HEAD")` cannot see the landing that superseded the copy,
    and the symbol comparison runs against a blob that is not the one the tree is about to hold.

    `superseded` RELAXES RULE 1 BY ONE CLASS AND NOTHING ELSE. It admits a copy whose every
    supplied name is proven unable to run against `base` -- and rules 2 and 3 still apply in full,
    so the base must still have a complaint about the copy and the bytes are still preserved and
    the recovery still verified before a byte moves. It is never a default and no automated caller
    passes it: `background.origin_reconcile` requires `REFRESHABLE`, which this state is not until
    a person types the flag. See `stale_copy_refusal.Dead` for the false positive it cannot rule
    out, which is why it is a person.

    `base_wins` RELAXES ONE STATE AND ONLY WHERE THE CLOCK HAS ALREADY SPOKEN -- `REPLACEMENT`,
    the one state with no legal exit at all. `SUPPLIES_NEW` is NOT admitted by it even when the
    same clock evidence is present, and that exclusion is the whole difference between this flag
    and `git checkout <path>`: a copy with a landable hunk HAS a door (`isolate_hunks --keep N`
    then `surgical_land --content`) that takes the work without the revert, so discarding it would
    destroy recoverable work where a route existed. `REPLACEMENT` is the state where both doors are
    proven inapplicable on this copy's own bytes -- `--keep` has no selection and `--content` lands
    a revert -- so the only enactment left is discarding the copy, and before this flag there was
    none: `WORKER_RESULT_THE_THREE_CLEARABLE_REVERTS_ARE_GONE_AND_THE_TWO_LEFT_NEED_A_DOOR_THAT_
    ENACTS_THE_BASE_WINNING_2026-09-22` names two files that had sat in the shared tree wedging
    every lane that touches them, with the door working correctly and the tree stuck anyway.
    Rules 2 and 3 are unchanged in full: `judge` must still refuse the copy -- and now with a rule
    from `base_wins_rules`, which is strictly stronger than rule 2's "has a complaint" -- and the
    bytes are still preserved and the recovery still verified before one is written.

    THE WRITE IS STILL HEAD'S BYTES, AND THAT IS NOT AN INCONSISTENCY. `refresh` clears a path by
    returning it to HEAD, because what refuses a fast-forward is *worktree differs from HEAD* --
    writing origin's bytes over it leaves it differing from HEAD and the advance still refused. The
    fast-forward the caller runs next is what installs `base`'s bytes. So the question asked is
    about the tree the path is about to hold and the act is the one that lets it get there.
    """
    staged = _staged_paths(root) if staged is None else staged
    # THE ADVANCE'S DOOR READS ONE SUFFIX CLASS WIDER THAN THE COMMIT GUARD, and the asymmetry is
    # deliberate. `READABLE` gates `violations()` on every commit in a tree three lanes write, where
    # a daemon rewriting a `.json` ledger between two commits is ordinary operation. Here the
    # question is only ever asked of a path already HOLDING a fast-forward, and answering it
    # "no reader" made that path PERMANENTLY unresolvable -- which, under the all-or-nothing rule in
    # `origin_reconcile.advance_shared_tree`, is fatal to every other blocker beside it.
    if Path(path).suffix not in READABLE + DATA_SUFFIXES:
        return Verdict(path, NO_READER,
                       "this control has no reader for {} files, so it CANNOT establish that the "
                       "copy has nothing to lose. An unavailable check is a failed check.".format(
                           Path(path).suffix or "extension-less"))
    head_text = blob_at(root, base, path)
    if head_text is None:
        return Verdict(path, NO_BASE,
                       "{} has no such path, so there is nothing for it to supersede the copy "
                       "with.".format(base))
    if base != "HEAD" and blob_at(root, "HEAD", path) is None:
        # The judgement tree holds it and HEAD does not, so there are no HEAD bytes to write and
        # `preserve` -- whose tree is HEAD's with these paths swapped in -- has no entry to swap.
        # Refusing here is what stops that surfacing as a `RefreshError` mid-write.
        return Verdict(path, NO_BASE,
                       "{} holds this path and HEAD does not, so the refresh has no HEAD bytes to "
                       "write over the copy. The fast-forward adds it; nothing needs clearing "
                       "here.".format(base))
    try:
        work_text = (root / path).read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return Verdict(path, NO_BASE, "the working copy could not be read: {}".format(exc))
    if work_text == head_text:
        return Verdict(path, AT_HEAD, "identical to {} -- nothing to refresh.".format(base))
    if path in staged:
        return Verdict(path, STAGED,
                       "the holder has this path STAGED. A commit from that index makes the tree "
                       "from the INDEX copy, not the working one, so refreshing the working copy "
                       "would leave the revert armed while looking repaired.")
    try:
        head_names, work_names = symbols(head_text, path), symbols(work_text, path)
    except Unparseable as exc:
        return Verdict(path, UNPARSEABLE,
                       "{} -- an unparseable blob is a finding, never a skip.".format(exc))
    if head_names is None or work_names is None:
        return Verdict(path, NO_READER,
                       "no symbol reader for this path, so 'supplies nothing HEAD lacks' is "
                       "unestablished and the refresh is not licensed.")
    if Path(path).suffix in DATA_SUFFIXES:
        # A DATA DOCUMENT IS ANSWERED IN ITS OWN TERMS AND NOT IN PYTHON'S. `cuts_among` and
        # `dead_among` are both arguments about Python: whether the base DELETED a name on purpose,
        # and whether a name could RUN against the base's module. Neither sentence means anything
        # about a JSON leaf, and running them here would dress a vacuous answer as a measured one.
        # So the subset question is asked directly -- which is all rules 1 and 2 ever were for a
        # document whose every leaf carries its own value (see `_json_leaf_names`).
        #
        # AND THE QUESTION IS ASKED TWICE, BECAUSE IT IS TWO QUESTIONS. The set difference over
        # value-bearing names answers *are these the same document* and must stay the gate -- keyed
        # on key paths alone, a copy that rewrote every figure reads as a strict subset and the
        # refresh destroys an edit while looking checked (`_json_leaf_names` carries that argument,
        # and two legs in `test_a_json_blocker_...py` are destructive proofs of it). `json_leaf_delta`
        # answers the other one -- *what does this copy hold that the base does not* -- and until
        # 2026-09-23 nothing did. THE BRANCH BOUNDARY DOES NOT MOVE, which is why this is a repair
        # to a GRADE and not a widening of a door that destroys bytes: an edited key path
        # contributes `k=<new digest>` to `work_names - head_names`, and a novel one contributes
        # its own, so that difference is non-empty exactly when `novel or edited` is. The condition
        # below is the same partition the old `if supplies:` cut. `--base-wins` reaches precisely
        # the copies it reached before. What moves is which of the two states the copy is told it
        # is in -- and `test_base_wins_reaches_a_DATA_replacement_...` asserts that reachability
        # against the DEFAULT in one test, so a boundary that DID move reds rather than passes.
        delta = json_leaf_delta(head_text, work_text, path)
        drops = tuple(sorted(head_names - work_names))
        if delta.novel or delta.edited:
            # `--base-wins` MUST BE CONSULTED HERE TOO, AND IT WAS NOT -- so the flag was shut for
            # the whole population it was built for. This branch returned unconditionally on
            # `supplies`, several screens ABOVE the Python branch's `base_wins` consultation, so a
            # `.json` path never reached it. And a leaf name carries its own value, so a REGENERATED
            # data artefact -- same schema, every figure moved -- "supplies" every leaf it holds by
            # construction. A stale regeneration is exactly the copy `--base-wins` exists to
            # discard, and it was the one copy that could never get there.
            #
            # Measured 2026-09-23 on the three feed inputs the capabilities publisher reads:
            # `svt_drift_belief_grade.json` and the two `ladder_churn_factors*.json`. All three
            # graded `predates_landing` by the clock, all three refused here, and `--base-wins`
            # refused them byte-identically -- which is what a flag that is never read looks like.
            # The two ladder copies carry ZERO structurally novel keys; every "supplied name" is a
            # changed value of a key the base already has.
            #
            # THE CONDITION IS THE CLOCK'S, NOT THE OPERATOR'S, exactly as in the Python branch: a
            # file older than the landing it would revert cannot be carrying work built on that
            # landing. Nothing below takes the operator's word for it, and the copy is preserved on
            # a ref before any byte is written.
            #
            # AND IT ASKS `clock_judge`, NOT `judge`, WHICH IS THE SECOND HALF OF THE SAME DEFECT.
            # `judge` opens with `Path(path).suffix not in READABLE -> None`, and READABLE is
            # `.html/.js/.py`. It is STRUCTURALLY UNABLE to have a complaint about a `.json`, so
            # gating a data path on it agrees with every answer by returning None to all of them --
            # the branch above would have been as unreachable as the flag it was restoring. The
            # module docstring says this flag "is gated on the CLOCK (`base_wins_rules`)", and
            # `clock_judge` is the oracle that name refers to: it reads the three paths measured
            # here as `predates_landing_by_clock` / `predates_landing_carrying_some` where `judge`
            # reads all three as no complaint.
            #
            # AND THE RULE SET IS THE DATA ONE, WHICH IS THE QUESTION THAT WAS LEFT OPEN HERE.
            # Until 2026-09-23 this read `BASE_WINS_RULES`, excluding PARTIAL, with the note that
            # whether "carries some of the landing's distinctive lines" means anything about a
            # document where a line is a VALUE and not a statement was a real question and not one
            # to answer silently inside a door that DISCARDS bytes. It was measured instead of
            # assumed -- see `base_wins_rules`, which carries the numbers -- and the answer is that
            # for these two files 57/57 and 1032/1060 of the carried lines appear verbatim in a
            # sibling report that cannot have been derived from the landing. So it is coincidence,
            # and `base_wins_rules` admits PARTIAL for `DATA_SUFFIXES` and for nothing else.
            clock = clock_judge(root, path, head_text, work_text, parent=base) if base_wins else None
            if clock is not None and clock.rule in base_wins_rules(path):
                return Verdict(path, REFRESHABLE,
                               "REPLACEMENT admitted under `--base-wins`: the stale-copy control "
                               "refuses this data copy [{}] against {} ({}), so the clock -- not "
                               "the operator -- has established it cannot be carrying work built "
                               "on that landing. It binds {} key path(s) {} does not, disagrees "
                               "with it about {} more, and drops {} it holds. No landing door "
                               "applies to a regenerated data artefact -- there is no hunk that "
                               "takes a changed figure without the revert -- so discarding it is "
                               "the only enactment of the base winning.".format(
                                   clock.rule, base,
                                   clock.commit[:9] if clock.commit else "no commit",
                                   len(delta.novel), base, len(delta.edited), len(delta.dropped)),
                               gains=delta.novel, edited=delta.edited, drops=drops,
                               discarded=_discarded_lines(head_text, work_text))
            # WHICH OF THE TWO REFUSALS, and this is the split the whole change exists for. Only
            # `novel` is content the base does not hold; `edited` is a disagreement about a value,
            # and calling it a supply is what named `isolate_hunks` at a document with no hunk to
            # select. The counts are printed BOTH WAYS ROUND in each branch, so a reader can see
            # which quantity the verdict rests on rather than take the verdict's word for it.
            unreached = ("" if not base_wins else
                         " `--base-wins` DOES NOT REACH THIS COPY: the stale-copy control's "
                         "verdict on it is [{}], not one of {}, so nothing but your word says the "
                         "copy is the older draft -- and that word is what the flag exists not to "
                         "take.".format("no complaint" if clock is None else clock.rule,
                                        "/".join(base_wins_rules(path))))
            if delta.novel:
                return Verdict(path, SUPPLIES_NEW,
                               "this copy binds {} JSON key path(s) {} does not have (e.g. {}), so "
                               "it is NOT a copy {} supersedes -- the refresh would destroy "
                               "structure that is in no other document. It also disagrees with {} "
                               "about the value at {} key(s) they both bind, which is a separate "
                               "question and not a supply. Decide which document wins and land it "
                               "deliberately.{}".format(
                                   len(delta.novel), base, ", ".join(delta.novel[:3]), base,
                                   base, len(delta.edited), unreached),
                               gains=delta.novel, edited=delta.edited)
            return Verdict(path, RIVAL_VALUES,
                           "this copy binds NO key path {} lacks. It is the same document with {} "
                           "value(s) changed (e.g. {}) and {} key(s) dropped -- a choice between "
                           "two drafts, not work to land, so `isolate_hunks` has no hunk that takes "
                           "a changed figure without the revert. Either this copy is the later "
                           "regeneration, in which case land it whole with `surgical_land "
                           "--content {}=<file>`, or {} is, in which case `--base-wins` enacts the "
                           "discard once the clock agrees.{}".format(
                               base, len(delta.edited), ", ".join(delta.edited[:3]),
                               len(delta.dropped), path, base, unreached),
                           gains=(), edited=delta.edited, drops=drops)
        if not drops:
            return Verdict(path, NOT_SUPERSEDED,
                           "every JSON leaf in this copy is present in {} with an equal value and "
                           "it drops none, so the two documents differ only in FORMATTING. There "
                           "is nothing for {} to supersede and nothing to refresh.".format(
                               base, base))
        return Verdict(path, REFRESHABLE,
                       "rival copy: it supplies NO JSON leaf {} lacks and DROPS {} that {} has "
                       "(e.g. {}), so {} strictly supersedes it leaf for leaf.".format(
                           base, len(drops), base,
                           ", ".join(d.split("=")[0] for d in drops[:3]), base),
                       gains=(), dead=(),
                       discarded=_discarded_lines(head_text, work_text))
    # A NAME THE BASE CUT ON PURPOSE IS NOT HOLDER WORK, AND THIS TOOL WAS GATED ON THE OPPOSITE
    # READING. Rule 1 asks "does the copy supply a name the base lacks" as a set difference, and
    # `WORKER_FINDING_THE_HOLDER_WORK_VERDICT_NAMED_A_FORBIDDEN_IMPORT_AS_WORK_TO_LAND` is what that
    # cost at both ends: the census called a deliberately-deleted name holder work and named THIS
    # door as the remedy for the copies where it did not -- and this door then refused the very
    # copies the census sends it, for the same reason, because it re-implemented the same
    # difference. One question, one implementation: `cuts_among` is the census's own discriminator.
    # The precondition is UNCHANGED in strength -- a name the base never bound still refuses here.
    # Stated as a SET DIFFERENCE and not a membership filter on purpose: `tools/
    # substring_source_scan_census.py` reads `not in` over anything reachable from file text as a
    # substring-shaped interrogation of Python source, and it is right to -- these names came out of
    # `symbols()`. The difference says the same thing without asking that question of a string.
    cuts = cuts_among(root, path, tuple(sorted(work_names - head_names)), parent=base)
    gains = tuple(sorted(work_names - head_names - frozenset(c.name for c in cuts)))
    dead = dead_among(root, path, gains, work_text, parent=base)
    # THE NAME COUNT WAS THE WHOLE TEST AND IT GRADED THREE DIFFERENT COPIES THE SAME WAY. Two
    # 2026-09-08 findings each named half of that (`..._THE_HOLDER_WORK_RULE_COUNTS_NAMES_...` and
    # `..._THE_R1_COPYS_MISSING_PARTNER_IS_IN_A_SALVAGE_COMMIT_...`) and froze `H_harness` for nine
    # days between them. The split below is theirs, in their order of confidence: a name that
    # CANNOT RUN is decided by the base's own module; a copy with NO LANDABLE HUNK is decided by
    # the reconstruction `--keep` would build; and what survives both is holder work, unchanged.
    # A SET DIFFERENCE AND NOT A MEMBERSHIP FILTER, for the same reason the `cuts` line above is
    # one: `tools/substring_source_scan_census.py` reads a `not in` over anything reachable from
    # file text as a substring-shaped interrogation of Python source, and it is right to -- these
    # names came out of `symbols()`. The difference says the same thing without asking that
    # question of a string. (Written as a filter first; the census caught it at the commit gate.)
    live = tuple(sorted(frozenset(gains) - frozenset(d.name for d in dead)))
    if gains and not live and not superseded:
        return Verdict(path, SUPERSEDED_DEAD,
                       "this copy supplies {} name(s) {} lacks and NOT ONE of them can run against "
                       "it -- each reaches for an attribute {}'s own module does not bind, so "
                       "landing any hunk of it lands a red. That is not holder work. Re-run with "
                       "`--superseded` to admit it, AFTER reading the names below: a lane writing "
                       "the control before the module it grades produces exactly this file, and "
                       "the difference is intent, which is not on disk.".format(
                           len(gains), base, base),
                       gains=gains, dead=dead)
    if live:
        landable = landable_hunks(head_text, work_text, path)
        if not landable:
            drops = tuple(sorted(head_names - work_names))
            # THE JUDGEMENT IS STILL A PERSON'S; WHAT `--base-wins` ADDS IS AN ENACTMENT FOR ONE
            # OF ITS TWO ANSWERS. "The working copy wins" was always enactable -- land it. "The
            # base wins" had no move: there is nothing to land, and the act required is discarding
            # the copy, which `git checkout <path>` is and which is walled. So the copy stayed,
            # and the stale-copy door refused every landing over it forever.
            clock = judge(root, path, head_text, work_text, parent=base) if base_wins else None
            if clock is not None and clock.rule in base_wins_rules(path):
                return Verdict(path, REFRESHABLE,
                               "REPLACEMENT admitted under `--base-wins`: the stale-copy control "
                               "refuses this copy [{}] against {} ({}), so the clock -- not the "
                               "operator -- has established it cannot be carrying work built on "
                               "that landing, and the {} name(s) it supplies are the older draft "
                               "of the {} it drops. Neither landing door applies to it, so "
                               "discarding it is the only enactment of the base winning.".format(
                                   clock.rule, base,
                                   clock.commit[:9] if clock.commit else "no commit", len(live),
                                   len(drops)),
                               gains=live, drops=drops,
                               discarded=_discarded_lines(head_text, work_text))
            return Verdict(path, REPLACEMENT,
                           "this copy supplies {} name(s) {} lacks, and EVERY hunk carrying one "
                           "also deletes a name {} has -- so `--keep` has no selection that takes "
                           "the work without the revert, and `--content` would land the revert. "
                           "It is a REPLACEMENT, not holder work: two implementations of one "
                           "property, and which survives is a judgement neither door may make. "
                           "Decide it, then land the winner deliberately.{}".format(
                               len(live), base, base,
                               "" if not base_wins else
                               " `--base-wins` DOES NOT REACH THIS COPY: the stale-copy control's "
                               "verdict on it is [{}], not one of {}, so nothing but your word "
                               "says the copy is the older draft -- and that word is what the "
                               "flag exists not to take.".format(
                                   "no complaint" if clock is None else clock.rule,
                                   "/".join(base_wins_rules(path)))),
                           gains=live, drops=drops)
        return Verdict(path, SUPPLIES_NEW,
                       "this copy SUPPLIES {} name(s) {} does not have, so it is not a copy {} "
                       "supersedes -- it is holder work. Use `python3 -m tools.isolate_hunks "
                       "--survey {}` and land hunk(s) {} over HEAD -- those are the ones that add "
                       "without deleting anything {} carries.{}".format(
                           len(live), base, base, path,
                           ", ".join(str(h) for h in landable), base,
                           "" if not base_wins else
                           " `--base-wins` DOES NOT REACH A COPY WITH A LANDABLE HUNK, however "
                           "stale the clock says it is: the hunk(s) above take the work WITHOUT "
                           "the revert, so a route to keep it exists and discarding it would "
                           "destroy work a door could have saved. The flag only enacts the base "
                           "winning where no door applies at all."),
                       gains=live)
    loss = judge(root, path, head_text, work_text, parent=base)
    if loss is None:
        return Verdict(path, NOT_SUPERSEDED,
                       "the stale-copy control has NO complaint about this copy against {}: it "
                       "does not predate the last landing there and it deletes no name. Refreshing "
                       "it would discard an ordinary edit, which is `git checkout <path>` with a "
                       "nicer name -- and that is forbidden here for this exact reason.".format(
                           base))
    return Verdict(path, REFRESHABLE,
                   "rival copy: supplies no name {} lacks{}{}, and the stale-copy control refuses "
                   "it [{}]. {} strictly supersedes it.".format(
                       base, "" if not cuts else
                       " that it did not CUT ON PURPOSE ({} -- see `git show {}`)".format(
                           ", ".join(c.name for c in cuts[:3]), cuts[0].commit[:9]),
                       "" if not dead else
                       " that CAN RUN against it ({} admitted under --superseded)".format(
                           len(dead)),
                       loss.rule, base),
                   gains=gains, dead=dead,
                   discarded=_discarded_lines(head_text, work_text))


# ------------------------------------------------------------------------------ preservation


def preserve(root: Path, paths: list[str], slug: str, message: str) -> tuple[str, str]:
    """Commit the CURRENT bytes of `paths` onto `refs/preserved/refresh-to-head/<slug>`.

    Returns (ref, commit sha). Raises rather than returning a failure, because every caller's next
    act is the destructive one and a preservation that merely reported trouble would be read past.

    THE TREE IS HEAD'S, WITH THESE PATHS SWAPPED IN, built through a THROWAWAY INDEX
    (`GIT_INDEX_FILE`) so the holder's real index is not touched -- their staged work is not this
    tool's to move. The parent is HEAD, which makes the commit's own diff exactly the bytes being
    destroyed: that is what `git log --all -S <a line of it>` searches, so the recovery route the
    caller is told about is the one the commit actually supports.
    """
    if not paths:
        raise RefreshError("nothing to preserve")
    with tempfile.TemporaryDirectory() as tmp:
        env = {"GIT_INDEX_FILE": str(Path(tmp) / "index")}
        _git_ok(root, "read-tree", "HEAD", env=env)
        for path in paths:
            entry = _git_ok(root, "ls-tree", "HEAD", "--", path).split()
            if not entry:
                raise RefreshError("{} is not in HEAD; refusing to preserve".format(path))
            mode = entry[0]
            blob = _git_ok(root, "hash-object", "-w", "--", str(root / path)).strip()
            _git_ok(root, "update-index", "--add", "--cacheinfo",
                    "{},{},{}".format(mode, blob, path), env=env)
        tree = _git_ok(root, "write-tree", env=env).strip()
    head = _git_ok(root, "rev-parse", "HEAD").strip()
    commit = _git_ok(root, "commit-tree", tree, "-p", head, "-m", message).strip()
    ref = PRESERVED_PREFIX + slug
    _git_ok(root, "update-ref", ref, commit)
    return ref, commit


def verify_recoverable(root: Path, commit: str, path: str, work_bytes: bytes,
                       probe: str | None) -> str:
    """Prove the bytes come back BEFORE they are destroyed. Returns the recovery command to print.

    Two legs, and the second is the one that matters. The first is identity -- the blob under the
    preserved commit hashes to what is on disk right now. The second RUNS the `git log --all -S`
    lookup this tool advertises: a preserved commit that the advertised search cannot find is a
    preservation in name only, and the difference is invisible until someone needs it.
    """
    stored = subprocess.run(["git", "show", "{}:{}".format(commit, path)], cwd=str(root),
                            capture_output=True, check=False)
    if stored.returncode != 0 or stored.stdout != work_bytes:
        raise RefreshError(
            "PRESERVATION FAILED for {}: the blob under {} is not the bytes on disk. Nothing has "
            "been written.".format(path, commit[:9]))
    if probe is None:
        # A copy that differs from HEAD only by DELETIONS has no line of its own to search for.
        # Say so rather than printing a `-S` command that would find nothing.
        return "git show {}:{}   # (this copy has no line HEAD lacks, so -S has no probe)".format(
            commit[:9], path)
    found = _git(root, "log", "--all", "--max-count=1", "--format=%H", "-S", probe, "--", path)
    if commit not in found.stdout:
        raise RefreshError(
            "PRESERVATION FAILED for {}: `git log --all -S` does not find {} -- the advertised "
            "recovery route does not reach it. Nothing has been written.".format(path, commit[:9]))
    return "git log --all -S {!r} -- {}".format(probe, path)


def _probe(verdict: Verdict) -> str | None:
    candidates = [ln for ln in verdict.discarded if not _trivial(ln)]
    return max(candidates, key=len) if candidates else None


# ------------------------------------------------------------------------------------ the move


def refresh(root: Path, paths: list[str], slug: str | None, write: bool,
            base: str = "HEAD", superseded: bool = False,
            base_wins: bool = False) -> tuple[int, str]:
    """Survey, and when `write` is set and EVERY named path is refreshable, do it.

    `base` is the JUDGEMENT tree only -- see `judge_copy`. The bytes written are always HEAD's,
    because the block this clears is *worktree differs from HEAD*.
    """
    staged = _staged_paths(root)
    verdicts = [judge_copy(root, path, staged, base=base, superseded=superseded,
                           base_wins=base_wins)
                for path in paths]
    report = "".join(v.render() for v in verdicts)
    refusals = [v for v in verdicts if v.refused]
    doable = [v for v in verdicts if v.state == REFRESHABLE]

    if refusals:
        return 1, ("\n[refresh-to-head] ❌ {} of {} path(s) REFUSED -- nothing written.\n\n{}".format(
            len(refusals), len(verdicts), report))
    if not write:
        return 0, ("\n[refresh-to-head] {} path(s) refreshable, {} already at HEAD. SURVEY ONLY -- "
                   "re-run with --write --slug NAME to perform it.\n\n{}".format(
                       len(doable), len(verdicts) - len(doable), report))
    if not doable:
        return 0, "\n[refresh-to-head] every named path is already at HEAD -- nothing to do.\n"
    if not slug:
        return 1, ("\n[refresh-to-head] ❌ --write needs --slug NAME. The preservation ref is how "
                   "anyone finds these bytes again by name; an unnamed one is findable only by "
                   "someone who already knows what to search for.\n")

    targets = [v.path for v in doable]
    current = {p: (root / p).read_bytes() for p in targets}
    ref, commit = preserve(root, targets, slug, (
        "preserved rival working copies before refresh-to-head: {}\n\n"
        "These copies supplied no name HEAD lacks and the stale-copy control refused each of "
        "them, so HEAD strictly supersedes them and tools/refresh_to_head.py wrote HEAD's bytes "
        "over them. This commit is on no branch and is merged nowhere; it exists so the bytes "
        "are findable.".format(", ".join(targets))))

    routes = []
    for verdict in doable:
        routes.append((verdict.path,
                       verify_recoverable(root, commit, verdict.path,
                                          current[verdict.path], _probe(verdict))))
    for path in targets:
        (root / path).write_bytes(_blob_bytes(root, "HEAD", path))

    lines = "".join("  {}\n      recover with: {}\n".format(p, cmd) for p, cmd in routes)
    return 0, ("\n[refresh-to-head] ✅ refreshed {} path(s) to HEAD at {}.\n"
               "  preserved as {} ({})\n{}\n{}".format(
                   len(targets), root, ref, commit[:9], lines, report))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="+", help="repo-relative path(s) to refresh")
    ap.add_argument("--root", default=str(ROOT), help="the repository holding the rival copies")
    ap.add_argument("--write", action="store_true", help="perform it (default is survey only)")
    ap.add_argument("--slug", help="names the refs/preserved/refresh-to-head/<slug> ref")
    ap.add_argument("--base", default="HEAD",
                    help="the tree that must supersede the copy (default HEAD). Use "
                         "`origin/main` on a tree that is BEHIND origin, where HEAD is itself a "
                         "stale base -- the bytes written are HEAD's either way.")
    ap.add_argument("--superseded", action="store_true",
                    help="admit a copy whose supplied names CANNOT RUN against the base -- each "
                         "reaches for an attribute the base's own module does not bind. Survey it "
                         "first: the names are printed, and a lane writing a control before the "
                         "module it grades produces the same file.")
    ap.add_argument("--base-wins", action="store_true",
                    help="enact the base winning on a REPLACEMENT copy -- one where `--keep` has "
                         "no selection and `--content` would land a revert, so no landing door "
                         "applies. Admitted ONLY where the stale-copy control has already "
                         "returned predates_landing or predates_landing_by_clock for that path: "
                         "the clock, not your word, is what establishes the copy is the older "
                         "draft. Does NOT reach a copy with a landable hunk.")
    args = ap.parse_args(argv)
    try:
        rc, text = refresh(Path(args.root), args.paths, args.slug, args.write, base=args.base,
                           superseded=args.superseded, base_wins=args.base_wins)
    except RefreshError as exc:
        print("\n[refresh-to-head] ❌ {}".format(exc))
        return 1
    print(text)
    return rc


if __name__ == "__main__":  # pragma: no cover -- entry point
    raise SystemExit(main())
