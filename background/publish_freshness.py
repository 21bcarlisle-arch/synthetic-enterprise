"""HOW LONG SINCE THE FIGURES MOVED — the one number that tells a frozen site from a live one.

DIRECTOR, 2026-08-13: *"content hasn't moved in ~17 hours while heartbeats keep landing — the
liveness signal is masking a content freeze ... alive-but-unchanged and alive-and-publishing must
not look the same to me or to the site."*

THE DEFECT THIS NAMES
---------------------
`site/data/tick_heartbeat.json` answers "is the tick running?" and answered it correctly for
eighteen hours: `verdict: drew` every sixty seconds, published to origin every thirty minutes by
`_refresh_published_liveness_on_skip`. Every daemon was healthy. Nothing was red. And the site
served 2026-08-12 figures the whole time, because every content commit was dying on the
pre-commit hook deadline.

Fault #1 (2026-07-25) correctly DECOUPLED the liveness signal from content-change, so a healthy
machine with unchanged output could still prove it was alive. What it did not do -- and what this
module adds -- is give that signal anything to say about CONTENT. A heartbeat that reports only
its own pulse is not a false statement; it is a true statement about the wrong subject, and a
true statement about the wrong subject is how eighteen hours pass unnoticed.

So the liveness surface now carries the statement of how stale everything else is. That is the
same shape as `publish_provenance.py` -- "publishes the one thing that must never freeze: the
statement of how frozen everything else is" -- applied to the surface that never stopped
publishing rather than to the one that did.

TWO CLOCKS, AND THEY ARE ALLOWED TO DISAGREE
--------------------------------------------
  published_age_seconds  since the PUBLISH PATH last got content to origin. Two sources, newer
                         wins (see `last_published_ts`): `record_published()`'s stamp, written
                         from exactly one place after `_push_reached_origin` returned True on a
                         content commit; and git's own answer for when CONTENT_PATHS last moved in
                         a commit origin HAS. Both are ground-truth-gated -- a phantom "up to date"
                         advances neither -- and the second exists because the first is silent
                         whenever the publisher mis-grades its own push (2026-09-16).
  committed_age_seconds  since content was last COMMITTED at all, asked of git rather than of our
                         own bookkeeping -- by ANY writer, not only the publisher.

They are deliberately not one field. Equal-and-small is healthy. Equal-and-large is a real
content freeze. `committed` small while `published` large is the case measured on 2026-08-13:
the publish path had not landed for 21.7 hours, and `site/data/dashboard.json` still reached
origin twice in that window -- once at 02:12 and once at 18:55 -- because an unrelated worker
commit happened to sweep the regenerated file along with it. Content moving by luck is not a
publishing pipeline, and a single blended number would have read those two accidents as health.

AND A QUEUE, WHICH IS NOT A CLOCK AT ALL
----------------------------------------
Both ages are about RECENCY. Neither is about THROUGHPUT, and on 2026-09-02/03 that gap ran for
nine hours: 62 run markers produced, 27 consumed, and this module said `live` throughout because
the publish path WAS landing -- just not the backlog behind it. `queue_depth` and
`queue_oldest_age_seconds` are that third subject. They are OBSERVATIONS carried on the line and
deliberately NOT folded into `state`: the queue is a stack rather than a FIFO, so a burst is
cleared by retiring superseded markers, and the property worth paging on (no PROGRESS on the
oldest across cycles) already belongs to `background_worker._check_zero_progress`. Reporting the
numbers costs nothing and duplicates no verdict; a second threshold over the same subject would
have alarmed on the drain working correctly.

FAIL-SILENT IS THE FAILURE MODE HERE (R15), so an unavailable answer is None and NEVER 0. A
freshness module that reports "0 seconds since publish" when it cannot find its own state file
would manufacture exactly the false all-clear it exists to end. Every caller must treat None as
UNKNOWN and never as fresh -- `is_publishing_down` does, by returning False only on a positive
measurement and escalating an unknown to its own named state.

REUSE: background/publish_freshness.py
CLASS: CUSTOM
INDEX: searched "freshness", "staleness", "publish age". `publish_provenance.py` is the closest
       and is a different subject: it records whether the newest run was VERIFIED (gate green)
       and what the visitor is being shown, and it is written BEFORE the commit so it travels
       with it. It therefore said "Verified 2026-08-13T16:34:33Z" over content from the previous
       day -- correctly, by its own contract, because the gate WAS green; the commit is what
       died. This module asks the question that stayed unasked: did the bytes reach origin.
"""
from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from background import publish_cause
from background.episode_monotonic import recorded_instant_seconds
from background.live_ledger_guard import guard_live_ledger_write

