"""The canon drift check, proven able to fail — in BOTH directions (R15).

Atom A45_the_canon_is_a_standing_subject. The control under test asks what the page claims that
the code no longer supports; these tests ask whether it could ever say anything else.

WHY BOTH DIRECTIONS ARE A NAMED REQUIREMENT AND NOT A NICETY. On 2026-08-28 the director's
guidance said `price_sensitivity` was read by nothing. A channel for it had landed on 2026-08-27.
A drift check that can only report OVER_CLAIM would have re-confirmed a dead claim with evidence,
which is worse than not checking — so `test_a_channel_that_appears_reports_superseded` is the
mutation that matters most here, and it is the one a one-directional design cannot pass.

THE FIXTURES ARE WHOLE MINIATURE REPOS, not monkeypatched internals. Every probe resolves paths
under a root, so a test can DELETE a channel, ADD one, move a claim's anchor off the page, or
point a probe at a path that does not exist, and watch the verdict change. A control tested only
against the live tree cannot be mutated without editing the live tree.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.canon_drift_check import (  # noqa: E402
    ERROR,
    HOLDS,
    OVER_CLAIM,
    SUPERSEDED,
    UNBOUND,
    Claim,
    ProbeError,
    evaluate,
    live_source,
    load_register,
    main,
    run,
)

LIVE_REGISTER = REPO_ROOT / "docs/design/canon_claims.yaml"

#: Pinned LITERALLY, not derived from the register. A parametrised test that draws its cases from
#: the registry it checks cannot see its own scope shrink: delete a claim and it leaves both sides
#: of the comparison at once. Adding a claim is expected to fail here — say so in the diff.
EXPECTED_CLAIM_IDS = frozenset({
    "C1_price_sensitivity_reaches_the_churn_decision",
    "C1_green_stance_carries_no_channel",
    "C1_channel_pref_carries_no_channel",
    "C2_a_rival_supplier_is_modelled",
    "C2_market_position_is_a_run_level_constant",
    "C3_collateral_is_a_cost_line_never_a_call",
    "C3_the_world_cannot_reach_the_liquidity_organs",
    "SITE_the_schematic_still_says_the_traits_are_coupled",
    "SITE_the_schematic_still_says_the_company_can_die",
    # 2026-08-28, the director's mission rewrite. The mission names three channels through which
    # value reaches a household -- modelling, tariffs, advice -- and THE MODEL ON A PAGE now states
    # that advice has modules on disk and no recipient. That is a CHANNEL claim of C1's exact shape
    # (the thing exists; does the WORLD call it?), so it is registerable and is registered.
    # Two claims rather than one on purpose: the recommenders can gain a recipient independently.
    "MISSION_switching_advice_has_no_recipient",
    "MISSION_decarb_advice_has_no_recipient",
    # 2026-08-28, atom A47, registered the day the figure landed. The page now claims the
    # household side of MONEY is instrumented; the probe asks for a READER outside the
    # defining module, because a module wired to nothing is the C2 defect in miniature.
    "MISSION_the_household_side_of_money_is_instrumented",
    # The same predicate on the RENDERED front door -- a claim-status defect there is the one a
    # visitor actually meets (R11).
    "SITE_the_front_door_says_the_household_saving_is_measured",
    # 2026-08-28. The canon page now states the arm's REACH (2.07% of renewals, electricity only),
    # which is a claim about a constant and therefore registerable. It reports SUPERSEDED the day
    # the arm widens -- the moment the coverage figures beside it stop being true.
    "MISSION_the_pricing_arm_is_electricity_only",
})

PAGE_TEXT = """# A PAGE

