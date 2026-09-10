**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery (`the-selection-leg-has-a-mean-and-not-enough-draws-to-state-its-sign`)

# PRE-REGISTRATION — what nine more seeds do to the selection leg's mean, and whether its sign becomes stateable

**Filed 2026-09-10, scheduled tick, BEFORE the run is launched.** The launch command is at the
bottom of this document and the artefact it writes does not exist at filing time. This is the
document R12 asks for: the selection leg is the one figure on the page that carries the thesis, its
family is nine draws wide, and the temptation this file exists to remove is running seeds until one
of them agrees.

---

## The family this extends, exactly as it stands

`docs/observability/value_cycle_ab_s1_noise_floor.json`, and the identical promoted copy at
`..._20260909b.json` that `generate_value_arms_data.CURRENT_WORLD_NOISE_FLOOR_PATH` points at.
Both are read; both must move together, and that pair is part of what "done" means here.

| | |
|---|---|
| seeds | `11111, 22222, 33333, 44444, 55555, 66666, 77777, 88888, 99999` |
| `redraw_scope.mode` | `all` (the undecomposed floor — the only mode whose spread bounds the published figure directly) |
| world digest | `39a192ce04c1eda8` |
| producing commit | `c066c114b4746d9fa6a16da1848ef1f2c610c9e1` |
| generated | 2026-09-09T15:17:31Z |
| `selection_gbp` rows | `+1260.93, −3036.25, +494.45, −2644.35, +286.06, +1090.00, −2482.58, −2719.11, −1952.63` |
| mean | **−£1,078.17** |
| stdev | £1,810.50 |
| sem | £603.50 |
| `sems_from_zero` | 1.787 against 1.96 needed |
| sign | **not stateable** |

## What is being run, decided before the answer

**Nine new seeds: `111111, 222222, 333333, 444444, 555555, 666666, 777777, 888888, 999999`.**

The seed list is mechanical on purpose — the six-digit repdigits continuing the five-digit
repdigits already drawn. There is no choice inside it to make, and therefore no choice to make
badly after seeing a result.

**Nine and not two.** The artefact's own arithmetic says `seeds_needed_to_state_a_sign: 11`. Running
exactly two more seeds and stopping is the worst available design, and it is worth naming why
rather than leaving it to be inferred: 11 is the *minimum* n at which the CURRENT mean would cross
1.96, so a family stopped at the first n that crosses is a family whose stopping rule is
"it crossed". Nine more takes the family to 18, where the current mean would sit 2.53 errors from
zero — margin enough that the crossing, if it happens, is not an artefact of where I stopped.

**THE STOPPING RULE IS FIXED NOW.** These nine seeds are the whole run. Whatever comes back is what
gets published, in either direction, including "still cannot tell at n=18". No tenth seed, no
second batch, and no re-run under a new stamp if the answer is unwelcome. If a later seat wants a
larger family it files its own prediction first.

**The arm is not touched.** No pricing constant, no elasticity, no threshold moves in this work.

## The predictions

Stated as bands, with the reasoning visible so a reader can see which assumption failed if one does.
All are conditional on the fold being legitimate (see the refusal conditions below).

**P1 — the mean of the nine NEW seeds alone.** Centre −£1,078; 95% band **[−£2,261, +£105]**.
This is the current mean ± 1.96 × the current sem, which is what the new nine's own mean is
distributed around if they are drawn from the same population as the old nine. A new-nine mean
outside this band is the interesting outcome, not the boring one — it says the nine on disk were
not typical.

**P2 — the mean of the folded family at n=18.** Centre **−£1,078**; 80% band **[−£1,670, −£486]**;
95% band **[−£2,138, −£18]**. The folded mean is the average of a known number and an unknown one,
so its predictive spread is about £461 — narrower than the new nine's alone, because half of it is
already measured.

**P3 — the standard error at n=18.** Centre **£427**; 95% band **[£288, £817]**. Centre is
£1,810/√18. The band is the χ²(8) interval on the standard deviation carried through, and it is
deliberately wide: nine draws is a poor estimate of a spread, and the sem inherits that.

