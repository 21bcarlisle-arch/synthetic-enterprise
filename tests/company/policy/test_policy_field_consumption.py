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
from company.interfaces.growth_desk import (
    offer_framing_for,
    replacement_cost_avoided_gbp,
    retention_discount_for_risk,
)
from company.policy.decision_policy import (
    CURRENT_POLICY,
    NAIVE_POLICY,
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
#   "active_scope"  — no consumer can be handed a policy, so the field is
#                     resolved from `active_policy()` on the company side of a
#                     door. These need the BEHAVIOURAL probe below, because a
#                     pin here is invisible to the caller.
#   "label"         — not consumed as a decision input at all.
#
# `probe` (active_scope only) resolves the field the way the world actually
# reaches it, so the probe fails if the real call path is pinned.
#
# THE "run_argument" VIA IS GONE — KNIFE3 step 39 (§3ah), and this is the change
# that made this file's own doctrine reach every field it declares.
#
# Five fields used to be declared `run_argument`: a consumer was handed the run's
# policy object and read the field off that parameter, which was correct by
# construction because `tools/run_frozen_baseline.py` passed `policy=` into
# `run_phase2b.main()`. Step 39 cut that argument — it was the world's last wall
# crossing into `company.policy.decision_policy` — so those five now resolve from
# the active scope behind `company.interfaces.growth_desk` and
# `company.trading.hedge_desk`.
#
# THIS FILE HAD TO MOVE WITH THE CODE OR IT WOULD HAVE GONE FAIL-SILENT, which is
# the R15 pattern this project catalogues and the reason the change is written up
# here rather than just made. Nothing in this file reads `via` except the
# `ACTIVE_SCOPE_FIELDS` filter. So had the five been left declared
# `run_argument`, every test below would have kept passing while the declaration
# described a mechanism that no longer exists: the completeness check compares
# field NAMES only, and the behavioural probe would simply have skipped them. The
# control would have gone on reporting green over five fields it had stopped
# covering — a counterfactual arm silently failing to switch a field is the exact
# defect this file was built for.
#
# The result is a strictly stronger control than before. `run_argument` was the
# UNPROBED via — it asserted nothing at runtime and leaned entirely on the static
# scan. Every consumable field now carries a behavioural probe that resolves it
# through its real call path and requires the two arms to differ.
FIELD_CONSUMPTION = {
    "name": {"via": "label"},
    # Sizing the retention discount. Reached through the growth desk's door,
    # which run_phase2b calls with a churn estimate and no policy. 0.55 sits in
    # CURRENT's medium tier (5%) and gets NAIVE's flat 5% too — so the probe
    # deliberately uses 0.80, where the tiers pay 8% and the flat rate does not.
    "retention_discount_mode": {
        "via": "active_scope",
        "probe": lambda: retention_discount_for_risk(0.80),
    },
    "retention_tiers": {
        "via": "active_scope",
        "probe": lambda: retention_discount_for_risk(0.80),
    },
    # NOT INDEPENDENTLY PROBEABLE, and declared honestly rather than given a
    # probe that would pass for the wrong reason. `flat_discount_pct` is the
    # value CURRENT falls back to in flat mode and NAIVE's actual rate; both
    # policies set it to 0.05, so no probe can witness a pin on this field —
    # there is nothing to witness. The two policies AGREEING is the whole
    # content, and `test_an_active_scope_field_switches_with_the_run` asserts
    # that a probed field's policies differ precisely so a field like this
    # cannot be given a fake probe and counted as covered.
    "flat_discount_pct": {"via": "label"},
    # The Phase-15b retention guard term. Resolved inside
    # replacement_cost_avoided_gbp, which lost its `counted_in_guard` parameter
    # in step 39. NAIVE returns 0.0, CURRENT returns the segment's cost.
    "include_acq_cost_saved_in_guard": {
        "via": "active_scope",
        "probe": lambda: replacement_cost_avoided_gbp(segment="resi"),
    },
    # The Phase-43b VaR hedge switch. Resolved inside decide_term_hedge, which
    # returns None when the layer is off — so the probe reports whether the desk
    # took a decision at all, which is what the switch actually controls.
    "use_var_hedge_decision": {
        "via": "active_scope",
        "probe": lambda: _var_hedge_decision_taken(),
    },
    # Was threaded as run_phase2b's own parameter into framing_type_for(policy,
    # ...). Step 39 replaced that with the growth desk's offer_framing_for,
    # the retention-channel sibling of collections_tone_for.
    "framing_mode": {
        "via": "active_scope",
        "probe": lambda: _framings_over_a_sample(),
    },
    # The finding's subject. Resolved per bill from inside the settlement path,
    # which has no policy argument and must not gain one.
    "tone_mode": {
        "via": "active_scope",
        "probe": lambda: collections_tone_for("C0001", "2023-01-31"),
    },
}


_FRAMING_SAMPLE = [
    ("C0001", "2023-01-31"), ("C0042", "2023-06-30"), ("C0777", "2024-11-30"),
    ("C1234", "2022-03-31"), ("C9999", "2025-09-30"), ("C0003", "2021-07-31"),
]


def _framings_over_a_sample() -> frozenset:
    """The framings the supplier chose across a spread of offers.

    A SET over a sample and not one call, and the reason is a real miss caught
    while writing this: the obvious probe, `offer_framing_for("C0001",
    "2023-01-31")`, returns 'gain_framed' under CURRENT_POLICY — that pair
    happens to land on the gain side of the sha256 cohort split — and
    'gain_framed' is also NAIVE_POLICY's fixed value. So the two arms agreed,
    and the probe reported a pin that was not there.

    A probe that can only witness a difference when a hash falls the right way
    is not a control, it is a coin toss stapled to an assertion. The set makes
    the property structural: CURRENT's ab_test must COVER BOTH framings and
    NAIVE's fixed mode must collapse to one, which is what the two modes mean
    and cannot come out equal by luck. `test_the_sample_covers_both_cohorts`
    below is the vacuity guard that keeps it that way.
    """
    return frozenset(offer_framing_for(cid, d) for cid, d in _FRAMING_SAMPLE)


def _var_hedge_decision_taken() -> bool:
    """Did the desk take a VaR decision for a representative term?

    The probe for `use_var_hedge_decision`. Goes through the real desk with a
    term that satisfies every other condition `run_phase2b` requires, so the
    only thing that can vary between the two arms is the policy switch. Returns
    a bool rather than the TermHedge because the arms must be COMPARED, and two
    TermHedge objects built from a live price history would differ for reasons
    that have nothing to do with the policy.
    """
    from company.interfaces.hedge_desk import build_hedge_desk

    price_records = [
        {"date": f"2023-{m:02d}-01", "price_gbp_per_mwh": 80.0 + m}
        for m in range(1, 13)
    ]
    decision = build_hedge_desk().decide_term_hedge(
        customer_id="C0001",
        term_start="2023-01-01",
        term_end="2023-12-31",
        commodity="electricity",
        volume_kwh=3000.0,
        forward_price_gbp_per_mwh=85.0,
        unit_rate_gbp_per_mwh=110.0,
        price_records=price_records,
        term_days=364,
        current_fraction=0.5,
        accept_decision=True,
    )
    return decision is not None


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
    with policy_scope(CURRENT_POLICY):
        under_current = probe()
    with policy_scope(NAIVE_POLICY):
        under_naive = probe()
    assert getattr(CURRENT_POLICY, field) != getattr(NAIVE_POLICY, field), (
        f"the two policies agree on {field}, so this probe cannot witness a pin"
    )
    assert under_naive != under_current, (
        f"{field} resolved identically in both arms ({under_naive!r}) — the naive arm "
        f"is running the live policy's {field}"
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


def test_the_sample_covers_both_cohorts():
    """VACUITY GUARD for the framing probe. If every pair in `_FRAMING_SAMPLE`
    landed on the same side of CURRENT_POLICY's split, the probe would return a
    one-element set in both arms and prove nothing — which is exactly how the
    single-pair version of this probe failed. Assert the sample really does
    straddle the cohort boundary, so the set comparison has something to see."""
    with policy_scope(CURRENT_POLICY):
        assert _framings_over_a_sample() == frozenset({"loss_framed", "gain_framed"}), (
            "the framing sample no longer covers both CURRENT cohorts, so the "
            "framing_mode probe cannot witness a pin"
        )
    with policy_scope(NAIVE_POLICY):
        assert _framings_over_a_sample() == frozenset({"gain_framed"}), (
            "the naive arm split its retention offers — NAIVE_POLICY's framing_mode "
            "is the fixed value 'gain_framed', not an A/B split"
        )


def test_a_resolver_honours_the_policy_it_was_handed():
    """`framing_type_for` still takes a policy ARGUMENT, and must still obey it.

    KNIFE3 step 39 note: `framing_mode` is now declared `active_scope` and probed
    through `offer_framing_for`, because run_phase2b no longer holds a policy to
    thread. That does NOT make this test redundant — it makes it the other half.
    The door resolves `active_policy()` and hands it to this resolver, so the
    probe above proves the door reads the right policy and this proves the
    resolver then USES what the door handed it. A resolver that ignored its
    argument and read the live constant internally would pass the AST scan (no
    constant is named at the call site) and would ALSO defeat the door's probe,
    since both arms would come back current.

    That is not hypothetical: it is the original finding's defect one layer down.
    `tone_for` and `framing_type_for` are the two resolvers on this path, and
    this is the assertion that they are honest about their own parameter."""
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
