**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

**Knowledge:** none — this is a harness/provenance state, not domain understanding.

# The pair move's floor is still not on disk at 21:33Z, and the "land the part you finished" half-move is the one its own pre-registration measured as harmful

Filed against the Lane 0 item *"pair-move the 20260910 run and its floor"*
(claim `pair-move-20260910-after-the-floor-lands`). **The pair move is still NOT done, and for the
same reason as the last two turns: the floor artefact does not exist.** This document records the
third successive re-measurement of its arrival, and one thing no prior document says — that the
standing instruction to land a partial increment has, on this particular item, a measured cost.

---

## 1. Premise re-measured 2026-09-10T21:33Z — UNSPENT, and the source path is still absent

The item names its floor source as
`/var/tmp/se-floorrun-20260910/docs/observability/value_cycle_ab_s1_noise_floor_20260910.json`.

```
$ ls /var/tmp/se-floorrun-20260910/docs/observability/*20260910*
value_cycle_ab_s1_floor_partition_probe_20260910.json
value_cycle_ab_s1_three_arm_20260910.json
$ find /var/tmp -maxdepth 4 -name 'value_cycle_ab_s1_noise_floor_20260910*.json'
(no output)
```

**No such file, in that tree or any other.** Every dated file in that worktree carries mtime
`Sep 10 15:50` — the checkout time — so the tree is a clean extract and the run has written nothing
into it yet. The producer is alive and has never emitted the artefact:

```
PID 1072649  Rsl  15:50  347:47  python3 -m tools.run_value_cycle_ab
  --noise-floor-seeds 11111,22222,33333,44444,55555,66666,77777,88888,99999
  --redraw-mode all --out docs/observability/value_cycle_ab_s1_noise_floor_20260910.json
/proc/1072649/cwd -> /var/tmp/se-floorrun-20260910
```

The `--out` path is **relative**, so it resolves under that cwd. The item's source path is correct;
it is merely not yet written. `run_value_cycle_ab` writes its artefact once, at the end.

**The premise is unspent.** The canonical pair on disk is still the 09-09 pair, byte-identical to
its dated originals — so nothing has landed by another route:

| canonical path | md5 | identical to |
|---|---|---|
| `value_cycle_ab_s1_three_arm.json` | `0c478778…` | `…_three_arm_20260909c.json` |
| `value_cycle_ab_s1_noise_floor.json` | `24da1d28…` | `…_noise_floor_20260909b.json` |

## 2. The arrival time, re-measured for the third time — ~23:05Z, not ~22:40Z

Counted directly from the producer's own log (`/var/tmp/longjob-noise-floor-20260910.log`, fd 1 and
2 of PID 1072649) in the unit the previous turn's CORRECTION established as the real one — a
**decade sweep**, nine seeds × three arms = **27 sweeps**. Each completed sweep prints exactly one
`OUTCOME:` line, so the count needs no conversion and no arithmetic over a counter that resets:

```
$ grep -c '^OUTCOME:' /var/tmp/longjob-noise-floor-20260910.log
22
```

**22 of 27 complete (81%)** at log mtime `21:32:25Z`. Start was `14:50Z`.

| reading | elapsed | sweeps | min/sweep | implied finish |
|---|---|---|---|---|
| 17:56Z (previous turn) | 186 min | 10.63 | 17.5 | ~22:40Z |
| **21:33Z (this turn)** | **403 min** | **22** | **18.3** | **~23:05Z** |
| marginal, between the two readings | 217 min | 11.37 | **19.1** | ~23:08Z |

**~23:05Z, and the job is decelerating slightly** — the marginal rate between the two readings is
19.1 min/sweep against a 17.5 min/sweep average up to the first. Five sweeps remain.

This is the third arrival estimate on this run and each has been later than the last: every document
before 2026-09-10T17:56Z says ~19:50Z, the drawn item says ~22:40Z, and the measurement says
~23:05Z. **The estimates are not converging on a stable answer — they are being revised in one
direction, which is what a systematically optimistic conversion looks like.** Both prior estimates
were taken early in the run and extrapolated a rate; this one is taken at 81% and the extrapolation
covers only the last five sweeps, so it is the least leveraged of the three. It is not thereby
right, and a fourth reading should be taken rather than trusted from here.

