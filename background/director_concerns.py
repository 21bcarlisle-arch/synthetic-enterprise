"""The director's concerns list: raise one with a proposal, carry it until he answers, never idle.

Director, 2026-10-04: *"Escalate with a proposal, and don't wait: concerns about strategy, vision or
canon intent. Raise it, propose the change or ask me to investigate, then carry on with everything
else. An open question to me sits in a list and never blocks the queue."* And the mechanism he
asked for: *"concerns written to the direction file's for_the_director list, with the seat never
idling on one."*

THE LIST IS `DIRECTION.yaml`'s `for_the_director`, and that record is rewritten by the orienting
seat every stretch. So a concern written there would vanish at the next rewrite unless something
carries it. Three halves, each a mechanism:

  * THIS CLI writes a row with a stable `id`, refuses one with no proposal or no recommendation
    (director, 19 Oct: reserved items too arrive with "I recommend X"), refuses a switch-on his
    23 Oct ruling made the machine's own (`switch_on_refusal`), and runs
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
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
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


def read_origin_raw(root: Path | None = None) -> dict | None:
    """`origin/main`'s record as parsed YAML, or None. The local ref, not a fetch: this is on the
    seat's hot path, and the reconciler fetches far more often than the seat orients."""
    path = direction_mod.DIRECTION_PATH
    root = root or PROJECT_DIR
    try:
        import yaml
        out = subprocess.run(["git", "show", f"origin/main:{path.relative_to(root).as_posix()}"],
                             cwd=str(root), capture_output=True, timeout=60)
        raw = yaml.safe_load(out.stdout) if out.returncode == 0 else None
    except Exception:  # noqa: BLE001 -- no origin copy means only the working copy's rows count
        return None
    return raw if isinstance(raw, dict) else None


def open_rows_on_either(here, origin) -> list[dict]:
    """The open concerns of the working copy, then origin's open ones it does not hold.

    THE DIRECTOR READS ORIGIN, and the shared checkout lags it: a row another lane landed on
    origin is missing from the working copy, so a brief built from the working copy alone omits
    it, and a record the session then carries verbatim deletes it from his list (2026-10-05,
    four listed against six on origin). An id that EITHER copy has answered or withdrawn is not
    open: whichever side is ahead holds the resolution, and listing it would re-open his answer."""
    closed = {str(r.get("id")) for rec in (here, origin) for r in rows_of(rec)
              if r.get("id") and r.get("status") != "open"}
    out, seen = [], set()
    for row in open_rows(here) + open_rows(origin):
        rid = str(row.get("id") or "")
        if rid in closed or (rid and rid in seen):
            continue
        seen.add(rid)
        out.append(row)
    return out


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
                # A recommendation may be ADDED to a carried row (the 19 Oct backfill), never
                # dropped or reworded under him once it is there.
                for k in ("what", "proposal") + (
                    ("recommendation",) if str(row.get("recommendation") or "").strip() else ())):
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


def _render_block(rows: list[dict], key: str = KEY) -> str:
    import yaml
    if not rows:
        return f"{key}: []\n"
    return yaml.safe_dump({key: rows}, sort_keys=False, allow_unicode=True, width=100)


def _replace_block(text: str, rows: list[dict], key: str = KEY) -> str:
    """`text` with ONLY its top-level `key` block replaced (or appended)."""
    lines = text.splitlines(keepends=True)
    start = next((i for i, ln in enumerate(lines) if ln.startswith(f"{key}:")), None)
    block = _render_block(rows, key)
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


# Director's ruling, 23 Oct 2026 07:03 BST ("Great. All good. Do these.", canon G9): a default-off
# switch whose pre-registered rule is met is the machine's to turn on, NOT a question for him -- the
# annualised advance sat in this list for a day as exactly that. Phrase-keyed on purpose: the CLI
# cannot grade a prereg, so it refuses the SHAPE and lets the raiser say why a switch is outside the
# ruling (it changes a ruling, a curriculum value or a reserved action, or the world after results).
_A_SWITCH = re.compile(r"\bDecisionPolicy\.\w+|\bswitch(?:es|ed)?\b|\bdefault\b", re.I)
_TURNED_ON = re.compile(
    r"\bon by default\b|\bdefault[- ]on\b|\b(?:turn|switch|flip)(?:s|ed|ing)?\b[^.;]{0,90}?\bon\b",
    re.I)
