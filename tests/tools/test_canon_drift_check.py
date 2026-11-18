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
    lapsed_watches,
    live_source,
    load_judgements,
    load_register,
    main,
    mint_drift_item,
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
    "C3_arrears_do_not_meet_the_bill",
    # Renamed 2026-08-29 when the correction they were waiting for landed on both rendered
    # surfaces. The old ids named today's verdict ("still says"); these name the property.
    # 2026-10-24: ..._only_one_trait_expresses retired (see `_retired`); the diagram steer took
    # the trait count off the picture, and C1_green_stance_carries_no_channel still binds it.
    "SITE_the_schematic_says_survival_is_not_yet_at_risk",
    "SITE_the_company_card_says_survival_is_not_yet_at_risk",
    # 2026-10-09: TIMEFRAME 1 read line by line; two corrections and the ledger half they split off.
    "CARBON_the_three_ledger_is_called_by_nothing",
    "CARBON_a_households_emissions_are_measured_and_published",
    "PRICING_the_forward_belief_window_adapts",
    # 2026-11-14, from the unbound-negatives list: the cap sentence, said twice on the page.
    "PRICING_the_renewal_desk_clamps_at_the_competitive_ceiling",
    "PRICING_the_ceiling_is_102_pct_of_the_published_svt",
    "PRICING_the_ceiling_tightens_to_97_pct",
    # 2026-08-28, the director's mission rewrite. The mission names three channels through which
    # value reaches a household -- modelling, tariffs, advice -- and THE MODEL ON A PAGE now states
    # that advice has modules on disk and no recipient. That is a CHANNEL claim of C1's exact shape
    # (the thing exists; does the WORLD call it?), so it is registerable and is registered.
    # Two claims rather than one on purpose: the recommenders can gain a recipient independently.
    "MISSION_switching_advice_has_no_recipient",
    # MISSION_decarb_advice_has_no_recipient retired 2026-11-14: the recommender is archived,
    # so its token is in no live code and the claim could not go red (see `_retired`).
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
    "MISSION_the_pricing_arm_prices_both_fuels",  # re-pointed 2026-10-04, see _retired
    # 2026-11-12: three of the six sections the coverage leg named unwatched gained a claim;
    # the first is the factual correction that pass found (no /simplified redirect survives).
    "OPEN_FINDINGS_no_simplified_redirect_survives",
    "TF2_the_worlds_cant_pay_wont_pay_key_drives_nothing",
    "PICTURE_the_svg_is_generated_at_publish",
    # 2026-11-15, bound from the unbound-negatives list: the share is read by no decision surface.
    "MISSION_the_household_share_is_read_by_no_decision_surface",
    # 2026-11-15, the per-section MINOR: the tariffs channel, the one the page calls LIVE.
    "MISSION_the_offered_rate_reaches_the_churn_decision",
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
    assert evaluate(claim, root).verdict == ERROR  # the organ does not exist: nothing to watch
    (root / "company/risk").mkdir(parents=True)
    (root / "company/risk/__init__.py").write_text("", encoding="utf-8")
    assert evaluate(claim, root).verdict == HOLDS
    (root / "simulation/squeeze.py").write_text(
        "from company.risk.liquidity_stress_test import run\n", encoding="utf-8")
    assert evaluate(claim, root).verdict == SUPERSEDED


def test_the_import_probe_catches_a_module_imported_by_its_leaf_name(tmp_path):
    """`from package import module` names the module only in the alias, never in `node.module`."""
    root, _ = _mini_repo(tmp_path)
    claim = Claim(id="i", page="docs/page.md", anchor="`price_sensitivity` reaches the churn decision",
                  claim="nothing calls the carbon ledger", expects="absent",
                  probe={"kind": "import_edge", "roots": ["simulation"], "target": "company.carbon.ledger"})
    (root / "company/carbon").mkdir(parents=True)
    (root / "company/carbon/ledger.py").write_text("X = 1\n", encoding="utf-8")
    assert evaluate(claim, root).verdict == HOLDS
    (root / "simulation/tally.py").write_text("from company.carbon import ledger\n", encoding="utf-8")
    assert evaluate(claim, root).verdict == SUPERSEDED


# ---------------------------------------------------------------- an absent claim must be able to flip
# Expert Hour, 2026-11-14: 5 of 20 live claims HELD by finding nothing, and could never have found
# anything -- a token no file held, a renamed constant, an archived module.

