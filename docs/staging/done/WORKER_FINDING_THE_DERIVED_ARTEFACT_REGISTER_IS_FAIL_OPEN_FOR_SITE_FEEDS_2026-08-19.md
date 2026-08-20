# [WORKER FINDING] The derived-artefact register cannot see a site feed, so the subclass a director instruction claimed this would delete was never enumerated (2026-08-19)

**Severity:** LATENT · **Lane:** H_harness

**Found during:** `G13_projection_consumers` v1 (level 0 → 1), answering its own exit criterion
(4): *"the staleness subclass the instruction claims this deletes is MEASURED, not asserted:
name the derived-artefact-staleness entries that this consumer removes from the register, and
show the register short by exactly those."*

**Disposition:** QUEUED, not fixed on sight (SELF_INTERRUPT_DISCIPLINE). The repair is a
register-population change with a completeness test to re-prove, which is its own draw.

## Observed, with evidence

`DIRECTOR_INSTRUCTION_QUERYABLE_PROJECTIONS_2026-08-10` claims of its third consumer: *"the
site's derived pages read projections instead of hand-refreshed files — **deleting a whole
subclass of the derived-artefact-staleness wedge disease**."* G13's exit turned that into a
measurement. The measurement does not come back the way the exit expects.

**The register, before and after this consumer landed** (`background/derived_artefact_register.py`,
run on the live tree):

| | value |
|---|---|
| `REGISTER` | 3 entries |
| `discover()` | the same 3 |
| `unregistered()` | `set()` |
| `--completeness` | rc 0 |

The three are `BLOCKED_ATOM_VISIBILITY.md`, `FORWARD_ATTACHMENT_LEDGER.md`,
`PULL_FORWARD_PROPOSALS.md`. **This consumer removes ZERO of them, and the register is not
short by anything.**

That is not a shortfall in the work. The register **cannot** carry a site feed, by construction.
`discover()`'s membership predicate is *a module in `background/` or `tools/` that takes a
`--write` argparse option **and** owns a module-level `docs/design/*.md` path*. Every member is
therefore a markdown design document. No `site/data/*.json` feed can ever be one, whatever its
staleness.

## The population that WAS never enumerated, now measured

Counted by AST over `tools/` and `background/` for the module that writes each feed, then
checked against the publish path (`background/process_run_complete.py`):

| | feeds |
|---|---|
| `site/data/*.json` total | **47** |
| writer the publish path calls | 36 |
| **writer NO publish path calls** | **4** |
| no writer at all | 5 |

The four: `fidelity.json` (`tools.generate_fidelity_data`), `judge_validation.json`
(`tools.generate_judge_validation_data`), `regulatory.json` (`tools.generate_regulatory_data`),
`wip_flow.json` (`tools.generate_wip_flow_data`). **Corroborated independently:** all four
generators are already listed in `docs/design/orphan_baseline.json` as caller-less, by a
mechanism that knows nothing about this one.

The five with no writer at all: `control_kill_list.json`, `glossary.json`,
`knowledge_price_cap.json`, `knowledge_topics.json`, `tours.json`.

G13 removes **one of the four** — `wip_flow.json`'s `wip` block, now fed from the projection
store at HEAD. Three remain, and the register is blind to all of it.

**Excluded deliberately, and said so rather than folded in:** `tick_heartbeat.json` also has no
publish-path caller, but `background/worker_tick.py` writes it every tick, so it is refreshed by
a live caller and is not this class. `projections.json` (this atom's own new feed) likewise has
no publish-path caller — see the residual in `G13_projection_consumers.yaml`; it is counted
honestly there, not quietly excluded here.

## Why it is a class, not one missing row

1. **The register's own docstring names the trap it fell into.** It says a hand-kept index is
   "exactly the fail-open control this project has been bitten by before
   (`feedback_index_is_a_fail_open_control`)", and answers it with AST discovery so a new derived
   artefact "cannot ship unregistered". That reasoning is sound and its scope is not: discovery
   is fail-closed *within* `docs/design/*.md` and fail-**open** for every other derived artefact
   in the repo. The guard is right; the population is wrong.
2. **The consequence is the same shape, one directory over.** A `docs/design/*.md` going stale
   wedges the publish gate loudly (four wedges on 2026-08-09/10, which is why the register
   exists). A `site/data/*.json` going stale wedges nothing and publishes a wrong number
   quietly — strictly worse, because the loud failure is the one that gets fixed.
3. **A director instruction has now been written against the un-enumerated population.** The
   2026-08-10 instruction reasons about "a whole subclass" that no artefact in this repo counts.
   An exit criterion asked for the count and the honest answer was "the register cannot say" —
   which is how an unenumerated population is supposed to surface, and did.

## What closing it looks like (the drawable half)

Extend `derived_artefact_register` from *one rendered path per module* to *the set of derived
artefacts a module writes*, with the site-feed segment-join oracle
`tools/file_scope_generated_paths.py` already implements (it finds 116 artefacts across five
trees where a full-path literal search finds 17 — that technique is the reusable half). Then the
existing publish-path repair applies unchanged to the wider set.

**R15 note, and it is not the obvious one.** The completeness test must be mutated by *adding a
site feed whose generator has no caller* and confirming the register reds — not by re-checking
that today's three resolve. Today's three resolving is exactly what a register that has silently
excluded 44 feeds also does.

## Not asserted

* **Whether all four remaining feeds should be publish-path-driven.** Two of the four
  (`regulatory.json`, `fidelity.json`) may be deliberately frozen artefacts rather than stale
  ones; that is a per-feed judgement and reading it off a count would be the absurdity this
  finding objects to. The count is a floor on the population, not a verdict on any member.
* **Whether the 5 no-writer feeds are dead or hand-authored.** `control_kill_list.json` has no
  writer *and* no reader found in `.py`/`.html`/`.mjs` — likely an orphan, checked no further.

— Worker finding, 2026-08-19, during `G13_projection_consumers` v1.
