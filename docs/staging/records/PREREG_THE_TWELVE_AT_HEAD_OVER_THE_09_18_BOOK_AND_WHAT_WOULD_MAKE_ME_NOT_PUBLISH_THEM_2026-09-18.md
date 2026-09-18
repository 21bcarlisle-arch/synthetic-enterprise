**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value_arms_floor_family

# PRE-REGISTRATION — the twelve at HEAD over the 09-18 book, and what would make me NOT publish them

**Filed:** 2026-09-18 16:20 local (15:20Z), with the run **not yet launched** and its artefact
non-existent. Nothing below was written after a seed was readable.
**Claim id:** `re-run-the-noise-floor-over-the-09-18-book-so-the-error-bar-stops-refusing`

---

## The premise, re-measured before starting (the drawn item asked for this)

`18327d977` is an ancestor of `origin/main`, so the comment repair it carries has landed. The RUN
it says is owed has not. Measured on this worktree at `18327d977`:

```
NOISE_FLOOR_PATH = value_cycle_ab_s1_noise_floor_folded18_single_arm_20260917.json  2026-09-17T21:39:28Z
THREE_ARM_PATH   = value_cycle_ab_s1_three_arm.json                                 2026-09-18T05:43:40Z
_staleness_caveat(floor, arms) FIRES.
```

**The premise is live and the work is not spent.**

## What the re-measurement added, and it is not what the item says

The item says the floor is *older* than the arms. It is, and that is the weaker half. The two
artefacts also answer, from their own payloads, that they are over **different books**:

| | settled billing accounts in window |
|---|---|
| published floor, all 18 seed rows | **164** |
| 09-18 arms, `control_arm` / `value_arm` / `level_arm` | **154 / 155 / 154** |

`_staleness_caveat`'s published refusal says *"the noise floor names no book identity of its own,
so nothing here can show that this spread was drawn over the decisions the figure is made of"*.
That sentence is **false on the live pair**: the floor names its book eighteen times over, and
what it names is not the book the figure comes from. The stamp proxy happens to refuse this pair
for a different reason, so the false clause costs nothing *today* — and it is the exact fail-open
the docstring itself predicts ("a floor measured on a DIFFERENT book that happens to be stamped
later still clears this guard silently"). That is filed separately and is not this run's subject.

## The run

Launched into its own detached worktree at `18327d977`, via `background.launch_long_job`:

```
tools.run_value_cycle_ab --noise-floor-seeds 3100001..3100012 --redraw-mode all
                         --out docs/observability/value_cycle_ab_s1_noise_floor_next12_at_18327d977.json
```

**The seeds are next12's, deliberately, and that is the whole design.** Three families then exist
on ONE seed set, differing only in the tree that drew them:

| family | tree | status |
|---|---|---|
| `next12_20260917` | `a178b56d6` (salvage, superseded instrument) | landed, n=12, sd £5,398.31 |
| `next12_at_4e7938f673` | `4e7938f673` (the instrument the published eighteen was drawn on) | **in flight**, PID 2977626, launched 13:56 local |
| `next12_at_18327d977` | `18327d977` (HEAD — the instrument that drew the 09-18 arms) | this run |

One variable, three points, and the series chains. A fresh seed set would have re-confounded the
instrument with the draw, which is the confound the 09-18 write-up said was owed.

**ETA: 2026-09-19 08:20Z ± 1h30m.** Priced against a COMPLETED SIBLING — `next12_20260917`, same
seed count, same `--redraw-mode all`, same `--redraw-key elasticity`, same machine: 15h56m from
`exec`. Not against a progress marker; the last floor ETA on this atom was seven hours wrong
because a twice-per-leg marker was counted once. Contention is priced as near-zero: 16 cores,
load 3.47, the one rival run is single-threaded.

## The predictions, and they are falsifiable

1. **The stamp guard goes quiet.** `generated_at` lands after `2026-09-18T05:43:40Z`, so
   `_staleness_caveat` returns `None` on `(this floor, THREE_ARM_PATH)`. This is near-certain and
   is worth nothing on its own — it is arithmetic on two clocks, not evidence about the book.
2. **The book matches.** Every seed row reports `billing_accounts_settled_in_window` in
   **154–155**, the arms' own across-arm range. This is the prediction that matters, and it is the
   one that can embarrass me: if it lands at 164, the book is a property of something other than
   the tree and my reading of the 164/154 gap above is wrong.
3. **The width replicates next12's, not the published eighteen's.** sd within £3,500–£7,500, i.e.
   closer to £5,398 than to £1,632. Reasoning: next12's book was already the 154 book, and the
   published eighteen's was the 164 book, so I am attributing the 3.31× dispersion gap to the
   BOOK (ten fewer settled accounts, ~65 priced instead of ~66) rather than to the instrument.
   **If this lands near £1,632 I am refuted and the instrument is the cause.**
4. **No sign.** `selection_distinguishable_from_zero` is `false`, at fewer than 2.0 sems.

Prediction 3 is the one I would bet against myself on, and it is stated at the level of a
number so it cannot be re-read after the answer.

## The decision rule, fixed now

- **Publish (move `NOISE_FLOOR_PATH`) only if predictions 1 AND 2 both hold.** A floor that is
  newer but over the wrong book is the fail-open above, bought with sixteen hours.
- **If 2 fails**, the artefact is filed and `NOISE_FLOOR_PATH` does not move, and the finding is
  that the book is not tree-determined. The page keeps refusing. A refusal on the page is a
  result; a quiet page over the wrong book is not.
- **3 and 4 do not gate publication either way.** They are readings, not targets. In particular a
  WIDER floor that withdraws the selection sign is not a reason to prefer the narrower published
  one — choosing a floor by the answer it gives is the defect this atom already has a write-up
  for, and it does not stop being one because the wider family is mine.
- **R12: this is not a cue to re-run until a seed agrees.**

## What "done" means for the drawn item

The item is DIRECTION and carries no exit test, so: done is `_staleness_caveat(floor, arms)`
returning `None` on a pair that a book comparison ALSO clears. This turn delivers the launch, this
pre-registration, and the book-identity repair. The publication itself needs the run, and the run
outlives this turn by sixteen hours — so it hands off with its own DO NOT DRAW BEFORE stamp.