## 3. The half-move this item is eligible for is measured as HARMFUL, and that is not written down anywhere the drawer can see it

The standing instruction on every drawn item is *"if it is bigger than one turn, land the part you
finished."* On this item, the part that is finished is the **run** half of the pair — and landing it
alone is exactly column **B** of the item's own pre-registration
(`docs/staging/records/SEAT_PREREG_WHAT_THE_20260910_PAIR_MOVE_CHANGES_AND_WHICH_PAIR_THE_BOUNDS_COME_FROM_2026-09-10.md`),
measured in memory on 2026-09-10T15:2xZ:

| | A. status quo (live today) | **B. run alone** | C. pair move |
|---|---|---|---|
| `contrast_bounds` shape | 7 keys | **3 keys** (`available`/`reason`/`what_this_costs`) | 7 keys |
| `contrasts` | 3 | **— refused —** | 3 |
| `staleness_caveat` | `None` | **FIRES** | `None` |
| `is_it_available_today` | `false` | `false` | **`true`** |

Under B the page withdraws every directional claim it currently makes and states the price in its
own words: *"no contrast on this page can have its direction stated until the noise floor is re-run
on the book published above."* **B is strictly worse than doing nothing.** The published page loses
three contrasts and gains a caveat, and it stays that way until the floor lands.

So on this item the honest increment is *not* the finished half. There is no partial data landing
available at all: the dated `…_three_arm_20260910.json` is **already tracked and clean at `HEAD`**
(`git diff --stat HEAD` on it is empty), so even the "also land the dated artefact" leg is already
spent. The four-path commit the item describes is **atomic by construction** — three of its four
paths cannot move until the fourth exists.

**This is the general shape, and it is worth more than the instance:** *"land the part you
finished" assumes the parts are independently valuable, and a pair move is precisely the class where
they are not.* A mixed-key canonical pair has cost this project a published fabricated figure before
(`a553f2f96`: *"the mixed-key split makes the page publish a fabricated 0% twice, under a sentence
asserting a split that was not made"*). The instruction is right in general and wrong here, and
nothing in the drawn item's own text tells the next drawer that — it says "land the part you
finished" in the same breath as "land all four paths in ONE commit".

## 4. What I did instead, and what is left

Landed: this finding. Nothing else could be landed without making the page worse.

**What is left is one command, once the artefact appears**, and it needs no further judgement — the
mechanism is settled by the pre-registration above, not by anything a future turn has to re-derive:

```
cp /var/tmp/se-floorrun-20260910/docs/observability/value_cycle_ab_s1_noise_floor_20260910.json \
   docs/observability/value_cycle_ab_s1_noise_floor_20260910.json
cp docs/observability/value_cycle_ab_s1_noise_floor_20260910.json \
   docs/observability/value_cycle_ab_s1_noise_floor.json
cp docs/observability/value_cycle_ab_s1_three_arm_20260910.json \
   docs/observability/value_cycle_ab_s1_three_arm.json
python3 -m tools.generate_value_arms_data
python3 -m tools.surgical_land -m "<message>" \
  docs/observability/value_cycle_ab_s1_noise_floor_20260910.json \
  docs/observability/value_cycle_ab_s1_noise_floor.json \
  docs/observability/value_cycle_ab_s1_three_arm.json \
  site/data/value_arms.json
```

**From a worktree on `origin/main`, and all four paths in one commit.** The run half must not land
without the floor half.

**One thing the next turn must check rather than assume:** the pre-registration's column C is a
*probe* — it reused the 09-09 floor's seed rows, so it establishes the provenance branches and
nothing about the numbers. The real nine-seed floor will carry different rows and different widths,
and `contrasts` may well come out with a different sign or a wider band than the page shows today.
**A≠C on numbers is not established, and the probe must not be quoted as if it were the result.**
