"""Attribute the publish cycles that died at `commit_refused` to the gate that refused them.

WHY THIS IS A SCRIPT AND NOT A NUMBER IN A DOCUMENT. The Lane 0 direction that produced it
arrived carrying `commit_refused 272`, and the number dissolved on contact with the log: it was
the sum of two DIFFERENT line shapes, one of which did not exist before 2026-08-19. A figure
that cannot be re-derived is a figure that rots exactly the way that one did, so the derivation
lives here and the document quotes it.

WHAT EACH NUMBER COUNTS -- stated here because the whole defect above was two numbers added
without asking that question:

  attempt   one `[process_run] Committing and pushing` line. The publish cycle reached the
            commit step. This is the ONLY denominator this module will produce.
  refusal   one `[process_run] Commit/push failed (commit_refused)` line. One per cycle.
  window    refusals are only NAMEABLE from 2026-08-13, when `git_commit_push` began returning
            named outcomes. Before that every failure -- refused or empty-index alike -- logged
            `Commit/push failed (possibly nothing changed)`. So the lifetime denominator is
            BLIND over its first 77%, and dividing 175 by it understates the rate 4.3x. The
            observable window is derived from the log, never hardcoded: it opens at the first
            named-outcome line.

The attribution itself reuses the publisher's OWN banner table (`_REFUSING_GATE_BANNERS` via
`_parse_refusing_gate`) rather than a second list of needles written here. A private vocabulary
would drift from the gates it names, and the drift would be invisible -- every unmatched refusal
would read as "unnamed gate", which is the answer this module gives when it genuinely cannot
tell.

FAIL-CLOSED ON ATTRIBUTION. A refusal whose hook block is no longer retained in the log, or whose
block names neither a known banner nor a red test, is reported as UNATTRIBUTABLE and counted in
its own bucket. It is never folded into the larger side to make a cleaner split.

EPISODES AND WHAT THEY COST. A run's length in CYCLES is not its cost: the publisher attempts
roughly every 36 minutes, but the gap has p90 5534s and max 19454s, so the conversion is not a
constant and cycles must be converted rather than multiplied. Three quantities, named apart
because substituting one for another is how this direction produced three wrong figures already:

  span     last refused attempt minus first, inside one run. A 1-cycle run has span 0. Honest,
           and it systematically understates because it excludes the recovery.
  outage   first refused attempt until the start of the next attempt that LANDED. This is the
           cost -- how long the publisher could not publish -- and a 1-cycle run has a real one.
  gap      how often the publisher attempts at all. Not a cost; it is the conversion factor, and
           outage is bounded below by it.

A RUN-BREAKER IS A LANDING, NOT "NOT THIS FAILURE MODE". `runs` above marks a cycle refused only
on `commit_refused`, so a `behind_origin` cycle mid-wedge reads as a recovery and ends the run.
For the cycle-share question that is defensible; for a cost question it understates the outage,
because the publisher did not land. `episodes()` breaks only on a landing and reports both.

RIGHT-CENSORING IS REPORTED, NEVER AVERAGED IN. A run still open at the end of the log has no
terminating landing, so its outage is a LOWER BOUND. That is also the run most likely to be the
longest -- an ongoing wedge is the one nobody has cleared -- so folding it into a median or a max
would bias the headline toward comfort. It is carried separately and excluded from both.
"""

from __future__ import annotations

import argparse
import collections
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path

from background.process_run_complete import (
    _REFUSING_GATE_BANNERS,
    _parse_failed_node_ids,
    _parse_refusing_gate,
)

DEFAULT_LOG = Path("docs/observability/sim-runner-log.md")

#: A timestamped runner-log line. Untimestamped lines are hook output belonging to the line above.
_TIMESTAMPED = re.compile(r"^- \[(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) UTC\]")
#: pytest's own summary shapes, and only those. A loose needle like `"failed" in text` matches the
#: word inside a gate's prose ("...would have failed...") and would credit a non-test gate's
#: refusal to a red test, which is the exact direction of error this measurement must not make.
_RED_TEST = re.compile(r"^(FAILED|ERROR) \S|^\d+ failed[,.]|\b\d+ failed, \d+ passed", re.M)

ATTEMPT_NEEDLE = "Committing and pushing"
REFUSAL_NEEDLE = "Commit/push failed (commit_refused)"
HOOK_BLOCK_NEEDLE = "Nothing to commit or commit failed"
#: The pre-2026-08-13 line that made a refusal and a no-op indistinguishable. Its LAST occurrence
#: is what closes the blind span; the first named outcome is what opens the observable one.
BLIND_NEEDLE = "Commit/push failed (possibly nothing changed)"

RED_TEST = "RED TEST"
UNNAMED = "UNNAMED (no known banner, no red named)"
NO_BLOCK = "UNATTRIBUTABLE (hook block not retained)"
#: The two buckets that are honest ignorance rather than an answer. Held as a set so a caller
#: that reports "non-test gate share" cannot accidentally sweep them onto that side.
UNATTRIBUTABLE = frozenset({UNNAMED, NO_BLOCK})


#: Any named commit outcome. `possibly nothing changed` deliberately does NOT match: it is the
#: blind-span line that made a refusal and a no-op indistinguishable, and episodes are only ever
#: built inside the observable window where it does not occur.
_NAMED_OUTCOME = re.compile(r"Commit/push failed \(([a-z_]+)\)")
LANDED = "landed"
MIXED = "MIXED (more than one cause in one episode)"


def _parse_ts(stamp):
    """`'2026-08-13 22:23'` -> aware datetime. The log's resolution is the minute."""
    return datetime.strptime(stamp, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)


def _hook_blocks(lines):
    """Every hook-output block: (start, end, timestamp). The block is the untimestamped run."""
    blocks = []
    for i, line in enumerate(lines):
        m = _TIMESTAMPED.match(line)
        if not (m and HOOK_BLOCK_NEEDLE in line):
            continue
        j = i + 1
        while j < len(lines) and not _TIMESTAMPED.match(lines[j]):
            j += 1
        blocks.append((i, j, "{} {}".format(m.group(1), m.group(2))))
    return blocks


def _body_at(lines, blocks, i):
    """The hook-output block belonging to the verdict at `lines[i]`, or None.

    Factored out of `_cause_at` because the subject analysis below needs the same block the cause
    was read from. Two independent lookups would eventually disagree about WHICH block belongs to a
    cycle, and then a subject would be compared against a cause from a different attempt.
    """
    # The hook block sits immediately above its verdict; anything further away belongs to a
    # different cycle and is not evidence about this one.
    near = [b for b in blocks if b[1] <= i and i - b[1] <= 3]
    if not near:
        return None
    b = max(near, key=lambda x: x[1])
    return "\n".join(lines[b[0]:b[1]])


def _cause_at(lines, blocks, i):
    """Which gate refused the `commit_refused` line at `lines[i]`. Fail-closed on ignorance."""
    body = _body_at(lines, blocks, i)
    if body is None:
        return NO_BLOCK
    return _parse_refusing_gate(body) or (RED_TEST if _RED_TEST.search(body) else UNNAMED)


def attribute(text):
    """Attribute every `commit_refused` cycle in `text`. Returns a plain dict of findings."""
    lines = text.split("\n")
    blocks = _hook_blocks(lines)
    attempts = [_TIMESTAMPED.match(line) for line in lines
                if _TIMESTAMPED.match(line) and ATTEMPT_NEEDLE in line]
    attempts = ["{} {}".format(m.group(1), m.group(2)) for m in attempts]

    opens = None
    for line in lines:
        m = _TIMESTAMPED.match(line)
        if m and REFUSAL_NEEDLE in line:
            opens = "{} {}".format(m.group(1), m.group(2))
            break

    counts = collections.Counter()
    sequence = []
    for i, line in enumerate(lines):
        if REFUSAL_NEEDLE not in line or not _TIMESTAMPED.match(line):
            continue
        # The hook block sits immediately above its verdict; anything further away belongs to a
        # different cycle and is not evidence about this one.
        key = _cause_at(lines, blocks, i)
        counts[key] += 1
        sequence.append(key)

    observable = [d for d in attempts if opens and d >= opens]
    # A run is over CYCLES, not over lines. A refused cycle emits its own attempt line first, so
    # counting attempt lines as run-breakers ends every run at 1 and reports a clustered log as a
    # uniform hazard -- which is the opposite of the finding.
    outcomes = []
    for line in lines:
        if not _TIMESTAMPED.match(line):
            continue
        if ATTEMPT_NEEDLE in line:
            outcomes.append(False)
        elif REFUSAL_NEEDLE in line and outcomes:
            outcomes[-1] = True
    runs = []
    run = 0
    for refused in outcomes:
        if refused:
            run += 1
        elif run:
            runs.append(run)
            run = 0
    if run:
        runs.append(run)

    total = sum(counts.values())
    unattributable = sum(counts[k] for k in UNATTRIBUTABLE)
    return {
        "refusals": total,
        "attempts_lifetime": len(attempts),
        "attempts_observable": len(observable),
        "observable_from": opens,
        "by_gate": dict(counts),
        "red_test": counts[RED_TEST],
        "non_test_gate": total - counts[RED_TEST] - unattributable,
        "unattributable": unattributable,
        "runs": sorted(runs, reverse=True),
        "sequence": sequence,
    }