PROJECT_DIR = Path(__file__).resolve().parent.parent
STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".last_content_publish.json"

#: Where the publisher's input queue lives. Completed sim runs land here as `run_complete_*.md`
#: and leave when `background_worker.process_leftover_run_markers` either publishes or retires
#: them, so the count is the depth of the queue BEHIND the publisher.
STAGING_DIR = PROJECT_DIR / "docs" / "staging"

#: THE PUBLISHER'S OWN RECORD OF REFUSING TO PUBLISH, written by `process_run_complete` at the
#: moment each publish attempt dies. Read here, never written here.
PUBLISH_GATE_STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".publish_gate_state.json"

#: The paths whose movement IS a content publish. Deliberately a short list of the surfaces a
#: visitor actually reads, not the full commit pathspec: adding every generated file would make
#: the age advance on any regeneration, and the question is whether the FIGURES moved.
CONTENT_PATHS = (
    "site/data/dashboard.json",
    "docs/status/LATEST.md",
    "docs/reports/ANNUAL_REPORT.md",
)

#: THE DECLARED PUBLISHING CADENCE. Director, 2026-09-04: *"The site publishes numbers and runs
#: once a week, thoroughly and robustly, not every half hour ... The reason is cost. Three of the
#: last five days had multi-hour publish outages, and fixing them has taken more of your time than
#: the content ever has ... Nearly all of it exists to sustain a cadence nobody reads at."*
#:
#: This is the SINGLE SOURCE OF TRUTH for that cadence: the producer's period and the staleness
#: verdict both derive from it, so changing the cadence moves the alarm with it rather than leaving
#: an alarm calibrated for the old one. An alarm keyed to a cadence it no longer describes is the
#: shape that had a correct control refusing correct work all week.
#:
#: AND THE CLAIM WAS FALSE FOR SEVENTEEN DAYS, WHICH IS WHY IT NOW NAMES WHAT IT EXCLUDES
#: ──────────────────────────────────────────────────────────────────────────────────────
#: Corrected 2026-09-21, beside the claim rather than over it. "Single source of truth" was
#: written here on 2026-09-04 and was not true when written: `suite_duration_watch` held a
#: second constant of the same name, 5,400s — 112x smaller — and stamped it into
#: `publish_gate_duration.jsonl` under the same field name this module's `snapshot()` uses,
#: `cadence_seconds`. A module asserting it is the only home for a quantity is not a mechanism;
#: it is a sentence, and a sentence cannot notice a rival. This is the VAT-rule class.
#:
#: THE RIVAL WAS NEVER THIS QUANTITY, and that is the resolution rather than a tie-break. The
#: two numbers are a DECISION and an OBSERVATION of different subjects:
#:
#:   HERE — how often the site PUBLISHES. A choice, the director's, moved only by him.
#:   THERE — how often sim RUNS ARRIVE. A measurement, moved by the book getting bigger. It is
#:     now called `suite_duration_watch.MEASURED_RUN_ARRIVAL_SECONDS` and writes
#:     `measured_arrival_seconds`, so neither the symbol nor the field can be picked up in
#:     mistake for this one. Nothing there was wrong except its name.
#:
#: WHY IT MATTERED, because a naming defect that costs nothing is worth leaving alone. It did
#: not: `settlement_ceiling_probe` read the arrival measurement as the publish interval and
#: priced `SETTLEMENT_CUSTOMER_YEAR_BUDGET` against it. Run duration SETS marker inter-arrival,
#: so that bound grows whenever the ceiling it bounds grows — the exact circularity the ceiling's
#: own note records as removed, re-entered through a second door nobody re-asked. Against 5,400s
#: the binding leg is TIME; against this constant it is MEMORY. The two answers differ in kind.
#:
#: THE CONTROL that makes this sentence checkable rather than merely written is
#: `tests/architecture/test_the_publish_cadence_has_one_home.py`. It reds if a second
#: `PUBLISH_CADENCE_SECONDS` is ever defined anywhere in the tree.
PUBLISH_CADENCE_SECONDS = 7 * 24 * 60 * 60

#: DERIVED, not picked: one full cadence plus one day of retry opportunity. The worker sweeps every
#: 30 minutes, so a day is 48 attempts; if none of 48 landed, the publisher is down rather than
#: unlucky. Keeping the grace explicit is what stops the next reader "just bumping" the threshold.
PUBLISH_GRACE_SECONDS = 24 * 60 * 60

