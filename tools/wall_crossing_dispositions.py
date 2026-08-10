#!/usr/bin/env python3
"""KNIFE pass 3 — every wall crossing carries a disposition, or this fails.

WHY THIS EXISTS (KNIFE_HOTSPOT_PASSES.md, pass 3 EXIT, first clause)
---------------------------------------------------------------------
Pass 3 stated its exit as CONDITIONS rather than a number, deliberately, because
pass 4 had just withdrawn "the count falls" when its own measurement contradicted
it (R12: the count is a diagnostic; LAW A: when a criterion and the evidence
disagree, the criterion is wrong). The first and load-bearing condition is:

    "Every one of the 88 surviving crossings carries a disposition. Cut (the edge
     is gone, and its tuple deleted from LEGACY_SIM_READS_COMPANY), or explicitly
     grandfathered with a named reason. No edge survives UNEXAMINED. That is the
     clause that cannot be satisfied by moving a measurement."

A clause written only in prose cannot honour that, for the same reason the KNIFE
ledger exists: a later pass can cut the easy twenty, close, and nothing in the
tree would say that sixty-eight edges were never looked at. This module is the
half that makes "examined" CHECKABLE — it reads the live crossings from the
walker and the dispositions from the register, and refuses any state in which the
two disagree.

WHAT IT GATES ON — EXAMINATION, NEVER THE COUNT (R12)
------------------------------------------------------
The same choice `tools/knife_hotspot_measure.py` made, for the same reason. This
tool has no opinion on whether 88 is too many. Eighty-eight edges each carrying an
honest `owed` row is a PASS; one edge with no row is a FAILURE. If the count
gated, the cheapest move for any future turn would be to widen the register, and
the register would begin optimising itself.

    a live crossing with no register row      -> rc 2   (the unexamined edge)
    a row claiming `cut` whose edge is LIVE   -> rc 2   (a false cut claim)
    a row for an edge that is not live,
      and not marked `cut`                    -> rc 2   (grandfathering a corpse)
    an `owed` row naming no cut design        -> rc 2   ("later" is not an examination)
    an `owed` row naming a design that
      does not exist in the register          -> rc 2   (a decorative nomination)
    a design block no row references          -> rc 2   (a plan for nothing)
    a `grandfathered` row with no reason,
      or a decorative one                     -> rc 2
    an unknown disposition value              -> rc 2
    the register missing/unparseable          -> rc 2
    ZERO crossings measured                   -> rc 2   (unmeasurable is a FAILED check)
    ZERO rows parsed                          -> rc 2   (the vacuity shape)
    the crossing count moved either way       -> rc 0   (reported in full, never hidden)

THE THREE DISPOSITIONS, AND WHY THERE ARE THREE AND NOT TWO
-------------------------------------------------------------
The exit clause names two — cut, or grandfathered. Applied literally to a pass of
this size that would force every edge to be either fixed today or declared
permanently acceptable today, and the second is how an XL pass quietly becomes a
green one: eighty-eight "acceptable"s is not an examination, it is a surrender
with a rubber stamp.

So there is a third, and it is the one that carries the weight:

  cut            The edge is GONE from the tree. Verified against the walker, not
                 against the claim — a row saying `cut` while the import is still
                 there is rc 2, which is the whole reason this class is checked
                 rather than trusted.
  grandfathered  The edge STAYS, permanently, for a named standing reason. This is
                 a wall-design RULING, not a deferral.
  owed           The edge is a real violation, it has been RULED ON, and the cut
                 that kills it is NAMED. Not "pending" — a row here carries a
                 design that exists in the register and says how the edge dies.

`owed` is the class that makes the register falsifiable per row rather than per
pass. It is the same device pass 4 used when it required a *nominated consumer*
for each of the 258 orphans and refused absent, decorative and refuted
nominations: a deferral that must name its own mechanism is examined; a deferral
that need only say "later" is not. Hence DECORATIVE_DESIGNS below, and hence the
requirement that a named design actually exist as a block — a nomination pointing
at nothing is the fail-open shape this class would otherwise have.

R15 — THE THREE KILLER PATTERNS, ANSWERED
------------------------------------------
TAUTOLOGY   — no disposition is ever derived from the tree, and no crossing is
              ever read from the register. The register is the sole authority on
              what was RULED; `tools/epistemic_wall.live_crossings()` is the sole
              authority on what EXISTS. A register edit can change a ruling but
              cannot move an edge, so a mismatch can only be closed by making the
              ruling true. `--json` reports `ruled_source` and `measured_source`
              separately so the independence is auditable rather than promised.
              Note in particular that the register carries NO file:line column:
              a measured value copied into the document would be exactly the
              same-source defect, and it would rot silently besides.
FAIL-OPEN   — an empty measurement and an empty register are both errors, not
              agreement. "No crossings found" and "the walker could not run" are
              the same number and opposite facts; so are "every edge disposed"
              and "no rows parsed". Unknown keys are rejected rather than ignored,
              so a typo'd `disposition:` cannot become a silently absent row.
FAIL-SILENT — an unavailable walker, an unreadable register or an unterminated
              block is a FAILED check. There is no skip disposition and nothing
              degrades to "assume fine".

R15 PROOF: `tests/tools/test_wall_crossing_dispositions.py` — every guard above
has a mutation proving it fires ALONE on its own named defect, plus vacuity twins
showing the suite is not silently passing on an empty population. The mutations
run against SYNTHETIC registers and synthetic crossing sets, never against the
live tree: a guard whose fixture needs a live instance of the defect dies exactly
when the codebase reaches its goal state, which is the design defect pass 3's own
first step had to repair in the KNIFE ledger's mutation proofs.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.epistemic_wall import crossings_at_head, live_crossings  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTER_DOC = REPO_ROOT / "docs" / "design" / "WALL_CROSSING_DISPOSITION_REGISTER.md"

EDGE_OPEN = "<!-- WALL-CROSSING-EDGES"
EDGE_CLOSE = "WALL-CROSSING-EDGES -->"
DESIGN_OPEN = "<!-- WALL-CROSSING-DESIGN"
DESIGN_CLOSE = "WALL-CROSSING-DESIGN -->"

DISPOSITIONS = frozenset({"cut", "grandfathered", "owed"})

# A nomination that names nothing. Pass 4 refused these for orphan consumers and
# the same words are the same evasion here.
DECORATIVE = frozenset({
    "", "-", "n/a", "na", "none", "tbd", "todo", "later", "pending", "unknown",
    "see above", "see below", "as above", "?", "wip", "future", "someday",
})

MIN_REASON_CHARS = 24


class RegisterError(Exception):
    """The register could not be read or parsed. Never degrades to a pass."""


class MeasurementError(Exception):
    """The walker could not measure. Unmeasurable is a FAILED check (R15)."""


@dataclass(frozen=True)
class EdgeRow:
    src: str
    dst: str
    disposition: str
    design: str          # "" unless disposition == owed
    reason: str          # "" unless disposition in {cut, grandfathered}
    lineno: int

    @property
    def key(self) -> tuple[str, str]:
        return (self.src, self.dst)


@dataclass(frozen=True)
class DesignBlock:
    name: str
    body: str
    lineno: int


def _decorative(value: str) -> bool:
    return value.strip().lower() in DECORATIVE


def _split_fields(raw: str, lineno: int) -> dict[str, str]:
    """Parse `k=v | k=v` tail fields. Unknown keys are an ERROR, not ignored."""
    out: dict[str, str] = {}
    for part in raw.split("|"):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            raise RegisterError(f"line {lineno}: field {part!r} is not `key=value`")
        k, v = part.split("=", 1)
        k = k.strip()
        if k in out:
            raise RegisterError(f"line {lineno}: duplicate field {k!r}")
        out[k] = v.strip()
    return out


def parse_register(text: str) -> tuple[list[EdgeRow], list[DesignBlock]]:
    """Parse both block kinds. An unterminated block is an error, never a block
    that swallows the rest of the file (bounded parsing)."""
    lines = text.splitlines()
    rows: list[EdgeRow] = []
    designs: list[DesignBlock] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()

        if stripped == EDGE_OPEN:
            i += 1
            closed = False
            while i < len(lines):
                ln = lines[i].strip()
                if ln == EDGE_CLOSE:
                    closed = True
                    break
                if ln and not ln.startswith("#"):
                    rows.append(_parse_edge_line(ln, i + 1))
                i += 1
            if not closed:
                raise RegisterError("a WALL-CROSSING-EDGES block is never terminated")

        elif stripped.startswith(DESIGN_OPEN):
            name = stripped[len(DESIGN_OPEN):].strip()
            if not name:
                raise RegisterError(f"line {i + 1}: a design block has no name")
            start = i + 1
            i += 1
            body: list[str] = []
            closed = False
            while i < len(lines):
                if lines[i].strip() == DESIGN_CLOSE:
                    closed = True
                    break
                body.append(lines[i])
                i += 1
            if not closed:
                raise RegisterError(
                    f"design block {name!r} is never terminated"
                )
            designs.append(DesignBlock(name, "\n".join(body).strip(), start))

        i += 1
    return rows, designs


_EDGE_RE = re.compile(r"^edge:\s*([\w.]+)\s*->\s*([\w.]+)\s*\|(.*)$")


def _parse_edge_line(line: str, lineno: int) -> EdgeRow:
    m = _EDGE_RE.match(line)
    if not m:
        raise RegisterError(f"line {lineno}: not a valid edge row: {line!r}")
    src, dst, tail = m.group(1), m.group(2), m.group(3)
    fields = _split_fields(tail, lineno)
    unknown = set(fields) - {"disposition", "design", "reason"}
    if unknown:
        raise RegisterError(
            f"line {lineno}: unknown field(s) {sorted(unknown)} — a typo'd key "
            "must not become a silently absent ruling"
        )
    if "disposition" not in fields:
        raise RegisterError(f"line {lineno}: row has no `disposition=`")
    return EdgeRow(
        src=src,
        dst=dst,
        disposition=fields["disposition"],
        design=fields.get("design", ""),
        reason=fields.get("reason", ""),
        lineno=lineno,
    )


def load_register(path: Path = REGISTER_DOC) -> tuple[list[EdgeRow], list[DesignBlock]]:
    if not path.exists():
        raise RegisterError(f"register document missing: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:                                  # pragma: no cover
        raise RegisterError(f"register unreadable: {exc}") from exc
    return parse_register(text)


def measure_crossings(at_head: bool = False) -> set[tuple[str, str]]:
    """The crossings, from the ONE shared walker. Zero is a failure.

    `at_head=False` reads the WORKING TREE — the right default for a gate that
    must red before you commit a new crossing.

    `at_head=True` reads the COMMITTED tree instead, and the pairing with the
    working-tree REGISTER is the whole point: the register is the CLAIM, HEAD
    is what a reader of the repo actually gets. A `cut` row whose edge is still
    live at HEAD means the cut has been written down but not landed. See the
    `--at-head` help text for why the obvious HEAD-vs-HEAD comparison is blind
    to exactly the case that motivated this.
    """
    try:
        live = crossings_at_head() if at_head else live_crossings()
    except Exception as exc:                                # pragma: no cover
        where = "HEAD" if at_head else "the working tree"
        raise MeasurementError(f"the wall walker could not run against {where}: {exc}") from exc
    if not live:
        raise MeasurementError(
            "the walker measured ZERO crossings — 'none found' and 'could not "
            "look' are the same number and opposite facts (R15 fail-open)"
        )
    return set(live)


def reconcile(
    rows: list[EdgeRow],
    designs: list[DesignBlock],
    measured: set[tuple[str, str]],
    measured_label: str = "THE TREE",
    measured_source: str = "tools.epistemic_wall.live_crossings",
) -> tuple[list[str], dict]:
    """Return (findings, report). A finding is rc 2. Counts alone never fail.

    `measured_label` names the tree in the finding text; `measured_source` names
    the callable that produced the measurement. BOTH are reported, and they are
    separate on purpose: the report has always named its two sources so a reader
    can tell what was compared against what, and "which tree" is a third fact
    that a reader of an at-HEAD run needs and cannot infer from the callable.

    Neither may change WHICH checks run: an at-HEAD pass that quietly skipped a
    check would be a weaker gate wearing a stronger gate's name.
    """
    findings: list[str] = []

    if not rows:
        findings.append(
            "the register parsed ZERO edge rows — an empty register agreeing with "
            "a non-empty tree is the vacuity shape, not a pass"
        )

    seen: dict[tuple[str, str], EdgeRow] = {}
    for row in rows:
        if row.key in seen:
            findings.append(
                f"line {row.lineno}: duplicate ruling for {row.src} -> {row.dst} "
                f"(first at line {seen[row.key].lineno}) — one edge, one disposition"
            )
            continue
        seen[row.key] = row

    design_names = {d.name for d in designs}
    dup_designs = [d.name for d in designs if sum(1 for o in designs if o.name == d.name) > 1]
    if dup_designs:
        findings.append(f"duplicate design block name(s): {sorted(set(dup_designs))}")

    referenced: set[str] = set()

    for row in seen.values():
        where = f"{row.src} -> {row.dst}"
        if row.disposition not in DISPOSITIONS:
            findings.append(
                f"{where}: unknown disposition {row.disposition!r} "
                f"(allowed: {sorted(DISPOSITIONS)})"
            )
            continue

        if row.disposition == "cut":
            if row.key in measured:
                findings.append(
                    f"{where}: ruled `cut` but the import IS STILL IN {measured_label} — "
                    "a cut is verified against the walker, never against the claim"
                )
            if _decorative(row.reason) or len(row.reason.strip()) < MIN_REASON_CHARS:
                findings.append(
                    f"{where}: `cut` carries no substantive reason "
                    f"(>= {MIN_REASON_CHARS} chars saying how it was cut)"
                )

        elif row.disposition == "grandfathered":
            if row.key not in measured:
                findings.append(
                    f"{where}: grandfathered but the edge is NOT LIVE — a standing "
                    "exemption for an edge that no longer exists is a pre-authorised "
                    "re-entry, which is the defect pass 3 deleted from the verifier"
                )
            if _decorative(row.reason) or len(row.reason.strip()) < MIN_REASON_CHARS:
                findings.append(
                    f"{where}: grandfathered with no named reason — the exit clause "
                    "says 'explicitly grandfathered with a named reason'"
                )
            if row.design:
                findings.append(
                    f"{where}: grandfathered rows carry a reason, not a `design=` — "
                    "a permanent ruling that names a cut is two rulings"
                )

        else:  # owed
            if row.key not in measured:
                findings.append(
                    f"{where}: ruled `owed` but the edge is NOT LIVE — a debt against "
                    "a corpse hides that the register is stale"
                )
            if _decorative(row.design):
                findings.append(
                    f"{where}: `owed` names no cut design — a deferral that need only "
                    "say 'later' is not an examination"
                )
            elif row.design not in design_names:
                findings.append(
                    f"{where}: `owed` names design {row.design!r}, which is not a "
                    "design block in this register — a nomination pointing at nothing"
                )
            else:
                referenced.add(row.design)

    unexamined = sorted(measured - set(seen))
    for src, dst in unexamined:
        findings.append(
            f"{src} -> {dst}: LIVE CROSSING WITH NO DISPOSITION — no edge may "
            "survive unexamined (KNIFE pass 3 exit, first clause)"
        )

    for d in designs:
        if d.name not in referenced:
            findings.append(
                f"design block {d.name!r} (line {d.lineno}) is referenced by no "
                "edge row — a plan for nothing"
            )
        if len(d.body) < MIN_REASON_CHARS:
            findings.append(
                f"design block {d.name!r} (line {d.lineno}) has no substantive body"
            )

    by_disposition = {
        d: sum(1 for r in seen.values() if r.disposition == d) for d in sorted(DISPOSITIONS)
    }
    report = {
        "ruled_source": str(REGISTER_DOC.relative_to(REPO_ROOT)),
        "measured_source": measured_source,
        "measured_tree": measured_label,
        "measured_crossings": len(measured),
        "rows": len(seen),
        "unexamined": len(unexamined),
        "by_disposition": by_disposition,
        "designs": sorted(design_names),
        "findings": findings,
    }
    return findings, report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    ap.add_argument("--register", type=Path, default=REGISTER_DOC)
    ap.add_argument(
        "--at-head", action="store_true",
        help=(
            "measure the COMMITTED tree instead of the working tree, and check the "
            "register's claims against it. This is the CLOSE-TIME check: a `cut` row "
            "is a claim about the repo, and until it is committed the repo does not "
            "contain it. Note the asymmetry that makes this work — the REGISTER is "
            "read from the working tree (the claim as just written) while the CODE is "
            "read from HEAD (what a clone gets). Comparing HEAD's register with HEAD's "
            "code instead would be blind to the case that motivated this flag, where a "
            "pass wrote its record and its code and committed NEITHER, leaving HEAD "
            "self-consistently in the old state."
        ),
    )
    args = ap.parse_args(argv)

    try:
        rows, designs = load_register(args.register)
        measured = measure_crossings(at_head=args.at_head)
    except (RegisterError, MeasurementError) as exc:
        if args.json:
            print(json.dumps({"error": str(exc), "findings": [str(exc)]}, indent=2))
        else:
            print(f"WALL-CROSSING DISPOSITIONS: FAILED — {exc}", file=sys.stderr)
        return 2

    label = "HEAD (the committed tree)" if args.at_head else "THE WORKING TREE"
    source = (
        "tools.epistemic_wall.crossings_at_head" if args.at_head
        else "tools.epistemic_wall.live_crossings"
    )
    findings, report = reconcile(
        rows, designs, measured, measured_label=label, measured_source=source
    )

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(
            f"measured against {label}: "
            f"{report['measured_crossings']} live crossings; "
            f"{report['rows']} ruled "
            f"(cut {report['by_disposition']['cut']}, "
            f"owed {report['by_disposition']['owed']}, "
            f"grandfathered {report['by_disposition']['grandfathered']}); "
            f"{len(report['designs'])} cut designs"
        )
        for f in findings:
            print(f"  FINDING: {f}")
        if not findings:
            print("WALL-CROSSING DISPOSITIONS: OK — every live crossing is examined.")

    return 2 if findings else 0


if __name__ == "__main__":                                  # pragma: no cover
    raise SystemExit(main())