def _absent_token_claim(token: str) -> Claim:
    return Claim(id="v", page="docs/page.md", anchor="`price_sensitivity` reaches the churn decision",
                 claim="the world never reads it", expects="absent",
                 probe={"kind": "token_live", "token": token, "roots": ["simulation"]})


def test_an_absent_claim_on_a_name_no_code_holds_is_an_error_not_a_hold(tmp_path):
    root, _ = _mini_repo(tmp_path)
    assert evaluate(_absent_token_claim("collateral_call"), root).verdict == ERROR
    # Partition control: the same claim on a name that IS real somewhere outside its roots holds.
    (root / "company").mkdir()
    (root / "company/desk.py").write_text("def collateral_call():\n    return 0\n", encoding="utf-8")
    assert evaluate(_absent_token_claim("collateral_call"), root).verdict == HOLDS


def test_a_name_held_only_in_prose_is_no_witness(tmp_path):
    root, _ = _mini_repo(tmp_path)
    (root / "company").mkdir()
    (root / "company/desk.py").write_text('"""collateral_call is not built."""\n', encoding="utf-8")
    assert evaluate(_absent_token_claim("collateral_call"), root).verdict == ERROR


def _literal_claim(spec: dict, expects: str = "present") -> Claim:
    return Claim(id="k", page="docs/page.md", anchor="`price_sensitivity` reaches the churn decision",
                 claim="a constant", expects=expects,
                 probe={"kind": "literal_assign", "file": "simulation/consts.py", **spec})


def test_a_literal_probe_on_a_renamed_constant_is_an_error_not_a_hold(tmp_path):
    root, _ = _mini_repo(tmp_path)
    (root / "simulation/consts.py").write_text("UPLIFTABLE_COMMODITIES = frozenset({'electricity'})\n",
                                               encoding="utf-8")
    claim = _literal_claim({"name": "UPLIFTABLE_COMMODITY", "value": "electricity"}, expects="absent")
    assert evaluate(claim, root).verdict == ERROR


def test_a_value_the_literal_probe_cannot_read_is_an_error_not_skipped(tmp_path):
    root, _ = _mini_repo(tmp_path)
    (root / "simulation/consts.py").write_text("ARM = build_arm()\n", encoding="utf-8")
    assert evaluate(_literal_claim({"name": "ARM", "value": 1}, expects="absent"), root).verdict == ERROR


def test_a_membership_guard_is_read_through_its_frozenset(tmp_path):
    root, _ = _mini_repo(tmp_path)
    consts = root / "simulation/consts.py"
    claim = _literal_claim({"name": "UPLIFTABLE_COMMODITIES", "contains": "gas"})
    consts.write_text("UPLIFTABLE_COMMODITIES: frozenset[str] = frozenset({'electricity', 'gas'})\n",
                      encoding="utf-8")
    assert evaluate(claim, root).verdict == HOLDS
    consts.write_text("UPLIFTABLE_COMMODITIES: frozenset[str] = frozenset({'electricity'})\n",
                      encoding="utf-8")
    assert evaluate(claim, root).verdict == OVER_CLAIM


def _call_claim() -> Claim:
    return Claim(id="c", page="docs/page.md", anchor="`price_sensitivity` reaches the churn decision",
                 claim="the margin-call book is marked once, at the run's end", expects="absent",
                 probe={"kind": "call_site", "function": "build_counterparty_collateral",
                        "roots": ["simulation"], "keyword": "mark_date", "value": "effective_end"})


@pytest.mark.parametrize("mark, verdict", [
    ("effective_end", HOLDS),        # today's world: one mark, after the loop
    ("month_end", SUPERSEDED),       # a mark inside the loop is a call the world can press with
    (None, ERROR),                   # no call at all: the probe watches nothing
])
def test_the_collateral_call_probe_can_hold_flip_and_refuse(tmp_path, mark, verdict):
    root, _ = _mini_repo(tmp_path)
    body = "def run(book, effective_end, month_end):\n"
    body += (f"    return seam.build_counterparty_collateral(book, mark_date={mark})\n"
             if mark else "    return book\n")
    (root / "simulation/run_loop.py").write_text(body, encoding="utf-8")
    assert evaluate(_call_claim(), root).verdict == verdict


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


# ---------------------------------------------------------------- the denominator beside "all HOLD"