def cycles(text):
    """Every publish cycle in the OBSERVABLE window, in log order.

    A cycle is one `Committing and pushing` line plus whatever outcome line follows it before the
    next one. There is no success line in this log -- the publisher logs an attempt and then only
    speaks again if it FAILED -- so `LANDED` is the absence of a named failure, not a positive
    observation. That asymmetry is why the window matters: before the named-outcome vocabulary
    arrived, absence meant nothing at all.
    """
    lines = text.split("\n")
    blocks = _hook_blocks(lines)
    opens = None
    for line in lines:
        m = _TIMESTAMPED.match(line)
        if m and REFUSAL_NEEDLE in line:
            opens = "{} {}".format(m.group(1), m.group(2))
            break

    out = []
    for i, line in enumerate(lines):
        m = _TIMESTAMPED.match(line)
        if not m:
            continue
        stamp = "{} {}".format(m.group(1), m.group(2))
        if ATTEMPT_NEEDLE in line:
            out.append({"at": stamp, "outcome": LANDED, "cause": None, "subject": None})
            continue
        named = _NAMED_OUTCOME.search(line)
        if named and out:
            out[-1]["outcome"] = named.group(1)
            if REFUSAL_NEEDLE in line:
                body = _body_at(lines, blocks, i)
                out[-1]["cause"] = _cause_at(lines, blocks, i)
                # Read from the SAME block the cause came from, so a subject can never be paired
                # with a cause parsed out of a different attempt.
                out[-1]["subject"] = _subject_at(out[-1]["cause"], body)
    return [c for c in out if opens and c["at"] >= opens]


def _episodes(seq, *, breaker_is_landing):
    """Group `seq` into maximal runs of non-landing cycles containing at least one refusal.

    `breaker_is_landing=False` reproduces the cycle-share definition -- only `commit_refused`
    continues a run, so any other failure ends it. `True` is the cost definition: only a LANDING
    ends an outage, because any other outcome means the publisher still did not publish.
    """
    def continues(c):
        return c["outcome"] != LANDED if breaker_is_landing else c["outcome"] == "commit_refused"

    out, cur = [], []
    for idx, c in enumerate(seq):
        if continues(c):
            cur.append((idx, c))
            continue
        if cur:
            out.append(_close(cur, seq))
            cur = []
    if cur:
        out.append(_close(cur, seq))
    return [e for e in out if e["refused_cycles"]]


def _close(cur, seq):
    """Finish one episode: its span, its outage, its causes, and whether it is censored."""
    members = [c for _, c in cur]
    member_ix = [i for i, _ in cur]
    refused = [c for c in members if c["outcome"] == "commit_refused"]
    start = _parse_ts(members[0]["at"])
    last = _parse_ts(members[-1]["at"])
    after = seq[cur[-1][0] + 1:]
    recovery = next((c for c in after if c["outcome"] == LANDED), None)
    # An episode holds EVERY non-landing cycle, so its recovery must be the very next cycle. If it
    # is not, a cycle was skipped and the "trailing gap" spans an attempt nobody counted. This is
    # the check that a duration comparison cannot make -- see `trailing_gap_report`.
    recovery_adjacent = bool(after) and recovery is after[0]
    causes = sorted({c["cause"] for c in refused if c["cause"]})
    return {
        "from": members[0]["at"],
        # The three timestamps `span_s` and `outage_s` are built from, carried RAW so the
        # decomposition can re-derive the trailing gap from them instead of differencing two
        # figures that would cancel a shared anchor error. See `trailing_gap_report`.
        "last_at": members[-1]["at"],
        # The last REFUSED attempt, which is the last attempt only when the episode ends on a
        # refusal. Under the cost definition a `behind_origin` cycle continues an episode without
        # refusing, so these two can differ and the difference is not a rounding detail.
        "last_refused_at": refused[-1]["at"] if refused else None,
        "recovery_at": recovery["at"] if recovery else None,
        "recovery_adjacent": recovery_adjacent,
        # EVERY member cycle, refused or not, with its index in `seq`. `interval_report` walks
        # THIS and not `refused`, because the interval between two attempts is only evidence about
        # one gate if no third attempt sits inside it -- and a `behind_origin` cycle is an attempt.
        # The index is what makes that checkable rather than asserted; see `intervals_adjacent`.
        "members": [{"at": c["at"], "outcome": c["outcome"], "cause": c["cause"], "ix": i}
                    for i, c in zip(member_ix, members)],
        "recovery_ix": (cur[-1][0] + 1 + next(
            (k for k, c in enumerate(after) if c["outcome"] == LANDED), 0)) if recovery else None,
        "cycles": len(members),
        "refused_cycles": len(refused),
        "span_s": (last - start).total_seconds(),
        # Censored: the log ends inside this run, so no landing bounds it. Its outage is a LOWER
        # bound and is reported as one -- never as a number that can be maxed or medianed.
        "censored": recovery is None,
        "outage_s": None if recovery is None
        else (_parse_ts(recovery["at"]) - start).total_seconds(),
        "causes": causes,
        # The ORDER the causes fired in, which is what separates gates QUEUEING (each cleared
        # once, the next then fires) from gates FLAPPING (one cause recurring after another has
        # intervened). A set cannot tell those apart and they call for opposite responses.
        "cause_sequence": [c["cause"] for c in refused],
        # Index-aligned with `cause_sequence` BY CONSTRUCTION -- both are built from `refused` in
        # one order. The subject analysis indexes one with the other's position, so a divergence
        # here would silently compare a gate's cause against another gate's subject.
        "subjects": [c["subject"] for c in refused],
        # An episode with two causes is not attributed to either. Same discipline as the
        # unattributable bucket: never assign to the side that makes the split cleaner.
        "cause": causes[0] if len(causes) == 1 else MIXED,
    }


def episode_report(text):
    """Episode duration by cause, on both run definitions. The whole point of the measurement."""
    seq = cycles(text)
    gaps = [(_parse_ts(b["at"]) - _parse_ts(a["at"])).total_seconds()
            for a, b in zip(seq, seq[1:])]
    strict = _episodes(seq, breaker_is_landing=False)
    cost = _episodes(seq, breaker_is_landing=True)

    bounded = [e for e in cost if not e["censored"]]
    by_cause = collections.defaultdict(list)
    for e in bounded:
        by_cause[e["cause"]].append(e["outage_s"])
    total = sum(e["outage_s"] for e in bounded)
    return {
        "cycles": len(seq),
        "median_gap_s": statistics.median(gaps) if gaps else 0.0,
        # The widest gap the log ITSELF contains. `trailing_gap_report` bounds one trailing gap by
        # it, and a hardcoded bound would go stale the first time the publisher stalls longer.
        "max_gap_s": max(gaps) if gaps else 0.0,
        "episodes_strict": len(strict),
        "episodes_cost": len(cost),
        "censored": [e for e in cost if e["censored"]],
        "bounded": bounded,
        "total_outage_s": total,
        "longest": max(bounded, key=lambda e: e["outage_s"]) if bounded else None,
        "by_cause": {k: sorted(v) for k, v in by_cause.items()},
        "mixed": sum(1 for e in cost if e["cause"] == MIXED),
        "multi_cycle": sum(1 for e in cost if e["cycles"] > 1),
    }