#: How stale the published CONTENT may get before it is a fault rather than the cadence working.
#:
#: WAS 3 HOURS, AND THAT WAS RIGHT FOR THE OLD CADENCE AND IS WRONG FOR THIS ONE. At a weekly
#: cadence a three-hour threshold means the banner reads "PUBLISHING IS DOWN" for six days out of
#: seven while the machine does exactly what it was told. An alarm that is correct once a week and
#: wrong the rest of the time is not a signal; it is the thing readers learn to ignore.
STALE_AFTER_SECONDS = PUBLISH_CADENCE_SECONDS + PUBLISH_GRACE_SECONDS

#: A SECOND CLOCK FOR A SECOND QUESTION, and separating them is the point. "Is the weekly publish
#: overdue?" is answered on the cadence above. "Is content being committed locally and never
#: reaching origin?" is a different fault with a different fix (the push, not the schedule) and it
#: is just as urgent at a weekly cadence as it was at a half-hourly one. It keeps the old horizon,
#: because nothing about the publishing cadence makes a stuck push less broken.
PUSH_LAG_AFTER_SECONDS = 3 * 60 * 60


def record_published(now: float | None = None) -> None:
    """Stamp a VERIFIED content publish. The only writer.

    Reachable from exactly one call site -- `git_commit_push`, immediately after
    `_push_reached_origin` confirmed via ls-remote that origin advanced to this HEAD. Never call
    it from a path that has not checked that: a stamp written on an unverified push would make
    this module agree with the very bookkeeping it exists to be independent of.
    """
    ts = time.time() if now is None else float(now)
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        guard_live_ledger_write(STATE_FILE, writer="publish_freshness.record_published").write_text(json.dumps({"ts": ts}))
    except OSError:
        pass  # never take a successful publish down over its own bookkeeping


def _stamped_publish_ts() -> float | None:
    """Our OWN record of a verified publish, or None if never recorded / unreadable (= UNKNOWN)."""
    try:
        return float(json.loads(STATE_FILE.read_text())["ts"])
    except (OSError, ValueError, KeyError, TypeError):
        return None


def content_on_origin_ts(*, _run=None) -> float | None:
    """When CONTENT_PATHS last moved in a commit ORIGIN HAS — asked of git, by reachability.

    THE SECOND READER OF A FALSE STATE (2026-09-16). This module's clock was a stamp written by
    `process_run_complete._record_content_published`, which fires only when the publisher's own
    push verdict returns True. That verdict was `remote_head == local_head`, which a publish
    created while BEHIND origin can never satisfy -- so on 2026-09-16 `describe()` told the
    delivery brief *"figures reached origin 159.8h ago"* three hours after `05add41ab` put
    `LATEST.md`, the annual report and every customer file on origin. Repairing the publisher's
    predicate alone would have left this sentence wrong until the NEXT publish; the honest fix is
    for this module to ask the same question the publisher now asks, of the same subject.

    `refs/remotes/origin/main` rather than the stamp, and the failure direction is the safe one:
    the tracking ref can only be BEHIND the remote (it moves on fetch and on push), so this can
    report the figures as older than they are and never as newer. That is the same direction
    `snapshot` already chose when it took the older of its two clocks.
    """
    run = _run or subprocess.run
    try:
        r = run(["git", "log", "-1", "--format=%ct", "refs/remotes/origin/main", "--"]
                + list(CONTENT_PATHS),
                cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=15)
    except Exception:  # noqa: BLE001 -- an unavailable check is UNKNOWN, never fresh
        return None
    if getattr(r, "returncode", 1) != 0:
        return None
    out = (r.stdout or "").strip().splitlines()
    try:
        return float(out[0]) if out else None
    except ValueError:
        return None


def last_published_ts(*, _run=None) -> float | None:
    """When content last reached origin, or None if neither source can say (= UNKNOWN).

    TWO SOURCES FOR ONE QUESTION, and the NEWER wins. Each can only MISS a publish, never invent
    one: the stamp is missed when the publisher mis-grades its own push (the defect above), and
    git's answer is missed when the tracking ref is behind the remote. Taking the newer therefore
    lets either one say "it reached", and neither can veto the other.

    The stamp's own known weakness -- it is written on a verified push whatever paths moved, so a
    provenance banner used to refresh it (2026-08-21) -- is NOT reintroduced by this, because
    `snapshot`'s verdict takes the OLDER of this clock and the content clock. A fresh stamp over
    frozen figures still reads `stale`; that is the control that closed the 28-hour outage and it
    is untouched here.

    `_run` is injected for tests only, and the production caller passes nothing on purpose: this
    is monkeypatched as a bare `lambda:` in the controls that pin one clock against the other.
    """
    on_origin = content_on_origin_ts(_run=_run)
    stamped = _stamped_publish_ts()
    if on_origin is None:
        return stamped
    if stamped is None:
        return on_origin
    return max(on_origin, stamped)


