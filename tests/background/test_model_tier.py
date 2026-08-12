"""Tests for background/model_tier.py — the per-draw model router (2026-08-12 tiering pilot).

The control being tested is unusual: it does not protect the tree, it protects the QUALITY of every
autonomous turn. Its failure mode is silent by nature — a Sonnet turn on work that needed Opus does
not go red, it goes shallow, and shallow only surfaces later as rework. So R15 applies with the
directions reversed from the usual: the thing that must be proven able to fail is CHEAPNESS. Every
test below that matters asserts some path lands on Opus.

The director's rule, which the whole file is shaped around:

    "Diagnosis, science, level moves and wall decisions stay Opus... If quality drops on
     anything, revert that class and say so — I'd rather spend the tokens than get shallower
     work."

Four properties are load-bearing, each with its own mutation:
  1. Reserved work is Opus, wherever it appears in the doorbell.
  2. A MIXED doorbell is Opus — the tier is the max over everything drawn, not the first match.
  3. An UNRECOGNISED doorbell is Opus — a rung added next month must cost tokens, not quality.
  4. A BROKEN OR EXPIRED PILOT CONFIG is Opus — the pilot cannot fail open into cheapness.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from background import model_tier as mt

REPO_ROOT = Path(__file__).resolve().parents[2]
SUPERVISOR = REPO_ROOT / "background" / "supervisor.py"


@pytest.fixture
def live_config(tmp_path) -> Path:
    """A pilot config with every pilot class on and a window that has not closed."""
    p = tmp_path / "pilot.yaml"
    p.write_text(
        "version: 1\nstarts: '2026-08-12'\nends: '2099-01-01'\nclasses:\n"
        "  stale_gap_row: {enabled: true}\n"
        "  site_surface: {enabled: true}\n"
        "  receipt_archival: {enabled: true}\n"
    )
    return p


# --- 1. Reserved work is Opus ------------------------------------------------

@pytest.mark.parametrize("marker,cls", [(m, c) for m, c, _ in mt.RESERVED])
def test_every_reserved_marker_routes_to_opus(marker, cls, live_config):
    """Table-driven over the real RESERVED table, so a marker added later is covered with no test
    change. Mutation: move any row from RESERVED to PILOT and its case here goes red."""
    d = mt.classify(f"agenda+staging empty -- {marker} something something", config=live_config)
    assert d.model == mt.OPUS
    assert d.tier == "opus"
    assert cls in d.classes


def test_the_four_director_reserved_classes_are_all_represented():
    """The director named four classes by name. If a refactor drops one from the table entirely,
    every parametrised case above still passes (they iterate whatever the table holds) — so the
    named four are pinned separately. This is the anti-vacuity guard on the test above."""
    classes = {cls for _m, cls, _w in mt.RESERVED}
    for required in ("diagnosis", "science", "level_move", "wall"):
        assert required in classes, f"director-reserved class '{required}' is not in RESERVED"


def test_every_reserved_and_pilot_marker_is_actually_emitted_by_supervisor():
    """ANTI-TAUTOLOGY (R15): the markers must be substrings the draw ACTUALLY emits, not plausible
    strings someone typed. A rung reworded upstream would otherwise silently stop matching and its
    work would fall through to 'unclassified' — which is Opus today, so it would fail safe and
    invisibly, and an invisible right answer is one refactor away from being a wrong one.

    The content-matched wall markers are exempt: they match atom titles and doorbell prose, not rung
    text, and are deliberately broader than any one emission site.
    """
    src = SUPERVISOR.read_text(encoding="utf-8")
    content_matched = {"epistemic wall", "wall_crossing", "KNIFE", "[DIRECTOR-RULING]", "[STEER]"}
    for marker, _cls, _why in mt.RESERVED + mt.PILOT:
        if marker in content_matched:
            continue
        assert marker in src, (
            f"marker {marker!r} is not emitted anywhere in supervisor.py — the classifier is "
            "matching on a string the draw no longer produces"
        )


def test_a_wall_atom_is_opus_on_any_lane(live_config):
    """Wall decisions are matched on CONTENT, not on a rung: a crossing can ride in on any lane.

    The fixture is injected deliberately: without a LIVE pilot config the site_surface class could
    not reach Sonnet anyway, and the test would pass without exercising the wall marker at all.
    """
    d = mt.classify(
        "agenda+staging empty -- LANE 2 SITE (1 atom(s) -- build site/** in parallel): "
        "KNIFE3_wall_crossing_paydown -- cut the crossings that survive passes 1 and 2",
        config=live_config,
    )
    assert d.model == mt.OPUS
    assert "wall" in d.classes


# --- 2. A mixed doorbell is Opus ---------------------------------------------

def test_a_mixed_doorbell_is_opus_even_though_a_pilot_class_is_present(live_config):
    """THE CENTRAL SAFETY PROPERTY. The tick spawns ONE process for a doorbell that combines
    `primary; ALSO -- refill`, so the tier must be the MAXIMUM over everything drawn. This is the
    real shape of a live draw: receipts to archive AND a BUILD atom with a level move."""
    reason = (
        "unprocessed staging -- WORKER_REPORT_A_2026-08-10.md; ALSO -- "
        "self-refill from maturity map (dial-weighted): D31 -- something (level 0->2)"
    )
    d = mt.classify(reason, config=live_config)
    assert d.model == mt.OPUS, "a pilot class in the draw let reserved work onto the cheaper tier"
    assert "level_move" in d.classes


def test_pilot_order_does_not_matter(live_config):
    """Mutation guard on 'first match wins': the same two items in the other order, same answer."""
    a = "STALE-GAP-ROW self-refill (RUNG 4b): re-take rows; ALSO -- LANE 1 BUILD: X (level 0->2)"
    b = "LANE 1 BUILD: X (level 0->2); ALSO -- STALE-GAP-ROW self-refill (RUNG 4b): re-take rows"
    assert mt.classify(a, config=live_config).model == mt.OPUS
    assert mt.classify(b, config=live_config).model == mt.OPUS


def test_staging_with_one_finding_among_many_receipts_is_opus(live_config):
    """The staging segment is a LIST, so it is parsed, not substring-matched. Nine receipts and one
    finding is judgment work: 'contains a receipt' must never be mistaken for 'is only receipts'."""
    receipts = ", ".join(f"WORKER_REPORT_R{i}_2026-08-10.md" for i in range(9))
    reason = f"unprocessed staging -- {receipts}, WORKER_FINDING_SOMETHING_2026-08-11.md"
    d = mt.classify(reason, config=live_config)
    assert d.model == mt.OPUS
    assert "finding_disposition" in d.classes


# --- 3. The pilot classes DO reach Sonnet when clean --------------------------
#
# Without these the file would pass with a classifier hard-wired to return Opus — the tautology
# that makes every safety assertion above meaningless.

def test_a_clean_stale_gap_draw_reaches_sonnet(live_config):
    d = mt.classify(
        "agenda+staging empty -- STALE-GAP-ROW self-refill (RUNG 4b): 3 published coupled-gap "
        "measurement(s) were taken by code that has since changed. Re-take them.",
        config=live_config,
    )
    assert d.model == mt.SONNET
    assert d.tier == "sonnet"
    assert d.classes == ["stale_gap_row"]
    assert d.is_pilot


def test_a_clean_site_lane_draw_reaches_sonnet(live_config):
    d = mt.classify(
        "agenda+staging empty -- self-refill from maturity map -- THREE-LANE draw || "
        "LANE 2 SITE (1 atom(s) -- build site/** in parallel; pixel-verify each per R11): "
        "SITE_V5_surface_3 -- the tariff comparison page (lane=SITE, level 0->2)",
        config=live_config,
    )
    assert d.model == mt.SONNET
    assert d.classes == ["site_surface"]


def test_the_staging_list_is_cut_correctly_when_a_mint_instruction_is_appended(live_config):
    """`find_work` appends '; <name>.md: MINT one atom per named deliverable...' when a ruling is
    among the staged docs. If the parse swallowed that prose it would land inside the last filename
    and the draw would read as judgment work — the right ANSWER by accident, off a wrong parse.
    Here the appended item is a ruling, so Opus is correct on the merits, and the classes must say
    so: `finding_disposition`, not a mangled receipt list."""
    reason = ("unprocessed staging -- WORKER_REPORT_A_2026-08-10.md, "
              "DIRECTOR_RULING_X_2026-08-12.md; DIRECTOR_RULING_X_2026-08-12.md: MINT one atom "
              "per named deliverable from its WORK THIS CREATES block [(1) a thing]")
    d = mt.classify(reason, config=live_config)
    assert d.model == mt.OPUS
    assert "finding_disposition" in d.classes


def test_receipts_survive_a_trailing_also_clause(live_config):
    """The other append: a receipts-only staging list plus an ALSO refill. The refill decides the
    tier (here a stale-gap row, also a pilot class), and the receipt list must still parse clean."""
    reason = ("unprocessed staging -- WORKER_REPORT_A_2026-08-10.md, run_complete_20260812T09.md"
              "; ALSO -- STALE-GAP-ROW self-refill (RUNG 4b): re-take 2 rows")
    d = mt.classify(reason, config=live_config)
    assert d.model == mt.SONNET
    assert d.classes == ["receipt_archival", "stale_gap_row"]


def test_a_receipts_only_staging_draw_reaches_sonnet(live_config):
    d = mt.classify(
        "unprocessed staging -- WORKER_REPORT_A_2026-08-10.md, WORKER_RECEIPT_B_2026-08-10.md, "
        "run_complete_20260812T090000.md",
        config=live_config,
    )
    assert d.model == mt.SONNET
    assert d.classes == ["receipt_archival"]


# --- 4. Everything unknown, broken or expired is Opus -------------------------

def test_an_unknown_doorbell_is_opus(live_config):
    """A draw rung added next month is unclassified here. Unclassified must cost tokens."""
    d = mt.classify("RUNG 99 SOMETHING-NEW self-refill: do the new thing", config=live_config)
    assert d.model == mt.OPUS
    assert d.classes == ["unclassified"]


@pytest.mark.parametrize("body", [
    "",                                                        # empty file
    "not: a: valid: yaml: [",                                  # malformed
    "- just\n- a\n- list\n",                                   # right YAML, wrong shape
    "version: 1\nclasses: {stale_gap_row: {enabled: true}}\n",  # NO `ends` -> no window
    "version: 1\nends: '2026-08-19'\nclasses: not-a-mapping\n",
])
def test_a_broken_pilot_config_is_opus(tmp_path, body):
    """FAIL-CLOSED TOWARD OPUS. Each of these is a way the pilot's own configuration can be wrong;
    none of them may make work cheaper."""
    p = tmp_path / "broken.yaml"
    p.write_text(body)
    d = mt.classify("STALE-GAP-ROW self-refill (RUNG 4b): re-take rows", config=p)
    assert d.model == mt.OPUS


def test_a_missing_pilot_config_is_opus(tmp_path):
    d = mt.classify("STALE-GAP-ROW self-refill (RUNG 4b): re-take rows",
                    config=tmp_path / "does-not-exist.yaml")
    assert d.model == mt.OPUS


def test_the_window_closes_the_pilot_with_no_edit(tmp_path):
    """"A defined period" is only defined if something ends it. Same config, two dates."""
    p = tmp_path / "pilot.yaml"
    p.write_text("version: 1\nstarts: '2026-08-12'\nends: '2026-08-19'\n"
                 "classes:\n  stale_gap_row: {enabled: true}\n")
    reason = "STALE-GAP-ROW self-refill (RUNG 4b): re-take rows"
    assert mt.classify(reason, config=p, today="2026-08-19").model == mt.SONNET  # last day: open
    assert mt.classify(reason, config=p, today="2026-08-20").model == mt.OPUS    # day after: shut


def test_disabling_one_class_reverts_only_that_class(tmp_path):
    """The director asked for per-class revert. Turning site_surface off must not disturb the rest."""
    p = tmp_path / "pilot.yaml"
    p.write_text("version: 1\nends: '2099-01-01'\nclasses:\n"
                 "  stale_gap_row: {enabled: true}\n  site_surface: {enabled: false}\n")
    assert mt.classify("STALE-GAP-ROW self-refill (RUNG 4b): x", config=p).model == mt.SONNET
    site = mt.classify("LANE 2 SITE (1 atom(s)): x", config=p)
    assert site.model == mt.OPUS
    assert "not enabled" in site.why


def test_the_live_pilot_config_parses_and_declares_only_real_pilot_classes():
    """The committed config must name classes the classifier can actually reach. A typo here would
    silently do nothing — a pilot that looks live and is not is worse than no pilot, because the
    measurement would report Opus results as Sonnet's."""
    import yaml
    data = yaml.safe_load(mt.PILOT_CONFIG.read_text(encoding="utf-8"))
    known = {cls for _m, cls, _w in mt.PILOT} | {"receipt_archival"}
    for name in (data.get("classes") or {}):
        assert name in known, f"pilot config enables '{name}', which no marker can produce"
    assert len(str(data.get("ends") or "")) == 10, "the pilot must declare a closing date"