OUTSIDE_THE_RULING = "outside the 23 Oct ruling:"


def switch_on_refusal(kind: str, *texts: str) -> str | None:
    """The reason a raise is the machine's own switch-on under the 23 Oct ruling, or None.

    A `reserved` concern always reaches him. Any other raise that proposes turning a switch on is
    refused unless one of its texts carries `outside the 23 Oct ruling: <why>`."""
    if kind == "reserved":
        return None
    text = " ".join(t or "" for t in texts)
    if not (_A_SWITCH.search(text) and _TURNED_ON.search(text)):
        return None
    if re.search(re.escape(OUTSIDE_THE_RULING) + r"\s*\S", text, re.I):
        return None
    return ("this proposes turning a switch on, and under the director's ruling of 23 Oct (canon G9, "
            "'Great. All good. Do these.') a default-off switch whose pre-registered rule was fixed "
            "before its arms ran and is met is the machine's to turn on: flip it, put the grade, the "
            "rule and the switch-on on one record with a control that reds if the default reverts, "
            "and report it in the stretch log. A refuted rule keeps it off on the same record. If it "
            "changes a ruling, a curriculum value or a reserved action, or the world after supplier "
            f"results were seen, say so in the text as '{OUTSIDE_THE_RULING} <why>' and raise again")


def _today(now: datetime | None) -> str:
    return (now or datetime.now(timezone.utc)).date().isoformat()


def raise_concern(kind: str, what: str, proposal: str, evidence: str | None = None, *,
                  recommendation: str = "", g5_class: str | None = None, path: Path | None = None,
                  now: datetime | None = None) -> dict:
    """Append an OPEN concern. Refuses one with no proposal, no recommendation, an unknown kind, a
    bare ask, or a `reserved` one that names no G5 class (and a G5 class on any other kind)."""
    from background.recommendation_guard import RecommendationRequired, check_message

    path = path or direction_mod.DIRECTION_PATH
    what, proposal = (what or "").strip(), (proposal or "").strip()
    if kind not in direction_mod.CONCERN_KINDS:
        raise ConcernRefused(f"kind must be one of {', '.join(direction_mod.CONCERN_KINDS)}")
    if not what:
        raise ConcernRefused("a concern needs a what")
    if kind == "reserved" and g5_class not in direction_mod.g5_classes():
        raise ConcernRefused(
            f"a reserved concern names its G5 class, one of {', '.join(direction_mod.g5_classes())}"
            f" (got {g5_class!r}). If it is none of them it is not reserved: act, record how to "
            "reverse it, and say what you did (canon G5)")
    if kind != "reserved" and g5_class:
        raise ConcernRefused(f"a {kind} concern carries no G5 class; raise it as reserved if it is")
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
    recommendation = (recommendation or "").strip()
    machines = switch_on_refusal(kind, what, proposal, recommendation)
    if machines:
        raise ConcernRefused(machines)
    lacks = direction_mod.concern_lacks_recommendation(
        {"id": "the new concern", "status": "open", "recommendation": recommendation})
    if lacks:
        raise ConcernRefused(lacks)
    text = path.read_text(encoding="utf-8")
    record = read_raw(path)
    if record is None:
        raise ConcernRefused(f"{path} is not a readable direction record")
    rows = [dict(r) for r in rows_of(record)]
    row = {"id": _unique_id(_slug(what), {str(r.get("id")) for r in rows}),
           "raised": _today(now), "kind": kind, "what": what, "proposal": proposal,
           "recommendation": recommendation, "status": "open", "resolution": ""}
    if g5_class:
        row["g5_class"] = g5_class
    if evidence:
        row["evidence"] = evidence.strip()
    _write(path, text, rows + [row])
    return row


