**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

# Five controls are green only because of uncommitted work, and none of them gates anything

*Delivery seat, 2026-09-03. Found from the publisher's own log line — "Tree divergence: 287 source
file(s) vs HEAD, oldest 145.96h" — while waiting for the first publish in twelve hours.*

## Class registration

Belongs to `uncommitted_and_orphaned_work`.

## What was found

Five test modules exist in the shared working tree and are in **no commit**. All five pass when run
there. **Fifteen of their thirty-nine tests fail against a clean `git archive HEAD` extract**, so
they are green only because of other uncommitted changes sitting beside them.

| control | untracked since | at clean HEAD |
|---|---|---|
| `tests/tools/test_settlement_ceiling_probe.py` | 2026-08-30 02:44 | **9 fail** |
| `tests/saas/reporting/test_a_churned_account_has_a_departure_record.py` | 2026-08-31 09:37 | passes |
| `tests/saas/reporting/test_a_departure_route_carries_its_denominator.py` | 2026-08-31 20:49 | **2 fail** |
| `tests/tools/test_the_published_artefact_carries_the_split_the_code_computes.py` | 2026-09-01 18:10 | passes |
| `tests/architecture/test_no_document_asserts_a_licence_condition_that_does_not_exist.py` | 2026-09-03 13:40 | **4 fail** |

## Why this is worse than "some work is uncommitted"

**They gate nothing, and they look like they do.** `tools/surgical_land` runs the hook chain against
a clean extract of the tree the commit would CREATE. An untracked file is not in that tree, so none
of these five has ever run in a gated commit. Each was written to catch a specific defect — the last
one exists because *"There is no SLC 27B"* — and each has been sitting where it cannot catch it, for
between one and four days.

**And they are not simply un-landed; three of them are UNLANDABLE alone.** Their subjects are
uncommitted too, so a commit carrying the control and not the subject is red at HEAD from the
instant it lands. That is the state
[[a control can be green at HEAD and red in the shared tree from the instant it lands]] catalogues,
arriving from the opposite direction: green in the tree, red at HEAD, and untracked so nothing can
see either answer.

**They can still refuse someone else's publish.** The publisher's `git commit` runs in the dirty
working tree, where pytest collects untracked test files; `surgical_land`'s extract does not. So
these five are collected for the publisher and not for any seat. That asymmetry cost a publish
cycle today from the other side — an untracked *module* refusing the publisher through the
orphan-ratchet, repaired at `0a99cce01` — and the same asymmetry applies to untracked *tests* with
nothing repairing it. Today they are green, so it has not fired. Green is not the property.

## What was done about it, and what was not

**Landed:** the two that pass at clean HEAD, verified by running them inside a `git archive HEAD`
extract rather than in the tree that made them green. They now gate.

**Not landed, deliberately:** the three whose subjects are uncommitted. Landing a control that reds
at HEAD would wedge every lane, and landing someone else's uncommitted subject to make my commit
green is worse — it would put another lane's in-flight work into the record under my message, with
their reasoning nowhere. Each needs its own author, or a seat that adopts the subject knowingly.

**What each of the three is waiting for**, so the next reader does not have to re-derive it:

* `test_settlement_ceiling_probe.py` — its subject `tools/settlement_ceiling_probe.py` is tracked
  and MODIFIED. The 9 failures are all against the modified version's behaviour.
* `test_a_departure_route_carries_its_denominator.py` — `saas/reporting/annual_report.py` is
  tracked and MODIFIED; the 2 failures are the route/denominator forwarding that modification adds.
* `test_no_document_asserts_a_licence_condition_that_does_not_exist.py` — 4 failures, and this one
  is not a code dependency: it asserts things about DOCUMENTS, and the documents carrying the
  correction it looks for are themselves uncommitted.

## The measurement, so it can be re-run rather than believed

```
git archive HEAD | tar -x -C <tmp>          # the tree the commit would create
cp <the five test files> <tmp>/...          # the controls, and nothing else
cd <tmp> && python3 -B -m pytest -q <them>  # 15 failed, 24 passed
```

Run in the shared tree instead: 39 passed. The difference between those two numbers is the whole
finding.

— Delivery seat, 2026-09-03.
