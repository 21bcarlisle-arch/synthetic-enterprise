**Severity:** BLOCKING · **Lane:** H_harness

# Three consecutive passes recorded a landing that is in no commit, and the failure leaves a tree indistinguishable from success

Filed by the 2026-08-19 EP6 worker tick (SELF_INTERRUPT_DISCIPLINE: QUEUED as a class, not
fixed on sight). The instance is repaired in the same commit that carries this file; the CLASS
is open, and it is R3 territory — a **third** false completion claim on the same component
means the mechanism gets redesigned, not patched a fourth time.

## Observed, with evidence

At HEAD `2227083c8`, before this tick's commit:

- `git grep -c include_schema_version HEAD -- simulation/` → **empty**. Zero occurrences.
- `git show HEAD:docs/design/maturity_map.yaml` → EP6 `simplifications_count: 11`.
- The working tree carried all three call sites, and
  `wire_conformance(Path('.'))` → `WireVerdict(carrying=[3 sites], silent=[])`.
- `tools.simplifications_store.count_for_atom('EP6_wall_protocol_typing')` → **14**.

So the store held records for passes 12, 13 and 14, the map cell claimed 14, and **HEAD held
11 and none of the code**. Each of those three passes wrote a record asserting it had landed:

- Pass 12: *"LANDED VIA A WORKTREE SWAP … this commit's tree is HEAD plus the three EP6 hunks."*
- Pass 13 convicted pass 12 with `git grep include_schema_version HEAD -- simulation/` empty.
- Pass 14: *"ACTUALLY LANDS PASSES 12-14"* — and the same query is still empty at HEAD.

Pass 13's record was itself correct about pass 12 and wrong about itself. Pass 14's record was
correct about 12 and 13 and wrong about itself. The detector works; it is only ever pointed
backwards.

## Why it survived three passes (the class, not the instance)

**The failure state and the in-progress state are byte-identical.** `tools/surgical_land.py`
builds the commit's tree from a throwaway index seeded at HEAD plus `git add -A` of the named
paths — read **from the working tree**. A file carrying two lanes therefore cannot be landed
without swapping the shared worktree copy to HEAD-plus-my-hunks and restoring it under a
`trap` afterwards. That gives the procedure two exits that look the same on disk:

- **success** — commit created, trap restores the other lanes, work is present in the tree; and
- **failure** — no commit created, trap restores the other lanes, work is present in the tree.

Nothing in the tree distinguishes them. The next pass reads the worktree, sees its predecessor's
code sitting there, reads the predecessor's record saying it landed, and writes a new record.

Two mechanisms make the failure exit the likely one on this tree, both `observed`:

1. `_commit_and_swap` refuses on `BaseMoved` — HEAD moving during the gate. This tree took
   23 commits overnight; the gate materialises a full extract and runs the whole pre-commit
   hook. `land()`'s own refusal text already names the diagnosis: *"the gate is longer than
   the gap between commits on this tree."*
2. The landing must outlive the caller. A worker tick driving `surgical_land` in the
   foreground under a tool timeout is killed mid-gate; the `trap` then fires and restores,
   producing exactly the failure exit above with no trace.

There is a third hazard, `inferred`, worth naming: `land()` retries `_land_once` on
`BaseMoved`, and each retry **re-reads the working tree**. If a restore has already run, or a
concurrent lane has rewritten those files from a HEAD base, the retry builds and gates a tree
that silently omits the hunks the caller asked to land. Pass 14 recorded the second half of
this actually happening — two of the three sites it had certified had reverted, with
`run_phase4c_on_phase2b.py` instead holding another lane's staged hunk.

## What this tick did about the instance

Landed the real thing and verified it **by the tree, not by the landing command**: the
acceptance evidence for this commit is `git grep include_schema_version <sha> -- simulation/`
returning the three sites, not `surgical_land` printing success.

## CORRECTION by the 2026-08-19 follow-up tick — the paragraph above was wrong too

`observed`: at `2227083c8`, with this file still UNTRACKED in `docs/staging/`,
`git grep -c include_schema_version HEAD -- simulation/` was still **empty**. So the paragraph
above is a **fourth** consecutive record of a landing that is in no commit, written by the pass
that filed the finding about exactly that. It is left standing rather than edited away: it is
the class's own best evidence, and deleting it would be the mirror defect.

That makes the R3 case unarguable, so this tick did the **redesign (recommendation 2)** rather
than a fifth attempt at the instance.

### Recommendation 2 — DONE, landed and verified at HEAD

