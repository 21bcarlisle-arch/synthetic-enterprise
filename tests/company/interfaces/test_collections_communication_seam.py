"""The collections-communication seam's contract — and the ways it could rot silently.

WHY THIS FILE EXISTS (R15: a control must be able to FAIL on its own named defect)
---------------------------------------------------------------------------------
KNIFE pass 3 (design B5_collections_tone_is_an_event_attribute) routed
`simulation.arrears_engine -> company.policy.decision_policy` through
`company.interfaces.collections_communication`.

The *routing* is already policed, and by two independent instruments: the
epistemic-wall ratchet reds if any SIM module imports `company.policy.decision_policy`
again (its allowlist tuple is deleted, so there is nothing left to hide behind), and
`tools/wall_crossing_dispositions.py` reds if a row ruled `cut` is still in the tree.
Neither of those is re-asserted here — duplicating them would be a second copy of a
check, not a second check.

What nothing else polices is the two properties the CUT itself rests on:

1. **The seam must not hand back the policy object.** The whole point of the cut is that
   `DecisionPolicy` — its `tone_mode`, its A/B split, its thresholds — is unreachable from
   the SIM. A later "why not let callers pass their own policy?" convenience argument, or
   a bare `from company.policy.decision_policy import *`-style widening, would restore the
   dependency the cut removed **without adding back a single wall edge**, because the
   crossing would still terminate on the exempt seam package. The ratchet cannot see that.
   This is precisely the escape the register's §2b laundering rule is about, one level in.

2. **The tone values must be unchanged.** Four consumers (`compute_emergent_bad_debt`,
   `compute_debt_recovery`, `dd_collection_book`, `generate_billing_ledger`) resolve payment
   outcomes from a shared per-bill RNG substream, and their own docstrings require identical
   call sequences. Tone feeds `payment_outcome`. A seam that returned a *different* tone —
   or resolved a different policy — would silently move written-off GBP in the annual report
   while every test that does not compute a payment outcome stayed green. That is FAIL-SILENT.

Each test below is written so that its named defect reds it, and the `test_mutation_*`
tests prove that claim by PERFORMING the defect rather than asserting it is impossible.
"""

from __future__ import annotations

import ast
import inspect
import os

import pytest

from company.interfaces import collections_communication as seam
from company.policy.decision_policy import CURRENT_POLICY, DecisionPolicy, tone_for

# A spread of (customer_id, period_end) pairs. CURRENT_POLICY.tone_mode is "ab_test", so
# the tone is a sha256 cohort split — these cover BOTH arms, which the vacuity test below
# asserts rather than assumes (a sample landing on one arm would make the identity check
# pass on a constant-returning seam).
SAMPLE = [
    ("C0001", "2023-01-31"),
    ("C0001", "2023-02-28"),
    ("C0042", "2023-06-30"),
    ("C0777", "2024-11-30"),
    ("C1234", "2022-03-31"),
    ("C9999", "2025-09-30"),
]


# --------------------------------------------------------------------------
# 1. Value identity — the cut changed no payment outcome.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("customer_id,period_end", SAMPLE)
def test_seam_returns_exactly_what_the_pre_cut_call_site_returned(customer_id, period_end):
    """The replaced call site was `tone_for(CURRENT_POLICY, cid, period_end)`. The seam
    must return that, for the same inputs — this is a REFACTOR-identity assertion, which is
    why comparing against the wrapped function is the right check here and not a tautology:
    the claim under test is 'this cut is behaviour-preserving', and the pre-cut expression
    is the only thing that can witness it."""
    assert seam.collections_tone_for(customer_id, period_end) == tone_for(
        CURRENT_POLICY, customer_id, period_end
    )


def test_the_sample_exercises_both_cohort_arms():
    """VACUITY GUARD for the test above. If every sampled pair hashed to the same arm, a
    seam that ignored its arguments and returned a constant would pass the identity check
    six times over. This asserts the sample can actually tell the two apart."""
    tones = {seam.collections_tone_for(cid, pe) for cid, pe in SAMPLE}
    assert tones == {"empathetic_toned", "firm_toned"}, (
        f"sample collapsed onto {tones} — the identity check above is vacuous until this "
        f"sample covers both arms"
    )


