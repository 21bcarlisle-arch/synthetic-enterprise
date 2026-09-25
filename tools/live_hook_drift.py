"""The hook chain git will ACTUALLY run, against the chain the trunk declares.

REUSE: tools/live_hook_drift.py
CLASS: CUSTOM
INDEX: searched "hook", "drift", "stale", "checkout", "hooksPath", "gate chain". Four modules
       come close and every one of them asks a different question:
       * `tools/stale_copy_refusal.py` grades a STAGED path's copy against the last landing to
         that path. The hooks dir is almost never in anybody's pathspec, so the population that
         control exists for excludes this file by construction.
       * `tools/hook_gate_mark.py` proves a FINISHED commit went through the chain. It cannot
         say which gates the chain contained, and it is itself the gate that is missing here.
       * `tools/time_the_commit_hook_chain.py` parses the hook into steps -- but it reads
         `ROOT/tools/git-hooks/pre-commit`, the committed tree's copy, which is the one side of
         this comparison that is never wrong.
       * `tools/canon_drift_check.py` compares a published page against the code; different
         subject, and its oracle is a claims YAML.
       The parser this file exports IS the one `test_time_the_commit_hook_chain.py` grew
       locally; that copy now imports this one, so there is one reader of the hook's bytes
       rather than two.

WHAT THIS OWNS, AND WHY IT IS NOT THE SAME AS "THE CHECKOUT IS BEHIND"
---------------------------------------------------------------------
`core.hooksPath` resolves to `<shared tree>/tools/git-hooks` -- a **working copy**, not the
index and not `origin/main`. It resolves to that same absolute path from inside every linked
worktree, so *where* a lane commits from changes nothing: every ordinary `git commit` in this
repository runs the shared checkout's hooks.

For almost any module in this tree a stale checkout DELAYS a fix. For this one it DELETES a
control, silently, and a green gate afterwards means only that the gates that still exist
passed. That asymmetry is the whole reason this file exists: nothing else in the tree compares
the two, and the gap was found by a seat grepping the live hook by hand.

Measured 2026-09-25, on real bytes: the shared checkout was 7 ahead / 49 behind, the live
`pre-commit` was 25,521 bytes against the trunk's 26,326, and the chain difference was exactly
one gate -- `hook_gate_mark --record`, landed at `934343669` and running nowhere.

THE COMPARISON IS OF INVOCATIONS, NOT OF BYTES, AND THAT IS THE LOAD-BEARING CHOICE
-----------------------------------------------------------------------------------
805 bytes of difference is not 805 bytes of danger. Substantially all of a hook diff is
comment, and a control that shouted on every comment edit would be turned off inside a week --
this repo's `commons_source_supersession` says the same thing about age. What can never be
benign is a gate the trunk declares that the live chain does not run, or an argv the trunk
changed that the live chain still runs the old way (`--gate` quietly becoming `--check` is a
control narrowed without anyone deciding to narrow it). So the verdict has three named parts:

  MISSING  -- the trunk declares this gate and the live chain does not run it AT ALL. The
              control does not exist for any commit made through `git commit` until the
              checkout advances.
  ALTERED  -- both run it, with different arguments. Same subject, different question asked.
  RETIRED  -- the live chain runs a gate the trunk has removed. Rarer and less dangerous, but
              it is a gate nobody currently maintains and its absence from the trunk means no
              test selects it.

Byte identity is still reported, because "identical" is the only reading that needs no
interpretation at all. It is never on its own a refusal.

WHY THIS IS NOT WIRED INTO `tools/git-hooks/pre-commit` AND ONLY THERE
-----------------------------------------------------------------------
Because that line would be read from the very working copy it exists to grade. A liveness
signal delivered through the channel it monitors freezes at its last-healthy value and is
unreachable in the one outage it was written for -- so a hook line alone would have been inert
today, on the exact day the gap was real. The wiring that bites is in `tools/surgical_land.py`,
which is resolved from the COMMITTING tree on every landing and is the door `CLAUDE.md` sends
every lane to. The hook line is added as well, and is honestly labelled there as inert until
the checkout advances.

WHY IT REPORTS RATHER THAN REFUSES BY DEFAULT
----------------------------------------------
A refusal here would red every lane in the tree for a condition no lane can fix from inside its
own commit -- the remedy is the reconciler advancing the shared checkout. A control keyed to a
state its reader cannot act on gets switched off, which would leave the gap exactly where it was
found. `--gate` exists for a caller that has decided it wants the refusal; nothing in the commit
chain passes it today, and the comment at the call site says so.

FAIL-CLOSED ON ITS OWN READING. If the reference revision does not resolve, or either file
cannot be read, or the REFERENCE parses to no invocations at all, the verdict is
`undetermined` with the reason named -- never a green. A green here requires that both sides
parsed and agreed.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: The hook whose chain is the subject. `commit-msg` is tracked in the same directory and is
#: compared for byte identity alongside it, but only `pre-commit` carries the gate chain.
HOOK_REL = "tools/git-hooks/pre-commit"

#: Every hook the trunk tracks, for the byte-level half of the report.
TRACKED_HOOKS = ("tools/git-hooks/pre-commit", "tools/git-hooks/commit-msg")

#: What the chain is compared AGAINST by default. `origin/main` and not `HEAD`: HEAD moves with
#: whatever the reader happens to have checked out, so a stale checkout comparing its hooks
#: against its own HEAD is the tautology this module exists to break.
DEFAULT_REFERENCE = "origin/main"


def hook_invocations(text: str) -> list[str]:
    """Every `python3 ...` command the hook runs, normalised to drop its shell tail.

    THE ONE READER OF THE HOOK'S BYTES. `tests/tools/test_time_the_commit_hook_chain.py` grew
    this function locally in 2026-09; it imports this copy now. Two independent parsers of the
    same file is the stand-in-fixture failure with the serial numbers filed off -- they agree
    until the day the hook gains a shape only one of them handles, and then the two controls
    disagree about what the chain is with no way to tell which is right.
    """
    found = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("python3 "):
            continue
        # Drop the shell tail (`|| exit 1`, `&& git add ...`) -- the subject is the command.
        found.append(re.split(r"\s*(?:\|\||&&|;)\s*", stripped)[0].strip())
    return found


def invocation_subject(command: str) -> str:
    """A step's identity: the module or script it runs, ignoring the interpreter and flags."""
    for token in command.split()[1:]:
        if token.startswith("-") and token != "-m":
            continue
        if token == "-m":
            continue
        return token.removeprefix("tools/").removeprefix("tools.").removesuffix(".py")
    raise ValueError(f"no subject found in {command!r}")


