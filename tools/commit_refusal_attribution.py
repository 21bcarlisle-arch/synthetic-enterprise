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

from background.process_run_complete import _parse_refusing_gate

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


def _cause_at(lines, blocks, i):
    """Which gate refused the `commit_refused` line at `lines[i]`. Fail-closed on ignorance."""
    # The hook block sits immediately above its verdict; anything further away belongs to a
    # different cycle and is not evidence about this one.
    near = [b for b in blocks if b[1] <= i and i - b[1] <= 3]
    if not near:
        return NO_BLOCK
    b = max(near, key=lambda x: x[1])
    body = "\n".join(lines[b[0]:b[1]])
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
            out.append({"at": stamp, "outcome": LANDED, "cause": None})
            continue
        named = _NAMED_OUTCOME.search(line)
        if named and out:
            out[-1]["outcome"] = named.group(1)
            if REFUSAL_NEEDLE in line:
                out[-1]["cause"] = _cause_at(lines, blocks, i)
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
    refused = [c for c in members if c["outcome"] == "commit_refused"]
    start = _parse_ts(members[0]["at"])
    last = _parse_ts(members[-1]["at"])
    after = seq[cur[-1][0] + 1:]
    recovery = next((c for c in after if c["outcome"] == LANDED), None)
    causes = sorted({c["cause"] for c in refused if c["cause"]})
    return {
        "from": members[0]["at"],
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


def _hours(seconds):
    return "{:.1f}h".format(seconds / 3600.0)


def _pct(n, d):
    return "n/a" if not d else "{:.1f}%".format(n / d * 100)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--log", default=str(DEFAULT_LOG))
    args = ap.parse_args(argv)
    r = attribute(Path(args.log).read_text(encoding="utf-8", errors="replace"))

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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
