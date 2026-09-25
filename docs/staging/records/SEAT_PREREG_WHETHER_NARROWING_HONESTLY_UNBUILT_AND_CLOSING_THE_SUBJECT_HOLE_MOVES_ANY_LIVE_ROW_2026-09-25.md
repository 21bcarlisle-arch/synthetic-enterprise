**Severity:** INFO · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: does the guard fix move any live row's cause, and in which direction?

Written BEFORE running the classifier over the live map. Subject: the change to
`tools/level_zero_contradicted_by_its_own_controls.ungradable_causes` made this turn —
`HONESTLY_UNBUILT` narrowed from "no named SUBJECT on disk" to "no named FILE on disk", and a new
eighth cause `SUBJECT_NEVER_WRITTEN` for a named subject that is absent and unknown to git.

## What I predict, and why each half is a separate bet

**Half one — the `HONESTLY_UNBUILT` narrowing moves NOTHING.** Predicted: 0 rows change. The
finding this repairs measured the branch as LATENT: both live members (`G14`, `G15`) name a file
that is genuinely absent, so the narrowing cannot reach them. The narrowing only bites a row whose
non-directory entries are ALL controls, and no such row was found on the live map. If this half
moves a row, the finding's latency claim was wrong and that is the more interesting result.

**Half two — `SUBJECT_NEVER_WRITTEN` is a bet I have NOT already measured.** Its route is a row
naming at least one file that IS on disk and at least one subject that is absent and unknown to
git. Nothing in the prior turn's census asked that question, so I am predicting into the dark.
Prediction: **between 0 and 3 rows**, and every one of them comes out of `NOTHING_IN_THE_ROW` —
because that is the only cause the new branch can take a row away from. A row moving out of
`POINTER_ROT` or `CONTROL_NEVER_WRITTEN` would mean the branch is mis-ordered and I would have to
say so.

**The direction that would refute the whole change:** any row moving INTO `HONESTLY_UNBUILT`, or
any row losing a cause without gaining one. Either is the false-silence this repair exists to
prevent, reintroduced by the repair.

## How it is measured

Both readings in ONE process — `HEAD`'s copy of the module and the working copy's, over the same
`docs/design/maturity_map.yaml` and the same tree — because a before/after taken as two runs over
a live shared tree is two variables. The counts and the per-row diff go in the result file beside
this one, whichever way they come out.
