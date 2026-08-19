# [WORKER-FINDING] A gap row is attributed to any writer whose text merely names it, and that suppressed the alarm on a tool that had never landed (2026-08-19)

**Severity:** BLOCKING · **Lane:** H_harness · **Disposition:** REPAIRED 2026-08-19 (the CLASS, not the instance — attribution is now an AST write-site resolution)

**Discharged:** `tests/background/test_gap_ledger_reconciler.py::test_a_writer_that_only_MENTIONS_another_row_in_a_comment_is_not_its_producer`,
`tests/background/test_gap_ledger_reconciler.py::test_a_writer_that_WRITES_a_key_it_never_SPELLS_is_still_its_producer`,
`tests/background/test_gap_ledger_reconciler.py::test_a_row_is_never_attributed_to_a_module_that_merely_READS_or_DOCUMENTS_it`,
`tests/background/test_gap_ledger_reconciler.py::test_a_DELEGATED_write_attributes_the_caller_that_never_names_the_ids`,
`tests/background/test_gap_ledger_reconciler.py::test_an_UNRESOLVABLE_write_site_is_reported_and_never_silently_empty`,
`tests/background/test_gap_ledger_reconciler.py::test_the_live_writer_family_has_no_unresolvable_write_site`,
`tests/background/test_gap_ledger_reconciler.py::test_a_marker_matched_on_PROSE_ALONE_produces_nothing`

**Found:** 2026-08-19 worker tick, LANE 1 BUILD draw on `EP1_clv_three_horizon` (pass 12), while
landing pass 11's uncommitted producer and checking what the reconciler would say about it.
**Subject:** `background/gap_ledger_reconciler.py` — `producers_for`, and the `never_landed`
branch that depends on it.
**Measured at:** HEAD `c728642c3`, working tree, by executing the shipped functions. Everything
below is `observed-with-evidence` unless labelled `inferred` (R9).

## The defect

`producers_for(atom_id, writers)` returns every writer `path` whose **whole file text contains
the atom id as a substring** — comments and docstrings included:

```python
return sorted(path for path, text in writers.items() if atom_id and atom_id in text)
```

The module holds the correct doctrine one layer up and does not apply it here.
`_WRITE_MARKER`'s own comment says, verbatim:

> A WRITE, not a mention. `background/coupled_triad.py` names half these atoms in its coupling
> table and `tools/generate_premise_demand_data.py` reads the ledger for the site — neither
> produces a row, and attributing a row to its reader would make staleness meaningless.

That rule decides **which files are writers at all**. It is never applied to deciding **which
row a writer produced**. So inside the writer set, attribution is by mention.

## The consequence, measured on the live tree — it is not cosmetic

