# The 20261004h arms are the 20261004r arms, and the selection leg now carries a direction

*Worker, 2026-10-04. Closes Lane 0 item `publish-the-20261004h-heads-arms-pair`.*

**Prediction (filed before the run, in the item):** digest stays `cdba75ebb9197b33` and the value
advantage moves by less than the 24.1k..27.5k re-draw spread.

**Result: held, and more strongly than predicted.** Both `20261004h` artefacts (re-taken at
committed origin `efe1b7dee`) are identical to the `20261004r` pair (run at `96517e68c` plus the
uncommitted QEP refit) in every field except `generated_at`, `producing_commit`, and two floats in
`bound_attribution.realised_margin_movement` that differ in the 15th significant digit (summation
order). Value advantage £20,888.60 at both; floor selection spread £6,549.94..£13,598.20 at both.

So `company/pricing/default_belief.py` (own_book as the default) and
`background/live_payment_triad.py`, which `f5ee6000b` named as able to move the arms, did not
move them in this world. That is an equivalence on this book and these seeds, not a proof they are
inert on every book.

**What the page now says.** With the run at HEAD's import closure, `_code_since_the_run` finds no
moved path, so the code withdrawal lifts, `is_heads_code` is true, and
`current_world.selection_leg.resolved` becomes `true`: all three re-draws are positive. The front
door's `data-selection-verdict` moves to `resolved`, the first time it has said so. The sentence
reports a direction on three draws, with no size. The floor's own SEM test still reads "not
distinguishable from zero" (3.8 SEMs against a bar of 4.30 at n=3), and the selection residual is
one account's renewal roll (2026-09-27 record), so "not yet the finding" stays.

No substrate exemption is argued: no path in the run's import closure differs between `efe1b7dee`
and the publishing HEAD. The three `96517e68c` exemptions are now dormant (their `run_commit` no
longer matches) and are left for the record.