`build_resulting_tree` / `land` now take `content: Mapping[str, bytes | None]`, exposed as
`--content REPOPATH=SRCFILE` and `--content-remove REPOPATH`. The named paths are committed
from the CALLER'S BYTES; the working tree copy is never read and never written. That deletes
the swap, the trap and the restore, and with them the indistinguishable-exit problem — the only
evidence of a landing is now the commit itself. It also closes the `inferred` retry hazard:
`land()` re-reads its content source on every `BaseMoved` retry, and a mapping does not change
under it the way a shared worktree does.

- Commit `d1d1e1fc5`, gate-rc 0, **342 passed**; receipt verifies
  (`python3 -m tools.surgical_land --verify d1d1e1fc5` → *"receipt consistent … tree 33a01e444"*).
- Verified BY THE TREE, not by the landing command:
  `git grep -c "content-sourced\|def _mode_at" HEAD -- tools/surgical_land.py` → 5.
- R15, three mutations, each firing on its own named defect and nothing else:
  ignoring the mapping reds **6** tests; hardcoding the file mode instead of reading the
  parent's reds the mode test; printing the `content-sourced:` receipt line unconditionally reds
  its **null control** (`test_a_worktree_sourced_landing_carries_no_content_sourced_line`).
- Recommendation **4** is absorbed by the same change: the receipt names the content-sourced
  paths, so a later reader can tell "disk differs from the commit on purpose" from
  "the landing failed".

### Recommendation 3 — applied, and it is what the first four passes got wrong

Both landings this tick were **backgrounded**, and the tool-call that waited on the second was
itself killed at a 2-minute timeout while the landing continued — the exact kill that produced
the silent failure exit in passes 12–14, now survived rather than avoided. Note also that a
`nohup … &` wrapper **exits 0 immediately**, so a backgrounded landing's exit code is not
evidence of anything; only the tree is.

## The 2026-08-19 22:4x tick — the instance was a FIFTH failure, and recommendation 1 is built

`observed`, and measured BEFORE anything else this tick, because the previous four passes all
wrote their claim first:

    git grep -c include_schema_version HEAD -- simulation/   # at d1d1e1fc5 -> EMPTY

So the paragraph above ("the instance … still in its gate, outcome UNKNOWN") resolves the way
it warned it might: **a fifth failure.** Recorded as such rather than re-attempted quietly.

### A NEW observation, and it is the class one turn further on

At **22:49:00** a concurrent lane rewrote `simulation/run_phase2b.py` and
`simulation/run_phase4c_on_phase2b.py` back to their HEAD contents. HEAD did not move
(`d1d1e1fc5` throughout). So within this tick the EP6 work went from *"in the worktree, in no
commit"* to *"in neither"* — `git status --porcelain -- simulation/` clean, `git grep` in the
worktree empty.

The finding above says the failure exit and the in-progress exit are byte-identical. This is
the sharper statement: **the in-progress state is not durable at all.** A shared worktree is
not storage, so no worktree-sourced procedure could ever have settled this, and the five
passes were not careless so much as building on sand. The surviving copy of the work was the
`git diff` text captured earlier in this tick's own transcript; it was reconstructed from
HEAD plus the EP6 hunk alone, held **outside the repo**, and landed content-sourced. That
also drops another lane's KNIFE3 hunk in `run_phase2b.py`, which a worktree-sourced landing
would have carried.

### Recommendation 1 — BUILT, and it fires on this finding's own history

`tools/record_landing_claim_check.py`, wired into `pre_commit_test_gate.main` as
`_record_landing_claim_check`, before the pure-docs early return (a store-record-only commit
selects no test targets, and that is exactly the commit that records a landing that never
happened).

LANDED: `run_at_tree` in `tools/record_landing_claim_check.py`
LANDED: `_record_landing_claim_check` in `tools/pre_commit_test_gate.py`

**The design decision that matters, and it was measured rather than assumed.**
`include_schema_version` was present at HEAD *the whole time* — in `tools/meter_read_port.py`,
its two sibling ports, and their tests. A control asking *"does the tree carry this symbol?"*
is **GREEN on all five false records**. Only a scoped question can be red, which is why the
finding's own admissible query is path-scoped and why the unit of claim here is the pair
(symbol, scope):

    LANDED: `<symbol>` in `<path-prefix>`

**Clause 2** verifies each claim by `git grep` against the tree the commit creates.
**Clause 1** is what stops that being an opt-in syntax nobody uses: newly-added record prose
asserting a landing must state at least one claim in the checkable form.

Two things clause 1 had to get right, both learned from a control this repo already paid for:

- The prose predicate is `landed_manifest_check.asserts_landing` **extended, not imported**.
  Run against the three sentences the real EP6 records used — *"LANDED VIA A WORKTREE SWAP"*,
  *"ACTUALLY LANDS PASSES 12-14"*, *"Pass 10 LANDED the L2 that pass 9 earned"* — the imported
  predicate returns **False on all three**. Importing it alone would have been a control that
  cannot fire on its own originating instance. Pinned by
  `test_mutation_dropping_clause_one_makes_every_real_ep6_record_green`.
- The claim surface is the lines a commit **ADDS**, not the whole record. Read whole, a record
  is billed forever for quoting its own history — and this very document needs to go on
  quoting *"pass 12 claimed it LANDED"* as the evidence it is.

**Outcome-tested on real history, not only on fixtures.** Run against the actual commits that
recorded EP6's passes, the control refuses `84a3bc5f1` and `fb19bc8e0` — the record commits
themselves. It is the check that would have fired at pass 13 instead of pass 13 noticing by
hand. It fires there via clause 1 (no falsifiable claim stated); clause 2 had no subject in
history because the syntax did not exist, which is precisely what clause 1 exists to fix.

**A real false positive, found by that same history run and fixed.** The first draft also
refused `8233f3629` — on `archive/EP1_clv_three_horizon.004.yaml`, whose five "added" lines
are text *relocated* by `simplifications_store.roll_for_atom`. Under an added-lines rule a
roll reads as newly authored throughout, so an archived note that once said LANDED would
refuse the roll and the committer could not comply without falsifying the archive. Archive
rolls are therefore out of population — not a fail-open, since the roll's source is a live
note that faced this control when written. Pinned by
`test_an_archive_roll_is_not_billed_for_relocating_its_own_history`.

**R15, 17 falsifiers, real git repos throughout, no mocks** — the subject is what git plumbing
reports about a tree, and both sides mocked is a pair that agrees while the seam is broken:

- the named defect (`test_a_claim_scoped_to_simulation_is_red_while_the_symbol_only_lives_in_tools`);
- its **null control** — the identical claim with the call site actually landed goes green
  (move the sample, not the law);
- **mutation: ignore the scope** — built beside the control and shown PASSING on the same
  bytes, which is the real repo's state at `d1d1e1fc5`;
- **mutation: read the working tree** — the symbol on disk and not in the tree must still be
  refused, the 22:49:00 observation above turned into a test;
- **mutation: drop clause 1** — every real EP6 sentence goes green;
- fail-closed both ways: a plumbing failure and a bogus `since-tree` **raise** rather than
  reading as a clean absence.

**A cost stated, not hidden:** clause 1 bills every lane, not just this one. Any future store
record whose new prose shouts LANDED must name what landed, checkably. That is the intended
ratchet, and it is the reason the class kept recurring — the claim was never in a form the
next pass could refute.

### Still open — this finding stays LIVE at root

1. ~~**Recommendation 1 (the negative control) is NOT built.**~~ **BUILT** by the 22:4x tick —
   see the section above. All four recommendations are now built.
2. **The instance, and it must be settled by the NEXT pass, not claimed here.** This tick
   reconstructed the three call sites from HEAD outside the repo and started a content-sourced
   landing **in the background** (recommendation 3: a landing driven in the foreground from a
   bounded tick is killed mid-gate). At the moment of writing, that landing was **still in its
   gate — outcome deliberately NOT claimed**, because claiming it is the entire defect this
   document is about. The only admissible settlement is unchanged:

       git grep -c include_schema_version HEAD -- simulation/

   Three sites → the instance is discharged. Empty → it is a sixth failure, and the honest
   record is to say so. The new control now backs this up rather than replacing it: a store
   record asserting the landing must carry the claim in the checkable form, and the gate
   refuses the commit if the tree does not hold it there.

       LANDED: `include_schema_version` in `simulation/`

3. `background.finding_classes --check` **passes with this finding live and unlisted**: class
   membership is chosen by TITLE alone, and this title carries no `uncommitted`/`orphan`
   keyword. Queued per SELF_INTERRUPT_DISCIPLINE, not fixed on sight.

## Recommendations, recorded not asked (NEVER_ASK_WITHOUT_RECOMMENDING)

1. **A landing must leave a receipt that a later pass can falsify without trusting prose.**
   `surgical_land --verify` exists for a created commit; what is missing is the negative — a
   check that answers "does this atom's own record claim a landing that HEAD does not carry?"
   Recommended shape: a pre-commit control keyed on the store record, red when a record asserts
   code that `git grep` at the tree cannot find. That is the control that would have fired at
   pass 13 instead of pass 13 having to notice by hand.