The world expresses one trait: `price_sensitivity` reaches the churn decision.
`green_stance` is drawn and read by no response function at all.
"""

CHANNEL_CLAIM = {
    "id": "channel_exists",
    "page": "docs/page.md",
    "anchor": "`price_sensitivity` reaches the churn decision",
    "claim": "price_sensitivity is read by the world",
    "expects": "present",
    "probe": {"kind": "token_live", "token": "price_elasticity_for_customer",
              "roots": ["simulation"], "exclude": ["simulation/population_draw.py"]},
}

NO_CHANNEL_CLAIM = {
    "id": "no_channel",
    "page": "docs/page.md",
    "anchor": "`green_stance` is drawn and read by no response function at all",
    "claim": "green_stance is read by nothing",
    "expects": "absent",
    "probe": {"kind": "token_live", "token": "green_stance",
              "roots": ["simulation"], "exclude": ["simulation/population_draw.py"]},
}


def _mini_repo(tmp_path: Path, *, channel: bool = True, green_channel: bool = False,
               claims: list[dict] | None = None, page: str = PAGE_TEXT) -> tuple[Path, Path]:
    """A whole miniature repo: a page, a register, and a `simulation/` package."""
    (tmp_path / "docs").mkdir(exist_ok=True)
    (tmp_path / "docs/page.md").write_text(page, encoding="utf-8")
    sim = tmp_path / "simulation"
    sim.mkdir(exist_ok=True)
    (sim / "population_draw.py").write_text(
        "def price_elasticity_for_customer(account, seed):\n    return 1.0\n\n"
        "GREEN = 'green_stance'\n",
        encoding="utf-8",
    )
    body = ["from simulation.population_draw import price_elasticity_for_customer\n\n"] if channel else []
    body.append("def roll(account):\n")
    body.append("    return price_elasticity_for_customer(account, 1)\n" if channel else "    return 1.0\n")
    if green_channel:
        body.append("\ndef react(account):\n    return account['green_stance'] * 2\n")
    (sim / "customer_events.py").write_text("".join(body), encoding="utf-8")
    register = tmp_path / "register.yaml"
    register.write_text(yaml.safe_dump({"claims": claims if claims is not None else [CHANNEL_CLAIM]}),
                        encoding="utf-8")
    return tmp_path, register


def _verdicts(root: Path, register: Path) -> dict[str, str]:
    return {v.claim.id: v.verdict for v in run(root, register)[0]}


# ---------------------------------------------------------------- the two mutations that matter

def test_a_channel_that_disappears_reports_over_claim(tmp_path):
    """The page says the trait reaches the world; the call is gone. That is an OVER_CLAIM."""
    root, register = _mini_repo(tmp_path, channel=False)
    assert _verdicts(root, register) == {"channel_exists": OVER_CLAIM}


def test_a_channel_that_appears_reports_superseded(tmp_path):
    """C1's real shape: the page says nothing reads the trait, and something now does.

    A check that only knew how to report over-claiming would call this HOLDS and be confidently
    wrong — which is exactly what happened to C1 by hand on 2026-08-28.
    """
    root, register = _mini_repo(tmp_path, green_channel=True, claims=[NO_CHANNEL_CLAIM])
    assert _verdicts(root, register) == {"no_channel": SUPERSEDED}


def test_the_unmutated_fixture_holds_both_ways(tmp_path):
    """The null rung: with the code as the page describes it, both claims HOLD.

    Without this, a check that returned drift unconditionally would pass both mutations above.
    """
    root, register = _mini_repo(tmp_path, claims=[CHANNEL_CLAIM, NO_CHANNEL_CLAIM])
    assert _verdicts(root, register) == {"channel_exists": HOLDS, "no_channel": HOLDS}


# ---------------------------------------------------------------- prose is not a channel

@pytest.mark.parametrize("prose", [
    '"""A module that mentions green_stance in its docstring."""\n\ndef f():\n    return 1\n',
    "# green_stance is deliberately not read here\ndef f():\n    return 1\n",
    "def f():\n    \"\"\"Reads green_stance one day, not today.\"\"\"\n    return 1\n",
])
def test_a_prose_mention_is_not_a_channel(tmp_path, prose):
    """The discriminator the 2026-08-28 verdict applied by hand: a grep would call this a channel."""
    root, register = _mini_repo(tmp_path, claims=[NO_CHANNEL_CLAIM])
    (root / "simulation/notes.py").write_text(prose, encoding="utf-8")
    assert _verdicts(root, register) == {"no_channel": HOLDS}


def test_live_source_keeps_real_code_it_strips_only_prose(tmp_path):
    """The strip must not be so keen that it hides a real read (the opposite failure)."""
    path = tmp_path / "m.py"
    path.write_text('"""doc."""\n# comment\nX = {"green_stance": 1}\n', encoding="utf-8")
    stripped = live_source(path)
    assert "green_stance" in stripped and "doc." not in stripped and "comment" not in stripped


# ---------------------------------------------------------------- fail-closed shapes

def test_an_anchor_removed_from_the_page_reports_unbound_not_a_pass(tmp_path):
    """The register going stale is drift. Silently skipping the claim would be the fail-open."""
    root, register = _mini_repo(tmp_path, page="# A PAGE\n\nNothing that was here is here now.\n")
    assert _verdicts(root, register) == {"channel_exists": UNBOUND}


def test_a_probe_over_a_missing_path_is_error_not_holds(tmp_path):
    """An unavailable check is a FAILED check — the probe's roots must actually exist."""
    root, register = _mini_repo(tmp_path)
    claim = Claim(id="x", page="docs/page.md", anchor="`price_sensitivity` reaches the churn decision",
                  claim="c", expects="absent",
                  probe={"kind": "token_live", "token": "z", "roots": ["no_such_dir"]})
    verdict = evaluate(claim, root)
    assert verdict.verdict == ERROR and "no_such_dir" in verdict.detail


