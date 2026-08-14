"""OPS13 -- THE PRODUCT INTERLEAVE -- R15 both-ways proof.

Atom `OPS13_product_interleave_armed` (DIRECTOR_RULING_FINDING_SEVERITY_AND_INTERLEAVE
2026-08-12, clause 4): "The product interleave arms NOW, unconditionally. One world/customer/
product atom per harness atom, every session, regardless of staging depth. It is no longer
coupled to a document count... It remains subject to clause 2: a lane carrying a live BLOCKING
finding takes the repair as its product-side draw until cleared."

The mechanism lives in `background/supervisor.py`:
`_apply_product_interleave()` arms the pairing on the grant the three-lane draw is about to make
(mutating the lane lists in place: appending when the fork budget has room, otherwise taking the
slot from the lowest-precedence harness atom, because MAX_CONCURRENT_FORKS is 1 and the interleave
must alternate rather than widen), and `product_interleave_digest_line()` renders the line that
`find_work()` logs EVERY cycle.

Per this suite's established convention for rungs embedded in the (very large)
`background/supervisor.py` -- `test_supervisor_blocker_precedence.py`,
`test_operational_red_persistent_draw.py`, `test_stale_gap_row_draw.py` -- "R15 both ways" is
proven BEHAVIOURALLY against the real functions with injected fixtures, never by exec'ing a
source-mutated copy of a 4,900-line module (the `feedback_editing_a_source_file_mid_pytest_run_
corrupts_inspect_getsource` class this project has already filed). Each direction below names the
mutation it kills:

  * test_r15_the_arm_does_not_move_with_staging_depth (exit 1) -- kills a mutation that
    re-couples the arm to a document count (`if len(list(STAGING_DIR.glob("*.md"))) >= 20: return`
    or any threshold between the two depths this test runs: 0 documents and 200).
  * test_r15_the_digest_line_can_never_be_suppressed (exit 4) -- kills a mutation that drops,
    empties or conditionalises the `log(product_interleave_digest_line(...))` call in
    `find_work()`; asserted on all three shapes of cycle (paired, violated, no-atom-drawn).
  * test_two_harness_atoms_and_no_product_atom_is_named_a_violation (exit 2) -- kills a mutation
    that lets an unpaired harness grant pass quietly.
  * test_the_digest_names_the_pair_actually_drawn (exit 3) -- kills a mutation that reports the
    grant the arm INTENDED rather than the one it made.
  * test_a_clause_2_blocker_takes_the_product_side_slot_and_is_named (exit 3, clause 2) -- kills a
    mutation that either ignores clause 2 (calling a blocker-held lane a violation) or applies it
    silently (satisfying the pairing without saying how).

Every test injects its own staging root, maturity map and interleave-state file
(`feedback_new_draw_rung_needs_fixture_isolation`); none reads the live `docs/staging/`,
`docs/design/maturity_map.yaml` or `docs/observability/.product_interleave_state.json`.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from background import supervisor

# ── fixtures ────────────────────────────────────────────────────────────────────

_HARNESS_ONLY_MAP = """\
- id: H1_harness_atom
  name: "A harness atom, the only candidate"
  lane: H_harness
  dial_inherited: 1
  level_current: 0
  level_target: 2
  loop_stage: build
  file_scope: []
"""

_HARNESS_AND_PRODUCT_MAP = """\
- id: H1_harness_atom
  name: "A harness atom with a high dial so it wins the primary pick"
  lane: H_harness
  dial_inherited: 9
  level_current: 0
  level_target: 2
  loop_stage: build
  file_scope: [background/harness_only.py]
- id: B1_product_atom
  name: "A product-lane atom"
  lane: B_commercial
  dial_inherited: 1
  level_current: 0
  level_target: 2
  loop_stage: build
  file_scope: [company/product_only.py]
"""

BLOCKING_PRODUCT_DOC = """\
# [WORKER-FINDING] A published figure in B_commercial may be wrong

**Severity:** BLOCKING · **Lane:** B_commercial