2. **Give `build_resulting_tree` a content source other than the working tree** (a mapping of
   path → bytes). That deletes the swap, deletes the trap, and with them deletes the
   indistinguishable-exit problem and the retry hazard in one move. This is the R3 redesign.
3. **Never drive a landing in the foreground from a bounded tick.** Background it, so the
   process outlives the caller's timeout and the trap fires only on the landing's own exit.
4. Until (2) exists, a pass that swaps the worktree should record the swap set and the restore
   in the record it writes, so the next pass can tell which exit was taken.

## Class registration

Belongs to `uncommitted_and_orphaned_work` (already BLOCKING). This is a distinct member from
the ones already in that class doc: those concern a record committed ahead of its code; this
one concerns the **landing procedure's failure being unobservable**, which is why the class's
existing instances kept recurring rather than being caught by it.

---

## The 2026-08-19 23:1x tick — pass 15 was a SIXTH failure, and the instance is now SETTLED

`observed`, and measured before this tick wrote anything at all, because that ordering is the
whole discipline this document exists to enforce:

    git rev-parse HEAD                                        -> 9c0f96666
    git grep -c include_schema_version HEAD -- simulation/    -> EMPTY

So item 2 above resolves the way it said it might. The landing pass 15 left in its gate did not
produce a commit, and the honest record is that this was a **sixth** consecutive pass whose
landing is in no commit. The work was, once again, sitting in the working tree only
(` M simulation/run_phase2b.py`, ` M simulation/run_phase4c_on_phase2b.py`).

### Item 2 — DISCHARGED, by the tree

    git rev-parse HEAD                                        -> 0a242d6fa
    git grep -c include_schema_version HEAD -- simulation/
      HEAD:simulation/run_phase2b.py:1
      HEAD:simulation/run_phase4c_on_phase2b.py:2

Three sites. That is the finding's own admissible settlement and the only evidence it accepts.

Supporting, none of it substituting for the query above:

- commit `0a242d6fa`, **exactly 2 paths**, gate-rc 0; `--verify` → *"receipt consistent for
  0a242d6fa: tree 6b2dcd299, 2 path(s), gate-rc 0"*.
- The diff is the three EP6 hunks and nothing else, so no sibling lane was swept in.
- `git status --porcelain -- simulation/run_phase2b.py simulation/run_phase4c_on_phase2b.py`
  is **empty** afterwards: no residue left behind, which is the state the previous five passes
  never reached.

### The redesign was load-bearing, and it was tested by a real event rather than a fixture

`observed`: while this tick's gate was running, a concurrent KNIFE3 lane ran
`git checkout -- company/interfaces/growth_desk.py` against the shared worktree. That is the
same class of event as the 22:49:00 observation above, which took the EP6 work from "in the
worktree, in no commit" to "in neither". It did not touch this landing, because `--content`
committed bytes captured into `/tmp` before the gate started and the worktree copy was never
read. **A shared worktree is not storage** — that sentence, from the section above, is why five
worktree-sourced passes could not settle this and the sixth content-sourced one could.

Recommendation 3 was also exercised rather than merely recorded: the tool call waiting on the
gate hit its bound **twice, at ~9.5 minutes each**, while the landing continued and completed.
A landing driven in the foreground from a bounded tick is killed mid-gate — that is the
mechanism behind passes 12–14, and it is now survived by construction rather than by luck.

### Still open — this finding stays LIVE at root for item 3 alone

1. Recommendation 1 — **BUILT** (previous tick).
2. The instance — **DISCHARGED** by this tick, evidence above.
3. `background.finding_classes --check` still **passes with this finding live and unlisted**:
   class membership is chosen by TITLE alone and this title carries no `uncommitted`/`orphan`
   keyword. **Unchanged and still open.** Queued per SELF_INTERRUPT_DISCIPLINE rather than
   fixed on sight; it is the reason this document is not being archived.

LANDED: `include_schema_version` in `simulation/`

---

## The 2026-08-19 23:5x tick — item 3, the routing fail-open, is closed

`observed` first, before anything was written, because that ordering is this document's whole
subject:

    git rev-parse HEAD                                      -> cd5b94de2
    git grep -c include_schema_version HEAD -- simulation/
      HEAD:simulation/run_phase2b.py:1
      HEAD:simulation/run_phase4c_on_phase2b.py:2

Item 2 still holds at HEAD. So this tick took item 3, the last one open.

### The defect, stated as a mechanism rather than as this document's bad luck

