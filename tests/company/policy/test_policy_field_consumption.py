"""Every field a counterfactual arm claims to switch must actually switch.

WHY THIS FILE EXISTS
--------------------
`docs/staging/WORKER_FINDING_THE_NAIVE_ARM_KEEPS_THE_LIVE_TONE_2026-08-10.md`: the
frozen-policy baseline replays a decade twice, once under `CURRENT_POLICY` and once
under `NAIVE_POLICY`, and publishes the margin delta as "the value of learning". The
naive arm ran naive retention, naive guard and naive hedging — and CURRENT dunning
letter tone, because `collections_tone_for` resolved a pinned `CURRENT_POLICY` instead
of the run's. One uncontrolled variable rode along inside a published delta, in an
unknown direction.

R10 forbids closing that as an instance fix on `tone_mode`. The CLASS is:

    a counterfactual arm that does not switch every field it claims to switch,
    because some field is resolved from a module-level policy CONSTANT rather
    than from the policy the run is executing under.

`framing_mode` was a live candidate for the identical bug (the finding says so and
does not check it — this file checks it). So the control below is not "tone_mode is
fixed"; it is two properties that make the class structurally hard to reintroduce:

  1. **COMPLETENESS.** Every field of `DecisionPolicy` is declared here with how it
     reaches its consumer. Adding a field to the dataclass without declaring it reds
     this file — so the next `tone_mode` cannot arrive undeclared.
  2. **NO PINNED RESOLUTION.** No production module may read a policy field off
     `CURRENT_POLICY`/`NAIVE_POLICY`, or hand one of those constants to a field
     resolver. That is the defect shape itself, stated as a repo property rather
     than as a fact about one call site.

Both are mutation-proven below (R15): the mutation tests PERFORM the defect — restore
the pin, add an undeclared field — rather than asserting it is impossible.

WHAT THIS FILE DOES NOT CLAIM
-----------------------------
It does not measure the SIZE of the correction. The published
`site/state/frozen_policy_baseline.json` was computed under the contaminated arm and
is refreshed by a multi-minute full-decade replay on a weekly staleness gate, so the
corrected delta arrives with that refresh and not with this commit. The direction is
recorded, unmeasured, in the finding's disposition — not asserted here.
"""

from __future__ import annotations

import ast
import dataclasses
import warnings
from pathlib import Path

import pytest

from company.interfaces.collections_communication import collections_tone_for
from company.policy.decision_policy import (
    CURRENT_POLICY,
    NAIVE_POLICY,
    VALUE_ARM_POLICY,
    DecisionPolicy,
    active_policy,
    framing_type_for,
    policy_scope,
)

PROJECT_DIR = Path(__file__).resolve().parents[3]

# The two names that, read directly, make a consumer blind to the run's policy.
PINNED_CONSTANTS = {"CURRENT_POLICY", "NAIVE_POLICY"}

# Functions/methods whose FIRST job is to resolve a policy field. Handing one of
# these a module-level constant is the `tone_for(CURRENT_POLICY, ...)` defect.
FIELD_RESOLVERS = {"tone_for", "framing_type_for", "retention_discount_for_risk"}

# Production trees that run during a simulation. `tests/` is excluded on purpose:
# a test naming `NAIVE_POLICY.tone_mode` is asserting the policy's contents, which
# is exactly what a test should do.
PRODUCTION_DIRS = ("company", "simulation", "saas", "tools", "background")

# THERE IS NO ALLOWLIST, DELIBERATELY.
#
# The first draft of this control exempted three files that legitimately NAME the
# constants — `decision_policy.py` (defines them), `run_frozen_baseline.py` (drives
# both arms), `run_phase2b.py` (`policy = policy or CURRENT_POLICY`). Every one of
# those exemptions was unnecessary and each was a blanket, file-scoped hole: the scan
# does not flag naming a constant, it flags RESOLVING A FIELD from one, and none of the
# three does that. Verified by pointing the matcher at each file with no exemption —
# zero hits. So the waivers bought nothing and would have let a genuine
# `CURRENT_POLICY.use_var_hedge_decision` hide inside `run_phase2b.py`, which is the
# fail-open-allowlist pattern from this project's own R15 catalogue.
#
# If a deliberate pin is ever genuinely needed, the shape is a per-SITE declaration
# carrying its reason — not a file added to a list, which exempts everything else in
# that file for free.


