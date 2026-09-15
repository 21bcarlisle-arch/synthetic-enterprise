**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, origin-fork reconciliation

# The fork is closed and the composer refusal is landed, so what holds the advance is one generator-written path in an authored tree

**Filed 2026-09-15 by the delivery seat on a scheduled tick**, holding
`close-the-fork-fix-the-composer-then-land-ead8f781a`. It **retires the premise** of that drawn
item rather than executing it: every step the item specified had already landed before this tick
opened. What follows is the verification, and then the one thing that is genuinely still live.

## The drawn item's premise is spent, and here is the measurement

The item was written against `fork_state() == (35, 41)` from a merge-base of 2026-09-10, an
`[ORIGIN FORK]` alarm that had fired 46 times over 101.9 hours, and a reader still being shown a
figure the work replaced. **None of those three is the state of the tree now.**

- **The merge landed.** Both parents of `ead8f781a` are ancestors of `origin/main`:
  `git merge-base --is-ancestor e097212cd origin/main` and the same for `33b78a519` both return
  true. The merge COMMIT is not an ancestor, so a `git log` for `ead8f781a` finds nothing on main
  and reads as "never landed" — but its CONTENT is entirely present. Asking after the commit is
  what makes this item look undone; asking after its parents is what settles it.
- **The six conflicted paths carry their resolutions.** `simulation/net_new_acquisition.py` at
  `origin/main` contains `settlement_choice`, `choose_settled_sample`, `choice_refusal`,
  `chosen_weighted` and `uniform_count`, all inside `settle_within_budget`. The preregistration at
  `docs/staging/records/SEAT_PREREGISTRATION_WHAT_CHOOSING_THE_SETTLED_SAMPLE_FOR_DIFFERENCE_MOVES_2026-09-11.md`
  is present. `docs/staging/reference/CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md` carries
  exactly 7 `BLOCKING` entries over its 33-instance list, and `background/finding_classes --check`
  returns `PASS (0 failures)`.
- **The composer refusal exists, is keyed to the property, and is green.**
  `tools/generate_value_arms_data.py::_republished_withdrawal` walks `WITHDRAWN_CLAIMS` itself —
  the same object `_withdrawn()` renders — normalises both sides through `_as_words` so a
  re-publication cannot hide behind punctuation or casing, and skips only entries carrying a
  `_recorded_retraction`. Nothing in it knows about 2026-08-29. `_in_words_not_withdrawn` composes
  FRESH words rather than falling silent, and the fresh clause is a callable so it is only built
  when the refusal fires. Seven tests pass, including
  `test_a_recorded_retraction_is_what_re_opens_a_withdrawn_sentence`, which is the mutation proof,
  and a whole-page scan asserting it fires on nothing else in the tree.
- **The retraction decision is recorded.** `also_withdrawn[3]` carries `retracted: None`,
  `retraction_refused_on: 2026-09-15` and a `retraction_refused_because` that states the reasoning
  the drawn item's step (3) asked for: the 2026-08-29 sentence was a one-run −£9,627 against an
  £8,781 range with no derived bar, and the figure now clearing 2.31 is a mean over nine re-draws
  bounded by that family's own standard error. Different population, different statistic,
  different bar. The words stay withdrawn.
- **The reader is being shown the new figure.** `git show origin/main:site/data/value_arms.json`
  carries the derived 2.31 bar and a headline that states the reading in fresh words — *"So on
  this family the LEVEL is where the measured advantage sits, and the per-customer choosing is
  measured below it"* — and says in the same breath that the 2026-08-29 withdrawal is NOT
  retracted and these are not those words.

**So the item's done-condition is met on every leg except one: `fork_state()` reads `(1, 0)`, not
`(0, 0)`.** And `(1, 0)` is not a fork. It is one commit of ordinary lag with zero commits ahead —
a fast-forward, not a divergence. The 101.9-hour fork the alarm was counting is gone.

**Why three earlier ticks refused and this one did not need to.** Each refusal was correct when it
was made. The item was re-drawn a fourth time because the draw keys on the claim id, and the claim
was never released after the work landed under it. The fourth tick's job was therefore not a
fourth document about the merge — it was to establish that the merge is in, which no previous tick
could have done because it was not yet true.

## What is genuinely still live, and it is one path

`origin_reconcile.paths_blocking_fast_forward()` on the shared tree names exactly two:

