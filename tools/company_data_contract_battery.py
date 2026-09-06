#!/usr/bin/env python3
"""R15 mutation battery for `tools/generate_company_data.py`, scored PER SUITE.

The FIFTH subject of the convergence-evidence sweep. The screen
(`python3 -m tools.converged_contract_screen --module tools/generate_company_data.py`)
answers 4 callers / 1 direct importer / 133 reaching suites.

This file is the SPEC -- the suites, the contracts, the two reachability anchors
and the null-round marker. The procedure lives in `tools/contract_battery.py`;
what it guarantees and why is documented there and deliberately not restated.

Pre-registration, written and landed BEFORE this ran:
`docs/staging/records/SEAT_PREREG_THE_SECOND_FLOOR_SEPARATES_A_CALLER_THAT_CATCHES_FROM_A_SUITE_THAT_IS_BLIND_2026-09-06.md`

THE DRAWN REASON EXPIRED, AND THE REPLACEMENT IS NOT THE SAME QUESTION
---------------------------------------------------------------------
This subject was ranked for having ZERO test importers. It has one --
`tests/tools/test_generate_company_data.py`, 16 tests, dedicated -- and it landed
before the item was drawn. The premise is spent and is recorded spent rather than
worked around. What replaces it is the reason this subject is worth a battery
anyway, and it is a stronger one: it is the first subject in the sweep whose
CALL SITES defeat the instrument.

THE FOURTH CALLER IS NOT A CALLER
---------------------------------
The screen's fourth caller is `tools.test_generate_company_data`, which is
`tests/tools/test_generate_company_data.py` BYTE FOR BYTE (`diff` is empty). It
is in NEITHER `HEAD` NOR `origin/main` -- `cbd5f6298` moved it to where a runner
looks -- and exists only as another lane's staged index entry. The screen reads
the working tree, so it is counting the file that repair removed. Scoring
it would enter the dedicated suite in the caller column as well as the direct
one, and `survived_all` -- whose population is the CALLER suites -- would then be
partly answered by the subject's own tests. It is excluded, and the screen
counting it is a screen finding, not a suite.

WHY THIS SUBJECT NEEDED A SECOND FLOOR
--------------------------------------
All three real callers import the subject LAZILY, inside a function body. Two of
them wrap that import in `except Exception`:

    background/process_run_complete.py:4103   try: ... except Exception as exc:
                                              log("company.json generation failed: ...")
    tools/generate_world_data.py:407          try: ... except Exception:
                                              return _POP_UNSTATED, "...could not be imported"
    tools/generate_dashboard_data.py:2631     unguarded

So the standard import-time floor -- which raises an `Exception` -- is CAUGHT AT
THE CALL SITE for two of the three, and their suites stay green while running the
caller end to end. On every previous subject that green was stamped
`NEVER REACHES`, and here that would be false in the flattering direction twice
over: it excuses the row, and it hides that the call site cannot propagate a
failure of the subject at all.

`HARD_POISON_*` below raises a `BaseException` subclass, which `except Exception`
does not catch. Green under the first floor and RED under the second is
`swallows_subject_failure`: reached, executed, and structurally unable to fail.

Usage:
    python3 -m tools.company_data_contract_battery
    python3 -m tools.company_data_contract_battery --only M1 --suites test_generate_company
"""
from __future__ import annotations

from tools.contract_battery import BatterySpec, run

#: The dedicated suite. 16 tests, and the only one that NAMES contracts of this
#: module (`_cost_to_serve_distribution`, `_arrears_distribution`). It is scored
#: as a caller column because it is a real importer of the subject; its twin in
#: `tools/` is not (see the module docstring).
DIRECT_SUITES = ("tests/tools/test_generate_company_data.py",)

#: One suite per real caller.
#:
#: `tests/saas/test_net_after_cts_and_blindfold_arithmetic.py` is the ONLY suite
#: in the tree that imports `tools.generate_world_data`, and it imports
#: `_crossing_blindfold` -- not `_book_population_class`, the function that
#: reaches this subject. It is scored anyway and not silently dropped: "the
#: caller's only suite does not run the path to the subject" is the answer, and
#: excluding it would delete the question.
CALLER_SUITES = (
    "tests/tools/test_generate_dashboard_data.py",
    "tests/saas/test_net_after_cts_and_blindfold_arithmetic.py",
    "tests/background/test_process_run_complete.py",
)