# ---------------------------------------------------------------------------
# The declaration. One row per DecisionPolicy field.
# ---------------------------------------------------------------------------
# `via` records HOW the field reaches the code that acts on it:
#
#   "run_argument"  — a consumer is handed the run's policy object and reads the
#                     field off that parameter. Correct by construction for the
#                     frozen baseline, which passes `policy=` to the entry point.
#   "active_scope"  — no consumer can be handed a policy (the collections seam
#                     must never accept one — B5 wall cut), so the field is
#                     resolved from `active_policy()`. These are the dangerous
#                     ones: they need the BEHAVIOURAL probe below, because a pin
#                     here is invisible to the caller.
#   "label"         — not consumed as a decision input at all.
#
# `probe` (active_scope only) resolves the field the way the world actually
# reaches it, so the probe fails if the real call path is pinned.
FIELD_CONSUMPTION = {
    "name": {"via": "label"},
    "retention_discount_mode": {"via": "run_argument"},
    "retention_tiers": {"via": "run_argument"},
    "flat_discount_pct": {"via": "run_argument"},
    "include_acq_cost_saved_in_guard": {"via": "run_argument"},
    "use_var_hedge_decision": {"via": "run_argument"},
    # Threaded correctly already: run_phase2b.py calls
    # framing_type_for(policy, ...) with its own parameter. Declared active_scope
    # anyway would be a lie; declared run_argument, it is covered by the
    # no-pinned-resolution scan, which is what would catch a regression to
    # framing_type_for(CURRENT_POLICY, ...) -- the finding's named sibling risk.
    "framing_mode": {"via": "run_argument"},
    # The finding's subject. Resolved per bill from inside the settlement path,
    # which has no policy argument and must not gain one.
    "tone_mode": {
        "via": "active_scope",
        "probe": lambda: collections_tone_for("C0001", "2023-01-31"),
    },
    # THE VALUE CYCLE'S ONE VARIABLE (2026-08-26). Resolved from inside
    # `company/pricing/renewal_rate_chain.decide_renewal_rate`, which is a WALL
    # DOOR and must not gain a policy argument: its own docstring argues that
    # what crosses is "a plain value, the supplier's own settled records, or the
    # supplier's own realised margin history", and a company decision object is
    # none of those. So it is the second `active_scope` field, for the same
    # reason as the first -- the consumer cannot be handed one.
    #
    # THE PROBE IS THE REAL DOOR, not a stub. It drives `decide_renewal_rate`
    # itself with an account whose own settled book is inside the arm's
    # observation window, so under `flat_rules` it returns the struck rate
    # untouched and under `value_based` it returns a different one. A probe that
    # read the field back off the policy would be the tautology R15 names: it
    # would pass against a chain that ignored the scope entirely.
    "renewal_margin_arm": {
        "via": "active_scope",
        "probe": lambda: _renewal_rate_under_the_active_arm(),
        # The witnessing pair. NAIVE_POLICY prices flat too -- the last-generation company had
        # no per-customer view either -- so CURRENT vs NAIVE cannot witness this field at all.
        # VALUE_ARM_POLICY is CURRENT with this one field changed, which is exactly the pair the
        # realised A/B runs.
        "arms": (CURRENT_POLICY, VALUE_ARM_POLICY),
    },
}


def _renewal_rate_under_the_active_arm() -> float | None:
    """Drive the renewal rate chain on one account and return the rate it decided.

    Deliberately an SME account (`is_domestic=False`) so the domestic price cap -- writer 4, the
    only writer that can move a rate DOWN -- cannot clamp the two arms back onto the same number
    and make this probe report agreement where there is none.
    """
    from company.pricing.renewal_rate_chain import decide_renewal_rate

    settled = [
        {
            "customer_id": "C0001",
            "commodity": "electricity",
            "settlement_date": f"2020-{m:02d}-15",
            "term_start": "2020-01-01",
            "consumption_kwh": 250.0,
            "revenue_gbp": 45.0,
            "net_margin_gbp": 1.0,
            "margin_gbp": 5.0,
            "settlement_periods_folded": 48,
        }
        for m in range(1, 13)
    ]
    return decide_renewal_rate(
        customer_id="C0001",
        billing_account="C0001",
        commodity="electricity",
        term_start="2021-01-01",
        tariff_type="fixed",
        term_index=2,
        struck_unit_rate_gbp_per_mwh=200.0,
        portfolio_margin_rates=[],
        prior_term_margin_gbp=None,
        prior_term_revenue_gbp=0.0,
        is_domestic=False,
        settled_records=settled,
    ).unit_rate_gbp_per_mwh


