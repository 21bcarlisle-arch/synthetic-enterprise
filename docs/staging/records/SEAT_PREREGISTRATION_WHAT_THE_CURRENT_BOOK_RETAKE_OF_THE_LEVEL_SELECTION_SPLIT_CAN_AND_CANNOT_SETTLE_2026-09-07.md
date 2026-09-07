**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the published arm comparison says selection and the newest run says level)

# PREREG — what the current-book re-take of the level/selection split can and cannot settle

The run is in flight. Every number below was written before any of its numbers existed.

## The run

| | |
|---|---|
| command | `python3 -m tools.run_value_cycle_ab --level-arm --out /var/tmp/value_cycle_ab_current_book_2026-09-07.json` |
| launched | 2026-09-07, `setsid`, its own session — not the tick's |
| pid at launch | 3046198 |
| tree | `/var/tmp/se-valuearms-20260907`, a **locked** worktree detached at `153e90cd0` |
| log | `/var/tmp/value_cycle_ab_current_book_2026-09-07.log` |
| artefact | written OUTSIDE both trees on purpose — a worktree clean deletes anything inside one |

The worktree is locked because this run takes hours and the reaper takes detached work at ninety
minutes. It is pinned to `HEAD`, not to the working tree: "the current book" has to mean something
reproducible, and 891 files of other lanes' uncommitted work is not it.

## Why any run on disk had to be re-taken

Not because the older figures were measured wrongly. Because none of them is on this book:

| run | producing commit | files changed since, in `company/ saas/ simulation/ sim/ run_value_cycle_ab` |
|---|---|---|
| `value_cycle_ab_s1_three_arm.json` (08-31) — feeds `realised.split` | `fe4df178b` | **88** |
| `..._s1_three_arm_20260903.json` — feeds `current_world` | `ace28fa44` | **60** |
| `..._gas_admitted_2026-09-07.json` — no surface | — | — |
| `..._leg_id_fixed_2026-09-07.json` — no surface | `08ec389fb` | **24** |

The instrument moved too, not just the book: `tools/run_value_cycle_ab.py` is **+445/−60 lines**
since the 09-03 run and **+49/−13** since `leg_id_fixed`. So "re-run it" was the only available
move — there is no artefact to repoint the generator at.

## The premise this corrects, before the run answers anything

The drawn item says *"The site currently tells the director the advantage is choosing"*. **It does
not.** `site/data/value_arms.json` → `current_world.composition` carries
`readable: false`, and the refusal beside it is keyed to a property, not to today's answer:

> across 3 re-draws of the same quantity in this same world — same book, same code, only the
> per-household price-sensitivity draw moved — the level leg runs −£882 to £9,085 and **changes
> sign**.

`value_cycle_ab_s1_noise_floor_20260903.json`, world `39a192ce04c1eda8`:

| seed | `level_advantage_gbp` | `level_share_of_advantage` |
|---|---|---|
| 11111 | −882.45 | −60.1% |
| 22222 | +1,733.38 | +71.2% |
| 33333 | +9,085.08 | +2,014.5% |

The page publishes 6.8% as one draw with that refusal attached, and states in terms that the 78.7%
panel beside it is a different world, date and commit and may not be differenced against it.

**So the alarm that we are publishing the flattering opposite is not supported, and neither is
93.9%.** `leg_id_fixed`'s 93.9% is a single draw of a quantity whose own floor spans −60% to
+2,014% in the same world. Publishing it as the answer would be the same error in the other
direction. Recorded here so that a later tick, holding a level-dominated result, cannot read this
lane's framing as licence to state it.

## The prediction

One variable this run does **not** hold fixed, and it is the reason no two of these artefacts may
be differenced: `flat_at_level` takes its level from **each run's own realised median margin**
(54.25, 48.25, 48.50, 20.00 £/MWh across the four runs above). The level arm is redefined by its
own result. This run redefines it again.

1. **`value_advantage_gbp` lands outside the 09-03 run's £2,336.** Twenty-four files of book moved
   under it, including the writer-3 gas repair. I cannot sign the direction and will not pretend to.
2. **`level_gbp_per_mwh` will NOT return to 48.25.** The gas leg is priced now; the median margin
   is taken over a population that was three-quarters electricity when 48.25 was measured.
3. **`level_share_of_advantage` will be a number, and it will still not be readable.** This is the
   load-bearing prediction and it is a prediction about the *page*, not the run — see below.
4. **`no_observed_history` stays near its post-repair floor and does not return to 179.** If it
   does, something in the 24 files reverted the id repair and that is the finding, not the split.

## What this run CANNOT settle, and it is the thing that was actually asked for

`_composition_in_this_world` decides `readable` from the **floor's** seed rows, not from the
three-arm run: it needs ≥2 re-draws of the level leg in this world and it needs them to agree in
sign. A single three-arm run carries no seeds. **So this run alone cannot make the page state a
split, however its own share comes out** — it will move the point estimate and leave the refusal
standing, for the same correct reason.

Which refusal, precisely, is itself a prediction. If this run's `world_identity` is still
`39a192ce04c1eda8`, the 09-03 floor is admitted on its digest, its three sign-changing seeds are
read, and `readable` comes out **`false`**. If the world digest has moved, the floor is not
admitted at all, there are no seed rows to test, and `readable` comes out **`null`** — *not asked*,
which is a different state and the weaker one. Either is correct behaviour; confusing them is not.

DONE, as drawn, therefore needs a **second** run that is not yet launched:
`--noise-floor-seeds 11111,22222,33333 --redraw-mode all` on this same book, at three full passes
per seed. It is deliberately not launched beside this one: two hour-scale simulations on a 24 GB
guest is how a leg gets OOM-killed, and an OOM-killed leg writes no artefact and reads exactly like
one still running.

**And the honest possibility is that the answer stays "we cannot tell".** If the level leg still
changes sign across the re-draw on the current book, then the split is not a quantity this world
can resolve at this book size, and *that* — published, with the seed range beside it — is the
complete result. It is not a lesser outcome than a number.

## What would refute each of these

1–2 are refuted by the artefact's own `level_vs_selection` block. 3 is refuted if `readable` comes
out `true` off a single three-arm run, which would mean the readability gate is reading seeds from
somewhere other than the current-world floor — a defect in the gate, and a bigger finding than the
split. 4 is refuted by `renewal_funnel`.

## Next tick picks up here

- `/var/tmp/value_cycle_ab_current_book_2026-09-07.json` exists → copy into
  `docs/observability/`, point `CURRENT_WORLD_THREE_ARM_PATH` at it, regenerate, land.
- log ends without the artefact → the run was killed; relaunch the same command. The tool writes
  only at the end, so there is nothing to resume from.
- then launch the floor leg, which is what actually decides whether the page may state a split.
- `git worktree unlock /var/tmp/se-valuearms-20260907 && git worktree remove …` once the artefact
  is copied out — it is locked against the reaper, not for keeps.