def last_committed_ts(*, _run=None) -> float | None:
    """When content was last COMMITTED locally, asked of git. None if git cannot answer.

    Independent of this module's own state file on purpose -- it is the cross-check that catches
    a publish committing locally and never reaching origin, which is a different fault with a
    different fix and used to be invisible from the outside.
    """
    run = _run or subprocess.run
    try:
        r = run(["git", "log", "-1", "--format=%ct", "--"] + list(CONTENT_PATHS),
                cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=15)
    except Exception:  # noqa: BLE001 -- an unavailable check is UNKNOWN, never fresh
        return None
    if getattr(r, "returncode", 1) != 0:
        return None
    out = (r.stdout or "").strip().splitlines()
    try:
        return float(out[0]) if out else None
    except ValueError:
        return None


def queue_depth() -> int | None:
    """How many completed runs are queued BEHIND the publisher. None if uncountable (= UNKNOWN).

    THE THIRD NUMBER, and the one neither clock can carry. Both ages answer "how long since
    something moved"; neither answers "is the pipeline keeping up with its input". On
    2026-09-02/03 those questions had different answers for nine hours: the runner produced 62
    markers, the processor consumed 27, and `describe()` said `live -- figures reached origin
    0.7h ago` throughout. That line was TRUE. It was true about the wrong subject, which is the
    same failure this module's own docstring was written to end, reached from the other side.

    Reported as an OBSERVATION and deliberately NOT folded into `state`. Depth alone is not a
    fault: the queue is a stack, not a FIFO (every marker describes the same world after a run,
    so the newest strictly dominates), and `background_worker.process_leftover_run_markers`
    clears a deep queue by RETIRING the superseded ones -- 17/17 at 2026-09-03 01:56Z. A
    threshold here would therefore alarm on a burst that the drain handles by design, and the
    property that actually matters -- no PROGRESS on the oldest marker across cycles -- already
    has a control that pages, `background_worker._check_zero_progress`. A second verdict over the
    same subject would be a control guarding a control, and turning a previously-unread field
    into a decision is what reddened five tests on 2026-09-02. So this reports the number and
    lets the existing alarm keep the verdict.

    None and never 0 when the directory cannot be read: a queue we failed to count must not read
    as a queue that is empty.
    """
    try:
        return sum(1 for _ in STAGING_DIR.glob("run_complete_*.md"))
    except OSError:
        return None


def queue_oldest_age_seconds(now: float | None = None) -> float | None:
    """How long the OLDEST queued run has waited. None if the queue is empty or uncountable.

    The count alone cannot tell a burst from a stall: 35 markers minted in the last ten minutes
    is a busy runner, and 3 markers whose oldest has waited nine hours is a pipeline that is not
    reaching its input. On 2026-09-02/03 it was the second -- oldest `20260902T160532Z`, measured
    at 01:07Z.

    THE STAMP IS READ FROM THE NAME, NEVER FROM THE MTIME. `sim_runner` names markers in UTC and
    this box runs local BST, so differencing a filename against an mtime manufactures an hour of
    phantom wait -- and the retirement path REWRITES mtimes, which would reset the age of a marker
    that has not moved. The name is the only clock that describes when the RUN finished.

    An unparseable name contributes no age rather than an age of zero: this must never report a
    fresh queue because it failed to read one.
    """
    now = time.time() if now is None else float(now)
    try:
        names = [p.name for p in STAGING_DIR.glob("run_complete_*.md")]
    except OSError:
        return None
    ages = []
    for name in names:
        stamp = Path(name).stem[len("run_complete_"):]
        try:
            ts = datetime.strptime(stamp, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc).timestamp()
        except ValueError:
            continue
        ages.append(max(0.0, now - ts))
    return max(ages) if ages else None