def _production_files() -> list[Path]:
    files: list[Path] = []
    for d in PRODUCTION_DIRS:
        root = PROJECT_DIR / d
        if root.is_dir():
            files.extend(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)
    return files


def _pinned_resolutions(
    files: list[Path], fields: set[str], root: Path = PROJECT_DIR
) -> list[str]:
    """Every place a production module resolves a policy field from a constant.

    Two shapes, because the original defect was the second one and an
    attribute-only scan would have missed it entirely:
      (a) `CURRENT_POLICY.<field>`      — read the field off the live constant
      (b) `tone_for(CURRENT_POLICY, …)` — hand the constant to a resolver

    `root` is a parameter solely so the mutation tests can point the SAME matcher
    at a synthetic tree. A second copy of this walker would prove that a copy of
    the control can fail and say nothing about the control (feedback: a harness's
    convenience chose the control's subject).
    """
    hits: list[str] = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        try:
            # Parsing the whole production tree surfaces every source file's
            # SyntaxWarnings (e.g. an invalid escape in a docstring) as noise in
            # THIS test's output. Linting escapes is not this control's subject, and
            # a control that spams unrelated warnings gets its real message ignored.
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:  # pragma: no cover - a syntax error is another test's job
            continue
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id in PINNED_CONSTANTS
                and node.attr in fields
            ):
                hits.append(f"{rel}:{node.lineno} reads {node.value.id}.{node.attr}")
            if isinstance(node, ast.Call):
                fname = (
                    node.func.attr
                    if isinstance(node.func, ast.Attribute)
                    else getattr(node.func, "id", None)
                )
                if fname in FIELD_RESOLVERS:
                    for arg in node.args:
                        if isinstance(arg, ast.Name) and arg.id in PINNED_CONSTANTS:
                            hits.append(
                                f"{rel}:{node.lineno} passes {arg.id} to {fname}()"
                            )
    return hits


# ---------------------------------------------------------------------------
# 1. Completeness — a new field cannot arrive undeclared.
# ---------------------------------------------------------------------------

def test_every_policy_field_declares_how_it_reaches_its_consumer():
    """The R10 half. `tone_mode` was added in 2026-07-10 and nothing asked how the
    counterfactual arm would switch it; the answer turned out to be "it doesn't",
    and that went unnoticed for a month. A field added from now on reds this until
    someone answers the question."""
    declared = set(FIELD_CONSUMPTION)
    actual = {f.name for f in dataclasses.fields(DecisionPolicy)}
    assert declared == actual, (
        f"undeclared policy fields: {sorted(actual - declared)}; "
        f"declared-but-gone: {sorted(declared - actual)} — every DecisionPolicy field "
        f"must state whether a counterfactual run switches it via the run argument or "
        f"via the active policy scope"
    )


# ---------------------------------------------------------------------------
# 2. No pinned resolution — the class, as a repo property.
# ---------------------------------------------------------------------------

def test_no_production_module_resolves_a_policy_field_from_a_pinned_constant():
    """The defect shape itself. Before the fix this named
    `company/interfaces/collections_communication.py` passing CURRENT_POLICY to
    tone_for(); it now names nothing, and would name any module that reacquired the
    pin — including for `framing_mode`, the sibling the finding flagged and did not
    check."""
    fields = {f.name for f in dataclasses.fields(DecisionPolicy)}
    hits = _pinned_resolutions(_production_files(), fields)
    assert not hits, (
        "policy fields resolved from a module-level constant instead of the run's "
        "policy — a counterfactual arm will not switch these:\n  "
        + "\n  ".join(hits)
    )


def test_the_scan_has_a_population_to_scan():
    """VACUITY GUARD. The test above passes trivially if the file walk returns
    nothing — a moved directory, a renamed tree, a `rglob` typo. Assert the
    population is real and contains the module the finding was about."""
    files = _production_files()
    assert len(files) > 100, f"production scan found only {len(files)} files"
    rels = {p.relative_to(PROJECT_DIR).as_posix() for p in files}
    assert "company/interfaces/collections_communication.py" in rels
    assert "simulation/arrears_engine.py" in rels


# ---------------------------------------------------------------------------
# 3. Behavioural probes — the active-scope fields really do switch.
# ---------------------------------------------------------------------------