def resolve(concern_id: str, status: str, resolution: str, *, path: Path | None = None,
            now: datetime | None = None, commitment: dict | None = None,
            no_action: str | None = None) -> dict:
    """Mark a concern answered or withdrawn. The resolution is required and is dated, and from
    `CLOSE_COMMITMENT_FROM` the close names what it commits the machine to, or why nothing."""
    path = path or direction_mod.DIRECTION_PATH
    if status not in ("answered", "withdrawn"):
        raise ConcernRefused("a concern is resolved as answered or withdrawn")
    if not (resolution or "").strip():
        raise ConcernRefused(f"{status} needs a resolution -- his words, or why it was withdrawn")
    closing = {"status": status, "resolution": resolution.strip(), "resolved": _today(now)}
    if commitment:
        closing["commitment"] = {k: str(commitment.get(k) or "").strip() for k in COMMITMENT_KEYS}
    if (no_action or "").strip():
        closing["no_action"] = no_action.strip()
    lacks = close_lacks_commitment(closing)
    if lacks:
        raise ConcernRefused(lacks)
    text = path.read_text(encoding="utf-8")
    rows = [dict(r) for r in rows_of(read_raw(path))]
    hit = [r for r in rows if str(r.get("id")) == concern_id]
    if not hit:
        raise ConcernRefused(f"no concern with id {concern_id!r} in {path.name}")
    hit[0].update(closing)
    _write(path, text, rows)
    return hit[0]


# ── A CLOSE THAT COMMITS IS CHECKED AGAINST DONE ─────────────────────────────────────────────
#
# Director, 28 Oct 06:39: *"why are actions for me not getting flagged better and reminded?"* --
# and 06:44, on the advisor's recommendation that closes are checked against done: *"Do it."* The
# case: `reading-reviewer-trial-your-08-56-yes` was closed on 26 Oct as "the trial as proposed" and
# two days later nothing had run it. The no-caller class, applied to decisions instead of code.
#
# NOT A PHRASE CLASSIFIER. Measured on decisions.jsonl the same morning: 28 of 42 concern ids were
# closed and nearly every resolution commits the machine to act ("Agree all", "approved", "Do
# these"), so no reading of the words can pick out the commitments. The rule is the PROPERTY: a
# close from `CLOSE_COMMITMENT_FROM` carries `commitment: {work_id, done_means, due}` or
# `no_action: <reason>`, and a close carrying neither is itself the debt -- listed as unstated,
# never refused, because a refused orientation loses the whole stretch's direction for one row.
# DATED FROM THE RULE'S START so the historical closes do not come back as noise.
#
# DONE IS A LANDING BOUND TO THE WORK ID after the close (`delivery_lane.last_landing`), the same
# binding every promoted landing already writes. Nothing reads the words of `done_means`; it is
# there for the reader of the note.
#
# WHERE THE CLOSE IS FOUND. A closed row leaves `DIRECTION.yaml` at the next orientation, and a row
# closed BETWEEN orientations never reached `decisions.jsonl` at all (the 26 Oct reader close is
# such a row: its last recorded state is `open`). So `delivery_seat.orient` records every closed
# row it was handed under the decision row's `closes`, and this reads that history plus both live
# copies of the record.

CLOSE_COMMITMENT_FROM = "2026-10-28"
COMMITMENT_KEYS = ("work_id", "done_means", "due")


def _iso_day(value) -> str | None:
    try:
        return datetime.fromisoformat(str(value)[:10]).date().isoformat()
    except (TypeError, ValueError):
        return None


def close_lacks_commitment(row: dict) -> str | None:
    """Why a closed row's commitment is not usable, or None. Applies only from the rule's start."""
    resolved = _iso_day(row.get("resolved"))
    if row.get("status") == "open" or (resolved and resolved < CLOSE_COMMITMENT_FROM):
        return None
    if str(row.get("no_action") or "").strip():
        return None
    c = row.get("commitment")
    if not isinstance(c, dict):
        return ("a close names what it commits the machine to -- commitment {work_id, "
                "done_means, due} -- or says no_action: <reason>")
    missing = [k for k in COMMITMENT_KEYS if not str(c.get(k) or "").strip()]
    if missing:
        return f"the commitment has no {', '.join(missing)}"
    due = _iso_day(c.get("due"))
    if due is None:
        return f"the commitment's due {c.get('due')!r} is not a date"
    if resolved and due < resolved:
        return f"the commitment is due {due}, before the close itself ({resolved})"
    return None


