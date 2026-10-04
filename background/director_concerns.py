"""The director's concerns list: raise one with a proposal, carry it until he answers, never idle.

Director, 2026-10-04: *"Escalate with a proposal, and don't wait: concerns about strategy, vision or
canon intent. Raise it, propose the change or ask me to investigate, then carry on with everything
else. An open question to me sits in a list and never blocks the queue."* And the mechanism he
asked for: *"concerns written to the direction file's for_the_director list, with the seat never
idling on one."*

THE LIST IS `DIRECTION.yaml`'s `for_the_director`, and that record is rewritten by the orienting
seat every stretch. So a concern written there would vanish at the next rewrite unless something
carries it. Three halves, each a mechanism:

  * THIS CLI writes a row with a stable `id`, refuses one with no proposal, and runs
    `recommendation_guard.check_message` over `what` + `proposal` so a bare ask never enters the
    list. It edits ONLY the `for_the_director` block of the file, so the rest of the record stays
    byte-identical, and it never commits -- it prints the pathspec to land.
  * `direction.validate` refuses a row without an id, a what, a proposal and a status, and a
    closed row without a resolution.
  * `delivery_seat.orient` refuses a new record that DROPS an open row (`carry_problems` below),
    restores the previous record so the row is not lost to the overwrite, and pages only for ids
    the previous oriented record had not already carried (`new_open_ids`).

NEVER BLOCKS THE QUEUE: nothing here reads the draw. `direction.validate` requires a non-empty
`focus` on every record, open concerns or not, so the seat cannot answer an open question by
stopping work.

KNOWN GAP, stated rather than hidden: a row raised by this CLI WHILE an orienting session is
running is written to a file the session is about to overwrite, and the seat's carry check compares
against the record it read before the session started. Raise between orientations, or re-raise.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from background import direction as direction_mod  # noqa: E402

KEY = "for_the_director"
_TOP_LEVEL_KEY = re.compile(r"^[A-Za-z_][\w-]*:")


class ConcernRefused(ValueError):
    """A concern that cannot enter the list, with the reason in the message."""


def read_raw(path: Path | None = None) -> dict | None:
    """The record as parsed YAML, or None. Never raises: the seat calls this on its hot path."""
    try:
        import yaml
        raw = yaml.safe_load((path or direction_mod.DIRECTION_PATH).read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 -- missing, unreadable and malformed all mean "no rows"
        return None
    return raw if isinstance(raw, dict) else None


def rows_of(record) -> list[dict]:
    rows = record.get(KEY) if isinstance(record, dict) else None
    return [r for r in rows if isinstance(r, dict)] if isinstance(rows, list) else []


def open_rows(record) -> list[dict]:
    """The concerns still waiting on the director, in the record's order."""
    return [dict(r) for r in rows_of(record) if r.get("status") == "open"]


def carry_problems(before, after) -> list[str]:
    """Every OPEN row of `before` that `after` fails to carry, as a refusal reason.

    Carried means: the same `id` is present, and either it is still `open` with its `what` and
    `proposal` unchanged, or it is `answered`/`withdrawn` (whose `resolution` `validate` requires).
    A reworded open row is refused because the director may be reading the old words: a concern
    changes by being withdrawn and raised again, never by being edited under him.
    """
    after_by_id = {str(r.get("id")): r for r in rows_of(after) if r.get("id")}
    problems = []
    for row in open_rows(before):
        rid = str(row.get("id") or "")
        if not rid:
            continue
        new = after_by_id.get(rid)
        if new is None:
            problems.append(
                f"for_the_director dropped the open concern {rid!r} -- an open concern is carried "
                "forward verbatim until it is answered or withdrawn with a resolution, or it "
                "vanishes from the director's list unanswered")
        elif new.get("status") == "open" and any(
                str(new.get(k) or "").strip() != str(row.get(k) or "").strip()
                for k in ("what", "proposal")):
            problems.append(
                f"for_the_director rewrote the open concern {rid!r} -- carry it verbatim, or "
                "withdraw it with a resolution and raise the new wording under a new id")
    return problems


def new_open_ids(previous_ids, after) -> list[str]:
    """Open concern ids in `after` that `previous_ids` did not carry -- the ones to page about.

    `previous_ids` is what the last ORIENTED decision row recorded, not the file on disk: a row
    this CLI wrote between orientations is on disk before the seat runs, and keying to the file
    would mean it is never paged at all.
    """
    seen = {str(i) for i in (previous_ids or ())}
    return [str(r["id"]) for r in open_rows(after) if r.get("id") and str(r["id"]) not in seen]


