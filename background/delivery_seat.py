"""The delivery seat — the periodic session that ORIENTS instead of executing.

Design and the decisions behind it: `docs/design/THE_DELIVERY_SEAT.md`. Read side (and the only
thing the draw ever imports): `background/direction.py`.

Director, 2026-08-25 (console): *"You have ticks that execute — wake, draw an atom, commit, exit —
and a seat that works when a human grants a turn. What you don't have is anything that orients:
something that wakes on its own, reads the last stretch across the alerts, the commits, the map
and the site, and decides what actually matters next, what's drifting, and what the next stretch
should be. My advisor and I have been doing that in a chat window, by hand. That's the most
expensive way it could possibly be done and it stops now."*

WHAT IT IS, IN ONE LINE: a bounded `claude -p` session on a three-hour timer that reads the last
stretch, judges it against the thesis, writes ONE direction record, and exits.

THREE THINGS IT MAY NOT DO, each a mechanism rather than an instruction:

  * IT MAY NOT WRITE CODE. `git add` is called with `direction.WRITE_SCOPE` and nothing else, so
    whatever the session touched outside those three paths is not in its commit. The pathspec is
    the control -- the same reason CLAUDE.md gives for committing by pathspec under concurrent
    writers -- and out-of-scope writes are RECORDED rather than reverted, because reverting would
    make this the second writer it exists not to be.
  * IT MAY NOT SET A TARGET. `direction.validate` refuses a record carrying target-shaped keys.
    Direction says what to work on; a target is a number the work then bends toward (R12).
  * IT MAY NOT GATE THE DRAW. Its output multiplies the supervisor's existing dial weights and can
    never zero one, so a wrong or stale direction makes the machine slower to reach something and
    never unable to (Rule 0: an empty feasible set is a defect in the dials).

R5, AND WHY THE SKIP RULE IS NOT AN OPTIMISATION. If nothing material happened in the stretch
there is nothing to orient on, and orienting anyway would produce a confident restatement of the
last direction with a fresh timestamp -- which reads, to everything downstream, exactly like a
decision. The skip is RECORDED with its reason, never silent. It also happens to be what the token
budget requires (director, twice: the weekly allowance is the binding constraint), but the reason
it is correct is the first one.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from background import child_diagnostics, direction_path_check, director_concerns
from background import direction as direction_mod
from tools import maturity_map_store as map_store
from tools import stretch_log as stretch_log_mod

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "delivery-seat-log.md"
MATURITY_MAP = PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"
STAGING_DIR = PROJECT_DIR / "docs" / "staging"

#: The model. Orientation is judgement about what matters, which is the definition of the OPUS
#: tier in CLAUDE.md's routing rule -- it is never mechanical volume and must never be tiered down
#: on the grounds that it runs on a timer.
from background.model_tier import OPUS as _OPUS_TIER  # noqa: E402 -- the one named model

MODEL = _OPUS_TIER

#: How far back a stretch reaches when there is no previous orientation to measure from.
FIRST_STRETCH_HOURS = 24.0

#: Wall-clock ceiling on the orienting session. It reads and writes one YAML file; a session still
#: running after this has stopped orienting and started doing something else.
SESSION_TIMEOUT_SECONDS = 1800

CHARTER = """You hold the DELIVERY SEAT on this project. This is a standing duty, not a task.

The director's words, verbatim, because they are the charter and not a summary of it:

  "The mission and the direction are mine. Yours is everything between that and the work:
  translating direction into priorities, keeping work flowing when it stalls, and holding the
  trade-offs -- speed against correctness, breadth against depth, shipping against verifying.
  When something blocks, you unblock it rather than report it. When priorities conflict, you
  decide rather than ask.

  You also own the judgement about what reaches me: what genuinely needs my direction, what I'd
  want to know, and what should just be recorded and left for review. Getting that wrong either
  way is a failure -- interrupting me with what you should have decided, or deciding something
  that was really a change of direction. When you decide, record the options you considered and
  why you chose as you did. That record is what I review, and it's what makes it safe for you
  not to ask."

THE THESIS you are judging the stretch against, also his:

  A faithful SIM, and inside it a supplier that makes commercial and operational decisions
  customer-by-customer on lifetime value, using only what it can actually know. It behaves like
  an average player by default and beats average precisely to the degree it understands and
  predicts the truth behind the SIM better than average. The advantage must come from INFERENCE,
  never from ACCESS. And there has to be a BASELINE to beat -- the same book run by a supplier
  applying flat rules with no per-customer view -- or "it performed well" means nothing.

THIS SESSION WRITES DIRECTION. IT DOES NOT WRITE CODE. Do not edit, create or delete any file
except `docs/direction/DIRECTION.yaml` and `docs/direction/wrong_triage.yaml`. Nothing else you touch will be committed, so a code edit
here is work thrown away and a second writer on a tree that already has three.

HOW YOUR DIRECTION IS WORKED (built 2026-08-25). A focus item that names a
maturity-map atom biases the ordinary draw toward it. A focus item that names ANYTHING ELSE is
handed to a worker tick as LANE 0 -- ahead of the dial-weighted lanes -- and that tick will do the
work and land it (`background/delivery_lane.py`). Until this landed, four of five of your
predecessor's focus items were unreachable by any draw and the director had to sit through an
interactive session to get them built. So:

  * write `what` as an INSTRUCTION a competent worker can act on with no further conversation --
    the file, the measurement, the decision to be made -- not as a topic;
  * `why` is what that worker uses to decide what DONE means, because a focus item has no exit
    test. Say what would make it finished;
  * two to five items, and they are worked in YOUR ORDER, so put the one that matters first;
  * an item that is genuinely finished must DISAPPEAR from focus at your next orientation. That
    disappearance is the acceptance test -- nothing else marks the work complete.

WHAT TO PRODUCE: overwrite `docs/direction/DIRECTION.yaml` with exactly this shape.

    version: 1
    oriented_at: "<the ISO-8601 UTC timestamp given in the brief>"
    thesis_read: >-
      One paragraph. Where the project actually stands against the thesis after this stretch --
      not what was done, what it MEANS. Say plainly if it went backwards.
    stretch_reviewed:
      since: "<from the brief>"
      commits: <int from the brief>
      substantive: <int from the brief>
    focus:            # ORDERED. The first is what matters most. Two to five items.
      - id: <a maturity-map atom id where one fits, otherwise a short kebab-case key>
        what: <one line: the work>
        why: <one line: why THIS, now, against the thesis or against what is drifting>
        lane: <OPTIONAL: the maturity-map lane this work belongs to, e.g. W2_customer_generator>
    not_now:          # REQUIRED and non-empty. What you considered and did NOT choose.
      - what: <the thing you rejected>
        why: <why it loses to what you chose -- the trade-off you actually made>
    wrong:            # What the machine got wrong this stretch. Empty list only if genuinely none.
      - what: <the error>
        corrected: true|false
    for_the_director: # Concerns raised WITH A PROPOSAL; usually empty. See below.
      - id: <stable kebab-case id; an open row from the brief keeps its id>
        raised: "<ISO date it was first raised>"
        kind: strategy|vision|canon_intent|reserved
        what: <the concern, stated -- not asked>
        proposal: <the change you propose, or "investigate: <what>">
        status: open|answered|withdrawn
        resolution: <empty while open; his words, dated, or why it was withdrawn>

RULES ON THE CONTENT, and the record is refused if it breaks them:

  * NO TARGETS. You may say what to work on. You may never say what number to hit. A key called
    target/goal/kpi/threshold/score/metric/quota anywhere in the file is refused outright. Quoting
    a measurement inside a `why` is fine and is what good direction looks like.
  * `not_now` MUST be non-empty. A direction that rejected nothing recorded no judgement, and the
    rejections are the half the director reviews.
  * `wrong` IS GRADED, NOT WRITTEN FROM MEMORY. The brief hands you `previous_wrong` -- last
    stretch's errors with the correction state you gave them. Every row there that is still
    uncorrected must appear in your `wrong` again, either still `corrected: false` or now `true`
    with the evidence in `thesis_read`. An uncorrected error that silently stops being listed has
    not been fixed; it has been forgotten, and that is the failure this section exists to catch.
    A row with an empty `what`, or with `corrected` missing or non-boolean, is REFUSED outright.
    A still-open row whose problem has been listed for 7+ days without an entry in
    `docs/direction/wrong_triage.yaml` is REFUSED, and so is any row matching an entry there
    already retired (fold, accept, or fix already_fixed): give each carried problem ONE fate in
    that file -- fix (with its owner), fold into a class register, or accept with a reason -- and
    then stop listing every retired one, rather than copying it forward again.
  * `for_the_director` IS THE DIRECTOR'S CONCERNS LIST (2026-10-04): *"Escalate with a proposal,
    and don't wait: concerns about strategy, vision or canon intent. Raise it, propose the change
    or ask me to investigate, then carry on with everything else. An open question to me sits in a
    list and never blocks the queue."* A row belongs here for the four reserved classes (real
    money, real people, an irretractable public claim in the company's name, a real person's
    safety) OR a concern about strategy, vision or canon intent -- and EVERY row carries a
    `proposal`. A row with no proposal, no id or no status is REFUSED. Everything else is yours
    to decide and record; interrupting him with what you should have decided is a failure.
  * OPEN ROWS ARE CARRIED FORWARD VERBATIM. The brief hands you `previous_for_the_director`, the
    open rows of the current record. Every one must appear in yours under the same `id`: still
    `status: open` with `what` and `proposal` unchanged, or `answered`/`withdrawn` with a
    `resolution` (his words, dated, or why). A record that drops or rewrites an open row is
    REFUSED and the previous record is restored. A concern NEVER blocks the focus: keep working
    everything else, and never put "waiting on the director" in focus. Raising a new one outside
    an orientation: `python3 -m background.director_concerns --raise --kind <k> --what ...
    --proposal ...`. He is paged once, for a row whose id is new.
  * GIVE EVERY FOCUS ITEM A `lane` unless its `id` is already an atom. Under a product-only tick
    mode the executor admits only items that can show they are product work, and an item whose
    prose names no atom, lane or path cannot -- on 2026-09-27 that was one of the director's own
    product questions. A lane that is not on the maturity map is refused.
  * Prefer work that CHANGES A LEVEL or closes a blocking finding over work that merely tidies.
  * If the previous focus was named and never drawn, say so in `thesis_read` and treat the steer
    itself as the thing that is drifting.

