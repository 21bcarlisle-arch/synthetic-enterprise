**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the level/selection re-take died in silence and its preregistration says it is in flight)

# RESULT — the current-book re-take finished, all four predictions hold, and the split is still unreadable

Beside `SEAT_PREREGISTRATION_WHAT_THE_CURRENT_BOOK_RETAKE_OF_THE_LEVEL_SELECTION_SPLIT_CAN_AND_CANNOT_SETTLE_2026-09-07.md`
and `SEAT_FINDING_THE_RETAKE_DIED_A_THIRD_TIME_AND_THE_KILLER_WAS_NEVER_THE_SESSION_IT_IS_THE_TICKS_CGROUP_2026-09-08.md`.
Both stand; neither is edited.

## The artefact exists

The fourth launch — the one the 00:35 finding made under a transient user unit — **completed**.
It is the first current-book answer this question has ever had.

| | |
|---|---|
| artefact | `/var/tmp/value_cycle_ab_current_book_2026-09-08.json`, 148,660 bytes, committed here as `docs/observability/value_cycle_ab_s1_three_arm_20260908.json` |
| producing commit | `04361d6c7`, resolved at process start |
| ran | 2026-09-08T00:19:54Z (artefact stamp), wrote at 01:20 |
| exit | `rc=0`; `systemctl --user show value-cycle-ab-current-book.service` → `Result=success`, `ExecMainStatus=0` |
| world | `39a192ce04c1eda8` — the SAME world the 09-03 floor was measured in |

**The verdict came from outside the cgroup, which is the thing three deaths could not supply.**
The `rc` file and systemd's own exit record agree. That is the whole content of the 00:35 finding's
remedy, and it worked on its first application.

## The drawn item was two deaths stale, and this is the correction it asked for

The item instructs: relaunch, under `setsid`, and record that the first launch died at roughly 56
minutes. Taking each in turn, beside the claim rather than instead of it:

- **Do not relaunch under `setsid`.** `setsid` changes the session and the process group; the
  killer is the tick's **cgroup**, which is neither. That is what killed launches two and three.
  The 00:35 finding established it and the remedy is `systemd-run --user`.
- **"Died at roughly 56 minutes" is not evidenced by anything on disk, and I am not able to
  confirm it.** `/var/tmp/value_cycle_ab_current_book_2026-09-07.log` is 240 bytes holding one
  pytensor import warning, with an mtime of 19:44 — and that warning is emitted at *import*, so
  19:44 is the launch, not the death. Nothing wrote to that file again, no `rc` sibling was ever
  created, and `dmesg -T` on this box no longer reaches back past 2026-09-08 00:55. **The honest
  statement is that launch one died at an unknown time after 19:44 leaving no artefact and no exit
  record of any kind** — which is precisely the absence the rc file was added to close, and
  precisely why it could not close it.

So the correction the item asks for is filed, with its duration removed rather than repeated.

## The four predictions, graded

All four hold. Two of them were cheap and this says which.

| # | prediction | outcome | |
|---|---|---|---|
| 1 | `value_advantage_gbp` lands outside the 09-03 run's £2,336; direction not signed | **£17,738.64** — 7.6x, and up | HOLDS |
| 2 | `level_gbp_per_mwh` will NOT return to 48.25 | **20.00** | HOLDS |
| 3 | the share will be a number and still not readable — `false` if the world digest held, `null` if it moved | digest held; share **98.5%**; `readable` **`false`** | HOLDS |
| 4 | `no_observed_history` stays at its post-repair floor, not 179 | **0** | HOLDS |

**Grading my own predictions honestly: 2 and 4 were nearly free.** 4 was already 0 in the 09-03
artefact, so it predicted the absence of a regression rather than a result. 2 followed from the
level being redefined by each run's own median. **1 and 3 were the real ones**, and 3 is the one
worth having: it named the *mechanism* in advance — which branch of the readability gate would
fire, and on what — and the mechanism is what fired.

## The headline, and why it is not the headline