SUITES = DIRECT_SUITES + CALLER_SUITES

#: Two suites with no import path to the subject. The poison rounds must leave
#: these GREEN; a floor that reddens everything for a reason unrelated to the
#: subject reads exactly like total reachability.
CONTROL_SUITES = (
    "tests/background/test_delivery_lane.py",
    "tests/design/test_atom_notes_store.py",
)

#: (id, the contract as the module states it, old, new). Each `old` appears
#: exactly once in the subject and the engine refuses the row if it does not.
#:
#: M1-M6 are `segment_revenue_mix` and `_book_mix` -- the converged surface, the
#: one thing TWO callers import. M7-M10 are the distributions the dedicated suite
#: was written for, included so the direct column can be told from the caller
#: columns rather than assumed stronger.
MUTATIONS = (
    (
        "M1",
        "an EMPTY segment mix is unavailable -- never a zero mix, which reads as a DOMESTIC book",
        '        return dict(available=False, reason="segment_annual missing or empty")',
        '        return dict(available=True, reason="segment_annual missing or empty",\n'
        '                    total_revenue_gbp=0.0, domestic_revenue_share_pct=0.0,\n'
        '                    non_domestic_revenue_share_pct=0.0, composition_class="domestic",\n'
        '                    revenue_by_segment={}, share_by_segment={},\n'
        '                    unclassified_revenue_gbp=0.0, unclassified_segments=[],\n'
        '                    dominance_threshold_pct=_DOMINANCE_SHARE_PCT, years=[])',
    ),
    (
        "M2",
        "a mix with NO POSITIVE REVENUE is unavailable, not a book of zero shares",
        '        return dict(available=False, reason="segment_annual carries no positive revenue")',
        '        return dict(available=True, reason="segment_annual carries no positive revenue",\n'
        '                    total_revenue_gbp=0.0, domestic_revenue_share_pct=0.0,\n'
        '                    non_domestic_revenue_share_pct=0.0, composition_class="domestic",\n'
        '                    revenue_by_segment={}, share_by_segment={},\n'
        '                    unclassified_revenue_gbp=0.0, unclassified_segments=[],\n'
        '                    dominance_threshold_pct=_DOMINANCE_SHARE_PCT, years=[])',
    ),
    (
        "M3",
        "UNCLASSIFIED revenue stays in the denominator -- an unknown segment never inflates "
        "the known shares (the fail-silent shape css_statement.py guards against)",
        "    total = sum(revenue.values()) + sum(unclassified.values())",
        "    total = sum(revenue.values())",
    ),
    (
        "M4",
        "the DOMINANCE threshold is what makes a book non-domestic -- not any non-zero share",
        "    if non_domestic_pct >= _DOMINANCE_SHARE_PCT:",
        "    if non_domestic_pct >= 0.0:",
    ),
    (
        "M5",
        "a genuinely MIXED book says mixed -- it is not filed under either population class",
        '        composition_class = "mixed"',
        '        composition_class = "domestic"',
    ),
    (
        "M6",
        "a segment's per-customer figures divide by THAT segment's own n -- never a fallback "
        "to the whole-book denominator, which is the blend this whole block exists to remove",
        "        n = counts.get(prefix)",
        "        n = counts.get(prefix) or n_total",
    ),
    (
        "M7",
        "account counts come from each account's OWN `segment` field, not an id substring "
        "(the id-substring reading files the SME accounts under residential)",
        '        seg = str(c.get("segment") or "").strip().lower()',
        '        seg = "i&c" if "IC" in str(c.get("account_id") or "") else "resi"',
    ),
    (
        "M8",
        "the COST-TO-SERVE distribution fails closed on an empty sample -- never a zero total "
        "the page renders as a real figure",
        '        rows.append((float(cts), seg, c))\n'
        '    if not rows:\n'
        '        return {"available": False, "n": 0}',
        '        rows.append((float(cts), seg, c))\n'
        '    if not rows:\n'
        '        return {"available": True, "n": 0, "min_gbp": 0.0, "median_gbp": 0.0,\n'
        '                "mean_gbp": 0.0, "max_gbp": 0.0, "values_gbp": []}',
    ),
    (
        "M9",
        "the ARREARS distribution fails closed on a ledger with no billed/banked pair",
        '        rows.append((arrears, seg, samp_custs.get(cid) or {}, lc))\n'
        '    if not rows:\n'
        '        return {"available": False, "n": 0}',
        '        rows.append((arrears, seg, samp_custs.get(cid) or {}, lc))\n'
        '    if not rows:\n'
        '        return {"available": True, "n": 0, "min_gbp": 0.0, "median_gbp": 0.0,\n'
        '                "mean_gbp": 0.0, "max_gbp": 0.0, "values_gbp": []}',
    ),
    (
        "M10",
        "gross arrears exposure is a FLOOR -- credit balances do not net off a bad-debt base",
        "    gross_exposure = round(sum(a for a, _, _, _ in rows if a > 0), 2)",
        "    gross_exposure = round(sum(a for a, _, _, _ in rows), 2)",
    ),
)

