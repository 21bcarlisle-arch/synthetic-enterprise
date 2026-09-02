**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `unminted`

# FINDING — the working tree holds the PARENT of the VAT fix, is armed to silently revert it, and is wedging every lane's constant-origin gate right now

**Found 2026-09-02, delivery seat, Lane 0, while landing the level-anchor collision decision.** Not
my pathspec and not my item. Found by following a red I had to attribute before I could land:
`tests/architecture/test_a_domain_constant_carries_its_origin.py::test_no_domain_constant_NAME_carries_two_values`
fails in the shared tree and passes at clean HEAD, so something uncommitted was causing it.

## Measured, not inferred

```
$ git log --oneline -1 -- company/billing/invoice.py
2bf3ad0aa a legal rate had two homes, a discount rate had three, and the gate could only see the first kind
$ FIX=$(git log --format=%H -1 -- company/billing/invoice.py)
$ git show "$FIX^:company/billing/invoice.py" > /tmp/parent_invoice.py
$ diff -q /tmp/parent_invoice.py company/billing/invoice.py
(no output)   # IDENTICAL to the pre-fix parent
```

| | content |
|---|---|
| **HEAD** (`2bf3ad0aa`, 2026-08-31 22:19) | the fix: VAT has ONE home, the per-segment table in `saas/non_commodity.py` |
| **this working tree** | byte-identical to `2bf3ad0aa^` — `VAT_RATE = 0.05  # 5% VAT on domestic energy (UK reduced rate)` |

The tree copy's mtime is **2026-08-31 18:20:56**, four hours *before* the fix commit. So the fix was
made in a sibling worktree, HEAD moved under this checkout, and this checkout's copy was never
written. Same mechanism as the level-anchor block a day earlier — six worktrees share this object
store and HEAD moves under all of them.

## Why this one is worse than the level-anchor case

There the tree held HEAD's **successor** and the decision was real. Here the tree holds HEAD's
**predecessor**, and there is no decision to take: it is simply older. Two consequences:

1. **It is an ARMED SILENT REVERT of the canonical VAT repair.** `company/billing/invoice.py` is in
   scope for any lane touching billing. The next `git add` that includes it — including a *correct*
   pathspec commit by a lane that legitimately edits that file — reinstates
   `VAT_RATE = 0.05` with the exact comment `2bf3ad0aa` says is "true of a household and wrong of
   every business supply". **This is the VAT rule CLAUDE.md names as the project's most expensive
   recurring shape**: one legal requirement, five implementations, a defect fixed in one and live in
   another. The repair for it would be undone by an ordinary commit, silently.
2. **It is wedging every lane right now.** `test_no_domain_constant_NAME_carries_two_values` reads
   the whole tree, so any commit whose gate selection reaches that file fails on a red it did not
   cause: `VAT_RATE` at `company/billing/invoice.py:19 = 0.05` against
   `saas/non_commodity.py:101 = {'resi': 0.05, 'SME': 0.2, 'I&C': 0.2}`.

## What I did NOT do, and why

**I did not touch `company/billing/invoice.py`.** The house rule against `git checkout <path>` and
`git stash` on this shared tree is absolute, and it is right here even though this is the case where
the restore looks obviously safe: the file is byte-identical to a committed object, so *this* one
could be restored losslessly — but establishing "obviously safe" is exactly the judgement that was
wrong about the level-anchor block twenty-four hours ago, where the same reasoning would have
destroyed HEAD's successor. **The rule is worth more than this instance of being right.**

I landed my own work by `python3 -m tools.surgical_land`, which gates the tree the commit *would*
create — in which `invoice.py` is at HEAD and the red is absent — rather than the dirty shared tree.
That is the sanctioned route and it does not clear the hazard for anyone else.

## What is owed

1. **Bring `company/billing/invoice.py` to HEAD, by a lane that owns billing**, and confirm by
   digest against `git show HEAD:` rather than by reading the diff. It is a lossless restore: the
   tree content is a committed object (`2bf3ad0aa^`), verified above, so nothing is destroyed. That
   is a statement about *this* file today and must be re-established, not assumed, if it is done
   later.
2. **The shape is now twice in two days and is not an incident.** A sibling worktree landing a fix
   leaves every other checkout holding the predecessor, with no signal anywhere. The level-anchor
   case was caught because a control went red; this one was caught because a *different* control went
   red and I chased it. Both were luck. Whether that is worth a mechanism — something that compares
   each checkout's tracked files against HEAD and reports drift — or only a habit is a judgement for
   the seat, filed here rather than built here, because a control that only guards our own controls
   is usually not worth having.

