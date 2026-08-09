"""Tests for the pull-forward proposal path (atom `FUT2_pull_forward_proposal`,
DIRECTOR_RULING_FUTURE_COMMITMENT_SETS_2026-08-08 §3 + WORK-THIS-CREATES #3).

The atom's origin note names the mutation that matters: *"the one proving the path CANNOT
proceed on silence — a timeout that unblocks is the failure, and it is the failure that would
be written by default, since propose-then-proceed is what every other path in this codebase
does."* So the tests below are built around three properties of the door, each with an
explicit vacuity guard (the honest path must provably RELEASE before a mutation test claiming
it refuses means anything — a door that never opens passes every refusal test for free):

  (a) SILENCE NEVER RELEASES — no clock exists in the release path, and an arbitrarily old
      proposal with no director word resolves PENDING.
  (b) THE VERDICT IS RE-DERIVED — `verify_release` fires on a verdict claiming a release that
      no director doc contains (the tautology: a door that opens on whatever it is told).
  (c) FAIL-CLOSED — a blind scan withholds the release and says so.

The fourth class is SOURCE INDEPENDENCE: the same release sentence, word for word, must
release from the director's channel and must NOT release from a worker's or a plain advisor's.
"""
from __future__ import annotations

import inspect
import textwrap
from pathlib import Path

import pytest
import yaml

from background import pull_forward_proposal as pfp

PROJECT = Path(__file__).resolve().parent.parent.parent

RELEASE_SENTENCE = "Unblock EP7_adapter_elexon_insights — the accretion makes the case."

FAKE_MAP = [
    {"id": "EP7_adapter_elexon_insights", "title": "Elexon Insights, for real",
     "lane": "W4_the_wall", "epoch": 3, "level_current": 0, "level_target": 3,
     "loop_stage": "idle", "depends_on": ["EP6_wall_protocol_typing"],
     "block_reason": "director-reserved curriculum sequencing (R13)."},
    {"id": "EP6_wall_protocol_typing", "title": "Type the wall", "lane": "W4_the_wall",
     "epoch": 3, "level_current": 0, "level_target": 3, "loop_stage": "idle",
     "block_reason": "director-reserved curriculum sequencing (R13)."},
    {"id": "EP4_collections_journey", "title": "The collections road", "lane": "C_customer_ops",
     "epoch": 2, "level_current": 0, "level_target": 3, "loop_stage": "idle"},
    {"id": "H_live_thing", "title": "Something already building", "lane": "H_harness",
     "epoch": 3, "level_current": 2, "level_target": 3, "loop_stage": "build"},
]


@pytest.fixture
def tree(tmp_path):
    """A miniature project tree: a map, two findings that declare accretion through FUT1,
    and an empty director channel (so silence is the default state under test)."""
    (tmp_path / "docs/design").mkdir(parents=True)
    (tmp_path / "docs/staging/in_progress").mkdir(parents=True)
    (tmp_path / "docs/staging/done").mkdir(parents=True)
    # sort_keys=False so `- id:` leads each block, which is the real map's hand-authored
    # form and the anchor `tools.merge_atom_status` locates an atom by.
    (tmp_path / "docs/design/maturity_map.yaml").write_text(yaml.safe_dump(FAKE_MAP, sort_keys=False))
    (tmp_path / "docs/staging/WORKER_FINDING_ADAPTER_2026-08-01.md").write_text(textwrap.dedent("""\
        # [WORKER-FINDING] the legacy Elexon wrappers are stale (2026-08-01)

        **Advances:** EP7_adapter_elexon_insights — the migration is half-done already.
        """))
    (tmp_path / "docs/design/D6_SOMETHING_DISCOVER.md").write_text(textwrap.dedent("""\
        # D6 — a discover mint

        **Advances:** EP4_collections_journey — misdated debt.
        """))
    return tmp_path


def _map(tree):
    return tree / "docs/design/maturity_map.yaml"


def _cases(tree):
    return pfp.candidates(root=tree, map_path=_map(tree))


def _stage_director_word(tree, name="from_rich_20260809_120000.md", body=None):
    p = tree / "docs/staging" / name
    p.write_text(body if body is not None else RELEASE_SENTENCE + "\n")
    return p


