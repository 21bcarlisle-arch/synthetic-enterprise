#!/usr/bin/env python3
"""THE STANDING-RED LEDGER — a red that keeps refusing the publisher becomes WORK, not a retry.

WHY THIS EXISTS. Five measurements name one subject and agree:

  * 82.9% of multi-cycle publish outage is redness STANDING, not the retry rhythm (988270c2e).
  * 77.8% of same-gate re-refusals are the IDENTICAL complaint, and one red was retried 24 times.
  * 0 of 7 SAME-TEST re-arrivals demonstrably re-broke -- all seven were persistence.
  * RED TEST alone is 67.8h of bracketed outage, 28.3% of ALL bounded outage, against 5.1h for
    the next gate (e0cc653c9).

And nothing anywhere acts on it. The publisher already KNOWS: `_record_commit_refusal_reds` parses
the failing node ids out of the hook chain's own output and writes them to
`.last_gate_blocking_tests.json`. But that file is a SNAPSHOT -- overwritten every cycle, deleted on
green -- so a red that has refused twenty-four consecutive cycles is indistinguishable, at every
reader in the system, from one that broke a minute ago. There is no AGE, so there is no escalation,
so the publisher retries into the same red on a rhythm that by measurement cannot clear it.

WHAT THIS IS. The same three properties the director required of the HEAD-red register -- a named
subject, a live baseline, and an end state where zero means zero -- applied to the OTHER red: the
one the publisher meets in the pre-commit hook chain and discards.

WHY IT IS NOT `background/head_red_register`, which is the nearest thing and was read first. Two of
that module's load-bearing rules are WRONG here, and adopting either would be a fail-open:

  * ITS POPULATION. `runs_red` counts nightly HEAD-green census runs. This counts publish cycles.
    Folding one into the other gives a number whose denominator is two different things, which is
    the *average unit rate* shape this project keeps paying for.
  * ITS ABSENCE RULE. `record()` sets `currently_red = False` for every test NOT in the failing
    set, which is correct for a census: the census runs the whole suite, so absence IS evidence of
    green. The hook chain runs FAIL-FAST. Absence there is evidence of nothing -- a refusal naming
    test B does not make test A green, it means pytest stopped before reaching it. Reusing that
    rule would let one fail-fast refusal mark eight hundred tests fixed.

So the store is separate and its rules are stated in its own terms. What IS reused: `by_module`
from that register (generic over node ids), and the whole draw/render shape, deliberately -- a
reader who knows one register can read this one.

THE ONE ASYMMETRY, and it is the design. Appearing in a refusal ADDS to a node's age. Not appearing
in a refusal does NOTHING. The only thing that discharges a node is the hook chain PASSING -- a
`git commit` that returns 0 through the same chain that refused. Not a green scoped gate (a
different suite, different scope), not age, not a quiet cycle. That asymmetry means the ledger can
over-report a red that was fixed by a commit that never happened, and can never under-report one
that is still blocking. Fail direction: toward naming work.

ZERO MEANS ZERO, enforced and not promised. `drawable()` is empty whenever nothing is standing, so
a healthy publisher parks no permanent item in the draw; and a landing empties the ledger in one
act, so the exit is real rather than a disposition paragraph.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
LEDGER_PATH = PROJECT_DIR / "docs" / "observability" / "publish_standing_reds.json"
REGISTER_NAME = "PUBLISH_STANDING_RED_REGISTER.md"
REGISTER_PATH = PROJECT_DIR / "docs" / "staging" / "reference" / REGISTER_NAME

#: How many refusal cycles naming the SAME node id, with no landing between them, make it a
#: STANDING red rather than a fresh break.
#:
#: TWO, AND ITS ORIGIN IS A MEASUREMENT. `e0cc653c9` asked of every same-test re-arrival in the
#: retained runner log whether it demonstrably re-broke, and the answer was **0 of 7** -- every
#: one was persistence of a red that had never been fixed. `988270c2e` found 77.8% of same-gate
#: re-refusals carrying the identical complaint. So the observed base rate of "the second refusal
#: naming this test is a NEW failure" is zero out of seven, and there is no evidence anywhere in
#: this project for a higher threshold. A larger number would be a value picked because a value
#: was needed, which is the shape CLAUDE.md's knowledge-first rule exists to refuse.
#:
#: It is not a dial and it does not want tuning against a replay: the replay was pre-registered
#: with this value already fixed (SEAT_PREREGISTRATION_WHAT_A_STANDING_RED_LEDGER_WOULD_HAVE_
#: ESCALATED_OVER_THE_REAL_LOG_2026-09-05.md) precisely so it could not be.
STANDING_AFTER_CYCLES = 2

#: How many standing reds the register names in full before it elides -- and it says so when it
#: does. Same rule as the HEAD-red register: a summary that hides its own truncation turns a named
#: subject back into a count.
MAX_LISTED = 100


def _now_iso(now: datetime | None = None) -> str:
    return (now or datetime.now(timezone.utc)).replace(microsecond=0).isoformat()


def node_key(line: str) -> str:
    """The NODE ID out of a pytest short-summary line. The identity this ledger ages on.

    CAUGHT WHILE WIRING THIS UP, and it is the whole reason this function exists rather than the
    raw string being used. `_parse_failed_node_ids` returns the FULL summary line --
    `FAILED tests/x.py::test_y - AssertionError: 0.31 != 0.29` -- and that is right for the
    snapshot, which wants the message. It is fatally wrong as an IDENTITY: any red whose assertion
    text carries a varying number (an elapsed time, a measured figure, a count, a temp path) would
    produce a different string every cycle and could never age past one.

    That is not a hypothetical. It is `alarm_repetition`'s founding incident re-entered through a
    different door: six identical pages that no dedup could catch because each carried
    `after {elapsed:.0f}s`, making 252s / 255s / 253s three unique strings. A ledger built to
    detect "the same red, again" that keys on a string containing the failure's own output would
    be blind to exactly the reds that recur -- and would look like it was working, because it
    would still fill up.

    The message is not discarded; it is kept per-row as `last_detail`, where a reader can see it
    and no counter is keyed to it.
    """
    text = str(line or "").strip()
    for verb in ("FAILED ", "ERROR "):
        if text.startswith(verb):
            text = text[len(verb):]
            break
    return text.split(" - ", 1)[0].strip()


# ── the store ────────────────────────────────────────────────────────────────────────────────
def empty_ledger() -> dict:
    return {"tests": {}, "refusals": 0, "landings": 0, "discharged": []}


def load_ledger(path: Path | None = None) -> dict:
    """The ledger, or an empty one.

    A missing or unreadable store is EMPTY, and the fail direction is deliberate and the OPPOSITE
    of the HEAD-red register's. There, an unreadable store loses ages and every red reads as new,
    which is noisier but never quieter. Here an empty ledger reports LESS work, so it is the
    dangerous direction -- and it is still the right one, because the alternative (treat unreadable
    as "something is standing") would escalate a subject the ledger cannot name, and an escalation
    with no node id in it is the wallpaper this replaces. An unreadable ledger is repopulated by
    the very next refusal, which is at most one publish cycle away.
    """
    try:
        data = json.loads((path or LEDGER_PATH).read_text())
    except (OSError, ValueError):
        return empty_ledger()
    if not isinstance(data, dict) or not isinstance(data.get("tests"), dict):
        return empty_ledger()
    base = empty_ledger()
    base.update(data)
    return base


def save_ledger(ledger: dict, path: Path | None = None) -> None:
    p = path or LEDGER_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n")


# ── the two acts ─────────────────────────────────────────────────────────────────────────────
def record_refusal(node_ids, *, git_hash=None, now=None, ledger=None) -> dict:
    """Fold one publish commit-refusal into the ledger and return the new ledger.

    PURE apart from its default argument -- the caller saves it. That is what lets the whole
    ageing and discharge rule be tested without a filesystem or a publisher.

    A refusal naming NO node id is still a refusal and still counted in `refusals`, but folds
    nothing into `tests`. That is a fact about the refusal, not a gap: a non-test gate
    (orphan-ratchet, finding-class, level-promotion) refuses without any test returning a verdict,
    and inventing a subject for it is exactly how five GREEN tests came to be named as the blockers
    of an orphan-ratchet refusal on 2026-09-02.
    """
    ledger = empty_ledger() if ledger is None else ledger
    stamp = _now_iso(now)
    tests = ledger.setdefault("tests", {})
    ledger["refusals"] = int(ledger.get("refusals") or 0) + 1
    seen: dict[str, str] = {}
    for raw in (node_ids or ()):
        key = node_key(raw)
        if key:
            seen.setdefault(key, str(raw).strip())
    for node in sorted(seen):
        row = tests.setdefault(node, {"first_blocked": stamp, "cycles_blocked": 0})
        row["cycles_blocked"] = int(row.get("cycles_blocked") or 0) + 1
        row["last_blocked"] = stamp
        row["last_detail"] = seen[node]
        row.setdefault("first_blocked", stamp)
        if git_hash:
            row["last_head"] = str(git_hash)
    ledger["_doc"] = (
        "MACHINE-WRITTEN by background/publish_standing_red on every publish commit refusal that "
        "named a red test. `cycles_blocked` counts publish REFUSAL CYCLES since the last observed "
        "landing in which the hook chain named this test -- NOT consecutive ones, because the hook "
        "chain is fail-fast and absence from a later refusal proves nothing. The ONLY discharge is "
        "the hook chain passing (record_landing)."
    )
    return ledger


def record_landing(*, git_hash=None, now=None, ledger=None) -> dict:
    """The hook chain PASSED, so every tracked red is discharged. Returns the new ledger.

    THIS IS THE ONLY EXIT and it is one act, not a judgement. A commit that returns 0 ran the same
    chain that refused, over the same tree, so nothing it did not stop can still be stopping it.

    What was standing is kept in `discharged` with its final age, capped, because "this red stood
    nine cycles and then cleared" is the evidence that the ledger's own counting was real -- a
    store that deletes on discharge can show a reader neither that nor the fact that it ever
    reduced. It is a RECORD, not a queue: nothing draws from it.
    """
    ledger = empty_ledger() if ledger is None else ledger
    stamp = _now_iso(now)
    tests = ledger.get("tests") or {}
    ledger["landings"] = int(ledger.get("landings") or 0) + 1
    if tests:
        rows = [{"node": n, "cycles_blocked": int(r.get("cycles_blocked") or 0),
                 "first_blocked": r.get("first_blocked"), "cleared_at": stamp,
                 "cleared_head": str(git_hash) if git_hash else None}
                for n, r in sorted(tests.items())]
        history = list(ledger.get("discharged") or []) + rows
        ledger["discharged"] = history[-MAX_LISTED:]
    ledger["tests"] = {}
    ledger["last_landing"] = stamp
    return ledger


# ── what is STANDING ─────────────────────────────────────────────────────────────────────────
def standing(ledger: dict, threshold: int = STANDING_AFTER_CYCLES) -> list[str]:
    """Node ids that have refused the publisher `threshold` or more cycles, oldest debt first.

    Two populations named apart rather than differenced: everything in `tests` has refused the
    publisher AT LEAST ONCE, and only this subset has refused it enough times that the evidence
    calls it persistence. The first is a fact about one cycle; the second is the escalation.
    """
    tests = ledger.get("tests") or {}
    hits = [(n, int(r.get("cycles_blocked") or 0)) for n, r in tests.items()
            if int(r.get("cycles_blocked") or 0) >= int(threshold)]
    return [n for n, _ in sorted(hits, key=lambda kv: (-kv[1], kv[0]))]


def worst(ledger: dict) -> int:
    """The largest cycles_blocked in the ledger, or 0. The headline the snapshot could not hold."""
    tests = ledger.get("tests") or {}
    return max((int(r.get("cycles_blocked") or 0) for r in tests.values()), default=0)


# ── the register document ────────────────────────────────────────────────────────────────────
def render(ledger: dict, *, threshold: int = STANDING_AFTER_CYCLES, now=None) -> str:
    """The register. Names every standing subject it can, and says so where it cannot."""
    from background.head_red_register import by_module

    nodes = standing(ledger, threshold)
    tests = ledger.get("tests") or {}
    lines = [
        "# [REGISTER] Reds that are standing in the publish path",
        "",
        "**Severity:** {} · **Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted".format(
            "BLOCKING" if nodes else "RECORDED"),
        "",
        "**THIS IS A REGISTER, NOT A QUEUE ITEM. Do not archive it.** It is re-rendered in place "
        "by `background/publish_standing_red` on every publish commit refusal. You action it by "
        "MAKING THE TEST GREEN. There is no acceptance list and no disposition: a red that is "
        "refusing the publisher cannot be forgiven the way a red at HEAD can, because the cost is "
        "not hypothetical -- it is publish outage, and it is being paid every cycle this list is "
        "not empty.",
        "",
        "A test may appear here AND in `HEAD_RED_REGISTER.md`. That is not double-counting: that "
        "register asks what is broken at HEAD, this one asks what is DEMONSTRABLY blocking "
        "publication and for how long, and a red can be either without being the other.",
        "",
    ]

    if not tests and not ledger.get("refusals"):
        lines += ["## Nothing has been observed", "",
                  "No publish refusal has been folded in, which is NOT a claim that the publish "
                  "path is clear.", ""]
        return "\n".join(lines)

    lines += [
        "## The count, with each number's population named",
        "",
        "| | |",
        "|---|---:|",
        "| tests that refused the publisher at least once, since the last landing | {} |".format(
            len(tests)),
        "| **standing — {}+ refusal cycles, no landing between** | **{}** |".format(
            threshold, len(nodes)),
        "| longest-standing, in refusal cycles | **{}** |".format(worst(ledger)),
        "| refusals folded in | {} |".format(ledger.get("refusals") or 0),
        "| landings observed | {} |".format(ledger.get("landings") or 0),
        "",
        "Last landing: {}.".format(ledger.get("last_landing") or "none observed"),
        "",
    ]

    if not nodes:
        lines += ["## ZERO MEANS ZERO", "",
                  "No red has refused the publisher {} or more times since it last landed. This "
                  "register is not drawn while this line is here.".format(threshold), ""]
        return "\n".join(lines) + _discharged(ledger) + "\n"

    lines += [
        "## The {} standing, longest-blocking first".format(len(nodes)),
        "",
        "`cycles` is publish refusal cycles since the last landing in which the pre-commit hook "
        "chain named this test. It is not a count of CONSECUTIVE cycles: the chain is fail-fast, "
        "so a cycle that named a different test says nothing about this one. Retrying will not "
        "clear any of these — 0 of 7 same-test re-arrivals in the runner log ever re-broke, so "
        "every one measured was persistence.",
        "",
        "| test | cycles | first blocked |",
        "|---|---:|---|",
    ]
    for node in nodes[:MAX_LISTED]:
        row = tests.get(node, {})
        lines.append("| `{}` | {} | {} |".format(
            node, row.get("cycles_blocked", "?"), str(row.get("first_blocked", "?"))[:16]))
    if len(nodes) > MAX_LISTED:
        lines.append("")
        lines.append("… {} more not listed. **Every one is in "
                     "`docs/observability/publish_standing_reds.json`**, which is the store this "
                     "table is rendered from.".format(len(nodes) - MAX_LISTED))

    grouped = by_module(nodes)
    if len(grouped) < len(nodes):
        lines += ["", "## By module", "",
                  "Where a whole module is standing, the cause is usually one thing — a conftest, "
                  "an import, a fixture — and not N separate defects.", "",
                  "| module | standing |", "|---|---:|"]
        for module, mods in sorted(grouped.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:20]:
            lines.append("| `{}` | {} |".format(module, len(mods)))

    return "\n".join(lines) + _discharged(ledger) + "\n"


def _discharged(ledger: dict) -> str:
    rows = list(ledger.get("discharged") or [])[-10:]
    if not rows:
        return ""
    out = ["", "", "## Recently discharged — the ledger reducing, which is the point", "",
           "| test | cycles it stood | cleared |", "|---|---:|---|"]
    for r in rows:
        out.append("| `{}` | {} | {} |".format(
            r.get("node", "?"), r.get("cycles_blocked", "?"), str(r.get("cleared_at", "?"))[:16]))
    return "\n".join(out)


def write_register(ledger: dict, *, path: Path | None = None,
                   threshold: int = STANDING_AFTER_CYCLES, now=None) -> Path:
    p = path or REGISTER_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(render(ledger, threshold=threshold, now=now))
    return p


# ── the two entry points the publisher calls ─────────────────────────────────────────────────
def note_refusal(node_ids, git_hash=None, *, ledger_path=None, register_path=None) -> list[str]:
    """Fold a refusal, persist, re-render. Returns the standing set. NEVER RAISES.

    A diagnostic must never red the path it observes -- the publisher is mid-refusal when this
    runs, and a ledger that took the publish cycle down would be strictly worse than no ledger.
    """
    try:
        ledger = record_refusal(node_ids, git_hash=git_hash, ledger=load_ledger(ledger_path))
        save_ledger(ledger, ledger_path)
        write_register(ledger, path=register_path)
        return standing(ledger)
    except Exception:  # noqa: BLE001 -- see the docstring; observing must not break the observed
        return []


def note_landing(git_hash=None, *, ledger_path=None, register_path=None) -> int:
    """Discharge the ledger on a passing hook chain, persist, re-render. NEVER RAISES.

    Returns how many tests were discharged -- 0 when the ledger was already empty, which is the
    steady state of a healthy publisher and not a failure.
    """
    try:
        before = load_ledger(ledger_path)
        n = len(before.get("tests") or {})
        ledger = record_landing(git_hash=git_hash, ledger=before)
        save_ledger(ledger, ledger_path)
        write_register(ledger, path=register_path)
        return n
    except Exception:  # noqa: BLE001 -- as above
        return 0


# ── the draw ─────────────────────────────────────────────────────────────────────────────────
def drawable(root: Path | str | None = None) -> list[str]:
    """The standing set, for `staging_rooms` to decide whether this register is WORK.

    Non-empty means the register is drawn. Never raises: a draw that cannot rank its own work must
    still see the rest of the queue, the same fail-open its two siblings take and for the same
    reason -- what is lost by returning early is one promotion; what would be lost by raising is
    the whole queue.
    """
    try:
        return standing(load_ledger())
    except Exception:  # noqa: BLE001
        return []


# ── the historical replay ────────────────────────────────────────────────────────────────────
def replay(log_text: str, *, threshold: int = STANDING_AFTER_CYCLES) -> dict:
    """Run the retained runner log through this ledger and report what it WOULD have escalated.

    Pre-registered before it was written (SEAT_PREREGISTRATION_WHAT_A_STANDING_RED_LEDGER_WOULD_
    HAVE_ESCALATED_OVER_THE_REAL_LOG_2026-09-05.md), with the threshold already fixed, so no
    number below can have been tuned to make the answer flattering.

    It reads the log through `commit_refusal_attribution.cycles`, which is the publisher's OWN
    parser reached through the module that already owns the log's vocabulary. A private reader
    here would drift from the gates it names and the drift would be invisible.

    ONE HONEST LIMIT, stated rather than smoothed. `cycles()` reports `subject: None` -- not an
    empty set -- when the log's retained 40-line window cut above the summary. Those refusals are
    counted in `unknown_subject` and fold NOTHING, so the replay's ages are a LOWER BOUND on what
    the live ledger will see. The live path does not have this limit: it reads both streams in
    full at the moment of refusal, which is exactly the buffer the log truncates.
    """
    from tools.commit_refusal_attribution import LANDED, RED_TEST, cycles

    ledger, peak, escalations, unknown = empty_ledger(), {}, 0, 0
    discharges, non_empty_discharges, folded_nothing = 0, 0, 0
    for cyc in cycles(log_text):
        if cyc["outcome"] == LANDED:
            if ledger.get("tests"):
                non_empty_discharges += 1
            discharges += 1
            ledger = record_landing(ledger=ledger)
            continue
        if cyc["cause"] == RED_TEST and cyc["subject"] is None:
            unknown += 1
        was = set(standing(ledger, threshold))
        subject = (sorted(cyc["subject"])
                   if cyc["cause"] == RED_TEST and cyc["subject"] else [])
        if not subject:
            folded_nothing += 1
        ledger = record_refusal(subject, ledger=ledger)
        escalations += len(set(standing(ledger, threshold)) - was)
        for node, row in (ledger.get("tests") or {}).items():
            peak[node] = max(peak.get(node, 0), int(row.get("cycles_blocked") or 0))
    return {
        "threshold": threshold,
        "escalated_nodes": sorted(peak, key=lambda n: (-peak[n], n))[:20],
        "escalated_distinct": sum(1 for v in peak.values() if v >= threshold),
        "escalation_events": escalations,
        "worst_cycles_blocked": max(peak.values(), default=0),
        "landings_seen": discharges,
        "landings_that_discharged_something": non_empty_discharges,
        "red_test_refusals_with_no_readable_subject": unknown,
        # A non-test gate refuses without any test returning a verdict, so it HAS no test subject
        # and must fold none. If this is ever zero the parser is finding tests where there are
        # none, which is worse than finding none -- see `record_refusal`.
        "refusals_that_folded_no_subject": folded_nothing,
        "refusals_folded": ledger.get("refusals") or 0,
        "peak": peak,
    }


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description="The standing-red ledger: reds that keep refusing the publisher.")
    ap.add_argument("--render", action="store_true", help="(re)write the register document")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--replay", metavar="LOG", nargs="?",
                    const="docs/observability/sim-runner-log.md",
                    help="replay a retained runner log through this ledger and print what it "
                         "would have escalated (the pre-registered measurement)")
    args = ap.parse_args(argv)
    if args.replay:
        rep = replay(Path(args.replay).read_text(errors="replace"))
        nodes = rep.pop("escalated_nodes")
        peak = rep.pop("peak")
        print(json.dumps(rep, indent=2))
        print("\nTop standing reds, by the most cycles they ever stood:")
        for n in nodes:
            print("  {:>3}  {}".format(peak[n], n))
        return 0
    ledger = load_ledger()
    nodes = standing(ledger)
    if args.render:
        print("wrote {}".format(write_register(ledger)))
    if args.json:
        print(json.dumps({"standing": nodes, "worst": worst(ledger),
                          "tracked": len(ledger.get("tests") or {}),
                          "refusals": ledger.get("refusals") or 0,
                          "landings": ledger.get("landings") or 0}, indent=2))
    else:
        print("PUBLISH STANDING RED: {} standing of {} tracked, worst {} cycle(s)".format(
            len(nodes), len(ledger.get("tests") or {}), worst(ledger)))
    return 1 if nodes else 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
