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
"""

from __future__ import annotations

import argparse
import collections
import re
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
        near = [b for b in blocks if b[1] <= i and i - b[1] <= 3]
        if not near:
            key = NO_BLOCK
        else:
            b = max(near, key=lambda x: x[1])
            body = "\n".join(lines[b[0]:b[1]])
            key = _parse_refusing_gate(body) or (
                RED_TEST if _RED_TEST.search(body) else UNNAMED)
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