# --- The tick actually uses it ------------------------------------------------

def test_worker_tick_chooses_the_model_from_the_draw():
    """Wiring. Mutation: revert worker_tick to the pinned `MODEL` constant and this goes red."""
    from background import worker_tick
    model, decision = worker_tick.choose_model(
        "agenda+staging empty -- self-refill from maturity map (dial-weighted): D31 -- x (level 0->2)"
    )
    assert model == mt.OPUS
    assert decision is not None and "level_move" in decision.classes


def test_worker_tick_falls_back_to_opus_when_the_classifier_raises(monkeypatch):
    """A tiering bug must be able to cost tokens and must not be able to cost quality."""
    import background.model_tier
    from background import worker_tick

    def boom(*a, **k):
        raise RuntimeError("classifier exploded")

    monkeypatch.setattr(background.model_tier, "classify", boom)
    model, decision = worker_tick.choose_model("STALE-GAP-ROW self-refill (RUNG 4b): x")
    assert model == worker_tick.MODEL == mt.OPUS
    assert decision is None


# --- The measurement record ---------------------------------------------------

def test_log_decision_writes_an_attributable_line(tmp_path):
    d = mt.classify("STALE-GAP-ROW self-refill (RUNG 4b): re-take rows",
                    config=tmp_path / "none.yaml")
    out = tmp_path / "tier.jsonl"
    mt.log_decision(d, "STALE-GAP-ROW self-refill (RUNG 4b): re-take rows", path=out, now=1.0)
    entry = json.loads(out.read_text().strip())
    assert entry["model"] == mt.OPUS
    assert entry["tier"] == "opus"
    assert entry["reason_sha"] and entry["reason_head"].startswith("STALE-GAP-ROW")
    assert entry["ts"] == 1.0


def test_log_decision_never_raises_on_an_unwritable_path(tmp_path):
    """Measurement must not be able to wedge the tick."""
    d = mt.classify("anything", config=tmp_path / "none.yaml")
    mt.log_decision(d, "anything", path=Path("/proc/definitely/not/writable/x.jsonl"))