def trailing_gap_report(ep):
    """Split each bounded episode's outage into the redness that STOOD and the rhythm's tail.

    Pre-registered before it was computed once, in
    `docs/staging/records/SEAT_PREREGISTRATION_WHETHER_THE_OUTAGE_IS_THE_REDNESS_STANDING_OR_THE_PUBLISHER_NOT_LOOKING_2026-09-05.md`.
    Read that first; the predictions and the trap below are stated there and not restated here.

    WHAT EACH SIDE IS, because they are brackets and neither is the quantity:

      span          every minute of it is between two OBSERVED refusals, so it is a LOWER bound on
                    how long the redness stood.
      trailing gap  outage minus span: from the episode's last attempt to the landing attempt. The
                    red may have cleared at any instant inside it, so it is an UPPER bound on time
                    lost to the retry rhythm and never an estimate of it.

    SINGLE-CYCLE EPISODES ARE NEVER POOLED IN. A single-cycle episode has span 0 by construction,
    so 100% of its outage is trailing gap -- pooling would return "the rhythm is the whole cost"
    as an arithmetic identity of the episode definition rather than as an observation about the
    publisher. The headline set is `multi`; `single` is reported beside it as cost the rhythm owns
    by definition.
    """
    rows = []
    for e in ep["bounded"]:
        gap = e["outage_s"] - e["span_s"]
        # NOT `outage - span` a second time. Re-derived from the episode's own two timestamps, so
        # a span and an outage anchored at DIFFERENT starts disagree here instead of cancelling --
        # the index-alignment defect this module has already had once, in `subjects`.
        direct = (_parse_ts(e["recovery_at"]) - _parse_ts(e["last_at"])).total_seconds()
        # The pre-registration's literal words are "the landing attempt minus the last REFUSED
        # attempt". That is the same quantity only where the episode ends on a refusal, which the
        # cost definition does not guarantee. Both are carried and the divergence is counted.
        to_refusal = (_parse_ts(e["recovery_at"])
                      - _parse_ts(e["last_refused_at"])).total_seconds()
        rows.append({
            "from": e["from"],
            "cycles": e["cycles"],
            "cause": e["cause"],
            "span_s": e["span_s"],
            "outage_s": e["outage_s"],
            "trailing_gap_s": gap,
            "trailing_gap_to_last_refusal_s": to_refusal,
            "ends_on_refusal": e["last_at"] == e["last_refused_at"],
            "anchors_agree": abs(direct - gap) < 1.0,
            "recovery_adjacent": e["recovery_adjacent"],
        })

    multi = [r for r in rows if r["cycles"] > 1]
    single = [r for r in rows if r["cycles"] == 1]

    def side(xs):
        outage = sum(r["outage_s"] for r in xs)
        gaps = sorted(r["trailing_gap_s"] for r in xs)
        return {
            "episodes": len(xs),
            "outage_s": outage,
            "span_s": sum(r["span_s"] for r in xs),
            "trailing_gap_s": sum(gaps),
            # None, not 0.0: an empty side has no median, and a zero here would read as "the tail
            # is nothing" when it means "there was nothing to measure".
            "median_trailing_gap_s": statistics.median(gaps) if gaps else None,
            "max_trailing_gap_s": gaps[-1] if gaps else None,
        }

    return {
        "rows": rows,
        "multi": side(multi),
        "single": side(single),
        # Controls. Each names a way the INSTRUMENT, not the world, would be wrong; a non-empty
        # list voids the decomposition rather than qualifying it.
        "negative": [r for r in rows if r["trailing_gap_s"] < 0],
        # THE PRE-REGISTRATION'S SECOND CONTROL, AND WHY IT IS NOT THE ONE THAT MATTERS. It asked
        # that a trailing gap not exceed the widest observed inter-attempt gap, "because it is ONE
        # gap by construction". Both readings of that fail. Against the 19,454s the document
        # quoted, it is keyed to yesterday's answer and reddens when the publisher merely stalls
        # longer -- which it since has, to 40.0h. Against a bound DERIVED from the log it cannot
        # fail at all: the trailing gap IS one of the gaps the maximum is taken over, so the
        # comparison is arithmetic. It is kept as a record-consistency canary -- it can still fire
        # on a corrupted episode record -- and it is not evidence about the publisher.
        "over_max_gap": [r for r in rows if r["trailing_gap_s"] > ep["max_gap_s"]],
        # This is what that control was REACHING for and could not express. The episode holds
        # every non-landing cycle, so its recovery must be the immediately next cycle; a
        # non-adjacent recovery means a cycle was skipped and the gap spans an uncounted attempt.
        # Unlike the duration comparison it is not implied by the arithmetic, so it can fail.
        "recovery_not_adjacent": [r for r in rows if not r["recovery_adjacent"]],
        "anchor_mismatch": [r for r in rows if not r["anchors_agree"]],
        "not_ending_on_refusal": [r for r in rows if not r["ends_on_refusal"]],
        "max_gap_s": ep["max_gap_s"],
    }


#: The five interval classes. Named as constants because the reachability control asserts over the
#: whole set, and a class spelled by hand in one branch would silently leave that set incomplete.
BRACKETED = "BRACKETED"
CLEARED_WITHIN = "CLEARED-WITHIN"
MASKED = "MASKED"
UNRANKABLE = "UNRANKABLE"
TRAILING = "TRAILING"
INTERVAL_CLASSES = (BRACKETED, CLEARED_WITHIN, MASKED, UNRANKABLE, TRAILING)
#: The only two that put a duration on a named gate -- and they point in OPPOSITE directions, so
#: they are never summed into one "attributed" figure. Held as a pair so a caller cannot add a
#: third by accident.
ATTRIBUTING = (BRACKETED, CLEARED_WITHIN)


def _classify_interval(a, b, ranks):
    """One interval, from the attempt `a` to the immediately next attempt `b`.

    `(class, gate the duration attaches to, gate demonstrably RE-BROKEN inside)`.

    THE ONE INFERENCE, and it is the same one `ordering_report` uses: the chain is serial and
    stops at the first refusal, so a cycle naming rank r is a positive observation that every gate
    BELOW r passed in that cycle, and says nothing whatever about the gates above it.
    """
    ca, cb = a["cause"], b["cause"]
    if ca is None or cb is None or ca not in ranks or cb not in ranks:
        # A `behind_origin` attempt refuses nothing and an UNATTRIBUTABLE one names nothing. Either
        # way one end carries no rank, so no comparison is licensed. Ignorance, reported as it.
        return UNRANKABLE, None, None
    if ca == cb:
        # NOT "the gate held". Both ends observed it refusing and nothing was observed in between,
        # so the log contains no evidence it cleared -- which is weaker, and is why this class is
        # called BRACKETED. It could have cleared and re-broken with no attempt to see it.
        return BRACKETED, ca, None
    if ranks[cb] > ranks[ca]:
        # The far end reached PAST `ca`, so `ca` demonstrably passed at some instant inside. An
        # UPPER bound on how much longer it held, never an estimate of it.
        return CLEARED_WITHIN, ca, None
    # The far end stopped BELOW `ca`, so `ca`'s state there is unobservable and no duration can be
    # attributed to it. The inference runs the other way instead: `cb` sits below `ca`, so `cb`
    # passed at the start and refused at the end -- it re-broke inside this interval.
    return MASKED, None, cb


def interval_report(text, ranks=None):
    """Attribute each bounded episode's outage to NAMED gates, interval by interval.

    WHY THE EPISODE IS THE WRONG UNIT, which is the whole reason `MIXED` exists. An episode has one
    `cause` field and can have several causes, so that field must either lie or abstain; it
    correctly abstains, and `MIXED` is 74.6% of bounded outage as a result. The largest label we
    publish is by construction not a cause. The unit with exactly one observation at each end is
    the interval between two consecutive attempts.

    THE PARTITION IS EXACT, NOT AN APPORTIONMENT. For members `m_0..m_{n-1}` and recovery `r`,
    `outage = (r - m_0) = sum(m_{i+1} - m_i) + (r - m_{n-1})`, so every second of an episode lands
    in exactly one interval and the last term is the trailing gap `trailing_gap_report` measures.
    Nothing here is weighted, shared out or estimated; `partition_error` asserts it per episode.

    Pre-registered before it was computed once, in
    `docs/staging/records/SEAT_PREREGISTRATION_WHAT_THE_MIXED_BUCKET_IS_STANDING_ON_2026-09-05.md`.
    The five classes and what each licenses are stated there and in `_classify_interval`.
    """
    ranks = gate_ranks() if ranks is None else ranks
    episodes = [e for e in _episodes(cycles(text), breaker_is_landing=True) if not e["censored"]]
    rows, per_episode = [], []
    for e in episodes:
        ms = e["members"]
        mine = []
        for a, b in zip(ms, ms[1:]):
            cls, gate, rebroke = _classify_interval(a, b, ranks)
            mine.append({
                "episode": e["from"], "episode_cause": e["cause"], "at": a["at"],
                "seconds": (_parse_ts(b["at"]) - _parse_ts(a["at"])).total_seconds(),
                "class": cls, "gate": gate, "re_broke": rebroke,
                # A PINNED TAUTOLOGY, and labelled as one rather than trusted. An episode is a
                # maximal run of CONSECUTIVE non-landing cycles, so members are adjacent by
                # construction and this flag cannot go false however the publisher behaves --
                # mutating it to a literal `True` kills no control. It survives as a canary over a
                # future change to `_episodes`, and it is NOT what protects the BRACKETED claim.
                # What protects that claim is walking `members` and not `refused`: with an
                # intervening `behind_origin` attempt the interval is UNRANKABLE rather than one
                # wide BRACKETED span, and THAT is mutation-proven (see the adjacency control).
                "adjacent": b["ix"] == a["ix"] + 1,
            })
        mine.append({
            "episode": e["from"], "episode_cause": e["cause"], "at": ms[-1]["at"],
            "seconds": (_parse_ts(e["recovery_at"]) - _parse_ts(ms[-1]["at"])).total_seconds(),
            # Unattributable BY CONSTRUCTION, exactly as the single-cycle 100% tail is: whatever
            # was red cleared somewhere inside here and the log cannot say when. It is a class and
            # not a residue, so it can never be quietly absorbed into an attributed total.
            "class": TRAILING, "gate": None, "re_broke": None,
            "adjacent": e["recovery_ix"] == ms[-1]["ix"] + 1,
        })
        per_episode.append({
            "from": e["from"], "cause": e["cause"], "outage_s": e["outage_s"],
            "cycles": e["cycles"], "intervals": mine,
            # C1. Re-derived from the members' OWN timestamps against the episode's outage, so a
            # decomposition that loses or double-counts time disagrees here instead of producing a
            # table of reasonable-looking rows that do not add up.
            "partition_error_s": abs(sum(r["seconds"] for r in mine) - e["outage_s"]),
            "has_masked": any(r["class"] == MASKED for r in mine),
        })
        rows.extend(mine)
    return {"rows": rows, "episodes": per_episode, "ranks": ranks}


