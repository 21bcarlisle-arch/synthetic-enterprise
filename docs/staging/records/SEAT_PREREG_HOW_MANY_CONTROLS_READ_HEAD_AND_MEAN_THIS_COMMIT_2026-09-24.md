**Severity:** ADVISORY · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# PRE-REGISTRATION: how many controls read `HEAD:` and mean *this commit*

Claim id: `census-git-show-head-controls-that-mean-this-commit`.
Written BEFORE the per-site classification below was run, so the answer can refute it. Precedent and
the mechanism: `docs/staging/done/SEAT_FINDING_THE_GATES_EXTRACT_POINTS_HEAD_AT_THE_PARENT_SO_A_CONTROL_READING_HEAD_GRADES_THE_PREVIOUS_COMMIT_2026-09-24.md`.

## The class, stated before looking

`tools/surgical_land._make_standalone_repo` writes the PARENT commit into the extract's `.git/HEAD`
while the working tree is `result_tree` — the tree the commit would create. So inside the gate, and
only there, `HEAD:<path>` is the commit BEFORE the one being graded.

A site is IN the class iff it reads `HEAD:` and the thing it wants is a property of the commit being
made. Two sub-shapes:

* **(a) SAMENESS** — asserts `HEAD:<path>` equals what the tree/live code says. Red by construction
  on any commit that legitimately changes that path.
* **(b) PRESENCE/CONTENT** — asks whether a path is in "the commit" by asking HEAD. Red by
  construction on any path the commit ADDS, and green for a path the commit DELETES.

A site is OUT of the class when it wants the parent *on purpose* — a ratchet or low-water mark
("did this commit remove/worsen X"). Those are correct in the extract AND in a worktree, and they
are the majority of `HEAD:` readers here. Also out: sites reading BOTH sides from HEAD, which are
self-consistent and merely lag by one commit; and daemons, which never run inside an extract.

## The predictions

1. **The count is small and the shape is skewed.** Between 1 and 4 in-class sites across the whole
   control population, against ~20 out-of-class `HEAD:` readers. If the census returns more than
   ~6, the classifier has drifted to "reads HEAD" rather than "means this commit" and the finding
   is about my instrument, not the tree.
2. **The in-class sites are shape (b), not shape (a).** Shape (a) is what wedged the value-arms leg
   and was repaired on 2026-09-24, so the surviving instances should be presence-flavoured — the
   cheap `cat-file -e HEAD:<path>` written to mean "is this in the commit".
3. **No in-class site lives in `background/`.** Daemons run against the shared tree, so the class
   cannot reach them; if one turns up there I have mis-stated the mechanism's blast radius.
4. **The repaired oracle is the INDEX, not a different commit.** `:<path>` is the tree the commit
   would create in the extract, and the staged state in a worktree — the same meaning in both. The
   precedent's warning that index-vs-working is equal by construction bites COMPARISONS, not
   presence questions, so it does not forbid this.

Recorded before the classification, and the result — including whichever of these is refuted — goes
beside it in `SEAT_RESULT_...` under the same claim id.