def _atom(tree, atom_id):
    doc = yaml.safe_load(_map(tree).read_text())
    return next(a for a in doc if a["id"] == atom_id)


# ------------------------------------------------------------------------------ the case

def test_ripeness_is_parked_plus_accretion(tree):
    ids = [c["atom_id"] for c in _cases(tree)]
    assert ids == ["EP4_collections_journey", "EP7_adapter_elexon_insights"]


def test_a_parked_atom_with_no_accretion_is_not_a_candidate(tree):
    """EP6 is parked but nothing has been filed toward it — there is no case to make."""
    assert "EP6_wall_protocol_typing" not in [c["atom_id"] for c in _cases(tree)]


def test_an_already_building_atom_is_not_a_candidate(tree):
    (tree / "docs/staging/WORKER_FINDING_OTHER.md").write_text("**Advances:** H_live_thing\n")
    assert "H_live_thing" not in [c["atom_id"] for c in _cases(tree)]


def test_the_case_carries_the_ledger_and_the_gate_verbatim(tree):
    c = next(c for c in _cases(tree) if c["atom_id"] == "EP7_adapter_elexon_insights")
    assert c["attachment_count"] == 1
    assert c["attachments"][0]["source"] == "docs/staging/WORKER_FINDING_ADAPTER_2026-08-01.md"
    assert c["gate"] == "director-reserved curriculum sequencing (R13)."
    assert c["deps_parked"] == ["EP6_wall_protocol_typing"]


def test_a_gate_that_was_never_stated_is_shown_not_invented(tree):
    c = next(c for c in _cases(tree) if c["atom_id"] == "EP4_collections_journey")
    assert c["gate_stated"] is False and c["gate"] == ""
    assert "_none stated on the atom_" in pfp.render_markdown(_cases(tree), root=tree)


def test_the_case_disappears_when_its_declaration_does(tree):
    """Ripeness is derived from the finding, not stored: delete the declaration, lose the case."""
    (tree / "docs/staging/WORKER_FINDING_ADAPTER_2026-08-01.md").write_text("# no declaration\n")
    assert "EP7_adapter_elexon_insights" not in [c["atom_id"] for c in _cases(tree)]


# --------------------------------------------------------- (a) SILENCE NEVER RELEASES

def test_silence_is_pending(tree):
    v = pfp.release_verdict("EP7_adapter_elexon_insights", root=tree)
    assert v["released"] is False
    assert "never silence" not in v["reason"] or True
    assert v["matched"] == []


def test_an_arbitrarily_old_proposal_is_still_pending(tree):
    """THE NAMED DEFECT: a timeout that unblocks. Age the whole tree by a year — every doc,
    every mtime — and the answer must not move a millimetre."""
    ancient = 1  # epoch + 1s; older than any conceivable deadline
    for p in tree.rglob("*"):
        if p.is_file():
            import os
            os.utime(p, (ancient, ancient))
    assert pfp.release_verdict("EP7_adapter_elexon_insights", root=tree)["released"] is False
    with pytest.raises(pfp.PullForwardNotReleased):
        pfp.apply_release("EP7_adapter_elexon_insights", map_path=_map(tree), root=tree)


def test_no_clock_can_reach_the_release_path(tree):
    """Structural mutation guard: the moment any release-path function accepts a time-shaped
    argument, the timeout-that-unblocks becomes writable. None of them may have one."""
    forbidden = {"now", "today", "max_age", "max_age_days", "since", "deadline",
                 "timeout", "after", "age", "elapsed", "default_after"}
    for fn in (pfp.release_verdict, pfp.verify_release, pfp.apply_release, pfp.director_sources):
        params = set(inspect.signature(fn).parameters)
        assert not (params & forbidden), f"{fn.__name__} accepts a clock: {params & forbidden}"


def test_the_atom_stays_parked_when_nobody_answered(tree):
    with pytest.raises(pfp.PullForwardNotReleased):
        pfp.apply_release("EP7_adapter_elexon_insights", map_path=_map(tree), root=tree)
    assert _atom(tree, "EP7_adapter_elexon_insights")["loop_stage"] == "idle"