def publisher_refusal(now: float | None = None, *, path: Path | None = None) -> dict:
    """DID THE PUBLISHER TRY AND FAIL — a different question from "are the figures old".

    THE GAP THIS CLOSES (2026-09-24). Both clocks above are AGES, and an age can only become a
    fault when its threshold comes due. At a weekly cadence that threshold is eight days
    (`STALE_AFTER_SECONDS`), which is correct for the question it answers and useless for this
    one: on 2026-09-24 the publisher had failed 45 consecutive attempts across 59 hours, with a
    run queued behind it, and `state` read `publishing` — truthfully, because eight days had not
    passed. The surface therefore rendered its ordinary healthy branch, and the "PUBLISHING IS
    DOWN" wording could not fire for another five days however many attempts died in between.

    "Not due yet" and "tried and failed" are different facts and only one of them was on the
    page. This is the second one, and it is available immediately rather than on a timer: the
    publisher records every refusal in `.publish_gate_state.json` as it happens.

    IT IS A SELF-REPORT, SO IT IS TRUSTED IN EXACTLY ONE DIRECTION. `process_run_complete` writes
    this file about its own failures, which makes a FAILING reading an admission against interest
    and a clean reading no evidence at all -- a publisher wedged before it can write, or a state
    file that was lost, both read as clean. So:

      failing           an episode of consecutive failures is open and no clean publish has
                        closed it. Believed, and said out loud on the surface.
      no_open_episode   the record exists and names no open episode. NOT a statement that
                        publishing is healthy -- the two content clocks are what establish that,
                        and they cannot be faked by an absent file.
      unknown           absent, unreadable, malformed, or the failure count is not a count.
                        FAIL-SILENT is the failure mode here (R15), so this is never folded into
                        `no_open_episode`.

    AND IT DOES NOT MOVE `state`, deliberately. `state` is the CONTENT clock's verdict, it is
    what `is_publishing_down()` and the deadman's page read, and `deadmans_switch
    ._check_content_publishing` states the reason in its own docstring: "a publisher that pages
    about its own health is the tautology R15 names". Folding a self-report into the verdict that
    pages would put the wedged component in charge of reporting its own wedge. The surface is a
    different consumer with a different need -- a reader looking at a figure wants to know that
    the last 45 attempts to replace it failed, whoever said so -- so this rides beside the verdict
    with its own name, and the alarm keeps its independent clock.

    EPISODE_FAILURES IS THE SUBJECT, NOT `failures`. The `failures` list is trimmed to a one-hour
    window (see `supervisor._publish_gate_wedge_active`), so a two-day outage whose last attempt
    was 70 minutes ago has an EMPTY list and an episode count of 45. Reading the list here would
    have gone quiet on exactly the long outages this exists for.
    """
    now = time.time() if now is None else float(now)
    p = PUBLISH_GATE_STATE_FILE if path is None else path
    unknown = {"state": "unknown", "consecutive_failures": None, "failing_for_seconds": None,
               "clean_publishes_this_episode": None, "cited_red_at_head": None,
               "held_refusal": None,
               "held_refusal_reason": ("the publisher's state could not be read, so no refusal "
                                       "record was inspected")}
    try:
        state = json.loads(Path(p).read_text())
    except (OSError, ValueError):
        return unknown
    if not isinstance(state, dict):
        return unknown
    failures = state.get("episode_failures")
    # `bool` is an `int` and `True` is not a count of anything. Same screen as everywhere else
    # that reads this file: a value that cannot be a count makes the answer UNKNOWN, never zero.
    if isinstance(failures, bool) or not isinstance(failures, int) or failures < 0:
        return unknown
    clean = state.get("episode_clean_publishes")
    clean = clean if isinstance(clean, int) and not isinstance(clean, bool) else None
    # The episode START is screened by the shared door rather than by a hand-rolled `> 0`: this
    # field is legitimately written as an epoch OR as ISO-8601, and a hand-roll drops the second
    # silently (`episode_monotonic.recorded_instant_seconds` carries both arguments).
    started = recorded_instant_seconds(state.get("wedge_since"))
    # THE CAUSE THIS RECORD IS ALREADY HOLDING, read from the file's OTHER fields rather than
    # inferred from the citation verdict above. See `publish_cause.held_refusal`: on 2026-09-24
    # `citation_at_head` was `not_established` with `total_red: 0` while `liveness_surface_refusal`
    # in the same file held an attributed, stamped `push_never_landed` with its evidence intact.
    # Carried BESIDE the citation and never folded into it -- they are answers to two different
    # questions (does the cited red still reproduce / is any cause on record at all), and a
    # reader is owed both.
    held, held_reason = publish_cause.held_refusal(state, now=now)
    # A MISSING START DOES NOT VETO THE FAILURE, and getting this backwards would be the fail-open
    # shape: the count is what establishes that attempts died, the stamp only says since when.
    return {
        "state": "failing" if failures >= 1 else "no_open_episode",
        "consecutive_failures": failures,
        "failing_for_seconds": None if started is None else round(max(0.0, now - started), 1),
        "clean_publishes_this_episode": clean,
        # Whether the red the publisher blames still reproduces at HEAD -- `reproduces`, `dead`,
        # `not_established`. A failing publisher citing a DEAD red is failing for a reason nobody
        # has named, which a reader of the front door should be told rather than left to assume
        # there is a known cause behind the outage.
        "cited_red_at_head": (
            str(state["citation_at_head"])[:40] if isinstance(state.get("citation_at_head"), str)
            else None),
        # The record, or None; and ALWAYS a sentence saying which refusal fields were held and
        # why they were not enough. A consumer that finds `held_refusal` None is never left to
        # guess whether anything was looked at.
        "held_refusal": held,
        "held_refusal_reason": held_reason,
    }


