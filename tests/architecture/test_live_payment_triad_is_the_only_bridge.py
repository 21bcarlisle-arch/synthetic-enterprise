"""R15 control for KNIFE pass 3 step 33 — disposition register §3ab.

WHAT THIS GUARDS
----------------
`simulation/run_phase2b.py` reaches `company.billing.account_ledger` and
`company.billing.payment_observation_consumer` INDIRECTLY, through a bridge
package. Those two rows are the register's last two indirect crossings.

Until this step they had **two** first-hop entries, not one:

  * `background.live_payment_triad` — the harness that legitimately holds the
    hidden SIM truth and the company's belief side by side to compute the gap
    (COUPLED_TRIAD_DESIGN 1.3), and
  * `tools.couple_w2_11_d5` — imported at function scope inside the run's
    fidelity-cell block purely to call `detection_cell_measurements`, which the
    run then fed with `_payment_triad.consumer`: a LIVE COMPANY OBJECT, held by
    the world's composition and handed across.

The register's row printed only `hops=`, the SHORTEST chain, so a reader taking
it at face value saw one import where there were two. Removing the first alone
would have cut nothing. This control pins BOTH halves of what step 33 did.

R15 — THE THREE KILLER PATTERNS, ANSWERED
-----------------------------------------
TAUTOLOGY   — no assertion here re-runs `detection_cell_measurements` and
              compares its output to itself before and after the move. That
              comparison would pass whatever the method did, because the
              method's body IS the old call site. What is asserted instead is
              REACHABILITY: what the world can still obtain, and through which
              bridges — a property the refactor could actually have got wrong,
              and did get wrong once already on a sibling door (§3aa row 1).
FAIL-OPEN   — control 2 runs the walker over a SYNTHETIC tree carrying the
              pre-step-33 shape and asserts it reports two entries there. A
              control that answered "one" on a tree that really has two would
              be measuring nothing on the real tree either.
FAIL-SILENT — an import failure is a FAILED test, never a skip. There is no
              `pytest.importorskip` in this module.
"""

from __future__ import annotations

import os
import sys
import textwrap

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from background.live_payment_triad import LivePaymentTriad  # noqa: E402
from tools.epistemic_wall import (  # noqa: E402
    indirect_crossings,
    live_indirect_crossings,
)

RUN = "simulation.run_phase2b"
COMPANY_SIDE = ("company", "saas")
SECOND_ENTRY = "tools.couple_w2_11_d5"
THE_BRIDGE = "background.live_payment_triad"


def _public_values(obj):
    """Every value the object hands out without being given arguments.

    Deliberately NOT `__all__`, not `vars()`, and not a name allowlist: the
    question is what a SIM caller can actually get hold of, so it is asked by
    getting hold of it.
    """
    for name in dir(obj):
        if name.startswith("_"):
            continue
        value = getattr(obj, name)
        if callable(value):
            continue  # a bound method is not an object handed over
        yield name, value


def _company_side(value) -> bool:
    return type(value).__module__.split(".", 1)[0] in COMPANY_SIDE


# --------------------------------------------------------------------------
# Control 1 — the world cannot obtain a company object from the triad.
# --------------------------------------------------------------------------

def test_the_triad_hands_out_no_company_object():
    triad = LivePaymentTriad()
    leaked = {n: type(v).__module__ for n, v in _public_values(triad) if _company_side(v)}
    assert leaked == {}, (
        f"LivePaymentTriad's public surface hands the world a company object: {leaked}. "
        "The run's composition must not hold the D5 consumer or its ledger book — "
        "the harness holds both sides, the world holds neither."
    )
    # Vacuity: the surface actually has something on it, so an empty walk is not
    # what made the assertion above pass.
    assert [n for n, _ in _public_values(triad)], (
        "no public attributes were inspected at all — the control measured nothing"
    )


