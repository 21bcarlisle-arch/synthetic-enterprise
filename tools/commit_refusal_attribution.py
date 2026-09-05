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

from background.process_run_complete import _REFUSING_GATE_BANNERS, _parse_refusing_gate

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
        seq = [(c, ranks[c]) for c in e["cause_sequence"] if c in ranks]
        steps, seen, peak = [], [], None
        for cause, rk in seq:
            if peak is not None and rk < peak:
                steps.append({"cause": cause, "below": peak})
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


def _hours(seconds):
    return "{:.1f}h".format(seconds / 3600.0)


def _pct(n, d):
    return "n/a" if not d else "{:.1f}%".format(n / d * 100)


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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