ACTIVE_SCOPE_FIELDS = [f for f, d in FIELD_CONSUMPTION.items() if d["via"] == "active_scope"]


@pytest.mark.parametrize("field", ACTIVE_SCOPE_FIELDS)
def test_an_active_scope_field_switches_with_the_run(field):
    """Reach the field the way the settlement path reaches it, once per arm, and
    require the answers to differ. This is the assertion that was false for a month:
    under NAIVE_POLICY the letters must be uniformly firm, because that is what the
    policy the arm claims to be running says."""
    probe = FIELD_CONSUMPTION[field]["probe"]
    # WHICH TWO POLICIES WITNESS THIS FIELD IS THE FIELD'S OWN PROPERTY (2026-08-26). This test
    # used to hardcode CURRENT vs NAIVE, which was true of the only active-scope field there
    # was. `renewal_margin_arm` is `flat_rules` in BOTH of those -- the naive company priced
    # flat too -- so a hardcoded pair would have hit the vacuity guard below and forced either a
    # skip or a dishonest edit to NAIVE_POLICY. A field declares its own witnessing pair; the
    # default stays CURRENT/NAIVE, so nothing else moved.
    left, right = FIELD_CONSUMPTION[field].get("arms", (CURRENT_POLICY, NAIVE_POLICY))
    with policy_scope(left):
        under_left = probe()
    with policy_scope(right):
        under_right = probe()
    assert getattr(left, field) != getattr(right, field), (
        f"the two policies agree on {field}, so this probe cannot witness a pin"
    )
    assert under_left != under_right, (
        f"{field} resolved identically in both arms ({under_left!r}) — the {right.name} arm "
        f"is running the {left.name} policy's {field}"
    )


def test_the_naive_arm_letters_are_uniformly_firm():
    """The finding's concrete claim, inverted into an assertion. CURRENT_POLICY's
    tone_mode is 'ab_test' (a sha256 cohort split); NAIVE_POLICY's is 'firm_toned'.
    A spread of customers and periods must therefore collapse to one tone under the
    naive scope and cover both under the current one."""
    sample = [
        ("C0001", "2023-01-31"), ("C0001", "2023-02-28"), ("C0042", "2023-06-30"),
        ("C0777", "2024-11-30"), ("C1234", "2022-03-31"), ("C9999", "2025-09-30"),
    ]
    with policy_scope(NAIVE_POLICY):
        naive_tones = {collections_tone_for(c, p) for c, p in sample}
    with policy_scope(CURRENT_POLICY):
        current_tones = {collections_tone_for(c, p) for c, p in sample}
    assert naive_tones == {"firm_toned"}, f"naive arm split its letters: {naive_tones}"
    assert current_tones == {"empathetic_toned", "firm_toned"}, (
        f"sample does not cover both current-arm cohorts ({current_tones}), so the "
        f"assertion above proves less than it appears to"
    )


def test_a_run_argument_resolver_honours_the_policy_it_was_handed():
    """The `run_argument` counterpart to the probe above, and the assertion that makes
    this file's claim about `framing_mode` a CHECK rather than a narration.

    The finding named `framing_mode` as "a live candidate for the identical bug, not
    checked here". It turned out clean — `run_phase2b.py:1353` threads its own
    parameter — but "clean" resting on a reading of one line is worth one assertion:
    a resolver that ignored its argument and read the live constant internally would
    pass the AST scan (no constant is named at the CALL site) and be invisible to the
    active-scope probe (`framing_mode` is not resolved that way). This is the third
    angle that covers that gap."""
    for cid, date in [("C0001", "2023-01-31"), ("C9999", "2025-09-30")]:
        assert framing_type_for(NAIVE_POLICY, cid, date) == "gain_framed", (
            "framing_type_for ignored the policy it was handed — NAIVE_POLICY's "
            "framing_mode is the fixed value 'gain_framed', not an A/B split"
        )
    under_current = {
        framing_type_for(CURRENT_POLICY, cid, d)
        for cid in ("C0001", "C0042", "C0777", "C1234", "C9999")
        for d in ("2023-01-31", "2024-06-30")
    }
    assert under_current == {"loss_framed", "gain_framed"}, (
        f"CURRENT_POLICY's ab_test split collapsed onto {under_current}, so the naive "
        f"assertion above proves less than it appears to"
    )