SECTIONED_PAGE = """# A PAGE

## Watched
The world expresses one trait: `price_sensitivity` reaches the churn decision.

## Unwatched
A sentence nothing in the register is bound to.
"""


def test_a_section_with_no_bound_claim_is_named_and_a_bound_one_is_not(tmp_path):
    """'17 checked, 0 drifting' was printed with no denominator while six of ten sections of the
    model page carried no anchor. Both legs: the bare section is named, the bound one is not --
    so a leg that names everything, or nothing, fails one of them."""
    root, register = _mini_repo(tmp_path, page=SECTIONED_PAGE)
    unwatched = run(root, register)[1]["unwatched_sections"]["docs/page.md"]
    assert "Unwatched" in unwatched
    assert "Watched" not in unwatched


def test_coverage_never_moves_the_exit_status(tmp_path, capsys):
    """Coverage is not drift: an unwatched section must be printed, never turn the check red."""
    root, register = _mini_repo(tmp_path, page=SECTIONED_PAGE)
    assert main(["--root", str(root), "--register", str(register)]) == 0
    assert "UNWATCHED on docs/page.md" in capsys.readouterr().out


# ---------------------------------------------------------------- unbound negatives (Expert Hour MAJOR 3)

#: The 14 Nov shape in miniature. One sentence, an anchored clause, and a "not yet" outside it.
#: The anchor made the sentence (and its section) read watched while its negative went unchecked.
NEGATIVES_PAGE = """# A PAGE

## Spine
`price_sensitivity` reaches the churn decision, and competition does not press yet: a rival is blocked.

## Bound
`green_stance` is read by no response function.

## Prose
The household is never converted to pounds.
"""


def test_a_negative_outside_every_anchor_is_named_even_in_a_bound_sentence(tmp_path):
    """Three legs over the whole partition, so a leg that names everything or nothing fails one.

    Named: "blocked", outside the anchor in an otherwise-bound sentence (the MAJOR 3 case).
    Not named: "read by no", inside an anchor. Not named: "never", outside the lexicon (rule prose).
    """
    green = dict(NO_CHANNEL_CLAIM, anchor="`green_stance` is read by no response function")
    root, register = _mini_repo(tmp_path, page=NEGATIVES_PAGE, claims=[CHANNEL_CLAIM, green])
    named = run(root, register)[1]["unbound_negatives"]["docs/page.md"]
    assert len(named) == 1 and "a rival is blocked" in named[0], named
    assert not any("green_stance" in s or "never converted" in s for s in named)


#: A45's blind pass, 15 Nov, MAJOR 2: four negatives from the model page with no "not yet" in them,
#: and one rule sentence that asserts no missing mechanism.
UNPHRASED_NEGATIVES_PAGE = """# A PAGE

## Spine
`price_sensitivity` reaches the churn decision.

## Prose
Nothing optimises the household figure.
The score has no household-side term in any currency.
Nothing it computes is ever offered to the household it is about.
So over-pricing still carries no competitive consequence.
Ground truth never crosses the wall.
"""


def test_a_negative_with_no_not_yet_in_it_is_named(tmp_path):
    """Each of MAJOR 2's four phrasings is named on its own sentence, and the rule sentence is not:
    a lexicon that names nothing fails the first leg, one that names everything fails the second."""
    root, register = _mini_repo(tmp_path, page=UNPHRASED_NEGATIVES_PAGE, claims=[CHANNEL_CLAIM])
    named = run(root, register)[1]["unbound_negatives"]["docs/page.md"]
    for phrase in ("Nothing optimises", "no household-side term", "Nothing it computes",
                   "carries no competitive"):
        assert sum(phrase in s for s in named) == 1, (phrase, named)
    assert len(named) == 4 and not any("never crosses" in s for s in named), named


def test_an_also_anchor_binds_its_sentence_and_its_removal_is_unbound(tmp_path):
    """One predicate the page states twice. The second copy is bound by `also_anchors`, so its
    negative is no longer named -- and if that copy leaves the page the claim is UNBOUND, exactly
    as for the first anchor. Without the second anchor the negative IS named (the leg can fail)."""
    green = dict(NO_CHANNEL_CLAIM, anchor="`green_stance` is read by no response function")
    root, register = _mini_repo(tmp_path, page=NEGATIVES_PAGE, claims=[CHANNEL_CLAIM, green])
    assert run(root, register)[1]["unbound_negatives"]["docs/page.md"]  # "blocked" named
    green["also_anchors"] = ["a rival is blocked"]
    register.write_text(yaml.safe_dump({"claims": [CHANNEL_CLAIM, green]}), encoding="utf-8")
    verdicts, report = run(root, register)
    assert report["unbound_negatives"]["docs/page.md"] == []
    assert {v.claim.id: v.verdict for v in verdicts}[green["id"]] == HOLDS
    (root / "docs/page.md").write_text(NEGATIVES_PAGE.replace("a rival is blocked", "a rival moves"),
                                       encoding="utf-8")
    assert {v.claim.id: v.verdict for v in run(root, register)[0]}[green["id"]] == UNBOUND


