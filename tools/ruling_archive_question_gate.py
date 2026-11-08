"""ARCHIVE-BLOCK gate — DIRECTOR_RULING_NO_QUESTION_LEFT_UNANSWERED 2026-07-28, deliverable 1.

THE NON-NEGOTIABLE (ruling §2): *"it must be impossible to archive a ruling as consumed while it
carries an unanswered question, and that must be enforced MECHANICALLY rather than by discipline —
the lesson of every rule this project has: exhortations decay, mechanisms hold."*

This is that mechanism. A commit that moves a [DIRECTOR-RULING]/[STEER] into an archive (see THE TWO ARCHIVES)
(the archival act — "consumed") while that ruling still carries a BLOCKING question (status `open`
or `carried` — i.e. not actually answered) is STRUCTURALLY REFUSED, exactly like the level-promotion
and coherence gates. Detection-after-the-fact is not enough; the ruling forbids the archive itself.

INDEPENDENCE / REUSE (R15 anti-tautology): the question set and the blocking predicate are REUSED
verbatim from `background.open_question_register.blocking_questions_for_ruling` — the SAME logic the
daily note and any reader use. This gate does NOT re-implement extraction or the disposition rule,
so it cannot drift from them and cannot be a tautology (it reads the ruling body being archived + the
disposition register, two independent sources).

THE TWO ARCHIVES (widened 2026-11-08): `docs/staging/done/` and `docs/staging/advisor/done/`. Since
October the advisor channel archives its rulings to the second, and a valid plant on 8 Nov showed
the gate refused there nothing it refused in the first.

WHAT IT BLOCKS / ALLOWS:
  * a ruling/steer file ADDED to either archive (or RENAMED into it) that carries an open or
    carried question  ->  REJECT.
  * an EDIT to a ruling already archived  ->  REJECT only for a blocking question the edit ADDS
    (one not blocking in the HEAD copy). 64 rulings were archived before the extractor read his
    quoted words, and their questions were answered in prose, not in the register; refusing every
    later correction to one of them would block an unrelated lane for a debt it did not create.
    An edit that re-opens or adds a question is still caught. A HEAD copy that cannot be read
    makes the edit an archival (fail-closed).
  * the same ruling once every question is CLOSED (answered / I-don't-know / not-measurable / wrong,
    recorded in docs/observability/open_question_register.json)  ->  ALLOW.
  * a ruling with NO questions at all  ->  ALLOW (nothing to block on).
  * a non-ruling file landing in done/, or any commit not touching done/  ->  ALLOW (never blocks).

FAIL-CLOSED (R15): if a file is being archived into done/ but its STAGED content cannot be read, the
gate REFUSES — an unverifiable archive may hide an unanswered question, and silently allowing it is
the fail-open pattern R15 forbids. A missing/corrupt disposition register makes every question
`open` (see open_question_register.load_dispositions), so it too fails toward REFUSE, never toward a
silent archive.

GIT-ENV SAFETY (H24): read-only plumbing only (`git diff --cached`, `git show :<path>` for the
staged blob). GIT_PREFIX is stripped so `:<path>` resolves from the repo root; GIT_INDEX_FILE is kept
because `:<path>` deliberately wants the commit's index — the staged content to inspect. No git WRITE
is ever run, so the gate cannot corrupt the in-progress commit.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from background.open_question_register import (  # noqa: E402
    _RULING_STEER_HEADER_RE,
    _RULING_STEER_PREFIXES,
    blocking_questions_for_ruling,
)

DONE_PREFIXES = ("docs/staging/done/", "docs/staging/advisor/done/")


def _env() -> dict:
    """Read-only git env: strip GIT_PREFIX so `:<path>` resolves from repo root; keep the rest."""
    return {k: v for k, v in os.environ.items() if k != "GIT_PREFIX"}


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(ROOT), env=_env(),
                          capture_output=True, text=True)


def archived_ruling_paths() -> tuple[list[str], list[str]]:
    """(archived, edited): paths under either archive that this commit ADDS or RENAMES-IN (the
    archival act), and paths already archived that it MODIFIES.

    `git diff --cached --name-status -M` yields `A\\tpath`, `M\\tpath`, or `R###\\told\\tnew`; the
    destination is the last field. A copy (`C`) is treated as an archival."""
    r = _git("diff", "--cached", "--name-status", "-M")
    archived: list[str] = []
    edited: list[str] = []
    for line in r.stdout.splitlines():
        parts = line.split("\t")
        if not parts:
            continue
        status = parts[0]
        dest = parts[-1].strip()
        if not dest.startswith(DONE_PREFIXES):
            continue
        if status[:1] in ("A", "R", "C"):
            archived.append(dest)
        elif status[:1] == "M":
            edited.append(dest)
    return archived, edited


def _is_ruling_or_steer_name(path: str, head: str) -> bool:
    base = Path(path).name
    return base.startswith(_RULING_STEER_PREFIXES) or bool(_RULING_STEER_HEADER_RE.search(head))


def _staged_blob(path: str) -> str | None:
    r = _git("show", f":{path}")
    return r.stdout if r.returncode == 0 else None


def _head_blob(path: str) -> str | None:
    r = _git("show", f"HEAD:{path}")
    return r.stdout if r.returncode == 0 else None


def evaluate(paths: list[str], blob_reader=_staged_blob, edited: list[str] = (),
             head_reader=_head_blob) -> tuple[int, str]:
    """Pure decision. `paths` are being archived; `edited` are already archived and being modified.
    Returns (exit_code, message).

    R15 independence: delegates the blocking judgement to open_question_register — this function only
    routes files and formats the refusal. Injectable readers let the test drive it without git."""
    problems: list[str] = []
    for path, is_edit in [(p, False) for p in paths] + [(p, True) for p in edited]:
        head = blob_reader(path)
        if head is None:
            problems.append(
                f"  • {path}: staged for an archive but its staged content could not be read "
                f"— cannot verify it carries no open question (fail-closed)."
            )
            continue
        if not _is_ruling_or_steer_name(path, head[:600]):
            continue  # a non-ruling artefact in an archive is never blocked
        name = Path(path).name
        blocking = blocking_questions_for_ruling(name, head)
        if is_edit and blocking:
            # An unreadable HEAD copy reads as empty, so every open question refuses (fail-closed).
            before = head_reader(path) or ""
            had = {b["key"] for b in blocking_questions_for_ruling(name, before)}
            blocking = [b for b in blocking if b["key"] not in had]
        if blocking:
            act = "this edit adds" if is_edit else "carries"
            qlines = "\n".join(
                f"      - [{b['status']}] {b['key']} {b['question'][:100]}" for b in blocking[:8]
            )
            problems.append(
                f"  • {path}: {act} {len(blocking)} unanswered question(s) in the director's quoted "
                f"words — a ruling is NOT consumed while any question is open/carried (ruling §1):\n{qlines}"
            )
    if problems:
        msg = (
            "\n[archive-question-gate] ❌ COMMIT REFUSED — DIRECTOR_RULING_NO_QUESTION_LEFT_UNANSWERED "
            "§2: a ruling may not be archived while it carries an unanswered question.\n"
            + "\n".join(problems)
            + "\n\n  To proceed: record a closing disposition (answered / unknown / not_measurable / "
            "wrong) for each question key in docs/observability/open_question_register.json, then "
            "re-commit. A 'carried'-with-reason is NON-SILENT but still UNANSWERED — it does not "
            "unblock archival.\n"
        )
        return 1, msg
    return 0, ""


def main() -> int:
    archived, edited = archived_ruling_paths()
    if not archived and not edited:
        return 0  # nothing entering or changing in an archive in this commit
    code, msg = evaluate(archived, edited=edited)
    if code != 0:
        sys.stderr.write(msg)
    return code


if __name__ == "__main__":
    sys.exit(main())