def configured_hooks_path(root: Path = ROOT) -> str | None:
    """`core.hooksPath` as configured, or None when git is using the repo's own private dir.

    THE DISTINCTION THIS BUYS, and it was paid for on this module's second landing. A repository
    with no `core.hooksPath` has no working-copy-versus-trunk question at all: git runs
    `<git-dir>/hooks`, which is not a checkout of anything tracked and cannot be behind. Reporting
    "CANNOT TELL" there is a fail-closed message that is CORRECT and PERMANENT -- and a warning
    that fires on every single run is a warning nobody reads by the third one. `surgical_land`
    builds a standalone extract per landing, so without this the gate would have shouted on every
    landing this repository ever makes.

    It is a distinct verdict rather than a silence: an ordinary clone that has never run
    `tools/install_git_hooks.sh` is in exactly this state and IS running no gates at all, which a
    reader wants told once, plainly.
    """
    out = subprocess.run(["git", "config", "--get", "core.hooksPath"], cwd=str(root),
                         capture_output=True, text=True)
    value = out.stdout.strip()
    return value or None


def live_hooks_dir(root: Path = ROOT) -> Path:
    """The hooks directory git will ACTUALLY use, asked of git rather than reconstructed.

    `git rev-parse --git-path hooks` honours `core.hooksPath` including the worktree case, which
    a hand-built `<root>/.git/hooks` does not: from a linked worktree the naive expression gives
    this worktree's private hooks dir, and this repository's whole defect is that the real answer
    is somebody ELSE'S working copy.
    """
    out = subprocess.run(["git", "rev-parse", "--git-path", "hooks"], cwd=str(root),
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise OSError(f"git could not resolve the hooks path: {(out.stderr or '').strip()}")
    resolved = Path(out.stdout.strip())
    return resolved if resolved.is_absolute() else (root / resolved).resolve()


#: How far back the provenance scan will look before it refuses to answer. The population is
#: commits touching ONE path, so this is generous; the point of the bound is that running out of
#: it is `undetermined` and never `mixture` -- see `live_provenance`.
PROVENANCE_SCAN_LIMIT = 500

#: The live copy is byte-identical to HEAD's blob. Ordinary: whatever the chain is, the checkout
#: is at least internally consistent, and advancing it is exactly the right move.
PROV_HEAD = "head"
#: The live copy is some ANCESTOR of HEAD's blob, not HEAD's. The checkout holds an older
#: revision of this path than its own HEAD says it should -- `git status` shows it as a
#: modification, and `git checkout -- <path>` (or any advance that touches the path) restores it.
PROV_BEHIND = "behind"
#: The live copy matches a commit NOT reachable from HEAD -- typically `origin/main` or a fork.
#: Somebody wrote a NEWER revision's bytes into the working copy by hand. This is the state that
#: makes the byte comparison read at its cleanest while the checkout itself has not moved an inch,
#: and the next advance that touches the path throws the patch away without a word.
PROV_OFF_HEAD = "off-head"
#: No commit in this repository carries these bytes. A hand-edit, a merge residue, a truncated
#: write. No git operation reconciles it: the next checkout conflicts or clobbers.
PROV_MIXTURE = "mixture"


@dataclass
class Provenance:
    """WHICH COMMIT, IF ANY, THE LIVE HOOK'S BYTES CAME FROM.

    WHY THIS IS A SECOND QUESTION AND NOT A DETAIL OF THE FIRST. `compare` asks whether the live
    chain matches the reference. That is a question about BYTES, and three completely different
    conditions produce the same answer to it:

      * the checkout is behind and will catch up -- the reconciler is the remedy and the gap
        closes itself;
      * somebody pasted the reference's bytes in by hand -- the byte comparison reads `byte for
        byte`, its cleanest verdict, while the checkout has not moved and the gates are running
        only because a human is holding them there. The next advance DELETES the patch;
      * the bytes belong to no commit at all -- no advance reconciles that.

    Measured 2026-09-25 on the shared tree, and this is why the leg exists rather than a
    hypothetical: `8e40bb205`'s own commit body records a lane writing three paths "from
    origin/main's blobs to disk with `git cat-file blob`, index untouched", deliberately outside
    its pathspec. That put the hooks directory in the second state at 01:16. At 01:46 the checkout
    advanced and the patch was gone. For thirty minutes this module would have reported the
    chain was `origin/main`'s byte for byte -- true, and the most misleading true thing it could
    have said, because the condition it exists to detect was untouched underneath.

    FAIL-CLOSED. Running out of scan budget is `undetermined` with the bound named, never
    `mixture`: "I did not find it" and "it is not there" are not the same claim, and only one of
    them licenses the alarming remedy.
    """

    blob: str | None = None
    #: One of the PROV_* constants, or None when the question could not be asked.
    verdict: str | None = None
    #: The commit whose blob at `HOOK_REL` equals the live bytes, when one was found.
    commit: str | None = None
    #: A named reason no verdict could be reached. Never set alongside a verdict.
    undetermined: str | None = None


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True)