def closed_rows(record) -> list[dict]:
    return [dict(r) for r in rows_of(record) if r.get("id") and r.get("status") != "open"]


def committed_revisions(since: str, root: Path | None = None) -> list[tuple[str, dict]]:
    """`(commit day, record)` for every committed revision of DIRECTION.yaml since `since`, oldest
    first. Bounded by date, so the walk stays a few dozen revisions. Never raises: git silent or a
    revision that will not parse gives fewer rows."""
    root = root or PROJECT_DIR
    rel = direction_mod.DIRECTION_PATH.relative_to(PROJECT_DIR).as_posix()
    try:
        import yaml
        log = subprocess.run(["git", "log", f"--since={since}", "--format=%H %cI", "--", rel],
                             cwd=str(root), capture_output=True, text=True, timeout=60)
        out = []
        for line in reversed(log.stdout.split("\n") if log.returncode == 0 else []):
            if not line.strip():
                continue
            sha, when = line.split(" ", 1)
            shown = subprocess.run(["git", "show", f"{sha}:{rel}"], cwd=str(root),
                                   capture_output=True, text=True, timeout=60)
            try:
                rec = yaml.safe_load(shown.stdout) if shown.returncode == 0 else None
            except Exception:  # noqa: BLE001 -- one unparseable revision is one fewer source
                rec = None
            if isinstance(rec, dict):
                out.append((when[:10], rec))
        return out
    except Exception:  # noqa: BLE001
        return []


def closes_on_record(history: list[dict] | None = None, records=None,
                     today: str | None = None, revisions=None) -> dict[str, dict]:
    """Every closed concern, latest state per id, each with `closed_on`.

    `history` is decisions.jsonl oldest first; `revisions` the committed DIRECTION.yaml revisions
    since the rule's start or a week ago, whichever is earlier, as `(day, record)` (the 26 Oct
    reader close is only there); `records` the live copies (working, origin). A row with no
    `resolved` takes the first day it was seen closed, so an undated close is dated by the record
    rather than escaping the rule."""
    today = today or _today(None)
    if history is None:
        history = list(reversed(direction_mod.read_decisions(limit=10**6)))
    if revisions is None:
        week_ago = (datetime.fromisoformat(today).date() - timedelta(days=7)).isoformat()
        revisions = committed_revisions(min(CLOSE_COMMITMENT_FROM, week_ago))
    if records is None:
        records = (read_raw(), read_origin_raw())
    out: dict[str, dict] = {}
    first_seen: dict[str, str] = {}

    def take(row, seen_on):
        if not isinstance(row, dict) or not row.get("id") or row.get("status") in (None, "open"):
            return
        rid = str(row["id"])
        first_seen.setdefault(rid, seen_on)
        merged = dict(out.get(rid) or {})
        merged.update({k: v for k, v in row.items() if v not in (None, "")})
        merged["closed_on"] = _iso_day(merged.get("resolved")) or first_seen[rid]
        out[rid] = merged

    for d in history:
        seen_on = _iso_day(d.get("at")) or today
        for row in list(d.get("for_the_director") or []) + list(d.get("closes") or []):
            take(row, seen_on)
    for day, rec in revisions:
        for row in closed_rows(rec):
            take(row, day)
    for rec in records:
        for row in closed_rows(rec):
            take(row, today)
    return out