def test_a_file_that_will_not_parse_is_an_error_not_a_pass(tmp_path):
    root, register = _mini_repo(tmp_path, claims=[NO_CHANNEL_CLAIM])
    (root / "simulation/broken.py").write_text("def (:\n", encoding="utf-8")
    assert _verdicts(root, register) == {"no_channel": ERROR}


def test_a_missing_page_is_an_error_not_a_pass(tmp_path):
    root, register = _mini_repo(tmp_path)
    (root / "docs/page.md").unlink()
    assert _verdicts(root, register) == {"channel_exists": ERROR}


@pytest.mark.parametrize("content", ["", "claims: []\n", "claims: null\n", "not_a_mapping\n"])
def test_an_empty_or_malformed_register_is_unusable_not_a_pass(tmp_path, content):
    register = tmp_path / "r.yaml"
    register.write_text(content, encoding="utf-8")
    with pytest.raises(ProbeError):
        load_register(register)


def test_a_missing_register_is_unusable_not_a_pass(tmp_path):
    with pytest.raises(ProbeError):
        load_register(tmp_path / "nope.yaml")


@pytest.mark.parametrize("bad", [
    {"expects": "maybe"},
    {"probe": {"kind": "invented_probe"}},
    {"anchor": None, "_drop": "anchor"},
])
def test_a_register_entry_that_cannot_be_checked_is_refused_at_load(tmp_path, bad):
    entry = dict(CHANNEL_CLAIM)
    entry.update({k: v for k, v in bad.items() if not k.startswith("_")})
    entry.pop(bad.get("_drop", ""), None)
    register = tmp_path / "r.yaml"
    register.write_text(yaml.safe_dump({"claims": [entry]}), encoding="utf-8")
    with pytest.raises(ProbeError):
        load_register(register)


def test_duplicate_claim_ids_are_refused(tmp_path):
    register = tmp_path / "r.yaml"
    register.write_text(yaml.safe_dump({"claims": [CHANNEL_CLAIM, dict(CHANNEL_CLAIM)]}), encoding="utf-8")
    with pytest.raises(ProbeError):
        load_register(register)


# ---------------------------------------------------------------- the other probe kinds

def test_the_module_name_probe_does_not_count_documents(tmp_path):
    """C2 exactly: eleven files named 'competitor' and every one a document."""
    root, _ = _mini_repo(tmp_path)
    (root / "docs/COMPETITOR_FRAME.md").write_text("a frame", encoding="utf-8")
    claim = Claim(id="rival", page="docs/page.md", anchor="`price_sensitivity` reaches the churn decision",
                  claim="a module models a rival", expects="present",
                  probe={"kind": "module_name", "roots": ["simulation", "docs"], "pattern": "competitor|rival"})
    assert evaluate(claim, root).verdict == OVER_CLAIM
    (root / "simulation/competitor_reference.py").write_text("RATE = 1.0\n", encoding="utf-8")
    assert evaluate(claim, root).verdict == HOLDS


def test_the_literal_probe_reads_the_value_not_only_the_name(tmp_path):
    """A constant that changed value is a different world; matching the NAME alone is fail-open."""
    root, _ = _mini_repo(tmp_path)
    (root / "simulation/consts.py").write_text("PRICE_DIFFERENTIAL_PCT = 0.05\n", encoding="utf-8")
    claim = Claim(id="k", page="docs/page.md", anchor="`price_sensitivity` reaches the churn decision",
                  claim="market position is a run-level constant at zero", expects="present",
                  probe={"kind": "literal_assign", "file": "simulation/consts.py",
                         "name": "PRICE_DIFFERENTIAL_PCT", "value": 0.0})
    assert evaluate(claim, root).verdict == OVER_CLAIM
    (root / "simulation/consts.py").write_text("PRICE_DIFFERENTIAL_PCT = 0.0\n", encoding="utf-8")
    assert evaluate(claim, root).verdict == HOLDS


