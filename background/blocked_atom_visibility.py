#!/usr/bin/env python3
"""FUT3 -- blocked does not mean forgotten.

WHY THIS EXISTS (DIRECTOR_RULING_FUTURE_COMMITMENT_SETS_2026-08-08 §4, WORK-THIS-CREATES #4)
--------------------------------------------------------------------------------------------
The ruling minted the Epoch 2-5 commitment sets as parked atoms and then made one claim about
them: *"blocked atoms are invisible to the draw but visible to the target-design deltas and the
staleness clocks, so the 82-vs-7 imbalance becomes a measured dial."* That is three separate
properties of three separate mechanisms, and the atom's own `origin_note` names the risk: the
blocked-atom exclusion could be implemented once and reused everywhere, in which case the futures
become invisible to precisely the surfaces the ruling wants them visible on -- and the whole
minting exercise is a no-op that looks fine.

This module confirms the property instead of assuming it, and carries the dial.

WHAT "BLOCKED" MEANS ON THIS MAP (measured, not assumed)
---------------------------------------------------------
It does NOT mean `blocked_on`. Zero of the 232 atoms carry one, and the EP1-EP20 mint recorded
why in the map itself: a releaser-token block is structurally unexpressible here
(`test_maturity_map_contract.check_edges` requires `blocked_on` to be a list of existing atom ids,
and an epoch gate is not an atom), and the ruling's own §3 gate wording is auto-ignored by
`supervisor._names_abolished_permission_block`. The map's real park form is `loop_stage: idle`,
with the gate stated as prose in `block_reason`. So the PARKED SET measured here is the idle set,
and `block_reason` is reported as the gate-named subset of it.

THE THREE PROPERTIES, EACH FROM AN INDEPENDENT SOURCE
------------------------------------------------------
  DRAW      Invisible. Measured by running `supervisor._maturity_map_draw_concurrent` -- the REAL
            production draw, not a re-reading of its conditions -- against a synthetic map holding
            one parked atom and its declared dependencies.
  CLOCKS    Visible. Measured by calling AO11's own `map_assertion_provenance.build_rows` and
            asking whether every parked id has a row. Not re-derived here; if AO11 ever grows a
            drawability filter this goes red.
  DIAL      Visible. The lane weights and the ruling's named-subject coverage, computed over ALL
            atoms, and computed a second time with the parked set removed. The gap between the two
            IS the visibility: today the whole of the counterparty-adapter and forecast-feed
            coverage lives in parked atoms, so a reader that filtered them would report zero.

R15 -- THE THREE KILLER PATTERNS, ANSWERED
-------------------------------------------
TAUTOLOGY   The draw verdict comes from the draw, and the clock verdict from the clock tool. This
            module re-implements neither predicate. And the draw probe is proven BOTH WAYS per
            atom: the same synthetic map with only the park lifted must hand the atom back. An
            atom excluded for some other reason (an unmet dependency, the coupled-triad L3 gate)
            is reported EXCLUDED_OTHERWISE, never counted as proof that parking works.
FAIL-OPEN   "No parked atoms" and "the park filter is broken" are the same empty list and opposite
            facts, so an empty parked set RAISES, as does a map under `ATOM_FLOOR`, as does a run
            in which not one atom reached EXCLUDED_BY_PARK (a probe that proved nothing must never
            read like a probe that passed).
FAIL-SILENT Supervisor or AO11 being unimportable/unrunnable RAISES. An unavailable check is a
            FAILED check; nothing here degrades to "assume visible".

R12 -- WE GATE ON MEASURABILITY, NEVER ON THE NUMBER
-----------------------------------------------------
`--check` returns 2 for a parked atom that IS drawable, a parked atom the clocks cannot see, a
vacuous population, an unavailable probe, or a rendered document that disagrees with the
derivation. It returns 0 for a harness share of 37% and 0 for a harness share of 90%. The dial is
a diagnostic. If the number could fail the build, the cheapest available move would be minting
empty commercial atoms, and the map would begin optimising itself.

WHAT THIS CANNOT TELL YOU
--------------------------
Subject coverage is matched on the ATOM ID, because that is exactly how the ruling measured the
problem ("zero atoms whose ids touch adapters, tournament, generative futures, CLV, or
forecast-feed"). It is therefore a FLOOR: an atom that is genuinely about CLV but whose id does
not say so is not counted. Stated rather than hidden -- the alternative, matching prose, would
count every atom whose notes mention the word.

THE RENDERING IS A PURE FUNCTION OF THE COMMITTED MAP (2026-08-28 repair)
--------------------------------------------------------------------------
It was not, and that wedged the publisher for four and a half hours. `docs/design/BLOCKED_ATOM_
VISIBILITY.md` is a REGISTERED DERIVED ARTEFACT (`background/derived_artefact_register.py`), so
`--check` disagreeing with the file on disk reds the publish gate. Two draw inputs made the
derivation move with the map untouched: the pass ceiling, whose store gains a note on every pass
the loop makes and reads `gate_authorizations.jsonl` for level moves, and the draw's own
`random.choices` over a probe set that could contain a drawable dependency. So the committed
split moved 40/38 -> 41/37 with no atom edited, the register's repair loop re-rendered into a
moving target, `MAX_REPAIR_PASSES` was exhausted, and the freshness control's PASS branch became
unreachable -- R15's fourth shape, on a control whose subject was a design document.

The rule this establishes, and the thing to check before adding any input here: **a derived
design document may report only STATE the committed sources determine.** A number this file
prints must not be able to change because the loop took a pass, a ledger gained a line, or a
draw rolled a die. `_draw_reading` neutralises every non-map draw input and `_probe_set` parks
the dependencies so the probed atom is the sole candidate; both carry the reasoning inline.
`tests/background/test_blocked_atom_visibility.py::TestDeterminism` holds it, and holds the other
half too -- a rendering that stopped moving when the MAP moves would be a frozen document, which
is the same defect wearing the opposite sign.

NOT SAFE TO RUN INSIDE A LIVE SUPERVISOR PROCESS
-------------------------------------------------
The draw probe repoints `supervisor.MATURITY_MAP_PATH` and stubs five of that module's live-state
readers for the duration of each measurement (restored in a `finally`, with two tests holding it).
Using the real draw is the whole point -- a re-implementation would be the tautology -- but it
means a concurrent draw in the SAME process would briefly see the synthetic map. This is a CLI and
a test, and that is why it stops at L2: wiring it into the digest or a pre-commit hook is L3 work
that must run it out-of-process (a subprocess, as `--check`'s own test already does).
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from collections import Counter
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path

from tools import maturity_map_store as map_store

REPO = Path(__file__).resolve().parent.parent
MAP_PATH = REPO / "docs" / "design" / "maturity_map.yaml"
DOC_PATH = REPO / "docs" / "design" / "BLOCKED_ATOM_VISIBILITY.md"


def _doc_label() -> str:
    """The document's path for a message. Repo-relative when it is in the repo, absolute when a
    test has repointed it -- a label must never be the thing that raises."""
    try:
        return str(DOC_PATH.relative_to(REPO))
    except ValueError:
        return str(DOC_PATH)

# The map has ~232 atoms. A parse resolving fewer than this has broken, and a broken parse must
# never present as a clean map (AO11 uses the same floor for the same reason).
ATOM_FLOOR = 100

# The ruling's own evidence sentence, kept as the reference point the atom names: "lane weights
# were 82 harness vs 7 commercial across 206 atoms". A historical measurement, not a target --
# printed beside today's so the dial has a direction, never compared against by --check.
MINT_BASELINE = {"date": "2026-08-08", "atoms": 206, "harness": 82, "commercial": 7}

HARNESS_LANE = "H_harness"
COMMERCIAL_LANE = "B_commercial"

# The subjects the ruling evidenced as having ZERO atoms. Matched on lowercased atom id. The first
# three are the verification target written into FUT3's own row; `tournament` comes from the
# ruling's problem paragraph.
SUBJECTS: dict[str, tuple[str, ...]] = {
    "clv": ("clv",),
    "counterparty_adapter": ("adapter_",),
    "forecast_feed": ("forecast_feed",),
    "tournament": ("tournament",),
}

DRAWN = "DRAWN"                              # parked, yet the BUILD draw offers it -- a DEFECT
EXCLUDED_BY_PARK = "EXCLUDED_BY_PARK"        # not offered; lifting the park alone makes it offered
EXCLUDED_OTHERWISE = "EXCLUDED_OTHERWISE"    # not offered, and not offered with the park lifted


class ProbeUnavailable(RuntimeError):
    """A probe could not measure. Always a failed check, never a pass."""


# ---------------------------------------------------------------------------
# The population
# ---------------------------------------------------------------------------

def load_atoms(path: Path | None = None) -> list[dict]:
    """Every atom on the map, or raise. Vacuity is a failure, not an empty report."""
    src = path or MAP_PATH
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - yaml is a hard dependency of the map
        raise ProbeUnavailable("pyyaml unavailable: the map cannot be read") from exc
    try:
        atoms = map_store.load_atoms(src)
    except (OSError, yaml.YAMLError) as exc:
        raise ProbeUnavailable("map unreadable at %s: %s" % (src, exc)) from exc
    if not isinstance(atoms, list):
        raise ProbeUnavailable("map at %s is not a list of atoms" % src)
    atoms = [a for a in atoms if isinstance(a, dict) and a.get("id")]
    if len(atoms) < ATOM_FLOOR:
        raise ProbeUnavailable(
            "only %d atoms parsed (floor %d) -- a broken parse must not read as a clean map"
            % (len(atoms), ATOM_FLOOR)
        )
    return atoms


def is_parked(atom: dict) -> bool:
    """The map's park form: parked FOR BUILD, still DISCOVER/FRAME-workable (CLAUDE.md epoch
    gating). `block_reason` is prose stating the gate and is NOT what parks the atom -- ten atoms
    carry one while being actively built, so keying on it would misreport them as blocked."""
    return atom.get("loop_stage") == "idle"


def parked_atoms(atoms: list[dict]) -> list[dict]:
    parked = [a for a in atoms if is_parked(a)]
    if not parked:
        raise ProbeUnavailable(
            "zero parked atoms found -- an empty parked set and a broken park filter are the "
            "same empty list and opposite facts, so this is a failed measurement"
        )
    return parked


# ---------------------------------------------------------------------------
# The dial
# ---------------------------------------------------------------------------

def lane_weights(atoms: list[dict]) -> dict[str, int]:
    return dict(Counter(a.get("lane") or "UNLANED" for a in atoms).most_common())


def subject_coverage(atoms: list[dict]) -> dict[str, list[str]]:
    """subject -> the atom ids covering it. Matched on the id, as the ruling measured it."""
    out: dict[str, list[str]] = {}
    for subject, tokens in SUBJECTS.items():
        out[subject] = sorted(
            a["id"] for a in atoms if any(t in a["id"].lower() for t in tokens)
        )
    return out


# ---------------------------------------------------------------------------
# Property 1 -- the DRAW, measured with the real draw
# ---------------------------------------------------------------------------

class _FixedDirection:
    """`supervisor._direction` with the live direction record removed. `focus_weights` is a
    WEIGHT and can never change who is a candidate, so this shim only removes a needless read."""

    @staticmethod
    def focus_weights(candidates, weights):
        return weights


@contextmanager
def _draw_reading(atoms: list[dict]):
    """Point the real supervisor draw at a synthetic map for the duration of the block.

    EVERY DRAW INPUT THAT IS NOT THE MAP IS NEUTRALISED HERE, and that is the whole of the
    2026-08-28 repair. See `park_exclusion_status` for the defect; the rule it establishes is
    that this module's rendering must be a PURE FUNCTION OF THE COMMITTED MAP. A draw input read
    from a live store makes the rendering a moving target, and a derived-artefact freshness check
    over a moving target has an unreachable PASS branch (R15's fourth shape).

    Each of the five reads below confounds the measurement in BOTH directions and none of them
    has anything to do with the park:

      `_build_in_progress_ids`             drops atoms a live fork happens to own.
      `_prefer_unmerged_free`              deprioritises atoms colliding with an unmerged branch.
      `_exclude_saturated_from_core_draw`  drops atoms over the pass ceiling. Its inputs are the
                                           simplifications store (one note appended per pass the
                                           loop makes) and `gate_authorizations.jsonl` (appended
                                           per level move) -- so it changes between two runs
                                           minutes apart with the map untouched. THIS is what
                                           moved the committed split from 40/38 to 41/37 on an
                                           unchanged map, and it is self-referential: the commit
                                           that lands a re-rendered document can itself change
                                           the next rendering.
      `_direction.focus_weights`           multiplies dials from a record carrying an expiry.
      `_coupled_load_gap_ledger`           the coupled-triad L3 gate's third input. The other two
                                           (the atom's own level_target, whether a twin is
                                           registered) are on the map; the ledger is not. Fixed
                                           to empty, which is the gate's own FAIL-CLOSED reading
                                           -- an unmeasured gap blocks -- so the rendered verdict
                                           is the conservative one and is stable.

    A parked atom that a fork happened to own, or that crossed the pass ceiling this morning,
    would otherwise read as "correctly excluded" for a reason that is not the park.
    """
    try:
        import yaml

        from background import supervisor
    except ImportError as exc:
        raise ProbeUnavailable("supervisor unavailable: the draw cannot be measured") from exc
    original_path = supervisor.MATURITY_MAP_PATH
    original_bip = supervisor._build_in_progress_ids
    original_unmerged = supervisor._prefer_unmerged_free
    original_saturated = supervisor._exclude_saturated_from_core_draw
    original_direction = supervisor._direction
    original_gap_ledger = supervisor._coupled_load_gap_ledger
    with tempfile.TemporaryDirectory() as tmp:
        probe_map = Path(tmp) / "probe_map.yaml"
        probe_map.write_text(yaml.safe_dump(atoms, sort_keys=False), encoding="utf-8")
        supervisor.MATURITY_MAP_PATH = probe_map
        supervisor._build_in_progress_ids = lambda: set()
        supervisor._prefer_unmerged_free = lambda candidates, lane="BUILD": candidates
        supervisor._exclude_saturated_from_core_draw = lambda candidates: candidates
        supervisor._direction = _FixedDirection
        supervisor._coupled_load_gap_ledger = lambda: {}
        try:
            yield supervisor
        finally:
            supervisor.MATURITY_MAP_PATH = original_path
            supervisor._build_in_progress_ids = original_bip
            supervisor._prefer_unmerged_free = original_unmerged
            supervisor._exclude_saturated_from_core_draw = original_saturated
            supervisor._direction = original_direction
            supervisor._coupled_load_gap_ledger = original_gap_ledger


def draw_offers(atoms: list[dict]) -> set[str]:
    """The ids the REAL BUILD draw would offer from this atom set."""
    with _draw_reading(atoms) as supervisor:
        drawn = supervisor._maturity_map_draw_concurrent()
    if not isinstance(drawn, list):
        raise ProbeUnavailable("the draw returned %r, not a list" % type(drawn))
    return {a.get("id") for a in drawn if isinstance(a, dict)}


def _probe_set(atom: dict, by_id: dict[str, dict]) -> list[dict]:
    """The atom plus its declared dependencies -- the draw's dependency gate returns False for a
    dependency it cannot find, so a lone atom with `depends_on` would be excluded by the fixture
    rather than by the park.

    THE DEPENDENCIES TRAVEL PARKED (2026-08-28, the second half of the determinism repair). They
    are here to SATISFY the dependency gate, which reads only their levels, and parking them
    keeps that intact. What it removes is their candidacy: `_is_valid_candidate` drops
    `loop_stage: idle`, so the probed atom is the draw's ONLY candidate and
    `random.choices(candidates, ...)` has one thing to choose. Left drawable, a dependency could
    win the primary pick and then exclude the probed atom for file-scope overlap -- a COIN FLIP
    reported as EXCLUDED_OTHERWISE, i.e. a rendered number that changes with nothing but the
    draw's own rng. Passing a seeded rng would have frozen the coin rather than removed it, and
    would have made the reported verdict an artefact of the seed.
    """
    probe = [atom]
    for dep_id in atom.get("depends_on") or []:
        dep = by_id.get(dep_id)
        if dep is not None:
            probe.append(dict(dep, loop_stage="idle"))
    return probe


def _unparked(atom: dict) -> dict:
    """The same atom with ONLY the park lifted -- the control that isolates the park as the cause."""
    control = dict(atom)
    control["loop_stage"] = "build"
    control.pop("block_reason", None)
    return control


def park_exclusion_status(atoms: list[dict]) -> dict[str, str]:
    """parked atom id -> DRAWN | EXCLUDED_BY_PARK | EXCLUDED_OTHERWISE, proven both ways."""
    by_id = {a["id"]: a for a in atoms}
    status: dict[str, str] = {}
    for atom in parked_atoms(atoms):
        probe = _probe_set(atom, by_id)
        if atom["id"] in draw_offers(probe):
            status[atom["id"]] = DRAWN
            continue
        control = [_unparked(atom)] + probe[1:]
        status[atom["id"]] = (
            EXCLUDED_BY_PARK if atom["id"] in draw_offers(control) else EXCLUDED_OTHERWISE
        )
    return status


# ---------------------------------------------------------------------------
# Property 2 -- the CLOCKS, measured with AO11's own reader
# ---------------------------------------------------------------------------

def clock_visible_ids(atoms: list[dict] | None = None) -> set[str]:
    """The atom ids AO11's staleness report carries a row for. Its own function, not a re-derivation."""
    try:
        sys.path.insert(0, str(REPO))
        from tools import map_assertion_provenance
    except ImportError as exc:
        raise ProbeUnavailable("AO11 unavailable: the staleness clocks cannot be measured") from exc
    try:
        rows = map_assertion_provenance.build_rows(atoms=atoms)
    except Exception as exc:  # an unavailable check is a FAILED check
        raise ProbeUnavailable("AO11 build_rows failed: %s" % exc) from exc
    if not rows:
        raise ProbeUnavailable("AO11 returned no rows -- an empty clock report is a failed check")
    return {r["atom"] for r in rows}


# ---------------------------------------------------------------------------
# The report
# ---------------------------------------------------------------------------

@dataclass
class VisibilityReport:
    total_atoms: int
    parked_ids: list[str]
    gate_named_ids: list[str]
    draw_status: dict[str, str]
    clock_invisible_ids: list[str]
    lane_weights_all: dict[str, int]
    lane_weights_excluding_parked: dict[str, int]
    subject_coverage_all: dict[str, list[str]]
    subject_coverage_excluding_parked: dict[str, list[str]]
    integrity_findings: list[str] = field(default_factory=list)

    @property
    def harness_share(self) -> float:
        return round(100.0 * self.lane_weights_all.get(HARNESS_LANE, 0) / self.total_atoms, 1)


def build_report(atoms: list[dict] | None = None, *, probe_draw: bool = True,
                 probe_clocks: bool = True) -> VisibilityReport:
    """The full three-property report.

    `probe_draw` / `probe_clocks` exist because both probes are slow (the draw runs twice per
    parked atom, AO11 walks git history) and the dial alone is worth printing quickly. They are
    NOT a fail-open: a skipped probe is recorded as an integrity finding, so a `--check` run
    cannot pass by declining to look.
    """
    atoms = atoms if atoms is not None else load_atoms()
    parked = parked_atoms(atoms)
    parked_ids = [a["id"] for a in parked]
    unparked = [a for a in atoms if not is_parked(a)]
    findings: list[str] = []

    if probe_draw:
        status = park_exclusion_status(atoms)
        drawn = sorted(i for i, s in status.items() if s == DRAWN)
        if drawn:
            findings.append(
                "PARKED-BUT-DRAWABLE (%d): %s -- the park does not hide these from the BUILD draw"
                % (len(drawn), ", ".join(drawn))
            )
        if not any(s == EXCLUDED_BY_PARK for s in status.values()):
            findings.append(
                "VACUOUS DRAW PROBE: not one parked atom became drawable when its park was lifted, "
                "so the exclusion is not attributable to the park at all"
            )
    else:
        status = {}
        findings.append("DRAW PROBE NOT RUN -- an unrun probe is a failed check, never a pass")

    if probe_clocks:
        visible = clock_visible_ids(atoms)
        clock_invisible = sorted(i for i in parked_ids if i not in visible)
        if clock_invisible:
            findings.append(
                "PARKED-AND-UNCLOCKED (%d): %s -- the staleness clocks cannot see these"
                % (len(clock_invisible), ", ".join(clock_invisible))
            )
    else:
        clock_invisible = []
        findings.append("CLOCK PROBE NOT RUN -- an unrun probe is a failed check, never a pass")

    return VisibilityReport(
        total_atoms=len(atoms),
        parked_ids=parked_ids,
        gate_named_ids=[a["id"] for a in parked if a.get("block_reason")],
        draw_status=status,
        clock_invisible_ids=clock_invisible,
        lane_weights_all=lane_weights(atoms),
        lane_weights_excluding_parked=lane_weights(unparked),
        subject_coverage_all=subject_coverage(atoms),
        subject_coverage_excluding_parked=subject_coverage(unparked),
        integrity_findings=findings,
    )


def _render_properties(report: VisibilityReport) -> list[str]:
    lines = [
        "## The three properties",
        "",
        "| Property | Source | Result |",
        "|---|---|---|",
    ]
    by_status = Counter(report.draw_status.values())
    lines.append(
        "| Invisible to the BUILD draw | `supervisor._maturity_map_draw_concurrent` (the real draw) "
        "| %d/%d parked atoms not offered — %d proven excluded BY THE PARK (lifting the park alone "
        "makes them drawable), %d excluded for another reason |"
        % (by_status[EXCLUDED_BY_PARK] + by_status[EXCLUDED_OTHERWISE], len(report.parked_ids),
           by_status[EXCLUDED_BY_PARK], by_status[EXCLUDED_OTHERWISE])
    )
    lines.append(
        "| Visible to the staleness clocks | `tools/map_assertion_provenance.build_rows` (AO11) "
        "| %d/%d parked atoms carry a row |"
        % (len(report.parked_ids) - len(report.clock_invisible_ids), len(report.parked_ids))
    )
    lines.append(
        "| Visible to the composition dial | this module, over all %d atoms | %d parked (%d with a "
        "gate stated in `block_reason`) |"
        % (report.total_atoms, len(report.parked_ids), len(report.gate_named_ids))
    )
    return lines


def _render_dial(report: VisibilityReport) -> list[str]:
    lines = [
        "## The dial",
        "",
        "At mint (%s) the ruling measured **%d harness vs %d commercial across %d atoms**. Today:"
        % (MINT_BASELINE["date"], MINT_BASELINE["harness"], MINT_BASELINE["commercial"],
           MINT_BASELINE["atoms"]),
        "",
        "| Lane | All atoms | Excluding parked | Hidden by a park-filtering reader |",
        "|---|---:|---:|---:|",
    ]
    for lane, total in report.lane_weights_all.items():
        visible = report.lane_weights_excluding_parked.get(lane, 0)
        lines.append("| `%s` | %d | %d | %d |" % (lane, total, visible, total - visible))
    lines += [
        "",
        "Harness share of the whole map: **%.1f%%** (%d of %d)."
        % (report.harness_share, report.lane_weights_all.get(HARNESS_LANE, 0), report.total_atoms),
        "This is a DIAGNOSTIC (R12). `--check` never fails on it.",
        "The same lane counts split by `loop_stage` are on the WIP-flow door "
        "(`tools/generate_wip_flow_data.py`); what is here and not there is the with/without-parked "
        "comparison and the two probes below it.",
    ]
    return lines


def _render_subjects(report: VisibilityReport) -> list[str]:
    lines = [
        "## Subject coverage — the ruling's own zero-coverage list",
        "",
        "Matched on the atom id, as the ruling measured it; a floor, not a census.",
        "",
        "| Subject | Atoms | Of which survive a park-filtering reader |",
        "|---|---:|---:|",
    ]
    for subject in SUBJECTS:
        allc = report.subject_coverage_all[subject]
        vis = report.subject_coverage_excluding_parked[subject]
        lines.append("| `%s` | %d | %d |" % (subject, len(allc), len(vis)))
    lines += [
        "",
        "**This table is the visibility property doing work.** Where the third column is 0 and the "
        "second is not, every atom covering that subject is parked — a reader that filtered parked "
        "atoms would report exactly the zero the ruling was minted to fix.",
        "",
        "## Integrity findings",
        "",
    ]
    if report.integrity_findings:
        lines += ["- %s" % f for f in report.integrity_findings]
    else:
        lines.append("None. All probes ran and all three properties hold.")
    return lines


def render(report: VisibilityReport) -> str:
    """The generated document. Derived on every run -- a hand-edited number here is caught by
    `--check`, which re-derives and diffs rather than trusting the file."""
    lines = [
        "# BLOCKED ATOM VISIBILITY — the dial the ruling asked for",
        "",
        "**Generated** by `background/blocked_atom_visibility.py` (atom `FUT3_blocked_atom_"
        "visibility`). Do not hand-edit: `--check` re-derives and fails on any disagreement.",
        "",
        "`DIRECTOR_RULING_FUTURE_COMMITMENT_SETS_2026-08-08` §4: parked atoms are invisible to the "
        "draw and visible to the clocks and the deltas. Each line below is measured, not asserted.",
        "",
    ]
    for section in (_render_properties, _render_dial, _render_subjects):
        lines += section(report) + [""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="machine-readable report")
    parser.add_argument("--check", action="store_true",
                        help="rc 2 on any integrity finding or doc drift; never on a number")
    parser.add_argument("--write", action="store_true",
                        help="regenerate docs/design/BLOCKED_ATOM_VISIBILITY.md")
    parser.add_argument("--no-draw-probe", action="store_true",
                        help="skip the draw probe (recorded as a finding, never a pass)")
    parser.add_argument("--no-clock-probe", action="store_true",
                        help="skip the clock probe (recorded as a finding, never a pass)")
    args = parser.parse_args(argv)

    try:
        report = build_report(probe_draw=not args.no_draw_probe,
                             probe_clocks=not args.no_clock_probe)
    except ProbeUnavailable as exc:
        print("PROBE UNAVAILABLE: %s" % exc, file=sys.stderr)
        return 2

    rendered = render(report)
    if args.write:
        DOC_PATH.write_text(rendered, encoding="utf-8")
        print("wrote %s" % _doc_label())

    findings = list(report.integrity_findings)
    if args.check and not args.write:
        on_disk = DOC_PATH.read_text(encoding="utf-8") if DOC_PATH.exists() else None
        if on_disk is None:
            findings.append("DOC MISSING: %s has never been generated" % _doc_label())
        elif on_disk != rendered:
            findings.append(
                "DOC DRIFT: %s disagrees with the derivation -- rerun with --write" % _doc_label())

    if args.json:
        payload = asdict(report)
        payload["harness_share_pct"] = report.harness_share
        payload["mint_baseline"] = MINT_BASELINE
        payload["integrity_findings"] = findings
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif not (args.write or args.check):
        print(rendered)

    if args.check:
        for f in findings:
            print("FINDING: %s" % f, file=sys.stderr)
        return 2 if findings else 0
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/blocked_atom_visibility.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("blocked_atom_visibility")
    raise SystemExit(main())
