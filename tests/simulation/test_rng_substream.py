"""Controls for the canonical RNG substream primitive (SP2_2_rng_substream_primitive, C-S2).

Each test names the defect it exists to catch.
"""

from __future__ import annotations

import ast
import hashlib
import importlib
import random
from pathlib import Path

import pytest

from simulation.rng_substream import substream, substream_key

REPO = Path(__file__).resolve().parents[2]

# Modules moved onto the primitive with NO draw change: each carried Formula B
# (``NS::name::seed``) privately. Their constant is ``STREAM_NAMESPACE`` or
# ``STREAM_NAME``.
MIGRATED = (
    "sme_distress",
    "household_budget",
    "dd_attribution",
    "arrears_engine",
    "payment_behaviour_source",
    "premise_demand",
    "willingness_classification",
    "self_rationing",
    "fabric_physics",
    "demand_model",
    "premise_trace",
)

# Still deriving their own seed. Formula A/C and the 4-part variants move their
# draws when migrated, so each is a deliberate baseline break owed its own re-pin.
# This set may only SHRINK: a new private derivation reds, and so does an entry
# that no longer derives (delete it from here when you migrate it).
NOT_YET_MIGRATED = {
    ("simulation/adoption_geography.py", "_substream"),
    ("simulation/conversation_response.py", "_substream"),
    ("simulation/final_bill_outcome.py", "_substream"),
    ("simulation/household_segments.py", "_engagement_propensity_substream"),
    ("simulation/household_siting.py", "_substream"),
    ("simulation/life_events.py", "_substream"),
    ("simulation/payment_seam_adapter.py", "_adapter_substream"),
    ("simulation/population_draw.py", "_substream"),
    ("simulation/population_draw.py", "_cohort_substream"),
    ("simulation/premise_population.py", "_substream"),
    ("simulation/sme_payment_behaviour.py", "_tier_substream"),
}


def _legacy_formula_b(namespace: str, name: str, base_seed: int) -> random.Random:
    key = f"{namespace}::{name}::{base_seed}".encode("utf-8")
    return random.Random(int.from_bytes(hashlib.sha256(key).digest()[:8], "big"))


def _private_derivations() -> set[tuple[str, str]]:
    found = set()
    for root in ("simulation", "sim", "company", "saas"):
        for path in sorted((REPO / root).rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.FunctionDef)
                    and "substream" in node.name
                    and "hashlib" in ast.unparse(node)
                ):
                    found.add((path.relative_to(REPO).as_posix(), node.name))
    return found


def test_the_primitive_value_is_stable_across_processes():
    """Defect: the formula drifts (byte order, digest width, separator) and every
    stream in the world silently re-seeds."""
    assert round(substream("W2_6_sme_distress", "onset", 12345).random(), 12) == 0.277512996019


@pytest.mark.parametrize("module_name", MIGRATED)
def test_a_migrated_module_draws_exactly_what_its_private_formula_drew(module_name):
    """Defect: the migration moved a module's draws -- a baseline break shipped as
    a refactor, invisible because each module's own pins may not cover every name."""
    mod = importlib.import_module(f"simulation.{module_name}")
    namespace = getattr(mod, "STREAM_NAMESPACE", None) or mod.STREAM_NAME
    for seed in (0, 1, 12345, 2**40 + 7):
        for name in ("", "onset", "payment_event::3", "away::2024"):
            got = mod._substream(seed, name).random()
            want = _legacy_formula_b(namespace, name, seed).random()
            assert got == want, (module_name, seed, name)


def test_a_valid_key_is_accepted_before_any_refusal_is_asserted():
    """Defect: a guard that refuses EVERYTHING passes every refusal test below."""
    assert substream_key("NS", "", 0) == b"NS::::0"
    assert substream_key("NS", "a::b", -3) == b"NS::a::b::-3"


@pytest.mark.parametrize(
    "namespace, name, seed, error",
    [
        ("", "onset", 1, ValueError),  # unnamespaced = the Formula-A collision
        ("A::b", "c", 1, ValueError),  # would share a key with ("A", "b::c")
        ("A:", "b", 1, ValueError),
        ("NS", 3, 1, TypeError),
        ("NS", "x", "1", TypeError),
        ("NS", "x", 1.0, TypeError),
        ("NS", "x", True, TypeError),
    ],
)
def test_a_key_that_could_collide_is_refused_with_its_reason(namespace, name, seed, error):
    """Defect: an empty or colon-bearing namespace falls back to a key another
    subsystem can reach, and two mechanisms share one stream."""
    with pytest.raises(error):
        substream(namespace, name, seed)


def test_the_key_is_injective_over_the_names_the_world_actually_uses():
    """Defect: two distinct (namespace, name, seed) triples hash the same bytes."""
    triples = [
        (ns, name, seed)
        for ns in ("A", "AB", "W2_6_sme_distress")
        for name in ("", "b", "b::1", "b::1::2", "::", "x:y")
        for seed in (0, 1, 12, -1)
    ]
    keys = [substream_key(*t) for t in triples]
    assert len(set(keys)) == len(triples)


def test_no_new_private_seed_derivation_and_no_stale_exemption():
    """Defect: a module copies the formula again instead of importing the
    primitive -- the census grew from 11 to 18 copies between DISCOVER and BUILD."""
    found = _private_derivations()
    canonical = ("simulation/rng_substream.py", "substream")
    assert canonical in found, "the census cannot see the canonical definition -- it is blind"
    assert found - {canonical} - NOT_YET_MIGRATED == set(), "new private derivation(s)"
    assert NOT_YET_MIGRATED - found == set(), "migrated: delete from NOT_YET_MIGRATED"