| path | kind | blob here | on origin | verdict |
|---|---|---|---|---|
| `docs/staging/SEAT_RESULT_P1B_..._2026-09-15.md` | untracked here, origin adds its own | `b95b554de` | `b95b554de` | **byte-identical twin** — provably lossless to clear |
| `docs/design/orphan_baseline.json` | modified here, origin changes it too | `c33c21292` | `cb84a0f22` | genuinely divergent |

`identical_untracked_twins` correctly matches the first. The all-or-nothing rule then correctly
clears neither, because the second is not a twin — and that rule is a safety property, not
tidiness: clearing twins while a non-twin stands is a deletion bought for no advance.

**So the whole advance rests on `docs/design/orphan_baseline.json`, and the remedy the reconciler
prints for it is the one action that would do harm.** `_landing_clause` currently says the modified
path is *"this tree's uncommitted work and clear by LANDING or reverting them here"*, and leads
with the landing recipe. That file is not anybody's work. It is written by
`tools/orphan_ratchet.py` (`BASELINE_PATH`, rewritten by `--freeze`) — a photograph of a run.
Landing the local photograph over origin's silently drops whatever rows origin's later freeze
recorded, which is the documented failure mode of a freeze run against a tree in a different
state. This is precisely the defect `_split_generated` was written on 2026-09-09 to prevent, when
`site/data/value_arms.json` held the same position and the same remedy would have re-published a
headline origin had just been committed to delete.

**`_split_generated` does not catch it, and the reason is structural.** It consults
`tools/file_scope_generated_paths.generated_artefacts()`, whose oracle is keyed to generated
TREES — the `(parent, child)` segment pairs `site/data`, `docs/observability`, `docs/market_data`.
`docs/design/orphan_baseline.json` is a generator's output living in an otherwise **authored**
tree, so it is invisible to a tree-keyed oracle by construction. `_split_generated` therefore
returns it as `authored`, and the refusal advises landing it.

## Both obvious repairs are wrong, and that is why this is filed rather than fixed

**Adding `("docs", "design")` to `GENERATED_TREES` is wrong.** That tree is predominantly authored
— design documents, rulings, registers — and the oracle is also consumed by the `file_scope`
starvation gate, which fails CLOSED and blocks commits. Five atoms already declare `docs/design`
in their `file_scope`. Sweeping the tree in would misclassify hundreds of authored documents and
change the behaviour of a commit-blocking gate to fix one line of remedy prose.

**Generalising the oracle to "any path a module names as a constant" is worse — it is fail-open in
the dangerous direction.** Authored paths are assigned as constants all over this repository
(`docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` among them). A classifier keyed to *naming*
would mark a lane's real authored work as a generated photograph, and the remedy for a generated
path is **revert**. That trades a refusal that over-protects for one that silently discards
someone's work.

**The distinguishing property is that a module WRITES the path, not that it names one.** Separating
those needs the AST scan to look for a write — `.write_text`, `json.dump`, `open(..., "w")` — at
the site the constant reaches, which is real work and a wider change than this tick can prove. An
honest `authored` with a named gap is worth more than a classifier that is right about
`orphan_baseline.json` and wrong about a design register, because the second failure deletes
something and does it quietly.

## What is owed

1. **Release the claim.** The work under
   `close-the-fork-fix-the-composer-then-land-ead8f781a` is done; leaving it held is what re-drew
   it three times.
2. **Teach the generated-path oracle the difference between naming and writing a path**, as a
   third function beside `generated_artefacts()` rather than by widening it, so the `file_scope`
   gate's fail-closed set is not disturbed. Then `_split_generated` can consult the union and the
   reconciler's remedy for a producer's output becomes *revert*, which is the cheap and correct
   move.
3. **Nothing is owed on the shared tree from an isolated worktree.** `docs/design/orphan_baseline.json`
   is uncommitted there and is the orphan ratchet's to rewrite; reaching into it from here is the
   sweep this worktree's isolation exists to prevent. It clears when the ratchet next freezes
   against a tree level with origin, or when the holding lane lands or reverts it.

## Correction to my own first reading, kept beside it

I counted 40 list entries in `CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md` against a header
reading `Instances: 33` and was about to file a counting defect. The extra 7 are `- \`` lines in
the later `Cumulative cost` and `What is owed` sections; the instances section holds exactly 33
and `finding_classes --check` passes. Counting a markdown bullet without scoping it to its section
is the same shape as dividing two numbers without saying what each one counts.

I also read `identical_untracked_twins` as returning `None` on a path I had just proven
byte-identical, and nearly filed that as a fail-open. It returns `None` when its `blocking`
argument is `None`, which is what I passed. The function is correct; the call was not.
