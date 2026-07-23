"""R15 both-ways proof of the parked-CAMPAIGN blind-spot fix (2026-07-23 NIGHT_ENFORCEMENT ruling
ADDENDUM -- the 20:00Z bug the director named as tonight's failing test).

THE DEFECT: a director-authored campaign continuation doc (DIRECTOR_CAMPAIGN_SITE_MODEL_SPINE) with an
OPEN, explicitly PROCEED-ABLE sub-item (§B "[proceed-able now]") was parked into docs/staging/
in_progress/ -- the dir the draw structurally excludes. It carries no worker `[IN-PROGRESS DISPOSITION`
banner (so `misparked_actionable_in_progress` misses it) and its items are not in CAMPAIGN_REGISTER.yaml
(SITE_V5 there is `closed`, so `_open_campaign_draw` misses it). The draw saw "nothing drawable" and
the tick idled 56+ min beside an open campaign. Director: "parked-campaign-with-open-items must be
drawable ... pick the mechanism, prove it both ways."

Proven BOTH ways:
  * FIRES on the exact defect -- a parked campaign with a proceed-able item IS surfaced (the killer:
    revert to a blanket in_progress/ exclude and this returns [] -> the 56-min stall reproduced).
  * DOES NOT false-fire -- a genuinely fully-blocked park, a non-campaign doc, and a campaign already
    reconciled into an OPEN register entry all stay quiet (no 2-min re-grant churn).
Plus the WIRING proof: the supervisor draw (`_real_staged_instructions`) actually surfaces it (R2 --
committed != running; the running draw must SEE it, not just the helper).
"""
from pathlib import Path

import background.supervisor as sup
from background.staging_disposition import misparked_open_campaign_in_progress

# The real 20:00Z incident doc, faithfully reduced: a blocker declaration (§A, director-gated) AND a
# proceed-able remaining sub-item (§B) whose "[proceed-able now]" marker sits well past the 1500-char
# head -- proving the whole-doc scan (a head-only scan would miss it, as the old net did).
_REAL_INCIDENT_DOC = (
    "# [IN PROGRESS] Site campaign continuation -- WORDS -> DIAGRAM -> EVIDENCE (2026-07-23)\n\n"
    "**BLOCKING OPEN SUB-ITEM (why this is parked here):** §A -- the canonical-door decision is\n"
    "director-pixel-gated. §C/§D cannot land canonically until §A resolves.\n\n"
    + ("Context padding to push the drawable declaration past the head-only window. " * 40)
    + "\n\n### §B -- Embed the director-APPROVED model-on-a-page diagram (F-MOAP-1)  [proceed-able now]\n"
    "The v4 SVG is the approved content; only the NAV-SPINE adoption is the gated part.\n"
)


def _mk(dirpath: Path, name: str, body: str) -> None:
    dirpath.mkdir(parents=True, exist_ok=True)
    (dirpath / name).write_text(body, encoding="utf-8")


# ---- FIRES on the defect -------------------------------------------------------------------------

def test_parked_campaign_with_proceedable_item_is_surfaced(tmp_path):
    d = tmp_path / "in_progress"
    _mk(d, "DIRECTOR_CAMPAIGN_SITE_MODEL_SPINE_2026-07-23.md", _REAL_INCIDENT_DOC)
    got = misparked_open_campaign_in_progress(d, register_path=tmp_path / "no_register.yaml")
    assert got == ["DIRECTOR_CAMPAIGN_SITE_MODEL_SPINE_2026-07-23.md"], (
        "a parked campaign with a PROCEED-ABLE sub-item MUST be surfaced (the exact 20:00Z defect); "
        "a blanket in_progress/ exclude reproduces the 56-min stall"
    )


def test_marker_past_the_head_still_caught(tmp_path):
    # the old net read only the first 1500 chars; §B's marker is beyond that -> whole-doc scan required
    d = tmp_path / "in_progress"
    assert "proceed-able" not in _REAL_INCIDENT_DOC[:1500].lower(), "fixture must exercise the tail"
    _mk(d, "DIRECTOR_CAMPAIGN_X.md", _REAL_INCIDENT_DOC)
    assert misparked_open_campaign_in_progress(d) == ["DIRECTOR_CAMPAIGN_X.md"]


# ---- DOES NOT false-fire (no churn) --------------------------------------------------------------

