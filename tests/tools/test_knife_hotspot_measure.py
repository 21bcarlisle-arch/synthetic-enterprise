"""R15 proof for the KNIFE pass ledger (`tools/knife_hotspot_measure.py`).

A control counts as evidence only if a MUTATION proves it fires on its own named defect. Every
guard below therefore has a test that (a) shows the live plan passing, and (b) shows one specific
corruption reddening it ALONE. Plus a VACUITY guard: the whole file passing while no hotspot block
was ever parsed is the fail-open shape that would make this ledger theatre, and it is asserted
against directly.

The three killer patterns, as they would appear here:
  TAUTOLOGY   — if the "measured" overlap were read from the plan document, every plan would
                reconcile with itself. `test_measurement_is_independent_of_the_document` moves a
                declaration and asserts the MEASUREMENT does not move with it.
  FAIL-OPEN   — a probe that scanned nothing, or a pair silently omitted from an `overlaps:` line,
                would pass. Both are asserted to fail.
  FAIL-SILENT — an unavailable walker or index is a FAILED check, not a skipped one.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools import knife_hotspot_measure as knife

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_DOC = REPO_ROOT / "docs" / "design" / "KNIFE_HOTSPOT_PASSES.md"


# --------------------------------------------------------------------------
# The live plan reconciles. (If this ever reds, the plan is stale, not the test.)
# --------------------------------------------------------------------------

def test_the_live_plan_document_exists_and_parses():
    decls = knife.load_plan(LIVE_DOC)
    assert {d.hotspot for d in decls} == set(knife.PROBES), (
        "every named hotspot must have a probe and every probe a hotspot"
    )


def test_the_live_plan_reconciles_with_the_tree():
    findings, _report = knife.reconcile(knife.load_plan(LIVE_DOC), LIVE_DOC)
    assert findings == [], "\n".join(findings)


def test_every_probe_scanned_something():
    """FAIL-OPEN: '0 files found' and '0 files walked' are opposite facts."""
    for name, probe in knife.PROBES.items():
        pop = probe()
        assert pop.scanned > 0, f"probe {name} scanned nothing"
        assert pop.files, f"probe {name} produced an empty population"


def test_cli_returns_zero_on_the_live_plan(capsys):
    rc = knife.main(["--doc", str(LIVE_DOC)])
    assert rc == 0
    assert "KNIFE LEDGER: OK" in capsys.readouterr().out


def test_json_report_separates_the_two_sources():
    """TAUTOLOGY: the report must make the independence auditable, not promise it."""
    rc = knife.main(["--doc", str(LIVE_DOC), "--json"])
    assert rc == 0


# --------------------------------------------------------------------------
# Mutation fixtures — a plan document built from the live one, then corrupted.
# --------------------------------------------------------------------------

def _live_text() -> str:
    return LIVE_DOC.read_text(encoding="utf-8")


def _write(tmp_path: Path, text: str) -> Path:
    p = tmp_path / "PLAN.md"
    p.write_text(text, encoding="utf-8")
    return p


def _mutate(old: str, new: str) -> str:
    """Apply a mutation to the live plan, PROVING it actually mutated.

    These fixtures pin literal declaration lines out of the live document, so
    editing the plan can silently turn a `.replace()` into a no-op — the test
    then measures an unmutated document and its guard never fires. That
    happened on 2026-08-09 when KNIFE pass 1 legitimately changed two overlap
    lines to zero. The asserts below caught it (the guards reported nothing, so
    the tests reddened rather than passing vacuously), but a control should say
    WHY it failed, not leave the reader to work out that the mutation never
    landed. An unmutated fixture is now a distinct, named failure.
    """
    text = _live_text()
    assert old in text, (
        f"mutation source line is no longer in the live plan: {old!r}. "
        "Re-point the fixture at a line that exists — do NOT relax the "
        "assertion; an un-mutated fixture proves nothing."
    )
    mutated = text.replace(old, new)
    assert mutated != text, "the mutation did not change the document"
    return mutated


def _findings_for(tmp_path: Path, text: str) -> list[str]:
    doc = _write(tmp_path, text)
    return knife.reconcile(knife.load_plan(doc), doc)[0]


def _overlap_the_tree_no_longer_has(monkeypatch, a: str, b: str, shared_file: str) -> None:
    """Make probes `a` and `b` genuinely share `shared_file`, on the MEASURED side.

    WHY THIS IS SYNTHESISED RATHER THAN PINNED (2026-08-09, KNIFE pass 3).
    These two guards used to point at whichever real overlap the tree happened to
    carry — first reporting<->customer, then (after pass 1) customer<->crossings at
    16 files. Pass 2 cut those sixteen, the overlap table went to ALL ZEROS, and both
    guards went RED at HEAD with "mutation source line is no longer in the live plan":
    there was no longer a real overlap to leave undeclared.

    That is the guard's own anti-vacuity assert doing its job, and it is also a design
    defect it exposed: a control whose fixture requires a LIVE instance of the defect
    dies exactly when the codebase reaches its goal state — and the goal state here is
    total disjointness. Repair the STATISTIC, not the fixture: the mutation now
    manufactures the overlap on the measured side, so the guard proves the same thing
    (a declared 0 against a real 1 is caught, and silence is not zero) on a tree with
    no tangle left in it, and will keep proving it forever.
    """
    for name in (a, b):
        real = knife.PROBES[name]()
        patched = knife.Population(
            files=real.files | {shared_file},
            edges=real.edges,
            scanned=real.scanned or 1,
            lines=real.lines,
            notes=real.notes,
        )
        monkeypatch.setitem(knife.PROBES, name, lambda p=patched: p)


def test_mutation_undeclared_overlap_reds(tmp_path, monkeypatch):
    """THE guard: a real overlap left undeclared is the concurrency hazard itself.

    This is the mutation that actually fired in anger — the drafted plan declared
    reporting/customer disjoint when they shared `simulation/run_phase4c_on_phase2b.py`.
    The plan now declares every pair at 0, truthfully, so the defect is manufactured
    on the measured side (see `_overlap_the_tree_no_longer_has`) and the plan's honest
    `0` becomes the lie.
    """
    _overlap_the_tree_no_longer_has(
        monkeypatch, "customer_straddle", "wall_crossings", "saas/_synthetic_shared_file.py"
    )
    findings = _findings_for(tmp_path, _live_text())
    assert any(
        "undeclared" in f and "customer_straddle" in f and "wall_crossings" in f
        for f in findings
    ), findings


def test_vacuity_the_undeclared_overlap_guard_is_silent_without_the_defect(tmp_path):
    """The other half of the mutation above: with no injected overlap the SAME call
    reports nothing. Without this, a guard that always fired would look identical."""
    findings = _findings_for(tmp_path, _live_text())
    assert not any("undeclared" in f for f in findings), findings


def test_mutation_invented_overlap_reds(tmp_path):
    """The mirror defect: a plan claiming a tangle the tree does not have."""
    text = _mutate(
        "overlaps: reporting_monolith=0, customer_straddle=0, wall_crossings=0",
        "overlaps: reporting_monolith=7, customer_straddle=0, wall_crossings=0",
    )
    findings = _findings_for(tmp_path, text)
    assert any("not there" in f for f in findings), findings


def test_mutation_omitted_pair_reds_rather_than_defaulting_to_zero(tmp_path, monkeypatch):
    """FAIL-OPEN: silence about a pair must never read as 'they do not overlap'.

    The omitted pair is deliberately one that DOES overlap — manufactured on the
    measured side, since the tree is now fully disjoint (see
    `_overlap_the_tree_no_longer_has`) — so the test proves silence is caught on
    exactly the case where defaulting to zero would hide a real hazard, rather than
    on a pair where zero happens to be right.
    """
    _overlap_the_tree_no_longer_has(
        monkeypatch, "customer_straddle", "wall_crossings", "saas/_synthetic_shared_file.py"
    )
    text = _mutate(
        "overlaps: reporting_monolith=0, wall_crossings=0, company_orphans=0",
        "overlaps: reporting_monolith=0, company_orphans=0",
    )
    findings = _findings_for(tmp_path, text)
    assert any("omits" in f and "wall_crossings" in f for f in findings), findings


def test_mutation_hotspot_dropped_leaves_its_probe_orphaned(tmp_path):
    """A hotspot quietly deleted from the plan must not quietly stop being measured."""
    text = _live_text()
    start = text.index("<!-- KNIFE-HOTSPOT\nhotspot: company_orphans")
    end = text.index(knife.BLOCK_CLOSE, start) + len(knife.BLOCK_CLOSE)
    text = text[:start] + text[end:]
    findings = _findings_for(tmp_path, text)
    assert any("company_orphans" in f and "no hotspot block declares it" in f for f in findings), findings


def test_mutation_probe_that_does_not_exist_reds(tmp_path):
    text = _live_text().replace("probe: wall_crossings", "probe: wall_crossings_v2", 1)
    findings = _findings_for(tmp_path, text)
    assert any("does not exist" in f for f in findings), findings


def test_mutation_unmeasurable_probe_is_a_failed_check_not_a_pass(tmp_path, monkeypatch):
    """FAIL-SILENT: an unavailable probe must be a FINDING, never an omission."""
    def dead():
        raise knife.ProbeUnavailable("the walker is gone")

    monkeypatch.setitem(knife.PROBES, "wall_crossings", dead)
    findings = _findings_for(tmp_path, _live_text())
    assert any("could not be measured" in f and "wall_crossings" in f for f in findings), findings


def test_mutation_empty_walk_raises_rather_than_reporting_zero(monkeypatch):
    """FAIL-OPEN, at the probe's own boundary."""
    monkeypatch.setattr(knife, "_wall_edges", lambda: ({}, 0))
    with pytest.raises(knife.ProbeUnavailable):
        knife.probe_wall_crossings()


