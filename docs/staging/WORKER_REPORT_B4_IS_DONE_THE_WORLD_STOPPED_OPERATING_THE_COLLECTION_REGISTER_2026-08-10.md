# WORKER REPORT — B4 is DONE; the world stopped operating the supplier's collection register

**Filed:** 2026-08-10, worker seat (scheduled tick).
**Atom:** `KNIFE3_wall_crossing_paydown` (KNIFE pass 3 of 4, lane `H_harness`), **step 13**.
**Level:** UNCHANGED at 0. This is one step of a pass that is visibly still cutting — 48 crossings
remain owed across `A_composition_lift` (44) and `B2_company_brain_decides_the_world` (4). No level
was moved and none is claimed.

## WHAT LANDED

`simulation.dd_collection_book -> company.billing.direct_debit` is **cut**. **49 → 48 live
crossings** (47 → 46 direct). `B4_billing_mechanics_reached_directly` is now **4 of 4 edges — the
first design in this register to close completely**, and its block has left §3 (a design no `owed`
row references is rc 2 by the tool's own rule).

Full write-up: `docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` §3h.

## WHY THIS EDGE WAS THE HARD ONE

B4's other three edges were the world *consulting* the company. This one was different in kind, and
the design block said so: `dd_collection_book` did not consult the company's billing module, it
**BUILT the company's artefact** — opened a `DirectDebitBook`, created mandates on it, ran a
rolling-median re-estimate deciding when to write to the customer's bank, snapped collections onto
the anniversary with `next_collection_on_day`, and appended `DDPaymentAttempt`s under the register's
own outcome vocabulary. A household does not run its supplier's collections desk.

Now: `company/billing/dd_collections_desk.py` owns the register and issues three instructions
(`MandateSetupInstruction`, `AmendmentInstruction`, `CollectionInstruction`) through
`company/interfaces/dd_collection_instructions.py`. The world puts them on the Bacs rails and
reports what happened to the money.

## THE FINDING WORTH KEEPING — a blocker inherited from a sibling row is a CLAIM, not a fact

Both of B4's landed doors (`credit_refund_requests.py`, `dd_review_outcome.py`) recorded the same
structural blocker: the design asks for a PUSH, there was no company-side emitter, so the push is
owed to `A_composition_lift`. Step 11 built a *bill* emitter and both pushes stayed owed against it.

This edge's row carried the same inherited sentence — and it was **wrong for this edge**. That
blocker is specific: a *bill* attribute needs a *bill* emitter. What this edge needed was a
**collection instruction**, and the desk that decides collections is its own emitter. Reading the
sibling's blocker off the row would have parked this edge behind `run_phase2b`'s 32-edge composition
problem indefinitely.

Same shape as step 12's finding one section up, where an edge sat in the wrong design class while
every count above it stayed correct: **the register's method is ruling by class, so a claim
inherited across rows in a class is exactly as load-bearing as a miscounted edge, and nothing in the
tooling looks for one.**

## EVIDENCE

**No number moves, and it is measured.** 140-customer / 30-month population through
`build_dd_collection_book` before and after: **74 mandates, 2,220 attempts, sha256
`fb084d0d52a9136576d71652d7a6430e7d39e21366f84609cde2d42f79bc2fb0` on both sides.** Deliberately NOT
pinned in a test — an equivalence claim about a moment in history, and pinning a generated value
would red on the next legitimate change to the routine while proving nothing about it.

**R15, both mutations RUN on the real tree, not named:**

1. **The exposure no existing instrument can see.** Re-exporting `DirectDebitBook` at the seam hands
   the world the register's construction back. Performed live → the seam control **reds (2 failed /
   7 passed)**.
2. **THE VACUITY GUARD.** Under the *same live widening*,
   `tests/architecture/test_epistemic_wall_ratchet.py` is **12 passed / 0 failed** — the ratchet is
   blind by construction, measured rather than argued. Without this, the control would be a
   `donated residual`. The in-suite version compares `live_crossings()` before/after.
3. **Re-injecting the deleted import is caught**, by a control that asks the WALKER, never a
   substring — the docstrings explaining the cut contain both `company.billing.direct_debit` and
   `DirectDebitBook`, so a text scan would fail on its own subject.

**A pre-existing R15 control had to be RE-AIMED, and that is worth one line.**
`test_direct_debit_dd1_staggered.py::test_mutation_removing_the_snap_collapses_the_dates` patched
`next_collection_on_day` on the SIM module. That name is exactly what the cut removed, so the
mutation lost its subject. Re-pointed at the desk; the property is unchanged. The class —
*moving a routine across the wall un-aims every mutation pointed at its old home* — is
**self-detecting**, because `monkeypatch.setattr` raises on a missing attribute rather than
silently patching nothing. Recording it as verified-fail-closed rather than as a new control.

**Suites:** `tests/company/billing/` + `tests/company/interfaces/` + the three DD suites — 2,413
passed / 1 failed→fixed (the re-aimed mutation above) / 1 xfailed. `tests/architecture/` 92 passed
(2 pre-existing ruff-ratchet reds, see below). `tests/tools/` register suites 89 passed.
`tools/knife_hotspot_measure.py` and `tools/wall_crossing_dispositions.py` agree at 48.
`tools.epistemic_verifier` **PASS** (543 files).

## TWO REDS THAT ARE NOT THIS CUT'S, MEASURED NOT ASSUMED

`test_static_quality_ratchet.py` reds on `I001` and `F841`. Both were checked against a
`git archive HEAD` export rather than assumed:

- **`I001` 1386 vs baseline 1384 — already red on HEAD**, and unchanged by this cut (1386 both
  sides; `simulation/dd_collection_book.py`'s own I001 pre-exists this edit byte for byte).
- **`F841` 131 vs baseline 130** — the extra one is `tools/scale_probe_10k.py:731`, which is
  **UNTRACKED**: another lane's in-flight work in the shared tree. Not committed here (pathspec
  commit), not mine to fix.

This is the known `ruff baseline is calibrated to uncommitted work` class, already staged.
Per SELF_INTERRUPT_DISCIPLINE: reported, not fixed on sight.

## STATE OF THE PASS

| design | owed edges |
|---|---|
| `A_composition_lift` | 44 — `run_phase2b` (32 direct + 2 indirect), `run_phase4c_on_phase2b` (10) |
| `B2_company_brain_decides_the_world` | 4 — the `customer_events` churn inversion, a coupled-triad build its own block forbids attempting as a mechanical move |
| `B4_billing_mechanics_reached_directly` | **0 — CLOSED** |

B5's residual PUSH remains owed against step 11's bill emitter and is untouched.