**P4 — does the sign become stateable?** **More likely than not, and not confidently: I put it at
about 60%, and the direction, if it is stated, will be NEGATIVE.** Stateable needs the folded mean
to be at least 1.96 sems from zero — with P2's centre and P3's centre, that threshold is £836 and
the centre estimate is £1,078, which clears it. But P2's 80% band has its upper edge at −£486,
which does not clear it, and P3's band alone can move the threshold from £564 to £1,601. So the
honest reading of my own numbers is that this run probably resolves it and quite possibly does not.

**P5 — a POSITIVE stateable sign.** Predicted at **under 2%**. This is the falsifier that matters
most. The page currently publishes a single realised draw of **+£319**, on the opposite side of zero
from its own family's centre. If the folded family comes back with a stateable POSITIVE sign, then
the nine seeds on disk were badly unrepresentative and every reading built on them — including my
own reasoning above — needs re-doing rather than patching.

**P6 — what will NOT move, and it must be proved and not assumed.** `level_share_of_advantage` is
a ratio the same rows compute, currently 1.069 ± 0.105. I predict its mean stays inside
**[0.98, 1.16]**. This is not "conceptually separate" from the selection leg — it is arithmetically
entangled with it, since selection and level partition one advantage. So this is a weak prediction
about magnitude and I am recording it to be graded, not to be leaned on.

## What would refuse the fold entirely

The new run happens on **today's tree**, not `c066c114b`. That is not free and the fold is not
automatic. Three conditions, checked against the new artefact before anything is folded:

1. **World digest must equal `39a192ce04c1eda8`.** If the new run reports a different world, the
   two families are measurements of different worlds and NO fold is legitimate — the new nine get
   published as their own family beside the old, and the page says so. This is the one that voids
   every prediction above.
2. **`redraw_scope.mode` must be `all`** and `clock` must be `settled-realised`. A floor in another
   mode does not bound this figure.
3. **No seed may appear twice** across the union. A duplicated row raises `n` and shrinks the sem
   while adding no observation, and the artefact it produces is well-formed, so nothing downstream
   could tell.

**A KNOWN IMPURITY, ADMITTED RATHER THAN DISCOVERED LATER.** Even with the digest equal, the folded
family mixes two code trees. `generate_value_arms_data.py`'s own constant comment records the size
of that: on the three seeds two trees shared, the same seed in the same world returned
`selection_gbp` differing by **+£38.96 to +£61.38**. If that shift applies to the nine old rows and
not the nine new, it moves the folded mean by roughly £25 — about 4% of one standard error, against
a family spanning £4,297. I judge that tolerable for the sign question and I am writing the figure
down here so the judgement is checkable rather than asserted. It is NOT tolerable to discover it
after publishing; that is why it is above the result and not in a footnote.

## How this gets graded

Beside the result, in the same document, whichever way it goes — including the outcome where the
prediction was simply wrong. A prediction filed after the answer is not a prediction, and a
prediction never graded is the same thing one step later.

Done for the Lane 0 item is: the family on disk is bigger than nine; the page either states a sign
or states plainly that it still cannot **with n=18 in front of the reader**; and this file carries
its grade.

## The launch

```
python3 -m tools.run_arms_rerun --stamp <stamp> --leg floor-all \
  --seeds 111111,222222,333333,444444,555555,666666,777777,888888,999999 --launch
```

`--launch` and not a hand-rolled background job: a job started from a bounded tick dies with the
tick's cgroup, which is how `arms-rerun-20260908` was lost. `--level-arm --redraw-mode all` come
from the `floor-all` leg definition, so the flags the selection leg needs cannot be forgotten.
No `--ignore-headroom`: `floor_run_headroom_refusal()` returns `None` at filing time, so the guest
holds this run on its own terms and there is nothing to override.

At ~44 minutes per seed (nine seeds took 6h36m on 2026-09-09) this run is expected to take about
six and a half hours and will cross several ticks.
