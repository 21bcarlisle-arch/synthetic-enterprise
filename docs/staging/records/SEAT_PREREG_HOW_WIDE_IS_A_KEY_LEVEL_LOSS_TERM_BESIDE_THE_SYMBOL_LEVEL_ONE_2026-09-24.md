**Severity:** INFO · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# PRE-REGISTRATION — how wide is a key-level loss term beside the symbol-level one?

Written **before** any of the three measurements below was run. Drawn as
`teach-the-stale-copy-reading-a-key-level-term-in-both-directions`. The finding this serves is
`SEAT_FINDING_THE_SAME_KEY_IS_NOT_A_SYMBOL_BLIND_SPOT_NOW_REFUSES_TO_CLEAN_A_REVERT_IT_ONCE_OFFERED_TO_CREATE_2026-09-24.md`
(`db1c8460e`).

## What is already established, and is therefore not measured here

Reproduced against `origin/main` at `db1c8460e`, reading the shared tree's working copy of
`saas/reporting/annual_report.py`:

* keys the copy GAINS over the base: **none**
* keys the copy DROPS: **`gas_shape_provider_by_customer`, `gas_shape_refusals`**
* `symbols()` delta both ways: **empty**
* `stale_copy_refusal.judge(...)` → **`None`** — no complaint at all

So `dict_key_gains` (the direction fixed at `19f340e65`) does not reach this copy, and the door's
"it deletes no name" is false of the artefact while true of symbols. That is the open half.

## The design being priced

One key-level term beside `symbols()`/`gains_over()`, answering **both** directions from one
population, so the two cannot drift. The DROP direction becomes a `Loss` in `judge` — the key-level
parallel of rule 2 (`SUBSET`) — and the GAIN direction keeps feeding `refresh_to_head`'s existing
`WHITELIST_GAIN`. No new state for dict keys alone.

Two open questions decide the shape, and both are counts, not arguments.

## Q1 — unconditional or clock-gated?

Rule 2 (`SUBSET`) refuses a strict symbol subset at any age, with `--drops` as the declared
escape. The key-level parallel would refuse a **strict key subset** (drops ≥1, gains 0) at any age.
`violations()` is the landing gate, so this prices real commits, not working copies.

**Measurement.** Over the last 200 commits of `origin/main`, for every changed `.py` path, compare
parent blob to result blob. Count the (commit, path) pairs the strict-key-subset leg would newly
refuse — newly meaning `judge` returns `None` today.

**Prediction: 1.5%–6% of changed `.py` path/commit pairs, and under 40 pairs absolute.**

**Decision rule, fixed now:** ≤ 5% → ship it unconditional, parallel to `SUBSET`. > 5% → gate it on
`taken_before` like rule 1b, and print the number as the reason.

## Q2 — how wide is the population?

The direction says a string literal in a list, a decorator and an `__all__` entry are the same
shape as a dict key, and forbids a clause each. The cheapest honest generalisation is *string
constants in literal collection position* — dict keys plus `list`/`set`/`tuple` display elements.
That widening also re-prices the GAIN direction, whose landed blast-radius claim ("exactly ONE
verdict across the 430 dirty paths of 2026-09-24") is measured on dict keys only.

**Measurement.** Q1's count re-run with the wider population; and, over the shared tree's dirty
paths, how many additional `REFRESHABLE` verdicts the wider population would withdraw.

**Prediction: the wider population at most triples Q1's count, and withdraws 2–10 additional
`REFRESHABLE` verdicts.**

**Decision rule, fixed now:** widen if the additional withdrawals are ≤ 3. Otherwise keep the
population at dict keys and record the measured number as the reason it was not widened — the
neighbours named in the direction stay one population's business, not four clauses', either way.

## Q3 — is the drop leg reachable on the live tree by anything but the file that commissioned it?

**Measurement.** Across the shared tree's dirty tracked `.py` paths against `origin/main`, how many
copies drop a declared key the base binds and gain none.

**Prediction: 2–15, i.e. `annual_report.py` is not alone.** A count of exactly 1 would mean the term
is keyed to today's answer rather than to a property, and would be said so here.

## What would refute the whole design

A Q1 count above 15% would say a key-level subset is an ordinary shape in this repository's commits
and that refusing it is a widening wearing a control's name. In that case the leg ships clock-gated
and narrow, and this document records that the unconditional form was priced and rejected.
