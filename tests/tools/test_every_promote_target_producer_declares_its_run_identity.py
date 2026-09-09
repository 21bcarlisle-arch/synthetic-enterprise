"""Every producer of a promote-by-copy target names which of its fields are its run identity.

THE DEFECT THIS REFUSES. `tools/promoted_artefact_claim_census` grades a sentence claiming which
run sits at a canonical path against the artefact's run identity. It cannot work out what that is:
measured 2026-09-09, `docs/reports/run_output_latest.json` offered seventeen run-identity tokens
and not one was this run's -- twelve were dates inside the simulated world (`clv_snapshot_as_of`,
`wholesale_credit_exposure.mark_date`, a collateral stress test's `stressed_date`) and five were
another producer's stamps folded in whole. A claim about "the 2021-12-31 run" graded as SUPPORTED
against a stress test's mark date.

Narrowing the census to a list of field NAMES is refuted and must not be retried: the four
producers name one fact five ways (`generated_at`, `snapshot_ts`, `decision_run_at`, `refused_at`,
`portfolio_as_of`), and `portfolio_as_of` is a real run stamp while `mark_date` is a date in 2025
the company lived through -- same English, same depth, opposite populations. So the definition
comes from the producer, and this is what stops a producer quietly dropping it: without a control
here, deleting the declaration turns the census's refusing leg silent for that target and NOTHING
else in the tree changes.

WHY THIS IS AN AST CONTROL AND NOT A CALL. Three of these four producers cannot be invoked in a
test: `generate_snapshot` shells out to regenerate the dashboard, `run_annual_report` runs the
world for ~13 minutes, and `run_value_cycle_ab` runs it three times. The payload dict literal is
the thing that becomes the artefact, so it is the thing to assert about.
"""

import ast
from pathlib import Path

import pytest

from tools.promoted_artefact_claim_census import (
    RUN_IDENTITY_DECLARATION,
    census,
    declared_run_identity_fields,
    promote_targets,
)

PROJECT = Path(__file__).resolve().parents[2]

#: One row per producer of a promote-by-copy target, and the key that identifies the dict literal
#: it writes as the artefact. The anchor is a field the payload has for its OWN reasons, so this
#: cannot be satisfied by the declaration being present somewhere else in the module.
#:
#: `tools/run_value_cycle_ab.py` carries THREE such payloads -- the three-arm run, the noise floor,
#: and `floor_refusal_artefact`. The refusal is the one worth naming: a refusal landing on the
#: noise-floor path is still a run and must still be able to say which one, or the file that exists
#: to make "refused" and "still running" different on disk would take that target's grading away.
PRODUCERS = {
    "tools/run_annual_report.py": "producing_commit",
    "tools/run_value_cycle_ab.py": "producing_commit",
    "tools/generate_snapshot.py": "snapshot_ts",
    "tools/run_live_decisions.py": "decision_run_at",
}


def _payloads_missing_declaration(source: str, anchor: str) -> list[int]:
    """Line numbers of dict literals carrying `anchor` and NOT declaring their run identity."""
    out: list[int] = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Dict):
            continue
        keys = {k.value for k in node.keys
                if isinstance(k, ast.Constant) and isinstance(k.value, str)}
        if anchor in keys and RUN_IDENTITY_DECLARATION not in keys:
            out.append(node.lineno)
    return out


def _payload_count(source: str, anchor: str) -> int:
    return sum(1 for node in ast.walk(ast.parse(source))
               if isinstance(node, ast.Dict)
               and any(isinstance(k, ast.Constant) and k.value == anchor for k in node.keys))


@pytest.mark.parametrize("module,anchor", sorted(PRODUCERS.items()))
def test_the_producer_declares_which_of_its_fields_are_its_run_identity(module, anchor):
    source = (PROJECT / module).read_text(encoding="utf-8")
    # REACHABILITY FIRST, because a scan that finds no payloads at all passes this test exactly
    # like one that finds six compliant ones. If a producer is renamed or its payload restructured
    # so the anchor no longer appears, this is the leg that says so instead of going quietly green.
    assert _payload_count(source, anchor) >= 1, (
        f"{module} no longer builds a payload keyed on {anchor!r} -- this control has stopped "
        f"measuring anything and the anchor must be re-established, not deleted")
    missing = _payloads_missing_declaration(source, anchor)
    assert not missing, (
        f"{module}:{missing} writes a promote-by-copy artefact without declaring "
        f"`{RUN_IDENTITY_DECLARATION}`. Every claim about which run sits at that path becomes "
        f"ungradable the moment those bytes are promoted, and nothing else goes red.")


def test_the_scan_fires_when_a_declaration_is_removed():
    """The poison round, run as its own test rather than trusted from the green above.

    "Survived" means two opposite things -- the rule holds, or the scan cannot see. This removes
    the declaration from a real producer's source text and requires the scan to name the line.
    """
    source = (PROJECT / "tools/run_live_decisions.py").read_text(encoding="utf-8")
    assert not _payloads_missing_declaration(source, "decision_run_at")
    poisoned = source.replace(
        '"run_identity_fields": ["decision_run_at", "portfolio_as_of"],', "", 1)
    assert poisoned != source, "the poison did not apply -- the literal it edits has moved"
    assert _payloads_missing_declaration(poisoned, "decision_run_at"), (
        "a producer that stopped declaring must be caught")


def test_a_declared_field_that_no_longer_resolves_is_caught_on_the_live_artefacts():
    """Every field a LIVE artefact declares must reach a scalar in that same artefact.

    A declaration naming a renamed field contributes no tokens, so the target silently degrades to
    "we cannot tell" -- which looks identical to a producer that never adopted the convention. This
    separates the two.

    IT IS AN EQUIVALENCE TODAY AND SAYS SO. The producers were changed on 2026-09-09; the bytes at
    every canonical path predate that, so no target declares yet and this loop has nothing to walk.
    That is the honest transition state and it is asserted here rather than left to read as a pass:
    if nothing declares, the census must be REPORTING that, not staying quiet about it.
    """
    checked = 0
    for target in promote_targets():
        import json
        try:
            payload = json.loads((PROJECT / target["canonical"]).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        fields = declared_run_identity_fields(payload)
        if not fields:
            continue
        for dotted in fields:
            node = payload
            for part in dotted.split("."):
                assert isinstance(node, dict) and part in node, (
                    f"{target['canonical']} declares {dotted!r} as its run identity and that path "
                    f"does not resolve -- the field was renamed and the declaration was not")
                node = node[part]
            assert not isinstance(node, (dict, list)), (
                f"{target['canonical']} declares {dotted!r}, which is a container: a declaration "
                f"must name a leaf or the census is back to walking a subtree it cannot read")
            checked += 1
    if checked == 0:
        result = census()
        assert result["ungradable_targets"], (
            "no promote target declares its run identity, so the census must be saying we cannot "
            "tell -- an empty `ungradable_targets` here would mean grading resumed against "
            "something nobody declared")