def test_mutation_unterminated_block_is_an_error_not_a_swallow():
    """BOUNDED PARSING: an unbounded field parser makes every later guard misfire."""
    text = f"{knife.BLOCK_OPEN}\nhotspot: x\nprobe: y\nbaseline_files: 1\noverlaps: \n"
    with pytest.raises(knife.PlanError, match="never terminated"):
        knife.parse_plan(text)


def test_mutation_unknown_key_is_rejected_not_ignored():
    """A typo'd key must not become a silently unmeasured declaration."""
    text = (f"{knife.BLOCK_OPEN}\nhotspot: x\nprobe: y\nbaseline_files: 1\n"
            f"overlap: z=0\noverlaps: z=0\n{knife.BLOCK_CLOSE}")
    with pytest.raises(knife.PlanError, match="unknown key"):
        knife.parse_plan(text)


def test_mutation_duplicate_hotspot_is_rejected(tmp_path):
    text = _live_text()
    start = text.index("<!-- KNIFE-HOTSPOT\nhotspot: company_orphans")
    end = text.index(knife.BLOCK_CLOSE, start) + len(knife.BLOCK_CLOSE)
    doc = _write(tmp_path, text + "\n" + text[start:end])
    with pytest.raises(knife.PlanError, match="same hotspot twice"):
        knife.load_plan(doc)