def test_an_unbound_negative_is_printed_and_never_moves_the_exit_status(tmp_path, capsys):
    green = dict(NO_CHANNEL_CLAIM, anchor="`green_stance` is read by no response function")
    root, register = _mini_repo(tmp_path, page=NEGATIVES_PAGE, claims=[CHANNEL_CLAIM, green])
    assert main(["--root", str(root), "--register", str(register)]) == 0
    out = capsys.readouterr().out
    assert "UNBOUND NEGATIVES on docs/page.md -- 1" in out
    assert "a rival is blocked" in out  # the sentence itself, not only its count


# ---------------------------------------------------------------- judged negatives (MAJOR 3 residual)

def _judged_repo(tmp_path: Path, judged: list[dict]) -> tuple[Path, Path]:
    green = dict(NO_CHANNEL_CLAIM, anchor="`green_stance` is read by no response function")
    root, register = _mini_repo(tmp_path, page=NEGATIVES_PAGE, claims=[CHANNEL_CLAIM, green])
    register.write_text(yaml.safe_dump({"claims": [CHANNEL_CLAIM, green], "_judged_negatives": judged}),
                        encoding="utf-8")
    return root, register


RIVAL_JUDGED = {"page": "docs/page.md", "excerpt": "a rival is blocked", "kind": "no_witness",
                "why": "no rival module exists to watch", "watch_none": "the fixture has no map"}


def test_a_judged_negative_is_settled_and_an_edited_sentence_is_named_again(tmp_path):
    """Three legs: unjudged it is named; judged it is not; its sentence edited, it is named again
    (and the stale row is reported), so a judgement can never outlive the words it judged."""
    root, register = _judged_repo(tmp_path, [])
    assert run(root, register)[1]["unbound_negatives"]["docs/page.md"]
    root, register = _judged_repo(tmp_path, [RIVAL_JUDGED])
    report = run(root, register)[1]
    assert report["unbound_negatives"]["docs/page.md"] == [] and report["judged_negatives"] == 1
    assert report["stale_judgements"] == []
    (root / "docs/page.md").write_text(
        NEGATIVES_PAGE.replace("a rival is blocked", "a rival is not yet blocking"), encoding="utf-8")
    report = run(root, register)[1]
    assert any("not yet blocking" in s for s in report["unbound_negatives"]["docs/page.md"])
    assert report["stale_judgements"] == ["docs/page.md: a rival is blocked"]


def test_a_summary_judgement_lapses_when_its_claim_stops_holding(tmp_path):
    summary = {"page": "docs/page.md", "excerpt": "a rival is blocked", "kind": "summary",
               "of": ["no_channel"], "why": "restates the green claim"}
    root, register = _judged_repo(tmp_path, [summary])
    assert run(root, register)[1]["unbound_negatives"]["docs/page.md"] == []
    root, register = _mini_repo(tmp_path, page=NEGATIVES_PAGE, green_channel=True)  # green now read
    green = dict(NO_CHANNEL_CLAIM, anchor="`green_stance` is read by no response function")
    register.write_text(yaml.safe_dump({"claims": [CHANNEL_CLAIM, green], "_judged_negatives": [summary]}),
                        encoding="utf-8")
    verdicts, report = run(root, register)
    assert {v.claim.id: v.verdict for v in verdicts}["no_channel"] == SUPERSEDED
    assert any("a rival is blocked" in s for s in report["unbound_negatives"]["docs/page.md"])