# ── THE END-TO-END CHECK, which is where most concerns should come from ──────────────────────
#
# Director, 2026-10-04: *"Own the end-to-end check: canon, logic, work and findings read together,
# as hypotheses under test, stated and unstated. When something surprises you, consider every
# explanation the evidence allows -- the world wrong, the maths wrong, me wrong, it not being that
# simple, or something none of us has thought of. Rank them by evidence, not convenience."* Asked
# for at three triggers: the Monday retrospective (`weekly_rhythm.close` refuses an unfilled one),
# an atom reaching its target level (`gate_authorization.record_level_up_self_certified` refuses a
# provenance with no `End-to-end:` clause), and a repeating alarm (`alarm_repetition.escalate`
# writes this section into the finding). ONE TEMPLATE, here, so the three cannot drift apart.

END_TO_END_HEADING = "## End-to-end check"
END_TO_END_TEMPLATE = (
    "_Template -- replace this paragraph with the check itself._ Read the canon "
    "(`docs/design/DIRECTOR_CANON*.md`, `docs/staging/DIRECTOR_CANON_*`, "
    "`docs/design/THE_MODEL_ON_A_PAGE.md`, `CLAUDE.md`), the logic, and the work and findings "
    "in question TOGETHER, as hypotheses under test, stated and unstated. For each surprise, list "
    "every explanation the evidence allows -- the world wrong, the maths wrong, the director "
    "wrong, it not being that simple, something none of us has thought of -- ranked by evidence, "
    "not convenience. Raise each resulting concern with `python3 -m background.director_concerns "
    "--raise --kind ... --what ... --proposal ...` and carry on; it never blocks the work."
)


def end_to_end_section(placeholder: str = "- ") -> list[str]:
    """The section as document lines, ready to splice into a staged document."""
    return [END_TO_END_HEADING, "", END_TO_END_TEMPLATE, "", placeholder, ""]


def end_to_end_unfilled(text: str) -> str | None:
    """Why `text`'s end-to-end section does not count as done, or None when it does.

    Filled means: the heading is there, and once the template paragraph and empty list markers are
    taken out, something written by a person is left before the next heading or rule. Keyed to
    WHAT IS LEFT, not to whether the template was deleted -- a reader who writes the check under
    the template has done it, and one who deletes the template and writes nothing has not.
    """
    lines = (text or "").splitlines()
    try:
        start = next(i for i, ln in enumerate(lines) if ln.strip() == END_TO_END_HEADING)
    except StopIteration:
        return f"it has no `{END_TO_END_HEADING}` section"
    body = []
    for ln in lines[start + 1:]:
        if ln.startswith("## ") or ln.strip() == "---":
            break
        body.append(ln)
    left = " ".join(" ".join(body).replace(END_TO_END_TEMPLATE, " ").split())
    left = re.sub(r"(^|\s)[-*0-9.]+(?=\s|$)", " ", left).strip()
    if not left:
        return f"its `{END_TO_END_HEADING}` section is still only the template"
    return None


def _slug(text: str) -> str:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return "-".join(words[:7]) or "concern"


def _unique_id(base: str, taken: set[str]) -> str:
    rid, n = base, 2
    while rid in taken:
        rid, n = f"{base}-{n}", n + 1
    return rid


def _render_block(rows: list[dict]) -> str:
    import yaml
    if not rows:
        return f"{KEY}: []\n"
    return yaml.safe_dump({KEY: rows}, sort_keys=False, allow_unicode=True, width=100)


def _replace_block(text: str, rows: list[dict]) -> str:
    """`text` with ONLY its top-level `for_the_director` block replaced (or appended)."""
    lines = text.splitlines(keepends=True)
    start = next((i for i, ln in enumerate(lines) if ln.startswith(f"{KEY}:")), None)
    block = _render_block(rows)
    if start is None:
        sep = "" if not text or text.endswith("\n") else "\n"
        return text + sep + block
    end = start + 1
    while end < len(lines) and not _TOP_LEVEL_KEY.match(lines[end]):
        end += 1
    return "".join(lines[:start]) + block + "".join(lines[end:])


def _write(path: Path, before_text: str, rows: list[dict]) -> None:
    """Write, but only if the edit introduces NO new `validate` refusal. A record that was already
    refused for some other reason is not this CLI's to repair, and must not stop a concern being
    raised -- so the comparison is before-vs-after, not after-is-clean."""
    import yaml
    new_text = _replace_block(before_text, rows)
    before_problems = set(direction_mod.validate(yaml.safe_load(before_text)))
    introduced = [p for p in direction_mod.validate(yaml.safe_load(new_text))
                  if p not in before_problems]
    if introduced:
        raise ConcernRefused("the edit would make the direction record refuse: "
                             + "; ".join(introduced))
    path.write_text(new_text, encoding="utf-8")