## The claim
Body text naming the untrustworthy instrument.
"""


def _atom(atom_id: str, lane: str) -> dict:
    return {"id": atom_id, "lane": lane, "dial_inherited": 1,
            "level_current": 0, "level_target": 2, "loop_stage": "build", "file_scope": []}


@pytest.fixture(autouse=True)
def _isolated_interleave_state(tmp_path, monkeypatch):
    """No test in this file may read or write the live owed ledger -- OR the live anti-livelock
    stall tracker, which `_product_side_draw` exercises through the real BUILD draw
    (`exclude_stalled=True`). Without the second redirect these tests write synthetic atom ids
    into `docs/observability/.atom_stall_tracker.json` and then read each other's writes: the
    first test's two draws of the same product atom flag it stalled, and the NEXT test's arm
    finds nothing to draw. Observed, not hypothesised -- it is how the first run of this file
    failed (`feedback_new_draw_rung_needs_fixture_isolation`)."""
    monkeypatch.setattr(supervisor, "PRODUCT_INTERLEAVE_STATE_FILE",
                        tmp_path / "state" / ".product_interleave_state.json")
    monkeypatch.setattr(supervisor, "ATOM_STALL_STATE_FILE",
                        tmp_path / "state" / ".atom_stall_tracker.json")


def _staging_with_depth(tmp_path: Path, count: int, name: str, *docs) -> Path:
    """A staging root holding `count` filler documents (plus any real ones given)."""
    root = tmp_path / name
    root.mkdir(parents=True, exist_ok=True)
    for i in range(count):
        (root / f"FILLER_{i:04d}.md").write_text(
            f"# Filler {i}\n\n**Severity:** LATENT · **Lane:** H_harness\n", encoding="utf-8")
    for doc_name, text in docs:
        (root / doc_name).write_text(text, encoding="utf-8")
    return root


def _quiet_map(monkeypatch, tmp_path, yaml_text: str, staging: Path):
    """Silence every rung above the three-lane draw and point the draw at injected state."""
    monkeypatch.setattr(supervisor, "_publish_gate_wedge_active", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_operational_red_persistent_draw", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_site_lane_draw_concurrent", lambda *a, **k: [])
    monkeypatch.setattr(supervisor, "STAGING_DIR", staging)
    map_path = tmp_path / "maturity_map.yaml"
    map_path.write_text(yaml_text, encoding="utf-8")
    monkeypatch.setattr(supervisor, "MATURITY_MAP_PATH", map_path)
    return map_path


# ── exit 1: the arm is unconditional ────────────────────────────────────────────

def test_r15_the_arm_does_not_move_with_staging_depth(tmp_path, monkeypatch):
    """EXIT 1. The SAME grant is armed identically with an EMPTY staging root and with 200
    documents in it. Any re-coupling to a document count -- the withdrawn `root < 20` trigger or
    any other threshold between 0 and 200 -- changes one of these two records and kills this test.
    """
    records = []
    logged = []
    monkeypatch.setattr(supervisor, "log", lambda msg: logged.append(msg))
    for depth in (0, 200):
        staging = _staging_with_depth(tmp_path, depth, f"staging_{depth}")
        monkeypatch.setattr(supervisor, "STAGING_DIR", staging)
        state = tmp_path / f"state_{depth}.json"
        # A debt owed by the previous grant, so the arm has something to FIRE on in both runs.
        state.write_text(json.dumps({"owed": ["H0_earlier_harness_atom"]}), encoding="utf-8")
        monkeypatch.setattr(supervisor, "PRODUCT_INTERLEAVE_STATE_FILE", state)
        _quiet_map(monkeypatch, tmp_path, _HARNESS_AND_PRODUCT_MAP, staging)
        build = [_atom("H1_harness_atom", "H_harness")]
        site: list = []
        discovery: list = []
        record = supervisor._apply_product_interleave(build, site, discovery)
        records.append((record, supervisor.product_interleave_digest_line(record),
                        [a["id"] for a in build + site + discovery]))

    (rec_empty, line_empty, grant_empty), (rec_full, line_full, grant_full) = records
    assert rec_empty["armed"] is rec_full["armed"] is True
    assert grant_empty == grant_full, "the grant the arm produced moved with staging depth"
    assert line_empty == line_full, "the digest line moved with staging depth"


def test_the_arm_takes_the_slot_rather_than_widening_the_grant(tmp_path, monkeypatch):
    """SERIAL BY DEFAULT (2026-08-03 token ruling): when a DEBT forces the product side at
    MAX_CONCURRENT_FORKS=1, the armed grant is the SAME WIDTH -- the product atom replaces the
    harness atom rather than adding a second concurrent fork."""
    monkeypatch.setattr(supervisor, "log", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "MAX_CONCURRENT_FORKS", 1)
    state = tmp_path / "owed.json"
    state.write_text(json.dumps({"owed": ["H0_earlier_harness_atom"]}), encoding="utf-8")
    monkeypatch.setattr(supervisor, "PRODUCT_INTERLEAVE_STATE_FILE", state)
    staging = _staging_with_depth(tmp_path, 0, "staging")
    _quiet_map(monkeypatch, tmp_path, _HARNESS_AND_PRODUCT_MAP, staging)

    build = [_atom("H1_harness_atom", "H_harness")]
    record = supervisor._apply_product_interleave(build, [], [])

    assert len(build) == 1, "the arm widened the grant instead of taking the slot"
    assert build[0]["id"] == "B1_product_atom"
    assert record["displaced"] == "H1_harness_atom"
    assert record["product"] == ["B1_product_atom"]
    assert record["violation"] is False


def test_an_undebted_harness_grant_is_not_displaced_it_accrues_the_debt(tmp_path, monkeypatch):
    """THE ALTERNATION, and the regression test for a defect this atom's own live check found: an
    arm that displaced on EVERY harness grant would mean the product side always wins and the
    harness side never draws -- a 0:1 ratio, not the 1:1 the ruling asks for. (Observed against the
    real map: SITE2_two_sided_wall_exhibit displaced by EP7_adapter_elexon_insights with nothing
    owed either way.) With no debt and no spare width the harness atom KEEPS its slot; the product
    side becomes owed and the NEXT grant forces it."""
    monkeypatch.setattr(supervisor, "log", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "MAX_CONCURRENT_FORKS", 1)
    staging = _staging_with_depth(tmp_path, 0, "staging")
    _quiet_map(monkeypatch, tmp_path, _HARNESS_AND_PRODUCT_MAP, staging)

    build = [_atom("H1_harness_atom", "H_harness")]
    rec1 = supervisor._apply_product_interleave(build, [], [])
    assert [a["id"] for a in build] == ["H1_harness_atom"], "the harness side was starved"
    assert rec1["armed"] is False
    assert rec1["violation"] is True
    assert rec1["owed"] == ["H1_harness_atom"]

    # ...and the very next grant is forced to the product side, which is the 1:1 ratio.
    build2 = [_atom("H1_harness_atom", "H_harness")]
    rec2 = supervisor._apply_product_interleave(build2, [], [])
    assert [a["id"] for a in build2] == ["B1_product_atom"]
    assert rec2["owed"] == []


def test_the_arm_adds_rather_than_displaces_when_the_fork_budget_has_room(tmp_path, monkeypatch):
    """The other half of the same rule: where width genuinely exists, the pair is drawn in the
    SAME grant and the harness atom keeps its slot."""
    monkeypatch.setattr(supervisor, "log", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "MAX_CONCURRENT_FORKS", 2)
    staging = _staging_with_depth(tmp_path, 0, "staging")
    _quiet_map(monkeypatch, tmp_path, _HARNESS_AND_PRODUCT_MAP, staging)

    build = [_atom("H1_harness_atom", "H_harness")]
    record = supervisor._apply_product_interleave(build, [], [])

    assert [a["id"] for a in build] == ["H1_harness_atom", "B1_product_atom"]
    assert record["harness"] == ["H1_harness_atom"]
    assert record["product"] == ["B1_product_atom"]
    assert record["owed"] == [], "a pair drawn in one grant owes nothing"


# ── exit 2: the violation is NAMED ──────────────────────────────────────────────

def test_two_harness_atoms_and_no_product_atom_is_named_a_violation(tmp_path, monkeypatch):
    """EXIT 2, in the exit criterion's own words: "a session drawing two harness atoms and no
    product atom is NAMED as a violation rather than passing quietly". Here the map holds no
    drawable product atom at all, so the arm fires and finds nothing -- the grant still has to
    say so. A mutation that returns quietly when the arm cannot fill the slot kills this test."""
    monkeypatch.setattr(supervisor, "log", lambda *a, **k: None)
    staging = _staging_with_depth(tmp_path, 0, "staging")
    _quiet_map(monkeypatch, tmp_path, _HARNESS_ONLY_MAP, staging)

    build = [_atom("H1_harness_atom", "H_harness"), _atom("H2_harness_atom", "H_harness")]
    record = supervisor._apply_product_interleave(build, [], [])
    line = supervisor.product_interleave_digest_line(record)

    assert record["violation"] is True
    assert "INTERLEAVE VIOLATION" in line
    assert "H1_harness_atom" in line and "H2_harness_atom" in line
    assert record["owed"] == ["H1_harness_atom", "H2_harness_atom"]


def test_the_owed_harness_atom_forces_the_next_grants_product_side(tmp_path, monkeypatch):
    """The enforcement half of exit 2: the pairing is not merely reported, it is MADE. Grant 1
    is harness-only (no product atom exists yet); grant 2 has one available and the arm forces
    it even though the BUILD draw would have picked the harness atom again."""
    monkeypatch.setattr(supervisor, "log", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "MAX_CONCURRENT_FORKS", 1)
    staging = _staging_with_depth(tmp_path, 0, "staging")

    _quiet_map(monkeypatch, tmp_path, _HARNESS_ONLY_MAP, staging)
    build1 = [_atom("H1_harness_atom", "H_harness")]
    rec1 = supervisor._apply_product_interleave(build1, [], [])
    assert rec1["owed"] == ["H1_harness_atom"]
    assert [a["id"] for a in build1] == ["H1_harness_atom"]
    assert rec1["violation"] is True, "an unpaired harness grant must be named, not quiet"

    # A product atom appears in the map; the debt is now payable.
    _quiet_map(monkeypatch, tmp_path, _HARNESS_AND_PRODUCT_MAP, staging)
    build2 = [_atom("H1_harness_atom", "H_harness")]
    rec2 = supervisor._apply_product_interleave(build2, [], [])

    assert [a["id"] for a in build2] == ["B1_product_atom"], "the owed product side was not forced"
    assert rec2["owed"] == [], "the debt was not paid by the product draw"


def test_a_product_only_grant_is_not_a_violation_and_owes_nothing(tmp_path, monkeypatch):
    """The opposite direction, so the control cannot be 'proven' by a version that calls every
    grant a violation: a grant with no harness atom in it owes nothing and is not named."""
    monkeypatch.setattr(supervisor, "log", lambda *a, **k: None)
    staging = _staging_with_depth(tmp_path, 0, "staging")
    _quiet_map(monkeypatch, tmp_path, _HARNESS_AND_PRODUCT_MAP, staging)

    build = [_atom("B1_product_atom", "B_commercial")]
    record = supervisor._apply_product_interleave(build, [], [])
    line = supervisor.product_interleave_digest_line(record)

    assert record["violation"] is False
    assert record["armed"] is False
    assert "INTERLEAVE VIOLATION" not in line
    assert record["owed"] == []


# ── exit 3: the digest carries the pair ACTUALLY drawn ──────────────────────────

def test_the_digest_names_the_pair_actually_drawn(tmp_path, monkeypatch):
    """EXIT 3. Both sides of the pair appear by id in the line, and they are the atoms left in
    the grant AFTER the arm ran -- not the ones it started with."""
    monkeypatch.setattr(supervisor, "log", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "MAX_CONCURRENT_FORKS", 2)
    staging = _staging_with_depth(tmp_path, 0, "staging")
    _quiet_map(monkeypatch, tmp_path, _HARNESS_AND_PRODUCT_MAP, staging)

    build = [_atom("H1_harness_atom", "H_harness")]
    record = supervisor._apply_product_interleave(build, [], [])
    line = supervisor.product_interleave_digest_line(record)

    granted = {a["id"] for a in build}
    assert "harness drawn: H1_harness_atom" in line
    assert "product drawn: B1_product_atom" in line
    assert "PAIRED" in line
    assert set(record["harness"]) | set(record["product"]) == granted


def test_a_clause_2_blocker_takes_the_product_side_slot_and_is_named(tmp_path, monkeypatch):
    """EXIT 3 + clause 2. A live BLOCKING finding in a PRODUCT lane means the repair IS this
    session's product-side draw: the grant is not a violation, the substitution is named, and no
    second product atom is drawn on top of it."""
    monkeypatch.setattr(supervisor, "log", lambda *a, **k: None)
    staging = _staging_with_depth(tmp_path, 0, "staging",
                                  ("WORKER_FINDING_B_LANE.md", BLOCKING_PRODUCT_DOC))
    _quiet_map(monkeypatch, tmp_path, _HARNESS_AND_PRODUCT_MAP, staging)

    build = [_atom("H1_harness_atom", "H_harness")]
    record = supervisor._apply_product_interleave(
        build, [], [], blocked_lanes=frozenset({"B_commercial"}))
    line = supervisor.product_interleave_digest_line(record)

    assert record["violation"] is False
    assert record["armed"] is False, "clause 2 already served the product side"
    assert [a["id"] for a in build] == ["H1_harness_atom"]
    assert "CLAUSE-2 SUBSTITUTION" in line
    assert "B_commercial" in line


def test_a_harness_lane_blocker_is_not_a_clause_2_product_substitution(tmp_path, monkeypatch):
    """The direction that stops clause 2 becoming a blanket excuse: a BLOCKING finding in the
    HARNESS lane serves the harness side, not the product side, so the pairing is still owed."""
    monkeypatch.setattr(supervisor, "log", lambda *a, **k: None)
    staging = _staging_with_depth(tmp_path, 0, "staging")
    _quiet_map(monkeypatch, tmp_path, _HARNESS_ONLY_MAP, staging)

    build = [_atom("H1_harness_atom", "H_harness")]
    record = supervisor._apply_product_interleave(
        build, [], [], blocked_lanes=frozenset({"H_harness"}))
    line = supervisor.product_interleave_digest_line(record)

    assert record["clause2_lanes"] == []
    assert record["violation"] is True
    assert "CLAUSE-2 SUBSTITUTION" not in line


# ── exit 4: SILENCE IS THE FAILURE ──────────────────────────────────────────────

def test_the_digest_line_is_never_empty_on_any_path(tmp_path, monkeypatch):
    """EXIT 4, at the renderer: every shape of cycle produces a non-empty line carrying the
    marker -- including `None`, the cycle that drew no maturity-map atom at all."""
    monkeypatch.setattr(supervisor, "log", lambda *a, **k: None)
    staging = _staging_with_depth(tmp_path, 0, "staging")
    _quiet_map(monkeypatch, tmp_path, _HARNESS_AND_PRODUCT_MAP, staging)

    build = [_atom("H1_harness_atom", "H_harness")]
    paired = supervisor.product_interleave_digest_line(
        supervisor._apply_product_interleave(build, [], []))
    _quiet_map(monkeypatch, tmp_path, _HARNESS_ONLY_MAP, staging)
    violated = supervisor.product_interleave_digest_line(
        supervisor._apply_product_interleave([_atom("H1_harness_atom", "H_harness")], [], []))
    no_atoms = supervisor.product_interleave_digest_line(None)

    for line in (paired, violated, no_atoms):
        assert line.startswith("PRODUCT INTERLEAVE (OPS13, clause 4):")
        assert len(line) > len("PRODUCT INTERLEAVE (OPS13, clause 4):") + 20
    assert "NO maturity-map atom drawn this cycle" in no_atoms
    assert "owed carried:" in no_atoms


def test_r15_the_digest_line_can_never_be_suppressed(tmp_path, monkeypatch):
    """EXIT 4 + R15, at the CALL SITE -- the half a renderer test cannot see. `find_work()` must
    log the line on every cycle: when the draw granted a pair, when it granted an unpaired harness
    atom, and when it drew no atom at all. A mutation that deletes, empties or conditionalises the
    `log(product_interleave_digest_line(...))` call kills this test on all three."""
    logged: list[str] = []
    monkeypatch.setattr(supervisor, "log", lambda msg: logged.append(msg))
    monkeypatch.setattr(supervisor, "_sync_origin_staging", lambda *a, **k: None)
    monkeypatch.setattr(supervisor.agenda_module, "load_agenda", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_real_staged_instructions", lambda *a, **k: [])
    monkeypatch.setattr(supervisor, "_is_drained_and_gated", lambda *a, **k: False)

    def _lines() -> list[str]:
        return [m for m in logged if m.startswith("PRODUCT INTERLEAVE (OPS13, clause 4):")]

    # 1. A real three-lane draw that grants an unpaired harness atom.
    staging = _staging_with_depth(tmp_path, 0, "staging")
    _quiet_map(monkeypatch, tmp_path, _HARNESS_ONLY_MAP, staging)
    monkeypatch.setattr(supervisor, "_idle_discover_frame_draw_concurrent", lambda *a, **k: [])
    supervisor.find_work(resumed_from_pause=False)
    assert len(_lines()) == 1, "find_work drew a grant and logged no interleave line"
    assert "H1_harness_atom" in _lines()[0]

    # 2. A cycle whose REAL draw returns from a rung above the three-lane draw: no atom drawn,
    #    still a line -- and it must report THIS cycle (no pair), not inherit step 1's pair.
    logged.clear()
    monkeypatch.setattr(supervisor, "_publish_gate_wedge_active",
                        lambda *a, **k: "RUNG 1 -- unwedge the publish gate")
    supervisor.find_work(resumed_from_pause=False)
    assert len(_lines()) == 1
    assert "NO maturity-map atom drawn this cycle" in _lines()[0]
    # step 1's PAIR is not re-reported as this cycle's; its unpaid DEBT legitimately still is.
    assert "harness drawn:" not in _lines()[0]
    assert "owed carried: 1 (H1_harness_atom)" in _lines()[0]

    # 3. A cycle that draws nothing at all (the rest path) -- the line still fires.
    logged.clear()
    monkeypatch.setattr(supervisor, "_self_refill_draw", lambda: None)
    supervisor.find_work(resumed_from_pause=False)
    assert len(_lines()) == 1


def test_the_stale_record_of_a_previous_grant_cannot_be_reported_as_this_cycles_pair(
        tmp_path, monkeypatch):
    """The other fail-silent shape: a cycle that returns from a priority rung must not inherit the
    LAST cycle's pair. `_self_refill_draw` resets the record before any rung can return."""
    monkeypatch.setattr(supervisor, "log", lambda *a, **k: None)
    staging = _staging_with_depth(tmp_path, 0, "staging")
    _quiet_map(monkeypatch, tmp_path, _HARNESS_AND_PRODUCT_MAP, staging)
    monkeypatch.setattr(supervisor, "_idle_discover_frame_draw_concurrent", lambda *a, **k: [])

    supervisor._self_refill_draw()
    assert supervisor._LAST_INTERLEAVE_RECORD is not None

    monkeypatch.setattr(supervisor, "_publish_gate_wedge_active",
                        lambda *a, **k: "WEDGE -- unwedge the publish gate")
    supervisor._self_refill_draw()
    assert supervisor._LAST_INTERLEAVE_RECORD is None
    assert "NO maturity-map atom drawn this cycle" in supervisor.product_interleave_digest_line(
        supervisor._LAST_INTERLEAVE_RECORD)