@pytest.mark.parametrize("row", [
    dict(RIVAL_JUDGED, why=" "),
    dict(RIVAL_JUDGED, kind="seems_fine"),
    dict(RIVAL_JUDGED, kind="summary"),
    dict(RIVAL_JUDGED, kind="summary", of=["no_such_claim"]),
], ids=["empty_why", "unknown_kind", "summary_without_of", "summary_of_unknown_claim"])
def test_a_malformed_judgement_refuses_rather_than_hides(tmp_path, capsys, row):
    root, register = _judged_repo(tmp_path, [row])
    with pytest.raises(ProbeError):
        run(root, register)
    assert main(["--root", str(root), "--register", str(register)]) == 2


def test_a_judged_negative_is_counted_on_the_surface_and_never_moves_the_exit_status(tmp_path, capsys):
    root, register = _judged_repo(tmp_path, [RIVAL_JUDGED])
    assert main(["--root", str(root), "--register", str(register)]) == 0
    assert "JUDGED NEGATIVES -- 1 named sentence(s)" in capsys.readouterr().out


# ---------------------------------------------------------------- a no_witness row watches its atom (M4)

def _watched_repo(tmp_path: Path, level: int) -> tuple[Path, Path]:
    root, register = _judged_repo(tmp_path, [dict(
        {k: v for k, v in RIVAL_JUDGED.items() if k != "watch_none"},
        watch={"atom": "W9_rival", "level": 1, "target": 2})])
    (root / "docs/design").mkdir(parents=True, exist_ok=True)
    (root / "docs/design/maturity_map.yaml").write_text(yaml.safe_dump(
        [{"id": "W9_rival", "level_current": level, "level_target": 2}]), encoding="utf-8")
    return root, register


def test_a_watched_judgement_holds_until_its_atom_moves_and_then_reds_and_mints(tmp_path, capsys):
    """The partition: at the judged level the sentence is settled and the check is green; once the
    atom that would build the rival moves, the sentence is named again, the check exits 1, and the
    lapse mints a work item. C2's shape: the mechanism landed while the page said it had not."""
    root, register = _watched_repo(tmp_path, level=1)
    report = run(root, register)[1]
    assert report["lapsed_watches"] == [] and report["unbound_negatives"]["docs/page.md"] == []
    assert main(["--root", str(root), "--register", str(register)]) == 0
    root, register = _watched_repo(tmp_path, level=2)
    report = run(root, register)[1]
    assert len(report["lapsed_watches"]) == 1 and "W9_rival was L1/T2" in report["lapsed_watches"][0]
    assert any("a rival is blocked" in s for s in report["unbound_negatives"]["docs/page.md"])
    assert main(["--root", str(root), "--register", str(register)]) == 1
    assert "[LAPSED WATCH]" in capsys.readouterr().out
    minted = mint_drift_item(report, tmp_path / "staging", today="2026-11-15")
    assert minted is not None and "LAPSED" in minted.read_text(encoding="utf-8")


@pytest.mark.parametrize("row", [
    {k: v for k, v in RIVAL_JUDGED.items() if k != "watch_none"},
    dict(RIVAL_JUDGED, watch_none=" "),
    dict(RIVAL_JUDGED, kind="not_about_code", watch_none="x"),
    dict({k: v for k, v in RIVAL_JUDGED.items() if k != "watch_none"}, watch={"atom": "W9_rival", "level": 1}),
    dict({k: v for k, v in RIVAL_JUDGED.items() if k != "watch_none"},
         watch={"atom": "NO_such_atom", "level": 1, "target": 2}),
], ids=["no_witness_unwatched", "empty_watch_none", "watch_on_other_kind", "watch_without_target",
        "watch_on_unknown_atom"])
def test_a_watch_that_could_never_fire_refuses(tmp_path, row):
    root, register = _watched_repo(tmp_path, level=1)
    register.write_text(yaml.safe_dump({**yaml.safe_load(register.read_text(encoding="utf-8")),
                                        "_judged_negatives": [row]}), encoding="utf-8")
    with pytest.raises(ProbeError):
        run(root, register)


def test_every_live_no_witness_row_watches_an_atom_the_map_holds():
    """Live: no no_witness judgement is unwatched without a reason, and each watched atom exists
    (run() refuses otherwise). Lapses are left to the check's exit status, not pinned here."""
    judgements = load_judgements(LIVE_REGISTER, {c.id for c in load_register(LIVE_REGISTER)})
    assert [j for j in judgements if j.kind == "no_witness" and j.watch] , "no live row watches an atom"
    lapsed_watches(REPO_ROOT, judgements)   # raises on an atom no map holds