def owning_checkout(live_hook: Path, root: Path = ROOT) -> Path | None:
    """The working tree the live hooks directory actually SITS IN, which is usually not `root`.

    THIS IS LOAD-BEARING AND IT WAS WRONG ON THE FIRST DRAFT, caught by printing the verdict from
    a linked worktree before writing the test. `core.hooksPath` is an absolute path into the
    SHARED tree, and it resolves to that same path from every worktree -- so a provenance leg that
    asked `HEAD` of `root` was asking a question about THIS lane's checkout and answering it about
    SOMEBODY ELSE'S working copy. From this seat's worktree the naive version called the shared
    tree's hooks `behind` and told the reader `git status` would show the path as modified, which
    was false in both trees at once. A linked worktree's HEAD has nothing to do with the copy on
    disk over there.

    Returns None when the hooks directory is not inside any working tree at all -- a hooksPath
    pointing outside the repo, which the caller must treat as undetermined and not as a verdict.
    """
    out = _git(live_hook.parent if live_hook.parent.is_dir() else root,
               "rev-parse", "--show-toplevel")
    if out.returncode != 0:
        return None
    top = out.stdout.strip()
    return Path(top) if top else None


def live_provenance(live_hook: Path, root: Path = ROOT, rel: str = HOOK_REL,
                    limit: int = PROVENANCE_SCAN_LIMIT) -> Provenance:
    """Which revision, if any, the bytes at `live_hook` are a copy of.

    Every git question below is asked of the checkout that OWNS the live copy (see
    `owning_checkout`), never of the caller's tree.

    The scan population is `git log --all -- <rel>`: every commit that touched this path, on any
    ref. That is deliberately wider than HEAD's history, because the whole point of `off-head` is
    a copy taken from a revision HEAD cannot see.
    """
    owner = owning_checkout(live_hook, root)
    if owner is None:
        return Provenance(undetermined=(
            f"the live hooks directory ({live_hook.parent}) is not inside any git working tree, "
            "so there is no checkout whose HEAD the bytes could be compared against."))
    root = owner
    hashed = _git(root, "hash-object", "--", str(live_hook))
    if hashed.returncode != 0:
        return Provenance(undetermined=(
            f"git could not hash the live hook ({live_hook}): "
            f"{(hashed.stderr or '').strip()}"))
    blob = hashed.stdout.strip()

    head = _git(root, "rev-parse", f"HEAD:{rel}")
    if head.returncode != 0:
        return Provenance(blob=blob, undetermined=(
            f"`git rev-parse HEAD:{rel}` failed, so there is no revision to compare the live "
            f"bytes against: {(head.stderr or '').strip()}"))
    if head.stdout.strip() == blob:
        return Provenance(blob=blob, verdict=PROV_HEAD,
                          commit=_git(root, "rev-parse", "HEAD").stdout.strip() or None)

    listed = _git(root, "log", "--all", f"--max-count={limit}", "--format=%H", "--", rel)
    if listed.returncode != 0:
        return Provenance(blob=blob, undetermined=(
            f"`git log --all -- {rel}` failed, so the provenance of the live bytes could not be "
            f"asked: {(listed.stderr or '').strip()}"))
    commits = [line for line in listed.stdout.split() if line]
    for commit in commits:
        got = _git(root, "rev-parse", f"{commit}:{rel}")
        if got.returncode == 0 and got.stdout.strip() == blob:
            ancestor = _git(root, "merge-base", "--is-ancestor", commit, "HEAD").returncode == 0
            return Provenance(blob=blob, commit=commit,
                              verdict=PROV_BEHIND if ancestor else PROV_OFF_HEAD)
    if len(commits) >= limit:
        # THE FAIL-CLOSED LEG. An exhausted budget is not evidence of absence, and `mixture` is
        # the verdict that sends a reader to hand-repair a file. Refuse instead.
        return Provenance(blob=blob, undetermined=(
            f"scanned the most recent {limit} commits touching {rel} without finding these bytes, "
            "and the budget ran out -- so they may still belong to an older revision. Re-run with "
            "a larger limit; this is NOT a finding of `mixture`."))
    return Provenance(blob=blob, verdict=PROV_MIXTURE)


