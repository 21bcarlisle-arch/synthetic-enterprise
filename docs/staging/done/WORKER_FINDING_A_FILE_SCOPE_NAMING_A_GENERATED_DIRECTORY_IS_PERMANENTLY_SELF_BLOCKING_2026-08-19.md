# WORKER FINDING — an atom whose `file_scope` names a machine-regenerated directory can never be drawn

**Severity:** LATENT · **Lane:** H_harness
**Date:** 2026-08-19
**Raised by:** the director's instruction of 2026-08-19 — *"Read
`DIRECTOR_INSTRUCTION_QUERYABLE_PROJECTIONS_2026-08-10` first … tell me why it never drew —
that's its own finding."*
**Class:** silent draw starvation. Not a bug in any control; every control behaved to spec.
**Status:** cause CONFIRMED by running the real draw. Instance fixed. Class fix named below.

---

## The question

`G12_queryable_projections` — the query store — was built on 2026-08-11 and reached L2. Its
consumer, `G13_projection_consumers`, is the atom that makes the store more than a design with
no caller. It has been `loop_stage: build`, unblocked, with its dependency satisfied, since
that day. `tools/lab_query.py` does not exist. Nothing reads the store.

Eight days. The director asked why.

## The answer I expected, and why it was wrong

The obvious hypothesis is that G13 was blocked — an unmet `depends_on`, a park, a
`block_reason`. **All three are false**, and I checked rather than assumed. G13 has
`depends_on: ['G12_queryable_projections']`, and G12 sits at `level_current: 2` against
`level_target: 2` — satisfied. No `block_reason`. Stage `build`.

Running the draw probe over the whole map, G13 **is offered**:

```
whole-map draw offered 17 atom(s): [... 'G13_projection_consumers' ...]
G13 offered from the whole map?   True
```

That result is where I would have stopped if I had trusted the probe. It is wrong, and the way
it is wrong matters: `blocked_atom_visibility._draw_reading` deliberately monkeypatches two of
the draw's filters off (`_build_in_progress_ids` and `_prefer_unmerged_free`) so that a
single-atom fixture is not excluded by an artefact of the fixture. That is correct for the job
that harness does. It also means **the probe does not answer "would the real draw offer this"**,
which is the question I was asking it.

## The actual cause, measured on the real draw with every filter live

```
paths carrying unmerged work: 137
  ...of which under site/data/: 18 -> ['site/data/activity_cost.json',
                                       'site/data/capabilities.json',
                                       'site/data/company.json',
                                       'site/data/dashboard.json', ...]

UNMERGED-WORK guard (BUILD): deprioritising [22 atoms, including 'G13_projection_consumers']
  -- file_scope overlaps unmerged branch/worktree work
     (a fresh fork would mint a rival implementation)

REAL draw offered: ['EP6_wall_protocol_typing', 'H27_payment_belief_gap',
                    'KNIFE3_wall_crossing_paydown', 'EP1_clv_three_horizon',
                    'SITE2_two_sided_wall_exhibit']
G13 offered by the REAL draw? False
```

G13's `file_scope` is `['site/data/', 'tools/lab_query.py', 'tests/tools/test_lab_query.py']`.

**`site/data/` is not a source directory. It is the publisher's output.** Every publish cycle
rewrites the JSON in it. So it carries uncommitted changes essentially always — 18 files' worth
at the moment of measurement. `_unmerged_work_paths()` reads that from git reality, correctly
reports it, and the guard deprioritises every atom whose scope overlaps it.

The guard is right. Its docstring states its purpose exactly: *"an atom whose declared
`file_scope` overlaps a path with unmerged work is not offered as fresh BUILD work while a
non-colliding candidate exists, so the draw cannot mint a rival implementation of work already
in flight."* On 2026-07-30 the absence of this guard produced two rival implementations of one
atom. It was built for a real defect and it prevents that defect.

But its escape hatch — *"if every candidate collides, the full set is restored rather than
reporting false exhaustion"* — only fires when **every** candidate collides. Five did not. So
the set was never restored, and G13 lost the comparison every tick, forever, silently.

**Nothing was broken. An atom pointed its scope at a directory a machine rewrites, and thereby
declared itself permanently in-flight.**

## The finding is bigger than G13

