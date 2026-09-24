**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The census: two in-class sites, ~20 out, and the record's own account of the extract was wrong

Claim id: `census-git-show-head-controls-that-mean-this-commit`.
Pre-registration, written before the classification:
`docs/staging/records/SEAT_PREREG_HOW_MANY_CONTROLS_READ_HEAD_AND_MEAN_THIS_COMMIT_2026-09-24.md`.
Precedent and the mechanism:
`docs/staging/done/SEAT_FINDING_THE_GATES_EXTRACT_POINTS_HEAD_AT_THE_PARENT_SO_A_CONTROL_READING_HEAD_GRADES_THE_PREVIOUS_COMMIT_2026-09-24.md`.

## What the extract actually holds — measured, not reasoned

Driven through the real `tools.surgical_land.materialise` on a two-commit fixture repo, for a commit
that changes a path the landing NAMES, changes one a merge ABSORBED, and CREATES a third:

| revision | named path | absorbed path | created path |
|---|---|---|---|
| `HEAD:` | parent | parent | **absent** |
| `:` (index) | **this commit** | **parent** | **this commit** |
| disk | this commit | this commit | this commit |

Pinned as a control, against the real builder rather than a restatement of it:
`tests/tools/test_the_gate_extracts_revisions_mean_what_a_control_thinks.py` — five legs, each
reachable, proven by three separate mutations of `surgical_land` that red three different legs
(`add -A` without the pathspec; dropping `read-tree parent`; not writing `.git/HEAD`).

## CORRECTION TO THE RECORD, beside the claim it corrects

The precedent finding wrote that the extract offers *"parent (`HEAD`), result (index), result
(working tree)"* and concluded that *"index-vs-working is equal by construction there"*. **The index
is not the result tree.** `_make_standalone_repo` does `read-tree <parent>`, and `materialise` then
stages only the landing's own pathspec over it. So:

* For a path the landing NAMES, index-vs-working is indeed equal by construction — that half holds,
  and it is the half that rules out the obvious one-line repair for a control about its own subject.
* For a path a MERGE ABSORBED, the index still carries the PARENT and disk carries the result. Those
  two differ. And the path that wedged the value-arms leg — `site/data/publish_provenance.json`,
  arriving by merge — was exactly that kind. The blanket claim is false in precisely the case that
  produced the finding.

The conclusion the precedent reached survives, because an index-vs-working comparison would still
have reproduced the wedge on every fast-forward merge. But the stated reason was wrong, and the
distinction is load-bearing for the repair below: **`:<path>` is a sound "this commit" oracle for a
path the landing names, and an unsound one for a path a merge absorbed.**

## The census

**IN the class** — reads a revision as *this commit* which the gate makes the parent:

1. `site/test_the_book_is_bounded_by_compute_reaches_the_reader.py` — `cat-file -e HEAD:<path>` over
   the measurement artefacts the published compute basis cites. **Red by construction on the one
   commit that ever writes an artefact and its citation together**, which is the only way that pair
   is ever written, and the refusal names the innocent new artefact. **REPAIRED in this landing:**
   asks `:<path>` first, `HEAD:<path>` as the fallback, with the reason beside it. Still refuses a
   citation to bytes in no revision — verified in both directions.
2. `tests/tools/test_generate_value_arms_data.py` — the precedent's instance, already repaired
   2026-09-24. Confirmed still repaired (both sides now read from HEAD, self-consistent).

**OUT of the class, and the reason matters** — these read `HEAD:` and *want* the parent, so they are
correct in the extract AND in a worktree. Ratchets and low-water marks: `tools/level_promotion_gate`
(`:` staged vs `HEAD:` baseline, stated in its own docstring), `tools/orphan_ratchet`,
`tools/canon_drift_check`, `tools/consolidation_rhythm` (the model for the repair above — index for
*this commit*, HEAD for the baseline, index-first-then-HEAD for the ledger),
`tests/architecture/test_static_quality_ratchet` (attribution per file), `tools/startup_anchor_freshness`
(`diff --cached HEAD`), `tools/isolate_hunks`, `tools/refresh_to_head`, `tools/map_assertion_provenance`.

**OUT, self-consistent** — read BOTH sides from HEAD, so they grade the parent and merely lag by one
commit rather than wedging: `tests/tools/test_a_published_surface_is_reproducible_from_its_committed_input`,
`tests/tools/test_a_published_feed_matches_what_its_generator_would_produce`,
`tools/published_feed_regeneration_check`.

**OUT, wrong blast radius** — `background/*` daemons (`launch_liveness`, `staging_rooms`,
`origin_reconcile`, `process_run_complete`, `delivery_lane`, `staging_root_resurrection_watch`,
`tree_divergence`) run against the shared tree and never inside an extract. Also out: every
`tests/**` site whose `HEAD:` read is against a tmp fixture repo it built itself.

## Against the pre-registration: three held, one REFUTED

1. **Count and skew — HELD.** Two in-class against ~20 out.
2. **The survivor is shape (b), presence — HELD.** The sameness instance was the one already
   repaired; the survivor is the cheap `cat-file -e HEAD:<path>` written to mean "is this in the
   commit".
3. **Nothing in `background/` — HELD.**
4. **"The repaired oracle is the INDEX" — REFUTED as stated.** The index is the parent for any path
   the landing did not name, so it is a sound oracle only for a named path. It is sound for the site
   repaired here (a cited artefact is written by the commit that cites it, so it is in that commit's
   pathspec) and it would NOT have been sound for the value-arms wedge. Recorded as a refutation
   rather than quietly narrowed, because the narrowed version is what the next reader needs and the
   wrong general version is what I would otherwise have left them.

## THE RESIDUE, and it is bigger than the class was

**21 occurrences across 5 files carry a branch keyed to "the landing checkout has no commit"** —
`_head_resolves()`, and `pytest.skip("no HEAD here — this is the landing checkout")`, in
`tests/tools/test_a_feed_is_published_from_a_clean_tree.py`,
`test_the_feed_check_can_grade_the_working_tree.py`,
`test_a_published_feed_matches_what_its_generator_would_produce.py`,
`test_a_published_surface_is_reproducible_from_its_committed_input.py` and
`tools/published_feed_regeneration_check.py`.

**That premise is now false.** The extract HAS a resolvable HEAD — leg
`test_the_extract_HAS_a_resolvable_HEAD_so_a_no_HEAD_skip_is_DEAD` is the runnable proof. So every
one of those branches is dead code, and the controls guarding themselves with it do not skip in the
gate: they run, against the PARENT. None of them wedges — they read both sides from HEAD — but each
one's own account of what it does in the gate is wrong, and a dead skip reads like a handled case,
which is worse than an absent one.

Left as a separate landable piece rather than folded in: it touches the whole published-feed control
family, and deciding per site whether the honest answer is "delete the branch" or "grade disk, which
IS the tree in the extract" is a judgement per control, not a sweep. Handed on.