def _today(now: datetime | None) -> str:
    return (now or datetime.now(timezone.utc)).date().isoformat()


def raise_concern(kind: str, what: str, proposal: str, evidence: str | None = None, *,
                  path: Path | None = None, now: datetime | None = None) -> dict:
    """Append an OPEN concern. Refuses one with no proposal, an unknown kind, or a bare ask."""
    from background.recommendation_guard import RecommendationRequired, check_message

    path = path or direction_mod.DIRECTION_PATH
    what, proposal = (what or "").strip(), (proposal or "").strip()
    if kind not in direction_mod.CONCERN_KINDS:
        raise ConcernRefused(f"kind must be one of {', '.join(direction_mod.CONCERN_KINDS)}")
    if not what:
        raise ConcernRefused("a concern needs a what")
    if not proposal:
        raise ConcernRefused(
            "a concern needs a proposal -- the change you propose, or 'investigate: <what>'. "
            "The director's rule: never ask without recommending")
    try:
        check_message(f"{what} {proposal}")
    except RecommendationRequired as exc:
        raise ConcernRefused(
            "recommendation_guard refused it as a bare ask -- state the concern and what you "
            f"propose rather than asking: {exc}") from exc
    text = path.read_text(encoding="utf-8")
    record = read_raw(path)
    if record is None:
        raise ConcernRefused(f"{path} is not a readable direction record")
    rows = [dict(r) for r in rows_of(record)]
    row = {"id": _unique_id(_slug(what), {str(r.get("id")) for r in rows}),
           "raised": _today(now), "kind": kind, "what": what, "proposal": proposal,
           "status": "open", "resolution": ""}
    if evidence:
        row["evidence"] = evidence.strip()
    _write(path, text, rows + [row])
    return row


def resolve(concern_id: str, status: str, resolution: str, *, path: Path | None = None,
            now: datetime | None = None) -> dict:
    """Mark a concern answered or withdrawn. The resolution is required and is dated."""
    path = path or direction_mod.DIRECTION_PATH
    if status not in ("answered", "withdrawn"):
        raise ConcernRefused("a concern is resolved as answered or withdrawn")
    if not (resolution or "").strip():
        raise ConcernRefused(f"{status} needs a resolution -- his words, or why it was withdrawn")
    text = path.read_text(encoding="utf-8")
    rows = [dict(r) for r in rows_of(read_raw(path))]
    hit = [r for r in rows if str(r.get("id")) == concern_id]
    if not hit:
        raise ConcernRefused(f"no concern with id {concern_id!r} in {path.name}")
    hit[0].update({"status": status, "resolution": resolution.strip(), "resolved": _today(now)})
    _write(path, text, rows)
    return hit[0]


def _pathspec_note() -> str:
    path = direction_mod.DIRECTION_PATH
    rel = path.relative_to(PROJECT_DIR) if path.is_relative_to(PROJECT_DIR) else path
    return (f"Not committed. Land it by pathspec: python3 -u -m tools.surgical_land -m '<why>' "
            f"{rel}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    act = ap.add_mutually_exclusive_group(required=True)
    act.add_argument("--raise", dest="raise_", action="store_true", help="raise a new concern")
    act.add_argument("--answer", metavar="ID", help="record the director's answer")
    act.add_argument("--withdraw", metavar="ID", help="withdraw a concern, with the reason")
    act.add_argument("--list", action="store_true", help="print every concern")
    ap.add_argument("--kind", choices=direction_mod.CONCERN_KINDS)
    ap.add_argument("--what")
    ap.add_argument("--proposal")
    ap.add_argument("--evidence")
    ap.add_argument("--resolution")
    args = ap.parse_args(argv)
    try:
        if args.list:
            for r in rows_of(read_raw()):
                print("[{}] {} ({}, raised {}): {}\n    proposal: {}{}".format(
                    r.get("status"), r.get("id"), r.get("kind"), r.get("raised"), r.get("what"),
                    r.get("proposal"),
                    f"\n    resolution: {r['resolution']}" if r.get("resolution") else ""))
            return 0
        if args.raise_:
            if not args.kind:
                raise ConcernRefused("--raise needs --kind")
            row = raise_concern(args.kind, args.what or "", args.proposal or "", args.evidence)
        else:
            rid = args.answer or args.withdraw
            row = resolve(rid, "answered" if args.answer else "withdrawn", args.resolution or "")
    except ConcernRefused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    print(f"{row['status']}: {row['id']}")
    print(_pathspec_note())
    return 0


if __name__ == "__main__":
    # SEAT GUARD, FIRST ACT: this writes the seat's direction record, so never on a foreign tree.
    from background._seat import refuse_if_foreign

    refuse_if_foreign("director_concerns")
    raise SystemExit(main())