def test_R15_mutation_a_restored_consumer_property_is_caught():
    """The exact deleted property, put back. The control must red."""

    class WithConsumer(LivePaymentTriad):
        @property
        def consumer(self):
            return self._consumer

    triad = WithConsumer()
    leaked = {n: type(v).__module__ for n, v in _public_values(triad) if _company_side(v)}
    assert "consumer" in leaked, (
        "the reachability walk did not see a restored `consumer` property — "
        "control 1 cannot fire on its own named defect"
    )


def test_the_private_consumer_is_still_there():
    """Not a formality: the cut must remove the DOOR, never the harness.

    A `LivePaymentTriad` that stopped holding the consumer would make control 1
    pass by breaking the thing the triad exists to do.
    """
    triad = LivePaymentTriad()
    assert _company_side(triad._consumer)
    assert _company_side(triad._ledger_book)


# --------------------------------------------------------------------------
# Control 2 — one bridge entry, and the walker can see two.
# --------------------------------------------------------------------------

def test_the_run_reaches_company_through_exactly_one_bridge():
    rows = {k: v for k, v in live_indirect_crossings().items() if k[0] == RUN}
    offenders = {k: v.entries for k, v in rows.items() if SECOND_ENTRY in v.entries}
    assert offenders == {}, (
        f"{RUN} reaches company through {SECOND_ENTRY} as well as the harness bridge: "
        f"{offenders}. Cutting one entry cuts no edge while the other stands."
    )
    for key, edge in rows.items():
        assert edge.entries == (THE_BRIDGE,), (
            f"{key}: expected the harness bridge as the sole entry, got {edge.entries}"
        )


def _synthetic_tree(tmp_path, run_body: str) -> str:
    root = tmp_path / "tree"
    files = {
        "simulation/run_phase2b.py": run_body,
        "background/live_payment_triad.py": (
            "from company.billing.account_ledger import LedgerBook\n"
        ),
        "tools/couple_w2_11_d5.py": (
            "from company.billing.account_ledger import LedgerBook\n"
        ),
        "company/billing/account_ledger.py": "LedgerBook = object\n",
    }
    for rel, body in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(body))
    for pkg in ("simulation", "background", "tools", "company", "company/billing"):
        (root / pkg / "__init__.py").write_text("")
    return str(root)


def test_R15_mutation_the_walker_reports_two_entries_on_the_pre_step_33_shape(tmp_path):
    """FAIL-OPEN answer: on a tree that really carries both imports, the same
    measurement control 2 uses must report BOTH. If it reported one here, its
    verdict on the real tree would mean nothing."""
    before = _synthetic_tree(
        tmp_path / "before",
        """
        from background.live_payment_triad import LivePaymentTriad

        def main():
            from tools.couple_w2_11_d5 import detection_cell_measurements
        """,
    )
    after = _synthetic_tree(
        tmp_path / "after",
        "from background.live_payment_triad import LivePaymentTriad\n",
    )
    key = ("simulation.run_phase2b", "company.billing.account_ledger")

    two = indirect_crossings(before)
    assert key in two, "the synthetic pre-step-33 tree produced no indirect crossing at all"
    assert two[key].entries == (THE_BRIDGE, SECOND_ENTRY), (
        f"the walker saw {two[key].entries} on a tree carrying both imports — "
        "control 2 cannot distinguish one entry from two"
    )

    one = indirect_crossings(after)
    assert key in one, (
        "the post-step-33 shape lost the edge entirely — that would be a cut, and "
        "step 33 did not claim one"
    )
    assert one[key].entries == (THE_BRIDGE,)


def test_the_edge_count_did_not_move():
    """Step 33 removed an ENTRY, not an EDGE, and says so.

    Pinned because the seductive misreading of this step is that it paid down
    the register. It did not: 7 live crossings before, 7 after.
    """
    rows = {k: v for k, v in live_indirect_crossings().items() if k[0] == RUN}
    assert len(rows) == 2, (
        f"expected the two indirect rows to still be LIVE, found {sorted(rows)}"
    )
