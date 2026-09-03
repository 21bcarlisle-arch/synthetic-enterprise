**Severity:** RECORDED · **Lane:** E_finance_treasury · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing`

# Pre-registration — whether the treasury figure's withheld clock can be repaired, and what reds if it is

*Delivery seat, 2026-09-03, lane-0. Written BEFORE the repair was attempted and BEFORE any test was
run against it. Continues the lane-0 direction whose act (c) says: establish whether treasury end =
treasury start + net margin is an accounting identity or a coincidence of this book. It is an
identity, and this document is about what the published surface does with that fact.*

---

## What is already established, and is not being re-derived

`SEAT_FINDING_THE_OPENING_DD_ESTIMATE_WORKS_AND_NOTHING_PUBLISHED_CAN_SEE_IT_2026-09-03.md` §3
established empirically, on one seed's 10,906 issued bills, that
`final − starting − total_net = 6.2e-05` — float rounding. Three modules state the same thing in
prose, and one of them runs a control on it:

| where | what it says |
|---|---|
| `simulation/run_phase2b.py:2618` | the producer: `treasury += rec["net_margin_gbp"]` |
| `simulation/settlement_clocks.py:243` | `reconcile_published_run_output` — **a live control** on `starting + total_net == final` against the published artefact |
| `saas/reporting/annual_report.py:964-967` | "deliberately no `banked` one … naming it 'banked' would have been a label invented for a clock this world does not have" |

The identity is not in question. What follows is.

## The contradiction I am about to act on

`tools/generate_dashboard_data.py:2344-2349` withholds a clock from `treasury_start_gbp` and
`treasury_end_gbp`, and states this reason:

> *"a treasury BALANCE, not a margin — **its clock is 'banked'**, but the banked-clock definition
> for opening/closing balances **has not been written down anywhere a reader can check**, so stating
> it here would be an assertion"*

Both halves are false as of today. The clock is not 'banked' — `annual_report.py` refuses that label
by name. And it *is* written down where a reader can check: `settlement_clocks.py` publishes a
control on the identity. So the register withholds a label for a reason that has been discharged
elsewhere, and nothing in the repository can notice — the VAT-rule class named in `CLAUDE.md`.

## The predictions

Each is falsifiable, each names the artefact that grades it, and none of them has been run.

**T1 — the repair is available.** `treasury_end_gbp` can be given a real basis entry
(`clock: "settled"`, `derived_from: "net_margin_gbp"`) that is *true of this book*, because
`treasury_end` moves only when settled net margin moves. Graded by: the identity holding on the real
published portfolio to within `CLOCK_TOLERANCE_GBP`.

**T2 — `treasury_start_gbp` is NOT repairable the same way, and must stay declared.** It is a run
input at t0, not a settled figure; nothing settled to produce it. Predicted outcome: it keeps a
declaration, with the false reason replaced by the true one. If I find myself giving it a clock, T2
is refuted and I have invented a label.

**T3 — the register cannot shrink without a red, and this is the sharper finding.**
`tests/tools/test_generate_dashboard_data_basis_subject_set.py::test_the_superseded_allowlist_was_blind_to_five_live_figures`
asserts `set(unseen_by_old_rule) == set(_BASIS_DECLARED_UNLABELLED)` — an equality against **today's
answer**, not against the property. Its own docstring says the pin exists so "a future pass can see
the debt shrink". I predict that removing exactly one key from the register turns that test RED, and
that the red is *procedural and inverted*: the control fires because the code became **more** honest.
This is R15's "control pinned to today's answer" — `CLAUDE.md`: *"goes red when the code becomes more
honest and stays green when the claim rots. That is exactly backwards."*

**T4 — that is the ONLY test that reds.** Predicted: `_check_basis_labels_present` still returns
`True`; `test_the_real_published_portfolio_passes_the_derived_gate`,
`test_no_figure_is_declared_unlabelled_once_it_has_a_real_basis_entry`,
`test_every_published_money_or_carbon_figure_is_either_labelled_or_declared` and
`test_the_declared_debt_is_printed_not_swallowed` all stay green. If a second test reds I have
misread the register's wiring, and I will say so here rather than adjust the prediction.

**T5 — the re-keyed control must be able to fail in BOTH directions.** After re-keying T3's
assertion to the property, I predict it stays green for the repair (debt 5 → 4) **and** reds if a
figure escapes both the basis block and the register — the thing the equality was actually for.
Graded by mutation, not by reading: I will delete a key from both sides and require a red.

## What must NOT happen

* No figure acquires a clock that is not true of this book. A wrong label is worse than a
  declaration, which is the register's entire premise.
* `treasury_start_gbp` does not get a 'banked' clock, or any invented one.
* The re-keyed T3 assertion does not become a tautology — an assertion that can only pass is the
  failure mode I am removing, not one to replace it with.

*Graded in the finding filed beside this document. Predictions stay as written, beside their
results, whether or not they held.*