# ── the owed ledger itself ──────────────────────────────────────────────────────

def test_an_unreadable_owed_ledger_is_named_in_the_line_not_silently_reset(tmp_path, monkeypatch):
    """FAIL-VISIBLE (R15 killer pattern 2). A debt ledger that quietly resets always reads paid,
    so a corrupt state file must SAY so in the same line that reports the pairing."""
    monkeypatch.setattr(supervisor, "log", lambda *a, **k: None)
    state = tmp_path / "corrupt.json"
    state.write_text("{not json", encoding="utf-8")
    monkeypatch.setattr(supervisor, "PRODUCT_INTERLEAVE_STATE_FILE", state)
    staging = _staging_with_depth(tmp_path, 0, "staging")
    _quiet_map(monkeypatch, tmp_path, _HARNESS_ONLY_MAP, staging)

    record = supervisor._apply_product_interleave([_atom("H1_harness_atom", "H_harness")], [], [])
    line = supervisor.product_interleave_digest_line(record)

    assert "UNREADABLE" in line
    assert record["state_error"] is not None


def test_the_owed_ledger_is_bounded(tmp_path, monkeypatch):
    """An unbounded debt list accumulates noise nothing can ever pay down. The ledger keeps the
    most recent unpaid ids only."""
    monkeypatch.setattr(supervisor, "log", lambda *a, **k: None)
    staging = _staging_with_depth(tmp_path, 0, "staging")
    _quiet_map(monkeypatch, tmp_path, _HARNESS_ONLY_MAP, staging)

    for i in range(8):
        supervisor._apply_product_interleave([_atom(f"H{i}_harness_atom", "H_harness")], [], [])

    owed = json.loads(supervisor.PRODUCT_INTERLEAVE_STATE_FILE.read_text())["owed"]
    assert len(owed) == supervisor._INTERLEAVE_OWED_CAP
    assert owed[-1] == "H7_harness_atom"


def test_lane_classification_is_the_complement_of_the_harness(tmp_path):
    """The interleave's own vocabulary: every non-harness lane is product-side, and an atom with
    no lane at all is NEITHER (it cannot silently satisfy the pairing)."""
    assert supervisor._is_harness_atom({"lane": "H_harness"}) is True
    assert supervisor._is_product_atom({"lane": "H_harness"}) is False
    for lane in ("W1_market_weather", "C_customer_ops", "D_billing_metering", "Z_new_lane"):
        assert supervisor._is_product_atom({"lane": lane}) is True
        assert supervisor._is_harness_atom({"lane": lane}) is False
    assert supervisor._is_product_atom({}) is False
    assert supervisor._is_harness_atom({}) is False