---

## DISPOSITION 2026-09-02 — drawn worker, lane D_billing_metering. BOTH owed items discharged.

### Owed item 1 — `company/billing/invoice.py` brought to HEAD, and it was a PAIR, not a file

The lossless property was **re-established today, not assumed**, exactly as this finding demanded:

```
tree blob   915b2c13ea3baef3529fe68675a6960f3f6a00ca
2bf3ad0aa^  915b2c13ea3baef3529fe68675a6960f3f6a00ca   -> identical, restore destroys nothing
```

Restored by writing `git show HEAD:<path>` (never `git checkout <path>`), and the pre-restore blobs
were additionally pinned at `refs/preserved/invoice_py_pre_vat_fix_20260902` and
`refs/preserved/test_invoice_char_pre_vat_fix_20260902`. Verified after by digest against
`git show HEAD:`, not by reading the diff.

**What this finding did not know: `tests/company/billing/test_invoice_characterization.py` was in
the identical state**, byte-identical to `2bf3ad0aa^`, and it `import`s `VAT_RATE` — the symbol
`2bf3ad0aa` deleted. So the tree held a **consistent predecessor pair**, and restoring `invoice.py`
alone left the tree with an `ImportError` at collection, which under this project's own rule costs
the whole suite, not one test. Measured, not reasoned:

```
ImportError: cannot import name 'VAT_RATE' from 'company.billing.invoice'
```

Both restored together; `pytest` on the pair plus the constant-origin gate: **119 passed**. The gate
this was wedging for every lane — `test_no_domain_constant_NAME_carries_two_values` — is green.

**The generalisable bit: an armed revert has a blast radius, and it is the pair, not the file.** A
half-restore is worse than no restore. I found the sibling only because I swept the whole tree for
the class instead of fixing the named instance.

### Owed item 2 — the judgement, and the answer was NOT to build a new mechanism

`background/tree_divergence.py` already exists and **already fired on this hazard** — as 1 of 272
files, its own alarm text ending *"Report only — the publish gate's subject is HEAD, so this blocks
nothing."* A second watcher would have been the "control that only guards our own controls".

The actual defect is that **`divergence` was one count over two populations with opposite
remedies** — the CLAUDE.md *say what it is before you measure it* shape, the same failure as
*average unit rate* and *bill shock*:

| population | tree holds | remedy |
|---|---|---|
| IN PROGRESS | novel bytes | **land it** |
| ARMED REVERT | an older committed version of that path | **restore it to HEAD** |

So the existing measure was taught the split rather than a new one being built: `armed_revert_paths`
plus `armed_reverts` / `armed_revert_unproven` on the artefact, and a `breaches()` line that names
the file **and its remedy** ("restore to HEAD, do not land" — because the intuitive move, committing
it, *is* the defect). **ARMED carries no threshold**: one file is not a smaller 272, it is a
different population, and a dial there would hide the only case it exists for.

Cheap because the filter is exact about what it *excludes*: novel bytes have no blob in the object
store, so only blob-existence survivors get a history walk — **2 of 283 files on the live tree**.

Mutation-proven under `python3 -B` (all three killed): tautology → the NOT-armed leg dies;
fail-open on git failure → the refusal leg dies; a threshold on the armed branch → the no-threshold
leg dies. Pre-registration and grading, **including one refuted prediction that was my own
denominator error**, in
`WORKER_PREREGISTRATION_WHAT_SPLITTING_DIVERGENCE_INTO_ARMED_AND_IN_PROGRESS_MUST_SHOW_2026-09-02.md`.

### Not claimed, and one thing left open

`armed_reverts: 0` on the live tree is a **clean tree, not a proven catch** — I restored both armed
files before the mechanism existed. It has not yet caught a real unplanned one.

**Scope, stated rather than left to be discovered:** the measure's population excludes *generated*
artefacts, so a generated file holding an ancestor version is not named. The sweep found one —
`site/data/weather.json`, a 1-line diff regenerated by `tools/fetch_weather_data.py` on every
publish, therefore self-healing and left alone as another lane's artefact. Whether that exclusion
should hold for generated files that are **not** self-healing is a real question and is **not**
answered here.

**Archived: both owed items discharged.**