@dataclass
class Drift:
    """What the live chain runs, against what the reference declares."""

    live_path: Path | None = None
    reference: str = DEFAULT_REFERENCE
    #: Trunk declares it, the live chain does not run it at all. The control does not exist.
    missing: list[str] = field(default_factory=list)
    #: Live runs a gate the trunk has retired.
    retired: list[str] = field(default_factory=list)
    #: (subject, live argv, reference argv) -- same gate, different question.
    altered: list[tuple[str, str, str]] = field(default_factory=list)
    #: Paths whose live bytes differ from the reference blob, whether or not the chain changed.
    bytes_differ: list[str] = field(default_factory=list)
    #: A named reason the comparison could not be made. Never empty alongside a green verdict.
    undetermined: str | None = None
    #: `core.hooksPath` is not configured, so there is no working copy to be behind. Not a clean
    #: bill and not an alarm: a third state, because it is neither.
    unconfigured: bool = False
    #: Which revision the live bytes are a copy of, when the question could be asked. Carried
    #: alongside the byte verdict rather than folded into it: they answer different questions and
    #: the REMEDY follows from this one, not from the other.
    provenance: Provenance | None = None

    @property
    def needs_reader(self) -> bool:
        """Whether this verdict has anything a lane about to trust a green gate must be told.

        WHY THIS IS NOT `not self.clean`, which is what the landing door used to ask. `clean` is a
        statement about the CHAIN, and the hand-patch condition is byte-identical to the reference
        by construction -- so the door's `if verdict.clean: return` silenced the report in exactly
        the state the provenance leg was written for. The qualification was reaching `report()`
        and dying at the one call site that has a reader.

        Only `head` is quiet. A copy whose bytes belong to an unreachable commit, to no commit, or
        to an older revision than its own checkout is worth a line even when the gates all match.
        """
        if self.unconfigured or not self.clean or self.bytes_differ:
            return True
        prov = self.provenance
        return prov is not None and prov.verdict != PROV_HEAD

    @property
    def clean(self) -> bool:
        """True only when the comparison was MADE and found nothing. An undetermined verdict is
        not clean: that distinction is the whole of this control's fail-closed behaviour."""
        return (self.undetermined is None and not self.unconfigured and not self.missing
                and not self.retired and not self.altered)