def close_debts(closes: dict[str, dict], *, today: str | None = None, landing=None) -> list[dict]:
    """Each close from the rule's start, graded: met, pending, overdue, unstated or no_action.

    `landing(work_id) -> (epoch seconds, paths)` is `delivery_lane.last_landing` unless a test
    passes its own. Met means a landing bound to the work id on or after the close day."""
    if landing is None:
        from background.delivery_lane import last_landing as landing
    today = today or _today(None)
    out = []
    for rid, row in sorted(closes.items(), key=lambda kv: (kv[1].get("closed_on") or "", kv[0])):
        closed_on = row.get("closed_on") or today
        if closed_on < CLOSE_COMMITMENT_FROM:
            continue
        graded = {"id": rid, "status": row.get("status"), "closed_on": closed_on,
                  "resolution": row.get("resolution") or ""}
        if str(row.get("no_action") or "").strip():
            out.append({**graded, "state": "no_action", "why": str(row["no_action"]).strip()})
            continue
        lacks = close_lacks_commitment({**row, "resolved": closed_on})
        if lacks:
            out.append({**graded, "state": "unstated", "why": lacks})
            continue
        c = row["commitment"]
        at, _paths = landing(str(c["work_id"]))
        landed_on = (datetime.fromtimestamp(at, timezone.utc).date().isoformat()
                     if at else None)
        graded.update({"work_id": c["work_id"], "done_means": c["done_means"],
                       "due": _iso_day(c["due"]), "landed_on": landed_on})
        if landed_on and landed_on >= closed_on:
            graded["state"] = "met"
        elif graded["due"] < today:
            graded["state"] = "overdue"
        else:
            graded["state"] = "pending"
        out.append(graded)
    return out


def machine_debts(today: str | None = None) -> list[dict]:
    """The closes the machine owes: overdue, or closed without saying what done is."""
    return [d for d in close_debts(closes_on_record(today=today), today=today)
            if d["state"] in ("overdue", "unstated")]


def _debt_line(d: dict) -> str:
    if d["state"] == "unstated":
        return (f"- **{d['id']}** (closed {d['closed_on']}): the close says neither what done is "
                f"nor why nothing is owed -- {d['why']}.")
    return (f"- **{d['id']}** (closed {d['closed_on']}, due {d['due']}): {d['done_means']} "
            f"-- nothing has landed under `{d['work_id']}` since the close.")


