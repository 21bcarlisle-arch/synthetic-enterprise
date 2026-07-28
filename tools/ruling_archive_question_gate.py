"""ARCHIVE-BLOCK gate — DIRECTOR_RULING_NO_QUESTION_LEFT_UNANSWERED 2026-07-28, deliverable 1.

THE NON-NEGOTIABLE (ruling §2): *"it must be impossible to archive a ruling as consumed while it
carries an unanswered question, and that must be enforced MECHANICALLY rather than by discipline —
the lesson of every rule this project has: exhortations decay, mechanisms hold."*

This is that mechanism. A commit that moves a [DIRECTOR-RULING]/[STEER] into `docs/staging/done/`
(the archival act — "consumed") while that ruling still carries a BLOCKING question (status `open`
or `carried` — i.e. not actually answered) is STRUCTURALLY REFUSED, exactly like the level-promotion
and coherence gates. Detection-after-the-fact is not enough; the ruling forbids the archive itself.

INDEPENDENCE / REUSE (R15 anti-tautology): the question set and the blocking predicate are REUSED
verbatim from `background.open_question_register.blocking_questions_for_ruling` — the SAME logic the
daily note and any reader use. This gate does NOT re-implement extraction or the disposition rule,
so it cannot drift from them and cannot be a tautology (it reads the ruling body being archived + the
disposition register, two independent sources).

WHAT IT BLOCKS / ALLOWS:
  * a ruling/steer file ADDED at docs/staging/done/… (or RENAMED into it) that carries an open or
    carried question  ->  REJECT.
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
    _RULING_STEER_PREFIXES,
    _RULING_STEER_HEADER_RE,
    blocking_questions_for_ruling,
)

DONE_PREFIX = "docs/staging/done/"


def _env() -> dict:
    """Read-only git env: strip GIT_PREFIX so `:<path>` resolves from repo root; keep the rest."""
    return {k: v for k, v in os.environ.items() if k != "GIT_PREFIX"}


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(ROOT), env=_env(),
                          capture_output=True, text=True)


def archived_ruling_paths() -> list[str]:
    """Paths under docs/staging/done/ that this commit ADDS or RENAMES-IN (the archival act).

    `git diff --cached --name-status -M` yields `A\\tpath`, `M\\tpath`, or `R###\\told\\tnew`. We take
    the destination path for A/M/R when it lands under done/. A plain modification of a file already
    in done/ is NOT an archival (it's already archived) — but including M is the SAFE direction: if
    someone edits a done/ ruling to re-open a question it should still be caught, and a still-closed
    ruling passes anyway. FAIL toward catching more, never fewer."""
    r = _git("diff", "--cached", "--name-status", "-M")
    out: list[str] = []
    for line in r.stdout.splitlines():
        parts = line.split("\t")
        if not parts:
            continue
        status = parts[0]
        dest = parts[-1].strip()  # rename dest is the last field; A/M have the path there too
        if not dest.startswith(DONE_PREFIX):
            continue
        if status[:1] in ("A", "M", "R"):
            out.append(dest)
    return out


def _is_ruling_or_steer_name(path: str, head: str) -> bool:
    base = Path(path).name
    return base.startswith(_RULING_STEER_PREFIXES) or bool(_RULING_STEER_HEADER_RE.search(head))


def _staged_blob(path: str) -> str | None:
    r = _git("show", f":{path}")
    return r.stdout if r.returncode == 0 else None


def evaluate(paths: list[str], blob_reader=_staged_blob) -> tuple[int, str]:
    """Pure decision over the list of done/-bound paths. Returns (exit_code, message).

    R15 independence: delegates the blocking judgement to open_question_register — this function only
    routes files and formats the refusal. Injectable blob_reader lets the test drive it without git."""
    problems: list[str] = []
    for path in paths:
        head = blob_reader(path)
        if head is None:
            # Being archived into done/ but unreadable -> cannot verify -> fail-closed (REFUSE).
            problems.append(
                f"  • {path}: staged for archival to done/ but its staged content could not be read "
                f"— cannot verify it carries no open question (fail-closed)."
            )
            continue
        if not _is_ruling_or_steer_name(path, head[:600]):
            continue  # a non-ruling artefact landing in done/ is never blocked
        blocking = blocking_questions_for_ruling(Path(path).name, head)
        if blocking:
            qlines = "\n".join(
                f"      - [{b['status']}] {b['question'][:100]}" for b in blocking[:8]
            )
            problems.append(
                f"  • {Path(path).name}: carries {len(blocking)} unanswered question(s) — a ruling "
                f"is NOT consumed while any question is open/carried (ruling §1):\n{qlines}"
            )
    if problems:
        msg = (
            "\n[archive-question-gate] ❌ COMMIT REFUSED — DIRECTOR_RULING_NO_QUESTION_LEFT_UNANSWERED "
            "§2: a ruling may not be archived to done/ while it carries an unanswered question.\n"
            + "\n".join(problems)
            + "\n\n  To proceed: record a closing disposition (answered / unknown / not_measurable / "
            "wrong) for each question in docs/observability/open_question_register.json, then re-commit. "
            "A 'carried'-with-reason is NON-SILENT but still UNANSWERED — it does not unblock archival.\n"
        )
        return 1, msg
    return 0, ""


def main() -> int:
    paths = archived_ruling_paths()
    if not paths:
        return 0  # nothing being archived to done/ in this commit
    code, msg = evaluate(paths)
    if code != 0:
        sys.stderr.write(msg)
    return code


if __name__ == "__main__":
    sys.exit(main())
