**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, the
generated-path oracle

# PRE-REGISTRATION — what one frame of interprocedural reach adds to the write-keyed oracle

**Filed:** 2026-09-15 by the delivery seat, BEFORE the measurement.
**Claim:** `teach-the-write-keyed-oracle-to-follow-a-path-into-a-helper`
**Result:** `docs/staging/SEAT_RESULT_THE_WRITE_KEYED_ORACLE_NOW_FOLLOWS_A_PATH_ONE_FRAME_INTO_A_HELPER_AND_TWO_OF_THE_EIGHT_IT_FOUND_ARE_NOT_PHOTOGRAPHS_2026-09-15.md`

---

## The question

`tools/file_scope_generated_paths.written_artefacts()` landed 2026-09-15 keyed to the write SITE,
and its own docstring names the gap it does not close:

> THE NAMED GAP. A path handed to a helper (`_write_json(BASELINE_PATH, data)`) and written one
> frame down is NOT found -- following that needs interprocedural reach this does not attempt.

Every producer that factors its write into a `_write` helper is therefore still classified
**authored**, and `origin_reconcile._split_generated` still offers to LAND its output — the exact
defect the oracle was built for, surviving in whatever fraction of producers use a helper. It
degrades in the safe direction, so nothing reports it.

**The measurement:** the write-keyed set with one frame of same-module reach, differenced against
the set without it.

**Measured before any change:** `len(fs._write_reached_paths())` = **147**.

---

## What is predicted, before looking

1. **The addition is non-empty.** If one frame of reach adds nothing, the gap named in the docstring
   is an EQUIVALENCE in this tree, not a defect — and that is the finding, not a failure. Recorded
   here so the flattering reading cannot be assumed after the fact.
2. **The addition is small — I predict fewer than 40 paths, and more than 2.** 147 is the current
   set; a helper frame that added a hundred would mean the resolver is binding something it should
   not, and I would treat that as a refutation of the implementation rather than a discovery.
3. **Every added path is attributable to a real write site.** This is the leg that matters. The
   remedy a consumer applies to a generated path is REVERT, so a wrongly-added path is a standing
   offer to throw away a lane's real work. I will check each addition individually, by reading the
   helper and the call site, and any path I cannot attribute comes back OUT rather than being
   argued in.
4. **No path currently on the authored side that a human authored is added.** Specifically
   `docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md`, `docs/design/DIRECTOR_CANON.md` and
   `docs/design/maturity_map.yaml` must not appear in the addition by a new route. (The last two are
   carved out by `WRITTEN_BUT_NOT_REPRODUCIBLE`, so the check is against `_write_reached_paths`,
   the raw scan, where the carve-out cannot mask a mistake.)

## What would refute the approach

- An addition containing a path whose module only READS it — the naming-vs-writing boundary broken
  one frame down instead of at the top.
- An addition that is large and diffuse. The safe failure mode of this oracle is missing a path;
  the expensive one is claiming one. If the diff does not read as "these are producers', obviously",
  the resolver binds too loosely and the right move is to narrow it, not to widen the carve-out.

## What done means

Named here so it is not chosen after the answer is known:

- one frame, **same-module only** — a call whose callee is a `def` at module level in the same file;
- the helper's parameter bound to the caller's resolved argument, and the helper's write
  destination re-resolved in that binding, so `path.write_text(...)`, `Path(path).write_text(...)`
  and `(path / "f.json").write_text(...)` all follow;
- a parameter REBOUND inside the helper is not followed — `path = SOMETHING_ELSE` means the write
  is not to the argument, and following it anyway is how a resolver starts manufacturing paths;
- **not** transitive: a helper calling a second helper is two frames and stays out;
- the addition measured, printed, and attributed path by path in the result record;
- an R15 control that fires on the defect — a fixture where the helper frame is the only route to
  the path — with its partner on the naming side of the boundary.

---

*A prediction filed after the answer is not a prediction. The result goes beside this one, whichever
way it falls.*