def _age(ts: float | None, now: float) -> float | None:
    return None if ts is None else max(0.0, now - ts)


def snapshot(now: float | None = None, *, _run=None) -> dict:
    """The publish-freshness block the heartbeat carries and the site renders.

    `state` is the reader's whole answer, so no consumer has to re-derive the comparison and
    two consumers cannot reach different verdicts from the same numbers:
        publishing   content reached origin within STALE_AFTER_SECONDS
        stale        it did not -- the freeze this exists to surface
        unpublished  no verified publish has EVER been recorded (a fresh install, or a state
                     file that was lost) -- reported as its own state rather than folded into
                     `stale`, because "we have no record" and "we have a record and it is old"
                     are answered differently
        unknown      the age could not be measured at all -- explicitly NOT `publishing`
    """
    now = time.time() if now is None else float(now)
    pub_ts, com_ts = last_published_ts(), last_committed_ts(_run=_run)
    pub_age, com_age = _age(pub_ts, now), _age(com_ts, now)

    # THE VERDICT IS THE OLDER OF THE TWO CLOCKS, and reading only `pub_age` cost 28 hours of
    # silence on 2026-08-21.
    #
    # `pub_age` comes from the state file, which `process_run_complete._record_content_published`
    # stamps on any push where `remote_head == local_head` -- i.e. whenever the publish path
    # successfully pushes ANYTHING. While the gate is red the publish path still pushes, every
    # cycle, a `chore(provenance): verification paused banner` commit (ten of twenty-five
    # consecutive commits on 2026-08-21). Each of those reset this clock.
    #
    # So the wedge silenced its own alarm. `is_publishing_down()` answered False and
    # `describe()` said "content publishing: live -- last reached origin 0.2h ago" while the
    # FIGURES had not moved for 20.8 hours and the last real publish was the previous evening.
    # The deadman's content check reads `state` and cleared its transition on every cycle, so
    # nobody was paged; the director noticed by hand.
    #
    # The ground truth was already here. `com_age` asks git when CONTENT_PATHS last moved and is
    # documented as "the cross-check that catches a publish committing locally and never
    # reaching origin". It was computed, returned in the snapshot, and not consulted by the
    # verdict -- this module's docstring says `state` exists so "two consumers cannot reach
    # different verdicts from the same numbers", and the two numbers inside it disagreed by a
    # day.
    #
    # Fresh now means BOTH: a push landed AND the figures moved. Taking the older of the two is
    # the fail-safe direction -- it can report stale when the site is fine (a quiet sim), which
    # costs an alarm someone dismisses; the other way round costs a day of silence.
    if pub_age is None:
        state = "unpublished" if not STATE_FILE.exists() else "unknown"
    elif com_age is None:
        state = "unknown"          # an unavailable cross-check is NOT evidence of freshness
    elif max(pub_age, com_age) <= STALE_AFTER_SECONDS:
        state = "publishing"
    else:
        state = "stale"

    return {
        "state": state,
        "published_age_seconds": None if pub_age is None else round(pub_age, 1),
        "committed_age_seconds": None if com_age is None else round(com_age, 1),
        "stale_after_seconds": STALE_AFTER_SECONDS,
        # THE AS-AT DATE, CARRIED SO THE PAGE CAN STATE IT. Director, 2026-09-04: *"the staleness
        # banner matters more, not less: a week-old site saying 'as at Monday' is honest, one that
        # implies currency is not."* The banner previously said NOTHING while `state == publishing`,
        # which was defensible at a half-hourly cadence and is a false impression at a weekly one:
        # silence beside a figure reads as "this is current". Derived from the CONTENT clock, never
        # the push clock -- the reader is asking how old the FIGURES are, not when a file last moved.
        "as_at_utc": (
            None if com_age is None
            else datetime.fromtimestamp(now - com_age, timezone.utc).strftime("%Y-%m-%dT%H:%MZ")),
        "cadence_seconds": PUBLISH_CADENCE_SECONDS,
        # The disagreement, named rather than left for a reader to spot: content is being
        # COMMITTED while the publish path is not landing it. Its own fault and its own fix --
        # either the push is not reaching origin, or (2026-08-13) the publisher's commit is dying
        # and the figures only travel when another writer happens to sweep them along.
        "committed_but_unpublished": bool(
            pub_age is not None and com_age is not None and pub_age - com_age > PUSH_LAG_AFTER_SECONDS
        ),
        # Additive and outside the verdict on purpose -- see `queue_depth`. Consumers read
        # `state` via .get() and none enumerate this dict, so a new observation cannot change
        # an existing answer; it can only give a reader something the two clocks never had.
        "queue_depth": queue_depth(),
        "queue_oldest_age_seconds": (
            None if (_o := queue_oldest_age_seconds(now)) is None else round(_o, 1)
        ),
        # DID IT TRY AND FAIL -- beside the ages, not folded into them. See `publisher_refusal`
        # for why this is carried as its own verdict rather than moving `state`: the ages answer
        # "is the weekly publish overdue" and cannot answer this one until the threshold comes
        # due, which on 2026-09-24 was five days after the publisher stopped working.
        "publisher": publisher_refusal(now),
    }


