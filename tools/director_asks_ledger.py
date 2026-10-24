"""The ledger of everything the director asked for, and whether it shipped.

Director, 24 Oct 2026 09:45 (advisor channel, DIRECTOR_STEER_A_LEDGER_OF_EVERYTHING_I_ASKED_FOR):
"Are there other things I've asked for this never finished shipping?? (Maybe for good reason, maybe
not?)" The front door's L2 diagram (ruled 9 Oct) and its live picture (27 Jul) had half shipped and
nothing could see it, because a director document left the queue by being MOVED to `done/` and the
move said nothing about whether the ask had shipped: 156 of the 159 in `docs/staging/done/` carry no
Done section at all.

Two sources, merged:

- the CENSUS, read from the tree: every `DIRECTOR_*` document in every staging folder, one row
  each. Where it sits says only what the queue did with it -- `open` (still in a queue folder),
  `closed_with_evidence` (in a done folder with a `## Done` section that names a commit or a path),
  `closed_without_evidence` (moved to done and nothing more);
- the RULINGS, `docs/direction/director_asks.yaml`, held by the delivery seat: what the record shows
  happened to an ask (`shipped`, `partly`, `not_started`, `superseded`, `declined`), its evidence and
  its next step. A ruling may also name an ask that has no document of its own (a canon s15 owed
  item, a ruling made in chat).

A census row is one DOCUMENT, not one distinct ask. Splitting documents into asks is the rulings'
job and is done row by row; until a document is ruled, its row says it is unruled rather than guess.
Readings of his usage, console transcripts and canon versions are record, not asks, and are counted
apart: the asks inside a console transcript are a named gap until they are itemised.

The control: an ask still open (`open`, `partly`, `not_started`) whose last movement -- the later of
the day it was asked and its ruling's `moved` date -- is more than 21 days old, and which
carries no `held` reason, is STALE. `--check` exits 1 naming each one, and the page shows the count.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
STAGING = "docs/staging"
RULINGS = "docs/direction/director_asks.yaml"
OUT_JSON = "site/data/director_asks.json"

# The steer's own number: "a control that reds when an ask has had no movement for 21 days".
NO_MOVEMENT_DAYS = 21
# Where a folder sends a document. Every other folder under staging is a queue.
DONE_FOLDERS = {"done", "advisor/done"}
# Document kinds that record rather than ask: his usage readings, console transcripts, canon versions.
RECORD_KINDS = ("DIRECTOR_READING_", "DIRECTOR_CONSOLE_", "DIRECTOR_CANON")
RULED = ("shipped", "partly", "not_started", "superseded", "declined")
STILL_OPEN = ("open", "partly", "not_started")
# A Done section names its evidence by a commit (7+ hex) or a path in the tree.
_EVIDENCE = re.compile(r"\b[0-9a-f]{7,40}\b|\b[\w.-]+/[\w./-]+\.\w+\b")
_DATE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def done_section(text):
    """The text under a `## Done` heading, or None when the document has none."""
    m = re.search(r"^## Done\b[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else None


def has_done_evidence(text):
    body = done_section(text)
    return bool(body and _EVIDENCE.search(body))


def _title(text, name):
    for line in text.splitlines():
        if line.startswith("# "):
            return re.sub(r"^#\s*(\[[^\]]*\]\s*)?", "", line).strip()
    return name


def _last_commit_days(root):
    """{basename: latest commit day} for every staging file, in one pass over history."""
    out = subprocess.run(["git", "-C", str(root), "log", "--format=@%cs", "--name-only", "--",
                          STAGING], capture_output=True, text=True).stdout
    seen, day = {}, None
    for line in out.splitlines():
        if line.startswith("@"):
            day = line[1:]
        elif line and day:
            seen.setdefault(Path(line).name, day)
    return seen


def census(root=ROOT):
    """(asks, record_counts): one row per DIRECTOR_* asking document under staging."""
    base = Path(root) / STAGING
    days = _last_commit_days(root)
    asks, record = [], {}
    for path in sorted(base.rglob("DIRECTOR_*.md")):
        name, folder = path.name, path.parent.relative_to(base).as_posix()
        kind = next((k for k in RECORD_KINDS if name.startswith(k)), None)
        if kind:
            record[kind.rstrip("_")] = record.get(kind.rstrip("_"), 0) + 1
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if folder in DONE_FOLDERS:
            state = "closed_with_evidence" if has_done_evidence(text) else "closed_without_evidence"
        else:
            state = "open"
        m = _DATE.search(name)
        asks.append({"id": name[:-3], "source": "{}/{}".format(STAGING, path.relative_to(base)),
                     "asked": m.group(1) if m else None, "ask": _title(text, name),
                     "state": state, "last_commit": days.get(name)})
    return asks, record


# Director documents moved to done before this day are grandfathered by the day they arrived, not by
# a list of names: the gate below is the steer's "a director document reaches done/ only with a Done
# section that links its evidence", and it binds every arrival from the day it was built.
DONE_EVIDENCE_FROM = "2026-10-25"


def _done_arrivals(root):
    """{path: first day it was committed under a done folder}. No rename detection: a move is the
    arrival, and git would otherwise report it as a rename and never as an add."""
    out = subprocess.run(["git", "-C", str(root), "log", "--no-renames", "--diff-filter=A",
                          "--format=@%cs", "--name-only", "--"]
                         + ["{}/{}".format(STAGING, d) for d in sorted(DONE_FOLDERS)],
                         capture_output=True, text=True).stdout
    seen, day = {}, None
    for line in out.splitlines():
        if line.startswith("@"):
            day = line[1:]
        elif line and day:
            seen[line] = day  # log runs newest first, so the last write is the first arrival
    return seen


def closed_without_evidence_since(root=ROOT, since=DONE_EVIDENCE_FROM):
    """Asking documents that reached a done folder on or after `since` with no evidenced Done
    section. A file not yet committed there arrives today."""
    arrivals, today = _done_arrivals(root), date.today().isoformat()
    asks, _ = census(root)
    return [a["source"] for a in asks if a["state"] == "closed_without_evidence"
            and arrivals.get(a["source"], today) >= since]


def load_rulings(root=ROOT):
    try:
        data = yaml.safe_load((Path(root) / RULINGS).read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return None
    return data.get("asks") or []


def merge(asks, rulings):
    """Rulings over the census, keyed by id; a ruling with no document becomes its own row."""
    by_id = {a["id"]: dict(a) for a in asks}
    for r in rulings:
        row = by_id.setdefault(r["id"], {"id": r["id"], "source": r.get("source"),
                                         "asked": r.get("asked"), "ask": r.get("ask"),
                                         "state": "open", "last_commit": None})
        for k in ("ask", "asked", "status", "evidence", "missing", "next_step", "moved", "held",
                  "superseded_by"):
            if r.get(k) is not None:
                row[k] = str(r[k]) if k in ("asked", "moved") else r[k]
    for row in by_id.values():
        row["status"] = row.get("status") or {"open": "open", "closed_with_evidence":
                                              "closed_with_evidence"}.get(row["state"],
                                                                          "closed_without_evidence")
    return sorted(by_id.values(), key=lambda r: (str(r.get("asked") or ""), r["id"]))


def last_movement(row):
    # Not the document's last commit: on 13 Oct one banner commit touched all fifteen July documents
    # still in progress, and a clock that a housekeeping edit resets cannot see an ask stand still.
    days = [str(d) for d in (row.get("asked"), row.get("moved")) if d]
    return max(days) if days else None


def stale(rows, today):
    """Open asks with no movement for NO_MOVEMENT_DAYS and no recorded reason for holding."""
    cutoff = (today - timedelta(days=NO_MOVEMENT_DAYS)).isoformat()
    return [r for r in rows if r["status"] in STILL_OPEN and not r.get("held")
            and (last_movement(r) or "0000") < cutoff]


def build(root=ROOT, today=None):
    today = today or date.today()
    asks, record = census(root)
    rulings = load_rulings(root)
    if rulings is None:
        return None
    rows = merge(asks, rulings)
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    late = stale(rows, today)
    return {"as_of": today.isoformat(), "no_movement_days": NO_MOVEMENT_DAYS, "counts": counts,
            "record_not_asks": record, "stale": [r["id"] for r in late], "rows": rows}


_LABEL = {"shipped": "shipped", "partly": "partly shipped", "not_started": "not started",
          "superseded": "superseded", "declined": "declined", "open": "open, not yet ruled",
          "closed_with_evidence": "closed, with a Done section naming its evidence",
          "closed_without_evidence": "closed with no evidence recorded"}
_ORDER = ("partly", "not_started", "open", "shipped", "superseded", "declined",
          "closed_with_evidence", "closed_without_evidence")


def _when(day):
    try:
        return date.fromisoformat(str(day)).strftime("%-d %b %Y")
    except ValueError:
        return "undated"


def _li(text):
    return "  <li>{}</li>".format(text)


def render_html(ledger):
    """The How it's built block: counts by status, the open asks with their next step, and the
    whole ledger one tap down. Every figure is the ledger's own, made at publish."""
    if ledger is None:
        return ("<p>The ledger of director asks could not be built at this publish ({} could not be "
                "read), so nothing is claimed about it.</p>".format(RULINGS))
    e, c, rows = html.escape, ledger["counts"], ledger["rows"]
    counts = ", ".join("<b>{}</b> {}".format(c[k], _LABEL[k]) for k in _ORDER if c.get(k))
    open_rows = [r for r in rows if r["status"] in STILL_OPEN]
    stale_ids = set(ledger["stale"])
    out = ["<p>Every document the director has written to the queue, and every ask with no document "
           "of its own, is one row of a ledger built at publish ({} rows). Where it stands: {}.</p>"
           .format(len(rows), counts)]
    if stale_ids:
        out.append('<p><b>{} open ask{} had no movement for {} days</b> and carr{} no '
                   "reason for waiting.</p>".format(len(stale_ids), "" if len(stale_ids) == 1
                                                    else "s have", NO_MOVEMENT_DAYS,
                                                    "ies" if len(stale_ids) == 1 else "y"))
    else:
        out.append("<p>No open ask has stood {} days without movement or a recorded reason.</p>"
                   .format(NO_MOVEMENT_DAYS))
    if open_rows:
        out.append('<p>Open now, with the next step:</p>\n<ul class="fo">')
        out += [_li("<b>{}</b> ({}{}): {} <i>{}</i>".format(
            e(_when(r.get("asked"))), _LABEL[r["status"]],
            ", no movement for {}+ days".format(NO_MOVEMENT_DAYS) if r["id"] in stale_ids else "",
            e(str(r.get("ask") or r["id"])), e(r.get("next_step") or r.get("missing")
                                               or "Not yet ruled.")))
            for r in open_rows]
        out.append("</ul>")
    out.append('<details class="more"><summary>The whole ledger</summary>\n<ul class="fo">')
    for r in sorted(rows, key=lambda r: (_ORDER.index(r["status"]), str(r.get("asked") or ""))):
        ev = "; ".join(str(x) for x in r.get("evidence") or [])
        out.append(_li("<b>{}</b> {} &mdash; {}{}{}".format(
            e(_LABEL[r["status"]]), e(_when(r.get("asked"))), e(str(r.get("ask") or r["id"])),
            " <i>Evidence: {}.</i>".format(e(ev)) if ev else "",
            " <i>Superseded by {}.</i>".format(e(r["superseded_by"])) if r.get("superseded_by")
            else "")))
    out.append("</ul>\n<p>A document moved to done before 25 Oct with no Done section is counted "
               "as closed with no evidence recorded: the move says the queue let it go, not that "
               "the ask shipped. Each is ruled as the audit reaches it.</p>\n</details>")
    return "\n".join(out)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--write", action="store_true", help="write " + OUT_JSON)
    p.add_argument("--check", action="store_true", help="exit 1 if any open ask is stale")
    args = p.parse_args(argv)
    ledger = build()
    if ledger is None:
        print("DIRECTOR ASKS LEDGER NOT BUILT: {} could not be read".format(RULINGS),
              file=sys.stderr)
        return 1
    if args.write:
        (ROOT / OUT_JSON).write_text(json.dumps(ledger, indent=1) + "\n", encoding="utf-8")
    print(" ".join("{}={}".format(k, v) for k, v in sorted(ledger["counts"].items())))
    late_close = closed_without_evidence_since()
    if args.check and late_close:
        print("CLOSED WITHOUT EVIDENCE: {} reached done/ with no Done section naming a commit or "
              "a path".format(", ".join(late_close)), file=sys.stderr)
        return 1
    if args.check and ledger["stale"]:
        print("STALE: {} open ask(s) have had no movement for {} days and carry no held reason: {}"
              .format(len(ledger["stale"]), NO_MOVEMENT_DAYS, ", ".join(ledger["stale"])),
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
