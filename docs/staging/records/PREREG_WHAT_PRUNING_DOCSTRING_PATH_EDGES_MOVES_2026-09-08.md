**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** no_caller_and_never_runs

# Pre-registration: what does pruning docstring path edges move?

**Filed:** 2026-09-08, delivery seat, isolated worktree, base `656a45f54` (== `origin/main`)
**Claim:** `prune-docstring-path-edges-and-freeze-the-128-in-one-commit`
**Result:** `SEAT_FINDING_A_DOCSTRING_PATH_STOPS_BEING_AN_EDGE_AND_THE_PROSE_HOLDING_SEVENTEEN_MODULES_UP_WAS_PROSE_DENYING_THEM_2026-09-08.md`

Written BEFORE the measurement. Nothing below is known.

## What is being changed

`tools/capability_index._path_references` stopped counting a repo-relative `.py` path written in a
`#` COMMENT as a reachability edge at `2e4fa042a`. A path written in a DOCSTRING is still an edge.
Same class, same defect: citing a module as the provenance of a finding — the habit `CLAUDE.md`
asks for — silently satisfies the control that asks whether anything RUNS it, so an editorial
reword refuses every lane in the tree.

## Premise re-measurement (done, before any work)

- `2e4fa042a` IS an ancestor of `origin/main`. The item said so and it is still true.
- The docstring half is **NOT** done: `_path_references` unions only `_comment_spans`, and its own
  docstring says at line 610 "A docstring path is still counted an edge."
- **One clause of the drawn item is SPENT.** The item says to "delete its held row from
  `docs/design/orphan_baseline.json`". That row is already gone, and not by anyone's judgement:

  | commit | orphans | epg row | `_doc` |
  |---|---|---|---|
  | `2e4fa042a` | 408 | present | HELD note |
  | `0388be7c1` | 409 | present | HELD note |
  | `0b3efd0a7` | 408 | **gone** | **canned** |
  | `656a45f54` (HEAD) | 407 | gone | canned |

  `freeze()` writes a literal `_doc` and `state["orphans"]` — it has no channel for a row held past
  its computed reachability. The hold that `2e4fa042a` placed, with its reason and its delete-me
  condition, could not survive the next `freeze()` and did not. This gets its own finding.

## Predictions

Recorded before running anything. They stay here whether or not they survive.

1. **P1 — floor.** Pruning docstring paths as well as comment paths moves the orphan set
   407 → 535 (the item's figure, measured in this tree on 2026-09-08 by whoever wrote the item).
   I predict I reproduce it to within ±3 modules on base `656a45f54`.
2. **P2 — epg.** `company.regulatory.epg_reconciliation_register` is among the newly orphaned.
   (Near-certain: its only edges are the two docstrings named in the item. Recorded so the
   measurement can still refute it.)
3. **P3 — the real cost is the register, not the floor.** `docs/design/ORPHAN_DISPOSITION_REGISTER.md`
   must rule on EVERY `company.`/`saas.` orphan or
   `test_the_live_register_rules_on_every_live_orphan` goes red and wedges every lane. I predict
   **30–60** of the ~128 newly orphaned modules are company/saas-side and need a fresh ruling —
   i.e. the majority of the 128 are `tools.`/`background.`/`simulation.`, governed elsewhere.
4. **P4 — no real invocation is lost.** As at `2e4fa042a`, I predict every pruned docstring edge is
   a provenance citation, not a call, and that reading them refutes none of the above. If any pruned
   edge IS a live `subprocess`/`exec` route, that module keeps its edge and the prediction is
   recorded as wrong here.
5. **P5 — the fallback.** A file that does not parse keeps its docstring edges (strictly narrower,
   same rule as comments): manufacturing an orphan out of a parse error would refuse a lane for a
   defect that has its own finding. I predict 0 unparseable files in this tree, so this leg needs a
   synthetic control and cannot be evidenced by the live measurement.

## Outcomes, written after — the predictions above are UNEDITED

| | Outcome |
|---|---|
| P1 | **HELD.** 407 → 535 exactly; +128, −0 |
| P2 | **HELD** |
| P3 | **WRONG.** 17, not 30–60 — and wrong for a definitional reason, below |
| P4 | **HELD.** All 197 pruned edges read; every one a citation |
| P5 | **HELD.** 0 unparseable; the leg is a synthetic control as predicted |

**P3 differenced a concept before defining it**, which is this project's most expensive recurring
shape and I walked straight into it. There are two orphan populations and I wrote one number
across both:

- `orphan_ratchet.compute` — unreachable from the committed SCHEDULE, transitively. 407 → 535, of
  which **60 arrivals are company/saas-side**. That is the number P3 named, and it is a real number.
- `capability_index.orphans` — no importer and no command. **This** is what the disposition register
  rules on, and what "needs a fresh ruling" means. 240 → 257: **17 rulings.**

`company.billing.consumption` separates them: `company.portal.app` imports it, so it is `wired` to
the index and needs no ruling — but the portal is itself unreachable from any entrypoint, so it is
an orphan to the ratchet. P3's band bracketed a true quantity that was not the one it asked about.

Full write-up:
`SEAT_FINDING_A_DOCSTRING_PATH_STOPS_BEING_AN_EDGE_AND_THE_PROSE_HOLDING_SEVENTEEN_MODULES_UP_WAS_PROSE_DENYING_THEM_2026-09-08.md`.

## What done means

No exit test was written for this — it is direction. Done is:

1. `_path_references` does not count a path inside a module/class/function docstring as an edge,
   and DOES still count one inside an ordinary string literal (a `subprocess` argument is a real
   route; only prose is not).
2. The floor is re-frozen **in the same commit**, from this clean base. Pruning without freezing
   refuses every lane; freezing without pruning records something untrue.
3. Every newly orphaned `company.`/`saas.` module carries a disposition ruling, including a fresh
   one for `epg_reconciliation_register` — whose two holders are docstrings that themselves state
   it has no production caller.
4. Controls are a PARTITION, not a leg per branch: a rule that pruned every string literal would
   pass "a docstring path is not an edge" and take the whole subprocess edge model with it.

## Refutation test, promised now

Read the pruned edges. If any one of them is a real invocation rather than a citation, the prune is
wrong for that file and the finding says so beside this prediction.