def interval_attribution(text, ranks=None, only=None):
    """Aggregate `interval_report` into the per-gate table, over `only` episode causes.

    `only=(MIXED,)` answers the question this was built for. `only=None` is every bounded episode.
    """
    rep = interval_report(text, ranks)
    eps = [e for e in rep["episodes"] if only is None or e["cause"] in only]
    rows = [r for e in eps for r in e["intervals"]]
    total = sum(r["seconds"] for r in rows)

    by_class = {c: sum(r["seconds"] for r in rows if r["class"] == c) for c in INTERVAL_CLASSES}
    counts = {c: sum(1 for r in rows if r["class"] == c) for c in INTERVAL_CLASSES}
    by_gate = collections.defaultdict(lambda: dict.fromkeys(ATTRIBUTING, 0.0))
    for r in rows:
        if r["class"] in ATTRIBUTING:
            by_gate[r["gate"]][r["class"]] += r["seconds"]
    re_broke = collections.Counter(r["re_broke"] for r in rows if r["re_broke"])

    # C4, and it is a SUBSET claim and not the equality the pre-registration asked for -- see the
    # finding. Both routes read the same backward rank move, but `ordering_report` walks the ranked
    # causes with unranked cycles SKIPPED, while an interval with an unranked end is UNRANKABLE.
    # So an established re-arrival separated by an unattributable cycle is invisible here, and the
    # size of that gap is a quantity rather than a discrepancy to smooth over.
    est = {e["from"] for e in ordering_report(text, ranks) if e["established"]}
    masked_eps = {e["from"] for e in rep["episodes"] if e["has_masked"]}

    return {
        "episodes": len(eps),
        "total_s": total,
        "intervals": len(rows),
        "by_class": by_class,
        "counts": counts,
        # Two columns, never one. A floor on a gate that stayed red and a ceiling on a gate that
        # went green are not the same quantity and their sum is not a quantity at all.
        "by_gate": {g: v for g, v in sorted(
            by_gate.items(), key=lambda kv: -kv[1][BRACKETED])},
        "re_broke": re_broke,
        "attributed_s": by_class[BRACKETED] + by_class[CLEARED_WITHIN],
        "residue_s": by_class[MASKED] + by_class[UNRANKABLE] + by_class[TRAILING],
        # Controls. A non-empty list VOIDS the table above rather than qualifying it.
        "partition_error": [e for e in eps if e["partition_error_s"] >= 1.0],
        "not_adjacent": [r for r in rows if not r["adjacent"]],
        "unreached_classes": [c for c in INTERVAL_CLASSES if not counts[c]],
        "over_outage": [e for e in eps
                        if sum(r["seconds"] for r in e["intervals"]
                               if r["class"] in ATTRIBUTING) > e["outage_s"] + 1.0],
        # THE SUBSET DIRECTION IS A THEOREM, so this is the second pinned tautology and is not
        # evidence. Two adjacent ranked members are also adjacent among the ranked causes, and
        # `rk(b) < rk(a) <= peak`, so every MASKED interval is a backward step against the running
        # peak too -- given both routes read ONE rank table, which they do. Emptying it kills no
        # control. It fires only if the two rank tables ever come apart.
        "masked_not_established": sorted(masked_eps - est),
        # THIS is the half that carries information and it is mutation-proven: established
        # re-arrivals the interval view cannot see, because an unattributable cycle sits between
        # the two observations and `ordering_report` steps over what UNRANKABLE stops at.
        "established_without_masked": sorted(est - masked_eps),
    }


#: The hook that IS the firing order. Ranks are derived from it at call time, never hardcoded
#: here -- a rank table written by hand is a paraphrase, and the defect this whole module exists
#: to avoid is a paraphrase of the gates drifting from the gates.
HOOK = Path("tools/git-hooks/pre-commit")
#: The commit-msg gate runs only after ALL of pre-commit passed, so it is last by construction and
#: is not findable in the pre-commit file. Its rank is "after everything", not a guess.
_AFTER_PRE_COMMIT = 10 ** 6


def _hook_order(hook_text):
    """Emitter module -> its position in the serial chain, read from the hook's own invocations.

    Matches both spellings the hook uses (`python3 tools/x.py` and `python3 -m tools.x`), because
    a matcher that knew only one would silently rank half the chain as absent -- and absent, in
    the ordering analysis below, reads as "no evidence" rather than as a broken instrument.
    """
    order = {}
    for i, line in enumerate(hook_text.split("\n")):
        m = re.search(r"python3\s+(?:-m\s+([\w.]+)|(\S+\.py))", line)
        if not m:
            continue
        mod = m.group(2) or (m.group(1).replace(".", "/") + ".py")
        order.setdefault(mod, i)
    return order


#: Shortest prefix of a needle still specific enough to locate. Below this a match is a
#: coincidence rather than a position, and a coincidental position is worse than none.
_MIN_NEEDLE = 24


def _needle_pos(body, needle):
    """Where `needle` is printed in `body`, or None when that cannot be established.

    NOT a bare `.find()`, and the difference is load-bearing. Gate banners are written in the
    source as ADJACENT STRING LITERALS split across lines, so the runtime needle
    (`"...HAS NO PARSEABLE SEVERITY HEADER"`) never occurs contiguously in the file that prints
    it. A `.find()` returns -1 there, and the obvious fallback -- treat -1 as 0 -- ranks that gate
    FIRST inside its emitter, which is the strongest position there is. That inverts the one
    comparison this module makes: it would report a backward step, i.e. an ESTABLISHED
    re-arrival, from a gate whose position was never found. So the fallback is None and the cause
    leaves the analysis entirely.
    """
    # The floor bounds SHRINKING, never the needle itself: `"[level-gate] ❌"` is 14 characters
    # and entirely specific, and an earlier draft of this floor silently dropped it -- along with
    # site-lane and scope-evidence, three of the commonest causes in the log -- leaving an
    # analysis that looked clean because its biggest gates had left it.
    at = body.find(needle)
    if at >= 0:
        return at
    probe = needle[:-1]
    while len(probe) >= _MIN_NEEDLE:
        at = body.find(probe)
        if at >= 0:
            return at
        probe = probe[:-1]
    return None


def gate_ranks(hook_text=None, emitter_texts=None):
    """`cause name -> (chain rank, rank within its emitter)`, derived from the enforcement.

    WHY A PAIR AND NOT AN INTEGER. Several causes share one emitter: `finding-class`,
    `finding-severity` and `RED TEST` are all printed by `pre_commit_test_gate.py`, which the hook
    invokes ONCE. Ranking them equal would throw away the fact that its `main()` runs the
    consolidation check second and pytest LAST -- and that fact is what makes the largest episode
    in the log analysable at all. The secondary rank is the byte offset of the cause's own needle
    inside the file that prints it, so it is read from the emitter rather than asserted here.

    A cause with no rank (unattributable, or a gate the hook no longer invokes) is ABSENT from the
    result rather than sorted to an end. Callers must skip it; ranking ignorance would invent
    ordering evidence, which is the one error this analysis cannot survive.
    """
    hook_text = HOOK.read_text(encoding="utf-8") if hook_text is None else hook_text
    order = _hook_order(hook_text)
    texts = {} if emitter_texts is None else dict(emitter_texts)

    def body(path):
        if path not in texts:
            p = Path(path)
            texts[path] = p.read_text(encoding="utf-8") if p.exists() else ""
        return texts[path]

    ranks = {}
    for name, needles, emitter in _REFUSING_GATE_BANNERS:
        if emitter not in order:
            continue
        inner = _needle_pos(body(emitter), needles[0])
        if inner is None:
            continue
        cand = (order[emitter], inner)
        # A gate with two rows (half-hourly) keeps its EARLIEST needle: the gate refuses at the
        # first of them, and the later row is a second message from the same chain position.
        if name not in ranks or cand < ranks[name]:
            ranks[name] = cand
    # The write-time gate lives in commit-msg, which runs after the whole pre-commit chain.
    for name, _, emitter in _REFUSING_GATE_BANNERS:
        if emitter not in order and "write_time_gate" in emitter:
            ranks[name] = (_AFTER_PRE_COMMIT, 0)
    tg = "tools/pre_commit_test_gate.py"
    if tg in order:
        # pytest is invoked, not printed, so RED TEST's needle is the subprocess call itself.
        m = re.search(r'"-m",\s*"pytest"', body(tg))
        ranks[RED_TEST] = (order[tg], m.start() if m else len(body(tg)))
    return ranks