def test_no_live_judgement_is_stale():
    """A live judgement whose excerpt left the page judges nothing; clear or rebind it."""
    assert run(REPO_ROOT, LIVE_REGISTER)[1]["stale_judgements"] == []


# ---------------------------------------------------------------- a red mints work (Expert Hour MAJOR 2)

def _note_repo(tmp_path: Path, *, channel: bool) -> Path:
    """`note_line` reads the default register path, so the fixture register goes there."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    root, register = _mini_repo(tmp_path, channel=channel, claims=[CHANNEL_CLAIM])
    target = root / "docs/design/canon_claims.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(register.read_text(encoding="utf-8"), encoding="utf-8")
    return root


def _minted(root: Path) -> list[Path]:
    from tools.canon_drift_check import DRIFT_ITEM_STEM
    return sorted((root / "docs/staging").rglob(f"{DRIFT_ITEM_STEM}*.md"))


def test_a_red_register_mints_one_classified_work_item_and_a_green_one_mints_none(tmp_path):
    """MAJOR 2: before this, a red changed one line of the daily note and filed nothing.

    Both legs of the partition in one test: a green register must mint nothing (a mint that fires
    unconditionally passes every red-only test), and a red one must mint exactly one item, read by
    the same severity parser the draw uses, and not a second one when the next note sees the same
    drift.
    """
    from background.finding_severity import parse_severity_text
    from tools.canon_drift_check import note_line

    green = _note_repo(tmp_path / "green", channel=True)
    assert "all HOLD" in note_line(green)
    assert _minted(green) == []

    red = _note_repo(tmp_path / "red", channel=False)
    line = note_line(red)
    items = _minted(red)
    assert len(items) == 1, items
    assert f"Minted `{items[0].name}`" in line
    text = items[0].read_text(encoding="utf-8")
    parsed = parse_severity_text(text, items[0])
    assert (parsed.severity, parsed.lane) == ("BLOCKING", "A_strategy_governance")  # an OVER_CLAIM
    assert "`channel_exists` | OVER_CLAIM" in text

    note_line(red)  # the next morning, same drift
    assert _minted(red) == items


def test_a_closed_item_is_not_reminted_and_a_different_drift_is(tmp_path):
    """The dedup reads every room, so a drift item moved to done/ stays closed; a NEW drift set
    is a new item, and a non-OVER_CLAIM red is LATENT."""
    from tools.canon_drift_check import mint_drift_item

    root, register = _mini_repo(tmp_path, channel=False, claims=[CHANNEL_CLAIM])
    staging = root / "docs/staging"
    first = mint_drift_item(run(root, register)[1], staging, today="2026-11-14")
    done = staging / "done"
    done.mkdir()
    first.rename(done / first.name)
    assert mint_drift_item(run(root, register)[1], staging, today="2026-11-15") is None

    (tmp_path / "b").mkdir()
    root2, register2 = _mini_repo(tmp_path / "b", green_channel=True, claims=[NO_CHANNEL_CLAIM])
    second = mint_drift_item(run(root2, register2)[1], staging, today="2026-11-15")
    assert second is not None and second.name != first.name
    assert second.read_text(encoding="utf-8").startswith("**Severity:** LATENT")


# ---------------------------------------------------------------- the `called` probe

def _called_claim(expects: str) -> Claim:
    return Claim(id="c", page="docs/page.md", anchor="`price_sensitivity` reaches the churn decision",
                 claim="the roll reads the offered rate", expects=expects,
                 probe={"kind": "called", "function": "_differential", "roots": ["simulation"]})


@pytest.mark.parametrize("body, expects, verdict", [
    # The live shape: defined and called. Present holds; absent is superseded.
    ("def _differential(r):\n    return r\n\ndef roll(r):\n    return _differential(r)\n", "present", HOLDS),
    ("def _differential(r):\n    return r\n\ndef roll(r):\n    return _differential(r)\n", "absent", SUPERSEDED),
    # The defect it was written for: the call cut, the def left. A token probe stayed green here.
    ("def _differential(r):\n    return r\n\ndef roll(r):\n    return 1.0\n", "present", OVER_CLAIM),
    ("def _differential(r):\n    return r\n\ndef roll(r):\n    return 1.0\n", "absent", HOLDS),
    # No such function anywhere: an absent claim watches a name, so it refuses.
    ("def roll(r):\n    return 1.0\n", "absent", ERROR),
])
def test_the_called_probe_ignores_the_def_and_can_hold_flip_and_refuse(tmp_path, body, expects, verdict):
    root, _ = _mini_repo(tmp_path)
    (root / "simulation/customer_events.py").write_text(body, encoding="utf-8")
    assert evaluate(_called_claim(expects), root).verdict == verdict


def _with_site(root: Path, page: str) -> Path:
    """A served page and a one-quote canon beside the fixture register."""
    from tools.canon_drift_check import CANON_DOC
    (root / "site").mkdir()
    (root / "site" / "index.html").write_text(page, encoding="utf-8")
    (root / CANON_DOC).parent.mkdir(parents=True, exist_ok=True)
    (root / CANON_DOC).write_text('**M1.** "We are creating enterprise value by automating ways to '
                                  'find individual customers we can create value for."\n', encoding="utf-8")
    return root


def test_the_scheduled_note_asks_the_site_leg_and_mints_its_red(tmp_path):
    """A45 blind pass, 15 Nov, MINOR: the site leg ran from `main()` only, so the daily note -- the
    trigger -- never asked it, and a withdrawn mission line on a served page reached no one.

    Both legs on the SAME green register: a site that holds mints nothing and prints its own
    denominator (a note that drops the leg would pass a red-only test), and a site carrying a
    superseded framing goes red in the line and mints one BLOCKING item, once.
    """
    from background.finding_severity import parse_severity_text
    from tools.canon_drift_check import note_line

    holds = _with_site(_note_repo(tmp_path / "holds", channel=True), "<p>Saved CO2.</p>")
    line = note_line(holds)
    assert "all HOLD" in line and "Site leg: 1 served page(s) hold against 1 canon quote(s)" in line
    assert _minted(holds) == []

    red = _with_site(_note_repo(tmp_path / "red", channel=True), "<h1>The cheapest tonne of carbon</h1>")
    line = note_line(red)
    assert "SITE LEG RED: 1 line(s)" in line and "'cheapest tonne'" in line
    assert "all HOLD against the code" in line
    items = _minted(red)
    assert len(items) == 1, items
    text = items[0].read_text(encoding="utf-8")
    assert parse_severity_text(text, items[0]).severity == "BLOCKING"
    assert "| served page | SUPERSEDED | site/index.html |" in text
    note_line(red)  # the next morning, same drift
    assert _minted(red) == items


COVERAGE_PAGE = """# A PAGE

