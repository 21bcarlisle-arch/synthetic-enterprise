**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** H45_the_queue_is_chained_to_the_map

**Knowledge:** none — this is machinery, not domain. No knowledge-layer page is reached or owed.

# LAW C's independent read believed a mint doc's sentence, which the same doc disclaimed three paragraphs later

**Delivery seat, scheduled tick, 2026-09-09.** Drawn as "mint one atom per named deliverable" from
`DIRECTOR_RULING_SUPPLIER_USE_CASE_REGISTER_AND_SIM_FIDELITY_2026-09-06.md`. The mint was already
specified. What was not already done was writing it down anywhere a machine could read.

---

## The headline

`docs/staging/done/PLANNER_MINTED_the_ruling_and_the_canon_are_seven_eighths_minted_..._2026-09-07.md`
carries two machine-readable coverage lines:

```
- Source: `DIRECTOR_RULING_SUPPLIER_USE_CASE_REGISTER_AND_SIM_FIDELITY_2026-09-06.md`, deliverable 1 — MINTED here as `A50`
- Source: `DIRECTOR_RULING_SUPPLIER_USE_CASE_REGISTER_AND_SIM_FIDELITY_2026-09-06.md`, deliverable 4 — MINTED here as `A51`
```

and, in its own closing section:

> **Did not:** write `A50`/`A51` into `docs/design/maturity_map.yaml`

Both statements were true when written. `A50` and `A51` have never appeared in
`maturity_map.yaml`, `maturity_map_closed.yaml` or `maturity_map_retired.yaml`, in the working tree
or in any commit — `git log -S"A50_"` over all three map files returns nothing. The document was
then archived to `done/`, so nothing re-drew it; the ruling stayed in the staging root, so it
re-drew in every tick's doorbell for two days.

**And `background/primary_state_scan.named_but_unminted()` — LAW C's second, independent read, the
source built to contradict the tick when the tick is wrong — reported both deliverables covered the
whole time.** Its coverage signal 1 accepted the `Source:` line and never asked whether `A50`
existed. The one mechanism in the architecture positioned to catch a mint that did not happen was
reading the claim instead of the referent.

## The measurement

Every `Source:` coverage line across the staging root, `in_progress/` and `done/`, with each cited
atom resolved against all three map files by id prefix (docs cite `G14`, the map stores
`G14_half_hourly_grid_carbon_intensity_aligned_to_settlement`):

| | count |
|---|---|
| coverage lines naming at least one atom | 10 |
| of those, every cited atom resolves | 8 |
| **dangling — cited atom on no map** | **2** — `A50`, `A51` |
| coverage lines naming no atom at all | 18 |

The class is exactly two members and they are the two the 09-07 tick deliberately deferred. Its
reason was good: the map was mid-collision that day, carrying 207 uncommitted lines from another
lane, and a pathspec commit of it would have swept them. **The deferral was correct and the
archiving is what lost it.** The contention it was waiting on has since cleared —
`W2_29`, `W2_30`, `W2_31` and `W1_28` are all at `HEAD`, and the map is clean against `HEAD` as of
this tick.

**A first pass at this measurement said all ten were dangling.** The id regex compared the cited
short form against the full slug, so `G14` "failed to resolve"
`G14_half_hourly_grid_carbon_intensity_aligned_to_settlement`. Recorded because the wrong number is
the more instructive one: a referent check keyed to the wrong matching rule reds on everything, and
the version of this fix that shipped without printing the table first would have refused eight
correct mints on its first run.

## What changed

**1. `A50` and `A51` are on the map**, specified as the 09-07 document specified them — lane
`A_strategy_governance`, `provenance: director_ruling`, targets L2 and L1, `A51 depends_on A50`
plus `G14`/`G15`. `A50`'s comment carries the gap it exists to close, measured today:
`site/data/capabilities.json` parses to `{generated_at, git_commit, phase, cards}` and contains the
string "use case" zero times, so the register the ruling asked to publish has no home on the page it
named. `A50`'s first dependency is stated rather than assumed — the ruling's deliverable 2 names six
sub-items whose homes the 09-07 tick explicitly did not verify, and "status per item" cannot be
truthful until each has one.

