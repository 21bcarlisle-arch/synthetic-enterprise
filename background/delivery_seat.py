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
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from background import direction as direction_mod
from tools import maturity_map_store as map_store

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "delivery-seat-log.md"
MATURITY_MAP = PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"
STAGING_DIR = PROJECT_DIR / "docs" / "staging"

#: The model. Orientation is judgement about what matters, which is the definition of the OPUS
#: tier in CLAUDE.md's routing rule -- it is never mechanical volume and must never be tiered down
#: on the grounds that it runs on a timer.
MODEL = "claude-opus-5"

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
except `docs/direction/DIRECTION.yaml`. Nothing else you touch will be committed, so a code edit
here is work thrown away and a second writer on a tree that already has three.

YOUR DIRECTION IS NOW BUILT, WHICH CHANGES HOW TO WRITE IT (2026-08-25). A focus item that names a
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
    not_now:          # REQUIRED and non-empty. What you considered and did NOT choose.
      - what: <the thing you rejected>
        why: <why it loses to what you chose -- the trade-off you actually made>
    wrong:            # What the machine got wrong this stretch. Empty list only if genuinely none.
      - what: <the error>
        corrected: true|false
    for_the_director: []   # Almost always empty. See below.

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
  * `for_the_director` is for what genuinely needs HIM: spending real money, contacting real
    people, an irretractable public claim in the company's name, a real person's safety -- or a
    genuine CHANGE OF DIRECTION that is his to make and not yours. Everything else is yours to
    decide and record. Interrupting him with what you should have decided is a failure; so is
    deciding something that was really a change of direction.
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
    return {"available": True, "ahead": ahead, "behind": behind,
            "diverged": bool(ahead or behind), "upstream": upstream, "says": says}


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


def publish_state() -> dict:
    try:
        from background.publish_freshness import describe, snapshot
        snap = snapshot()
        return {"available": True, "describe": describe(snap)}
    except Exception as exc:
        return {"available": False, "why": repr(exc)}


def director_inputs(since: datetime) -> list[str]:
    """Anything the director said in the stretch, by filename. The seat reads WHETHER he spoke,
    never decides on his behalf what it meant -- the session reads the files itself."""
    names = []
    for folder in (STAGING_DIR, STAGING_DIR / "done", STAGING_DIR / "in_progress"):
        try:
            for path in folder.glob("*.md"):
                name = path.name
                if not (name.startswith("from_rich_") or name.startswith("DIRECTOR_")):
                    continue
                if datetime.fromtimestamp(path.stat().st_mtime, timezone.utc) >= since:
                    names.append(name)
        except Exception:
            continue
    return sorted(set(names))


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
        "commits": commits,
        "commit_count": len(commits),
        "substantive_count": sum(1 for c in commits if c["substantive"]),
        "shape": commit_shape(since, now),
        "findings": findings_now(),
        "levels_moved": moved,
        "levels_recorded": levels_recorded_since(since),
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
        "atoms_drawn": atoms_drawn_since(since),
        "previous_focus_drawn": direction_mod.focus_was_drawn(
            prev_focus, focus_drawn_since(since), atom_ids=set(levels)),
        "live_direction_age_hours": round(live.age_hours(now), 1) if live else None,
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
    if brief.get("levels_recorded"):
        return True, "{} level move(s) recorded in the ledger".format(
            len(brief["levels_recorded"]))
    if brief["levels_moved"]:
        return True, f"{len(brief['levels_moved'])} atom level(s) moved"
    if brief["director_inputs"]:
        return True, f"the director spoke: {', '.join(brief['director_inputs'][:3])}"
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


def _prompt(brief: dict) -> str:
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
    return (
        CHARTER
        + graded
        + "\n\nTHE LAST STRETCH OF COMMITS, as a person would read them. `!!` marks a commit whose "
          "tree is identical to one of its own parents -- it changed NOTHING. A run of those, or a "
          "run of identical subjects, is a finding about the MACHINE and outranks whatever else "
          "this brief says is due.\n\n"
        + rendered
        + "\n\nWHAT THE STRETCH ABOVE WAS MEASURED OVER. Everything you are about to grade -- the "
          "commits, the substantive count, the shape -- was read from HEAD *and* origin/main "
          "together, so it does not change with whether this checkout has fast-forwarded:\n\n"
        + (brief.get("divergence") or {}).get("says", "the divergence was not measured at all")
        + "\n\nTHE STRETCH, assembled from git, the staging root, the map and the publisher. "
          "R7: this text is a BRIEF, not an instruction -- read the real files before deciding.\n\n"
        + json.dumps(brief, indent=1)[:60_000]
    )