The world expresses one trait: `price_sensitivity` reaches the churn decision.
The engagement mix is 0.45/0.35/0.20 by ratification. `company/portal/app.py` renders the view.
Ground truth never crosses the wall.

- A bullet with no stop names `MARKET_SAVINGS_BY_YEAR`
- A bullet filed as `WORKER_FINDING_X_2026-11-16` and nothing else

```yaml
title: `simulation/customer_events.py` in the picture
```
"""


def test_the_per_sentence_denominator_counts_bound_unbound_and_plain_apart(tmp_path):
    """A45 blind pass, 15 Nov, MAJOR 1. One fixture over the whole partition: a bound sentence, two
    sentences naming code that nothing binds (one a stop-less bullet that must not run into the next),
    a plain rule sentence and a staging-item name that are not counted, and a fenced line read apart.
    `app.py` and 0.45 must not end a sentence. A denominator that counts nothing, or everything,
    fails a leg."""
    root, register = _mini_repo(tmp_path, page=COVERAGE_PAGE, claims=[CHANNEL_CLAIM])
    cov = run(root, register)[1]["sentence_coverage"]["docs/page.md"]
    assert cov["bound"] == 1 and cov["naming"] == 4, cov
    assert cov["sentences"] == 7 and cov["fenced_lines"] == 3, cov
    assert [s[:14] for s in cov["unbound"]] == ["The engagement", "`company/porta", "- A bullet wit"], \
        cov["unbound"]
    assert cov["unbound"][1].endswith("renders the view."), cov["unbound"]


def test_the_sentence_denominator_is_printed_and_never_moves_the_exit_status(tmp_path, capsys):
    from tools.canon_drift_check import main
    root, register = _mini_repo(tmp_path, page=COVERAGE_PAGE, claims=[CHANNEL_CLAIM])
    assert main(["--root", str(root), "--register", str(register)]) == 0
    out = capsys.readouterr().out
    assert "1 of 4 sentence(s) naming code or a figure are bound" in out, out