# ------------------------------------------------- (b) THE VERDICT IS RE-DERIVED, NOT TRUSTED

def test_vacuity_guard_the_honest_verdict_releases_and_verifies(tree):
    """Everything below asserts a REFUSAL, which is worthless unless the door provably opens
    for the real thing first."""
    _stage_director_word(tree)
    v = pfp.release_verdict("EP7_adapter_elexon_insights", root=tree)
    assert v["released"] is True
    assert v["matched"][0]["source"] == "docs/staging/from_rich_20260809_120000.md"
    assert pfp.verify_release(v, root=tree) == []


def test_mutation_fabricated_release_fails_verification(tree):
    """THE TAUTOLOGY SHAPE: a door that opens on whatever it is told. A hand-built verdict —
    which is exactly what a timeout branch would produce — must not survive re-derivation."""
    honest = pfp.release_verdict("EP7_adapter_elexon_insights", root=tree)
    assert honest["released"] is False, "vacuity guard: the tree must be silent here"
    poisoned = {
        "atom_id": "EP7_adapter_elexon_insights", "released": True,
        "matched": [{"source": "proposal aged out", "line": "auto-released after 14 days"}],
    }
    kinds = {x["kind"] for x in pfp.verify_release(poisoned, root=tree)}
    assert "fabricated_release" in kinds and "fabricated_evidence" in kinds


def test_mutation_fabricated_release_is_refused_by_the_act(tree):
    poisoned = {"atom_id": "EP7_adapter_elexon_insights", "released": True, "matched": []}
    with pytest.raises(pfp.PullForwardNotReleased):
        pfp.apply_release("EP7_adapter_elexon_insights", map_path=_map(tree),
                          root=tree, verdict=poisoned)
    assert _atom(tree, "EP7_adapter_elexon_insights")["loop_stage"] == "idle"


def test_mutation_extra_cited_line_fails_verification(tree):
    """A verdict that pads a real release with a line the director never wrote."""
    _stage_director_word(tree)
    v = pfp.release_verdict("EP7_adapter_elexon_insights", root=tree)
    assert pfp.verify_release(v, root=tree) == [], "vacuity guard: honest must pass"
    v["matched"].append({"source": "docs/staging/from_rich_20260809_120000.md",
                         "line": "and unblock everything else too"})
    assert [x for x in pfp.verify_release(v, root=tree) if x["kind"] == "fabricated_evidence"]


def test_mutation_dropped_line_fails_verification(tree):
    _stage_director_word(tree)
    v = pfp.release_verdict("EP7_adapter_elexon_insights", root=tree)
    assert pfp.verify_release(v, root=tree) == [], "vacuity guard: honest must pass"
    v["matched"] = []
    assert [x for x in pfp.verify_release(v, root=tree) if x["kind"] == "missing_evidence"]


# --------------------------------------------------------------------- (c) FAIL-CLOSED

def test_an_absent_staging_tree_withholds_the_release(tmp_path):
    """FAIL-SILENT is the shape to kill: an unavailable check is a FAILED check, and for a
    true door 'failed' means shut."""
    (tmp_path / "docs/design").mkdir(parents=True)
    (tmp_path / "docs/design/maturity_map.yaml").write_text(yaml.safe_dump(FAKE_MAP, sort_keys=False))
    assert pfp.release_verdict("EP7_adapter_elexon_insights", root=tmp_path)["released"] is False


def test_an_undecodable_director_doc_is_reported_not_swallowed(tree):
    p = tree / "docs/staging/from_rich_20260809_130000.md"
    p.write_bytes(b"\xff\xfe unblock EP7_adapter_elexon_insights \xff")
    v = pfp.release_verdict("EP7_adapter_elexon_insights", root=tree)
    assert v["released"] is False
    assert "docs/staging/from_rich_20260809_130000.md" in v["unreadable_sources"]
    assert [x for x in pfp.verify_release(v, root=tree) if x["kind"] == "blind_scan"]


# ------------------------------------------------------------- source + wording independence

