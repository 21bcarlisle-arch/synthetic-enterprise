# PREREG — does a per-path hatch on the PREFIX refusal let the two DECLINED trees be declared?

**Written 2026-09-15 by the delivery seat, BEFORE any file under either candidate tree was opened
and before the declarations were tried.** Lane 0, claim
`a-prefix-refusal-has-no-per-path-hatch-so-two-probably-real-generated-trees-stay-undeclared`.

The frame immediately before this one declared a fourth tree, `docs/status`, and DECLINED two more
— `site/state` and `docs/reports` — for a reason its own §8 states as structural rather than
evidential:

> `WRITTEN_BUT_NOT_REPRODUCIBLE` is a per-path hatch and a PREFIX refusal has no equivalent. A tree
> holding one irreproducible record cannot be declared and then corrected, so the bar for a tree is
> *every* path under it, not most.

A bar set by a missing mechanism is the wrong reason to leave a starvation door open. This asks
whether building the missing mechanism lets the evidence decide instead.

---

## 1. The two properties this turn must NOT conflate, stated before any code is written

The item that drew this says "give `offends()` an explicit per-path EXCEPTION set **the way the two
oracles already have `WRITTEN_BUT_NOT_REPRODUCIBLE`**". Reusing that *set* would be wrong, and I am
writing down why before I am tempted by how tidy it would be:

| | `WRITTEN_BUT_NOT_REPRODUCIBLE` | what `offends()` needs |
|---|---|---|
| question | does a REVERT lose content no run can recompute? | does a `file_scope` naming this STARVE its atom? |
| consumer | `origin_reconcile._split_generated`'s union | `gate_violations()`, the commit gate |
| harm of a wrong exception | a lane's real work is reverted | an atom starves invisibly — the G13 defect |

They are not merely different, on the decisive case they are **opposite**. An accumulated ledger
like `site/state/live_decisions_log.jsonl` is irreproducible *because* every run rewrites it — which
makes it maximally dirty, which makes it maximally starving. Excepting it from `offends()` would be
a fail-open in the exact shape this gate exists to close.

So the new set is a different set with a different predicate: **a path under a declared generated
tree that NO RUN REWRITES** — an authored document living inside a generator's tree. That is the
only shape for which the prefix is wrong and the property is satisfiable.

## 2. Questions, with the answers I do not have

**Q1.** Declaring `("site", "state")` adds **0** live `file_scope` violations.
**Q2.** Declaring `("docs", "reports")` adds **0** live `file_scope` violations.
*(Both inherited from the preceding finding's §8, which reports 0 live violations for each. Restated
here as predictions because that count was taken against the map as it stood then, and the map is
written by other lanes.)*

**Q3.** The two declarations together move the union
(`generated_artefacts() | written_artefacts()`, today 246) by **+1 to +15**. The write-keyed oracle
already holds 8 paths under `site/state` and 9 under `docs/reports`, so the union can only gain what
the tree-keyed segment/whole-string match finds and the write scan missed.

**Q4.** At least one tracked file under `docs/reports` is AUTHORED and needs the new exception —
named in advance: `docs/reports/REPORTING_BACKLOG.md`.

**Q5.** `site/state` contains **NO** authored file, so it needs no member of the new exception set
at all; its only per-path need is `live_decisions_log.jsonl` in `WRITTEN_BUT_NOT_REPRODUCIBLE`,
which already exists. If Q5 holds, the mechanism this turn builds is load-bearing for exactly one of
the two trees, and saying so is part of the deliverable.

**Q6 — THE CALIBRATION, the one I most expect to be wrong.** The new exception set has at least one
member that changes `violations()` on the live map today — i.e. some atom's `file_scope` really does
name an authored path under one of the new prefixes. **I predict FALSE.** Q1 and Q2 predict zero
violations under either tree, and a set whose members no live declaration reaches cannot move
`violations()`.

## 3. The stopping rule, written before the answer

If Q6 is FALSE — which I expect — then the exception set is **machinery no live tree state
exercises**, and the honest reading is the one the write-keyed oracle's own docstring already made
about the `self._write(...)` frame: *"machinery no tree state can exercise, so it is not built; the
measurement is the deliverable."*

I am not going to route around that, so the rule is stated now rather than chosen later:

- The exception set ships **only if** it carries a control that can fail on tree state — a
  STALENESS test that goes red when a member becomes write-reached, the mirror of
  `test_the_not_reproducible_carve_out_is_load_bearing`. That control is exercised by the live tree
  every run, whatever `violations()` says.
- A member is admitted **only** on positive evidence of authorship, per file: no write site anywhere
  in the scanned trees, and the document saying so in its own words. "It has no generation stamp" is
  absence of evidence and is not enough on its own.
- If a candidate tree needs an exception I cannot evidence, the tree is **declined again** — and
  this time for an evidential reason, which is a different and acceptable answer.

## 4. What DONE means for this item

1. `offends()` consults an explicit per-path exception set, mutation-proven — the test fails with
   the exception removed and fails again with a member that should not be there.
2. A staleness control keyed to the PROPERTY (a member that becomes write-reached is a defect), not
   to today's membership.
3. `site/state` and `docs/reports` each re-judged on evidence, declared or declined **with the
   numbers**, and the declaration landed with its re-measured `FROZEN` in the SAME commit — a freeze
   measured against a narrower prefix set reads STALE and refuses every lane.
4. Every prediction above scored in the finding, including the ones that fail.
