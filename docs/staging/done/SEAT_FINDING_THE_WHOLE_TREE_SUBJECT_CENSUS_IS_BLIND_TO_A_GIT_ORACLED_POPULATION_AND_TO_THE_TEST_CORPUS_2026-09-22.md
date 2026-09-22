**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — the instrument, found while closing a Lane 0 item

# The census built to find guards whose subject and selector disagree cannot see two whole classes of them, and both were live

**Found** while landing the load-bearing half of
`origin-main-carries-seven-reds-that-no-commits-gate-selection-reaches`. **Not repaired here, and
the reason is in the last section — repairing it inside that commit would have made the instrument
agree with the list it grades.**

## One line

`tools/whole_tree_subject_census.py --strict-dataflow` returns **0**, and five controls with exactly
the class's defect were red at `origin/main` at the moment it said 0.

## The two blind spots, measured

**1. The population must come from a FILESYSTEM WALK.**

```python
_WALK_ATTRS = frozenset({"glob", "rglob", "iterdir"})
```

Leg 1 requires an AST-visible call to one of those. A control whose subject is the **committed
bytes** — `git ls-files`, `git grep`, `git show :<path>` — matches it not at all. That is not an
exotic shape: it is the only honest subject for "what does the RECORD claim", because the working
tree is not what a clone carries. Four of the five live members are git-oracled, and two of them
(`test_no_committed_discharge_cites_an_unlanded_falsifier`,
`test_no_committed_store_claims_an_unlanded_falsifier`) exist *specifically* to grade committed
records against the index.

**2. `tests` is excluded from `SOURCE_ROOTS`, on a reason that is false for a ratchet.**

```python
# `tests` is excluded by leg 1: a test whose subject is other tests is reached by staging those
# tests, which the stem selector does handle (a changed test file selects itself).
```

That is true of a test's **own assertions** and false of a **ratchet over the corpus**. Staging
`tests/sim/test_scenario_spine_consumption.py` selects that file; it does not select the repo-wide
ratchet that file just joined. The two are different files.

**The cost of record, measured not predicted.** `test_no_tree_scan_passes_on_an_empty_population`'s
subject is every tracked `tests/**/test_*.py`. **Five** test functions matching `ast.walk` accumulated
in the tree while it was red at `origin/main`, and every commit that added one was green. That is the
exclusion's price, paid.

## Why this is BLOCKING rather than RECORDED

The census is not a report — it is load-bearing. `tools/pre_commit_test_gate.py` states, beside
`CENSUSED_WHOLE_DIRECTORY_SUBJECTS`:

> MEMBERSHIP IS RE-DERIVABLE … `--strict-dataflow` returns exactly this batch, from a predicate
> pre-registered BEFORE the first count was run. Adding a line here DISCHARGES that member … so the
> strict count reads 0 once this lands and a nineteenth instance shows up as a **1** rather than as
> silence.

And `test_the_strict_census_stays_discharged` converts that 0 into a commit-time refusal. So the
claim the repository actually rests on is: *a new whole-tree-subject control landing with a stem-only
selector is refused at the commit that writes it.* **That claim is false for any such control whose
population comes from git, and for any ratchet over the test corpus** — it lands, green, and shows up
as silence, which is what happened five times over.

This is R15's FAIL-SILENT killer one level up from where the catalogue usually finds it: not a
control that cannot fail, but a **census whose emptiness is read as absence** when it is scope.

## What is NOT claimed, and it is the important part

**I have not measured the population.** Five members are known because they were red simultaneously
and I read the failures; that is five instances, not a census. The strict count is 0 today and the
honest reading of that 0 is "this predicate found nothing", not "there is nothing".

Nor is the direction of the fix obvious, and that is the second reason it is not done here:

- widening `_WALK_ATTRS` to git oracles is not a vocabulary edit, it is a different **leg** — leg 2/3
  ask whether "the walk IS provably the counted population", and there is no walk to prove anything
  about when the population is a `git grep`;
- un-excluding `tests` needs the exclusion's reason **split**, not deleted: it is right for a test
  whose subject is its own file and wrong for a ratchet, and a blanket un-exclusion would pull in
  every test file in the tree.

## Why it was filed rather than fixed, stated plainly

Both repairs change **which files a PRE-REGISTERED predicate counts**. Doing that inside the commit
that adds five entries to the list the predicate discharges would make the census agree with the list
by construction — the independence half of R15's TAUTOLOGY pattern, and the exact thing the census
was built to avoid. The five entries are landed as their own named batch
(`GIT_ORACLED_AND_TEST_CORPUS_SUBJECTS`), deliberately **not** folded into
`CENSUSED_WHOLE_DIRECTORY_SUBJECTS`, so that when the predicate is widened it will either return them
— confirming this finding — or not, refuting it. The prediction is written before the measurement:

> **Pre-registered, 2026-09-22.** Widen the predicate to accept a git-derived population and to
> include `tests` for corpus-wide ratchets, and re-run `--strict-dataflow`. I predict it returns
> **more than five** — the five below plus at least two others, because "grade the committed record
> against the index" is a shape this repo reaches for often and nothing has ever been able to count
> it. If it returns exactly five, the class is closed by this landing and my "not measured" caveat
> was over-cautious. If it returns fewer than five, the widening is wrong and not the census.

## The five, for whoever takes this

    tests/architecture/test_a_commons_artefact_can_tell_when_its_source_was_revised.py   commons + docs/staging
    tests/architecture/test_a_coverage_claim_declares_what_it_reduces_over.py            tools/ + simulation/
    tests/architecture/test_no_tree_scan_passes_on_an_empty_population.py                tests/ (blind spot 2)
    tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py        docs/ + the index
    tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py           stores + the index

**What done means:** `--strict-dataflow` either returns these five (and whatever else it finds) or
names, in its own docstring, why a git-derived population is deliberately out of its scope — and if
the latter, something else has to count them, because right now nothing does.