def test_the_import_probe_catches_a_submodule_import(tmp_path):
    root, _ = _mini_repo(tmp_path)
    claim = Claim(id="i", page="docs/page.md", anchor="`price_sensitivity` reaches the churn decision",
                  claim="the world cannot reach the company's risk organs", expects="absent",
                  probe={"kind": "import_edge", "roots": ["simulation"], "target": "company.risk"})
    assert evaluate(claim, root).verdict == HOLDS
    (root / "simulation/squeeze.py").write_text(
        "from company.risk.liquidity_stress_test import run\n", encoding="utf-8")
    assert evaluate(claim, root).verdict == SUPERSEDED


# ---------------------------------------------------------------- the instrument as shipped

def test_exit_status_is_zero_only_when_every_claim_holds(tmp_path, capsys):
    root, register = _mini_repo(tmp_path)
    assert main(["--root", str(root), "--register", str(register)]) == 0
    (root / "simulation/customer_events.py").write_text("def roll(a):\n    return 1.0\n", encoding="utf-8")
    assert main(["--root", str(root), "--register", str(register)]) == 1


def test_an_unusable_register_exits_two_and_says_so(tmp_path, capsys):
    root, _ = _mini_repo(tmp_path)
    assert main(["--root", str(root), "--register", str(tmp_path / "gone.yaml")]) == 2
    assert "UNAVAILABLE" in capsys.readouterr().err


def test_the_json_report_names_every_drifting_claim(tmp_path, capsys):
    root, register = _mini_repo(tmp_path, channel=False)
    main(["--root", str(root), "--register", str(register), "--json"])
    report = json.loads(capsys.readouterr().out)
    assert report["claims_checked"] == 1
    assert [d["id"] for d in report["drift"]] == ["channel_exists"]
    assert report["counts"] == {OVER_CLAIM: 1}


# ---------------------------------------------------------------- the LIVE register

def test_the_live_register_membership_is_pinned_literally():
    ids = {c.id for c in load_register(LIVE_REGISTER)}
    assert ids == EXPECTED_CLAIM_IDS, (
        "the live claim register changed shape — a claim dropped silently is the canon going "
        "unwatched, which is the defect this atom exists for"
    )


def test_every_live_claim_is_bound_to_a_sentence_still_on_its_page():
    """UNBOUND at HEAD means the page moved and the register did not follow.

    This is the test that makes the register maintained: edit a canon page's claim and this goes
    red until the register is brought with it.
    """
    unbound = [v.claim.id for v in run(REPO_ROOT, LIVE_REGISTER)[0] if v.verdict == UNBOUND]
    assert unbound == [], f"register anchors no longer on their pages: {unbound}"


def test_no_live_claim_reports_error():
    """ERROR means the INSTRUMENT is broken (a missing path, an unparseable file), which is a
    different thing from the canon having drifted, and it must never be tolerated silently."""
    broken = [(v.claim.id, v.detail) for v in run(REPO_ROOT, LIVE_REGISTER)[0] if v.verdict == ERROR]
    assert broken == [], f"probes could not run: {broken}"


def test_the_daily_self_note_actually_asks_the_question():
    """The TRIGGER, not just the arm. A standing check nothing runs is the shape this project
    keeps catching in its own instruments — the atom is 'something OTHER THAN THE DIRECTOR asks'."""
    from background.daily_self_note import render_note
    note = render_note("2026-08-28T09:00:00Z")
    assert "**Canon drift**" in note
    assert "canon drift:" in note and "registered claim(s)" in note


def test_the_note_goes_red_rather_than_silent_when_the_check_cannot_run(monkeypatch):
    """FAIL-SILENT killer: an unavailable check must read as RED in the note, never as no drift."""
    import tools.canon_drift_check as module
    from background.daily_self_note import render_note

    def boom(*_a, **_k):
        raise ProbeError("register missing")

    monkeypatch.setattr(module, "note_line", boom)
    note = render_note("2026-08-28T09:00:00Z")
    assert "canon drift check unavailable" in note and "🔴 RED" in note


def test_the_shipped_entrypoint_runs_as_a_module():
    """R2-adjacent: the thing an orientation actually invokes is the command line, not the import."""
    proc = subprocess.run([sys.executable, "-m", "tools.canon_drift_check", "--json"],
                          cwd=REPO_ROOT, capture_output=True, text=True, timeout=180)
    assert proc.returncode in (0, 1), proc.stderr
    assert json.loads(proc.stdout)["claims_checked"] == len(EXPECTED_CLAIM_IDS)
