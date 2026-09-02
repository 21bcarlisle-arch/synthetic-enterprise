#!/usr/bin/env python3
"""THE HEAD-RED REGISTER — a route into the draw for tests that are red at HEAD.

WHY THIS EXISTS (director, 2026-09-02): *"Why hasn't the 830 been fixed? My reading: the
HEAD-green census reports and nothing draws it. Twelve, seventeen, thirty-three and now 830 —
each announced, none worked, while everything with a route into the draw gets done. Same shape
as the reaper built in July and never called. … Red tests at HEAD need a way into the queue with
the same standing as a class register — a named subject, a live baseline, and an end state where
zero means zero."*

He is right on all three counts, and each was a distinct defect:

**A NAMED SUBJECT.** The census pages a COUNT and names ten tests out of 830. There is nothing
in that message a person can pick up and fix — only a number to worry about. Its full list went
to a systemd journal that nothing reads and no artefact kept.

**A LIVE BASELINE.** `head_red_baseline.json` was written 2026-08-12 and never touched since. It
contains `known_red: []`. So "830 NEWLY failing" has never meant a delta at all: with an empty
acceptance list every red is "new", every night, forever. The word `newly` was false in every
message the control has ever sent, including the four the director just listed back.

**ZERO MEANS ZERO.** Nothing here ever reduced. The census observed, alarmed, and discarded its
own output; the observation was not persisted, so no test had an AGE, no red had a subject, and
no state existed from which "fixed" could be read.

THE ONE PROPERTY THIS MUST NOT BREAK, and it is the reason the design splits in two.
`head_red_baseline.json`'s own docstring says it: *"NOTHING WRITES THIS FILE AUTOMATICALLY: a
control that absorbs its own new failures into its own baseline cannot fail."* That is exactly
right and it stays. So there are two stores and they are different KINDS of thing:

    OBSERVATION  (this module, machine-written, live)   what IS red, and for how long
    ACCEPTANCE   (head_red_baseline.json, human, rare)  what we have DECIDED to live with

A machine may write what it saw. Only a person may write what is forgiven. The draw pressure
comes from the observation, so the machine can never quiet itself by observing.

THE EXIT, AND WHY THERE IS NO DISPOSITION SECTION HERE. A class register is actioned by writing
a DECISION into it, because a finding class is a judgement about a pattern. A red test is not:
it is either fixed, or it is accepted BY NAME with a reason on the acceptance list. Giving this
register a blanket "disposition" would let one paragraph retire 830 subjects, which is the
wallpaper the census was already producing. So the only two exits are per-test and both are
real acts. **That is what makes zero mean zero.**
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
OBSERVED_PATH = PROJECT_DIR / "docs" / "observability" / "head_red_observed.json"
REGISTER_NAME = "HEAD_RED_REGISTER.md"
REGISTER_PATH = PROJECT_DIR / "docs" / "staging" / "reference" / REGISTER_NAME

#: How many run summaries to keep. Enough to see a trend across a fortnight of nightly runs
#: without the file growing without bound.
MAX_RUNS_KEPT = 30

#: How many red tests the register lists in full before it elides — and when it elides it says
#: so and points at the observation store, which holds every one. The same rule the digest
#: follows: a summary that hides its own truncation turns a named subject back into a count.
MAX_LISTED = 400


def _now_iso(now: datetime | None = None) -> str:
    return (now or datetime.now(timezone.utc)).replace(microsecond=0).isoformat()


# ── the OBSERVATION store (machine-written, and only ever additive about what it saw) ────────
def load_observed(path: Path | None = None) -> dict:
    """The observation store, or an empty one. A missing/unreadable store is EMPTY.

    Fail direction is toward reporting MORE work, never less: an unreadable store loses the
    ages and the first-seen dates, so every current red reads as brand new and the register is
    noisier than it should be. It can never read as "nothing is red", which is the failure that
    would matter.
    """
    try:
        data = json.loads((path or OBSERVED_PATH).read_text())
    except (OSError, ValueError):
        return {"runs": [], "tests": {}}
    if not isinstance(data, dict):
        return {"runs": [], "tests": {}}
    data.setdefault("runs", [])
    data.setdefault("tests", {})
    return data


class UnobservedRunRefused(ValueError):
    """A run row that no completed census could have produced. See `record`."""


def record(failures, *, head_sha: str | None, passed: int | None, causes: dict | None = None,
           now: datetime | None = None, store: dict | None = None) -> dict:
    """Fold one census run into the observation store and return the new store.

    PURE apart from its default argument — the caller saves it. That is what lets the whole
    ageing rule be tested without a filesystem.

    A test that is red again keeps its `first_seen` and gains a run; a test that has stopped
    failing keeps its record with `last_seen` where it was and `currently_red` False, because
    "this one came back" and "this one is finally fixed" are both things a reader needs and a
    store that deletes on green can express neither.

    A PASS COUNT IS THE PROOF THAT A RUN HAPPENED, so a row without one is refused (2026-09-02).
    `_record_observation` is the only sanctioned caller and it already turns UNPROVEN away, and
    `verdict()` calls a run UNPROVEN precisely when `passed` is None or zero — so `passed is None`
    arriving here means the row is not a census observation at all, whatever the file's `_doc`
    says about being machine-written.

    THE INSTANCE. This store's first row — `2026-09-02T04:30:02+00:00`, head `ec2e0b1a4`, 830 red
    — carries `"passed": null`, and could not have been written by the run it describes: that run
    finished at 04:30:02 **BST** and exited 1 on the pre-register code, an hour before this row's
    UTC stamp, and printed the older "newly failing" wording that `bc57c8e30` replaced. Its 830
    node ids match the journal's exactly, 830 for 830, so it is a faithful hand transcription of a
    COMPLETE run with one field dropped — not a truncated run, which is what it was read as. The
    cost of that dropped field was a whole day: the count could not be told apart from a partial
    one, so it had to be treated as a floor of unknown depth.

    The refusal is unreachable from the nightly path on purpose. Its subject is the OTHER way a
    row can arrive, which is the way the only row here did arrive.
    """
    if passed is None:
        raise UnobservedRunRefused(
            "refusing a run row with no pass count: `verdict()` calls such a run UNPROVEN and "
            "`_record_observation` never forwards one, so this row was not written by a completed "
            "census. Record what the run printed, including its pass count, or record nothing.")
    store = load_observed() if store is None else store
    stamp = _now_iso(now)
    failing = set(failures or ())
    tests = store.setdefault("tests", {})

    for node in sorted(failing):
        row = tests.setdefault(node, {"first_seen": stamp, "runs_red": 0})
        row["last_seen"] = stamp
        row["runs_red"] = int(row.get("runs_red") or 0) + 1
        row["currently_red"] = True
        row.setdefault("first_seen", stamp)
    for node, row in tests.items():
        if node not in failing:
            row["currently_red"] = False

    runs = store.setdefault("runs", [])
    runs.append({"at": stamp, "head": head_sha, "red": len(failing), "passed": passed,
                 "causes": dict(causes or {})})
    del runs[:-MAX_RUNS_KEPT]
    store["_doc"] = (
        "OBSERVATION, machine-written by background/head_red_register.record on every "
        "HEAD-green census run. This is what IS red and for how long. It is NOT an acceptance "
        "list and nothing here forgives anything: what we have decided to live with lives in "
        "docs/observability/head_red_baseline.json, is written by a person, and is the only "
        "thing that reduces what this register asks for."
    )
    return store


def save_observed(store: dict, path: Path | None = None) -> None:
    p = path or OBSERVED_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(store, indent=2, sort_keys=True) + "\n")


# ── what is OWED: observed red, minus what a person has accepted ─────────────────────────────
def owed(store: dict, accepted) -> list[str]:
    """Red tests nobody has accepted, sorted. The register's whole subject.

    Two populations, named apart rather than differenced into one number: `currently_red` is an
    OBSERVATION and `accepted` is a DECISION. The count this returns is the only one that can
    reach zero by work being done.
    """
    accepted = set(accepted or ())
    return sorted(n for n, row in (store.get("tests") or {}).items()
                  if row.get("currently_red") and n not in accepted)


def by_module(nodes) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for node in nodes:
        grouped.setdefault(str(node).split("::", 1)[0], []).append(node)
    return {k: sorted(v) for k, v in sorted(grouped.items())}


def oldest_first(store: dict, nodes) -> list[tuple[str, dict]]:
    """The owed set, longest-standing first — the debt order.

    A test red for twenty consecutive runs is a different thing from one that broke last night,
    and the census could express neither because it kept no history. Ranking by `runs_red` is
    the same argument `class_debt` makes for instance count: recurrence is the signal, and it is
    measured over the whole population rather than the part that happened to record a cost.
    """
    tests = store.get("tests") or {}
    return sorted(((n, tests.get(n, {})) for n in nodes),
                  key=lambda kv: (-int(kv[1].get("runs_red") or 0), kv[0]))


# ── the register document ────────────────────────────────────────────────────────────────────
def render(store: dict, accepted, *, now: datetime | None = None) -> str:
    """The register. Names every subject it can, and says so where it cannot."""
    owed_nodes = owed(store, accepted)
    runs = store.get("runs") or []
    last = runs[-1] if runs else {}
    accepted = sorted(set(accepted or ()))
    lines = [
        "# [REGISTER] Tests red at HEAD",
        "",
        "**Severity:** {} · **Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted".format(
            "BLOCKING" if owed_nodes else "RECORDED"),
        "",
        "**THIS IS A REGISTER, NOT A QUEUE ITEM. Do not archive it.** It is re-rendered in place "
        "by `background/head_red_register` on every HEAD-green census run. You action it by "
        "MAKING A TEST GREEN, or by adding that test BY NAME to "
        "`docs/observability/head_red_baseline.json` with a reason. There is no third exit and "
        "no blanket disposition: one paragraph must not be able to retire 830 subjects, which is "
        "the wallpaper this register exists to replace.",
        "",
    ]

    if not runs:
        lines += ["## No census has run yet", "",
                  "Nothing has been observed, which is NOT a claim that HEAD is green.", ""]
        return "\n".join(lines)

    lines += [
        "## The count, with each number's population named",
        "",
        "| | |",
        "|---|---:|",
        "| red at HEAD, last run | **{}** |".format(last.get("red", 0)),
        "| accepted by a person, with a reason | {} |".format(len(accepted)),
        "| **owed — neither fixed nor accepted** | **{}** |".format(len(owed_nodes)),
        "| passed, same run | {} |".format(_passed_cell(last)),
        "",
        "Last run **{}** at HEAD `{}`.".format(last.get("at", "?"), str(last.get("head") or "?")[:9]),
        "",
    ]
    if last.get("causes"):
        lines += ["Causes that run: " + ", ".join(
            "{} x{}".format(k.rsplit(".", 1)[-1], v) for k, v in last["causes"].items()), ""]

    if not owed_nodes:
        lines += ["## ZERO MEANS ZERO", "",
                  "Nothing is red at HEAD that a person has not already accepted by name. "
                  "This register is not drawn while this line is here.", ""]
        return "\n".join(lines) + "\n" + _history(runs) + "\n"

    ranked = oldest_first(store, owed_nodes)
    worst = ranked[0][1].get("runs_red") if ranked else 0
    lines += [
        "## The {} owed, longest-standing first".format(len(owed_nodes)),
        "",
        "`runs` is consecutive census runs this test has been red — the recurrence signal, the "
        "same argument `class_debt` makes for instance count. The longest-standing red here has "
        "survived **{} run(s)**.".format(worst),
        "",
        "| test | runs red | first seen |",
        "|---|---:|---|",
    ]
    for node, row in ranked[:MAX_LISTED]:
        lines.append("| `{}` | {} | {} |".format(
            node, row.get("runs_red", "?"), str(row.get("first_seen", "?"))[:10]))
    if len(ranked) > MAX_LISTED:
        lines.append("")
        lines.append("… {} more not listed here. **Every one is in "
                     "`docs/observability/head_red_observed.json`**, which is the store this "
                     "table is rendered from.".format(len(ranked) - MAX_LISTED))

    lines += ["", "## By module", "",
              "Where a whole module is red, the cause is usually one thing — a conftest, an "
              "import, a fixture — and not N separate defects.", "",
              "| module | red |", "|---|---:|"]
    for module, nodes in sorted(by_module(owed_nodes).items(),
                                key=lambda kv: (-len(kv[1]), kv[0]))[:40]:
        lines.append("| `{}` | {} |".format(module, len(nodes)))

    if accepted:
        lines += ["", "## Accepted, by name, by a person", ""]
        lines += ["- `{}`".format(n) for n in accepted[:100]]

    return "\n".join(lines) + "\n" + _history(runs) + "\n"


#: What a missing pass count MEANS, now that `record` refuses to write one. "unreadable" said the
#: machine had tried and failed to parse a summary line; since 2026-09-02 the only way a row can
#: lack a count is that no completed census wrote it, and a reader comparing two runs needs to know
#: that about the earlier one. The distinction is the whole difference between "830 is a floor of
#: unknown depth" and "830 is a complete list with one field missing".
NO_PASS_COUNT = "not written by a completed census run"


def _passed_cell(run: dict) -> str:
    return str(run.get("passed")) if run.get("passed") is not None else NO_PASS_COUNT


def _history(runs) -> str:
    rows = ["", "## Run history", "", "| run | red | passed |", "|---|---:|---:|"]
    for r in runs[-14:]:
        rows.append("| {} | {} | {} |".format(
            r.get("at", "?"), r.get("red", "?"), _passed_cell(r)))
    return "\n".join(rows)


def write_register(store: dict, accepted, *, path: Path | None = None,
                   now: datetime | None = None) -> Path:
    p = path or REGISTER_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(render(store, accepted, now=now))
    return p


# ── the draw ─────────────────────────────────────────────────────────────────────────────────
def drawable(root: Path | str | None = None) -> list[str]:
    """The owed set, for `staging_rooms` to decide whether this register is WORK.

    Non-empty means the register is drawn. Never raises: a draw that cannot rank its work must
    still see the rest of the queue, so a broken read here degrades to "not promoted" rather
    than taking the queue down — the same fail-open `_with_accruing_class_registers` already
    takes, and for the same reason.
    """
    try:
        from background.head_red_baseline import load_baseline
        accepted = load_baseline()
    except Exception:  # noqa: BLE001
        accepted = set()
    try:
        return owed(load_observed(), accepted)
    except Exception:  # noqa: BLE001
        return []


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Render the HEAD-red register from the observation store.")
    ap.add_argument("--render", action="store_true", help="(re)write the register document")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    from background.head_red_baseline import load_baseline
    store, accepted = load_observed(), load_baseline()
    o = owed(store, accepted)
    if args.render:
        print("wrote {}".format(write_register(store, accepted)))
    if args.json:
        print(json.dumps({"owed": len(o), "accepted": len(accepted),
                          "runs": len(store.get("runs") or [])}, indent=2))
    else:
        print("HEAD-RED: {} owed, {} accepted by name".format(len(o), len(accepted)))
    return 1 if o else 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