Twenty-two of the twenty-seven buildable atoms were deprioritised in that same draw. The
buildable set the loop actually sees is **five**, not twenty-seven.

That is the mechanism behind the convergence collapse the director asked about separately. Level
moves from the ledger:

| date | level moves |
|---|---|
| 2026-08-09 | 33 |
| 2026-08-10 | 14 |
| 2026-08-12 | 9 |
| 2026-08-13 | 3 |
| 2026-08-14 | 10 |
| 2026-08-15 | **0** |
| 2026-08-16 | **0** |
| 2026-08-17 | 1 |
| 2026-08-18 | **0** |

The guard's reach is a function of how dirty the tree is, and the tree has been getting dirtier.
As unmerged paths accumulated, the buildable set shrank — with no alarm, because a deprioritised
atom is indistinguishable from an atom that simply lost a weighted draw. The loop then did the
only thing left that was always available: another DISCOVER pass. **The cheapest lawful path
became the one that produces nothing, not because discovery was made cheap, but because building
was quietly made impossible.**

## What I have done

1. **G13's scope narrowed to SOURCES ONLY** — `tools/lab_query.py`,
   `tools/generate_projections_page.py` and their tests. My first attempt at this fix was
   wrong in an instructive way and I am recording it rather than the tidy version: I replaced
   the directory `site/data/` with the specific artefact `site/data/projections.json`, which
   looks like the fix and merely **defers** it. That file would be regenerated by the publisher
   on every cycle exactly like its twenty siblings, so it would become permanently dirty the
   moment it existed, and G13 would starve again at its next level — with the same silence.

   The convention already in the map says so plainly, and I should have read it before
   inventing a rule: **15 of the 17 SITE atoms name zero `site/data` entries.** An atom scopes
   the generator, never the generated. Verified against the mechanism rather than the map —
   with the narrowed scope the real draw, every filter live, now returns:

   ```
   REAL draw now offers: ['EP6_wall_protocol_typing', 'H27_payment_belief_gap',
                          'KNIFE3_wall_crossing_paydown', 'EP1_clv_three_horizon',
                          'G13_projection_consumers', 'SITE2_two_sided_wall_exhibit']
   G13 offered by the REAL draw now? True
   ```

   **The two exceptions carry the same latent defect**: `SITE6_knowledge_in_nav_glossary_dissolved`
   names `site/data/glossary.json` and `SITE12_evidence_a_reader_can_use` names
   `site/data/capabilities_door.json`. SITE12 is in the deprioritised list above, today, for
   this reason. Left in place rather than swept, so the class gate below has live cases to
   fail on instead of a clean tree that proves nothing.
2. **The pass ceiling** (landed separately) bounds the other half: an atom investigated five
   times without moving leaves the discovery draw and becomes a decision.
3. **`EP1` and `EP6` promoted to build** on the director's instruction — both had **empty**
   `file_scope`, which is the same defect wearing different clothes: an atom that may legally
   edit nothing cannot change its own state either. Both now carry real scopes, and both appear
   in the real draw's offer set above, which is the proof the promotion took.

## What is still open — the class fix (R10)

An instance fix is not a closure here. The invariant that was missing:

> **A `file_scope` entry may not name a path any generator writes.**

This is checkable and cheap: the publish path already knows which files it regenerates. A gate
comparing every atom's `file_scope` against that set would have failed the day G13 was minted,
with a message naming the exact collision. Until it exists, the next atom to name `site/data/`,
`docs/observability/`, or `docs/market_data/` will starve the same way and nothing will say so.

Queued as an atom rather than fixed on sight, per SELF_INTERRUPT_DISCIPLINE.

## Secondary observation, not the cause

`docs/observability/.build_in_progress.json` holds three atoms (`SITE1_expert_doors`,
`W1_7_renewable_capacity_trends`, `F1c_harness_conversation_gap`) marked in-flight since
**2026-08-13** — forks six days dead. This is **not** what starved G13: that reader carries a
TTL and fails open, so the stale entries already expire and exclude nothing. It is recorded
because it is exactly the class of unbounded-lifetime litter the 2026-08-19 housekeeping ruling
covers, and the disk governor landed today does not reap it — it reaps scratch directories, not
stale state files. Named so it is not mistaken for a cause, and not lost.