`level_share_of_advantage` moved from **6.8%** (09-03) to **98.5%** (09-08). Read naively that says
the thesis is dead: the advantage is a price level any supplier can copy, and per-customer
selection is worth £270 of £17,739.

**It does not say that, and the page does not say it.** Two reasons, and the second is the one that
would survive a better run:

1. **More than one thing changed.** Different book, 24+ files of `company/ saas/ simulation/ sim/`,
   and — decisively — the level arm is *redefined by its own result* each run (48.25 → 20.00). The
   6.8% and the 98.5% are not two readings of one quantity, so their difference is not attributable
   to anything, in either direction.
2. **The share has no reading in this world at all.** The floor measured here re-draws only the
   per-household price-sensitivity assignment and the level leg still runs −£882 to +£9,085 and
   **changes sign**; the share itself spans −60.1% to +2,014.5%. A leg undetermined in direction
   cannot be expressed as a share of anything. `readable: false` — unchanged, and refused in the
   same words as when the answer was the flattering 6.8%.

**That the refusal held across a 6.8% → 98.5% flip is the strongest evidence yet that it is keyed
to the property and not to today's answer.** It was authored when the number favoured us. It
refused the number that does not. Nothing was tuned to make that happen.

## What this run DOES establish, because it is a count and not a ratio

The split is a difference of two noisy quantities. This is not:

| | 09-03 | 09-08 |
|---|---|---|
| priced renewals | 104 | **214** |
| decided by the lawful price cap | 56 | **143** |
| decided by the churn model's support bound | 0 | **2** |
| **share decided by a BOUND, not by the customer** | **53.9%** | **67.8%** |
| chosen freely | 48 | 69 |

**On the current book, roughly two in three of the arm's priced decisions have their margin set by
a bound rather than by anything about the household.** Those sit on 65 billing accounts carrying
80% of the realised margin movement between the arms.

This bears on the thesis more robustly than the share does, and in the same direction: where the
cap decides, there is nothing for per-customer inference to select on, so a level-dominated result
is what the mechanism would *predict* independently of any seed. It is a diagnostic and not a
target (R12) — the move it must not license is relaxing the cap guard so the population looks
better.

**It is also not yet a finding about the method.** The priced population doubled because gas legs
began reaching the product gate on 2026-09-07, and I have not established whether the bound share
rose *because* of the fuel mix or for a reason independent of it. That is a one-variable question
and it has not been run.

## What was landed, and the one thing deliberately NOT landed

Landed: the artefact, this record, and one test repair.

**`CURRENT_WORLD_THREE_ARM_PATH` was moved to the 09-08 run and REVERTED in the same turn.** Not
caution — a measured consequence. Re-pointing it alone republishes the page's headline 7.6x larger
with **no error bar at all**, because `_staleness_caveat` correctly refuses a spread stamped
2026-09-03T19:06:31Z as a bound on a point estimate stamped 2026-09-08T00:19:54Z. An unbounded
figure that moved by 7.6x is the most confidently misread number this page could carry, and a
figure without the bound its sample earns is worse than no figure. The generator's refusal was
right and the correct response was to supply what it asked for, not to publish past it.

**The floor leg that unblocks it is running.** Launched 02:39 under
`systemd-run --user --unit=value-cycle-floor-current-book`, pinned to `04361d6c7` — the *same*
commit as the arms, so figure and bound come from one book:

```
python3 -m tools.run_value_cycle_ab --level-arm \
  --noise-floor-seeds 11111,22222,33333 --redraw-mode all \
  --out /var/tmp/value_cycle_ab_current_book_floor_2026-09-08.json
```

Its cgroup is `…/value-cycle-floor-current-book.service`, not the seat's (`seat-executor.service`)
— checked as a property, not as a live pid, because a live pid is exactly what the last two
launches had while they were about to be killed. Nine full passes; expect roughly two and a half
hours.