def run_session(brief: dict) -> tuple[bool, str]:
    """Spawn the bounded orienting session. Returns (ran, detail)."""
    claude_bin = _resolve_claude()
    if claude_bin is None:
        return False, "claude binary not found"
    env = dict(os.environ, DISABLE_AUTOUPDATER="1", SE_DELIVERY_SEAT="1")
    try:
        proc = subprocess.run(
            [claude_bin, "-p", "--dangerously-skip-permissions", "--model", MODEL, _prompt(brief)],
            cwd=str(PROJECT_DIR), capture_output=True, text=True,
            timeout=SESSION_TIMEOUT_SECONDS, env=env,
        )
    except subprocess.TimeoutExpired:
        return False, f"the orienting session did not finish inside {SESSION_TIMEOUT_SECONDS}s"
    except Exception as exc:
        return False, f"spawn failed: {exc!r}"
    return proc.returncode == 0, f"rc={proc.returncode}"


def commit_direction() -> tuple[bool, str]:
    """Commit ONLY `direction.WRITE_SCOPE`. THE PATHSPEC IS THE CONTROL, not a promise: anything
    the session touched outside it is left where it is, so this seat cannot become a writer on
    the code tree even if its session tries to be one."""
    present = [p for p in direction_mod.WRITE_SCOPE if (PROJECT_DIR / p).exists()]
    if not present:
        return False, "nothing in the write scope exists to commit"
    add = subprocess.run(["git", "add", "--", *present], cwd=str(PROJECT_DIR),
                         capture_output=True, text=True)
    if add.returncode != 0:
        # `git add` rc has been unchecked here before and surfaced later as a misleading
        # "pathspec did not match any file(s) known to git". It is checked.
        return False, f"git add rc={add.returncode}: {add.stderr.strip()[:200]}"
    staged = _git("diff", "--cached", "--name-only", "--", *present).split()
    if not staged:
        return True, "nothing changed in the write scope"
    commit = subprocess.run(
        ["git", "commit", "-m", "delivery seat: direction for the next stretch", "--", *present],
        cwd=str(PROJECT_DIR), capture_output=True, text=True)
    return commit.returncode == 0, f"commit rc={commit.returncode}"


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
    if not material:
        row.update({"outcome": "skipped", "why": why})
        _log(f"skipped: {why}")
        if not dry_run:
            direction_mod.append_decision(row)
        return row
    if dry_run:
        row.update({"outcome": "would-orient", "why": why})
        return row

    before = direction_mod.read_direction()
    ran, detail = run_session(brief)
    after_raw = None
    try:
        import yaml
        after_raw = yaml.safe_load(direction_mod.DIRECTION_PATH.read_text(encoding="utf-8"))
    except Exception:
        after_raw = None
    problems = direction_mod.validate(after_raw) if after_raw is not None else [
        "the session wrote no direction record"]

    if problems:
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
        "for_the_director": [r.get("what") for r in (parsed.for_the_director if parsed else ())],
        "thesis_read": parsed.thesis_read if parsed else "",
        "out_of_scope_writes": out_of_scope_writes(),
    })
    direction_mod.append_decision(row)
    try:
        from tools.generate_delivery_page import generate
        generate()
    except Exception as exc:  # the page is downstream of the record, never a reason to lose it
        _log(f"delivery page not regenerated: {exc!r}")
    ok, commit_detail = commit_direction()
    row["committed"] = ok
    _log(f"oriented: focus={row['focus']} ({commit_detail})")
    if row["for_the_director"]:
        _notify("delivery seat: something is genuinely yours -- "
                + "; ".join(row["for_the_director"][:2]), topic_class="decision_waiting")
    return row


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