def compare(live_text: str, reference_text: str, *, reference: str = DEFAULT_REFERENCE) -> Drift:
    """The pure half: two hook texts in, a verdict out. No git, no filesystem."""
    d = Drift(reference=reference)
    ref_commands = hook_invocations(reference_text)
    if not ref_commands:
        # ANTI-VACUITY, and it guards the direction that matters. Both sides parsing to nothing
        # would make every comparison below trivially true -- a control that stopped being one.
        # Keyed to the REFERENCE rather than to a count of today's gates, because the number of
        # gates is supposed to change and the trunk having none never is.
        d.undetermined = (
            f"the reference hook ({reference}:{HOOK_REL}) parsed to NO python3 invocations -- "
            "the reader is broken, or that revision does not carry this repo's hook. Refusing to "
            "report a comparison that would be vacuously green.")
        return d
    live_commands = hook_invocations(live_text)
    live_by_subject = {invocation_subject(c): c for c in live_commands}
    ref_by_subject = {invocation_subject(c): c for c in ref_commands}
    d.missing = [s for s in ref_by_subject if s not in live_by_subject]
    d.retired = [s for s in live_by_subject if s not in ref_by_subject]
    d.altered = [(s, live_by_subject[s], ref_by_subject[s]) for s in ref_by_subject
                 if s in live_by_subject and live_by_subject[s] != ref_by_subject[s]]
    return d


def _show(root: Path, reference: str, rel: str) -> str | None:
    out = subprocess.run(["git", "show", f"{reference}:{rel}"], cwd=str(root),
                         capture_output=True, text=True)
    return out.stdout if out.returncode == 0 else None