`tools/couple_clv.py` (pass 11's producer, on disk, in no commit) carried one comment citing a
naming precedent: `` `WORLD_recontracting_relationship_start` ``. Nothing else in the file
touches that atom; it writes exactly one row, `EP1_clv_three_horizon`.

**Before** rewording that comment, executing `reconcile()`:

```
WORLD_recontracting_relationship_start  producers = ['tools/couple_clv.py',
                                                     'tools/couple_contact.py',
                                                     'tools/couple_supply_start.py']
status = stale — "2 commit(s) touched tools/couple_clv.py, tools/couple_contact.py,
                  tools/couple_supply_start.py since 15125f388"
never_landed items: NONE
```

**After** rewording the same comment, nothing else changed:

```
WORLD_recontracting_relationship_start  producers = ['tools/couple_contact.py',
                                                     'tools/couple_supply_start.py']
never_landed: {'item': 'tools/couple_clv.py', 'kind': 'tool',
               'detail': 'family gap tool whose output appears in no ledger row'}
```

Two distinct failures, from one comment:

1. **A false producer, forward-looking.** Once `tools/couple_clv.py` is committed, every future
   commit touching it marks the recontracting row `stale` — a file that has never computed that
   number would keep declaring the number out of date. `commits_since` hid this until now only
   because the path did not exist at HEAD, so `git log HEAD -- <path>` returned nothing for it.
   That is a fail-open that **ends the moment the file lands**.
2. **The alarm suppressed itself, on its own subject.** `never_landed` is defined as "family gap
   tool whose output appears in no ledger row". `tools/couple_clv.py` was exactly that — its row
   is in no commit — and the alarm did not fire, because a comment made it look like a producer
   of a row that *had* landed. The tool the control exists to catch was invisible to it for the
   one reason the control's own doctrine already names.

`inferred`: nothing else in the current writer set is mis-attributed this way. Census over
`tools/*.py` + `background/*.py` for the two ids involved found `EP1_clv_three_horizon` in one
file and `WORLD_recontracting_relationship_start` in four, of which the reconciler's own module
is not a writer. A full N×M census of every ledger key against every writer's text has **not**
been run and is the first thing the repair should do — the population of this defect is unknown,
not zero.

## Why BLOCKING and not LATENT

`background/finding_severity.py` clause 2: a finding that a control or instrument in an area is
untrustworthy is BLOCKING by construction, and down-classifying to keep one's own lane open is
the anti-pattern that module names in its own header. This is a control that failed to fire on
its own named defect while reporting a clean sweep — the R15 FAIL-SILENT pattern, in a control
whose whole job is to notice unlanded measurement. I am the lane it holds.

## What was NOT done, deliberately (R10, SELF_INTERRUPT_DISCIPLINE)

I reworded the comment in `tools/couple_clv.py`, which is inside this atom's `file_scope`, so
that landing pass 11 does not durably install a false producer. **That fixes one instance and
closes nothing.** R10 forbids closing an absurdity-class defect with an instance fix, and the
instance fix here is worse than most: it amounts to "do not spell another atom's id in a
comment", which is an exhortation, is unenforced, and is exactly the prose-only shape
MAKE_IT_STICK says will evaporate. The comment now states that reasoning in place so the next
reader does not mistake it for a style choice.

## The repair, recommended (NEVER_ASK_WITHOUT_RECOMMENDING)

Attribute a row to a writer by a **write site naming the key**, not by the file containing the
string: resolve each writer's `LEDGER_KEY`-style module constants and its literal arguments to
`write_gap_entry(...)` / `--write-ledger` invocations (AST, not text — the same bindings-not-text
discipline `unregistered_clv_modules` already uses one module away), and treat a bare textual
mention as evidence of nothing.

R15 shape for it, both directions, so the repair is not itself theatre:

* a writer that MENTIONS a key in a comment only → must NOT appear in that key's producer set
  (the mutation above, which today's code fails);
* a writer that WRITES a key it does not spell in prose → must still appear (the null control:
  move the sample, not the law — otherwise "match nothing" passes the first test);
* the `never_landed` sweep re-run over the whole family with the corrected attribution, because
  its current all-clear is only as good as the attribution beneath it, and one suppression has
  already been observed.

---

## THE REPAIR, and what it measured (2026-08-19, same day, worker tick RUNG 1c)

Built as recommended: `background/gap_ledger_reconciler.py` resolves an atom id to a writer by
**reachability from a write site** — a literal argument to `write_gap_entry` /
`write_fabric_gap_entries`, or a module-level constant that flows into one — through this file's
own bindings, through `from M import NAME`, and through `alias.NAME`. Bindings, never text.

**THE POPULATION WAS NOT ONE, AND IT WAS NOT ONLY FALSE POSITIVES.** This document said the
population was "unknown, not zero" and that a full census was the first thing the repair should
do. It was run, over all 19 discovered writers × 14 live ledger rows at HEAD `c728642c3`. Four
rows' producer sets were wrong, in BOTH directions:

| row | attributed by text | attributed by write site |
|---|---|---|
| `W1_5_premise_demand_shape` | + `background/fabric_gap_ledger.py` | — (a sentence about L3) |
| `W2_9_segment_debt_tnc` | + `background/gap_metric.py` | — (a worked example in a docstring) |
| `W2_11_payment_behaviour_source` | + `background/live_ledger_guard.py` | + `background/live_payment_triad.py` |
| `WORLD_recontracting_relationship_start` | + `tools/couple_contact.py` | — (the comment this finding was filed on) |

The third row is the one this document did not predict and is the more dangerous half.
`background/live_payment_triad.py` **is** a real producer — it calls `write_gap_entry` with
`WORLD_ATOM_ID` imported from `tools.couple_w2_11_d5` — and its text never spells
`W2_11_payment_behaviour_source` anywhere. So the substring rule was **fail-open on a real
producer**: eight commits to the live triad could not mark the row it writes as stale, while the
row was attributed to a module that only reads it. The defect was never only over-attribution.

**A SECOND SUPPRESSED ALARM, of the same shape as the one this finding was filed for.** Re-running
the `never_landed` sweep with the corrected attribution — the third thing this document asked for
— fires on **two** tools, not one:

* `tools/couple_clv.py` — the subject of this finding, still in no commit at the time of writing.
* `tools/couple_contact.py` — **new**. It writes `WORLD_contact_propensity_response`, which is in
  the ledger neither at HEAD nor on disk. It has never landed a row. The alarm was suppressed by
  its own line 59, a comment naming `WORLD_recontracting_relationship_start` as a precedent — the
  identical mechanism, on a different file, undetected for as long as that comment has existed.

**THE FAIL DIRECTION REVERSED, so the repair carries its own fail-closed half.** Under a substring
rule a missed producer was impossible; under resolution it is the live risk, and it is silent (a
row with no producer reads fresh forever). `unresolved_write_sites` therefore reports any write
site whose id cannot be read, `reconcile` emits it as `attribution_unresolved` drift, and a
SyntaxError counts as unresolved rather than as an empty set. Empty across the live family today.

**R15, five mutations, each on a named defect, all RED on the shipped mutant and restored
byte-identical:** the substring rule reinstated reds the three attribution tests; disabling
delegation reds the `couple_fabric` test (one level of delegation is resolved on purpose — the
caller's write site names none of the ids, and dropping it would be the new fail-open); swallowing
unresolved sites reds the fail-closed test. Null control, in this document's own words: a writer
that WRITES a key it never spells must still appear — that is the live `live_payment_triad` case
above, and it is why "match nothing" does not pass.

**Found in passing, and worth its own line:** three writer fixtures in the test file were not
valid Python (a dangling `if` block, a half-written call). A substring rule never parsed them, so
they had stood as stand-ins for writers while being unparseable. They are real modules now.

60 tests green in the file. Prior behaviour on the ratchet is unchanged: `background/gap_metric.py`
and `background/live_ledger_guard.py` are still discovered as writers (they quote `--write-ledger`
in help text) and now correctly produce nothing, which is asserted rather than left implicit.