def is_publishing_down(snap: dict | None = None) -> bool:
    """Is content publishing FAILING right now?

    True only on a positive measurement of staleness. An `unknown` age is not silently treated as
    healthy -- it is not this predicate's subject, and the caller pages on it separately -- but it
    is likewise never reported as down, because a missing measurement is not evidence of a fault.
    """
    snap = snapshot() if snap is None else snap
    return snap.get("state") in ("stale", "unpublished")


#: The citation readings that ARE an answer to "why did this publish not land". Only `reproduces`
#: is: it says the named reds were re-run at HEAD and are still red, so `blocking_tests` is the
#: answer and no further hunting is owed. `dead`, `not_asked`, `not_established` and an absent
#: field all leave the question OPEN, and an open question is exactly the trigger for reading the
#: refusal record beside it. Keyed to the property (is this an answer) and not to today's
#: vocabulary: a reading added to `process_run_complete` tomorrow lands OUTSIDE this tuple and so
#: makes the summary look harder, which is the safe direction.
CITATION_ANSWERS = ("reproduces",)

#: How much of a held refusal's evidence line the summary quotes, and it quotes the END.
#:
#: CORRECTED 2026-09-24, BESIDE THE CLAIM THAT WAS WRONG. This landed as 200 chars taken from the
#: HEAD, on the reasoning that these lines are observation-first: *"the commit was created here
#: and `git ls-remote` says origin did not advance to it (push rc=1, origin=..., head=...)"*.
#: That is true of the composed-sentence causes and FALSE of the population. Within the hour the
#: live record moved to a `gate_refusal`, whose evidence is hook OUTPUT kept by
#: `process_run_complete._refusal_evidence_kept` -- which keeps the LAST 900 characters, for the
#: reason its own docstring gives: *"a hook chain prints its refusal LAST, so the one part of the
#: output the field exists to hold was the one part guaranteed to be dropped"*, measured at 31
#: consecutive failures reading `unattributed`. Quoting the head of a deliberately-kept tail
#: re-committed that exact error one layer up, and the rendered line proved it -- the 200
#: characters shown were the elision marker and two green gates.
#:
#: So: same direction as the writer, for the writer's own reason. And the budget is set ABOVE the
#: length of the composed-sentence evidence (224 chars, measured on the live `push_never_landed`
#: record) so those are quoted WHOLE and the head-or-tail question does not arise for them at all.
#: Where it does bite the subject is hook output, and there the end is the verdict.
#:
#: The lesson generalises past this constant: the first version reasoned from the one record that
#: happened to be on disk and called it the population. Printing the line at a real input it had
#: not been designed against is what caught it, in seconds.
HELD_EVIDENCE_QUOTED_CHARS = 280