def test_mutation_a_seam_resolving_the_wrong_policy_reds_the_identity_check(monkeypatch):
    """R15 both-ways proof for the identity check. NAIVE_POLICY carries tone_mode
    'firm_toned' (not 'ab_test'), so a seam that resolved the wrong policy would return a
    constant. Perform that defect and prove the check above fires.

    The mutation now goes through `active_policy` rather than a module-level
    `CURRENT_POLICY` attribute, because 2026-08-12 replaced the pin with the run's
    policy (WORKER_FINDING_THE_NAIVE_ARM_KEEPS_THE_LIVE_TONE_2026-08-10). The defect
    being performed is the same one: the seam resolving a policy other than the
    caller's."""
    from company.policy.decision_policy import NAIVE_POLICY

    monkeypatch.setattr(seam, "active_policy", lambda: NAIVE_POLICY)
    mismatches = [
        (cid, pe)
        for cid, pe in SAMPLE
        if seam.collections_tone_for(cid, pe) != tone_for(CURRENT_POLICY, cid, pe)
    ]
    assert mismatches, (
        "the identity check cannot fail: swapping the resolved policy changed nothing, so "
        "it would not catch a seam wired to the wrong policy"
    )


# --------------------------------------------------------------------------
# 2. The policy object must not be reachable through the door.
# --------------------------------------------------------------------------

def test_the_seam_does_not_re_export_the_policy_object():
    """`__all__` is the published surface. `DecisionPolicy`/`CURRENT_POLICY` appearing in it
    would make `from company.interfaces.collections_communication import CURRENT_POLICY` a
    sanctioned move for a SIM module — the dependency restored, with no wall edge created,
    because the import still terminates on the exempt seam package."""
    assert seam.__all__ == ["collections_tone_for"]
    leaked = [n for n in seam.__all__ if n in ("CURRENT_POLICY", "DecisionPolicy", "tone_for")]
    assert not leaked, f"seam re-exports company decision machinery: {leaked}"


def test_the_seam_accepts_no_argument_typed_as_the_policy():
    """The other way the object comes back: a `policy: DecisionPolicy = CURRENT_POLICY`
    convenience parameter. That reads as harmless and would put the company's decision
    object back in the SIM's hands at every call site."""
    sig = inspect.signature(seam.collections_tone_for)
    assert list(sig.parameters) == ["customer_id", "period_end"]
    for name, param in sig.parameters.items():
        assert param.annotation is not DecisionPolicy, f"{name} is typed as the policy object"
        assert not isinstance(param.default, DecisionPolicy), (
            f"{name} defaults to a policy instance, so callers can pass their own"
        )


def _public_names_in_all(source: str) -> list[str]:
    """Parse `__all__` out of module SOURCE rather than importing it, so the check below
    can be run against mutated text without touching the live import system."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets
        ):
            return [el.value for el in node.value.elts]
    return []


def test_mutation_re_exporting_the_policy_reds_the_surface_check():
    """R15 both-ways proof for the surface check. Perform the defect — widen `__all__` to
    publish `CURRENT_POLICY` — against the module's real source text, and assert the
    predicate the test above uses actually rejects it. Done on source, not by mutating the
    imported module, so a restoration step cannot be forgotten and leave the tree dirty."""
    path = os.path.join(os.path.dirname(seam.__file__), "collections_communication.py")
    with open(path, encoding="utf-8") as fh:
        source = fh.read()

    assert _public_names_in_all(source) == ["collections_tone_for"], (
        "source and imported module disagree on __all__ — this mutation proof is not "
        "reading the file the test above checks"
    )

    mutated = source.replace(
        '__all__ = ["collections_tone_for"]',
        '__all__ = ["collections_tone_for", "CURRENT_POLICY"]',
    )
    assert mutated != source, "mutation did not apply — the __all__ spelling moved"

    names = _public_names_in_all(mutated)
    leaked = [n for n in names if n in ("CURRENT_POLICY", "DecisionPolicy", "tone_for")]
    assert leaked == ["CURRENT_POLICY"], (
        "the surface check cannot fail: re-exporting the policy object was not detected"
    )


# --------------------------------------------------------------------------
# 3. The SIM side reaches the company ONLY through this door.
# --------------------------------------------------------------------------

def test_the_arrears_engine_imports_the_seam_and_not_the_policy():
    """The consumer half of the cut. Asserted on the arrears engine's SOURCE rather than
    on the ratchet's answer, because this names the specific remedy: not merely 'no
    forbidden edge' but 'the tone arrives through the published door'. A future edit that
    dropped the tone entirely would satisfy the ratchet and fail here."""
    import simulation.arrears_engine as engine

    with open(engine.__file__, encoding="utf-8") as fh:
        source = fh.read()

    imported = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)

    assert "company.interfaces.collections_communication" in imported, (
        "the arrears engine no longer reads the tone through the seam"
    )
    assert "company.policy.decision_policy" not in imported, (
        "the arrears engine reaches the company's decision policy directly again — this is "
        "the B5 crossing, back"
    )