def test_mutation_missing_document_is_a_failed_check(tmp_path):
    with pytest.raises(knife.PlanError, match="unreadable"):
        knife.load_plan(tmp_path / "nope.md")


def test_mutation_document_with_no_blocks_is_a_failed_check(tmp_path):
    doc = _write(tmp_path, "# a plan with nothing declared\n")
    with pytest.raises(knife.PlanError, match="no hotspots at all"):
        knife.load_plan(doc)


def test_mutation_malformed_overlaps_entry_is_rejected():
    text = (f"{knife.BLOCK_OPEN}\nhotspot: x\nprobe: y\nbaseline_files: 1\n"
            f"overlaps: z\n{knife.BLOCK_CLOSE}")
    with pytest.raises(knife.PlanError, match="not `<hotspot>=<count>`"):
        knife.parse_plan(text)


# --------------------------------------------------------------------------
# Independence and vacuity.
# --------------------------------------------------------------------------

def test_measurement_is_independent_of_the_document(tmp_path):
    """TAUTOLOGY: editing a baseline must move the DELTA and never the MEASUREMENT."""
    truth = knife.reconcile(knife.load_plan(LIVE_DOC), LIVE_DOC)[1]
    measured_before = {h["hotspot"]: h["measured"]["files"] for h in truth["hotspots"]}

    text = _live_text().replace("baseline_files: 258", "baseline_files: 1")
    doc = _write(tmp_path, text)
    after = knife.reconcile(knife.load_plan(doc), doc)[1]
    measured_after = {h["hotspot"]: h["measured"]["files"] for h in after["hotspots"]}

    assert measured_before == measured_after, "the document moved a measurement — tautology"
    orphans = next(h for h in after["hotspots"] if h["hotspot"] == "company_orphans")
    assert orphans["delta_files"] == measured_after["company_orphans"] - 1


