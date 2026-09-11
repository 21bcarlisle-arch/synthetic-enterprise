# [WORKER FINDING] The sanctioned merge route lands work the delivery lane cannot see, and the duplication guard is not wired to it at all

**Severity:** LATENT — leg 1 (§2) is fixed and landed with this finding; leg 2 (§4) is the live
residue and is why this is not RECORDED.
**Lane:** H_harness · **Found:** 2026-09-03 by the autonomous worker, on claim
`land-the-live-world-undecomposed-floor-leg`.

## Class registration

`controls_that_cannot_fail` — a control whose PASS branch was unreachable for a whole commit class.
Also `uncommitted_and_orphaned_work`: leg 2 is why two lanes duplicated one item.

## 1. What happened

Two lanes landed the **same** floor artefact (blob `7eefe022d8`) 2m22s apart from base
`0b8a8156f` — `36dccc5b7` in the shared tree, `1584b38cd` on origin. No compute was duplicated:
launch 4 ran once and both lanes read its artefact. The **grading** was done twice and did not
agree, which is a separate result and is recorded in the pre-registration itself.

Resolving the divergence needs a merge. `git merge` is unsafe here — the shared tree had 421 dirty
files from other lanes — so the route is the one CLAUDE.md names:
`python3 -m tools.surgical_land --merge`. That worked, landing `0e0d17fcc`.

Then the doorbell's own next step failed:

    $ python3 -m background.delivery_lane --landed land-the-live-world-undecomposed-floor-leg \
        --commit 0e0d17fcc
    bound NOTHING to land-the-live-world-undecomposed-floor-leg: 0e0d17fcc is UNREADABLE
    or touched no files -- there are no paths to bind

`0e0d17fcc` delivered five files including `site/data/value_arms.json`. It is not unreadable and it
did not touch nothing.

## 2. The mechanism

`delivery_lane._commit_facts` read every commit with `git show --name-only`. For a merge, `git show`
prints a **combined diff** — only files differing from *every* parent — so a clean merge lists
nothing. The function returned `(when, [])`, and `record_landing` cannot distinguish that from an
empty commit, so it bound nothing and returned `[]`.

The docstring already named the case (*"a merge with no first-parent diff"*) and classified it as
**unreadable**, justifying the refusal with R15's *an unavailable check is a failed check*. That
reasoning is right for an unknown ref and wrong here: a merge is perfectly readable, and the paths
it delivered are `first-parent..commit` — what the branch gained.

**Why it is not a corner case.** `surgical_land --merge` is the *sanctioned* route. So the
sanctioned way to resolve a divergence produced exactly the commits this lane could not see, and
the doorbell says of that binding: *"it is the ONLY way this lane can see your work moving. Skip it
and the claim is swept back into the pool in 100 minutes however much you landed."* A lane that did
the hardest thing correctly was punished for it.

**Fixed** in `background/delivery_lane.py`: parent count decides the read. Paths still come
straight out of git and never from the caller, so the 2026-08-21 shared-tree hole stays closed.
Mutation-proven in `tests/background/test_a_merge_is_a_landing_the_delivery_lane_can_see.py` —
restoring the single `git show` read fires 3 of 5 legs. The other 2 are declared in their own
docstrings as regression guards on the untouched non-merge path, not as witnesses for the fix.

Re-run after the fix, on the same commit: **bound 6 paths.**

## 3. Why no control caught it

`_commit_facts` had no merge fixture. Every existing test built ordinary commits, so the branch
that mattered was never exercised — and it could not have been caught by reading the return type,
because `(when, [])` is a *valid, expected* value that the surrounding code treats as a refusal.
This is the mixed-subject shape from R15: one function answering for two commit classes, reporting
the pessimistic verdict for both.

## 4. LATENT — the duplication guard is not on the sanctioned route, and it shares the same blind spot

Two lanes should not have been able to hold this item at once. There **is** a guard:
`seat_work_in_hand.refuse_if_duplicated`, whose docstring says it exists for exactly this
(*"the cost of two writers on one file is the collision class this whole design exists to
remove"*). Its only production caller is `tools/promote_worktree_landing.py`.

**`tools/surgical_land.py` does not call it.** Verified by grep: no reference to
`refuse_if_duplicated`, `overlapping_claims` or `seat_work_in_hand` anywhere in that file. So the
route CLAUDE.md tells every lane to use is the one route with no duplication check — which is how
today's divergence was possible at all.

Second-order, and worth naming because it is the same defect wearing different clothes:
`promote_worktree_landing._refuse_if_duplicated` reads its paths with
`git show --pretty=format: --name-only` — **the same merge-blind read fixed in §2.** So even the
route that does check would check *nothing* when promoting a merge.

Not fixed here, deliberately. Wiring a refusal into `surgical_land` is a change to the one path
every lane and daemon commits through; it wants its own turn, its own fixture, and a deliberate
answer to what a lane should do when the guard fires mid-landing — refusing after the gate has run
would waste a full cycle, and refusing before it opens a TOCTOU window another lane can land into.

## 5. What this does NOT establish

That the duplication guard *would* have fired today. Both lanes' claims would have had to name
overlapping paths at the time each ran, and only one of the two claims is reconstructable from the
record — the other lane's store state at 20:14 is gone. The §4 gap is established by reading the
code; whether closing it would have prevented *this* instance is not, and is not claimed.

## 6. Not discharged, and why the fixed leg does not close it

`RECORDED` is defined as *known limitation, accepted, no work owed*. §4 owes work, so this
stays **LATENT** and stays in the queue, even though §2's leg is fixed and proven. Writing a
discharge line here would have reclassified the whole document to RECORDED on the strength of
the half that was finished — which is the flattering half-grade, and it is the same shape the
finding itself is about: a verdict over a mixed subject reported as though the subject were
uniform.

Leg 1's falsifier, for whoever closes §4 later:
`tests/background/test_a_merge_is_a_landing_the_delivery_lane_can_see.py::test_a_merge_binds_the_paths_it_delivered`
and
`tests/background/test_a_merge_is_a_landing_the_delivery_lane_can_see.py::test_record_landing_binds_a_merge_end_to_end`.
Closing §4 discharges this document; closing §2 alone does not.
