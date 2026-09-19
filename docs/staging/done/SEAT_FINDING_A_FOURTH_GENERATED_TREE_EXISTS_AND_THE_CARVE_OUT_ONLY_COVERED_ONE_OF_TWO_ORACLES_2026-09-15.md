**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `does-a-fourth-generated-tree-exist-that-nobody-declared`)

# A fourth generated tree exists, `docs/status`, and declaring it exposed that the irreproducible-record carve-out only ever covered one of the two oracles that share a union

**Filed 2026-09-15, delivery seat.** Prereg:
`docs/staging/records/PREREG_WHETHER_A_FOURTH_GENERATED_TREE_EXISTS_THAT_NOBODY_DECLARED_2026-09-15.md`,
written before any directory was counted.

The five preceding frames all widened **how a path is spelled**. This one asks the other half —
**which trees are declared at all** — and it is the first in the sequence that moves the commit
gate rather than the reconciler.

---

## 1. The asymmetry that made this a separate turn

The whole-string frame that landed immediately before this provably *could not* move
`gate_violations()`: `offends()` decides a `file_scope` entry by tree PREFIX, and every member
`generated_artefacts()` can return already sits under one of those prefixes, so the membership test
is **subsumed**.

A `GENERATED_TREES` addition moves the *subsuming* predicate itself. Every `file_scope` entry under
the new prefix starts offending at once, and `FROZEN` was measured against exactly three prefixes on
2026-08-19. Widening without re-measuring the freeze makes it read STALE — and
`tests/tools/test_file_scope_generated_paths.py:78` asserts `gate_violations() == []`, so a
half-landed widening refuses **every lane's** commit, not just this one's.

Order was therefore forced: census → candidate → re-measure `FROZEN` → land both together.

## 2. The instrument, and the one that could not be used

`generated_artefacts()` cannot answer this question. It is keyed to `GENERATED_TREES` and returns
only paths under the three declared prefixes, so asking it where the *undeclared* generated trees
are is asking a question of the thing whose blindness is the subject — a control that is evidence
about itself.

The census was therefore computed over `_write_reached_paths()`, the raw write-site scan, which
resolves a destination from a write SITE with no knowledge of which trees are declared.

## 3. The census

12,846 tracked files; 169 write-reached paths (130 tracked, 39 not). Per directory, at every depth:
`density = |tracked ∩ reached| / |tracked|`.

**The three declared trees:**

| tree | tracked | reached | density |
|---|---|---|---|
| `docs/market_data` | 3 | 1 | 0.333 |
| `docs/observability` | 271 | 46 | 0.170 |
| `site/data` | 322 | 39 | 0.121 |

**Undeclared directories with any write-reached file, by density:**

| directory | segs | tracked | reached | density |
|---|---|---|---|---|
| `sim/household_siting` | 2 | 2 | 2 | 1.000 |
| `sim/weather_cells` | 2 | 2 | 2 | 1.000 |
| **`docs/status`** | **2** | **5** | **4** | **0.800** |
| `docs/reports` | 2 | 33 | 9 | 0.273 |
| `site/state` | 2 | 50 | 8 | 0.160 |
| `site/brand` | 2 | 5 | 1 | 0.200 |
| `docs/design` | 2 | 901 | 12 | 0.013 |
| `docs/staging` | 2 | 7,905 | 1 | 0.000 |

## 4. Q1 failed, and the diagnosis is finer than the stopping rule I wrote

**Q1 FALSIFIED.** I predicted all three declared trees would score ≥ 0.5 and called it the
calibration — "the one I most expect to be wrong". All three score *below* 0.5. My §5 rule said:
*stop, density is the wrong instrument, do not use the census to justify any addition.*

The rule's verdict is right and its diagnosis is too coarse, and the difference matters enough to
write down rather than quietly route around.

Density is not the *wrong* instrument, it is a **one-sided** one. A write site is positive evidence
that a module writes there; the *absence* of one is not evidence of authorship, because the scan's
recall is poor by construction — the module's own docstring counts **364 unresolved write
destinations** against the 169 it resolves. `site/data` scores 0.121 not because 88% of it is
authored but because the instrument can only spell 12% of what writes into it. So **low density is
uninformative and high density is informative**, and a threshold applied symmetrically to both was
the wrong shape of test, not the wrong measurement.

What I did with that: the census was used **only to nominate** candidates, never to justify the
addition. `docs/status` was then verified file by file on provenance — which is the evidence §6
rests on — and the decisive argument is the live gate instance in §5, which is not a density
argument at all. I am recording that I overrode the stopping rule as written rather than claiming
it was satisfied.

**Q3 HELD** — I named `docs/status` in advance as the single most likely candidate.
**Q7 FALSIFIED** — I predicted the highest-density undeclared directory would not be two segments;
`sim/household_siting` and `sim/weather_cells` both score 1.000 and both are exactly two.
**Q6 FALSIFIED** — I predicted an undeclared directory with ≥5 gitignored generated files. There is
none. The only directory meeting the bar is `docs` itself (37), of which 36 are `docs/observability`
(declared) and 1 is `docs/staging/reference/HEAD_RED_REGISTER.md`. The aggregation over ancestor
directories manufactured the appearance of a candidate; the finding is that there is no gitignored
generated tree hiding anywhere.

## 5. `docs/status` is generated, file by file

Not density — provenance, checked individually:

| file | written by | its own first lines |
|---|---|---|
| `LATEST.md` | `generate_snapshot`, `publish_surface_gate`, `status_honesty`, `naive_organ`, `sim_runner` | `Last updated: 2026-09-10T01:08:41Z` |
| `PROJECT_STATE.txt` | `generate_project_state`, `process_run_complete` | `Generated: 2026-09-10T01:13:18Z` |
| `STARTUP_ANCHORS.md` | `startup_anchor_freshness`, `process_run_complete` | `Generated: 2026-09-10 by tools/startup_anchor_freshness.py` |
| `SEAT_STRETCH_LOG.md` | `stretch_log`, `process_run_complete` | (see §7 — the exception) |
| `index.html` | `render_site_nav` | not write-reached; rendered |

**And there is a live instance.** `OPS3_first_post_ruling_publish` declares
`docs/status/LATEST.md` in its `file_scope`. `LATEST.md` is the live-state page rewritten by five
producers, so the unmerged-work guard has deprioritised that atom on every tick it was dirty —
which is always — for as long as both the declaration and the blindness have existed. That is the
G13 starvation defect, live, invisible, and the reason this is a declaration rather than a
speculative ratchet.

The same atom was **already** frozen for `docs/observability/.publish_gate_state.json`. One atom
starving through a second door nobody could see is what a class looks like from inside.

## 6. What the change actually moves

| | before | after |
|---|---|---|
| `generated_artefacts()` | 191 | 193 |
| `written_artefacts()` | 161 | 160 |
| **union (`origin_reconcile._split_generated`)** | **247** | **246** |
| `violations()` | 10 | 11 |
| `gate_violations()` | 0 | 0 |

`LATEST.md` and `STARTUP_ANCHORS.md` join the tree-keyed oracle; both were already in the
write-keyed one, so **the union does not gain a single path**. The one union movement is a
*removal* (§7). This is the exact mirror of the previous frame, where the gate could not move and
the union did — and it is why the two were carved apart.

## 7. The defect the declaration exposed

`WRITTEN_BUT_NOT_REPRODUCIBLE` is the escape hatch for a path a module rewrites whole that is still
nobody's photograph. It was subtracted from `written_artefacts` **only**, and that was safe purely
by accident: no member happened to live under a declared prefix, so the tree-keyed oracle could not
produce one however the list grew.

Declaring `docs/status` ends the accident. `tools/stretch_log.append` reads the log, splices one
entry in after the header and writes the file back whole — the `naive_organ` shape exactly, an
append wearing a rewrite's clothes, which `WRITING_MODE_CHARS` cannot see. The entry is the seat's
own words (`validate_subject` refuses one that cannot stand alone), stamped with the day and the
HEAD it was written at. No run makes it again, and the remedy the reconciler prints for a generated
path is `git show HEAD:<path> > <path>` — which discards the stretch whose reasoning is the only
record of why a call was made.

It was **already** reachable through the write-site door and uncarved, so the harm was live before
this change; declaring the tree would have added a second door to it and made the one-line fix
insufficient. So the subtraction now applies to both oracles. Two oracles feeding one union with a
carve-out honoured by one of them is not a carve-out — the path arrives through the other door and
the fix looks applied.

**And it does not buy that safety with the gate**, asserted rather than assumed: 0 of 193 oracle
members escape the prefix test, so membership is dead weight for `offends()` and the subtraction
reaches exactly one consumer — the reconciler's union, where the revert harm lives.

## 8. The two candidates DECLINED, with their numbers

Neither is swept in on density, and the reason is structural rather than fastidious:
**`WRITTEN_BUT_NOT_REPRODUCIBLE` is a per-path hatch and a PREFIX refusal has no equivalent.** A
tree holding one irreproducible record cannot be declared and then corrected, so the bar for a tree
is *every* path under it, not most.

- **`docs/reports`** — 33 tracked, 9 reached (0.273, higher than two of the three declared trees).
  **0** live `file_scope` violations, so there is nothing to prevent today. `REPORTING_BACKLOG.md`
  reads as authored judgement — *"prioritised follow-on items identified while building the Phase
  5a annual report"* — and `ANNUAL_REPORT.md` carries no generation stamp. Ambiguous reproducibility
  plus nothing to prevent is a decline, not a deferral.
- **`site/state`** — 50 tracked, 8 reached (0.160). **0** live violations. The 42 unreached files
  are `live_decisions_YYYYMMDD.json` snapshots written under a computed name, which is exactly why
  the scan cannot resolve them — so this one is probably a real generated tree and is declined for
  the *weaker* reason: `live_decisions_log.jsonl` is an accumulated ledger of run-stamped decisions,
  the same irreproducible shape as §7, and there would be no hatch for it.
- **`sim/household_siting`, `sim/weather_cells`** — 2/2 each, below the tracked ≥ 3 bar, and
  `sim/` is not a neighbour of any declared tree. Recorded, not acted on.

## 9. What is still out

- **A generated tree that is one segment deep, or three, cannot be expressed at all.**
  `GENERATED_TREES` members are exactly `(parent, child)`. `docs/observability/scale_probe_10k` is
  already reached only because its parent is declared. This is a real structural limit, named here
  rather than discovered by the next census.
- `docs/status/index.html` stays classified authored: `.html` is not in `ARTEFACT_SUFFIXES` and
  `render_site_nav` does not reach it through a resolvable destination. It degrades the safe way —
  offered a landing, never reverted.
- The write-site scan's recall is the ceiling on every census of this kind: **364 unresolved
  destinations against 169 resolved.** Any future directory census inherits the one-sidedness in
  §4, and should be written as a one-sided test from the start.