def test_fully_blocked_campaign_not_surfaced(tmp_path):
    d = tmp_path / "in_progress"
    _mk(d, "DIRECTOR_CAMPAIGN_BLOCKED.md",
        "# [IN PROGRESS] Campaign parked -- fully blocked\n\n"
        "**BLOCKING OPEN SUB-ITEM:** awaiting the director's pixel decision; director-reserved.\n"
        "Nothing here is drawable until he rules. Do NOT act before §A.\n")
    assert misparked_open_campaign_in_progress(d) == [], (
        "a genuinely fully-blocked park (no proceed-able marker) must stay quiet -- else the 2-min "
        "re-grant churn CLAUDE.md warns of"
    )


def test_non_campaign_doc_not_surfaced(tmp_path):
    d = tmp_path / "in_progress"
    _mk(d, "SOME_ANALYSIS.md",
        "# A done analysis\n\nThe remaining step may now proceed once the director issues an [ACT].\n")
    assert misparked_open_campaign_in_progress(d) == [], (
        "scope guard: this net is campaign-specific (the worker-mispark net covers worker docs); a "
        "non-campaign doc must not be surfaced here"
    )


def test_reconciled_into_open_register_not_double_surfaced(tmp_path):
    d = tmp_path / "in_progress"
    _mk(d, "DIRECTOR_CAMPAIGN_SITE_MODEL_SPINE_2026-07-23.md", _REAL_INCIDENT_DOC)
    reg = tmp_path / "CAMPAIGN_REGISTER.yaml"
    reg.write_text(
        "campaigns:\n"
        "  - id: SITE_MODEL_SPINE\n"
        "    status: open\n"
        "    ruling: docs/staging/in_progress/DIRECTOR_CAMPAIGN_SITE_MODEL_SPINE_2026-07-23.md\n"
        "    items:\n"
        "      - id: b_embed_diagram\n"
        "        status: open\n",
        encoding="utf-8")
    assert misparked_open_campaign_in_progress(d, register_path=reg) == [], (
        "a campaign reconciled into an OPEN register entry is drawn via the register -- this net must "
        "not double-surface it (that is the legitimate closure path, self-terminating)"
    )


def test_closed_register_entry_does_not_suppress(tmp_path):
    # SITE_V5 in the real register is `closed`; a closed entry must NOT suppress a live parked campaign
    d = tmp_path / "in_progress"
    _mk(d, "DIRECTOR_CAMPAIGN_SITE_MODEL_SPINE_2026-07-23.md", _REAL_INCIDENT_DOC)
    reg = tmp_path / "CAMPAIGN_REGISTER.yaml"
    reg.write_text(
        "campaigns:\n"
        "  - id: SITE_MODEL_SPINE\n"
        "    status: closed\n"
        "    ruling: docs/staging/in_progress/DIRECTOR_CAMPAIGN_SITE_MODEL_SPINE_2026-07-23.md\n",
        encoding="utf-8")
    assert misparked_open_campaign_in_progress(d, register_path=reg) == [
        "DIRECTOR_CAMPAIGN_SITE_MODEL_SPINE_2026-07-23.md"], (
        "a CLOSED register entry means the campaign is not being drawn -- a live parked continuation "
        "must still be surfaced")


def test_fail_open_on_missing_dir(tmp_path):
    assert misparked_open_campaign_in_progress(tmp_path / "nope") == []


# ---- WIRING proof (R2: the running draw actually sees it) -----------------------------------------

def test_supervisor_draw_surfaces_parked_campaign(tmp_path, monkeypatch):
    staging = tmp_path / "staging"
    (staging).mkdir()
    _mk(staging / "in_progress", "DIRECTOR_CAMPAIGN_SITE_MODEL_SPINE_2026-07-23.md", _REAL_INCIDENT_DOC)
    reg = tmp_path / "CAMPAIGN_REGISTER.yaml"
    reg.write_text("campaigns: []\n", encoding="utf-8")
    monkeypatch.setattr(sup, "STAGING_DIR", staging)
    monkeypatch.setattr(sup, "CAMPAIGN_REGISTER_PATH", reg)
    real = sup._real_staged_instructions()
    assert "in_progress/DIRECTOR_CAMPAIGN_SITE_MODEL_SPINE_2026-07-23.md" in real, (
        "the running supervisor draw must SEE the parked campaign (not just the helper) -- else the "
        "tick still rests beside it (R2)")
