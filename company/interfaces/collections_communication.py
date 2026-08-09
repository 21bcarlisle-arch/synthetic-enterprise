"""The company's COLLECTIONS-COMMUNICATION surface — the one place the world may
learn the tone of a dunning letter it received.

WHY THIS MODULE EXISTS (KNIFE pass 3, design B5_collections_tone_is_an_event_attribute)
---------------------------------------------------------------------------------------
`simulation/arrears_engine.py` used to `from company.policy.decision_policy import
CURRENT_POLICY, tone_for` and apply the company's dunning POLICY itself, in order to
decide how a customer's payment probability was nudged.

The register's ruling separates two things that import collapsed into one:

  * What the world LEGITIMATELY observes — **the letter that arrived, and its tone.**
    A real customer receives a firmly- or empathetically-worded arrears letter and
    reacts to it. Their reaction is world physics, and the tone is an attribute of the
    communication, so the world must be able to see it.
  * What the world MUST NOT read — **the policy that chose the tone.** `DecisionPolicy`
    is the company's internal decision object: its `tone_mode`, its A/B cohort split,
    its thresholds. A real supplier's customers do not read its collections strategy
    document; they read the letter.

Importing `CURRENT_POLICY` handed the world both. This module publishes only the first.

WHAT CROSSES, PRECISELY
-----------------------
One string per (customer, billing period): the tone the company chose for that cycle's
communication. `DecisionPolicy` itself is deliberately NOT re-exported, and no argument
of that type is accepted — a caller cannot reach the policy object through this door, so
the SIM cannot come to depend on the company's decision machinery by accident. That is
the property `tests/company/interfaces/test_collections_communication_seam.py` exists to
keep true, and it is mutation-proven.

**This is a cut, not laundering.** `company/interfaces/` is WALKED by
`tools/epistemic_wall.py` byte for byte, exactly as `company/policy/` is. Nothing moved
out of the instrument's reach. The edge is exempt because it terminates on the sanctioned
crossing surface — the ratchet's own published `SEAM_PACKAGE` rule, whose doctrine string
names this exact remedy — and not because the measurement stopped looking. Contrast
`docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` §2b, where relocating a composition
root to `tools/` was REFUSED, for the reason that does not apply here: `tools/` is outside
`WALL_DIRS` and the walker never looks there.

THE HONEST LIMIT — this is a PULL, and the design asks for a PUSH
-----------------------------------------------------------------
B5 as written says the tone should become "an attribute of the collections-action event
the company emits", with the arrears engine reacting to an event it RECEIVES. This module
does not achieve that half, and does not pretend to: the world still asks, per bill, at
the moment it needs the answer.

The reason is structural and was measured, not assumed. There is no company-side bill
emitter to stamp the attribute onto: the bill dicts these consumers read are built by
`simulation/run_phase4c_on_phase2b.py::build_monthly_bills` — a SIM composition root, and
one of the ten shape-A files carrying 14 owed edges of its own. Stamping `collections_tone`
onto a bill at emission therefore cannot happen until bill emission itself sits on the
company side, which is `A_composition_lift`'s work and not this pass's.

Doing it anyway, from where the code stands today, would mean the SIM stamping the bill
with a value it pulled from the company and then reading its own stamp back — the shape of
a push with the substance of a pull, and a strictly worse artefact than an honest pull
through a named door. So the push is recorded as owed, not simulated. What this module
does buy, now: the policy OBJECT and its TYPE are unreachable from the SIM, the crossing
is legible at one reviewable chokepoint, and the remaining dependency is a single string.
"""

from __future__ import annotations

from company.policy.decision_policy import CURRENT_POLICY, tone_for

__all__ = ["collections_tone_for"]


def collections_tone_for(customer_id: str, period_end: str) -> str:
    """The tone of the collections communication the company sent this customer for the
    billing period ending `period_end` — e.g. "empathetic_toned" / "firm_toned".

    Company-observable by construction: the company chose this, so the world seeing it is
    the world seeing a letter it was sent. Never reads
    `simulation/nudge_physics.py`'s hidden tone-susceptibility — that is the customer's
    private responsiveness, and the company discovers it only statistically, via
    `company/analytics/nudge_discovery.py`.

    Resolved against the LIVE policy (`CURRENT_POLICY`). That is the pre-existing
    behaviour of the call site this replaced, preserved deliberately and byte for byte so
    this cut changes no payment outcome. It is also a known limit worth naming: a run that
    swaps the policy (`tools/run_frozen_baseline.py`'s NAIVE arm) does NOT swap the tone
    here, because this resolves the live policy rather than the run's. Filed as a finding
    rather than fixed inside a wall pass — see
    `docs/staging/WORKER_FINDING_THE_NAIVE_ARM_KEEPS_THE_LIVE_TONE_2026-08-10.md`.
    """
    return tone_for(CURRENT_POLICY, customer_id, period_end)