def ordering_report(text, ranks=None):
    """Which episodes carry a gate that went PASSING -> REFUSING, and which merely look like it.

    THE ONLY INFERENCE THE LOG LICENSES. The chain is serial and stops at the first refusal, so a
    cycle naming a gate at rank r is a positive observation that every gate below r PASSED in that
    cycle. A later cycle naming a rank BELOW the highest already reached is therefore a gate that
    passed and then refused -- an established re-arrival, immune to the firing order.

    AND THE ONE IT DOES NOT. A forward step is what a genuine queue AND a set of gates that were
    all red from the start both produce, because a later gate's state is unobservable while an
    earlier one refuses. So `queueing` is NOT falsifiable here and is never reported as found:
    the complement bucket is ORDER-CONSISTENT, which is a statement about what we cannot tell
    apart, not a finding that the gates queued.
    """
    ranks = gate_ranks() if ranks is None else ranks
    episodes = [e for e in _episodes(cycles(text), breaker_is_landing=True) if not e["censored"]]
    out = []
    for e in episodes:
        # The index is kept because unranked causes are SKIPPED here, so a position in `seq` is
        # not a position in `cause_sequence` -- and `subjects` is index-aligned with the latter.
        # Re-deriving the position downstream by counting ranked causes would pair a step with
        # another cycle's subject the moment one unattributable cycle sits in between.
        seq = [(k, c, ranks[c]) for k, c in enumerate(e["cause_sequence"]) if c in ranks]
        steps, seen, peak = [], [], None
        for k, cause, rk in seq:
            if peak is not None and rk < peak:
                steps.append({"cause": cause, "below": peak, "at": k})
            peak = rk if peak is None else max(peak, rk)
            seen.append(cause)
        # A RECURRENCE is the predecessor's post-hoc test: a cause reappearing after a different
        # one intervened. Kept so the two classifications can be compared row by row rather than
        # only in aggregate -- the disagreement is the finding.
        recurs = any(any(x != c for x in seen[seen.index(c):len(seen) - seen[::-1].index(c)])
                     for c in set(seen))
        out.append({**e, "ranked_causes": len(seq), "backward_steps": steps,
                    "established": bool(steps), "recurrence": recurs})
    return out


def masking_exposure(text, ranks=None):
    """Per gate: how often it was NAMED, PROVEN to have passed, and simply UNKNOWABLE.

    THE COST OF THE SAME EARLY EXIT THAT MAKES `ordering_report` WORK. A cycle naming rank r
    proves every gate below r passed and says nothing about the gates above it, so `by_gate` is a
    distribution of FIRST failing gate. Each count there is a LOWER bound, and the bias is monotone
    in chain position: the last gate is only ever visible when every gate before it passes.

    Without this table the natural reading of a gate with zero refusals is "it never blocked a
    publish". For the deepest gates that is not an observation about the gate at all -- their state
    is unknown on every refused cycle in the window, and "never named" and "never broken" are
    indistinguishable. Reported per gate rather than as one bias figure, because the exposure is
    wildly uneven across the chain and a single number would hide exactly that.

    A cause with no rank is skipped, not sorted to an end -- same rule as `gate_ranks`.
    """
    ranks = gate_ranks() if ranks is None else ranks
    seq = [c["cause"] for c in cycles(text) if c["outcome"] == "commit_refused"]
    out = {}
    for gate, rank in ranks.items():
        named = passing = unknown = 0
        for cause in seq:
            if cause == gate:
                named += 1
            elif cause in ranks and ranks[cause] > rank:
                # A DEEPER gate was reached, which is a positive observation that this one passed.
                passing += 1
            else:
                # Either a shallower gate refused first (this one was never reached) or the cause
                # has no rank. Both are ignorance, and neither is folded onto the passing side.
                unknown += 1
        out[gate] = {"rank": rank, "named": named,
                     "proven_passing": passing, "unknown": unknown}
    return out


# ---------------------------------------------------------------------------------------------
# WHAT the gate refused ON, not merely WHICH gate refused.
#
# The predecessor closed by saying the log "records which gate refused and never what changed
# between attempts", and proposed reading the TREE STATE between consecutive refused cycles. That
# route is not taken here and the reason is a base rate: `git log --all --since=2026-08-13` is
# 60-191 commits a day against a median 3300s gap between attempts, so "did the tree move" answers
# YES for re-breaks and non-re-breaks alike. The premise is also false -- every gate prints the
# artefact it objected to, inside the block the log already retains.

#: `- TWO ROOMS <F>.md: …`, `- UNCONSOLIDATED <F>.md: …`, `- STALE SEVERITY <F>.md: …`,
#: `- RESURRECTED <F>.md: …`, `- MISSING CLASS DOC <F>.md`. The KIND is matched as a shape
#: (leading capitals) rather than enumerated, so a new objection kind is picked up instead of
#: silently dropped.
#
# THE SUBJECT IS THE FIRST `.md` ON THE LINE, and the two near-misses pull opposite ways.
# RESURRECTED's TAIL names a SECOND document (`superseded by <CLASS>.md`) which is not what
# refused, so the pattern must not reach past the first token. But `MISSING CLASS DOC <F>.md` ends
# at the filename with NO trailing colon -- so anchoring on `:` to exclude that tail drops this
# kind entirely, and 8 of the log's 49 finding-class subjects leave the analysis silently. That is
# the predecessor's own defect (a fail-closed fix whose table read clean because its biggest
# entries had left it) and it was caught the same way: by printing both forms against the real log
# rather than by reasoning about the regex.
#
# ESTABLISHED EQUIVALENCE, not an untested branch: inserting `.*?` before the group changes
# nothing (61 subjects, identical list, over the whole retained log), because leftmost-minimal
# matching already prefers the empty skip. The tightness here is documentation of intent; what
# actually selects the first token is the regex engine, and the control above pins the OUTCOME.
_SUBJ_FINDING_CLASS = re.compile(r"^\s*-\s+[A-Z][A-Z ]+?\s(\S+\.md)\b", re.M)
#: `§0: level_current 2->3 on <ATOM> declares a level for source this commit does NOT contain`.
_SUBJ_LEVEL_GATE = re.compile(r"^§\d+:\s+level_current\s+\S+\s+on\s+(\S+?)\s", re.M)
_ORPHAN_BANNER = "orphan-ratchet: THIS COMMIT ADDS WORK THAT NOTHING RUNS."
_ORPHAN_END = "Nothing imports these"


def _subjects_finding_class(body):
    return frozenset(_SUBJ_FINDING_CLASS.findall(body)) or None


def _subjects_level_gate(body):
    return frozenset(_SUBJ_LEVEL_GATE.findall(body)) or None


def _subjects_orphan(body):
    """The indented module lines between the ratchet's banner and its explanation."""
    out, inside = [], False
    for line in body.split("\n"):
        if _ORPHAN_BANNER in line:
            inside = True
            continue
        if not inside:
            continue
        if _ORPHAN_END in line:
            break
        token = line.strip()
        # One bare token per line. A line with a space in it is the prose, not a module, and
        # admitting it would make two blocks differ on wording rather than on subject.
        if token and " " not in token:
            out.append(token)
    return frozenset(out) or None


def _subjects_pytest(body):
    """pytest's own `FAILED <nodeid>` summary, via the parser the publisher itself uses."""
    return frozenset(_parse_failed_node_ids(body)) or None


#: cause name -> how that gate names its subject. Keyed by the name the BANNER TABLE produces, so
#: a gate renamed there loses its extractor loudly (KeyError-free: it just becomes UNKNOWN) rather
#: than keeping a stale key that matches nothing. A gate absent here is never guessed at.
SUBJECT_EXTRACTORS = {
    "finding-class consolidation": _subjects_finding_class,
    "level-promotion gate": _subjects_level_gate,
    "orphan-ratchet": _subjects_orphan,
    "site-lane gate": _subjects_pytest,
    RED_TEST: _subjects_pytest,
}


def _subject_at(cause, body):
    """The artefacts `cause` objected to in `body`, or None when that cannot be established.

    None is NOT an empty set and the difference is the whole discipline. The banner already told
    us this gate refused, so it printed a subject; finding none means the log's `last 40 lines`
    window cut above it. Returning `frozenset()` would make two truncated blocks compare EQUAL and
    manufacture a `SAME` verdict -- fabricating a standing red out of missing evidence, which is
    the one direction this analysis cannot survive.
    """
    fn = SUBJECT_EXTRACTORS.get(cause)
    return fn(body) if fn and body else None


SAME = "SAME"
GREW = "GREW"
SHRANK = "SHRANK"
CHANGED = "CHANGED"
UNKNOWN_SUBJECT = "UNKNOWN"
#: The verdicts that are honest ignorance rather than an answer. Held as a set for the same reason
#: `UNATTRIBUTABLE` is: a caller reporting a headline share cannot sweep it onto either side.
SUBJECT_UNKNOWN = frozenset({UNKNOWN_SUBJECT})


def subject_verdict(before, after):
    """How the subject moved between two refusals of the SAME gate."""
    if not before or not after:
        return UNKNOWN_SUBJECT
    if before == after:
        return SAME
    if before < after:          # strict subset: the old subject is still there, more arrived
        return GREW
    if after < before:          # strict subset the other way: something was repaired
        return SHRANK
    return CHANGED


