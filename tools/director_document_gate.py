"""A change to what the director MEANT is his; a correction of what is plainly WRONG is the seat's.

REUSE: tools/director_document_gate.py
CLASS: CUSTOM
INDEX: searched "director document", "commit message gate", "trailer", "canon", "mission".
       `tools/next_step_gate.py` and `tools/write_time_gate.py` are the nearest organs and this is
       their SIBLING, not an extension: same hook, same shape (a required RECORD, never a required
       decision), a third question. `tools/canon_drift_check.py` asks whether the canon still
       matches the CODE; this asks who may change the canon's INTENT. Neither answers the other.

WHY THIS EXISTS
---------------
Director, 2026-10-04, verbatim:

    "Get on with, without asking: knowledge, in-flight work, error fixing, and correcting plain
     factual errors anywhere, including canon. Say what you corrected. ... The reservation is
     narrow: director documents and the mission statement, not every file that mentions a goal."

and the mechanism he asked for: "a check that a commit changing a director document's intent goes
to staging as a proposal, while a marked factual correction can land."

So the line is not "never touch a director document" -- that would forbid the factual correction he
explicitly handed over. The line is that a content change to one must SAY WHICH KIND IT IS:

    Director-doc: correction -- <what was factually wrong, and the evidence>
    Director-doc: his-words  -- <where his words come from: console date, NTFY file, ruling>
    Director-doc: record     -- <bookkeeping that changes no intent, e.g. a header classification>

and anything that is none of those is a change of intent, which goes to `docs/staging/` as a
proposal instead of landing.

THE ESCAPE IS DELIBERATE AND COUNTED, exactly as `next_step_gate`'s `none -- <reason>` is. A gate
cannot tell a true `correction` from a reworded intent; any reason typed satisfies any predicate a
gate can write. So the trailer is a record, and `--report` reads the rate and the reasons back out of
`git log` -- the commit message is durable, tracked, and cannot be lost to `surgical_land`'s
throwaway extract (the trap `next_step_gate`'s first store fell into).

WHAT IS IN SCOPE -- `is_director_document`, the one place it is defined
-----------------------------------------------------------------------
* `docs/**/DIRECTOR_*.md`, EXCEPT `DIRECTOR_CONSOLE_*`: those are verbatim console transcripts that
  `tools/console_instruction_record.py` appends to. Appending his words is capture, not intent, and
  asking for a trailer on every capture would teach the reflexive `record` that empties the count.
  (That tool's reply files are `SEAT_REPLY_*.md` -- outside the prefix by construction, named here
  so nobody widens the prefix and sweeps them in.)
* `docs/design/THE_MODEL_ON_A_PAGE.md`.
* THE MISSION STATEMENT: the block of `CLAUDE.md` from `## The mission` to the next line that is
  exactly `---`. CLAUDE.md as a whole is NOT a director document -- the seat rewrites it routinely --
  so the block's text is compared, HEAD against the staged blob, and an edit elsewhere is unasked.

WHAT IS A CONTENT CHANGE, and the traffic that must pass untouched
------------------------------------------------------------------
An `M`, a rename below 100% similarity, a `D` that is not half of a move into `docs/staging/done/`,
or a change of the mission block's text. Measured traffic that must NOT be asked:
* archive moves of rulings into `docs/staging/done/` -- pure renames, `R100`;
* a move git splits into `D` + `A` (the archive copy is in the resulting tree under `done/`);
* adding a NEW director document (`A`) -- that records his words, it does not change them;
* his own amendments, which arrive as GitHub-authored commits and never run a local hook at all.

A MERGE ASKS ONLY ABOUT WHAT THE MERGE ITSELF WROTE -- the lesson `write_time_gate.staged_additions`
and `next_step_gate.moves_no_parent_carried` each paid for separately. Against `HEAD` alone, an
`origin_reconcile` merge "modifies" every director document the trunk side modified, and that side
already carried its own trailer (or was his). A path whose staged blob an OTHER parent already holds
is subtracted; so is a mission block an other parent already reads.

FAILS OPEN, LOUDLY, ON AN UNREADABLE GIT -- the `next_step_gate` choice and for its reason: this runs
on every commit in a tree several lanes write at once, and one unasked commit is recoverable where a
wedged tree is not. The failure prints its cause on stderr; it never reads as "nothing in scope".

THE REPO IS THE CWD, not `Path(__file__)`. git runs `commit-msg` from the top of the worktree being
committed, and `surgical_land.run_message_gate` runs it with `cwd=<extract>`; asking the cwd is what
lets the controls drive a REAL `git commit` through the wired hook in a temporary repo.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

MISSION_FILE = "CLAUDE.md"
MISSION_HEADING = "## The mission"
MODEL_ON_A_PAGE = "docs/design/THE_MODEL_ON_A_PAGE.md"
ARCHIVE_DIR = "docs/staging/done/"
KINDS = ("correction", "his-words", "record")

#: Any line opening with the trailer key, so a malformed one is refused rather than ignored.
_TRAILER_LINE_RE = re.compile(r"^\s*Director-doc\s*:(.*)$", re.IGNORECASE | re.MULTILINE)
#: The well-formed body: a kind, a `--`, and a non-empty reason.
_TRAILER_BODY_RE = re.compile(r"^\s*(correction|his-words|record)\s*--\s*(\S.*?)\s*$", re.IGNORECASE)


def is_director_document(repo_path: str) -> bool:
    """Is this repo-relative path a director document? The ONE definition of the scope.

    The mission block of CLAUDE.md is a director document too, but it is a BLOCK, not a path, so it
    is asked by `mission_block` and not here: `is_director_document("CLAUDE.md")` is False, on
    purpose, because the rest of that file is the seat's.
    """
    p = PurePosixPath(repo_path)
    if repo_path == MODEL_ON_A_PAGE:
        return True
    if not p.parts or p.parts[0] != "docs":
        return False
    name = p.name
    if not (name.startswith("DIRECTOR_") and name.endswith(".md")):
        return False
    return not name.startswith("DIRECTOR_CONSOLE_")


def mission_block(text: str | None) -> str | None:
    """The mission statement's text, from `## The mission` to the next line that is exactly `---`.

    None when the heading is absent. A heading with no closing rule runs to the end of the file --
    the block is then everything that could be the mission, which is the strict reading.
    """
    if text is None:
        return None
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.rstrip() == MISSION_HEADING:
            out = []
            for later in lines[i:]:
                if later.rstrip() == "---":
                    break
                out.append(later)
            return "\n".join(out)
    return None


@dataclass(frozen=True)
class Change:
    status: str          # one letter: A M D R C T
    score: int | None    # rename/copy similarity, else None
    old: str | None
    new: str | None


def parse_name_status(raw: str) -> list[Change]:
    """`git diff --name-status -M -z` output -> Changes. Pure, so the controls need no repo."""
    toks = [t for t in raw.split("\x00")]
    out: list[Change] = []
    i = 0
    while i < len(toks):
        code = toks[i]
        if not code:
            i += 1
            continue
        letter = code[0]
        score = int(code[1:]) if code[1:].isdigit() else None
        if letter in ("R", "C"):
            out.append(Change(letter, score, toks[i + 1], toks[i + 2]))
            i += 3
        else:
            path = toks[i + 1]
            out.append(Change(letter, score, None if letter == "A" else path,
                              None if letter == "D" else path))
            i += 2
    return out


def owed(changes: list[Change], resulting_paths: set[str] | None = None) -> list[Change]:
    """The director-document CONTENT changes among `changes`. Pure.

    `resulting_paths` is the set of paths in the tree this commit creates; it is how a `D` is
    recognised as half of an archival move -- its basename is under `docs/staging/done/` there.
    None means "not asked", and then only a `done/` copy ADDED in this same commit excuses a D.
    """
    present = set(resulting_paths or ()) | {c.new for c in changes
                                            if c.status in ("A", "C") and c.new}
    found: list[Change] = []
    for c in changes:
        if c.status in ("A", "C"):
            continue  # a new director document records his words; a copy changes nothing
        if not (is_director_document(c.old or "") or is_director_document(c.new or "")):
            continue
        if c.status == "R" and c.score == 100:
            continue  # content identical: an archive move, the measured common case
        if c.status == "D":
            archived = ARCHIVE_DIR + PurePosixPath(c.old or "").name
            if c.old != archived and archived in present:
                continue  # the root copy leaves; the archive copy is in the tree
        found.append(c)
    return found


def describe(c: Change) -> str:
    if c.status == "R":
        return f"R{c.score:03d} {c.old} -> {c.new} (renamed AND edited)"
    if c.status == "D":
        return f"D {c.old} (deleted, and no archive copy under {ARCHIVE_DIR})"
    return f"{c.status} {c.new}"


def parse_trailer(message: str) -> tuple[str | None, str | None, str | None]:
    """(kind, reason, refusal). Exactly one well-formed `Director-doc:` line, or a refusal."""
    lines = _TRAILER_LINE_RE.findall(message)
    if not lines:
        return None, None, "no `Director-doc:` trailer"
    if len(lines) > 1:
        return None, None, f"{len(lines)} `Director-doc:` lines; exactly one is a record"
    m = _TRAILER_BODY_RE.match(lines[0])
    if not m:
        return None, None, (f"`Director-doc:{lines[0]}` is not `<kind> -- <reason>` with kind one "
                            f"of {', '.join(KINDS)} and a non-empty reason")
    return m.group(1).lower(), m.group(2), None


def verdict(message: str, content_changes: list[str]) -> tuple[bool, str]:
    """(passes, explanation). Pure. `content_changes` is `owed(...)` plus any mission-block line."""
    if not content_changes:
        return True, "no director document's content changed"
    kind, reason, refusal = parse_trailer(message)
    if refusal is None:
        return True, f"director document changed under a `{kind}` record"
    return False, (
        "This commit changes the content of a director document:\n"
        + "".join(f"    {c}\n" for c in content_changes)
        + f"and the message has {refusal}.\n\n"
        "A change to the INTENT of a director document is the director's. Do not land it: write it "
        "to `docs/staging/` as a proposal (`SEAT_PROPOSAL_<SUBJECT>_<date>.md`), raise it on "
        "`docs/direction/DIRECTION.yaml`'s `for_the_director` list "
        "(`python3 -m background.director_concerns --raise ...`), and carry on with other work.\n\n"
        "If it changes no intent, say which kind it is in ONE line and it lands:\n"
        "    Director-doc: correction -- <what was factually wrong, and the evidence>\n"
        "    Director-doc: his-words -- <where his words come from: console date, NTFY file, ruling>\n"
        "    Director-doc: record -- <bookkeeping that changes no intent>\n"
        "A plain factual correction is yours to make (director, 2026-10-04) -- and say what you "
        "corrected beside the claim in the document itself."
    )


# --- the git reads: read-only plumbing, GIT_PREFIX stripped (the sibling gates' H24 discipline) ---

def _git(*args: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "GIT_PREFIX"}
    return subprocess.run(["git", *args], env=env, capture_output=True, text=True, timeout=120)


def _show(spec: str) -> str | None:
    r = _git("show", spec)
    return r.stdout if r.returncode == 0 else None


def _blob(spec: str) -> str | None:
    r = _git("rev-parse", "--verify", "-q", spec)
    return r.stdout.strip() if r.returncode == 0 else None


def merging_parents() -> list[str]:
    """The other parents of a merge being committed. Read via `--git-path` so a linked worktree's
    own `MERGE_HEAD` is found (the reason `write_time_gate.merging_parents` reads `--git-dir`)."""
    r = _git("rev-parse", "--git-path", "MERGE_HEAD")
    if r.returncode != 0:
        return []
    try:
        raw = Path(r.stdout.strip()).read_text(encoding="utf-8")
    except OSError:
        return []
    return [ln.strip() for ln in raw.splitlines() if ln.strip()]


def staged_content_changes() -> list[str]:
    """What this commit's index does to director documents, minus what another merge parent carries.

    Raises when git cannot answer -- the caller fails open on that, loudly.
    """
    has_head = _git("rev-parse", "--verify", "-q", "HEAD").returncode == 0
    base = "HEAD" if has_head else "4b825dc642cb6eb9a060e54bf8d69288fbee4904"  # the empty tree
    r = _git("diff", "--cached", "-M", "--name-status", "-z", base)
    if r.returncode != 0:
        raise RuntimeError(f"git diff --cached failed (rc={r.returncode}): {r.stderr.strip()[:200]}")
    changes = parse_name_status(r.stdout)
    deleted = [c for c in changes if c.status == "D" and is_director_document(c.old or "")]
    resulting: set[str] = set()
    if deleted:
        archived = [ARCHIVE_DIR + PurePosixPath(c.old or "").name for c in deleted]
        ls = _git("ls-files", "--cached", "--", *archived)
        if ls.returncode != 0:
            raise RuntimeError(f"git ls-files failed: {ls.stderr.strip()[:200]}")
        resulting = {ln.strip() for ln in ls.stdout.splitlines() if ln.strip()}
    found = owed(changes, resulting)

    mission_moved = False
    if any(c.new == MISSION_FILE or c.old == MISSION_FILE for c in changes):
        new_block = mission_block(_show(f":{MISSION_FILE}"))
        old_block = mission_block(_show(f"HEAD:{MISSION_FILE}")) if has_head else None
        mission_moved = new_block != old_block

    parents = merging_parents()
    if parents:
        found = [c for c in found if not _a_parent_carries(c, parents)]
        if mission_moved:
            new_block = mission_block(_show(f":{MISSION_FILE}"))
            if any(mission_block(_show(f"{p}:{MISSION_FILE}")) == new_block for p in parents):
                mission_moved = False
    lines = [describe(c) for c in found]
    if mission_moved:
        lines.append(f"the mission statement in {MISSION_FILE} ('{MISSION_HEADING}' to '---')")
    return lines


def _a_parent_carries(c: Change, parents: list[str]) -> bool:
    """Does an other merge parent already hold this change's result? Unreadable -> no (strict)."""
    if c.status == "D":
        return any(_git("rev-parse", "--verify", "-q", p).returncode == 0
                   and _blob(f"{p}:{c.old}") is None for p in parents)
    staged = _blob(f":{c.new}")
    return staged is not None and any(_blob(f"{p}:{c.new}") == staged for p in parents)


