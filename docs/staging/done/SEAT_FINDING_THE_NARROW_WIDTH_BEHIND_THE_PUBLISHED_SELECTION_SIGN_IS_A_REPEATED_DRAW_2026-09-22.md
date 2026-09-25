**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`

# The narrow width behind the published selection sign is made of repeated draws, and five of the published floor's eighteen are repeats

Pre-registration and full result:
`docs/staging/records/PREREG_THE_ONE_VARIABLE_FLOOR_RUN_AND_WHETHER_ITS_NARROW_WIDTH_IS_A_DEGENERATE_REDRAW_2026-09-22.md`.

Drawn as `the-one-variable-floor-run-that-separates-the-instrument-from-the-seed-set`. The run the
item asked for was **already on disk**, unlanded, in a locked worktree — eleven hours of compute a
prior turn produced and never landed. It is landed by this commit. Running it again would have
cost another eleven hours to re-derive a number already paid for.

## What the run settles, and it settles it cleanly

The one-variable run — next12's twelve seeds at `4e7938f673` — closes the 2x2 the census could not.
Held against the 09-18 pre-registration's own numeric decision rule (`sd_X < 3000` ⇒ the width is
the instrument's), **`sd_X = 1311.96` confirms it**, and the two legs are not close:

| leg | held fixed | moved | F | df | p | sd ratio |
|---|---|---|---|---|---|---|
| instrument | the seeds | the tree | 16.93 | (11,11) | 4.9e-05 | 4.11x |
| seed set | the tree | the seeds | 1.97 | (8,11) | 0.295 | 1.40x |

**The width is a property of the instrument.** The seed set does not move it. That question, open
in `NOISE_FLOOR_PATH`'s comment block since 2026-09-18, is now answered.

## THE FINDING, which is the part nobody asked for

Answering it exposed why the narrow instrument is narrow, and it is not a fact about the world.

**Every family drawn at an old tree repeats a `selection_gbp`. Neither family drawn at a new tree
repeats one. Five families, no exceptions:**

| family | tree | n | distinct | repeated |
|---|---|---|---|---|
| **`folded18_single_arm` — THE PUBLISHED FLOOR** | spliced (old) | 18 | **15** | one 2x, one 3x |
| the nine of 09-10 | `4e7938f673` | 9 | 8 | one 2x |
| the nine of 09-10b | `9f0ab066f` | 9 | 7 | one 3x |
| this run | `4e7938f673` | 12 | 10 | one 3x |
| next12 of 09-17 | `a178b56d6` | 12 | **12** | none |
| next12 at 18327d977 | `18327d977` | 12 | **12** | none |

The three repeating families are the NARROW ones. The two that never repeat are the WIDE ones. The
width disagreement and the repeated draws are one phenomenon, not two.

**`NOISE_FLOOR_PATH` is the worst case, and it is the one the page publishes.** 5 of its 18 draws
are repeats of other draws. The page's NEGATIVE selection sign is stated at 2.50 sems computed
across those eighteen.

### The mechanism is not a re-draw that failed to fire

The obvious reading is wrong and the artefact refutes it on its own rows: `elasticity_redrawn` is
292–296 with `elasticity_held_fixed: 0` on every seed. The re-draw fires. Two mechanisms:

1. **An identical pass.** Seeds 3100003 and 3100012 agree in every recorded field.
2. **A residual pinned across a pass that genuinely differed.** Seed 3100006 drew 292 elasticities
   against 3100003's 296 and a `value_advantage_gbp` of 20,383.78 against 18,757.89 — a materially
   different pass — yet the same `selection_gbp` to fifteen digits. Between those passes
   `value_advantage_gbp` moved 1,625.897961 and `level_advantage_gbp` moved **1,625.897961**,
   identical to the last digit. The arms move in lockstep and the residual is their difference.

Mechanism 2 is the serious one. On this instrument the selection residual is, over part of its
range, **structurally unable to vary** — not small, pinned. A standard deviation taken across draws
that include pinned ones is not an estimate of dispersion in the world; it is an estimate of how
often the instrument pinned.

## What this does and does not establish

- **Does:** the narrow width, and therefore the published NEGATIVE selection sign that rests
  entirely on it, is not established as a property of the world. This is why the finding is
  BLOCKING rather than LATENT — a published figure's instrument is in question, not its arithmetic.
- **Does not:** establish that the wide width is right. Not repeating is not being correct, and no
  claim is made here that 5,398.31 is the true dispersion.
- **Does not:** identify the code change between `4e7938f673` and `a178b56d6` that removed the
  lockstep. That is the next question and it is handed on, not answered.

**The honest position is that the page can state no selection sign from this family** — which is
less confident than what it publishes today, and the less confident direction is the one the
evidence points.

## Why the sign is not withdrawn in this commit

Because withdrawing it is a change to what the page claims, and the seat does not make that change
on a finding a reader cannot see. The order is: publish the evidence, then move the constant. This
commit lands the artefact, this finding and the pre-registration. The census row that carries the
repeat count to the reader, and the `NOISE_FLOOR_PATH` decision that follows it, are the next
increment and are named in the hand-off.

**Reversal:** nothing here changes a published figure. `git revert` of this commit removes an
artefact, two staging documents and a census row; no constant moves.