def subject_report(text, ranks=None):
    """Every consecutive pair of refusals by ONE gate inside one bounded episode, classified.

    WHY PAIRS ARE PER-GATE. Two DIFFERENT gates refusing in sequence is the queueing question, and
    `ordering_report` already settled what this log can and cannot say about it. The question here
    is the one left open: when the SAME gate refuses again, is it the same complaint?

    `established` reuses the rank inference exactly as `ordering_report` states it -- an
    intervening refusal at a strictly HIGHER rank is a positive observation that this gate PASSED
    between the two, because the chain is serial and stops at the first refusal.
    """
    ranks = gate_ranks() if ranks is None else ranks
    episodes = [e for e in _episodes(cycles(text), breaker_is_landing=True) if not e["censored"]]
    pairs = []
    for e in episodes:
        causes, subs = e["cause_sequence"], e["subjects"]
        where = collections.defaultdict(list)
        for i, c in enumerate(causes):
            where[c].append(i)
        for gate, idxs in where.items():
            for i, j in zip(idxs, idxs[1:]):
                established = gate in ranks and any(
                    causes[k] in ranks and ranks[causes[k]] > ranks[gate]
                    for k in range(i + 1, j))
                pairs.append({
                    "episode_from": e["from"], "gate": gate,
                    "verdict": subject_verdict(subs[i], subs[j]),
                    "established": established,
                    # Endpoints inclusive. The analytic control in the pre-registration is keyed to
                    # this: an established pair needs a cycle strictly between its ends, so a span
                    # of 2 would mean the pairing or the rank lookup is wrong.
                    "span": j - i + 1,
                    "outage_s": e["outage_s"],
                })
    return pairs


def subject_tally(pairs):
    """Verdict counts over all pairs and over established pairs, plus the unknown bound."""
    def tally(rows):
        c = collections.Counter(p["verdict"] for p in rows)
        known = sum(v for k, v in c.items() if k not in SUBJECT_UNKNOWN)
        return {"counts": dict(c), "known": known, "total": len(rows)}

    return {"all": tally(pairs), "established": tally([p for p in pairs if p["established"]])}


# ---------------------------------------------------------------------------------------------
# WHICH TEST, not merely "a test". `RED TEST` names the GATE, and the gate is one line of the hook.
# An established re-arrival of it is two different findings wearing one label:
#
#   one control re-breaking        -> a contended or flaky control; go and find THAT test.
#   different tests in turn        -> ordinary arrival traffic from other lanes; the tree is
#                                     being broken, and no single control is at fault.
#
# Those call for opposite responses, so a mechanism built on the undivided bucket would be built
# on a number that means neither. No new instrumentation is needed: the hook block already prints
# pytest's own `FAILED <nodeid>` summary, `_subjects_pytest` already reads it via the parser the
# publisher itself uses, and `_close` already carries those sets index-aligned with the causes.
#
# THE COMPARISON IS AGAINST THE PREVIOUS RED TEST REFUSAL IN THE SAME EPISODE, never across
# episodes: an episode is bounded by a LANDING, and a landing is a positive observation that every
# gate passed. Two reds either side of one are unrelated by construction.

#: Identical node-id sets. One control, red then red again -- but see `passed_between`: identical
#: sets only demonstrate a RE-break where the gate was observed to pass in between. Without that
#: observation the same set is the cheaper explanation, persistence, and is reported as such.
SAME_TEST = "SAME TEST"
#: Sets that intersect without being equal. NOT folded into either side: it carries a re-break AND
#: other movement, and calling it one of the two would put a mixed case behind a clean headline.
SHARED_TESTS = "SHARED TESTS"
#: Disjoint sets. The gate re-broke on something else entirely -- arrival traffic.
DIFFERENT_TESTS = "DIFFERENT TESTS"
#: No earlier `RED TEST` refusal in this episode. Not ignorance and not an answer: a positive
#: observation that this redness ARRIVED here, with nothing in the episode to compare it against.
FIRST_RED = "FIRST RED IN EPISODE"
#: One of the two blocks did not retain a pytest short-summary section, so its node ids are simply
#: gone. Reported, never guessed: the `last 40 lines` window cuts above the summary often enough
#: that treating an absent summary as "no tests failed" would score a re-break as DIFFERENT TESTS.
NODE_IDS_UNAVAILABLE = "UNAVAILABLE (node ids not retained)"
#: The two rows that answer no part of the same-vs-different question. Held as a set for the same
#: reason `UNATTRIBUTABLE` and `SUBJECT_UNKNOWN` are: a caller reporting a share cannot sweep
#: either onto a side and report a split over a denominator that never earned it.
RED_TEST_UNSPLIT = frozenset({FIRST_RED, NODE_IDS_UNAVAILABLE})


def _node_id_verdict(before, after):
    """How the failing-test set moved between two `RED TEST` refusals."""
    if not before or not after:
        return NODE_IDS_UNAVAILABLE
    if before == after:
        return SAME_TEST
    return SHARED_TESTS if before & after else DIFFERENT_TESTS


def red_test_report(text, ranks=None):
    """Every established re-arrival of `RED TEST`, split by WHICH tests were failing.

    Built on `ordering_report`'s peak-rank test and not on a second definition of its own: a
    backward step is the only re-arrival this log establishes, and re-deriving it here would give
    the two reports room to disagree about which cycles are even in scope.

    `passed_between` is the STRONGER observation and is carried rather than folded in. The step
    itself says the gate passed somewhere before this cycle; `passed_between` says a strictly
    higher-ranked gate refused between THIS pair, so the serial chain reached past `RED TEST` and
    it passed *since the earlier red*. Only there does an identical set mean a control re-broke.
    Everywhere else an identical set is persistence, which is the cheaper explanation and must not
    be published as a flaky control.
    """
    ranks = gate_ranks() if ranks is None else ranks
    rows = []
    for e in ordering_report(text, ranks=ranks):
        causes, subs = e["cause_sequence"], e["subjects"]
        for step in e["backward_steps"]:
            if step["cause"] != RED_TEST:
                continue
            k = step["at"]
            prior = [j for j in range(k) if causes[j] == RED_TEST]
            if not prior:
                rows.append({"episode_from": e["from"], "at": k, "verdict": FIRST_RED,
                             "passed_between": False, "outage_s": e["outage_s"]})
                continue
            j = prior[-1]
            rows.append({
                "episode_from": e["from"], "at": k,
                "verdict": _node_id_verdict(subs[j], subs[k]),
                "passed_between": any(
                    causes[m] in ranks and ranks[causes[m]] > ranks[RED_TEST]
                    for m in range(j + 1, k)),
                "outage_s": e["outage_s"],
            })
    return rows


def red_test_tally(rows):
    """Verdict counts over all rows and over those where the gate demonstrably passed between.

    `SAME_TEST` is the ONE verdict whose plain reading is wrong, so its two halves travel with the
    count rather than in a note beside it. On its own `SAME TEST 7 (46.7%)` reads "a flaky control,
    go and find it", and on this log every one of those seven is persistence -- a standing red the
    publisher retried into, with the gate never once observed to pass between the pair. A caller
    that reports `counts` and not the halves publishes the flattering reading, and the correction
    sitting three lines below in prose is exactly the footnote a figure must not depend on.

    Keyed to the PROPERTY, not to today's zero: the day a re-break is demonstrated the row reports
    it as one, and neither half is the default the other falls through to.
    """
    def tally(subset):
        c = collections.Counter(r["verdict"] for r in subset)
        same = [r for r in subset if r["verdict"] == SAME_TEST]
        return {"counts": dict(c), "total": len(subset),
                "split": sum(v for k, v in c.items() if k not in RED_TEST_UNSPLIT),
                "same_test_rebroke": sum(1 for r in same if r["passed_between"]),
                "same_test_persisted": sum(1 for r in same if not r["passed_between"])}

    return {"all": tally(rows),
            "passed_between": tally([r for r in rows if r["passed_between"]])}


def _hours(seconds):
    return "{:.1f}h".format(seconds / 3600.0)


def _pct(n, d):
    return "n/a" if not d else "{:.1f}%".format(n / d * 100)