def monday_note(now: datetime | None = None, *, closes: dict | None = None,
                open_rows_now: list[dict] | None = None, landing=None) -> str:
    """The director's Monday note: four sections, plain words, two minutes. Empty says none."""
    now = now or datetime.now(timezone.utc)
    today = _today(now)
    week_ago = (now.date() - timedelta(days=7)).isoformat()
    closes = closes_on_record(today=today) if closes is None else closes
    graded = {d["id"]: d for d in close_debts(closes, today=today, landing=landing)}
    if open_rows_now is None:
        open_rows_now = open_rows_on_either(read_raw(), read_origin_raw())
    this_week = [r for r in closes.values() if (r.get("closed_on") or "") >= week_ago]

    def landed(rid: str) -> str:
        d = graded.get(rid)
        if d is None:
            return "closed before closes carried a due date"
        return {"met": f"landed {d.get('landed_on')}",
                "pending": f"not landed yet, due {d.get('due')}",
                "overdue": f"OVERDUE since {d.get('due')}",
                "unstated": "no done-means or due date was recorded",
                "no_action": f"nothing to land: {d.get('why')}"}[d["state"]]

    def short(text, n=220) -> str:
        text = " ".join(str(text or "").split())
        return text if len(text) <= n else text[: n - 3].rsplit(" ", 1)[0].rstrip() + "..."

    lines = [f"# Monday note for the director -- {today}", "",
             "Written by the Monday step (`background/weekly_rhythm.py`); the live overdue list is "
             "`python3 -m background.director_concerns --overdue`.", ""]
    lines += ["## What you decided this week", ""]
    decided = [r for r in this_week if r.get("status") == "answered"]
    # ONE ANSWER CAN CLOSE SEVERAL QUESTIONS (26 Oct: four rows, one ruling). Printed per row, the
    # first 220 characters of that ruling repeat four times and name none of the questions, so a
    # shared answer is printed once with each question it closed beneath it.
    # Grouped by the line the reader SEES, not the whole text: the live four share the quoted
    # ruling and each ends in its own outcome ("Declined: ...", "Ruled: ...") past character 220,
    # so keying on the whole text never grouped them and the note printed the same cut-off quote
    # four times with none of the four outcomes. Each row's own remainder goes beneath the quote.
    by_answer: dict[str, list[dict]] = {}
    for r in decided:
        by_answer.setdefault(short(r.get("resolution")), []).append(r)
    for seen, rows in by_answer.items():
        if len(rows) == 1:
            lines.append(f"- **{rows[0]['id']}**: {seen} -- {landed(rows[0]['id'])}.")
            continue
        texts = [" ".join(str(r.get("resolution") or "").split()) for r in rows]
        shared = os.path.commonprefix(texts)
        if len(set(texts)) > 1:
            shared = shared.rsplit(" ", 1)[0]
        lines.append(f"- **One answer to {len(rows)} questions**: {short(shared)}")
        for r, text in zip(rows, texts):
            own = text[len(shared):].strip()
            lines.append(f"  - **{r['id']}**: {short(r.get('what'), 160)}"
                         + (f" -- {short(own, 200)}" if own else "") + f" -- {landed(r['id'])}.")
    if not decided:
        lines.append("None.")
    lines += ["", "## Waiting on you", ""]
    lines += [f"- **{r.get('id')}**: {short(r.get('what'))} -- {short(r.get('recommendation'))}"
              for r in open_rows_now] or ["None."]
    lines += ["", "## Closed on the seat's own recommendation", ""]
    own = [r for r in this_week if r.get("status") == "withdrawn"]
    # THE RECOMMENDATION, not the resolution: a seat close is closed ON its recommendation, and
    # the resolutions of one sweep share their opening words, so they read as nine identical lines.
    lines += [f"- **{r['id']}**: {short(r.get('recommendation') or r.get('proposal'), 200)} -- "
              f"{landed(r['id'])}." for r in own] or ["None."]
    lines += ["", "## Overdue (the machine's own debt, not yours)", ""]
    lines += [_debt_line(d) for d in graded.values() if d["state"] in ("overdue", "unstated")] \
        or ["None."]
    return "\n".join(lines) + "\n"


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
    act.add_argument("--overdue", action="store_true",
                     help="print the closes the machine owes: overdue, or with no done-means")
    act.add_argument("--monday-note", action="store_true", help="print the director's Monday note")
    ap.add_argument("--kind", choices=direction_mod.CONCERN_KINDS)
    ap.add_argument("--what")
    ap.add_argument("--proposal")
    ap.add_argument("--evidence")
    ap.add_argument("--recommendation",
                    help="'I recommend X', with the evidence, the trade-off, the holding position "
                         "until he rules and what would change it")
    ap.add_argument("--resolution")
    ap.add_argument("--g5-class", help="for --kind reserved: which G5 class it is")
    ap.add_argument("--work-id", help="closing: the claim id whose landing meets the commitment")
    ap.add_argument("--done-means", help="closing: what will have landed when it is done")
    ap.add_argument("--due", help="closing: the date it is due by (YYYY-MM-DD)")
    ap.add_argument("--no-action", help="closing: why this close commits the machine to nothing")
    args = ap.parse_args(argv)
    if args.overdue:
        debts = machine_debts()
        print("\n".join(_debt_line(d) for d in debts) if debts else "None overdue.")
        return 0
    if args.monday_note:
        print(monday_note(), end="")
        return 0
    try:
        if args.list:
            for r in rows_of(read_raw()):
                print("[{}] {} ({}, raised {}): {}\n    proposal: {}\n    recommendation: {}{}".format(
                    r.get("status"), r.get("id"), r.get("kind"), r.get("raised"), r.get("what"),
                    r.get("proposal"), r.get("recommendation") or "(none)",
                    f"\n    resolution: {r['resolution']}" if r.get("resolution") else ""))
            return 0
        if args.raise_:
            if not args.kind:
                raise ConcernRefused("--raise needs --kind")
            row = raise_concern(args.kind, args.what or "", args.proposal or "", args.evidence,
                                recommendation=args.recommendation or "",
                                g5_class=args.g5_class)
        else:
            rid = args.answer or args.withdraw
            commitment = ({"work_id": args.work_id, "done_means": args.done_means,
                           "due": args.due}
                          if args.work_id or args.done_means or args.due else None)
            row = resolve(rid, "answered" if args.answer else "withdrawn", args.resolution or "",
                          commitment=commitment, no_action=args.no_action)
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