def trailer_report(window: int = 500) -> dict:
    """How often each trailer kind was used, from the commit record itself (never from a store)."""
    r = _git("log", f"-{int(window)}", "--format=%x00%h%x01%B")
    if r.returncode != 0:
        raise RuntimeError(f"git log failed: {r.stderr.strip()[:200]}")
    counts = {k: 0 for k in KINDS}
    reasons: list[tuple[str, str, str]] = []
    for chunk in r.stdout.split("\x00"):
        if "\x01" not in chunk:
            continue
        sha, body = chunk.split("\x01", 1)
        kind, reason, refusal = parse_trailer(body)
        if refusal is not None:
            continue
        counts[kind] += 1
        if kind in ("record", "correction"):
            reasons.append((sha, kind, reason[:160]))
    return {"window": window, "counts": counts, "reasons": reasons}


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[1] == "--report":
        window = int(argv[2]) if len(argv) >= 3 else 500
        rep = trailer_report(window)
        c = rep["counts"]
        print(f"[director-doc-gate] over the last {rep['window']} commits: "
              + ", ".join(f"{k} {c[k]}" for k in KINDS) + ".")
        for sha, kind, reason in rep["reasons"]:
            print(f"    {sha} {kind} -- {reason}")
        return 0
    if len(argv) < 2:
        return 0
    try:
        message = Path(argv[1]).read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"[director-doc-gate] message unreadable, not blocking: {exc}", file=sys.stderr)
        return 0
    try:
        changes = staged_content_changes()
    except Exception as exc:  # noqa: BLE001
        # FAILS OPEN, LOUDLY -- see the module docstring. Never silently: "git could not answer"
        # and "nothing in scope" look identical from outside unless this line is printed.
        print(f"[director-doc-gate] git unreadable, not blocking: {exc}", file=sys.stderr)
        return 0
    ok, why = verdict(message, changes)
    if not ok:
        print("[director-doc-gate] COMMIT REFUSED.\n" + why, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