#: THE FIRST FLOOR: an `Exception` at import time. Stated before the run, with
#: its expected weakness named: two of the three call sites catch this, so a
#: green here is NOT evidence a suite never ran the caller.
POISON_OLD = "\ndef generate():"
POISON_NEW = ('\nraise RuntimeError("POISON: generate_company_data reachability floor")'
              "\n\n\ndef generate():")

#: THE SECOND FLOOR, and the reason the engine now has one. `except Exception`
#: does not catch a `BaseException` subclass, so this passes through the two
#: swallowing call sites and reddens any suite that actually RUNS them. Green
#: under the first and red under this one is REACHES-AND-SWALLOWS: the third
#: state, and the one that reads most like the good answer.
#:
#: It is raised at module scope for the same reason the first floor is -- the
#: contract under test is not reached until the import succeeds, so the import is
#: where both floors have to bite.
HARD_POISON_OLD = "\ndef generate():"
HARD_POISON_NEW = (
    "\nclass _HardPoison(BaseException):\n"
    '    """Not an Exception: `except Exception` at a call site does not catch it."""\n'
    "\n"
    "\n"
    'raise _HardPoison("HARD POISON: generate_company_data second floor")'
    "\n\n\ndef generate():"
)

#: THE NULL ROUND. This subject is a GENERATOR whose output other tools read, and
#: the tree contains suites that read a generator's SOURCE and walk it as an AST
#: (`tests/tools/test_website_integrity_fix.py` does exactly that for the
#: front-door mix claim). So `died` and "the suite executed the mutated line" are
#: separable claims here and the round is live rather than ceremonial.
#:
#: The marker carries both halves, as on the previous subject: a module-level
#: no-op assignment (new bytes, a new AST node, no behaviour) and a comment
#: naming the two modules that import this one lazily (new bytes, NO AST node) --
#: the exact input that separates a substring search from a walk.
NULL_OLD = "def generate():"
NULL_NEW = (
    "# NULL ROUND (tools/contract_battery.py): behaviour-preserving by construction.\n"
    "# It names generate_world_data and generate_dashboard_data on purpose -- a substring\n"
    "# search for either would be satisfied by this comment and an AST walk would not.\n"
    "# Neither is imported here, so both readings must still return unreachable.\n"
    "_NULL_ROUND_MARKER = None\n"
    "\n"
    "\n"
    "def generate():"
)

SPEC = BatterySpec(
    name="company_data",
    subject="tools/generate_company_data.py",
    suites=SUITES,
    mutations=MUTATIONS,
    poison_old=POISON_OLD,
    poison_new=POISON_NEW,
    hard_poison_old=HARD_POISON_OLD,
    hard_poison_new=HARD_POISON_NEW,
    control_suites=CONTROL_SUITES,
    null_old=NULL_OLD,
    null_new=NULL_NEW,
)


def main(argv: list[str] | None = None) -> int:
    return run(SPEC, argv)


if __name__ == "__main__":
    raise SystemExit(main())