def _print_interval_attribution(text):
    """The MIXED bucket, decomposed onto named gates. See `interval_report` for why."""
    at = interval_attribution(text, only=(MIXED,))
    print("\n=== WHAT IS THE **MIXED** BUCKET STANDING ON? ===")
    print("MIXED is the episode `cause` field ABSTAINING, not a cause -- an episode with two")
    print("causes is attributed to neither, correctly. So the largest label we publish names no")
    print("gate. The interval between two consecutive attempts has exactly ONE observation at")
    print("each end, and an episode's intervals partition its outage EXACTLY.")
    if not at["episodes"]:
        print("\nno MIXED episodes -- nothing measured, and this is not a zero.")
        return at
    bad = (at["partition_error"], at["not_adjacent"], at["over_outage"])
    if any(bad):
        print("\nCONTROLS FAILED -- the attribution below is VOID, not merely qualified:")
        for label, xs in zip(("interval durations do not sum to the episode's outage",
                              "an interval's ends are not consecutive attempts -- an attempt "
                              "sits inside it",
                              "a gate is attributed more than its episode's whole outage"), bad):
            if xs:
                print("  {:3d}: {}".format(len(xs), label))
        return at
    print("\ncontrols: the intervals of each of the {} MIXED episodes sum to its outage to the"
          .format(at["episodes"]))
    print("second; every interval's ends are consecutive attempts, so 'nothing was observed in")
    print("between' is a property of the log; and no gate is attributed more than its episode.")
    if at["unreached_classes"]:
        print("\nCLASSES NOT REACHED in this window (never a zero -- an unreached class is an")
        print("unproven branch): {}".format(", ".join(at["unreached_classes"])))

    total = at["total_s"]
    print("\n{} MIXED episodes, {} of outage, {} intervals".format(
        at["episodes"], _hours(total), at["intervals"]))
    print("\n  {:>7}  {:>6}  {:>4}  class".format("hours", "share", "n"))
    for c in INTERVAL_CLASSES:
        print("  {:>7}  {:>6}  {:>4}  {}".format(
            _hours(at["by_class"][c]), _pct(at["by_class"][c], total), at["counts"][c], c))
    print("\n  attributed to a NAMED gate (BRACKETED + CLEARED-WITHIN): {} ({})".format(
        _hours(at["attributed_s"]), _pct(at["attributed_s"], total)))
    print("  residue, and it is named ignorance and not a bucket:      {} ({})".format(
        _hours(at["residue_s"]), _pct(at["residue_s"], total)))

    print("\nper gate. THE TWO COLUMNS ARE NOT ADDED and neither is 'how long the gate was red':")
    print("  BRACKETED    both ends observed it refusing, nothing seen in between, so the log")
    print("               holds NO EVIDENCE it cleared. Not proof it stood.")
    print("  CLEARED      the far end reached PAST it, so it demonstrably passed inside. An")
    print("               UPPER bound on how much longer it held.")
    print("  {:>9}  {:>9}  gate".format("BRACKETED", "CLEARED"))
    for gate, v in at["by_gate"].items():
        print("  {:>9}  {:>9}  {}".format(
            _hours(v[BRACKETED]), _hours(v[CLEARED_WITHIN]), gate))
    if at["re_broke"]:
        print("\ngates demonstrably RE-BROKEN inside a MASKED interval (it passed at the near end,")
        print("refused at the far one). A count of observations, never a duration -- the interval")
        print("cannot be attributed to it either:")
        for gate, n in at["re_broke"].most_common():
            print("  {:3d}  {}".format(n, gate))

    print("\nCROSS-CHECK against `ordering_report`, which reads the same backward rank move by a")
    print("different route. It walks the RANKED causes with unranked cycles skipped; an interval")
    print("with an unranked end is UNRANKABLE. So MASKED is a SUBSET, not an equal:")
    print("  MASKED episodes that ordering_report does NOT call established: {}  <- must be 0"
          .format(len(at["masked_not_established"])))
    print("  established episodes with NO masked interval:                   {}".format(
        len(at["established_without_masked"])))
    print("  the second number is the re-arrivals whose backward step is separated by an")
    print("  unattributable cycle -- real, and invisible to the interval view by construction.")
    return at


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--log", default=str(DEFAULT_LOG))
    args = ap.parse_args(argv)
    path = Path(args.log)
    if not path.exists():
        print("REFUSED: no log at {} -- nothing was measured.".format(path))
        return 2
    r = attribute(path.read_text(encoding="utf-8", errors="replace"))

    # FAIL CLOSED ON AN ABSENT SUBJECT. Every line this measures was written to the daemon's
    # WORKING copy: the log is tracked, but its committed copy was truncated to 2026-07-17 on
    # 2026-08-31. So a clean checkout, an isolated worktree, CI or a `git archive HEAD` extract
    # holds a file with no named outcome in it -- and three findings now publish
    # `python3 -m tools.commit_refusal_attribution` as their re-derivation instruction. Run from
    # one of those, this printed `0 refusals, share 0.0%, total bounded outage 0.0h`: a complete,
    # confidently formatted report that the publisher had never once failed. An absent subject
    # read as a clean result is the comfortable direction and the wrong one, so it refuses and
    # names which copy it read.
    if r["observable_from"] is None:
        print("REFUSED: {} contains no named commit outcome, so nothing here is measurable.\n"
              "  read {} attempt line(s), {} of them refused\n"
              "  The named-outcome vocabulary began 2026-08-13. A file without it is either\n"
              "  entirely older than that, or it is the COMMITTED copy -- truncated to\n"
              "  2026-07-17 on 2026-08-31. The subject is the running daemon's working copy.\n"
              "  Point --log at the shared tree's copy; do not read a zero here as a result."
              .format(path, r["attempts_lifetime"], r["refusals"]))
        return 2

    print("subject: {} ({} bytes)".format(path, path.stat().st_size))
    print("commit_refused cycles: {}".format(r["refusals"]))
    print("observable window opens: {}".format(r["observable_from"]))
    print("attempts (lifetime):   {}  -> share {}  [BLIND over its first span; NOT a rate]".format(
        r["attempts_lifetime"], _pct(r["refusals"], r["attempts_lifetime"])))
    print("attempts (observable): {}  -> share {}  <- the rate".format(
        r["attempts_observable"], _pct(r["refusals"], r["attempts_observable"])))
    print("\nrefusing gate:")
    for gate, n in sorted(r["by_gate"].items(), key=lambda kv: -kv[1]):
        print("  {:5d}  {:>6}  {}".format(n, _pct(n, r["refusals"]), gate))
    print("\nnamed red {} ({}) | non-test gate {} ({}) | unattributable {} ({})".format(
        r["red_test"], _pct(r["red_test"], r["refusals"]),
        r["non_test_gate"], _pct(r["non_test_gate"], r["refusals"]),
        r["unattributable"], _pct(r["unattributable"], r["refusals"])))
    runs = r["runs"]
    if runs:
        clustered = sum(x for x in runs if x >= 5)
        print("\n{} contiguous runs; longest {} ({} of all refusals); "
              "runs of >=5 hold {} ({})".format(
                  len(runs), runs[0], _pct(runs[0], r["refusals"]),
                  clustered, _pct(clustered, r["refusals"])))

    ep = episode_report(Path(args.log).read_text(encoding="utf-8", errors="replace"))
    print("\n=== EPISODES: what a refusal actually COSTS ===")
    print("median gap between attempts: {:.0f}s  <- outage is bounded below by this".format(
        ep["median_gap_s"]))
    print("episodes, run broken by any non-refusal: {}".format(ep["episodes_strict"]))
    print("episodes, run broken only by a LANDING:  {}  <- the cost definition".format(
        ep["episodes_cost"]))
    for e in ep["censored"]:
        print("  CENSORED episode from {} ({} cycles): outage >= {} and EXCLUDED "
              "from every figure below".format(
                  e["from"], e["cycles"], _hours(e["span_s"])))
    total = ep["total_outage_s"]
    print("\ntotal bounded outage: {} over {} episodes".format(_hours(total), len(ep["bounded"])))
    if ep["longest"]:
        lg = ep["longest"]
        print("longest single outage: {} from {} ({} cycles, {}) -> {} of all outage".format(
            _hours(lg["outage_s"]), lg["from"], lg["cycles"], lg["cause"],
            _pct(lg["outage_s"], total)))
    print("\noutage by cause (bounded episodes only):")
    for cause, xs in sorted(ep["by_cause"].items(), key=lambda kv: -sum(kv[1])):
        print("  {:3d} ep  median {:>6}  max {:>6}  total {:>7} ({:>6})  {}".format(
            len(xs), _hours(statistics.median(xs)), _hours(xs[-1]),
            _hours(sum(xs)), _pct(sum(xs), total), cause))
    print("\nmixed-cause episodes: {} of {} multi-cycle ({})".format(
        ep["mixed"], ep["multi_cycle"], _pct(ep["mixed"], ep["multi_cycle"])))

    tg = trailing_gap_report(ep)
    print("\n=== DECOMPOSITION: how much of the outage is REDNESS, how much is RHYTHM? ===")
    print("span is a LOWER bound on how long the red stood (both ends are observed refusals).")
    print("trailing gap is an UPPER bound on time lost to the retry rhythm (the red may have")
    print("cleared at any instant inside it). Neither is the quantity; the answer is which")
    print("bracket is wide. Pre-registered 2026-09-05 before this was computed once.")
    bad = (tg["negative"], tg["over_max_gap"], tg["recovery_not_adjacent"],
           tg["anchor_mismatch"])
    if any(bad):
        print("\nCONTROLS FAILED -- the decomposition below is VOID, not merely qualified:")
        for label, xs in zip(("trailing gap < 0 (anchors differ)",
                              "trailing gap > widest observed inter-attempt gap "
                              "({:.0f}s: the episode record is corrupt)".format(tg["max_gap_s"]),
                              "the recovery is not the next cycle -- an attempt was skipped",
                              "re-derived trailing gap disagrees with outage - span"), bad):
            if xs:
                print("  {:3d} episode(s): {}".format(len(xs), label))
                for r in xs[:5]:
                    print("      from {}  span {}  outage {}  gap {:.0f}s".format(
                        r["from"], _hours(r["span_s"]), _hours(r["outage_s"]),
                        r["trailing_gap_s"]))
    else:
        print("\ncontrols on all {} bounded episodes: trailing gap >= 0; the recovery is the NEXT"
              .format(len(tg["rows"])))
        print("cycle, so the gap spans no uncounted attempt; and the gap equals a re-derivation")
        print("from the episode's own two timestamps, so span and outage share their anchor.")
        print("(A trailing gap is one of the gaps `max_gap_s` is taken over, so comparing it to")
        print(" that maximum -- {:.0f}s here -- cannot fail and is a record canary, not evidence.)"
              .format(tg["max_gap_s"]))
    if tg["not_ending_on_refusal"]:
        print("\n{} bounded episode(s) end on a NON-refusal attempt, so their trailing gap runs"
              .format(len(tg["not_ending_on_refusal"])))
        print("from that attempt and not from the last refusal. Both are carried per episode; the")
        print("figures below use the last ATTEMPT, which is what `outage - span` means.")
    for label, s in (("MULTI-CYCLE  <- the headline", tg["multi"]),
                     ("SINGLE-CYCLE <- span 0 BY CONSTRUCTION; 100% trailing gap is an identity "
                      "of\n                the episode definition, not an observation. Never "
                      "pooled above.", tg["single"])):
        print("\n{}".format(label))
        if not s["episodes"]:
            print("  no episodes -- nothing measured, and this is not a zero.")
            continue
        print("  {} episodes, total outage {}".format(s["episodes"], _hours(s["outage_s"])))
        print("    span (redness stood, LOWER bound):  {:>8}  {:>6}".format(
            _hours(s["span_s"]), _pct(s["span_s"], s["outage_s"])))
        print("    trailing gap (rhythm, UPPER bound): {:>8}  {:>6}".format(
            _hours(s["trailing_gap_s"]), _pct(s["trailing_gap_s"], s["outage_s"])))
        print("    median trailing gap {} | max {}  (median gap between attempts: {:.0f}s)".format(
            _hours(s["median_trailing_gap_s"]), _hours(s["max_trailing_gap_s"]),
            ep["median_gap_s"]))
    all_outage = tg["multi"]["outage_s"] + tg["single"]["outage_s"]
    print("\nsingle-cycle share of ALL bounded outage: {}  <- cost the rhythm owns by definition"
          .format(_pct(tg["single"]["outage_s"], all_outage)))

    ordered = [e for e in ordering_report(
        Path(args.log).read_text(encoding="utf-8", errors="replace")) if e["cause"] == MIXED]
    mixed_outage = sum(e["outage_s"] for e in ordered)
    est = [e for e in ordered if e["established"]]
    oc = [e for e in ordered if not e["established"]]
    print("\n=== ORDERING: did a gate RE-BREAK, or is the firing order faking it? ===")
    print("the chain is serial and stops at the first refusal, so a cycle naming rank r is a")
    print("positive observation that every gate below r PASSED. A later cycle naming a LOWER")
    print("rank is a gate that passed and then refused. A FORWARD step establishes nothing --")
    print("a queue and a set of gates red from the start are indistinguishable here.")
    print("\nESTABLISHED re-arrival: {} of {} mixed episodes, {} of mixed outage ({})".format(
        len(est), len(ordered), _hours(sum(e["outage_s"] for e in est)),
        _pct(sum(e["outage_s"] for e in est), mixed_outage)))
    print("ORDER-CONSISTENT (cannot tell from simultaneous redness): {}, {} ({})".format(
        len(oc), _hours(sum(e["outage_s"] for e in oc)),
        _pct(sum(e["outage_s"] for e in oc), mixed_outage)))
    concealed = [e for e in est if not e["recurrence"]]
    print("\nof which the contiguous-block test MISSES {}: a cause appearing once, at a rank "
          "below\none already reached, is a re-arrival that no recurrence test can see.".format(
              len(concealed)))
    for e in sorted(ordered, key=lambda x: -x["outage_s"])[:5]:
        print("  {:>6}  {:3d}cyc  {:<18}  {}".format(
            _hours(e["outage_s"]), e["cycles"],
            "ESTABLISHED" if e["established"] else "order-consistent",
            " -> ".join(c.split(" (")[0] for c in e["cause_sequence"][:6])))

    _print_interval_attribution(Path(args.log).read_text(encoding="utf-8", errors="replace"))

    exposure = masking_exposure(Path(args.log).read_text(encoding="utf-8", errors="replace"))
    refused_cycles = sum(1 for c in cycles(
        Path(args.log).read_text(encoding="utf-8", errors="replace"))
        if c["outcome"] == "commit_refused")
    print("\n=== WHAT THE SAME EARLY EXIT COSTS THE CAUSE SPLIT ===")
    print("`by_gate` above is a distribution of FIRST failing gate. Each count is a LOWER bound")
    print("and the bias is monotone in chain position. Over {} refused cycles:".format(
        refused_cycles))
    print("  {:<34} {:>6} {:>8} {:>8}".format("gate (in chain order)", "named", "PROVEN", "unknown"))
    print("  {:<34} {:>6} {:>8} {:>8}".format("", "", "passing", ""))
    for gate, row in sorted(exposure.items(), key=lambda kv: kv[1]["rank"]):
        print("  {:<34} {:6d} {:8d} {:8d}".format(
            gate.split(" (")[0][:34], row["named"], row["proven_passing"], row["unknown"]))
    blind = [g for g, row in exposure.items() if row["named"] == 0 and row["proven_passing"] == 0]
    if blind:
        print("\n{} gate(s) have NO observation of any kind in this window -- never named,".format(
            len(blind)))
        print("never proven passing. For these 'it never refused a publish' is not an")
        print("observation about the gate; it is unobservable:")
        for gate in sorted(blind, key=lambda g: exposure[g]["rank"]):
            print("  {} (unknown on all {} refused cycles)".format(gate, exposure[gate]["unknown"]))

    pairs = subject_report(path.read_text(encoding="utf-8", errors="replace"))
    t = subject_tally(pairs)
    print("\n=== SUBJECT: when a gate refuses AGAIN, is it the SAME complaint? ===")
    print("every gate prints the artefact it objected to, so the log DOES say what changed.")
    print("SAME = a STANDING RED nobody is working; the publisher retries into it on its own")
    print("rhythm. CHANGED/GREW = an ARRIVAL STREAM from other lanes. Opposite remedies.")
    for label in ("all", "established"):
        row = t[label]
        print("\n{} pairs: {} ({} with an extractable subject)".format(
            "ALL same-gate" if label == "all" else "ESTABLISHED (gate demonstrably PASSED between)",
            row["total"], row["known"]))
        for v, n in sorted(row["counts"].items(), key=lambda kv: -kv[1]):
            base = "of extractable" if v not in SUBJECT_UNKNOWN else "of all pairs"
            print("  {:5d}  {:>6} {}  {}".format(
                n, _pct(n, row["total"] if v in SUBJECT_UNKNOWN else row["known"]), base, v))
    rows = red_test_report(path.read_text(encoding="utf-8", errors="replace"))
    rt = red_test_tally(rows)
    print("\n=== RED TEST, SPLIT BY WHICH TEST: one control re-breaking, or the tree moving? ===")
    print("RED TEST names the GATE, so an established re-arrival of it is two different findings")
    print("wearing one label. ONE control re-breaking is a contended or flaky test to go and find;")
    print("DIFFERENT tests in turn is arrival traffic from other lanes and no control's fault.")
    for label, note in (("all", "every established RED TEST re-arrival"),
                        ("passed_between",
                         "and a higher gate refused BETWEEN the pair, so RED TEST passed since")):
        row = rt[label]
        print("\n{}: {} ({} answer the same-vs-different question)".format(
            note, row["total"], row["split"]))
        for v, n in sorted(row["counts"].items(), key=lambda kv: -kv[1]):
            base = "of splittable" if v not in RED_TEST_UNSPLIT else "of all steps"
            # The bound goes ON the row it inverts. A reader who quotes the SAME TEST count and
            # stops has quoted "a flaky control" out of evidence that says the opposite.
            note = "" if v != SAME_TEST else "   [{} demonstrably re-broke, {} persistence]".format(
                row["same_test_rebroke"], row["same_test_persisted"])
            print("  {:5d}  {:>6} {}  {}{}".format(
                n, _pct(n, row["total"] if v in RED_TEST_UNSPLIT else row["split"]), base, v, note))
    # Read off the tally rather than re-counted from `rows`: two derivations of one figure are
    # two figures, and this file exists because two such figures were once added together.
    print("\nwithout the between-observation an identical set is PERSISTENCE, not a re-break:")
    print("  {} of the {} SAME TEST steps carry it.".format(
        rt["all"]["same_test_rebroke"],
        rt["all"]["same_test_rebroke"] + rt["all"]["same_test_persisted"]))

    by_gate = collections.defaultdict(collections.Counter)
    for p in pairs:
        by_gate[p["gate"]][p["verdict"]] += 1
    print("\nby gate (pairs):")
    for gate, c in sorted(by_gate.items(), key=lambda kv: -sum(kv[1].values())):
        print("  {:5d}  {:<32} {}".format(
            sum(c.values()), gate.split(" (")[0],
            "  ".join("{} {}".format(v, n) for v, n in sorted(c.items()))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