def drift(root: Path = ROOT, reference: str = DEFAULT_REFERENCE) -> Drift:
    """The live reading: resolve the hooks dir git will use and compare it to `reference`."""
    try:
        hooks = live_hooks_dir(root)
    except OSError as exc:
        return Drift(reference=reference, undetermined=str(exc))

    live_hook = hooks / Path(HOOK_REL).name
    if configured_hooks_path(root) is None:
        # Asked BEFORE the hook is read, because the unreadable-hook refusal below would otherwise
        # claim this state -- and `<git-dir>/hooks/pre-commit` is missing in every repo that never
        # installed one, which is the commonest reason that file is absent.
        return Drift(live_path=live_hook, reference=reference, unconfigured=True)
    # THE SUBJECT IS READ FIRST, and the order is load-bearing rather than tidy. Both failures are
    # `undetermined`, so neither is hidden -- but only one of them is ACTIONABLE by the reader, and
    # a reader told "origin/main does not resolve" goes and fetches while the hook git is about to
    # run sits unreadable. Found by this module's own landing: inside `surgical_land`'s extract
    # there is no `origin/main`, so the reference leg fired first and masked the leg under test.
    try:
        live_text = live_hook.read_text(encoding="utf-8")
    except OSError as exc:
        return Drift(live_path=live_hook, reference=reference, undetermined=(
            f"the hook git will run ({live_hook}) could not be read: {exc}. An unreadable gate "
            "chain is a FAILED reading, not an absent problem."))
    reference_text = _show(root, reference, HOOK_REL)
    if reference_text is None:
        return Drift(live_path=live_hook, reference=reference, undetermined=(
            f"`git show {reference}:{HOOK_REL}` failed -- that revision does not resolve here, so "
            "there is nothing to compare the live hook against. Fetch it, or name another "
            "revision with --reference; this is NOT a clean bill."))

    d = compare(live_text, reference_text, reference=reference)
    d.live_path = live_hook
    # Asked AFTER the unconfigured and unreadable legs above, both of which return early: a repo
    # with no `core.hooksPath` has no working copy whose provenance could be in question, and
    # bytes that could not be read have none to ask about.
    d.provenance = live_provenance(live_hook, root)
    for rel in TRACKED_HOOKS:
        ref_bytes = _show(root, reference, rel)
        if ref_bytes is None:
            continue
        candidate = hooks / Path(rel).name
        try:
            if candidate.read_text(encoding="utf-8") != ref_bytes:
                d.bytes_differ.append(rel)
        except OSError:
            d.bytes_differ.append(rel)
    return d


def provenance_lines(prov: Provenance | None) -> list[str]:
    """The remedy, which is DIFFERENT in each state and used to be one fixed sentence.

    The sentence this replaces -- "the remedy is the reconciler advancing the SHARED checkout" --
    is right in exactly one of these four states. In `off-head` it names the operation that
    DESTROYS the live copy as the thing to go and do.
    """
    if prov is None:
        # NOT SILENCE, and not the old fixed sentence either. `compare()` is the pure half and
        # cannot ask git anything, so the remedy genuinely is not known on this path -- saying
        # which remedy applies would be picking one of four. Naming the gap sends the reader to
        # the call that can answer it.
        return ["[live-hook] the REMEDY depends on which revision these live bytes came from, and "
                "that was not asked here (the pure comparison cannot reach git). Run `python3 -m "
                "tools.live_hook_drift` for the provenance verdict before acting."]
    if prov.undetermined:
        return ["[live-hook] CANNOT TELL which revision the live bytes came from, so the remedy "
                "below is unknown too:", f"[live-hook]   {prov.undetermined}"]
    short = (prov.commit or "")[:9]
    if prov.verdict == PROV_HEAD:
        return ["[live-hook] provenance: the live bytes ARE this checkout's HEAD blob "
                f"({short}), so the copy is a snapshot and not a patchwork. If it is behind the "
                "trunk, the remedy is the reconciler advancing the SHARED checkout."]
    if prov.verdict == PROV_BEHIND:
        return ["[live-hook] provenance: the live bytes are an OLDER revision than this "
                f"checkout's own HEAD -- they are {short}'s blob. The checkout did not write "
                "HEAD's copy here, so `git status` is showing this path as modified. Establish "
                "whose edit that is before restoring it; a lane may be holding work in it."]
    if prov.verdict == PROV_OFF_HEAD:
        return ["[live-hook] provenance: the live bytes match a commit this HEAD CANNOT REACH "
                f"({short}) -- somebody wrote another revision's blob into the working copy by "
                "hand. READ THE BYTE VERDICT ABOVE IN THAT LIGHT: a copy patched from the "
                "reference matches it exactly while the checkout has not moved at all, so a "
                "green here is a human holding the gates in place and not a healthy tree.",
                "[live-hook]   The remedy is NOT to advance the checkout: the next advance that "
                "touches this path discards the patch silently. Land those bytes, or expect them "
                "gone and say so where the next reader will look."]
    if prov.verdict == PROV_MIXTURE:
        return ["[live-hook] provenance: NO COMMIT in this repository carries these bytes -- the "
                "live hook is a hand-edit or a partial write, not a checkout of anything. No "
                "advance reconciles this: the next one conflicts or clobbers. Diff it against "
                "HEAD's blob and decide what it was meant to be."]
    return []