def _cause_clause(pub: dict) -> str:
    """The half-sentence that says WHY the publisher is refusing — or what was held instead.

    THIS IS THE REPAIR (2026-09-24). What stood here was a single conditional on one value:

        " and the red it cites is DEAD at HEAD, so the cause is unattributed"  if  cited == "dead"

    Two things were wrong with it, and both were live in the same file on the same day.

    FIRST, `unattributed` was FALSE. `liveness_surface_refusal` held `push_never_landed` at a
    named commit with its evidence intact, in the same record the clause had just read. The
    summary told every reader there was no named cause while a named cause sat two keys away, and
    the here-relative red that was the real blocker went unnamed for three hours in a seat whose
    whole job is to unblock.

    SECOND, the clause was keyed to ONE reading of the citation field. When the field moved to
    `not_established` -- which is what it says whenever no red is named at all, i.e. on EVERY
    push failure, provenance refusal and behind-origin refusal -- the clause fell silent
    altogether and said nothing about cause in either direction. The louder of the two defects was
    the one that fired less often.

    So the branch is on whether the citation ANSWERS the question, not on which word it holds,
    and the fall-through is a report rather than a silence: either the held cause and where it
    came from, or the fields that were held and why they were not enough. There is no path
    through this function that says "unattributed" without having looked.

    NOT A RE-RUN, AND THAT IS ON PURPOSE. Re-asking a citation means running pytest, which
    `process_run_complete._reask_citation_at_head` does at failure time where the subject and the
    budget both are. This function is quoted into banners, logs and the delivery brief; a suite
    run behind a one-line summary would be a new way for the summary to be slow rather than a new
    way for it to be right. What it re-asks is the STORED VERDICT'S STANDING: a verdict that does
    not answer the question is not believed just because it is present.
    """
    cited = pub.get("cited_red_at_head")
    if cited in CITATION_ANSWERS:
        # The citation reproduces: `blocking_tests` IS the answer and adding a second cause here
        # would give the reader two places to look for one fault.
        return ""
    lead = (" and the red it cites is DEAD at HEAD" if cited == "dead"
            else f" and its citation reads {cited}" if isinstance(cited, str)
            else " and no citation is recorded")
    held = pub.get("held_refusal")
    if isinstance(held, dict) and held.get("cause"):
        # NAME THE FIELD, not just the cause. "where it came from" is what lets a reader go and
        # check the claim -- and it is the fact whose absence made this defect survive, because
        # nobody knew there was a second field to read.
        evidence = " ".join(str(held.get("evidence")).split())
        if len(evidence) > HELD_EVIDENCE_QUOTED_CHARS:
            # THE END, NOT THE BEGINNING -- see `HELD_EVIDENCE_QUOTED_CHARS`. And SAY IT WAS CUT:
            # a quote that starts mid-word with no marker reads as a corrupted record rather than
            # a bounded one, and a reader who thinks the record is corrupt does not go and read
            # the rest of it.
            evidence = "[...] " + evidence[-HELD_EVIDENCE_QUOTED_CHARS:].lstrip()
        return (lead + ", but `{}` in the same record holds {} at git={}: {}".format(
            held.get("field"), held.get("cause"), str(held.get("git_hash"))[:9], evidence))
    why = pub.get("held_refusal_reason")
    return (lead + ", so the cause is unattributed -- "
            + (str(why) if isinstance(why, str) and why.strip()
               else "and no refusal record was inspected, which is not the same as there being "
                    "none"))


def describe(snap: dict | None = None) -> str:
    """One human line for a page, a banner or a log. Never says "fresh" without a number."""
    snap = snapshot() if snap is None else snap
    state, age = snap.get("state"), snap.get("published_age_seconds")
    if state == "unpublished":
        return "content publishing: NO verified publish on record"
    if state == "unknown":
        return "content publishing: age UNKNOWN (freshness could not be measured)"
    # REPORT THE OLDER CLOCK, for the same reason the verdict now takes it: quoting the push
    # clock here produced "DOWN -- last published 0.2h ago", a line that argues against its own
    # verdict and reads as a glitch rather than a 20-hour outage. The number in a one-line
    # summary has to be the number that made the verdict.
    com_age = snap.get("committed_age_seconds")
    worst = max([a for a in (age, com_age) if a is not None] or [0])
    hours = worst / 3600.0
    # THE BACKLOG RIDES ON THE `live` LINE TOO, and that is the whole point of carrying it. A
    # reader who is told publishing is live has been given the answer to the question they asked
    # and no hint that 35 completed runs are queued behind it, which is exactly how the
    # 2026-09-02/03 shortfall stayed unread while this line was quoted in three places.
    depth = snap.get("queue_depth")
    queued = f" -- {depth} completed run(s) queued behind the publisher" if depth else ""
    # THE WORD "live" HAS TO STOP MEANING "and the publisher works". This line is quoted into the
    # delivery brief and the deadman's log, and on 2026-09-24 it read `live -- figures reached
    # origin 61.1h ago` while 45 consecutive publish attempts had been refused. Both halves were
    # true; the summary was not. A refusal the publisher has recorded outranks the age here for
    # the same reason it does on the banner -- the age says the deadline has not come, the
    # refusal says the thing that would meet it is broken.
    pub = snap.get("publisher") or {}
    refused = ""
    if pub.get("state") == "failing":
        n = pub.get("consecutive_failures")
        since = pub.get("failing_for_seconds")
        refused = (f" -- PUBLISHER REFUSING: {n} consecutive attempt(s) failed"
                   + (f" over {since / 3600.0:.1f}h" if isinstance(since, (int, float)) else "")
                   + _cause_clause(pub))
    if state == "stale":
        extra = " (content is still being committed -- the PUBLISH PATH is what stopped)" \
            if snap.get("committed_but_unpublished") else ""
        return (f"content publishing: DOWN -- figures last moved {hours:.1f}h ago"
                f"{extra}{refused}{queued}")
    verdict = "FAILING" if refused else "live"
    return (f"content publishing: {verdict} -- figures reached origin {hours:.1f}h ago"
            f"{refused}{queued}")
