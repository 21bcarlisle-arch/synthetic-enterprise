**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** measure-the-dotted-module-fail-open-in-the-path-edge-model

# The dotted-module fail-open is zero, because the launch form and the guard are the same fact

**2026-09-08. Lane 0 delivery.** Claim:
`measure-the-dotted-module-fail-open-in-the-path-edge-model`.

Changed: `tools/capability_index.py` (`_DOTTED_INVOCATION`, `_dotted_invocations`, `_prose_spans`,
row field `named_by_dotted`, integrity check 7). Controlled:
`tests/tools/test_capability_index.py` (5 tests, poison round first).

---

## What was asked

`tools/capability_index._PATH_TOKEN` matches repo-relative `.py` PATHS only, so a module launched
as `python3 -m package.module` is invisible to the reachability graph. **Measure how many modules
are reached ONLY by that form and are currently counted orphans, then decide whether to add a
dotted-name edge and re-freeze in the same commit.**

This was the last untested blindness hypothesis from `ORPHAN_DISPOSITION_REGISTER` section 1. The
docstring prune (`0a1ba2d2f`) found it in its own refutation test and did not fix it. The one
census on record — August 2026, "1 hit, a docstring example" — predates 707 commits and both
prunes, so it was re-measured rather than trusted.

## The measurement

Run over the whole working tree, then again over a clean `HEAD` extract at `b71f148bc`
(`git worktree add --detach`). **Identical both times**, which matters because a recent finding
had fourteen modules living only in the shared working tree.

```
rows 1,127   orphans 271

  production `-m` invocation, prose pruned    names  40 modules   orphans among them: 0
  test `-m` invocation, prose pruned          names  32 modules   orphans among them: 0
```

**The answer is ZERO. Not one module is held out of the orphan set by the `-m` form.**

The 40 split as follows, and the split is the finding:

```
  38  carry a `__main__` guard  ->  `_is_entrypoint` already reads them as `entrypoint`
   2  carry no guard            ->  held `wired` by ordinary importers
        background.boot_sha        5 importers   (named by background.generate_units)
        background.publish_scope   2 importers   (named by background.process_run_complete)
```

## Why it is zero, and why that is not luck

**A module worth invoking as `python3 -m x.y` is a module with an `if __name__ == "__main__"`
guard, and the guard alone already makes it an entrypoint.** The `-m` string and the guard are the
same fact seen twice — one in the caller, one in the callee — and the index was already reading the
second copy. The path-form blindness was never load-bearing because the thing it was blind to has a
witness inside the module itself.

That is a *structural* argument, so it is worth more than the count of 40. It also names its own
exception precisely: a `-m` target with **no guard and no importer**. That module would be a live
mechanism the index calls dead, and it is the only shape this blindness can actually cost anything.
It does not exist today. The two guardless targets above are one deleted import away from being it.

## The decision: record the route, do not wire it

**No dotted-name edge was added.** Three reasons, in order of weight.

**It would buy no verdict.** Every subject is already `entrypoint` or `wired`. 40 new caller edges,
0 status changes, and the orphan set — which is what the ratchet and the disposition register read —
is byte-identical. So no re-freeze of `docs/design/orphan_baseline.json` was needed or made.

**It would cost what the last two commits paid for.** The comment prune freed 34 modules and the
docstring prune a further 128, both by proving that *naming* a module is not *running* it. A dotted
module name is far easier to write in passing than a path is — every "re-take it with `python3 -m
tools.x`" comment in this repo is one — so a dotted edge model reopens that fail-open in its easiest
direction.

**The broader version was tried and refuted by its own first hit.** Before settling on `-m`, the
census was run over ANY dotted module name in a non-prose string literal — the rule that would also
catch `background.derived_artefact_register.REGISTER`, which holds module names as data and launches
them by variable. It wired exactly one orphan: `company.portal.app`, named by
`tools.company_network_isolation.KNOWN_ROUTES`. That is a **false edge** — the isolation checker
names it as the subject it AUDITS, not as something it runs. One candidate, and it was wrong.

So the route is **recorded and not wired**: `named_by_dotted` on the row, `callers` untouched.

## The control, and what it is keyed to

Integrity check 7: **a `-m` target with no `__main__` guard and no importer is a FALSE ORPHAN and
fails the index.** Keyed to the property that makes today's answer zero, not to the zero. It stays
green if the count moves from 40 to 4 or to 400, and it goes red the day the exception above is
written — which is the only day it matters.

R15 order was **poison round first**, because "the census found nothing" and "the census cannot see"
produce the same output:

| test | what it proves |
|---|---|
| `test_a_module_launched_by_dotted_name_is_recorded_and_still_reads_orphan` | the census REACHES — a real `-m` launch of a guardless, unimported module is recorded; and it is still `orphan`, so no edge was smuggled in |
| `test_check_seven_fires_on_the_false_orphan_the_dotted_form_can_manufacture` | the finding FIRES on its own named defect |
| `test_a_dotted_launch_of_an_ENTRYPOINT_is_not_a_finding` | it does NOT fire on the 38, so it is not a check that would be deleted in a week |
| `test_a_dotted_name_cited_in_PROSE_is_not_recorded` | the comment/docstring rule holds for this form too |
| `test_the_live_repos_dotted_census_is_populated_and_costs_no_orphan` | the measurement, with a vacuity floor of 10 subjects so a blinded regex cannot report calm |

The floor is the leg that matters most. Without it, deleting one character from `_DOTTED_INVOCATION`
makes "no false orphans" true of an empty set, and the control reports calm for every subject —
this project's recurring shape (a harness saying SURVIVED for everything when its own parser goes
blind).

`_prose_spans` was factored out and threaded into both readers so the tokenize pass and the `ast`
parse still happen once per source. `--check` is a 48-second path; a second rule computing its own
spans would have doubled it.

## What is still invisible, stated rather than implied

Two routes this graph genuinely cannot see, and neither is fixable by a regex:

- **`-m` with a variable module name.** `background/derived_artefact_register.py:219` runs
  `[sys.executable, "-m", art.module, "--check"]`; `tools/surgical_land.py:503` does the same. The
  names are literals in a `REGISTER` tuple, so the broader dotted-literal rule above WOULD see those
  — and that rule was rejected on the `company.portal.app` false edge. Measured cost today: no
  orphan among them.
- **A module named only in a DATA file.** `background/gap_ledger_reconciler.runners_for` builds its
  `-m` command from `producers` recorded in the gap ledger, converting a `.py` path to a dotted name
  at run time. That path never appears in any `.py` source, so neither `_PATH_TOKEN` nor this new
  rule can see it. This is a different blindness — references from `docs/**` artefacts — and it is
  not this claim's.

## What is next

Nothing is blocked on this. The hypothesis from `ORPHAN_DISPOSITION_REGISTER` section 1 is closed
with a measurement and a control instead of a paragraph, and section 1 should be updated to say so
rather than to keep listing it as untested. The data-file blindness above is the honest successor
question and is worth one census before anyone assumes it is also zero.