def test_outside_any_scope_the_live_policy_still_governs():
    """The fix must not move an ordinary run. Every caller that does not enter a
    scope — which is all of them except the frozen baseline — sees CURRENT_POLICY,
    so the B5 cut's byte-for-byte identity claim survives this change."""
    assert active_policy() is CURRENT_POLICY
    from company.policy.decision_policy import tone_for
    for cid, pe in [("C0001", "2023-01-31"), ("C9999", "2025-09-30")]:
        assert collections_tone_for(cid, pe) == tone_for(CURRENT_POLICY, cid, pe)


def test_a_scope_does_not_leak_past_its_block():
    """Why `policy_scope` is a context manager and not a setter. An arm that leaked
    would make the NEXT run — or the next test — a chimera, which is the same defect
    one level out."""
    with policy_scope(NAIVE_POLICY):
        assert active_policy() is NAIVE_POLICY
    assert active_policy() is CURRENT_POLICY

    with pytest.raises(RuntimeError):
        with policy_scope(NAIVE_POLICY):
            raise RuntimeError("arm failed")
    assert active_policy() is CURRENT_POLICY, "a failed arm leaked its policy"


# ---------------------------------------------------------------------------
# 4. R15 — each control above, proven to fire on its own named defect.
# ---------------------------------------------------------------------------

def test_mutation_restoring_the_pin_reds_the_scan(tmp_path):
    """PERFORM the original defect — a module resolving tone via
    `tone_for(CURRENT_POLICY, ...)` — and prove the scan names it. Written against a
    synthetic file so the mutation cannot leave the real seam edited if this test
    dies mid-run (feedback: mutation restore wipes edit)."""
    victim = tmp_path / "company" / "interfaces"
    victim.mkdir(parents=True)
    (victim / "pinned_seam.py").write_text(
        "from company.policy.decision_policy import CURRENT_POLICY, tone_for\n"
        "def collections_tone_for(customer_id, period_end):\n"
        "    return tone_for(CURRENT_POLICY, customer_id, period_end)\n",
        encoding="utf-8",
    )
    files = list(victim.glob("*.py"))
    hits = _pinned_resolutions(files, {"tone_mode"}, root=tmp_path)
    assert hits, "the scan does not fire on tone_for(CURRENT_POLICY, ...)"
    assert "passes CURRENT_POLICY to tone_for()" in hits[0]


def test_mutation_a_field_read_off_the_constant_reds_the_scan(tmp_path):
    """The other shape: `CURRENT_POLICY.framing_mode` read directly. An
    attribute-blind scan would pass here, so this proves shape (a) is live too."""
    (tmp_path / "consumer.py").write_text(
        "from company.policy.decision_policy import CURRENT_POLICY\n"
        "def choose():\n"
        "    return CURRENT_POLICY.framing_mode\n",
        encoding="utf-8",
    )
    hits = _pinned_resolutions(
        [tmp_path / "consumer.py"], {"framing_mode"}, root=tmp_path
    )
    assert hits, "the scan does not fire on CURRENT_POLICY.framing_mode"
    assert "reads CURRENT_POLICY.framing_mode" in hits[0]


def test_mutation_an_undeclared_field_reds_the_completeness_check():
    """PERFORM the `tone_mode` history: a field arrives on the dataclass and nobody
    declares how a counterfactual arm switches it."""
    actual = {f.name for f in dataclasses.fields(DecisionPolicy)} | {"discount_ceiling"}
    declared = set(FIELD_CONSUMPTION)
    assert declared != actual, (
        "the completeness check cannot fail: an undeclared field compared equal to "
        "the declared set"
    )
    assert sorted(actual - declared) == ["discount_ceiling"]


def test_mutation_a_pinned_seam_reds_the_behavioural_probe(monkeypatch):
    """The scan is static; this is the runtime half. Re-pin the seam's resolver to
    the live policy and prove the per-field probe fires. Together they cover a pin
    the AST cannot see (one built at runtime) and one the runtime cannot see (a pin
    on a path this test's sample never reaches)."""
    import company.interfaces.collections_communication as seam

    monkeypatch.setattr(seam, "active_policy", lambda: CURRENT_POLICY)
    with policy_scope(NAIVE_POLICY):
        under_naive = seam.collections_tone_for("C0001", "2023-01-31")
    with policy_scope(CURRENT_POLICY):
        under_current = seam.collections_tone_for("C0001", "2023-01-31")
    assert under_naive == under_current, (
        "the behavioural probe cannot fail: with the seam pinned to the live policy "
        "the two arms still disagreed"
    )