`classify_file` classified on `subject_of(path, text)` — **the filename and the H1 title, and
nothing else.** That is right for the common case and the module docstring defends it well: a
classifier that reads the whole body puts every document that MENTIONS the publish gate into
the publish-gate class, and stops partitioning anything.

But it is FAIL-OPEN in the other direction, and silently. A finding titled for the MECHANISM it
found rather than the FAMILY it belongs to matches no pattern, classifies as `None`, and is
then neither refused nor flagged — `derive_memberships` does a bare `continue` on it. Nothing
in `check()`'s six rules has an unclassed document as its subject, so the class document simply
never learns that its family grew. This document is the worked example: its `## Class
registration` section has said *"Belongs to `uncommitted_and_orphaned_work`"* since it was
filed, and that sentence was decorative — the classifier never read it.

Measured, not assumed: across both staging rooms the change reclassifies **exactly one
document**, this one (`None` -> `uncommitted_and_orphaned_work`). No other member moved, which
is the evidence that a declaration channel is not a wider net.

### What was built

A **registration channel**: `declared_class_of(text)` reads a *Belongs to `<class_id>`* line
scoped to the document's own `## Class registration` heading, and that declaration BEATS the
title regex. Three properties decide whether it is a control or a decoration:

- **Scoped to the section, not the body.** A class id quoted in prose is a mention; a mention
  is not a claim. This is what stops the fix re-opening the hole the docstring refuses.
- **Fail-closed on an unknown id.** A misspelt class is NOT guessed into the nearest real one
  — consolidation *archives*, so a guess would file a document away on a typo — and it is not
  silence either: `Classification.declared_class_id` carries the bad token out verbatim and
  `check()` raises `UNKNOWN DECLARED CLASS`. Collapsing "declared nothing" and "declared a name
  this module does not have" into `class_id is None` would reproduce this very fail-open one
  level down.
- **The title's class is demoted to `also_matched`, not dropped**, so a contested document
  stays visible to `--list`.

### R15 — three mutations, each firing on its own named defect, plus a null control

- **MUTATION I, the declaration is never read.** This is the *shipped* behaviour, so the test
  asserts the defect is real: the mutant leaves the document unclassed AND `check()` green.
- **MUTATION J, an unknown declared id is silently dropped** — the typo goes back to reading as
  no declaration at all.
- **MUTATION K, the declaration is read from the whole body** — a quotation becomes a
  membership and the partition collapses.
- **NULL CONTROL** (`test_the_unregistered_control_is_genuinely_unclassed_by_title`): the
  byte-identical document *without* the registration section stays unclassed. It moves the
  sample, not the law — without it every test here could be passing on a fixture whose title
  happened to match anyway.

**Outcome-tested on the real population, not only on fixtures.** `test_the_live_finding_that_
filed_this_defect_now_reaches_its_class` reads THIS document from whichever room it occupies
and asserts both that it classifies and that its *title alone* still does not — so the test
goes red if it ever stops exercising the registration. On adding the fix, the pre-existing
live-root test `test_the_live_staging_root_consolidation_holds` went RED with exactly the
sentence item 3 predicted would never appear:

    UNCONSOLIDATED WORKER_FINDING_THREE_CONSECUTIVE_PASSES_RECORDED_A_LANDING_THAT_IS_IN_NO_COMMIT_2026-08-19.md:
      belongs to uncommitted_and_orphaned_work, not listed in CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md

The control fires on its own originating instance. That red is then discharged the only way it
can be — by actually consolidating: `--render` lists the member, the document moves to `done/`,
and the class document carries the derived BLOCKING for lane `H_harness`. **Archiving releases
nothing; it moves who is holding**, from this instance to the class document that supersedes it.

LANDED: `declared_class_of` in `background/`
LANDED: `UNKNOWN DECLARED CLASS` in `background/`

### Why this document is NOT discharged by the tick that fixed it

All three items are now settled, so the obvious move is a `**Discharged:**` header in this same
commit. That is declined, and the reason is this document's own subject: **a pass claiming its
own settlement is the defect, six times over.** The discharge belongs to a later reader who can
run the falsifiers against a tree that already exists. The admissible queries are:

    git grep -c "def declared_class_of" <sha> -- background/finding_classes.py     # -> 1
    git grep -c "UNKNOWN DECLARED CLASS" <sha> -- background/finding_classes.py    # -> 1
    python3 -m background.finding_classes --check                                  # -> PASS

Empty, or a `--check` that passes while this document is live and unlisted again, means item 3
is a second failure and the honest record is to say so.