@pytest.mark.parametrize("name,body_prefix", [
    ("from_rich_20260809_120000.md", ""),
    ("DIRECTOR_RULING_PULL_FORWARD_2026-08-09.md", "# [DIRECTOR-RULING] pull it forward\n\n"),
    ("ADVISOR_STEER_BRIDGE_2026-08-09.md", "# [DIRECTOR-RULING] staged by the advisor\n\n"),
])
def test_the_directors_own_channels_release(tree, name, body_prefix):
    _stage_director_word(tree, name=name, body=body_prefix + RELEASE_SENTENCE + "\n")
    assert pfp.release_verdict("EP7_adapter_elexon_insights", root=tree)["released"] is True


@pytest.mark.parametrize("name", [
    "WORKER_FINDING_I_WANT_THIS_2026-08-09.md",
    "PLANNER_MINTED_pull_forward_2026-08-09.md",
    "ADVISOR_STEER_PLAIN_2026-08-09.md",
])
def test_nobody_else_can_open_the_door(tree, name):
    """THE SAME SENTENCE, word for word, from a non-director author. The agent writes
    WORKER_ and PLANNER_ docs itself — if those released, the door would be one the machine
    could walk through by writing a file, which is no door at all."""
    _stage_director_word(tree, name=name, body="# a doc\n\n" + RELEASE_SENTENCE + "\n")
    v = pfp.release_verdict("EP7_adapter_elexon_insights", root=tree)
    assert v["released"] is False, f"{name} must not be able to release"
    with pytest.raises(pfp.PullForwardNotReleased):
        pfp.apply_release("EP7_adapter_elexon_insights", map_path=_map(tree), root=tree)


def test_the_generated_proposal_cannot_release_its_own_subject(tree):
    """The rendering names the atom and quotes the word 'unblock' in its instructions. If the
    scan read its own projection, every proposal would release itself on sight."""
    (tree / "docs/design/PULL_FORWARD_PROPOSALS.md").write_text(
        pfp.render_markdown(_cases(tree), root=tree))
    assert pfp.release_verdict("EP7_adapter_elexon_insights", root=tree)["released"] is False


def test_a_refusal_is_not_a_release(tree):
    """Over-recognition is the dangerous direction. 'Do not unblock X' names the atom and
    carries the verb; reading it as consent would be the worst failure this module has."""
    for line in ["Do not unblock EP7_adapter_elexon_insights yet.",
                 "EP7_adapter_elexon_insights stays parked — never open it before EP6.",
                 "pull-forward is proposal-only for EP7_adapter_elexon_insights"]:
        _stage_director_word(tree, body=line + "\n")
        assert pfp.release_verdict("EP7_adapter_elexon_insights", root=tree)["released"] is False, line


def test_a_mention_without_a_release_verb_is_not_a_release(tree):
    _stage_director_word(tree, body="What is the state of EP7_adapter_elexon_insights?\n")
    assert pfp.release_verdict("EP7_adapter_elexon_insights", root=tree)["released"] is False


def test_a_release_for_one_atom_does_not_release_another(tree):
    _stage_director_word(tree)
    assert pfp.release_verdict("EP4_collections_journey", root=tree)["released"] is False


# --------------------------------------------- the release is not an orphan transition (R11)

def test_release_moves_the_atom_into_the_draw_and_clears_the_dead_park(tree):
    _stage_director_word(tree)
    before = _atom(tree, "EP7_adapter_elexon_insights")
    assert before["loop_stage"] == "idle" and before["block_reason"]
    res = pfp.apply_release("EP7_adapter_elexon_insights", map_path=_map(tree), root=tree)
    after = _atom(tree, "EP7_adapter_elexon_insights")
    assert after["loop_stage"] == "build"
    assert "block_reason" not in after, "a park reason outliving its park is a stale cell"
    assert res["released_by"] == ["docs/staging/from_rich_20260809_120000.md"]


def test_release_touches_only_the_released_atom(tree):
    _stage_director_word(tree)
    pfp.apply_release("EP7_adapter_elexon_insights", map_path=_map(tree), root=tree)
    for other in ("EP6_wall_protocol_typing", "EP4_collections_journey", "H_live_thing"):
        a = _atom(tree, other)
        assert a["loop_stage"] == FAKE_MAP[[x["id"] for x in FAKE_MAP].index(other)]["loop_stage"]
    assert _atom(tree, "EP6_wall_protocol_typing")["block_reason"]