def report(d: Drift) -> str:
    """The loud surface. Written to be read by a lane that is about to trust a green gate."""
    lines = []
    if d.undetermined:
        lines.append("[live-hook] CANNOT TELL whether the gates git runs are the gates the trunk "
                     "declares.")
        lines.append(f"[live-hook]   {d.undetermined}")
        return "\n".join(lines)
    if d.unconfigured:
        return ("[live-hook] core.hooksPath is NOT set here, so git runs {} -- a private directory "
                "that is not a checkout of anything tracked and cannot be behind. There is nothing "
                "to compare. In a real clone this means NO gates run at all: "
                "`sh tools/install_git_hooks.sh`.".format(d.live_path))
    if d.clean and not d.bytes_differ:
        # NOT AN UNQUALIFIED PASS, and that is the correction this branch carries. A working copy
        # hand-patched from the reference reads exactly here, so the provenance line is printed
        # alongside the green rather than only beside a difference.
        return "\n".join([
            f"[live-hook] the hook chain git will run IS {d.reference}'s, byte for byte "
            f"({d.live_path}).", *provenance_lines(d.provenance)])
    lines.append(f"[live-hook] the hooks git will run live at {d.live_path}, which is a WORKING "
                 f"COPY, and it differs from {d.reference}.")
    if d.missing:
        lines.append("[live-hook] GATES THE TRUNK DECLARES THAT DO NOT RUN -- these controls do "
                     "not exist for any commit made through `git commit` here, and a green gate "
                     "does NOT mean they passed:")
        for subject in d.missing:
            lines.append(f"[live-hook]   MISSING  {subject}")
    for subject, live_argv, ref_argv in d.altered:
        lines.append(f"[live-hook]   ALTERED  {subject}: runs `{live_argv}`, trunk declares "
                     f"`{ref_argv}`")
    for subject in d.retired:
        lines.append(f"[live-hook]   RETIRED  {subject}: runs here, absent from {d.reference}")
    if d.bytes_differ and not (d.missing or d.altered or d.retired):
        lines.append("[live-hook] the chain itself is intact; the difference is in "
                     f"{', '.join(d.bytes_differ)} outside the gate lines (comment or prose).")
    # THE TWO NEVER-DOS, printed on every difference and not inside any one provenance state.
    # They are true whatever the live bytes turn out to be -- a daemon restart never advances a
    # checkout, and a worktree checkout is never the door -- and folding them into the `head`
    # remedy would have deleted them from the three states where somebody is most likely to reach
    # for one of them.
    lines.append("[live-hook] whatever follows, it is NOT a daemon restart (that blinds the "
                 "staleness detector to the checkout gap) and NOT a checkout from a worktree "
                 "(other lanes hold uncommitted work there).")
    lines.extend(provenance_lines(d.provenance))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--reference", default=DEFAULT_REFERENCE,
                        help=f"revision whose hooks are the truth (default {DEFAULT_REFERENCE})")
    parser.add_argument("--gate", action="store_true",
                        help="exit 1 when a gate the reference declares does not run live, or "
                             "when the comparison cannot be made")
    args = parser.parse_args(argv)
    d = drift(reference=args.reference)
    print(report(d))
    if args.gate and not d.clean:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