**2. Coverage signal 1 now checks the referent.** When a `Source:` line names atoms, every one must
resolve on the map or the line covers nothing. Reads the map files directly off disk — no supervisor
import, no tick argument, so LAW C's independence wall is intact; the maturity map is named in
LAW C's own text as primary state.

**3. The stated limit is held by a control, not by a sentence.** 18 of the 28 live coverage lines
name no atom at all: the older one-mint-doc-per-deliverable form, where the *document* is the mint
record. Requiring an id on every line would fabricate residue for 18 correct mints — the opposite
failure, and the more expensive one. `test_a_coverage_line_naming_no_atom_is_untouched` reds if
someone closes that hole blind. It remains a real hole and it is named here rather than patched.

## Evidence

**Poison round before the battery**, because "survived" means two opposite things. Live residue with
`A50`/`A51` on the map: **37**, and this ruling contributes none. Against a map with the two rows cut:
**39**, the two newly exposed being exactly this ruling's deliverables 1 and 4. So the branch is
reachable and it fires on the instance it was written for.

**Mutation battery**, 18 tests in `tests/background/test_named_but_unminted.py`:

| mutation | reds |
|---|---|
| referent check deleted (the old fail-open restored) | 3 tests |
| prefix rule degenerated to substring match | 1 test (`A5` would have resolved `A50`) |
| fail-safe flipped — unreadable map read as empty | 1 test |

**Fail-safe direction preserved and proven both ways.** No readable map ⇒ "cannot check" ⇒ the
citation is accepted exactly as before, so a read error can never *fabricate* residue, matching this
module's declared positive-detection contract. An *empty but readable* map is the opposite verdict
on the same input, and the test asserts both.

**One existing control was keyed to today's answer and I re-keyed it rather than deleting it.**
`test_law_c_takes_no_tick_or_enumeration_argument` asserted the literal parameter set
`{staging_dir, in_progress_dir, done_dir}`. Adding `map_files` — a primary-state path, which is
precisely what that wall exists to permit — turned it red for a change that made the module *more*
independent. It now asserts the property: every parameter is path-typed and defaults to `None`, so
nothing that is not a primary-state location can be injected at all.

## Disposition

The ruling is archived to `docs/staging/done/`. All four of its deliverables are now covered: 1 and 4
by `A50`/`A51`, 2 by `W2_25`/`W2_26`/`W2_31` with the limit above, 3 by `G14`/`G15`. **Minted is not
built** — the build obligation now lives on the map, which is the queue that draws build work, and
the doc's presence in the staging root was drawing mint work that no longer exists. Archiving it is
what stops the re-draw; it burned several ticks' orientation, each of which reached this same
conclusion and none of which could act on it because the map was contended.

`test_the_two_atoms_the_defect_lost_are_on_the_real_map_now` is the guard on that archiving: with the
ruling in `done/` it is no longer a residue source, so if `A50`/`A51` are ever swept off the map
again the residue signal will not re-expose them — that test will.

## What is next

1. **`A50` is drawable now** and its first step is the six sub-items of the ruling's deliverable 2 —
   locate a home for each or declare it missing. The register cannot carry a truthful status per
   item before that.
2. **`A51` has a person at the end of it.** Three of its four sections describe the register, so it
   waits on `A50`; the fourth states the hedging risk envelope (ruling 3.3) as reserved and awaiting
   the director. A ratification is parked behind a report nobody has written.
3. **The 18-line hole is unclosed.** A mint doc naming no atom still covers by assertion alone. The
   honest fix is not a stricter regex — it is that the newer coverage lines carry an id and the older
   ones cannot be retrofitted, so the rule has to be dated or the old docs re-headed. Filed, not
   guessed at.
4. **The shape generalises past this module.** The 09-07 audit already found that "the measuring got
   minted; the telling did not", across six rulings. This tick adds the layer below it: a record
   claiming a mint is not the mint, and until today nothing anywhere checked the difference.

— Delivery seat, 2026-09-09.
