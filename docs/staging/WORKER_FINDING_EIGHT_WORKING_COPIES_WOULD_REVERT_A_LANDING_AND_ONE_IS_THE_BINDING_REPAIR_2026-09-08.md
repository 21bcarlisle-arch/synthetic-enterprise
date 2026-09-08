**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Eight working copies in the shared tree would revert a landed commit, and one of them is the binding repair — again

**Filed 2026-09-08 by the delivery seat (lane 0), from the census run by
`tools/stale_copy_refusal.py --census`, which is the guard this finding also arms.**

## What was measured

Of 59 code paths that differ from HEAD in `/home/rich/synthetic-enterprise`, **eight contain not one
of the distinctive lines the last commit to that path added.** Those copies were taken before that
commit landed. Any lane that names one of these paths in a pathspec commit deletes the landed work,
and every gate downstream is green on it, because the tree it reverts to was valid an hour ago.

| path | last landing | distinctive lines, none present |
|---|---|---|
| `tests/tools/test_commit_refusal_attribution.py` | `680141f67` | 146 |
| `tests/tools/test_r1_inference_ceiling.py` | `d7b2a35d4` | 108 |
| `tests/tools/test_dd_opening_arms.py` | `6b491420d` | 44 |
| `background/self_clearing_alarm_census.py` | `fc950dda6` | 37 |
| `site/harness/index.html` | `fe79a5dd9` | 13 |
| **`tools/promote_worktree_landing.py`** | `b06fa3528` | **14** |
| `site/test_harness_delivery_record.py` | `2a61d1a61` | 11 |
| `simulation/policy_costs.py` | `29b4dcd3b` | 5 |

## Why this one is BLOCKING and not a tidy-up

**`tools/promote_worktree_landing.py` is missing all fourteen lines of `_bind_to_claim`.** That is
the function that binds a landing's paths to the drawing lane's claim — the repair whose *first*
deletion is the banked finding `A_REWRITE_DELETED_THE_BINDING_REPAIR`. The identical deletion is
sitting in the shared tree right now, one pathspec commit away from happening a second time, by
exactly the mechanism the first finding named. Nothing in the repo could see it: the reverted file
parses, its imports resolve, and `tools/symbol_landing_check.py` is green on it **by construction**
(a stale copy is internally consistent — the symbol and its callers revert together, so every
reference resolves).

Two of the others are not harness plumbing either:

- **`simulation/policy_costs.py`** would delete the 2026 and 2027 CCL and OY levy rates, each
  carrying its gov.uk citation in the same line (`2027: 8.27,  # gov.uk CCL rates, 'Rate from 1
  April 2027'`). That is sourced domain evidence, and reverting it puts the model back on a
  silently shorter rate table.
- **`site/harness/index.html`** would delete a 13-line comment block whose whole content is *why
  the frontier's rows must never be rendered as the sharing side* — "at zero pass-through nothing
  moves, so nothing is created… that row alone would publish value TRANSFERRED as value created."
  A future reader without that comment re-adds the row. The page loses **no** id and **no**
  function, so a symbol-level guard passes it while looking checked.

## What was already tried, and why it did not work

The lane-0 direction prescribed a hand sweep for this class last orientation. It moved the count
from 24 to 16 and the population then took on a member 32 hours deep — a sweep does not converge
against lanes that keep opening files.

The direction then prescribed a *refusal* keyed to **strict symbol subset**: refuse when the
worktree copy's symbol set is a strict subset of `git show HEAD:<path>`'s. **Measured, that rule
fires on zero of these eight** — pre-registered before the run and refuted by it
(`PREREG_THE_STALE_COPY_CENSUS_IS_A_DIFFERENT_QUESTION_FROM_THE_MTIME_CENSUS_2026-09-08.md`). The
cause is worth keeping: `surgical_land` never writes the working tree — deliberately, and that is
what makes it safe for a two-lane file — so a landed commit leaves other lanes' copies stale while
their symbol sets remain **supersets** of HEAD. Their own additions are still there; only the other
lane's are missing. A symbol-set rule cannot see a landing it never received.

## What is now in place

`tools/stale_copy_refusal.py`, wired into `tools/surgical_land.py` **before the extract** (the
refusal is about the tree, not the tests, and no amount of running the suite can find this). It
refuses a path when the copy the commit would land contains **not one** of the distinctive lines the
last commit to that path added — qualitative, no threshold. `--drops <path>` declares a deletion as
deliberate and is printed on the landing, because an exemption nobody can see is a hole.

It **narrows** rather than closes the class: a lane that has already pulled the landing and then
rewrites over it is invisible to both rules. That is stated in the module's docstring.

## What is next, and it is not this guard

The guard stops the *ninth* one. It does not repair the eight, and it cannot: only the lane holding
each copy knows which hunks are theirs. Two of the eight are mine to route, six are not.

1. **`tools/promote_worktree_landing.py` first**, ahead of everything, because it is the one that
   silently breaks the record of what every other lane landed. `tools/isolate_hunks.py --survey`
   then `surgical_land --content` lands the holder's hunks over HEAD without reading the file.
2. The remaining seven, same route. `python3 -m tools.stale_copy_refusal --census
   --root /home/rich/synthetic-enterprise` regenerates this table; it is the check, not this
   document.
3. **The guard has never fired in production** — it was landed from a clean isolated worktree with
   nothing stale to refuse. Its reachability is proven by a poison round in
   `tests/tools/test_stale_copy_refusal.py`, not by a live refusal. The first live refusal is worth
   reading rather than assuming: a false positive here wedges the ONE legal landing door, which is
   the pressure toward bypass that `surgical_land` exists to remove.