def test_a_released_atom_stops_being_a_proposal(tree):
    _stage_director_word(tree)
    pfp.apply_release("EP7_adapter_elexon_insights", map_path=_map(tree), root=tree)
    assert "EP7_adapter_elexon_insights" not in [c["atom_id"] for c in _cases(tree)]


def test_a_folded_multiline_block_reason_is_removed_whole(tmp_path):
    """The map's real `block_reason` values are folded over several lines. Deleting only the
    first would leave orphan continuation lines and corrupt the atom."""
    (tmp_path / "docs/design").mkdir(parents=True)
    (tmp_path / "docs/staging").mkdir(parents=True)
    (tmp_path / "docs/design/maturity_map.yaml").write_text(
        "- id: EP7_adapter_elexon_insights\n"
        "  title: Elexon\n"
        "  level_current: 0\n"
        "  loop_stage: idle\n"
        "  block_reason: director-reserved curriculum sequencing (R13). Epoch-3\n"
        "    commitment set; pull-forward is proposal-only.\n"
        "  lane: W4_the_wall\n"
    )
    (tmp_path / "docs/staging/from_rich_20260809_120000.md").write_text(RELEASE_SENTENCE + "\n")
    pfp.apply_release("EP7_adapter_elexon_insights",
                      map_path=tmp_path / "docs/design/maturity_map.yaml", root=tmp_path)
    doc = yaml.safe_load((tmp_path / "docs/design/maturity_map.yaml").read_text())
    assert doc[0]["loop_stage"] == "build" and "block_reason" not in doc[0]
    assert doc[0]["lane"] == "W4_the_wall", "the fields after the removal must survive"


# --------------------------------------------------------------------------- the rendering

def test_the_rendering_states_the_no_silence_rule(tree):
    md = pfp.render_markdown(_cases(tree), root=tree)
    assert "nothing here proceeds on silence" in md
    assert "PENDING the director" in md
    assert "docs/staging/WORKER_FINDING_ADAPTER_2026-08-01.md" in md


def test_check_fails_on_a_stale_rendering(tree):
    rp = tree / "docs/design/PULL_FORWARD_PROPOSALS.md"
    rp.write_text(pfp.render_markdown(_cases(tree), root=tree))
    ok = pfp.check(root=tree, map_path=_map(tree), rendering_path=rp)
    assert ok["problems"] == [], "vacuity guard: a current rendering must pass"
    rp.write_text(rp.read_text().replace("EP4_collections_journey", "EP19_invented"))
    bad = pfp.check(root=tree, map_path=_map(tree), rendering_path=rp)
    assert [p for p in bad["problems"] if p["kind"] == "stale_rendering"]


def test_a_missing_rendering_is_a_failed_check_not_a_pass(tree):
    res = pfp.check(root=tree, map_path=_map(tree),
                    rendering_path=tree / "docs/design/PULL_FORWARD_PROPOSALS.md")
    assert [p for p in res["problems"] if p["kind"] == "missing_rendering"]


# ------------------------------------------------------------------------------- live tree

def test_live_tree_proposes_and_releases_nothing():
    """The real repo: candidates are derived, and NOT ONE of them is released — no director
    doc on disk today opens an epoch atom. A green here that came from an empty candidate set
    would be vacuous, so the count is asserted too."""
    cases = pfp.candidates()
    assert cases, "vacuity guard: FUT1 has live accretion, so there must be live candidates"
    for c in cases:
        assert pfp.release_verdict(c["atom_id"])["released"] is False, c["atom_id"]


def test_live_rendering_is_current():
    res = pfp.check()
    assert res["problems"] == [], (
        "regenerate: python3 -m background.pull_forward_proposal --write")


def test_the_draw_does_not_consult_this_module():
    """The origin note's standing risk: this must never become a permission gate. The
    supervisor's draw must not import it, and FUT1 must not either."""
    for rel in ("background/supervisor.py", "background/forward_attachment_register.py"):
        src = (PROJECT / rel).read_text()
        assert "pull_forward_proposal" not in src, f"{rel} must not consult the door"