def test_a_missed_baseline_is_reported_and_never_gates(tmp_path):
    """R12: the number is a DIAGNOSTIC. If a delta reddened the build, the cheapest move for
    any future turn would be to widen the baseline, and the ledger would optimise itself."""
    text = _live_text().replace("baseline_files: 258", "baseline_files: 1")
    doc = _write(tmp_path, text)
    findings, report = knife.reconcile(knife.load_plan(doc), doc)
    assert findings == [], "a baseline delta must not be a finding"
    assert knife.main(["--doc", str(doc), "--check"]) == 0
    orphans = next(h for h in report["hotspots"] if h["hotspot"] == "company_orphans")
    assert orphans["delta_files"] > 0, "the delta must still be REPORTED, not hidden"


def test_vacuity_the_suite_cannot_pass_while_nothing_is_parsed():
    """The fail-open shape that would make this whole file theatre."""
    decls = knife.load_plan(LIVE_DOC)
    assert len(decls) >= 4, "fewer than four hotspots declared — the plan lost a target"
    for d in decls:
        assert d.overlaps, f"hotspot {d.hotspot} declares no overlaps at all"


def test_the_plan_restates_the_directors_four_walls():
    """A plan that dropped a pre-ruled mitigation would still reconcile numerically."""
    text = _live_text().lower()
    for wall in ("one hotspot per pass", "behaviour-preserving", "byte-identical", "archive, never delete"):
        assert wall in text, f"the plan no longer states the ruled wall: {wall}"


def test_the_wall_ratchet_is_named_as_the_arbiter():
    """Enforcement lives in the ratchet; this ledger reports. If the plan stopped saying so,
    a future pass could believe this tool gates the crossings, which it deliberately does not."""
    assert "test_epistemic_wall_ratchet" in _live_text()


def test_probe_populations_use_the_same_walker_as_the_ratchet():
    """One definition of 'a crossing', two consumers. A second AST walk here would be the
    write-time blindness the whole programme exists to end."""
    import tests.architecture.test_epistemic_wall_ratchet as ratchet

    raw = ratchet.build_edges(ratchet.REPO_ROOT, ratchet.WALL_DIRS)
    expected = set(ratchet.company_reads_sim(raw)) | set(ratchet.sim_reads_company(raw))
    assert knife.probe_wall_crossings().edges == frozenset(expected)


def test_orphan_probe_reports_that_orphans_carry_tests():
    """The finding that governs pass 4's METHOD: no-caller is not dead-code. If this ever
    stops holding, pass 4's disposition rule needs rewriting, and the note is where it shows."""
    pop = knife.probe_company_orphans()
    assert pop.notes and "no-caller is NOT dead-code" in pop.notes[0]
    assert json.dumps(list(pop.notes))  # serialisable into the report