Write the file, then stop. Do not commit -- the seat commits it for you, by pathspec.
"""


def _log(msg: str) -> None:
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        with LOG_FILE.open("a", encoding="utf-8") as fh:
            fh.write(f"- [{stamp}] {msg}\n")
    except Exception:
        pass


def _git(*args: str) -> str:
    try:
        out = subprocess.run(["git", *args], cwd=str(PROJECT_DIR), capture_output=True,
                             text=True, timeout=60)
        return out.stdout if out.returncode == 0 else ""
    except Exception:
        return ""


def _upstream() -> str | None:
    """`origin/main` if this checkout has one, else None. A tree with no remote is a legitimate
    state (a worktree cut for an isolated run, a fresh clone mid-fetch) and must degrade to a
    HEAD-only reading that SAYS it is HEAD-only, never to a phantom divergence.

    A `_git_or_none` variant was written first, on the reasoning that `_git` collapses failure and
    a clean empty answer into the same "". Mutating it back to "" did not fire a single test, and
    the mutation was right: NEITHER call here can distinguish them. `rev-parse --verify -q` prints
    a sha on success, so "" is unambiguous; and the fail-closed leg below is the DIGIT PARSE, not
    the return type. It was deleted rather than kept as unfalsifiable machinery."""
    return "origin/main" if _git("rev-parse", "--verify", "-q", "origin/main").strip() else None


def branch_divergence() -> dict:
    """HEAD against `origin/main`, stated as a fact rather than assumed away.

    WHY THIS EXISTS. Every judgement in this module -- the stretch, the substantive count, the
    `wrong` grades the orienting session is handed -- was measured with `git log` in the local
    checkout with NO revision argument, which means HEAD and only HEAD. A commit that is on
    `origin/main` and not yet in this checkout was, to the seat, a commit that had not happened.
    The seat then graded the stretch as quiet and skipped orienting, and the skip was recorded with
    a reason that was true of HEAD and false of the work.

    That this had not yet produced a wrong brief was luck, not structure: the shared tree is
    usually level when the timer fires. `WORKER_FINDING_REPEATING_ALARM_PUBLISH_REFUSED_ORIGIN_
    AHEAD_ORIGIN_MAIN_IS_COMMIT_S_AHEAD_2026-09-03.md` is the condition firing for real.

    The count is `--left-right` over the symmetric difference, so `ahead` is what only HEAD has and
    `behind` is what only origin/main has; both can be non-zero at once and that is the case the
    old reading could not represent at all. Never raises."""
    upstream = _upstream()
    if upstream is None:
        return {"available": False, "why": "no origin/main in this checkout",
                "says": "HEAD-ONLY READING: there is no origin/main here, so the stretch below "
                        "covers this checkout alone and cannot speak for the shared branch."}
    raw = _git("rev-list", "--left-right", "--count", f"HEAD...{upstream}")
    parts = raw.split()
    if len(parts) != 2 or not all(p.isdigit() for p in parts):
        return {"available": False, "why": f"unreadable rev-list output: {raw!r}",
                "says": "HEAD-ONLY READING: the divergence between HEAD and origin/main could not "
                        "be measured, so the stretch below cannot be said to cover the branch."}
    ahead, behind = int(parts[0]), int(parts[1])
    lacking = units_lacking_origin() if behind else []
    if not ahead and not behind:
        says = "HEAD and origin/main are level, so the stretch below is the whole branch."
    else:
        says = (
            "HEAD AND origin/main HAVE DIVERGED: {} commit(s) are on HEAD only and {} are on "
            "origin/main only. The stretch below covers BOTH sides, so it is the same work "
            "either way -- but a divergence is itself a fact about the machine: {}".format(
                ahead, behind,
                "this checkout has not fast-forwarded, so daemons running from it are executing "
                "code the branch has moved past" if behind else
                "work is committed here and not pushed, so nothing downstream of origin can see "
                "it")
        )
        says += _render_lacking(lacking)
    return {"available": True, "ahead": ahead, "behind": behind,
            "diverged": bool(ahead or behind), "upstream": upstream, "says": says,
            "units_lacking_origin": lacking}


#: Where the user units that run from this checkout are declared. `process_manifest.yaml` lists the
#: long-running daemons only, so the timers -- this seat among them -- are read from here.
UNIT_DIR = Path.home() / ".config" / "systemd" / "user"

#: This seat's own unit, named first: it is the one reading the brief.
SEAT_UNIT = "delivery-seat"


def _units_running_here(unit_dir: Path | None = None) -> dict[str, str]:
    """`{unit: entry file}` for every user unit whose WorkingDirectory is this checkout."""
    from background import code_closure
    out: dict[str, str] = {}
    for f in sorted((unit_dir or UNIT_DIR).glob("*.service")):
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        wd = re.search(r"^WorkingDirectory=(.+)$", text, re.M)
        cmd = re.search(r"^ExecStart=(.+)$", text, re.M)
        if not (wd and cmd) or Path(wd.group(1).strip()).resolve() != PROJECT_DIR.resolve():
            continue
        entry = code_closure.entry_path(cmd.group(1), PROJECT_DIR)
        if entry:
            out[f.stem] = entry
    return out


def lacking_origin(units: dict[str, str], closure_of, behind_paths: set[str],
                   commits_touching) -> list[dict]:
    """Each unit whose import closure holds a path origin/main changed and this checkout lacks,
    with the origin-only commits that touched it. The seat's own unit sorts first.

    `boot_sha.paths_behind_trunk` + `process_reconciler.loaded_code_behind_trunk` answer this for
    the manifest's daemons; this seat and the other timers are not in that population, which is
    how 0be518a08 sat on origin for three hours while the seat ran the code it replaced."""
    out = []
    for unit, entry in units.items():
        hits = sorted(set(closure_of(entry)) & behind_paths)
        if hits:
            out.append({"unit": unit, "entry": entry, "paths": hits,
                        # The entry module's own commits lead: the closure is static and
                        # over-approximates, so its long tail is weaker evidence than these.
                        "own_commits": commits_touching([entry]) if entry in hits else [],
                        "commits": commits_touching(hits)})
    return sorted(out, key=lambda r: (r["unit"] != SEAT_UNIT, r["unit"]))


def units_lacking_origin() -> list[dict]:
    """Live wrapper over `lacking_origin`. Never raises: a reading that cannot be taken is one
    row saying so, not an empty list that reads as a clean fleet."""
    try:
        from background import code_closure
        upstream = _upstream() or "origin/main"
        behind = {p.strip() for p in _git("diff", "--name-only", f"HEAD...{upstream}", "--")
                  .splitlines() if p.strip()}
        return lacking_origin(
            _units_running_here(),
            lambda entry: code_closure.import_closure(entry, PROJECT_DIR),
            behind,
            lambda paths: _git("log", "--format=%h", f"HEAD..{upstream}", "--", *paths).split())
    except Exception as exc:  # noqa: BLE001 -- the brief must assemble
        return [{"unit": "?", "unreadable": f"{type(exc).__name__}: {exc}"}]


def _render_lacking(rows: list[dict]) -> str:
    if not rows:
        return ""
    if rows[0].get("unreadable"):
        return (" WHICH UNITS RUN WITHOUT ORIGIN'S CODE could not be read: "
                + rows[0]["unreadable"] + ".")
    def one(r: dict) -> str:
        own = r.get("own_commits") or []
        rest = [c for c in r["commits"] if c not in own]
        parts = (["{} to {} itself".format(", ".join(own), r["entry"])] if own else []) + (
            ["{} commit(s) to code it imports ({})".format(
                len(rest), ", ".join(r["paths"][:3]) + (" ..." if len(r["paths"]) > 3 else ""))]
            if rest else [])
        return "{} lacks {}".format(r["unit"], " and ".join(parts))
    return (" UNITS RUNNING WITHOUT AN ORIGIN COMMIT TO CODE THEY IMPORT: "
            + "; ".join(one(r) for r in rows)
            + ". A restart does not load these; only the checkout advancing does.")


# --------------------------------------------------------------------------- #
# Reading the stretch                                                          #
# --------------------------------------------------------------------------- #

def last_orientation() -> dict | None:
    """The most recent orientation row, skip or not. None on the very first run."""
    rows = direction_mod.read_decisions(limit=1)
    return rows[0] if rows else None


def stretch_since(now: datetime | None = None) -> datetime:
    now = now or datetime.now(timezone.utc)
    row = last_orientation()
    stamp = direction_mod._iso((row or {}).get("at"))
    if stamp is None:
        from datetime import timedelta
        return now - timedelta(hours=FIRST_STRETCH_HOURS)
    return stamp


def commits_since(since: datetime) -> list[dict]:
    """Commits in the stretch, split substantive vs mechanical by REUSING the daily self-note's
    own classifier. A second classifier here would be a parallel measurement layer, and the two
    would disagree the first time either moved -- the anti-gaming principle the self-note's design
    already argues at length."""
    try:
        from background.daily_self_note import _is_substantive_file
    except Exception:
        def _is_substantive_file(_f):  # noqa: ANN001 - fail-soft: nothing reads as mechanical
            return True
    # THE REVISION ARGUMENT IS THE WHOLE POINT, and its absence was the defect. `git log` with no
    # revision means HEAD, so the stretch was the local checkout's stretch and a commit sitting on
    # `origin/main` un-fast-forwarded was invisible to every grade in the brief. Naming both refs
    # makes the range the UNION reachable from either (git de-duplicates), so the answer is the
    # same whether or not this checkout happens to have caught up -- which is the property, not
    # today's zero-zero divergence.
    revs = [r for r in ("HEAD", _upstream()) if r]
    raw = _git("log", f"--since={since.isoformat()}", "--pretty=format:%H%x00%s", "--name-only",
               *revs)
    commits: list[dict] = []
    current: dict | None = None
    for line in raw.splitlines():
        if "\x00" in line:
            if current:
                commits.append(current)
            sha, subject = line.split("\x00", 1)
            current = {"sha": sha[:9], "subject": subject, "files": []}
        elif line.strip() and current is not None:
            current["files"].append(line.strip())
    if current:
        commits.append(current)
    for c in commits:
        c["substantive"] = any(_is_substantive_file(f) for f in c["files"])
        c["files"] = c["files"][:12]
    return commits


def commit_shape(since: datetime, now: datetime | None = None) -> dict:
    """READ the stretch's commits as a list a person would read, and say if the shape is wrong.

    Director, 2026-09-02: *"Every instrument you have counts commits, gates them or receipts them.
    None reads them. Twelve identical titles in an hour was visible at a human glance and invisible
    to you by construction."*

    WHY `commits_since` ABOVE DID NOT ALREADY DO THIS, which is the part worth keeping. It does
    classify substantive vs mechanical -- and it classifies BY FILENAME, from `git log
    --name-only`, which prints **no filenames at all for a merge commit**. So all 29 of that day's
    empty merges scored `substantive: False`, `substantive_count` was 0, and `is_material` read
    the stretch as EMPTY and skipped orientation. A machine committing every six minutes and a
    machine doing nothing produced the identical brief.

    The two readings answer different questions and both are kept: `substantive` asks *were the
    files worth orienting on*, this asks *did the commit change anything at all*. The second is
    structural (tree against every parent's tree) so no subject line or merge shape defeats it.

    Never raises: a seat that cannot orient because its shape reader is unavailable is a worse
    failure than one that orients without it, and the unavailability is recorded either way.
    """
    try:
        from background import commit_narrative
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "why": repr(exc)}
    try:
        hours = max(0.25, ((now or datetime.now(timezone.utc)) - since).total_seconds() / 3600.0)
        # BOTH SIDES, for the same reason `commits_since` reads both: the shape reader is the leg
        # `is_material` trusts to call a stretch a machine fault, and a run of empty merges pushed
        # to origin that this checkout has not caught up to is exactly the case it exists for.
        state = commit_narrative.narrative(
            since_hours=hours, limit=200,
            revs=tuple(r for r in ("HEAD", _upstream()) if r))
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "why": repr(exc)}
    return {
        "available": True,
        "count": state["count"],
        "carrying_work": state["carrying_work"],
        "changed_nothing": sum(1 for r in state["commits"] if r["carries_work"] is False),
        "shape_is_wrong": state["shape_is_wrong"],
        "findings": [{"kind": f["kind"], "detail": f["detail"], "commits": f["commits"][:12]}
                     for f in state["findings"]],
        "rendered": commit_narrative.render(state),
    }


#: A process below this is a COMMAND, not a job: the `ps` that produces this reading, a `git`
#: the brief itself shells out to, the shell around them. Nothing that finishes inside a minute
#: can change what the seat writes as its focus. Set against the case that motivated the reading
#: rather than against a round number -- a value-arm leg four minutes from finishing MUST appear,
#: so the floor has to sit well below that, and `SESSION_TIMEOUT_SECONDS` (1800) is far too high
#: to be the floor even though it is the right ceiling for "will outlive this turn".
ELAPSED_FLOOR_SECONDS = 60

def _project_namespaces() -> set[str]:
    """Top-level package directories, so an argv can be told to be THIS PROJECT'S work.

    Read off the tree rather than typed, because anything else on the machine
    (networkd-dispatcher, unattended-upgrades) is somebody else's python and is not the seat's
    business -- and because a hand-typed list of package names would go stale the first time one
    is added.

    IT IS THE PRESENCE OF PYTHON, NOT OF `__init__.py`. Every top-level package here is a
    NAMESPACE package: `background`, `tools`, `simulation` and `saas` have no `__init__.py`
    between them, and an earlier draft of this asking for one found exactly `company` and `tests`
    -- so `python3 -m background.anything` was dropped from the reading entirely, and the live box
    only looked right because a long argv happened to also mention a file path.
    """
    try:
        return {p.name for p in PROJECT_DIR.iterdir()
                if p.is_dir() and not p.name.startswith(".") and any(p.glob("*.py"))}
    except OSError:
        return set()


def _job_name(tokens: list[str]) -> str:
    """The MODULE a process runs, which is how a person names a long job when they talk about it.

    `python3 -m background.launch_long_job` is "background.launch_long_job", not "python3". The
    argv head is kept alongside for the cases this cannot name, but a reading whose every row said
    `/usr/bin/python3` would be the "buried at a glance" failure the ask names explicitly.

    ONLY THE INTERPRETER'S OWN `-m` COUNTS, and that restriction was earned on the live box on the
    first run of this reading: a sibling `claude -p` seat was named `tools.surgical_land`, because
    its PROMPT recites `python3 -m tools.surgical_land` as the instruction for how to land. A
    scan of every token for `-m` reads any process that merely MENTIONS a module as running it --
    the identical defect `process_reconciler._runs_daemon` exists to refuse, arrived at again from
    a different direction. So the executable must be a python, and the scan stops at the first
    non-option token, which is where the interpreter's arguments end and the program's begin.
    """
    if not tokens:
        return "?"
    if os.path.basename(tokens[0]).startswith("python"):
        i = 1
        while i < len(tokens):
            tok = tokens[i]
            if tok == "-m" and i + 1 < len(tokens):
                return tokens[i + 1]
            if not tok.startswith("-"):
                return tok           # the script path: the interpreter's options are over
            i += 1
    return os.path.basename(tokens[0])


def _elapsed_phrase(seconds: int) -> str:
    """`17h42m`, `4m10s`. A number of seconds is not readable at a glance and this reading's whole
    claim is that it is -- the seventeen-hour duplicate run had to be obvious, not computed."""
    if seconds >= 3600:
        return "{}h{:02d}m".format(seconds // 3600, (seconds % 3600) // 60)
    if seconds >= 60:
        return "{}m{:02d}s".format(seconds // 60, seconds % 60)
    return "{}s".format(seconds)


def _boot_id() -> str | None:
    """This boot's id in the journal's own spelling (no dashes), or None if it cannot be read."""
    try:
        return open("/proc/sys/kernel/random/boot_id").read().strip().replace("-", "")
    except OSError:
        return None


def _wait_channel(session: str) -> str:
    """WHAT THE DAEMON'S MAIN PID IS BLOCKED IN, verbatim from the kernel, or "" if unreadable.

    THE GAP THIS CLOSES. `mute` tells you nothing has been written in this run. It cannot tell you
    WHY, and the two answers it collapses are opposite: a daemon sleeping between polls and a
    daemon wedged on something that will never return are both silent, both `active (running)`
    under systemd, and both counted present by the census. Every reading this machine kept asked
    whether the process EXISTS, and a wedged one exists. On 2026-09-22 the four established causes
    each had to rule out a wedge BY HAND -- `/proc/<pid>/wchan` read off the live box, once, into
    a manifest comment that goes stale the moment the daemon restarts. This asks it every time.

    NO THRESHOLD, NO VERDICT, NO ALLOW-LIST OF "HEALTHY" CHANNELS, deliberately and for the reason
    `declared_daemon_health` gives about cadence: these daemons block in different places for good
    reasons -- `hrtimer_nanosleep` for a sleeper, `do_sys_poll` for `token-proxy` listening on a
    socket, an empty channel for one that is actually on CPU -- so any list of blessed values would
    be picked rather than established, and would be load-bearing within a week. The raw channel is
    published beside the age and the reader judges it, exactly as they already judge the age.
    WHAT MAKES IT READABLE ANYWAY is that it is stable per daemon: a channel that CHANGES between
    two briefs is the signal, and that comparison needs no constant from us.

    `""` is returned for every failure -- no such unit, no main process, `/proc` gone, permission
    refused -- and the caller renders it as "could not be read", never as evidence either way.

    IT READS `/proc` DIRECTLY AND SPAWNS NOTHING, which is a correctness point and not only a
    cost one. The obvious implementation asks `systemctl --user show -p MainPID`, and that is
    exactly what `tests/conftest.py`'s G-T1 guard refuses: `systemctl` is in `_BLOCKED_SPAWN`,
    so the real-box test that exercises this function would have raised `RuntimeError` inside
    `running_now` and emptied the whole declared list. The guard caught it on the first run.
    Reading the cgroup out of `/proc/<pid>/cgroup` needs no process, is faster than the fork it
    replaces, and works identically under pytest and in the daemon.

    THE MAIN PROCESS IS FOUND BY PARENTHOOD, NOT BY LOWEST PID. Every pid in the unit's cgroup is
    a candidate, and the main one is the only member whose PARENT is outside the cgroup -- systemd
    spawned it, and everything else in there descends from it. The tempting `min(pids)` is wrong
    on this box specifically: pids wrap (the counter passed 3.9M against a 4.19M ceiling on
    2026-09-22), so a child spawned after a wrap has a LOWER pid than its own parent.
    """
    want = "{}.service".format(session)
    members = {}
    try:
        candidates = [p for p in os.listdir("/proc") if p.isdigit()]
    except OSError:
        return ""
    for pid in candidates:
        try:
            with open("/proc/{}/cgroup".format(pid)) as fh:
                if want not in fh.read():
                    continue
            # Field 4 of /proc/<pid>/stat is PPID. The comm field can contain spaces and
            # parentheses, so the split is taken AFTER the last ')' -- the standard parse.
            with open("/proc/{}/stat".format(pid)) as fh:
                members[pid] = fh.read().rpartition(")")[2].split()[1]
        except (OSError, IndexError):
            continue
    main = [pid for pid, ppid in members.items() if ppid not in members]
    if len(main) != 1:
        # Zero: nothing in the cgroup, or the parse failed. More than one: the unit's process
        # tree is not the shape this assumes, and guessing between them would be a made-up
        # answer about the one question this function exists to answer honestly.
        return ""
    try:
        return open("/proc/{}/wchan".format(main[0])).read().strip()
    except OSError:
        return ""


def _entry_speaker(entry: dict, session: str) -> bool | None:
    """Did this journal entry come from the SERVICE, or is it systemd writing ABOUT the service?

    `journalctl -u x.service` returns both, and they mean opposite things. The service's own
    output -- the daemon or any child it spawns -- is tagged `_SYSTEMD_USER_UNIT=x.service`.
    systemd's bookkeeping ("Starting x.service", "Started x.service") is tagged
    `_SYSTEMD_USER_UNIT=init.scope`, because the manager, not the service, emitted it.

    THE FIRST DRAFT OF THIS ASKED `_PID == MainPID` AND WAS WRONG IN BOTH DIRECTIONS, caught by
    running it against the real box rather than a fixture. `ntfy-responder` and `dispatcher` were
    graded mute while they were demonstrably working: their newest lines came from a `git push`
    CHILD (pid 321004, 321120), whose pid is not the MainPID and whose output is nonetheless
    proof the daemon is alive and doing its job. A control that reads a working daemon as mute is
    worse than no control, because the four rows it was written for are then indistinguishable
    from the two it libelled.

    `None` when the tag is absent, never a guess: a missing field is not evidence of muteness.
    """
    unit = entry.get("_SYSTEMD_USER_UNIT") or entry.get("_SYSTEMD_UNIT")
    if not unit:
        return None
    return unit == "{}.service".format(session)


def _unit_last_write(session: str) -> tuple[int | None, str, bool | None]:
    """Seconds since `<session>.service` last wrote to its journal, why not, and WHOSE line it was.

    A daemon's own log is the only per-daemon clock this machine keeps. The unit name is the
    manifest's `session` plus `.service` -- `generate_units.py` derives it the same way, so there
    is no second naming convention to drift.

    THREE OUTCOMES, AND THE MIDDLE ONE IS NOT THE OTHERS. A stamp; `None` because the question
    could not be PUT (no journalctl, a timeout, an unparseable head); and `None` because the
    journal answered and holds NOTHING for this unit, which is a real reading and a loud one. They
    are told apart by the reason string, never collapsed -- a `None` that declares its reason and
    a `None` that is silence collapsing into the flattering branch is this project's recurring bug.

    THE AGE IS MEASURED ON THE MONOTONIC CLOCK, and that is the repair this function needed.
    The old body did `time.time() - __REALTIME_TIMESTAMP`, which silently prices in every
    correction the wall clock has taken since the line was written. On 2026-09-22 that read four
    daemons as having last written 14.61 HOURS BEFORE THEY STARTED -- an impossibility the brief
    published as a fact, because the guest's realtime clock was 14.61h behind while those entries
    were stamped and was resynchronised afterwards. `__MONOTONIC_TIMESTAMP` cannot be corrected,
    so `uptime - log_monotonic` is the true age. Measured against the four: 166.02h realtime
    against 151.40h monotonic for `token-proxy`, and the same 14.61h gap on the other three, whose
    two start times differ by two days -- one shared skew, not three coincidences.
    The monotonic clock is per-BOOT, so it is used only when the entry's `_BOOT_ID` is this boot's;
    otherwise the realtime reading is returned with its weakness named rather than hidden.

    WHOSE LINE IT WAS is the third return value, and it is what separates MUTE from QUIET. When
    the newest entry did not come from the service itself (see `_entry_speaker`), the only thing
    in this unit's journal is systemd writing ABOUT the daemon ("Started x.service") and nothing
    inside the service has produced a line in this run. That is a categorically louder reading
    than a daemon that has spoken and then gone quiet, and no threshold is invented to reach it:
    it is the structural question "has this run written a line at all", which has an answer at
    every age. The age is published beside it so a daemon that started a minute ago reads as the
    harmless case it is -- that judgement is the reader's, exactly as it is for the quiet rows.
    """
    try:
        proc = subprocess.run(
            ["journalctl", "--user", "-u", "{}.service".format(session),
             "-n", "1", "-o", "json", "--no-pager"],
            capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError) as exc:
        return None, "could not be asked ({!r})".format(exc), None
    head = (proc.stdout or "").strip().splitlines()
    if not head:
        # rc=1 with no output is journalctl's "no entries matched" -- a clean answer, not a fault.
        return None, "its journal holds no entry at all", None
    try:
        entry = json.loads(head[0])
        realtime = float(entry["__REALTIME_TIMESTAMP"]) / 1e6
    except (ValueError, KeyError, TypeError):
        return None, "its journal's newest line carried no readable timestamp", None

    spoke = _entry_speaker(entry, session)
    why = ""
    age = max(0, int(time.time() - realtime))
    try:
        log_mono = float(entry["__MONOTONIC_TIMESTAMP"]) / 1e6
        uptime = float(open("/proc/uptime").read().split()[0])
    except (KeyError, ValueError, TypeError, OSError, IndexError):
        why = "measured on the wall clock; this line carries no monotonic stamp"
    else:
        if entry.get("_BOOT_ID") and entry["_BOOT_ID"] == _boot_id():
            age = max(0, int(uptime - log_mono))
        else:
            why = "measured on the wall clock; that line was written in an earlier boot"
    return age, why, spoke


def declared_daemon_health(present: set[str], entries: list | None = None,
                           last_write=None, wait_channel=None) -> list[dict]:
    """THE COMPLEMENT of the subtraction in `running_now`: every declared daemon that MUST be
    running, whether `ps` found it, and how long since it last wrote its own log.

    THE SUBTRACTION WAS A CONTROL THAT COULD NOT FAIL. `running_now` matched the manifest against
    `ps` and published only how MANY it had taken out -- `daemons_subtracted: 10`. The set it
    computed to do that was thrown away, so the brief's sentence read identically whether ten
    daemons were up or none were, and nothing downstream reads a floor on that count. On
    2026-09-20 the machine produced zero commits over a whole stretch and every instrument in the
    brief printed a version of "quiet".

    WHY THE LOG AGE IS HERE AND NOT JUST THE ABSENCE. The incident that motivated this reading was
    NOT an absence: the WSL2 guest froze with its host, so all ten daemons were still on the box,
    frozen in place, and an absence-only leg would have reported nothing at all. What they had in
    common was that not one of them had written a line for fourteen hours. Absence and silence are
    different observables and only the pair covers the case
    (`docs/staging/WORKER_FINDING_THE_WORKER_DID_NOT_DIE_THE_BOX_FROZE_...`).

    NO SILENCE THRESHOLD IS INVENTED HERE, deliberately. The daemons have no common cadence --
    `dispatcher` legitimately ran 3.3 days between restarts while `background-worker` cycles every
    ten minutes -- so any single number would be picked rather than established, and would be
    load-bearing within a week. The AGE is published and the reader judges it; ten daemons that
    all last spoke fourteen hours ago is a shape no constant is needed to see.

    ONLY `state: enabled` ROWS. A `dark`, `held` or `retired` daemon being absent is the declared
    intention, and reporting it would be the crying-wolf failure `_runs_daemon`'s own docstring was
    written against. The worker seat is excluded by its `SEAT_MATCH` sentinel -- it is detected via
    tmux and has no `ps` token, so it would be permanently and falsely absent.
    """
    from background.process_reconciler import SEAT_MATCH, load_manifest

    # Resolved here rather than bound as a default, so a test can replace the journal reader on
    # the module and have this call see it -- a default argument would capture the original.
    last_write = _unit_last_write if last_write is None else last_write
    wait_channel = _wait_channel if wait_channel is None else wait_channel
    rows = []
    for entry in (load_manifest() if entries is None else entries):
        match = entry.get("match")
        if entry.get("state") != "enabled" or not match or match == SEAT_MATCH:
            continue
        age, why, spoke = last_write(entry["session"])
        rows.append({
            "session": entry["session"],
            "match": match,
            "on_box": match in present,
            "last_log_seconds": age,
            "last_log": _elapsed_phrase(age) if age is not None else None,
            # `why` carries two different things and they must not share a key: a reason there is
            # no age at all, and a caveat about the ruler the age was taken with. Collapsing them
            # would put a live reading into a field every reader treats as "no reading".
            "why_no_log": why if age is None else "",
            "clock_caveat": why if age is not None else "",
            # True: the newest line in this unit's journal is the daemon's own. False: it is only
            # systemd writing about the daemon, so this run has produced no line whatever -- MUTE.
            # None: the question could not be put. The three never collapse.
            "mute": spoke is False,
            "spoke_this_run": spoke,
            # THE MANIFEST'S OWN ANSWER, carried as a key of its own and never merged into any of
            # the three above. `why_no_log` is a MEASURED absence -- this reading could not get a
            # number. `declared_cause` is a DECLARED one -- a human established why this daemon is
            # silent and wrote it on the row. Collapsing them would make an investigated daemon
            # indistinguishable from an uninvestigated one, which is the whole distinction the
            # brief needs: the actionable list is the mute rows with NO cause on file.
            "declared_cause": (entry.get("log_silence") or "").strip(),
            # ASKED ONLY OF THE MUTE ROWS, and that is a cost decision rather than a claim: it is
            # a subprocess per daemon, it is the only population where the answer changes what the
            # reader should do, and a daemon that has spoken in this run has already proved it is
            # not wedged by the only evidence that matters. A quiet row's blank here is therefore
            # "not asked", which is why the key is only ever rendered inside the mute sentence.
            "wait_channel": wait_channel(entry["session"]) if spoke is False else "",
        })
    return rows


def _mute_sentence(declared_rows: list) -> str:
    """The MUTE daemons, said separately from the quiet ones or not said at all.

    THE DEFECT THIS IS WRITTEN AGAINST. Four declared daemons -- `token-proxy`, `dispatcher`,
    `ntfy-responder`, `worker-seat-manager` -- were on the box, `active (running)` under systemd,
    counted present by the daemon census, and had produced no journal line of their own since
    starting, in one case for six days. Every liveness reading this machine keeps said they were
    fine, because every one of them asks whether the process EXISTS. `ntfy-responder` is the
    channel the director reaches the seat on; a mute one is indistinguishable from a quiet one and
    the difference is whether "he said nothing" or "we stopped listening" is the true sentence.

    IT IS A SENTENCE, NOT A REGISTER. No alarm document, no threshold, no per-daemon cadence
    table -- the reading is structural (did this run write a line at all) and the seat that reads
    the brief is the control. `None` rows are excluded rather than assumed innocent: a daemon
    whose speaker could not be established is not evidence of muteness and not evidence against.

    WHICH DEFINITION OF MUTE THIS APPLIES, said on the page because the count has already moved
    under a reader who could not see that it had. Two definitions were in use on 2026-09-22 and
    they gave 4 and 5 over the same box within hours:

      A -- "the DAEMON'S OWN stdout has written no journal line since it started." The manifest's
           first four `log_silence` rows were established under this one.
      B -- "NOTHING INSIDE THE UNIT has written a line in this run -- not the daemon, not any
           child it spawned -- so the only entry is systemd's own." THIS IS THE ONE APPLIED HERE.

    B is narrower and it is the honest one for a LIVENESS question, for the reason
    `_entry_speaker` gives: `ntfy-responder` and `dispatcher` were graded mute under A while
    demonstrably working, because their newest lines came from a `git push` CHILD -- output that
    is proof the daemon is alive and doing its job, and that A throws away. A remains the right
    definition for a DIAGNOSABILITY question ("can this daemon tell me anything when it goes
    wrong"), and the two manifest rows that answer A rather than B say so on their own faces.
    SO A COUNT THAT MOVES FROM 4 TO 5 IS NOT DECAY, and nothing here should be read as decay
    unless the SESSIONS change -- which is why they are named, every time, rather than counted.
    """
    mute = [r for r in declared_rows if r.get("mute")]
    if not mute:
        return ""
    explained = [r for r in mute if r.get("declared_cause")]
    unexplained = [r for r in mute if not r.get("declared_cause")]

    def _age(row):
        return " ({} so far)".format(row["last_log"]) if row["last_log"] else ""

    def _channel(row):
        """The wait channel as the kernel gives it, with `0` spelled out rather than translated.

        `/proc/<pid>/wchan` is `0` when the task is not blocked in the kernel at all -- it is on
        CPU. That is a kernel convention, not a judgement of ours, and it is the one value a
        reader cannot look up from the name; every other value IS a symbol they can grep for.
        It is still printed verbatim beside the gloss, so nothing here is a translation layer.
        """
        chan = row.get("wait_channel")
        if not chan:
            return "could not be read -- which is NOT evidence that it is fine"
        if chan == "0":
            return "0 (the kernel's 'not blocked at all' -- it was on CPU when asked)"
        return chan

    out = (
        "\n\n{} DECLARED DAEMON(S) ARE MUTE, WHICH IS NOT THE SAME AS QUIET. The only entry in "
        "each of these units' journals is systemd's own line saying it started -- nothing inside "
        "the service has written at all in this run, however long it has been up. MUTE HERE MEANS "
        "DEFINITION B (see this function's docstring); the sessions, not the count, are the "
        "reading.\n".format(len(mute)))
    if unexplained:
        out += (
            "\n  NO CAUSE ON FILE -- this is the actionable list, and it is the only part of this "
            "sentence that asks anything of you:\n"
            + "\n".join(
                "    {:<22} on the box, unit active, silent for its whole run{}"
                "\n      blocked in: {}".format(r["session"], _age(r), _channel(r))
                for r in unexplained)
            + "\n    `blocked in` is `/proc/<MainPID>/wchan` verbatim -- no threshold and no "
              "allow-list of healthy channels, because these daemons block in different places "
              "for good reasons. It is here so a WEDGED daemon reads differently from a freshly "
              "started one, which mute and age alone cannot tell apart: an ordinary sleeper sits "
              "in `hrtimer_nanosleep` and a socket listener in `do_sys_poll`, and the signal is a "
              "channel that CHANGES between two briefs -- a comparison needing no constant.\n"
              "    Establish which it is per daemon -- writing somewhere this reading does not "
              "watch, wedged, mute by construction, restarted faster than it speaks, or genuinely "
              "with nothing to say -- and write it to `log_silence` on that daemon's row in "
              "`background/process_manifest.yaml`, which is where this sentence reads it back "
              "from. A CLASS VERDICT WILL BE WRONG FOR AT LEAST ONE OF THEM: the five established "
              "so far came out as five different causes.\n")
    if explained:
        out += (
            "\n  CAUSE ESTABLISHED AND ON FILE -- carried here from `log_silence` in "
            "`background/process_manifest.yaml` so a finding is not filed where nothing looks. "
            "These need no action; they are shown because a mute daemon that VANISHES from this "
            "list has changed behaviour, and that is worth seeing. THE WAIT CHANNEL IS RE-ASKED "
            "LIVE FOR THESE TOO, and that is the point of repeating it beside a cause that "
            "already mentions one: the cause was established ONCE, against a pid that no longer "
            "exists, and a daemon with a filed cause can wedge tomorrow. A cause on file must not "
            "become a reason to stop looking -- that is a control pinned to the day's answer:\n"
            + "\n".join("    {}{}, blocked in {}: {}".format(
                r["session"], _age(r), _channel(r),
                " ".join(r["declared_cause"].split())) for r in explained)
            + "\n")
    out += (
        "\nA mute daemon passes every liveness check here, because they all ask whether the "
        "process exists.")
    return out


def _unlanded_worktree_commits() -> dict:
    """`tools.unlanded_worktree_commits.census`, fail-closed: a census that raised is
    `available: False`, never an empty list."""
    try:
        from tools.unlanded_worktree_commits import census
        return census(PROJECT_DIR)
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "why": repr(exc)}


def _render_unlanded(reading: dict | None) -> str:
    from tools.unlanded_worktree_commits import render
    return render(reading or {"available": False, "why": "the reading was not taken"})


def running_now(floor_seconds: int = ELAPSED_FLOOR_SECONDS) -> dict:
    """WHAT IS ON THE BOX, with the DECLARED permanent daemons subtracted.

    Six consecutive orientations ran this `ps` by hand, and twice in a row the answer changed what
    the seat wrote: once it would have said "launch the ON leg" about a leg four minutes from
    finishing. The expensive precedent is the seventeen-hour duplicate floor run that was ordered
    killed, never killed, and ended only because it happened to finish. None of that is visible in
    a commit list, a divergence or a findings count -- the brief's other six readings all describe
    the TREE, and a job that has not landed yet is in none of them.

    THE SUBTRACTION IS THE WHOLE DESIGN, and it is why this is not just `ps`. The permanent daemons
    are the LONGEST-running processes on the box -- days, against a job's hours -- so an elapsed
    floor alone sorts them straight to the top and buries the one row that matters. The stated
    failure for this reading is exactly that: "lists every python process including the four
    permanent daemons, so the one long job that matters is buried". They are subtracted using
    `process_manifest.yaml`, the single declaration of what SHOULD be running, and the token match
    `process_reconciler._runs_daemon` already got right -- a substring test counts `grep
    ntfy_responder` as the daemon, which false-positived a control within minutes of going live.
    So the day a daemon is added, it is added to the manifest because nothing starts it otherwise,
    and it stops appearing here without this function being touched.

    "NOTHING LONG IS RUNNING" IS A POSITIVE STATEMENT. An empty list and a reading that failed are
    the same shape on the page and opposite in meaning, so `nothing_long_running` is only True when
    the `ps` actually ran and returned rows to filter. `available: False` says the other thing.

    No scheduler, no lock, no contention register: one reading, printed into a brief that already
    prints six others.
    """
    try:
        proc = subprocess.run(["ps", "-eo", "pid=,etimes=,rss=,euid=,args="],
                              capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"available": False, "why": repr(exc)}
    if proc.returncode != 0:
        return {"available": False, "why": "ps exited {}".format(proc.returncode)}

    try:
        from background.process_reconciler import _runs_daemon, load_manifest
        entries = load_manifest()
        declared = [e["match"] for e in entries if e.get("match")]
    except Exception as exc:  # noqa: BLE001
        # Without the declaration the daemons cannot be told from the jobs, and a reading that
        # buries its subject is the failure this was written against. Say so; do not guess.
        return {"available": False, "why": "process manifest unreadable: {!r}".format(exc)}

    namespaces = _project_namespaces()
    me = os.geteuid()
    mine = os.getpid()
    jobs, present = [], set()
    for line in (proc.stdout or "").splitlines():
        parts = line.split(maxsplit=4)
        if len(parts) < 5:
            continue
        try:
            pid, etimes, rss, euid = (int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]))
        except ValueError:
            continue
        args = parts[4]
        if euid != me or pid == mine:
            continue
        # THE DAEMON MATCH RUNS BEFORE THE ELAPSED FLOOR, and that ordering is the whole
        # correctness of the absence leg below. `deploy_restart` cycles several of these every ten
        # minutes, so a healthy daemon is routinely younger than the 60s floor; filtering by age
        # first would drop it from `present` and report a daemon that is running as MISSING. The
        # floor exists to keep short-lived JOBS out of the list, and a daemon is never a job.
        hit = next((m for m in declared if _runs_daemon(args, m)), None)
        if hit is not None:
            present.add(hit)
            continue
        if etimes < floor_seconds:
            continue
        tokens = args.split()
        touches_project = any(
            tok.startswith(str(PROJECT_DIR))
            or tok.split(".")[0] in namespaces
            or (tok.endswith(".py") and (PROJECT_DIR / tok).exists())
            for tok in tokens)
        if not touches_project:
            continue
        jobs.append({
            "pid": pid,
            "elapsed_seconds": etimes,
            "elapsed": _elapsed_phrase(etimes),
            "rss_mb": round(rss / 1024.0, 1),
            "what": _job_name(tokens),
            "argv_head": args[:160],
        })
    jobs.sort(key=lambda j: -j["elapsed_seconds"])
    try:
        declared_rows = declared_daemon_health(present, entries)
    except Exception as exc:  # noqa: BLE001
        declared_rows, declared_why = [], repr(exc)
    else:
        declared_why = ""
    return {
        "available": True,
        "floor_seconds": floor_seconds,
        "nothing_long_running": not jobs,
        "count": len(jobs),
        "daemons_subtracted": len(present),
        "jobs": jobs,
        # The complement of the subtraction above, which used to be computed and discarded.
        "declared": declared_rows,
        "declared_absent": [r for r in declared_rows if not r["on_box"]],
        "declared_unreadable": declared_why,
    }


def _stamp(raw) -> datetime | None:
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def ended_since(since: datetime, register: Path | None = None) -> dict:
    """THE COMPLEMENT OF `running_now`: every `launch_long_job` job that stopped in the stretch.

    `running_now` lists survivors, and so does every other reader of the box. On 2026-09-29 two
    runs of one five-seed family died -- `ab5-runA` OOM-killed at 10:01Z, `ab5-runA2` exit 1 at
    15:08Z -- and each stayed invisible for over an hour, although the launch register had settled
    each to `died` within minutes. The register was right; nothing that orients read it.

    READ FROM THE REGISTER, NOT FROM `systemctl`. `launch_liveness.check` has already asked the
    user manager and written the verdict back, so the book holds the answer, and a brief that
    re-probed would be a second, drifting copy of the same question (and the G-T1 test guard
    refuses the spawn anyway).

    THE END TIME IS SYSTEMD'S `ExecMainExitTimestamp` WHERE THE RECORD HAS IT. Records settled
    before that field was kept carry only `settled_at` -- when somebody next ASKED -- and that is
    reported as a bound (`ended_by`), never as the time it ended.

    An unreadable register is `available: False`, not an empty list: "no job died" and "we could
    not read the book" are opposite answers of the same shape.
    """
    from background import launch_liveness as ll

    records, verdict = ll.load_register(register)
    if ll.prior_unreadable(verdict):
        return {"available": False, "why": "the launch register at {} could not be read "
                "({})".format(register or ll.RECORDS_PATH, verdict)}
    rows = []
    for r in records:
        if r.get("claim") in (ll.LIVE, None):
            continue
        exited = _stamp(r.get("exited_at"))
        settled = _stamp(r.get("settled_at"))
        launched = _stamp(r.get("launched_at"))
        # THE WINDOW IS THE SETTLE, NOT THE EXIT. A settle always follows its exit, so an exit in
        # the stretch implies a settle in it; and a death before the last orientation that was
        # only settled after it was invisible to that orientation, so this stretch is the first
        # that can see it.
        if not any(t is not None and t >= since for t in (settled, launched)):
            continue
        evidence = r.get("evidence") or ""
        result = r.get("result") or (re.search(r"Result=([\w-]+)", evidence) or [None, None])[1]
        status = r.get("exit_status") or (
            re.search(r"ExecMainStatus=(\d+)", evidence) or [None, None])[1]
        rows.append({
            "job": r.get("job"), "unit": r.get("unit"), "claim": r.get("claim"),
            "launched_at": r.get("launched_at"),
            "ended_at": r.get("exited_at"),
            "ended_by": None if exited else r.get("settled_at"),
            "result": result, "exit_status": status,
            "log": r.get("log"), "artefact": r.get("artefact"),
        })
    rows.sort(key=lambda x: (x["claim"] != ll.DIED, x["ended_at"] or x["ended_by"] or ""))
    return {"available": True, "since": since.isoformat(), "jobs": rows,
            "died": [x for x in rows if x["claim"] == ll.DIED]}


def findings_now() -> dict:
    """Open staging findings by severity, from the parser the rest of the tree already reads."""
    try:
        from background.finding_severity import scan_staging_root
        rows = scan_staging_root(STAGING_DIR)
    except Exception as exc:
        return {"available": False, "why": repr(exc)}
    by_sev: dict[str, list[str]] = {}
    for row in rows:
        by_sev.setdefault(getattr(row, "severity", "UNCLASSIFIED"), []).append(
            Path(getattr(row, "path", "?")).name)
    return {"available": True, "counts": {k: len(v) for k, v in sorted(by_sev.items())},
            "blocking": by_sev.get("BLOCKING", []), "unclassified": by_sev.get("UNCLASSIFIED", [])}


def staging_flow() -> dict:
    """Is the work queue draining or silting up? The FOLDER, not the documents in it.

    `findings_now()` above reads what is in the staging root and every other control here reads
    the documents; on 2026-09-03 the root was found at 168 tracked documents, up from 15 six days
    earlier, with nothing in the tree ever having read the folder's own size. Fail-soft like every
    other brief field — a brief that cannot be assembled is worse than one missing a line.
    """
    try:
        from background.staging_rooms import root_flow, sediment_violations, work_queue

        return {"flow": root_flow(), "sediment": sediment_violations(),
                "work_queue_len": len(work_queue())}
    except Exception as exc:
        return {"available": False, "why": repr(exc)}


def levels_recorded_since(since: datetime) -> list[dict]:
    """Level moves RECORDED IN THE LEDGER during the stretch.

    R16: THE LEDGER IS THE RECORD, and this is the seat's own first correction of itself. Its
    first orientation reported "no level movement in the window" while
    `gate_authorizations.jsonl` held five self-certified moves, because the brief compared the
    MAP FILE between orientations -- which has no history, cannot see a move that happened and
    was later superseded, and reads as empty on the very first run when there is no previous
    snapshot to diff against. The map is a live record of where things ARE; the ledger is the
    record of what MOVED, and a seat asking "what happened in this stretch" wants the second.

    The map snapshot is still taken (see `map_levels`) because a diff catches a level that moved
    with NO ledger entry -- which is a different defect and one the level-promotion gate exists
    to refuse. The two disagreeing is information, so both are carried.
    """
    path = PROJECT_DIR / "docs" / "observability" / "gate_authorizations.jsonl"
    cutoff = since.timestamp()
    out = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return out
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "LEVEL_UP" not in str(row.get("action", "")):
            continue
        if float(row.get("ts") or 0.0) >= cutoff:
            out.append({"atom": row.get("atom"), "level": row.get("level"),
                        "why": str(row.get("provenance") or "")[:400]})
    return out


def map_levels() -> dict:
    """Every atom's current level, as the MAP FILE has it. Kept beside the ledger read above, not
    replaced by it: a level that moved in the map with no ledger entry is a different defect from
    a level that moved and was recorded, and only the diff can see the first."""
    try:
        atoms = map_store.load_atoms(MATURITY_MAP)
    except Exception:
        return {}
    if not isinstance(atoms, list):
        return {}
    return {a["id"]: a.get("level_current") for a in atoms
            if isinstance(a, dict) and "id" in a}


#: Per-atom wall clock for the level-zero contradiction check, TIGHT because this runs inside the
#: seat's three-hourly orientation and a brief that does not arrive is worse than one missing a
#: row. `KNIFE3_wall_crossing_paydown` names twelve architecture suites and will time out here --
#: that is correct and it reports itself as ungradable rather than silently passing.
#: MEASURED, and the first two guesses were both wrong in instructive ways. An unbudgeted pass
#: took 259s. Of the six gradable rows, FOUR resolve in ~19s between them and produce every
#: verdict this is here for; the other two -- `D27_belief_window_saturates_on_this_book` and
#: `KNIFE3_wall_crossing_paydown` (twelve architecture suites) -- exceed any cap worth setting
#: and simply consume it. So the per-atom cap's job is to give up on those two QUICKLY rather
#: than to let them finish.
_LEVEL_ZERO_TIMEOUT_S = 60

#: And a budget over the WHOLE pass, because a per-atom cap is not a bound on a pass: six rows at
#: 120s is a twelve-minute worst case, and this runs inside a three-hourly orientation whose brief
#: has to arrive.
#:
#: WHY IT IS NOT ALSO 120. It was, for one measurement, and that is the interesting failure: the
#: two expensive rows come FIRST in map order, ate the whole budget between them, and the pass
#: returned ZERO contradictions with all 34 rows ungradable -- honest, self-describing, and
#: completely useless. A budget tight enough to starve the rows that answer is worse than no
#: check, because "no contradictions" is exactly what a healthy map looks like. At 60s/300s the
#: two expensive rows time out, every other row is reached, and the four real verdicts land.
#: Ceiling is budget + one timeout = 360s, since the budget is checked before a run starts and
#: never interrupts one in flight.
_LEVEL_ZERO_BUDGET_S = 300


#: Where a row goes when the check returned no cause for it. It should now be unreachable --
#: `ungradable_causes` is total as of 2026-09-16 -- and it is kept precisely for that reason: the
#: day a new branch in the producer returns nothing, the row must show up under a key that says
#: so, not vanish out of the brief. A fallback deleted because "it cannot happen" is how the
#: fail-silent this whole field exists to end gets back in.
NO_CAUSE_RECORDED = "no cause recorded by the check -- the producer returned an empty list"


def _by_cause(ungradable: list[dict], causes_of=None) -> dict:
    """`{cause: [atom id, ...]}` over the whole ungradable set, sorted for a stable brief.

    BY CAUSE, NOT BY REASON, and the two are different questions -- the module that computes them
    says so in the comment above its own vocabulary. A `reason` is the SHAPE of the row's
    `file_scope` ("names a control file that is not on disk"); a `cause` is the state of the WORK
    and carries the repair. Three rows sharing one reason had three different repairs, which is
    the split this grouping exists to show, and grouping by reason re-merged it one level up in
    the only place the check is ever read. That is this project's most-repeated defect: a repair
    landed in the producer while the reader kept getting the old answer.

    A ROW WITH SEVERAL CAUSES APPEARS UNDER EACH. `A51` has a pointer to repoint AND a control to
    write; filing it under a single primary cause would send a reader to repoint the pointer and
    call the row repaired. That means the group sizes SUM TO MORE THAN the row count, on purpose
    -- these are repairs owed, not a partition of rows, and anyone differencing the two numbers
    should read this line rather than infer a bug.

    NO CAUSE VOCABULARY OF ITS OWN. The keys are whatever the producer returned, so a cause this
    function has never heard of is grouped under it rather than dropped -- a fixed list of groups
    cannot promise that across a change to the producer, and the unrecognised member falling
    through every branch is exactly how a row goes silently missing.

    `causes_of` exists so a test can hand rows their causes without a repository; `None` reads the
    `causes` the producer already attached, which is the live path.
    """
    out: dict = {}
    for u in ungradable:
        attached = causes_of(u) if causes_of else (u.get("causes") or [])
        named = [str(c["cause"]) for c in attached
                 if isinstance(c, dict) and c.get("cause")]
        for cause in (named or [NO_CAUSE_RECORDED]):
            if u.get("id") not in out.setdefault(cause, []):
                out[cause].append(u.get("id"))
    return {k: sorted(v, key=lambda x: (x is None, str(x))) for k, v in sorted(out.items())}


def self_contradicting_levels() -> dict:
    """Atoms at `level_current: 0` / `loop_stage: build` whose OWN named controls all pass.

    THIS IS AN ORIENTATION INPUT, NOT A GATE, and it belongs here rather than in a commit hook
    for a measured reason: a full pass costs minutes, and a gate that costs minutes gets bypassed
    (`background/head-green-census.timer` carries the same argument for the same reason).

    WHY THE SEAT AND NOT THE DRAW. `tools/lane_formation.py::formation` derives `buildable_lanes`
    from exactly these two fields, so a row stuck at zero keeps winning draws it has already been
    paid for -- but the draw is a bounded tick and structurally cannot spend two minutes on it.
    The seat re-orients every three hours and is the only place that can hold the whole map, so
    this is where the corrupted input gets noticed.

    Failure returns `available: False` with the reason. A brief that says "I could not check" is
    a fact the orienting session can act on; a brief that silently omits the row is not.
    """
    try:
        from tools import level_zero_contradicted_by_its_own_controls as lz
        atoms = map_store.load_live_atoms(MATURITY_MAP)
        legs: list = []
        contradicted, ungradable = lz.assess(atoms, timeout_s=_LEVEL_ZERO_TIMEOUT_S,
                                             budget_s=_LEVEL_ZERO_BUDGET_S, leg_log=legs)
    except Exception as exc:  # noqa: BLE001 -- an unavailable check is reported, never inferred
        return {"available": False, "why": repr(exc)}
    # Computed once and read by three fields below, because they have to agree: a split, the rows
    # excluded from it, and a count of what is left are three views of ONE grouping, and building
    # each from its own pass is how they come to disagree.
    by_cause = _by_cause(ungradable)
    return {
        "available": True,
        # The IDS, not a count. A count tells the seat a number it cannot act on; the ids are the
        # rows to go and move, and there have never been more than a handful.
        #
        # SPLIT ON WHETHER THE MOVE CAN ACTUALLY BE MADE (2026-09-06). Both of the map's real
        # contradictions -- SITE4 in H_harness, PB4 in W2_customer_generator -- sit in lanes
        # holding live BLOCKING findings, so OPS11 refuses the recording this list was asking
        # for. A flat list sent the seat to spend a turn finding that out, three hours at a time.
        "contradicted": [c["id"] for c in contradicted if not c.get("frozen_by")],
        # Reported with the blockers NAMED, because the work here is the lane and the finding
        # names are what identifies it. Still contradicted, still the map being wrong -- the
        # freeze says who has to move first, never that the row is acceptable.
        "contradicted_but_frozen": {c["id"]: list(c.get("frozen_by") or [])
                                    for c in contradicted if c.get("frozen_by")},
        # Kept, because it is the coverage headline and several readers want the one number:
        # 28 of 34 rows named no control a runner could execute when this was measured
        # (docs/staging/SEAT_FINDING_TWENTY_EIGHT_OF_THIRTY_FOUR_LEVEL_ZERO_ROWS_NAME_NO_CONTROL_A_RUNNER_CAN_EXECUTE_2026-09-06.md).
        "ungradable_count": len(ungradable),
        # AND THE ROWS THEMSELVES, BY NAME AND BY REPAIR CLASS. A count is a coverage limit; it
        # is not the thing that was skipped. Reporting only the number made the majority of the
        # partition anonymous: a reader could see that 28 rows went ungraded and had no way to
        # learn WHICH, so the one row among them that was ungradable for a fixable reason -- a
        # stale path, a scope where a control should be -- was indistinguishable from the ones
        # that are honestly unbuilt. That is a silent skip wearing a count.
        #
        # GROUPED BY CAUSE AND NOT BY REASON (2026-09-16), because only the cause carries a
        # repair. `ungradable_causes` had already made that split in the producer and this, its
        # only consumer, was still grouping by the `reason` shape field -- so the split existed
        # and the brief printed the undifferentiated count anyway. A repair landing in the
        # producer while the reader gets the old answer is this project's most-repeated defect,
        # and it was committed here against its own census.
        #
        # THE KEY IS RENAMED, not reused. Same field name with different contents is exactly how
        # a downstream reader comes to be quietly wrong about what it is reading.
        #
        # ROWS OWING NO REPAIR ARE NOT IN HERE. See the field below -- they are the part of this
        # count that was never a defect, and leaving them in is what made the number look stuck.
        "ungradable_by_cause": {k: v for k, v in by_cause.items()
                                if k not in lz.CAUSES_OWING_NO_REPAIR},
        # The rows that are RIGHT to read zero: no file the atom names exists, so the map is not
        # wrong about them and there is nothing to repair until someone builds the atom or closes
        # it. Reported apart rather than netted off, because a count that silently excluded them
        # would be a smaller number nobody could check.
        "ungradable_owing_no_repair": sorted(
            {aid for cause in lz.CAUSES_OWING_NO_REPAIR for aid in by_cause.get(cause, [])},
            key=lambda x: (x is None, str(x))),
        # ROWS, not repairs: a row with two causes appears under both keys above, so summing the
        # groups double-counts it. This is the number the census is actually trying to move.
        "ungradable_owing_repair_count": len(
            {aid for cause, ids in by_cause.items() if cause not in lz.CAUSES_OWING_NO_REPAIR
             for aid in ids}),
        # NO SILENT CAP. The two counts above cannot distinguish "this row names no control" from
        # "this row HAS a control and I ran out of time to run it" -- and only the second means
        # the seat is being told less than the check could have told it. A 120s budget once
        # returned zero contradictions with every row unreached, which reads identically to a
        # clean map. These are the rows the bound cost us, by name.
        #
        # `.get`, and that is not defensiveness: subscripting here raised KeyError on a row with
        # no `reason`, which the caller's own `except` turned into `available: False` for the
        # WHOLE check -- one malformed row costing the seat every verdict in the pass. A row that
        # cannot be classified is not in `bounded_out`, which is the honest answer, and it is
        # still named in `ungradable_by_cause` above -- under NOTHING_IN_THE_ROW, which is what
        # a budget-spent or runner-unavailable row now carries.
        "bounded_out": [u["id"] for u in ungradable
                        if u.get("reason") in (lz.BUDGET_EXHAUSTED, lz.RUN_UNAVAILABLE)],
        # WAS A RUNNER EVER ASKED, which nothing above can answer and three lanes needed. Every
        # field in this brief is about the ROW -- what it names, what it owes, what the bound
        # cost. None of them says whether the instrument ran, and the one that looks like it does
        # is the absence of `contradicted` entries. On the live map 2026-09-26 that absence meant
        # NO CONTROL WAS EXECUTED AT ALL: 27 rows returned by a cheap leg and one silenced by the
        # HEAD-red register, which is not the same fact as a pass that weighed rows and found
        # nothing wrong. Three lanes reported the census as stuck off this brief, and the work
        # item drawn off it instructed the next invocation to enlarge a budget nothing spends.
        #
        # TWO NUMBERS, because one of them moves with `_LEVEL_ZERO_BUDGET_S` and the other does
        # not: `clears_every_cheap_leg` is how many rows are a runner's to weigh at all, and it
        # is the one to read when asking whether the instrument has anything to do. See the
        # census module's own comment for why publishing only the first is a trap.
        #
        # NOT DERIVED FROM `ungradable`: a row silenced at HEAD is in neither list, so any count
        # built by subtraction here would be wrong in exactly the direction that hides this.
        "reached_the_runner": sum(1 for e in legs if e["leg"] == lz.REACHED_THE_RUNNER),
        "clears_every_cheap_leg": sum(
            1 for e in legs if e["leg"] in (lz.REACHED_THE_RUNNER, lz.BUDGET_EXHAUSTED)),
    }


def publish_state() -> dict:
    try:
        from background.publish_freshness import describe, snapshot
        snap = snapshot()
        return {"available": True, "describe": describe(snap)}
    except Exception as exc:
        return {"available": False, "why": repr(exc)}


def director_inputs(since: datetime, now: datetime | None = None) -> list[str]:
    """Anything the director said in the stretch. The seat reads WHETHER he spoke, never decides
    on his behalf what it meant -- the session reads the files itself.

    Staged files (`from_rich_*`, `DIRECTOR_*`) are named by filename and dated by mtime. The
    console capture is read TURN BY TURN instead, one entry per turn as `<file>@<stamp>`, dated by
    the turn's own `### <ISO>` heading: the capture is appended to all day and moved between rooms
    by `staging_migrate_rooms`, so its mtime says when the file was last touched, not when he
    spoke. For five stretches this returned [] while he was steering from the console, because
    the capture lives in `console/`, which the glob never read.

    Every heading in a `DIRECTOR_CONSOLE_*` file is his: the seat's answers go to the
    `SEAT_REPLY_*` sibling precisely so they cannot be read as his voice, and are not read here.
    """
    names = []
    for folder in (STAGING_DIR, STAGING_DIR / "done", STAGING_DIR / "in_progress"):
        try:
            for path in folder.glob("*.md"):
                name = path.name
                if not (name.startswith("from_rich_") or name.startswith("DIRECTOR_")):
                    continue
                if name.startswith("DIRECTOR_CONSOLE_"):
                    continue  # read by its turns below, never by mtime
                if datetime.fromtimestamp(path.stat().st_mtime, timezone.utc) >= since:
                    names.append(name)
        except Exception:
            continue
    return sorted(set(names)) + console_turns_since(since, now)


def console_turns_since(since: datetime, now: datetime | None = None) -> list[str]:
    """`<room>/DIRECTOR_CONSOLE_<day>.md@<stamp>` for each console turn stamped at or after
    `since`. Days are the capture's own: `by_day` files a turn under its UTC stamp's date."""
    from tools.console_instruction_record import record_path, turns_in_record

    now = now or datetime.now(timezone.utc)
    out = []
    day = since.astimezone(timezone.utc).date()
    while day <= now.astimezone(timezone.utc).date():
        path = record_path(day.isoformat(), staging=STAGING_DIR)
        try:
            turns = turns_in_record(path)
        except Exception:
            turns = []
        for stamp, _text in turns:
            try:
                when = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            except ValueError:
                continue
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            if when >= since:
                out.append(f"{path.relative_to(STAGING_DIR).as_posix()}@{stamp}")
        day += timedelta(days=1)
    return out


def atoms_drawn_since(since: datetime) -> list[str]:
    """Atom ids the supervisor's draw actually selected in the stretch.

    READ FROM THE DRAW'S OWN TRACKER, not inferred from commit subjects. The first version of
    this took the first word of each commit subject, which on this project is "company:" or
    "world:" and never an atom id -- so the steer-effectiveness check would have reported "focus
    never drawn" every single time and the control designed to catch a no-op steer would itself
    have been one. `docs/observability/.atom_stall_tracker.json` carries `last_drawn_at` per atom
    because the anti-livelock guard needs it, so the fact is already recorded and nothing new has
    to be measured for it.

    NAMED LIMIT: the tracker records the PRIMARY pick of each weighted draw. An atom taken as a
    concurrent disjoint additional candidate is not in it, so this under-reports rather than
    over-reports -- which is the safe direction for a control whose job is to notice a steer that
    is NOT biting.
    """
    try:
        from background.supervisor import ATOM_STALL_STATE_FILE
        state = json.loads(ATOM_STALL_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []
    cutoff = since.timestamp()
    return sorted(aid for aid, row in state.items()
                  if isinstance(row, dict) and float(row.get("last_drawn_at") or 0.0) >= cutoff)


def atoms_stalled_with_reason(since: datetime, focus: tuple = (),
                              now: datetime | None = None) -> list[dict]:
    """Stalled atoms the draw took in the stretch, AND stalled atoms in focus, each with the
    `stop_reason` the supervisor wrote beside its counter (`_atom_stop_reason`).

    `atoms_drawn` says only that an atom was drawn. B11 and D48 were each drawn 151 times with
    nothing beside the count, and the seat re-issued the same steer blind. B11 had landed twice
    under Lane 0 slugs, and D48's scope file had never existed. A row from a supervisor that has
    not written a reason yet (one still running code older than the field) has it read here.

    THE FOCUS LEG, because the draw leg cannot reach the atoms it was built for: the anti-livelock
    draw prefers the LEAST-stalled candidate, so once B11 and D48 were the most-stalled rows the
    draw stopped taking them (last drawn 15:51Z on 2026-10-05, measured at 18:30Z) and a reason
    written only on a draw was never written. A stalled focus atom the draw no longer takes has
    its reason read here, from git, with `drawn_this_stretch: False` saying why.
    """
    try:
        from background.supervisor import ATOM_STALL_STATE_FILE
        state = json.loads(ATOM_STALL_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []
    cutoff = since.timestamp()
    focus_ids = {str(f.get("id") if isinstance(f, dict) else f) for f in focus}
    rows = []
    for aid, row in sorted(state.items()):
        if not (isinstance(row, dict) and row.get("stalled")):
            continue
        drawn = float(row.get("last_drawn_at") or 0.0) >= cutoff
        if not (drawn or aid in focus_ids):
            continue
        reason = ((drawn and row.get("stop_reason"))
                  or _stop_reason_read_now(aid, row, now or datetime.now(timezone.utc)))
        rows.append({"id": aid, "consecutive_unchanged": row.get("consecutive_unchanged"),
                     "drawn_this_stretch": drawn, "stop_reason": reason})
    return rows


def _stop_reason_read_now(atom_id: str, row: dict, now: datetime) -> str:
    """The supervisor's own reader, run here for a focus atom the draw no longer takes."""
    try:
        from background.supervisor import _atom_stop_reason
        atom = next((a for a in map_store.load_live_atoms() if a.get("id") == atom_id), None)
    except Exception as exc:  # noqa: BLE001 - the brief must not fail on its own diagnostic
        return f"the map could not be read ({type(exc).__name__}) -- cannot say"
    if atom is None:
        return "not on the live map, so its file_scope cannot be read -- cannot say"
    return _atom_stop_reason(atom, row.get("episode_started_at"), now.timestamp())


def focus_drawn_since(since: datetime) -> list[str]:
    """Everything the draw took in the stretch, ACROSS BOTH KEY SPACES.

    `atoms_drawn_since` reads `.atom_stall_tracker.json`, which is keyed by maturity-map atom id.
    A Lane 0 focus id is by construction NOT an atom -- that is `delivery_lane`'s founding premise
    -- so it could never appear there, and `focus_was_drawn`, which calls itself THE CONTROL ON
    THIS WHOLE MECHANISM, was asking whether a slug was in a dictionary that cannot hold slugs.

    Measured over 11 recorded orientations carrying 2-4 Lane 0 ids each: `drawn` contained a Lane
    0 slug ZERO times, and every `steered: True` was the same two perennial atoms the weighted
    draw was picking anyway. R15's fourth shape (a PASS branch that cannot be reached) made WORSE
    by a mixed subject, because the disjunction masked it as a pass instead of showing a constant
    False. `WORKER_FINDING_THE_STEER_EFFECTIVENESS_CONTROL_CANNOT_SEE_LANE_ZERO_AT_ALL_2026-08-27`
    names it and its fix 2 is this: give the slugs a channel, from the ledger of what the lane has
    actually handed out.

    AND A THIRD CHANNEL, 2026-09-02: what the SEAT EXECUTOR actually ran. The lane's ledger records
    what `draw()` handed out, and the executor's busiest route does not go through `draw()` -- a
    promoted continuation is taken straight from the handoff store. So the executor's log carried
    seven RUNNING/FINISHED pairs across five ids while this function, reading both of the other
    channels, still answered `[]` for every one of them. A steer that is biting presenting as a
    steer that is not is what makes the seat re-rank work already in hand.

    UNION, NOT REPLACEMENT: the three channels see three different routes and no one of them is a
    superset. Each under-reports on its own, which is why the disjunction is the honest read here
    and not the fail-open the same shape usually is -- there is no "did NOT happen" claim being
    OR'd away, only three partial records of what did.
    """
    from background import delivery_lane, seat_executor
    return sorted(set(atoms_drawn_since(since))
                  | set(delivery_lane.drawn_since(since.timestamp()))
                  | set(seat_executor.ids_run_since(since.timestamp())))


def _drawn_never_landed(now: datetime) -> list[dict]:
    """Lane 0 items handed out in the last day whose window closed with nothing committed.

    Imported here rather than at module level for the same reason `focus_drawn_since` does it:
    `delivery_lane` reaches back into this package and the pair is kept loadable by keeping the
    edge one-way at import time.
    """
    from background import delivery_lane

    return delivery_lane.drawn_without_landing(now=now.timestamp())


def _continuation_queue(now: datetime, since: datetime) -> dict:
    """The handoff store as the DRAW sees it: what `live()` will offer, and what was retired.

    THE ORIENTATION HAD NO KEY FOR THIS STORE, SO IT READ THE RAW ROWS. On 2026-10-04 at 14:25Z the
    orienting session ran `seat_continuation._load()` and printed `id`, `what`, `written_at` --
    a projection that drops `retired_at`. Two rows retired at 12:58Z and 13:46Z, one to two
    minutes after the commits that spent them, read exactly like queued work, and the record
    said they had "outlived the commits that spent them". Focus row two then cost a whole tick to
    find nothing. The store has three non-offered states (retired, superseded, expired) and a
    raw read shows none of them, so the brief carries the reading through the store's own
    predicates instead of leaving each session to hand-roll one.
    """
    from background import seat_continuation

    t = now.timestamp()
    try:
        offered = seat_continuation.live(now=t)
        retired = seat_continuation.retired()
    except Exception as exc:  # the brief must still assemble; the gap is stated, not hidden
        return {"readable": False, "why": f"{type(exc).__name__}: {exc}"}
    stretch_start = since.timestamp()
    return {
        "readable": True,
        "offered": [{"id": i.get("id"), "what": str(i.get("what") or "")[:200],
                     "hours_old": round((t - float(i.get("written_at") or 0.0)) / 3600.0, 1)}
                    for i in offered],
        # A RETIREMENT IS A FINISH, not a queue entry. Scoped to the stretch because an older one
        # is history; tombstones are kept and labelled, since a focus row finished this stretch is
        # the same news.
        "retired_this_stretch": [
            {"id": i.get("id"),
             "retired_at": datetime.fromtimestamp(float(i["retired_at"]), timezone.utc).isoformat(),
             "focus_row_tombstone": bool(i.get("focus_row_tombstone"))}
            for i in retired if stretch_start <= float(i.get("retired_at") or 0.0) <= t],
    }


def _previous_concern_ids() -> list[str]:
    """The concern ids the most recent ORIENTED decision row recorded -- the set a concern is
    "new" against for paging. A legacy row stored bare strings and yields no ids, so a row open at
    the first orientation after the shape changed is paged once, which is the honest reading."""
    for row in direction_mod.read_decisions(limit=50):
        if row.get("outcome") == "oriented":
            return [str(r.get("id")) for r in row.get("for_the_director") or []
                    if isinstance(r, dict) and r.get("id")]
    return []


def build_brief(now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    since = stretch_since(now)
    divergence = branch_divergence()
    commits = commits_since(since)
    previous = last_orientation() or {}
    prev_levels = previous.get("map_levels") or {}
    levels = map_levels()
    moved = {aid: [prev_levels.get(aid), lvl] for aid, lvl in levels.items()
             if aid in prev_levels and prev_levels.get(aid) != lvl}
    live = direction_mod.read_direction()
    prev_focus = tuple(previous.get("focus") or ())
    return {
        "now": now.isoformat(),
        "since": since.isoformat(),
        # FIRST, AND BEFORE `commits`, ON PURPOSE. The brief reaches the orienting session as
        # `json.dumps(...)[:60_000]` -- a truncation whose victim is whatever sorts last -- and the
        # statement that the reading covers both sides of a divergence is worth nothing if the
        # commit list can push it off the end.
        "divergence": divergence,
        # SECOND, AND AHEAD OF `commits`, FOR THE SAME REASON THE LINE ABOVE IS FIRST. A drawn item
        # that finished its window with nothing landed is invisible to every other key here:
        # `commits` cannot show work that was never committed, `atoms_drawn` says only that it WAS
        # handed out, and the claim it was handed out under has been swept back into the pool in
        # silence. The fact has been on disk in the draw ledger since the ledger was built --
        # `first_drawn_at` populated against no landing -- and nothing read it until 2026-09-07,
        # when two finished, correct, tested repairs sat uncommitted through four orientations
        # while the lane recorded both items as drawn and moved on. NOT scoped to the stretch:
        # three hours is shorter than the fact is interesting, and see
        # `delivery_lane.DRAWN_WITHOUT_LANDING_HORIZON_SECONDS` for why a day is the horizon.
        #
        # AND IT IS NOT `focus_`, WHICH IS WHAT THIS KEY WAS CALLED FOR ITS FIRST FIVE WEEKS.
        # `_drawn_never_landed` reads the claims ledger over ITS OWN horizon and returns EVERY
        # Lane 0 item handed out in it; nothing anywhere filters it to the focus. The name asserted
        # a population the value does not hold, and it sits inches from `previous_focus_drawn`,
        # which is the previous focus, over the stretch -- a different window AND a different
        # population, read side by side by the one reader both exist for. For four stretches the
        # two agreed only because the evidence happened not to contain a contradiction; on
        # 2026-09-21 it did -- this key held exactly one row, an ordinary draw that was never in
        # focus at all, while `previous_focus_drawn` correctly reported all three focus items
        # drawn. Both windows are now stated in the prompt sentences `_prompt` writes for them.
        "lane_0_drawn_never_landed": _drawn_never_landed(now),
        # AND THE ATOMS THE DRAW KEEPS TAKING WITHOUT MOVING, each with its reason, for the same
        # truncation reason: a counter alone sent the seat back to the same steer for three stretches.
        "atoms_stalled_with_reason": atoms_stalled_with_reason(
            since, prev_focus + tuple(live.focus if live else ()), now),
        # AND THE HANDOFF QUEUE, THIRD and for the same truncation reason: read through `live()`,
        # never the raw store -- see `_continuation_queue` for the focus row a raw read cost.
        "continuation_queue": _continuation_queue(now, since),
        "commits": commits,
        "commit_count": len(commits),
        "substantive_count": sum(1 for c in commits if c["substantive"]),
        "shape": commit_shape(since, now),
        # WHAT IS ON THE BOX, and AHEAD of the tree readings below for the same truncation reason
        # `divergence` is first. Every other key here describes the TREE; a job that is still
        # running has landed nothing, so it appears in none of them -- and it is the one fact that
        # has changed what this seat wrote twice in a row. Six consecutive orientations ran this
        # `ps` by hand before it was a key.
        "running": running_now(),
        # AND WHAT STOPPED, beside it. A job that died is in neither `running` nor any tree
        # reading, which is exactly how two deaths on 2026-09-29 went unseen for over an hour.
        "ended": ended_since(since),
        # AND WHAT ONLY A WORKTREE'S HEAD HOLDS. Finished commits on no remote ref are in no tree
        # reading either -- SPINE_1 lived for hours only at a detached HEAD and survived because
        # the console seat happened to remember it.
        "unlanded_worktree_commits": _unlanded_worktree_commits(),
        "findings": findings_now(),
        "levels_moved": moved,
        "levels_recorded": levels_recorded_since(since),
        # A ROW THE MAP CANNOT SEE MOVING IS WORSE THAN ONE THAT DID NOT MOVE. `levels_moved` and
        # `levels_recorded` above both need a level to have CHANGED to say anything; the absence
        # of a move that the evidence already supports is invisible to both, and it is what made
        # PB4 and PB6 sit at zero with their work landed and passing.
        "self_contradicting_levels": self_contradicting_levels(),
        "publish": publish_state(),
        "director_inputs": director_inputs(since),
        # THE FOLDER, NOT ITS DOCUMENTS. `findings_now()` above reads what is IN the staging root;
        # nothing read the root ITSELF, so it went from 15 documents to 168 in six days without a
        # single control having an opinion about it. Director, 2026-09-03: *"if it can grow
        # eleven-fold in six days with nothing reading it, that's the sediment alarm firing on
        # you."* Reported in the brief and NOT wired into `is_material`: a queue that is growing is
        # the normal state of a machine that files as it works, and orienting on it every three
        # hours would make every stretch material and tell the seat nothing.
        "staging_flow": staging_flow(),
        "previous_focus": list(prev_focus),
        # THE SELF-AUDIT'S CORRECTION LEG WAS UNFED BY CONSTRUCTION. The seat is required to write
        # `corrected: true|false` against every error, and the brief handed it `previous_focus` --
        # never the previous errors. So every `corrected` value in the record was RECONSTRUCTED
        # from whatever the orienting session happened to notice, not GRADED against the list it
        # was actually asked about, and an error nobody remembered simply left the record with no
        # verdict at all. Handing the rows back is what turns the field from a declaration into a
        # grade, and it is the same shape as `previous_focus_drawn`: the seat measures whether its
        # own last steer took, and now whether its own last errors were fixed.
        "previous_wrong": direction_mod.wrong_rows(previous),
        # THE CONCERNS STILL WAITING ON THE DIRECTOR, handed back so the session CARRIES them
        # rather than rewriting the list from memory -- the same shape as `previous_wrong`, and
        # `orient` refuses a record that drops one. `concerns_unpaged` is the open ids the last
        # ORIENTED row did not record, i.e. raised by the CLI since and not yet paged.
        "previous_for_the_director": director_concerns.open_rows(director_concerns.read_raw()),
        "concerns_unpaged": director_concerns.new_open_ids(
            _previous_concern_ids(), director_concerns.read_raw()),
        "atoms_drawn": atoms_drawn_since(since),
        # THE WINDOW IS PASSED, NOT ASSUMED. This one is the STRETCH -- `focus_drawn_since(since)`
        # and nothing older -- while `lane_0_drawn_never_landed` above is a day of the draw
        # ledger. The two sat side by side stating neither, which is how one reader took them for
        # one reading.
        "previous_focus_drawn": direction_mod.focus_was_drawn(
            prev_focus, focus_drawn_since(since), atom_ids=set(levels),
            window="this stretch only -- the {}h since {}".format(
                round((now - since).total_seconds() / 3600.0, 1), since.isoformat())),
        "live_direction_age_hours": round(live.age_hours(now), 1) if live else None,
        # THE LANDING DOOR, ASKED AT WRITE TIME. `delivery_lane.path_note` prints these verdicts to
        # whoever DRAWS an item, which closes the reader's half and leaves the writer's open: the
        # orientation is where a spent pile BECOMES an item, and it is the one place the read costs
        # nothing because the tree is already in hand. Measured on the four live focus items at
        # 07:40 on 2026-09-22, every file path the focus list named had nothing to land and the
        # list was authored blind to it. Graded against the LIVE record, because that is the one
        # whose items are about to be carried forward or dropped.
        "live_direction_path_concerns": direction_path_check.concerns(live.raw) if live else [],
    }


def is_material(brief: dict) -> tuple[bool, str]:
    """Is there anything to orient ON? Returns (yes, reason) either way, because the reason is
    recorded whichever it is."""
    if brief["substantive_count"]:
        return True, f"{brief['substantive_count']} substantive commit(s) in the stretch"
    # A STRETCH THAT COMMITTED AND CHANGED NOTHING IS A FINDING, NOT SILENCE, and getting these
    # two the same way round is the whole reason 29 empty merges went unremarked for three and a
    # quarter hours. Every other clause here asks "did something happen worth reacting to"; this
    # one asks "did the machine spend three hours producing commits that contain nothing", which
    # is a fault report about the machine and outranks a quiet night by a distance. It is placed
    # ABOVE the level and director clauses deliberately: a spinning daemon is why the rest of the
    # stretch is empty, so it is the thing to orient on first.
    shape = brief.get("shape") or {}
    if shape.get("shape_is_wrong"):
        kinds = ", ".join(sorted({f["kind"] for f in shape.get("findings", [])})) or "wrong shape"
        return True, (
            "the commit stretch reads wrong ({}): {} commit(s), {} carrying work, {} that changed "
            "nothing at all -- a machine fault, not a quiet stretch".format(
                kinds, shape.get("count"), shape.get("carrying_work"),
                shape.get("changed_nothing")))
    # A CHECKOUT THAT IS BEHIND ITS OWN BRANCH IS A MACHINE FAULT, and it is placed here with the
    # other machine fault rather than with the "did something happen" clauses. `behind` means the
    # daemons running from this tree are executing code the branch has moved past -- pushed is not
    # imported -- and it is precisely the state in which every OTHER clause below is least able to
    # be trusted. `ahead` alone is NOT listed: work committed here and not yet pushed is the normal
    # condition of a lane mid-turn, and orienting on it would fire on the seat's own commit.
    div = brief.get("divergence") or {}
    if div.get("available") and div.get("behind"):
        return True, (
            "this checkout is {} commit(s) behind origin/main, so anything running from it is on "
            "code the branch has moved past".format(div["behind"]))
    # WORK THAT WAS DRAWN, GIVEN ITS WINDOW, AND LANDED NOTHING. Placed with the machine faults
    # above the "did something happen" clauses, because it is one: the lane recorded the item as
    # handed out, the claim was swept back into the pool in silence, and every other clause here
    # reads a stretch in which -- as far as git can tell -- that work does not exist. On
    # 2026-09-07 that was two finished, tested, correct repairs sitting uncommitted while four
    # orientations ran. It outranks a quiet stretch because the bottleneck it names is not "the
    # lane is not drawing" but "the lane is drawing and nothing is coming out", and only the
    # second one is invisible to the commit count.
    missed = brief.get("lane_0_drawn_never_landed") or []
    if missed:
        return True, (
            "{} drawn Lane 0 item(s) finished their claim window with NOTHING landed -- {} -- so "
            "the ledger says they were handed out and git says nothing came of them".format(
                len(missed), ", ".join("{} ({}h ago)".format(r.get("id"), r.get(
                    "hours_since_draw")) for r in missed[:3])))
    # A LONG JOB THAT DIED IN THE STRETCH. Its work landed nothing, so every clause above and
    # below reads the stretch as if it had never been launched -- and a quiet stretch would skip
    # the one orientation that could relaunch it.
    died = (brief.get("ended") or {}).get("died") or []
    if died:
        return True, "{} long job(s) died in the stretch: {}".format(
            len(died), ", ".join("{} ({})".format(r["job"], r.get("result") or "no result")
                                 for r in died[:3]))
    if brief.get("levels_recorded"):
        return True, "{} level move(s) recorded in the ledger".format(
            len(brief["levels_recorded"]))
    if brief["levels_moved"]:
        return True, f"{len(brief['levels_moved'])} atom level(s) moved"
    if brief["director_inputs"]:
        return True, f"the director spoke: {', '.join(brief['director_inputs'][:3])}"
    if brief.get("concerns_unpaged"):
        return True, "{} concern(s) for the director raised since the last orientation and not " \
            "yet paged: {}".format(len(brief["concerns_unpaged"]),
                                   ", ".join(brief["concerns_unpaged"][:3]))
    findings = brief["findings"]
    if findings.get("blocking"):
        return True, f"{len(findings['blocking'])} BLOCKING finding(s) open"
    if brief["live_direction_age_hours"] is None:
        return True, "there is no live direction record at all"
    if brief["live_direction_age_hours"] > direction_mod.FOCUS_MAX_AGE_HOURS:
        return True, "the live direction has expired and would otherwise stop steering silently"
    return False, (
        "no substantive commit, no level move, no director input, no blocking finding, and the "
        "live direction is still inside its window -- there is nothing this stretch to orient on"
    )


# --------------------------------------------------------------------------- #
# Orienting                                                                    #
# --------------------------------------------------------------------------- #

def _resolve_claude() -> str | None:
    for candidate in (os.environ.get("CLAUDE_BIN"), "claude",
                      str(Path.home() / ".nvm/versions/node/v24.16.0/bin/claude")):
        if not candidate:
            continue
        try:
            if subprocess.run(["which", candidate], capture_output=True,
                              text=True, timeout=10).returncode == 0:
                return candidate
        except Exception:
            continue
        if Path(candidate).exists():
            return candidate
    return None


def _render_continuation_queue(queue: dict | None) -> str:
    """The handoff queue as sentences, so a retired row cannot be read as queued work."""
    if not queue or not queue.get("readable"):
        return ("\n\nTHE CONTINUATION QUEUE COULD NOT BE READ ({}). Do not reconstruct it from "
                "`seat_continuation._load()`: raw rows carry retired, superseded and expired "
                "entries that the draw never offers.".format((queue or {}).get("why", "absent")))
    offered = queue.get("offered") or []
    retired = queue.get("retired_this_stretch") or []
    return (
        "\n\nTHE CONTINUATION QUEUE, read through `seat_continuation.live()` -- exactly what the "
        "draw will offer, {} row(s). A row that is not listed here is NOT queued, whatever the "
        "raw store holds:\n\n".format(len(offered))
        + ("\n".join("- {} ({}h old): {}".format(r["id"], r["hours_old"], r["what"])
                      for r in offered) or "- (none)")
        + "\n\nRETIRED THIS STRETCH -- finished by the tick that held them; not queued, not "
          "owed:\n\n"
        + ("\n".join("- {} at {}{}".format(r["id"], r["retired_at"],
                                             " (focus-row tombstone)" if r.get(
                                                 "focus_row_tombstone") else "")
                      for r in retired) or "- (none)")
    )


def _prompt(brief: dict) -> str:
    # Imported here, not at module level, for `_drawn_never_landed`'s reason: `delivery_lane`
    # reaches back into this package and the pair is kept loadable by keeping the edge one-way at
    # import time. Read from the lane rather than restated, so the prose and the reader that
    # writes it cannot drift into two vocabularies for one store.
    from background.delivery_lane import DRAWN_WITHOUT_LANDING_HORIZON_SECONDS
    from background.delivery_lane import NOT_DONE as delivery_lane_NOT_DONE

    # READ FROM THE CONSTANT, NEVER TYPED. The sentences below are the only place a reader is told
    # what window this block covers, and a hand-typed "24 hours" beside a horizon that moves is
    # the same defect one layer down from the one being repaired here.
    horizon_hours = round(DRAWN_WITHOUT_LANDING_HORIZON_SECONDS / 3600.0, 1)

    # THE LIST GOES ABOVE THE JSON, AND OUTSIDE THE TRUNCATION. `brief` is dumped with a 60k cap
    # and `commits` is the first big key in it, so a long stretch can push everything after it off
    # the end -- including the one part of this brief that is meant to be READ rather than counted.
    # A vantage that a truncation can silently remove is not a vantage. Director, 2026-09-02:
    # *"every orientation reads the last stretch of commits as a list a person would read -- what
    # landed, what it was, whether the shape is right."*
    shape = brief.get("shape") or {}
    rendered = shape.get("rendered") or ""
    if not shape.get("available", True):
        rendered = "THE COMMIT STRETCH COULD NOT BE READ ({}) -- so its shape was NOT checked, " \
                   "and nothing below should be taken as evidence that it is sound.".format(
                       shape.get("why", "unknown"))
    # AND SO DOES THE LIST BEING GRADED, for the same reason and it is not a second instance of
    # the same lesson so much as the first one not being finished. `previous_wrong` is the
    # THIRTEENTH key of the brief, behind `commits` and behind `shape.rendered`, so on a long
    # stretch the seat would be told to grade a list that had been truncated off the end of its
    # own prompt -- and would then do exactly what it did before this field existed: write the
    # errors it happened to remember. An input that a truncation can silently remove is not an
    # input.
    # AND SO DOES THIS, and for a third time it is the same lesson unfinished rather than a new
    # one. `lane_0_drawn_never_landed` is the SECOND key of the brief precisely so a truncation
    # cannot reach it -- but a key the seat has to notice inside 60k of JSON is not the same thing
    # as a sentence it has to read. This is the one fact in the brief that is about work that
    # ALREADY EXISTS and only needs committing, so it belongs above the list of everything that
    # would otherwise be started instead.
    rows = brief.get("lane_0_drawn_never_landed") or []
    if rows:
        # AND EACH ROW NOW NAMES ITS DISPOSITION, because this sentence used to say one thing --
        # "nobody did it, check `git status`" -- about three different situations, and the seat
        # was grading its own steer on the total. A row whose premise was already spent is not
        # work sitting in the tree, and sending the reader to look for it there is how the same
        # open error got restated for seven stretches. `not_done` is the residual and the only
        # one the `git status` instruction is about, so it is the one the count is over.
        undisposed = [r for r in rows if r.get("disposition", delivery_lane_NOT_DONE)
                      == delivery_lane_NOT_DONE]
        missed = (
            "\n\nDRAWN, GIVEN ITS WINDOW, AND NOTHING LANDED UNDER ITS OWN NAME. MEASURED OVER "
            "THE LAST {}h OF THE DRAW LEDGER -- not over this stretch -- and over EVERY Lane 0 "
            "item the lane handed out in that horizon, whatever the focus of the day was. The "
            "lane handed "
            "each of these out and the claim was swept back into the pool with no commit bound "
            "to it. {} of the {} have NO disposition recorded, and THAT WORK MAY ALREADY BE DONE "
            "AND SITTING IN THE WORKING TREE -- that is what this looked like on 2026-09-07, "
            "twice, and finished work that never left the tree is worse than work not started, "
            "because the ledger says the item was drawn. CHECK `git status` FOR THE `not_done` "
            "ROWS BEFORE STARTING ANYTHING NEW. A row that is NOT `not_done` has been explained "
            "already and is not yours to redo; if one of the `not_done` rows landed under "
            "another id or was drawn against a premise something else had already spent, say so "
            "with `--landed-under` or `--premise-spent` rather than leaving it "
            "unnamed. A `landed_unbound` row is the one exception to `is not yours to redo` "
            "being the end of it: it names a commit that landed on that item's own paths inside "
            "its own window with nothing bound to it, which is evidence the work MOVED and not "
            "that it finished -- read the commit it names, then `--landed <id> --commit <sha>` "
            "if it is the work, and carry on from there rather than from "
            "scratch. A `premise_not_yet_ripe` row is the OPPOSITE instruction and the only one "
            "here that is about the FUTURE: its window closed before the instant its own prose "
            "names, so there was never anything to find -- do not go looking in the tree, and do "
            "not draw it again until the instant the evidence names has "
            "passed:\n\n".format(horizon_hours, len(undisposed), len(rows))
            + "\n".join("- {} (drawn {}h ago, {}{})".format(
                r.get("id"), r.get("hours_since_draw"),
                r.get("disposition", delivery_lane_NOT_DONE),
                ": " + r["evidence"] if r.get("evidence") else "") for r in rows)
        )
    else:
        missed = ("\n\nNO DRAWN LANE 0 ITEM finished its window without landing. MEASURED OVER "
                  "THE LAST {}h OF THE DRAW LEDGER -- the same horizon and the same population "
                  "as when this block has rows: every Lane 0 draw in it, not just the ones in "
                  "focus -- so everything the lane handed out either landed or is still inside "
                  "its window.".format(horizon_hours))
    # THE OTHER DRAWN-WORK READING, SAID NEXT TO THE FIRST AND SAID TO BE DIFFERENT. These two are
    # the only keys in the brief about work that was drawn, they are read side by side by the one
    # reader they exist for, and until 2026-09-21 neither stated its window and one of them was
    # named for a population it does not hold. They answer different questions over different
    # windows and CAN disagree without either being wrong; a reader that cannot tell them apart
    # reads a disagreement as a fault and a fault as a disagreement.
    steer = brief.get("previous_focus_drawn") or {}
    if steer:
        drawn_of = steer.get("drawn") or []
        focus_of = steer.get("focus") or []
        steered = (
            "\n\nAND SEPARATELY: DID LAST STRETCH'S FOCUS REACH THE DRAW. MEASURED OVER {} -- a "
            "different window from the block above, and a different population: the previous "
            "focus alone ({} named, {} drawn), never the whole lane. If this says the steer bit "
            "and the block above still lists work, that is not a contradiction: an item can be "
            "drawn on steer and land nothing, and an item never in focus can be drawn and land "
            "nothing.\n\n  {}".format(
                steer.get("window") or "AN UNSTATED WINDOW",
                len(focus_of), len(drawn_of), steer.get("note", "")))
    else:
        steered = ("\n\nWHETHER LAST STRETCH'S FOCUS REACHED THE DRAW WAS NOT MEASURED in this "
                   "brief, so the block above is the only drawn-work reading here and it is not "
                   "about the focus.")
    stalled_rows = brief.get("atoms_stalled_with_reason") or []
    if stalled_rows:
        steered += (
            "\n\nSTALLED ATOMS, drawn this stretch or in focus, each with the reason read from "
            "git over the atom's own file_scope. A focus atom marked 'not drawn' is one the "
            "anti-livelock draw has stopped taking, so nothing reaches it unless a Lane 0 slice "
            "names it. Working the atom happens through such a slice, not through the draw:\n\n"
            + "\n".join("- {} ({} unchanged draws{}): {}".format(
                r.get("id"), r.get("consecutive_unchanged"),
                "" if r.get("drawn_this_stretch", True) else "; not drawn this stretch",
                r.get("stop_reason"))
                for r in stalled_rows))
    # THE LANDING DOOR'S VERDICT ON THE ITEMS YOU ARE ABOUT TO CARRY FORWARD, and it is a SENTENCE
    # for the same reason the two blocks above are: a key buried in 60k of JSON is a key that gets
    # read on the quiet stretches and skipped on the busy ones. This is the WRITE-TIME half of
    # `delivery_lane.path_note` -- the draw can only annotate prose that already exists, and the
    # focus list is where a spent ask becomes an item.
    path_rows = brief.get("live_direction_path_concerns") or []
    if path_rows:
        verdicts = (
            "\n\nTHE LANDING DOOR HAS AN OPINION ABOUT THE LIVE FOCUS ITEMS' OWN PATHS, read from "
            "the shared tree's working copies. It ANNOTATES and never refuses, and each row "
            "carries the evidence that would overturn it -- a change set with nothing to land is "
            "also what an item whose real subject is a directory looks like. Re-run it against a "
            "draft before you file it: `python3 -m background.direction_path_check --record "
            "<file>`.\n\n"
            + "\n".join("- [{}] {}: {}".format(r.get("class"), r.get("id"), r.get("says"))
                        for r in path_rows))
    else:
        verdicts = ""
    prior = brief.get("previous_wrong") or []
    if prior:
        open_rows = [r for r in prior if r.get("corrected") is False]
        graded = (
            "\n\nWHAT YOU SAID WAS WRONG LAST STRETCH, and your verdict on each. THIS IS A LIST "
            "TO GRADE, NOT A LIST TO REPLACE: every row still marked open must appear in your "
            "`wrong` again -- still `corrected: false`, or `corrected: true` with the evidence in "
            "`thesis_read`. An open error that quietly stops being listed has not been fixed, it "
            "has been forgotten.\n\n"
            + "\n".join(
                "- [{}] {}".format(
                    {True: "corrected", False: "STILL OPEN"}.get(r.get("corrected"),
                                                                 "no verdict recorded"),
                    r.get("what", ""))
                for r in prior)
            + "\n\n{} of {} still open.".format(len(open_rows), len(prior))
        )
    else:
        graded = ("\n\nNO PREVIOUS SELF-AUDIT ROWS were recorded, so there is nothing to grade. "
                  "That is either a clean stretch or a seat that stopped looking, and only you "
                  "can say which.")
    # AND SO DOES WHAT IS ON THE BOX, for the same truncation reason and because this one has to
    # be a SENTENCE rather than a key. The seat ran this `ps` by hand at six consecutive
    # orientations; a fact it has to dig out of 60k of JSON is a fact it will dig out on the
    # stretches when it is not busy and skip on exactly the stretches when the box is.
    running = brief.get("running") or {}
    # THE DECLARED DAEMONS THAT ARE NOT THERE, said first and said unasked. This block is
    # deliberately OUTSIDE the three branches below, because the branch an absence lands in is the
    # idle one -- a box with no daemons on it has no long jobs either, so the old reading answered
    # a dead machine with "NOTHING LONG IS RUNNING. Anything you start, you are starting from
    # cold," which is true, cheerful, and the single most misleading sentence the brief can print.
    absent = running.get("declared_absent") or []
    if not running.get("available", False):
        # The ps never ran, so `declared_absent` is empty for the reason that proves nothing. An
        # empty list and an unasked question are the same shape and opposite in meaning; the
        # unreadable-box sentence below carries this case on its own.
        absence_sentence = ""
    elif running.get("declared_unreadable"):
        absence_sentence = (
            "\n\nWHICH DECLARED DAEMONS ARE ABSENT COULD NOT BE READ ({}) -- so nothing below "
            "says they are present.".format(running["declared_unreadable"]))
    elif absent:
        absence_sentence = (
            "\n\n{} DECLARED DAEMON(S) ARE NOT ON THE BOX. Every one of these is `state: enabled` "
            "in `background/process_manifest.yaml`, which means it MUST be running; nothing "
            "starts it except the declaration. This outranks whatever else this brief says is "
            "due, because the readings below describe a tree that nothing is currently working "
            "on:\n\n".format(len(absent))
            + "\n".join(
                "  {:<22} absent; last wrote its own log {}".format(
                    r["session"],
                    "{} ago".format(r["last_log"]) if r["last_log"] is not None
                    else r["why_no_log"] or "at an unknown time")
                for r in absent)
            # Said in the absent branch too: a box can have one daemon missing AND another mute,
            # and the mute one would otherwise be invisible for exactly as long as the absence
            # takes to fix -- the reading would go quiet about it the moment something else broke.
            + _mute_sentence(running.get("declared") or []))
    else:
        # MUTE is taken out of the quiet population FIRST. A daemon that has written nothing at
        # all in this run would otherwise sort into the same list as one that logs hourly and
        # render as the same row -- just with a bigger number -- and the reader would apply the
        # same "no common cadence, judge it yourself" licence to both. It is not the same
        # observable: quiet is a daemon with nothing to say, mute is a daemon that has never
        # spoken, and only the second is consistent with a process that is up and doing nothing.
        declared_rows = running.get("declared") or []
        quiet = [r for r in declared_rows
                 if r["last_log_seconds"] is not None and not r.get("mute")]
        quiet.sort(key=lambda r: -r["last_log_seconds"])
        absence_sentence = (
            "\n\nEVERY DECLARED DAEMON IS ON THE BOX ({} of them, positively matched against "
            "`process_manifest.yaml` rather than inferred from an empty list).".format(
                len(declared_rows))
            + (" The quietest has not written its own log for {} (`{}`) -- no threshold is "
               "applied to that, because these daemons have no common cadence; judge it "
               "yourself, and note that ALL of them going quiet together is what a frozen "
               "guest looks like.".format(quiet[0]["last_log"], quiet[0]["session"])
               if quiet else "")
            + _mute_sentence(declared_rows))
    if not running.get("available", False):
        running_sentence = (
            "\n\nWHAT IS RUNNING COULD NOT BE READ ({}) -- so 'nothing is running' is NOT what "
            "this says, and a long job may be in flight.".format(running.get("why", "unknown")))
    elif running.get("nothing_long_running"):
        running_sentence = (
            "\n\nNOTHING LONG IS RUNNING. Positively measured, not inferred from an empty list: "
            "`ps` ran, and after subtracting the {} declared daemons no process of this project's "
            "has been up longer than {}s. Anything you start, you are starting from cold.".format(
                running.get("daemons_subtracted", 0), running.get("floor_seconds")))
    else:
        running_sentence = (
            "\n\nWHAT IS ON THE BOX RIGHT NOW, with the {} declared permanent daemons subtracted "
            "so the jobs are not buried. DO NOT LAUNCH SOMETHING THAT IS ALREADY RUNNING, and do "
            "not write a focus that assumes a job has not started:\n\n".format(
                running.get("daemons_subtracted", 0))
            + "\n".join(
                "  {:>8}  {:>8}  {:>7}MB  {}".format(
                    j["pid"], j["elapsed"], j["rss_mb"], j["what"])
                for j in running.get("jobs", [])))
    ended = brief.get("ended") or {}
    if not ended.get("available", False):
        ended_sentence = (
            "\n\nWHICH LONG JOBS ENDED COULD NOT BE READ ({}) -- so 'none died' is NOT what this "
            "says.".format(ended.get("why", "the reading was not taken")))
    elif not ended.get("jobs"):
        ended_sentence = (
            "\n\nNO `launch_long_job` JOB LAUNCHED OR ENDED IN THIS STRETCH, read from the launch "
            "register and not inferred from what is still running.")
    else:
        def _when(j):
            if j["ended_at"]:
                return "ended {}".format(j["ended_at"])
            return "ended by {} (settle time; exit time not recorded)".format(j["ended_by"])
        ended_sentence = (
            "\n\nLONG JOBS THAT STOPPED IN THIS STRETCH -- the complement of the list above, from "
            "the launch register. {} DIED. A died job landed nothing; before focusing on its "
            "subject, read its log and decide whether to relaunch, and never write that its run "
            "is in flight:\n\n".format(len(ended.get("died") or []))
            + "\n".join(
                "  {:<8} {:<32} {}  Result={} status={}  log {}".format(
                    "DIED" if j["claim"] == "died" else j["claim"], j["job"], _when(j),
                    j["result"] or "?", j["exit_status"] or "?", j["log"] or "none")
                for j in ended["jobs"]))
    queue_sentence = _render_continuation_queue(brief.get("continuation_queue"))
    concerns = brief.get("previous_for_the_director") or []
    carried = (
        "\n\nTHE DIRECTOR'S OPEN CONCERNS -- CARRY EVERY ONE FORWARD under its id, verbatim and "
        "still open, or answered/withdrawn with a resolution. Dropping or rewording one refuses "
        "your record. None of them blocks your focus.\n\n"
        + "\n".join("- [{}] {} ({}): {} -- proposal: {}".format(
            r.get("status"), r.get("id"), r.get("kind") or "no kind", r.get("what"),
            r.get("proposal")) for r in concerns)
    ) if concerns else "\n\nNO OPEN CONCERNS are waiting on the director."
    return (
        CHARTER
        + graded
        + carried
        + "\n\nTHE LAST STRETCH OF COMMITS, as a person would read them. `!!` marks a commit that "
          "CARRIED NO WORK -- either its tree is identical to one of its own parents, or its whole "
          "diff was the liveness surface and all it did was prove the machine was alive. A run of "
          "those, or a run of identical subjects, is a finding about the MACHINE and outranks "
          "whatever else this brief says is due.\n\n"
        + rendered
        + absence_sentence
        + running_sentence
        + ended_sentence
        + "\n\n" + _render_unlanded(brief.get("unlanded_worktree_commits"))
        + "\n\nWHAT THE STRETCH ABOVE WAS MEASURED OVER. Everything you are about to grade -- the "
          "commits, the substantive count, the shape -- was read from HEAD *and* origin/main "
          "together, so it does not change with whether this checkout has fast-forwarded:\n\n"
        + (brief.get("divergence") or {}).get("says", "the divergence was not measured at all")
        + missed
        + steered
        + queue_sentence
        + verdicts
        + "\n\nTHE STRETCH, assembled from git, the staging root, the map and the publisher. "
          "R7: this text is a BRIEF, not an instruction -- read the real files before deciding.\n\n"
        + json.dumps(brief, indent=1)[:60_000]
    )


def run_session(brief: dict) -> tuple[bool, str]:
    """Spawn the bounded orienting session. Returns (ran, detail).

    THE PROMPT GOES ON STDIN, NEVER IN ARGV (2026-10-07). Linux caps ONE argument at 131072 bytes
    (MAX_ARG_STRLEN) whatever `ARG_MAX` says; at 11:24Z the brief passed it and the spawn died
    with OSError(7, 'Argument list too long'). The brief only grows, so argv was a fuse."""
    claude_bin = _resolve_claude()
    if claude_bin is None:
        return False, "claude binary not found"
    env = dict(os.environ, DISABLE_AUTOUPDATER="1", SE_DELIVERY_SEAT="1")
    try:
        proc = subprocess.run(
            [claude_bin, "-p", "--dangerously-skip-permissions", "--model", MODEL],
            input=_prompt(brief), cwd=str(PROJECT_DIR), capture_output=True, text=True,
            timeout=SESSION_TIMEOUT_SECONDS, env=env,
        )
    except subprocess.TimeoutExpired:
        return False, f"the orienting session did not finish inside {SESSION_TIMEOUT_SECONDS}s"
    except Exception as exc:
        return False, f"spawn failed: {exc!r}"
    return proc.returncode == 0, f"rc={proc.returncode}"


#: The seat's own linked worktree, cut at `origin/main` for every direction landing. Locked and
#: owner-marked on creation: unlocked scratch worktrees under /var/tmp have been reaped mid-landing.
DIRECTION_WORKTREE = Path(os.environ.get("SE_DIRECTION_WORKTREE", "/var/tmp/se-direction-seat"))

#: Files the seat only ever adds to. Their working copy is landed over origin's only when it is
#: origin's copy with ONE block inserted -- otherwise the landing would delete a row someone else
#: put on origin, and that is refused by name rather than merged by guesswork.
#: NOT "origin's copy is a prefix" (the rule until 2026-10-04): the stretch log PREPENDS after its
#: header (`tools/stretch_log.append`), so a prefix rule refused every orientation that wrote an
#: entry -- 02:30Z and 08:25Z on 10-04 -- and the feed carrying H45's hand-read field sat on disk.
APPEND_ONLY = ("docs/direction/decisions.jsonl", "docs/status/SEAT_STRETCH_LOG.md")


class DirectionNotLanded(RuntimeError):
    """The direction record did not reach origin. The message names why."""


def _git_in(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(root), capture_output=True, timeout=300)


def _origin_bytes(root: Path, path: str) -> bytes | None:
    out = _git_in(root, "show", f"origin/main:{path}")
    return out.stdout if out.returncode == 0 else None


def keeps_all_of(ours: bytes, theirs: bytes) -> bool:
    """True when `ours` is `theirs` with one contiguous block inserted anywhere -- appended rows
    and an entry prepended under a header both qualify; a changed or dropped byte does not."""
    head = len(os.path.commonprefix([ours, theirs]))
    return len(ours) >= len(theirs) and ours.endswith(theirs[head:])


def _refuse_an_append_only_rewrite(root: Path, content: dict[str, bytes]) -> None:
    for path in APPEND_ONLY:
        theirs = _origin_bytes(root, path)
        if path in content and theirs is not None and not keeps_all_of(content[path], theirs):
            raise DirectionNotLanded(
                f"{path} on origin/main is not kept whole by this tree's copy (it is not origin's "
                f"copy plus one inserted block), so landing it would delete what origin holds. Not "
                f"merged by guesswork: the file needs a hand landing that keeps both sides")


def _cut_direction_worktree(root: Path, worktree: Path) -> None:
    """Put `worktree` at the freshly fetched `origin/main`. The worktree is the seat's alone and
    holds nothing the shared tree does not: every landing's bytes are re-read from the shared
    copy, so resetting it discards at most a landing origin has already moved past."""
    if (worktree / ".git").exists():
        reset = _git_in(worktree, "reset", "--hard", "--quiet", "origin/main")
        if reset.returncode != 0:
            raise DirectionNotLanded(f"could not reset {worktree} to origin/main: "
                                     f"{reset.stderr.decode(errors='replace')[-300:]}")
    else:
        _git_in(root, "worktree", "prune")
        add = _git_in(root, "worktree", "add", "--detach", str(worktree), "origin/main")
        if add.returncode != 0:
            raise DirectionNotLanded(f"could not cut {worktree} at origin/main: "
                                     f"{add.stderr.decode(errors='replace')[-300:]}")
        _git_in(root, "worktree", "lock", str(worktree), "--reason", "the delivery seat's own")
    (worktree / ".se_worktree_owner").write_text(str(os.getpid()))


#: The reconciling merge's message. `NEXT:` is the commit-msg gate's own trailer.
DIRECTION_MERGE_MESSAGE = ("delivery seat: merge origin/main into the direction landing (upstream "
                           "does not touch its paths)\n\nNEXT: none -- a reconciling merge; the "
                           "record's own next step is the direction it carries")


def _origin_touched(worktree: Path, landing: list[str]) -> list[str]:
    """The landing's paths that origin changed since this landing's base. A path that cannot be
    asked counts as touched, so the cheap route is never taken on a question git did not answer."""
    base = _git_in(worktree, "merge-base", "HEAD", "origin/main")
    if base.returncode != 0:
        return list(landing)
    diff = _git_in(worktree, "diff", "--name-only", base.stdout.decode().strip(), "origin/main",
                   "--", *landing)
    if diff.returncode != 0:
        return list(landing)
    return diff.stdout.decode().split()


def _merge_origin_into(worktree: Path, lander) -> str:
    """Land origin/main INTO the gated landing through the door's own `--merge`, and return the
    merge's sha. The door gates it like any landing, selecting tests on the merge's combined diff:
    when origin's new commits touch none of the landing's paths that diff is empty and no test is
    selected, so this costs the structural gates, not the ~15 minutes a re-cut spends re-running
    the 35 tests the record's paths select. A red gate is raised, never retried."""
    from tools import surgical_land
    try:
        return lander(worktree, [], DIRECTION_MERGE_MESSAGE, attempts=1, merge="origin/main")
    except surgical_land.IndexNotRefreshed as exc:
        _git_in(worktree, "reset", "--quiet")
        return exc.sha


def land_direction_on_origin(root: Path, paths: list[str], message: str,
                             content: dict[str, bytes], *, worktree: Path | None = None,
                             lander=None, promoter=None, regenerate=None,
                             deadline_s: float = 0.0, clock=None) -> str:
    """Land `content` onto `origin/main` itself, never onto the shared HEAD, and return the sha.

    WHY NOT THE SHARED HEAD (2026-10-04). The shared tree sits behind AND diverged from origin as
    a standing state, not a moment, so a direction commit made there and then pushed was refused
    every time: 543dcff6d and 7234966b2 stayed local-only while origin's DIRECTION.yaml -- the
    record the director reads -- stood at the 10-03 14:21 orientation for two stretches. Here the
    landing is gated in the seat's own worktree cut at `origin/main`, so it is a fast-forward by
    construction, and `promote_worktree_landing` pushes it and verifies origin moved.

    THE LOOP IS ONLY OVER ORIGIN MOVING under the gate. Any other refusal -- a red gate, a dirty
    worktree, a duplicate claim -- is raised on the first attempt; retrying a verdict is how a
    flaky test becomes a landed regression.

    UNTIL `deadline_s`, NOT TWO ATTEMPTS (2026-10-07). A busy origin is the normal case: on 10-07
    origin moved twice in 50 minutes, the second attempt lost too, and origin's record stood three
    hours stale. One attempt always runs; another starts only while `deadline_s` has not passed.
    Each re-base re-cuts at the new origin and writes the same bytes, which is safe only while
    origin's DIRECTION.yaml is still the copy the first attempt saw -- the seat's own file, which
    nobody else edits. If it changed, someone did, and that is refused by name, not overwritten.

    A LOST RACE IS SETTLED BY A MERGE WHEN ORIGIN DID NOT TOUCH THE RECORD (2026-10-07). The 17:22
    record lost all 3 attempts in 2637 s: each re-cut re-ran the full gate (~880 s; the record's
    paths select 35 test files and the site lane), and origin gained 2-4 commits an hour, so a
    15-minute gate loses about as often as it wins. When none of origin's new commits touch the
    landing's paths, the gated commit stands and origin is merged into it through the door; only
    when they do is the landing re-cut, where the base check above refuses another writer's edit."""
    from tools import promote_worktree_landing as promote_mod
    from tools import surgical_land

    worktree = worktree or DIRECTION_WORKTREE
    lander = lander or surgical_land.land
    promoter = promoter or promote_mod.promote
    clock = clock or _monotonic
    started, base, moved = clock(), None, []
    while True:
        _git_in(root, "fetch", "--quiet", "origin")
        record = _origin_bytes(root, DIRECTION_RECORD)
        if moved and record != base:
            raise DirectionNotLanded(f"origin/main moved under the gate {len(moved)} time(s) and "
                                     f"its {DIRECTION_RECORD} is no longer the copy this record "
                                     f"was written against, so another writer edited it. Not "
                                     f"re-based over it: " + " | ".join(moved))
        base = record
        # ASKED OF EVERY ORIGIN, not only the first: a move can carry an append to these files too.
        _refuse_an_append_only_rewrite(root, content)
        _cut_direction_worktree(root, worktree)
        # THE WORKTREE'S FILES CARRY THE BYTES TOO. The door commits `content` without touching the
        # working copy, which then still holds origin's old bytes -- and promotion refuses that as
        # uncommitted work. Found on this route's first hand landing, 2026-10-04.
        for rel, data in content.items():
            (worktree / rel).parent.mkdir(parents=True, exist_ok=True)
            (worktree / rel).write_bytes(data)
        landing, landed_content = list(paths), dict(content)
        page = (regenerate or regenerate_startup_anchors)(worktree)
        if page is not None:
            landed_content[STARTUP_ANCHORS_PAGE] = page
            # The worktree's copy carries the bytes too, as the record's do above.
            (worktree / STARTUP_ANCHORS_PAGE).parent.mkdir(parents=True, exist_ok=True)
            (worktree / STARTUP_ANCHORS_PAGE).write_bytes(page)
            if STARTUP_ANCHORS_PAGE not in landing:
                landing.append(STARTUP_ANCHORS_PAGE)
        try:
            sha = lander(worktree, landing, message, attempts=1, content=landed_content)
        except surgical_land.IndexNotRefreshed as exc:
            # THE COMMIT LANDED; only this worktree's index lags it, and the index is ours alone.
            sha = exc.sha
            _git_in(worktree, "reset", "--quiet")
        tip = sha
        while True:
            try:
                promoter(worktree)
                return sha
            except promote_mod.PromotionRefused as exc:
                _git_in(worktree, "fetch", "--quiet", "origin")
                if _git_in(worktree, "merge-base", "--is-ancestor", "origin/main",
                           tip).returncode == 0:
                    raise DirectionNotLanded(f"landed {tip[:9]} in {worktree} and the push "
                                             f"was refused: {exc}") from exc
                moved.append(str(exc).splitlines()[0][:160])
            if clock() - started >= deadline_s or _origin_touched(worktree, landing):
                break
            tip = _merge_origin_into(worktree, lander)
        if clock() - started >= deadline_s:
            raise DirectionNotLanded(f"origin/main moved under the gate on all {len(moved)} "
                                     f"attempt(s) inside {deadline_s:.0f}s: " + " | ".join(moved))


#: THE PAGE AN ADVISOR ORIENTS FROM, refreshed on every orientation (director, 2026-10-04: "It's only
#: refreshed on publish, which is weekly now, so the page an advisor orients from can be a week
#: stale. Regenerate it whenever an anchor changes."). The anchors change every stretch -- this seat's
#: own DIRECTION.yaml, decisions.jsonl and stretch log are three of them -- and this seat is the one
#: writer that lands on origin every three hours, so the page is at most a stretch old. A change to the
#: anchor SET is refused in the same commit unless the page is regenerated
#: (`startup_anchor_freshness.anchor_set_refusal`).
STARTUP_ANCHORS_PAGE = "docs/status/STARTUP_ANCHORS.md"


def regenerate_startup_anchors(worktree: Path) -> bytes | None:
    """The startup-anchor page as the worktree's OWN tool computes it from the worktree's history,
    or None. Generated in the landing worktree, cut at origin, never from the shared tree: the shared
    tree lags origin, and a page computed there would describe a stale anchor set and could REGRESS
    origin's copy. The page is downstream of the record, so any failure returns None and the record
    lands without it."""
    tool = worktree / "tools" / "startup_anchor_freshness.py"
    out = worktree / STARTUP_ANCHORS_PAGE
    if not tool.is_file():
        return None
    try:
        before = out.read_bytes() if out.is_file() else None
        subprocess.run([sys.executable, str(tool)], cwd=str(worktree), capture_output=True,
                       timeout=300, env=dict(os.environ, PYTHONPATH=str(worktree)))
        after = out.read_bytes() if out.is_file() else None
    except (OSError, subprocess.SubprocessError):
        return None
    return after if after is not None and after != before else None


#: WHAT THE SEAT ITSELF WRITES AND COMMITS BESIDE THE DIRECTION RECORD -- written by this module's own
#: code after the session has exited, never by the orienting session, whose charter still forbids
#: it every file but `DIRECTION.yaml`. Kept apart from `direction_mod.WRITE_SCOPE` so the session's
#: scope does not widen.
SEAT_WRITTEN = ("docs/status/SEAT_STRETCH_LOG.md",)


def stretch_entry_from_row(row: dict) -> tuple[str, str]:
    """The stretch-log entry for one orientation, rendered from the decision row it already recorded.

    THE LOG'S ONLY WRITER USED TO BE AN INTERACTIVE SESSION, present only while the director is
    (`SEAT_FINDING_THE_STRETCH_LOG_HAS_ONE_WRITER_...`, 2026-09-30). Every fix to its alarm went quiet
    within a week because none changed the writer, while this seat wrote the same reflection every
    three hours into `decisions.jsonl`. So this seat is now the writer that cannot be absent; the
    interactive seat still adds entries when it closes a piece of its own. Nothing here is invented:
    every line is a field of the row.
    """
    thesis = " ".join((row.get("thesis_read") or "").split())
    first = thesis.split(". ")[0].rstrip(".")
    subject = f"orientation: {first}"[:180]
    if not first or stretch_log_mod.validate_subject(subject):
        subject = ("orientation: what the stretch meant against the thesis, what went wrong, and "
                   "what was chosen against")
    wrong = row.get("wrong") or []
    lines = [f"*Written by the orientation seat from its own record ({row.get('at', '?')}; "
             f"{row.get('commits', '?')} commits, {row.get('substantive', '?')} substantive, since "
             f"{row.get('since', '?')}).*", "", "## What the stretch meant", "", thesis or "(no reading)", ""]
    lines += ["## What went wrong", ""]
    lines += [f"- {'corrected' if w.get('corrected') else 'NOT corrected'}: {w.get('what')}" for w in wrong] \
        or ["- nothing recorded"]
    lines += ["", "## Chosen against", ""]
    lines += [f"- {w}" for w in (row.get("not_now") or [])] or ["- nothing recorded"]
    lines += ["", "## Focus for the next stretch", ""]
    lines += [f"- `{f}`" for f in (row.get("focus") or [])] or ["- none"]
    return subject, "\n".join(lines)


def skipped_entry_from_row(row: dict) -> tuple[str, str]:
    """The entry for a SKIPPED run: that it skipped and the reason it recorded, and nothing else.

    WHY A SKIP WRITES AT ALL. The check escalates on its clock, so a skip that wrote nothing made a
    quiet stretch (or the director's own tick-mode hold) page exactly like a stopped writer, and the
    page could not say which. With every run writing, an escalation means the orientation stopped.
    No reflection is invented: the seat judged the stretch not material and this says only that.
    """
    why = " ".join(str(row.get("why") or "no reason recorded").split())
    subject = f"orientation skipped: {why}"[:180]
    if stretch_log_mod.validate_subject(subject):
        subject = "orientation skipped: the stretch was judged not material, reason below"
    body = (f"*Written by the orientation seat from its own record ({row.get('at', '?')}; "
            f"{row.get('commits', '?')} commits, {row.get('substantive', '?')} substantive, since "
            f"{row.get('since', '?')}).*\n\nThe seat did not orient, so there is no reading of "
            f"this stretch against the thesis. Its recorded reason: {why}")
    return subject, body


def write_stretch_entry(row: dict, append_fn=None) -> bool:
    """Append the run's entry to the stretch log: an oriented row's reading, or a skipped row's
    reason. A row with neither (a refusal, an oriented row whose reading is empty) writes nothing,
    and the check then escalates on its own clock, which is the right signal.
    Never raises: the log is downstream of the decision record, never a reason to lose it."""
    oriented = row.get("outcome") == "oriented" and (row.get("thesis_read") or "").strip()
    if not oriented and row.get("outcome") != "skipped":
        row["stretch_entry"] = False
        return False
    try:
        entry = stretch_entry_from_row(row) if oriented else skipped_entry_from_row(row)
        (append_fn or stretch_log_mod.append)(*entry)
        row["stretch_entry"] = True
    except Exception as exc:  # noqa: BLE001
        row["stretch_entry"] = False
        _log(f"stretch-log entry NOT written ({type(exc).__name__}: {exc}) -- the check will escalate")
    return row["stretch_entry"]


DIRECTION_RECORD = "docs/direction/DIRECTION.yaml"

#: WHEN A DIRECTION LANDING STOPS STARTING ATTEMPTS, and it is the unit's budget, not a count. Two
#: attempts (the publish landing's argument) gave up silently on 10-07 when origin moved twice in 50
#: minutes. The real bound is the cgroup: `delivery-seat.service` kills the whole run at
#: `TimeoutStartSec`, and a landing killed mid-gate writes no refusal and pages nobody. So a new
#: attempt starts only while one more full gate still fits: the budget, less what this process has
#: already spent (the session included), less one gate run -- 15-25 min measured, per the unit's own
#: comment, so the top of that range.
DIRECTION_UNIT = Path.home() / ".config/systemd/user/delivery-seat.service"
DIRECTION_UNIT_FALLBACK_BUDGET_S = 4500   # the unit's TimeoutStartSec on 2026-10-04, if unreadable
DIRECTION_GATE_RUN_S = 1500
_PROCESS_STARTED = time.monotonic()
_monotonic = time.monotonic   # the landing loop's clock, a seam for its control


def direction_unit_budget_s(unit: Path | None = None) -> float:
    """`TimeoutStartSec` as the unit file states it, else the named fallback."""
    try:
        lines = (unit or DIRECTION_UNIT).read_text(encoding="utf-8").splitlines()
    except OSError:
        lines = []
    found = [value.strip() for key, _, value in (line.partition("=") for line in lines)
             if key.strip() == "TimeoutStartSec" and value.strip().isdigit()]
    return float(found[-1]) if found else float(DIRECTION_UNIT_FALLBACK_BUDGET_S)


def direction_land_deadline_s(now: float | None = None) -> float:
    """Seconds from now within which a direction landing may still START another attempt."""
    spent = (time.monotonic() if now is None else now) - _PROCESS_STARTED
    return max(0.0, direction_unit_budget_s() - spent - DIRECTION_GATE_RUN_S)


def commit_direction(lander=None) -> tuple[bool, str]:
    """Commit ONLY `direction.WRITE_SCOPE`. THE PATHSPEC IS THE CONTROL, not a promise: anything
    the session touched outside it is left where it is, so this seat cannot become a writer on
    the code tree even if its session tries to be one.

    THROUGH `surgical_land.land`, NOT `git commit` (2026-10-03). Of the 11 failed commits since
    the reason was logged (09-30), 10 were contention and not a verdict: HEAD moved under the
    ~18-minute gate six times ("cannot lock ref 'HEAD'"), and another writer held `index.lock`
    at `git add` four times. Neither was retried, so the record and the feed stayed uncommitted
    until the next orientation, three hours on -- and that held H45's level, which waits on this
    feed. The landing door gates the tree the commit would create, never takes the shared index,
    and re-gates when the race is lost; a red gate stays terminal.

    ONTO ORIGIN, NOT THE SHARED HEAD (2026-10-04) -- see `land_direction_on_origin`. The shared
    working copy is left as it is; it reads dirty against its own HEAD until the tree advances."""
    present = [p for p in (*direction_mod.WRITE_SCOPE, *SEAT_WRITTEN) if (PROJECT_DIR / p).exists()]
    if not present:
        return False, "nothing in the write scope exists to commit"
    # ASKED OF ORIGIN, NOT HEAD: the landing goes to origin and the shared HEAD lags it, so a
    # record already on origin still reads dirty against HEAD and would be landed as a no-op.
    _git("fetch", "--quiet", "origin")
    if not _git("diff", "--name-only", "origin/main", "--", *present).strip():
        return True, "nothing changed in the write scope"
    content = {p: (PROJECT_DIR / p).read_bytes() for p in present}
    try:
        sha = (lander or land_direction_on_origin)(
            PROJECT_DIR, present, "delivery seat: direction for the next stretch", content,
            deadline_s=direction_land_deadline_s())
    except Exception as exc:  # noqa: BLE001 -- a refusal is a value; the record is already on disk
        # The refusal's own words are the diagnosis (2026-09-30: a bare rc classified nothing).
        why = refusal_verdict(str(exc))
        return False, f"landing refused ({type(exc).__name__}): {why or 'no message'}"
    return True, f"commit rc=0; landed {sha[:9]} on origin/main"


def refusal_verdict(text: str, limit: int = 600) -> str:
    """The refusal's head line and the lines that name what went red, joined on one line.

    THE FIRST THREE LINES WERE THE BOILERPLATE (2026-10-09 02:43). A red gate's refusal from
    `surgical_land` opens with its own header, then `[live-hook]` and the `✓` lines of every check
    that PASSED, and only then the refusing step's `❌` banner. Cut at three lines and 300
    characters, the 02:43 record ended mid-word inside `[live-hook]`: the direction record stayed
    off origin, its four files held the shared tree's fast-forward, and nothing said which gate.
    `origin_reconcile` lost its refusal to the same cut and fixed it the same way (eaa94ed5f)."""
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if not lines:
        return ""
    if "❌" in text:
        said = [line.strip() for line in text[text.index("❌"):].splitlines() if line.strip()]
    else:
        said = [line for line in lines[1:]
                if child_diagnostics.is_verdict_line(line) and "✓" not in line] or lines[1:3]
    return " | ".join([lines[0], *said])[:limit]


def out_of_scope_writes() -> list[str]:
    """Files the working tree carries that are NOT in the write scope, reported so an orienting
    session that started editing code is visible. NOT reverted: reverting would stamp on whatever
    concurrent lane is legitimately mid-edit, which is the second-writer problem one worse."""
    changed = _git("status", "--porcelain").splitlines()
    scope = set(direction_mod.WRITE_SCOPE)
    out = []
    for line in changed:
        path = line[3:].strip()
        if path and path not in scope:
            out.append(path)
    return out[:40]


def orient(now: datetime | None = None, dry_run: bool = False) -> dict:
    """One orientation. Always returns the row it recorded."""
    now = now or datetime.now(timezone.utc)
    brief = build_brief(now)
    material, why = is_material(brief)
    row = {
        "at": now.isoformat(),
        "since": brief["since"],
        "commits": brief["commit_count"],
        "substantive": brief["substantive_count"],
        "previous_focus_drawn": brief["previous_focus_drawn"],
        "map_levels": map_levels(),
    }
    if material:
        # THE DIRECTOR'S TICK MODE (background/tick_mode.py) can hold or space this route; the
        # skip is recorded exactly like a quiet stretch, with the mode's reason. Unreadable = normal.
        try:
            from background import tick_mode
            ok, _mode, held = tick_mode.gate("delivery-seat")
            if not ok:
                material, why = False, held
        except Exception as e:  # noqa: BLE001 - named in the log, never swallowed
            _log(f"tick mode unreadable ({e!r}) -- running as normal")
    if not material:
        row.update({"outcome": "skipped", "why": why})
        _log(f"skipped: {why}")
        if not dry_run:
            direction_mod.append_decision(row)
            write_stretch_entry(row)
        return row
    if dry_run:
        row.update({"outcome": "would-orient", "why": why})
        return row

    before = direction_mod.read_direction()
    # THE RAW RECORD AND ITS BYTES, read before the session can overwrite them: the carry check
    # needs the open concerns the session was handed, and a refusal restores these bytes so a
    # dropped concern is not lost to the overwrite and then read as "never raised" next stretch.
    try:
        before_bytes = direction_mod.DIRECTION_PATH.read_bytes()
    except OSError:
        before_bytes = None
    before_raw = director_concerns.read_raw()
    try:
        from background import tick_mode
        tick_mode.note_spawn("delivery-seat")
    except Exception:  # noqa: BLE001 - a lost stamp only lets the next spawn come sooner
        pass
    ran, detail = run_session(brief)
    if not ran:
        return record_session_did_not_run(row, why, detail, before)
    after_raw = None
    try:
        import yaml
        after_raw = yaml.safe_load(direction_mod.DIRECTION_PATH.read_text(encoding="utf-8"))
    except Exception:
        after_raw = None
    problems = direction_mod.validate(after_raw) if after_raw is not None else [
        "the session wrote no direction record"]
    dropped = director_concerns.carry_problems(before_raw, after_raw) if after_raw is not None \
        else []
    # THE TRIAGE REFUSALS bind the WRITE and never the read (`direction.wrong_triage_problems`):
    # a retired item listed again, or an untriaged one carried past WRONG_CARRY_TRIAGE_DAYS.
    untriaged = direction_mod.wrong_triage_problems(after_raw) if after_raw is not None else []
    problems = problems + dropped + untriaged

    if problems:
        if (dropped or untriaged) and before_bytes is not None:
            # RESTORED, because the file IS the list: leave the session's overwrite on disk and
            # the next orientation reads a record with the concern already gone, carries nothing,
            # and passes. This file is inside the seat's own write scope. A triage refusal is
            # restored for the reader's sake: `read_direction` does not run the triage check, so
            # a refused record left on disk would steer the draw as if it had been accepted.
            direction_mod.DIRECTION_PATH.write_bytes(before_bytes)
            row["restored_previous_record"] = True
        # FAIL-CLOSED ON THE ARTEFACT, and this is the one place the seat does not fail soft: a
        # malformed direction record is not direction. The PREVIOUS record keeps steering (it is
        # untouched on disk unless the session overwrote it, and if it did the reader's own
        # validation drops it to no-focus), and the refusal is recorded with its reasons.
        row.update({"outcome": "refused", "why": why, "session": detail, "problems": problems,
                    "focus": list(before.focus_keys()) if before else []})
        _log(f"REFUSED the session's direction record: {problems}")
        _notify("delivery seat: the orienting session's direction record was refused -- "
                + "; ".join(problems[:2]), topic_class="blocked_work")
        direction_mod.append_decision(row)
        return row

    parsed = direction_mod.read_direction()
    previous_ids = _previous_concern_ids()   # BEFORE this row is appended and becomes "previous"
    row.update({
        "outcome": "oriented",
        "why": why,
        "session": detail,
        "ran": ran,
        "focus": list(parsed.focus_keys()) if parsed else [],
        "not_now": [r.get("what") for r in (parsed.not_now if parsed else ())],
        # `corrected` TRAVELS WITH THE ERROR, and until 2026-09-03 it did not. The seat was asked
        # to write `corrected: true|false` on every self-audit row, wrote it faithfully into
        # `DIRECTION.yaml` for twenty consecutive records, and then this line threw it away -- so
        # the append-only record, `site/data/delivery.json` and the published panel all carried
        # 212 declared errors with no correction state on any of them, and NOTHING in the tree
        # read the field. A self-audit whose correction half is discarded one hop downstream is a
        # list of complaints, not an audit.
        "wrong": [{"what": r.get("what"), "corrected": bool(r.get("corrected"))}
                  for r in (parsed.wrong if parsed else ())],
        # THE WHOLE ROW, NOT ITS `what` (2026-10-04): the id is what the next orientation pages
        # against, and the status and resolution are the half of a concern the director reads.
        "for_the_director": [
            {k: r.get(k) for k in ("id", "kind", "what", "proposal", "status", "resolution")}
            for r in (parsed.for_the_director if parsed else ())],
        "thesis_read": parsed.thesis_read if parsed else "",
        "out_of_scope_writes": out_of_scope_writes(),
        # THE RECORD IT JUST WROTE, GRADED BEFORE IT IS COMMITTED, and this is the leg the brief
        # cannot cover. The brief grades the PREVIOUS record -- the items about to be carried
        # forward -- and says nothing about an item the session invented this stretch. Both legs
        # are the same classifier over the same tree; what differs is which record exists at the
        # moment it is asked. RECORDED AND NOT REFUSED: `commit_direction` runs either way, for
        # `path_note`'s reason (an item naming a spent path is often still the right work), and
        # the row lands in `decisions.jsonl` where `last_orientation` hands it back next stretch.
        "path_concerns": direction_path_check.concerns((parsed.raw if parsed else None)),
    })
    direction_mod.append_decision(row)
    write_stretch_entry(row)
    try:
        from tools.generate_delivery_page import generate
        generate()
    except Exception as exc:  # the page is downstream of the record, never a reason to lose it
        _log(f"delivery page not regenerated: {exc!r}")
    ok, commit_detail = commit_direction()
    row["committed"] = ok
    _log(f"oriented: focus={row['focus']} ({commit_detail})")
    if not ok:
        record_landing_refused(row, commit_detail)
    for concern in row["path_concerns"]:
        # LOGGED ONE PER LINE AND NOT COUNTED. A count tells the next reader a number; the class
        # and the id tell them which item to go and look at, which is the whole point of asking
        # the door before the record is filed rather than after it is drawn.
        _log("path check [{}] {}: {}".format(concern["class"], concern["id"], concern["says"]))
    # PAGED ONCE PER CONCERN, NOT ONCE PER STRETCH. Until 2026-10-04 this paged on every record
    # whose list was non-empty, so a row carried forward -- which the carry check now REQUIRES --
    # would have re-paged him every three hours until he answered.
    fresh = director_concerns.new_open_ids(previous_ids, parsed.raw if parsed else None)
    if fresh:
        by_id = {r["id"]: r for r in row["for_the_director"]}
        _notify("delivery seat: a concern for you, with a proposal -- " + "; ".join(
            "[{}] {} -- proposal: {}".format(i, by_id[i]["what"], by_id[i]["proposal"])
            for i in fresh[:2]), topic_class="decision_waiting")
    row["concerns_paged"] = fresh
    return row


def record_session_did_not_run(row: dict, why: str, detail: str, before) -> dict:
    """The session never oriented: record it REFUSED, page, and land NOTHING.

    11:24Z 2026-10-07: the spawn died before the session started, and `orient` carried on as if
    it had run. The record it then validated was the shared working copy's, untouched, so the row
    read `oriented` and `commit_direction` landed that stale copy over origin (a42daa6a0),
    reverting 1cd4bda0e's triage. Whatever is on disk after a failed session is not this stretch's
    direction, so nothing is committed; the row stays in the working copy's `decisions.jsonl` and
    lands with the next orientation's record."""
    reason = f"the orienting session did not run: {detail}"
    row.update({"outcome": "refused", "why": why, "session": detail, "ran": False,
                "committed": False, "problems": [reason],
                "focus": list(before.focus_keys()) if before else []})
    _log(f"REFUSED: {reason}")
    _notify("delivery seat: " + reason[:300] + " -- origin's steer is the previous stretch's",
            topic_class="blocked_work")
    direction_mod.append_decision(row)
    return row


def record_landing_refused(row: dict, detail: str) -> dict:
    """The record did not reach origin: say so in the record and to the director.

    9 RECURRENCES, AND THE LAST ONE WAS SILENT (2026-10-07). The row was appended as `oriented`
    before the landing -- it has to be, it is part of what lands -- and a refused landing left it
    reading `oriented`, so the decisions record and the director's view of origin disagreed for
    three hours with nothing saying why. APPENDED, NOT REWRITTEN: the file is append-only, so the
    last word is a second row carrying the same orientation with `outcome: refused`. It keeps the
    orientation's `at`, so the next stretch is still counted from the orientation."""
    refused = dict(row, outcome="refused", landing_refused=detail, committed=False)
    direction_mod.append_decision(refused)
    _notify("delivery seat: the direction record did NOT reach origin, so origin's steer is the "
            "previous stretch's -- " + detail[:300], topic_class="blocked_work")
    return refused


def _notify(message: str, *, topic_class: str) -> None:
    """Through `background.notify.notify`, never `send_ntfy` directly -- the notify contract, and
    a test enumerates new direct callers. The seat pages RARELY: only when its own record was
    refused, or when something is genuinely the director's.

    IT PAGED TWICE IN A MONTH AND NEITHER PAGE WAS SENT. Until 2026-09-03 this passed no `kind`,
    which `notify()` has required since G-N2 ("an untyped page is forbidden"), so every call
    raised TypeError -- into an `except Exception` that logged and returned. `docs/observability/
    delivery-seat-log.md` carries both: 2026-08-28 08:31:31Z, P9 book depth priced and returned
    as a curriculum question; and 2026-08-30 23:30:30Z, which route the world takes past 2025 AND
    "whether YEAR_LEVEL_ANCHOR should aim at the published band's MIDPOINT instead of its high
    endpoint". Both are the reserved class -- a director's decision, not a seat's -- and both went
    to a log file nobody reads instead of to him. The second one names the exact defect the level
    fit was still carrying four days later.

    So the `except` stays (a page that cannot be sent must not take its message with it) and the
    reason it was firing is gone. `topic_class` is REQUIRED rather than defaulted: this function's
    two callers mean different things to him -- a refused record is blocked work, a decision that
    is genuinely his is a decision waiting -- and a default here would pick one of them silently.
    """
    try:
        from background.notify import notify
        notify(message, kind="real_alarm", topic_class=topic_class)
    except Exception as exc:
        _log(f"notify failed ({exc!r}), message was: {message}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="assemble the brief and report whether it would orient, spawning "
                             "nothing and recording nothing")
    parser.add_argument("--brief", action="store_true", help="print the brief and exit")
    args = parser.parse_args(argv)
    if args.brief:
        print(json.dumps(build_brief(), indent=1))
        return 0
    row = orient(dry_run=args.dry_run)
    print(json.dumps({k: v for k, v in row.items() if k != "map_levels"}, indent=1))
    return 0


if __name__ == "__main__":
    # SEAT GUARD, FIRST ACT. Orienting on a foreign checkout would read someone else's git log,
    # someone else's staging root, and write direction into a tree that is not the seat's.
    from background._seat import refuse_if_foreign

    refuse_if_foreign("delivery_seat")
    sys.exit(main())
