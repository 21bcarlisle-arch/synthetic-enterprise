"""Seam: the world hands over the bills and takes back the supplier's ANNUAL DD REVIEW.

KNIFE pass 3, step 32, 2026-08-17, disposition register §3aa —
`B13_the_annual_dd_review_is_the_suppliers_own_desk`.

WHY THIS DOOR EXISTS, AND WHY IT IS NOT `A_composition_lift`'s WORK
--------------------------------------------------------------------
`simulation/run_phase4c_on_phase2b.py` used to
`from company.billing.dd_review_runner import run_annual_reviews` and drive the
supplier's annual Direct Debit review itself. That edge sat `owed` to
`A_composition_lift` for seven steps, and the register said in TWO places, in its
own words, that the design could never cut it:

  * `simulation/run_phase4c_on_phase2b.py`'s own docstring — *"no further
    composition lift removes it, because there is no company process here left to
    lift — only a value being carried from a company organ into the run's output
    dict."*
  * `company/interfaces/billing_experience.py`'s docstring — *"it is the last one
    on that module, and it is the one this design was never going to cut."*

An `owed` row whose named design has publicly declared the edge out of its own
scope is a decorative nomination. `tools/wall_crossing_dispositions.py` cannot
catch that one, because the word in the `design=` field is a real design block
that really exists — the DECORATIVE test looks for "later"/"tbd", not for a
design that has excused itself. So the row was parked forever behind a cut nobody
intended to make, which is the failure this register keeps rediscovering under
this exact design (steps 28, 29 and 30 each found one).

WHAT THE RE-RULING SAYS
------------------------
`A_composition_lift` cuts by LIFTING A PROCESS: the world stops composing the
supplier's routine and the routine moves company-side. §3h was right that there is
no process here left to lift — `run_annual_reviews` is already company-side, pure
and read-only. The defect is therefore not composition at all. It is that the
supplier's DD desk is REACHABLE: importing the runner module hands the world
`review` (the ±5% variance band — a modelling convention applied under the
SLC 27.15 duty, not a licence rule), `DDAction`, `DDReviewBook` and
`LARGE_INCREASE_THRESHOLD_PCT` (the 15% bill-shock cut). Those are the supplier's
own compliance reading and its own materiality judgement, and a real customer does
not read them. The remedy for a routing residual is a DOOR, and the door is the
whole remedy — which is exactly why it needed a design of its own rather than a
seat in a queue behind a composition lift.

WHAT CROSSES, PRECISELY
------------------------
Bills in — a list of the company's OWN issued bill dicts, which is data the world
already holds. A JSON-safe `dict` out: `{"summary": {...}, "events": [...]}`, the
same shape the run output surface and `saas/reporting/annual_report.py` already
consume.

**No company TYPE crosses at all.** This door deliberately returns the serialised
form rather than `DDReviewRunResult`, which is a stronger cut than the four
sibling doors on this module (`bill_assembly`, `accounting_close`,
`customer_value`, `billing_experience`) each of which returns a company view
object. It costs nothing here because the single call site already immediately
called `.serialise()` and put the dict in the run output — so the SIM never wanted
the object, and now it cannot obtain one. `DDReviewBook`, `DDReviewEvent`,
`DDReviewRunResult`, `DDAction`, `review` and `LARGE_INCREASE_THRESHOLD_PCT` are
all unreachable through this module.

**This is a cut, not laundering**, by the same measured argument
`company/interfaces/collections_communication.py` records: `company/interfaces/`
is WALKED by `tools/epistemic_wall.py` byte for byte, exactly as
`company/billing/` is. Nothing moved out of the instrument's reach. The edge is
exempt because it terminates on the sanctioned crossing surface — the ratchet's
own published `SEAM_PACKAGE` rule — and not because the measurement stopped
looking. Contrast register §2b, where relocating a composition root to `tools/`
was REFUSED, for the reason that does not apply here: `tools/` is outside
`WALL_DIRS` and the walker never looks there.

THE HONEST LIMIT
-----------------
This is a PULL. The world asks, once per run, at the moment it needs the answer.
The push — the company EMITTING its review events onto a stream the world reacts
to — is the same debt `collections_communication.py` records, and it is not paid
here and not pretended. What it buys is real and bounded: the desk's rule and its
thresholds are unreachable from the SIM, and the crossing is one legible
chokepoint carrying JSON.

**DD4b is still not built** and this door does not build it. Routing a
`large_increase` review into the live churn/resentment engine shifts ground-truth
churn and needs population-level verification; `dd_review_runner`'s docstring
records it as the registered next gated step and that is still true. This door
changes who can reach what, and no number.

R15 PROOF: `tests/company/interfaces/test_dd_review_seam.py` — three controls,
each with a mutation that performs its own named defect.
"""

from __future__ import annotations

__all__ = ["annual_dd_review_view"]


def annual_dd_review_view(
    bills: list[dict],
    opening_dd_gbp: dict | None = None,
) -> dict:
    """The supplier's annual DD review over its own issued `bills`, serialised.

    `opening_dd_gbp` carries the monthly amount the supplier SET when each
    account opened — the annualised estimate that replaced the first-issued-bill
    artefact on 2026-09-02 (atom `D_opening_dd_seasonal_sizing`). It crosses as
    plain floats per customer id: the AMOUNT, never the routine that chose it,
    which is the same property `dd_review_outcome` holds for the reviewed
    amount. A customer absent from it is REFUSED and counted in the serialised
    summary's `unestimated_customers`, never opened from a bill.

    Returns the JSON-safe `{"summary": ..., "events": [...]}` form. Nothing of
    the supplier's decision machinery — the variance rule, the bill-shock
    threshold, the review book type — is reachable through this door, which is
    the property `test_dd_review_seam.py` exists to keep true.

    THE IMPORT IS FUNCTION-SCOPE ON PURPOSE, and this is not a style choice.
    Written at module scope it binds `run_annual_reviews` into THIS module's
    namespace, and a SIM caller could then write
    `from company.interfaces.dd_review import run_annual_reviews` — obtaining the
    desk's object-returning entry point through a path the ratchet EXEMPTS,
    because it terminates under `SEAM_PACKAGE`. The cut would be defeated
    invisibly. Binding it inside the call leaves this module's namespace carrying
    the door and nothing else. It was control 1 of the R15 suite that found this
    on the door's own first draft, which is the reason the control is written
    against reachability rather than against `__all__`. The precedent for the
    shape is `simulation/arrears_engine.py`, which reaches the
    collections-communication seam the same way.
    """
    from company.billing.dd_review_runner import run_annual_reviews

    return run_annual_reviews(bills, opening_dd_gbp=opening_dd_gbp).serialise()
