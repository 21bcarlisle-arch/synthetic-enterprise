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