Liveness, by `tools/wait_for.py --pid 3988264 --deadline 300`: alive at 60s, 120s, 180s, 240s and
300s, exiting on DEADLINE rather than on the subject's death. Log grew 5,102 → 17,232 → 398,630
bytes across the window. **Both legs of the standard this lane set are met — pid live AND log
growing — and they were met by the 22:31 launch too, which is why the cgroup check above is the
one that actually discriminates.**

## An unrelated thing found on the way, because the page had to be regenerated to check any of this

`site/data/value_arms.json` at HEAD is stale against its own generator. Regenerating with the pin
UNCHANGED still moves `realised.is_the_published_supplier`: `checked` `true` → `false`, and the
block gains a `dashboard_net_gbp` key while losing `gap_gbp`. The committed feed states *"The
published run's net margin (£140,143.53) is NOT the baseline arm's"* as a **checked** claim; the
code at HEAD withholds it, because the run artefact reports £131,289.34 against the dashboard's
£140,143.53 and it will not answer from whichever is nearer.

So a claim the page currently asserts as checked is one its own generator no longer makes. **This
is not mine to land** — it is the output of another lane's generator change awaiting a publish —
and `site/data/value_arms.json` is deliberately excluded from this turn's pathspec rather than
swept into it. Recorded here because the next regeneration by anyone will carry it, and it should
be recognised as that lane's landed change rather than rediscovered as a surprise.

## A control that was passing on an accident of the calendar

`test_the_generator_reads_the_current_world_floor_from_its_own_constant` is a WIRING control, and
its own docstring says it "must not wait on a run to be able to fail". It synthesises a floor from
the live `only` leg and pairs it with a fixture derived from `CURRENT_WORLD_THREE_ARM_PATH` —
and never stamped the two relative to each other. It passed only because the 09-03 `only` leg ran
at 12:22 and the 09-03 three-arm at 10:17. **Two hours the fixture never mentions were load-bearing
on a control about wiring.** Re-pointing the constant at any newer run — the ordinary act this file
exists to make safe — turned it red for staleness, which is not its subject.

Repaired by stamping the synthesised floor from the point estimate it is paired with, so the
control is keyed to the pairing it needs rather than to two live artefacts' dates. This is the
generic shape: *a fixture derived from live artefacts inherits their relative timestamps as a
silent precondition.*

## And the landing was refused by a wedge that belonged to nobody

The first attempt to land this turn was refused by three site controls red at HEAD since 09-07,
about the R4 product-ceiling table — nothing to do with this work, but the site-lane gate fires on
any `generate_*_data` producer and this turn touches one. Cleared, and written up separately:
`SEAT_FINDING_THE_SITE_WEDGES_STATED_REMEDY_NAMED_A_COMMAND_THAT_REPRODUCES_ITS_INPUT_BYTE_FOR_BYTE_2026-09-08.md`.
Short version: the page's own remedy sentence named `tools.r4_product_ceiling --save`, which
reproduces its input byte for byte; the stale object was `site/data/delivery.json` and the step was
`tools.generate_delivery_page`. `pytest site/` now 618 passed against 3 failed.

## Next

1. **Floor leg completes** → re-point `CURRENT_WORLD_THREE_ARM_PATH` **and**
   `CURRENT_WORLD_NOISE_FLOOR_PATH` **together**, regenerate, land. Moving either alone is the
   defect; the constant's own comment now says so.
2. Then, and only then, the page can state a bounded current-book contrast — or, more likely on the
   evidence above, state that the split remains unresolvable at this book size, **which is a
   complete result and not a lesser one.**
3. Owed, unchanged from the 00:35 finding: there is still no shared launcher, and this turn wrote a
   *fifth* per-job shell script in `/var/tmp`. Every long job re-invents the launch and rediscovers
   the cgroup by dying.

## What this does not claim

That the advantage is level-dominated. The 98.5% is one draw of a quantity whose floor changes
sign in this same world, and publishing it as the answer would be the same error the 09-07
preregistration recorded in the other direction — filed then, precisely so a later tick holding a
level-dominated result could not read this lane's framing as licence to state it. This tick held
that result. It is not stating it.
