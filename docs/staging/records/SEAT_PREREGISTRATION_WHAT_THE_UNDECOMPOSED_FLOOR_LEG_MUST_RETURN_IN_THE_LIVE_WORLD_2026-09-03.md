**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# What the undecomposed floor leg must return in the live world

*Delivery seat, 2026-09-03, lane-0, claim `the-baseline-was-beaten-in-a-world-that-no-longer-exists`.
Filed while `se-noise-floor-all-20260903b` is queued and has produced nothing. §1 is measured; §2 is
the prediction and its answer is not in hand.*

---

## 1. Measured — the two decomposition legs, like-for-like, same mode, two worlds

Both 2026-09-03 legs carry `world_identity.digest` **`39a192ce04c1eda8`**, which is the live world
and the same world as the three-arm run published under `/capabilities/`. Same seed family
(11111 / 22222 / 33333) on all four.

| leg | 2026-08-31 (old world) | 2026-09-03 (live world) | move |
|---|---|---|---|
| `only` — redraw the priced roster only | stdev **3,776.27**, range 7,547.97 | stdev **5,923.04**, range 10,983.77 | **+56.85%** |
| `except` — redraw everything but the roster | stdev **0.00**, range 0.00 | stdev **0.00**, range 0.00 | unchanged |

The `except` leg returns three byte-identical seeds in both worlds: redrawing every household
outside the hand-authored roster moves the selection figure by exactly nothing. That is the
decomposition's attribution — essentially all of the floor's variance sits on the priced side —
reproduced independently in the live world rather than carried over from the old one.

**P4 is NOT graded by this.** P4 was written about `selection_gbp_spread.stdev` on
`value_cycle_ab_s1_noise_floor.json`, which is the **`all`** leg, and that leg was OOM-killed at
11:27Z (`ExecMainStatus=9`) and wrote nothing. `only` and `all` are different modes and grading one
against the other's prediction is the leg-swap this claim exists to stop. P4 stays pending. What §1
establishes is that the floor's direction of travel on the mode that *can* be compared is **wider**,
which is P4's direction on a different leg.

## 2. The prediction, filed before the `all` leg returns

In the **old** world the `all` and `only` legs returned the *same* selection spread to every digit
printed — stdev 3,776.2691398368634 and range 7,547.969953000022 on both — while `except` returned
zero. That is not a coincidence: `only` redraws exactly the households that produce priced
decisions, `except` redraws the rest, and the rest contribute no variance, so the undecomposed leg
has nothing to add to the priced one. If that structure is a property of the instrument rather than
of the old world's particular numbers, it must hold again.

> **P6 — the undecomposed leg reproduces the `only` leg.**
> **Predicted:** `value_cycle_ab_s1_noise_floor_20260903.json` returns
> `selection_gbp_spread.stdev` of **5,923.04 ± 5%**, and `range` near **10,983.77**.
> **Refuted if:** it lands outside 5,600–6,250, or if `except` and `all` stop reconciling to
> `only` the way they did in the old world.
> **If refuted**, the reading is about the INSTRUMENT and not about the world: it would mean the
> decomposition's premise — that the unpriced side contributes no variance — is a fact about the
> old world's draw and not a property of the book, and the decomposition would need re-deriving
> rather than re-running.

> **P7 — the current contrast still cannot be resolved, and now by a wider margin.**
> The live-world `value_advantage_gbp` is **£2,335.87**. Against a live-world floor near £5,923 that
> is 0.39× — comfortably inside.
> **Predicted:** `selection_distinguishable_from_zero` stays **false** in the live world.
> **Refuted if:** the re-run resolves it, which on a floor that widened would need explaining.

**Neither figure may be published until the `all` leg lands.** £2,335.87 over £5,923.04 is a ratio
between a contrast from the live world and a spread from the live world, so it *would* be a
quantity — but it is the wrong leg. The `only` leg's spread does not bound the published figure;
`redraw_scope` on the `all` artefact says so in its own words: *"every household re-drawn — the
undecomposed floor, and the only mode whose spread bounds the published figure directly."* Quoting
the `only` leg because it is the one that finished is the same move as quoting the old world's floor
because it is the one on disk.

`tools/generate_value_arms_data._current_world_contrast` refuses the verdict in code until a floor
naming this world is on the page, and it will keep refusing after these two legs land, correctly,
because neither is the undecomposed one.

## 3. What is owed next

*Rewritten 2026-09-03 16:38 BST. The unit named below is the THIRD launch of this leg; §3 as first
written named `se-noise-floor-all-20260903b`, which is dead. Probing that name now returns
`inactive` and reads as "the leg died again" when the live leg is running normally — the phantom-
outage shape, from a stale document rather than a clock.*

### The leg that is actually running

| | |
|---|---|
| unit | `se-floor-all-20260903c.service` — **check `systemctl --user is-active` before concluding anything** |
| started | 2026-09-03 16:07:03 BST, ~2h25m, expect ~18:32 BST |
| worktree | `/var/tmp/se-floorrun-20260903` at commit `1d821e12b` |
| `--out` | `/var/tmp/se-floor-artefacts/value_cycle_ab_s1_noise_floor_20260903.json` |

**The `--out` path is outside every git worktree on purpose.** Leg A *succeeded* at 15:18:37 BST and
`ensure_worktree` deleted its artefact at 15:35:25 with `git clean -qfd`, 17 minutes later. Fixed at
`ff8e27ce3`; the number was not recoverable. **An absent artefact is exactly what a run still in
progress looks like** — do not read absence as failure, and do not launch a fourth run.

### Grading constraint on P4

The **5,923.0446** stdev quoted in earlier doorbells came from the artefact `ensure_worktree`
deleted. It is not recoverable evidence and nothing may be graded against it. **Grade P4, P6 and P7
against this run's artefact only.** §1's table above stands — it was measured from the `only` and
`except` legs, which are on disk.

### The chain is already armed — do not re-audit it

Checked 2026-09-03 16:35 BST by feeding `_current_world_bound` the live-world `only` leg twice: once
as it is, and once with `redraw_scope.mode` set to `all` as a **shape** stand-in for what the running
leg will write. The real `only` leg is refused on the leg guard (`floor_leg: only`); the stand-in is
admitted and yields a bound on `value_advantage_gbp` with `n=3`. So the artefact's schema clears
every guard in `_current_world_bound`, including the last one — `_seed_spreads` / `_spread_for`,
which is downstream of all the others and is the guard that could have let a 2h25m run land without
moving the page.

*No number from that stand-in is a measurement of anything and none may be published: it is the
`only` leg wearing an `all` label, which is the exact leg-swap this claim exists to stop. It
establishes that the plumbing admits the shape, and nothing else.*

`CURRENT_WORLD_NOISE_FLOOR_PATH` already points at
`docs/observability/value_cycle_ab_s1_noise_floor_20260903.json`, so **step (c) is a file copy, not a
code change.**

### How P6 must be graded — filed 2026-09-03 17:12 BST, before this run's artefact exists

**The digits cannot tell the two legs apart in this world, so grading on them is unsafe.** The
journal for the deleted leg B (`redraw mode all`) and the `only` leg on disk agree on every figure
either one printed:

| | leg B journal, `mode all`, 15:18:37 | `..._only_20260903.json`, on disk |
|---|---|---|
| seed 11111 | `+2,349.68` | `2349.683596000017` |
| seed 22222 | `+700.32` | `700.3180280000088` |
| seed 33333 | `-8,634.09` | `-8634.087115000002` |
| sd / range | `5,923.04` / `10,983.77` | `5923.0446166138645` / `10983.77071100002` |

That is P6's premise doing exactly what P6 says it should: `except` contributes zero variance, so
the undecomposed leg has nothing to add to the priced one. **It also means a grader who opens the
wrong file gets the right number.** So P6 and P4 are graded by pasting, from the artefact this run
writes, `redraw_scope.mode` (must be `all`), `generated_at` (must be after 16:07 BST today), and
the `--out` path it was read from — *and only then* the figures. A grading that quotes digits
without those three has not distinguished the legs and does not count.

> **P8 — this run reproduces leg B's seed rows.**
> **Predicted:** `selection_gbp_spread.stdev` = `5923.0446166138645` and the three seed
> `selection_gbp` values equal the `only` leg's to full precision.
> **Refuted if:** any seed row differs at all — which would mean the floor is not deterministic
> given seed and world, and would put every floor figure on this page back in question.
> **This prediction is NOT blind and must not be scored as if it were.** It is retrodiction from
> leg B's console output, which is in the journal. Its only value is as a determinism check; it is
> not evidence for P6, and P6's own grade stands on its originally-filed ±5% band.

**The leg guard is contingent, not redundant — do not "simplify" it when this lands.**
`_current_world_bound` is about to admit an artefact whose numbers are identical to the `only`
leg it refuses. The next reader will see a guard rejecting a file for carrying the same figures as
one it accepts and read it as pedantry. It is not: the identity holds *because* the unpriced side
happened to contribute zero variance in this world, which is a measured result of the `except` leg
and not a property of the instrument. In a world where `except` is non-zero the two legs diverge
and the guard is the only thing standing between the page and a bound 1.4x too narrow.

### The decompose command, in full

    python3 -m tools.run_value_cycle_ab --decompose \
      docs/observability/value_cycle_ab_s1_noise_floor_20260903.json \
      docs/observability/value_cycle_ab_s1_noise_floor_only_20260903.json \
      docs/observability/value_cycle_ab_s1_noise_floor_except_20260903.json \
      docs/observability/value_cycle_ab_s1_three_arm_20260903.json \
      --contrast value_advantage_gbp

**`--contrast` is not optional in practice and the instruction that commissioned this work omits
it.** It defaults to `selection_gbp` for continuity with the artefacts written before the flag
existed, while the page's headline figure and bound are `value_advantage_gbp`
(`generate_value_arms_data.PAGE_FIGURE_CONTRAST`). Running the bare `--decompose` would split a
different quantity from the one the page publishes and label it as the page's — which is `1df22e3bd`,
*"the decomposition never said which contrast it split, and always split the wrong one"*, reappearing
through the flag added to fix it.

### Bind the landing to THIS claim id — the doorbell names one that is claimed nowhere

> **REFUTED 2026-09-03 17:40 BST, by the turn this section was written to steer. Do not follow it.**
> The operative instruction is the correction immediately below this block. This text is kept
> because a wrong prediction beside its result is the only evidence the check was designed before
> its answer was known — not because any of it is still actionable.

*Filed 2026-09-03 17:35 BST, while the leg is still running, so it is in front of the turn that
lands rather than behind it.*

The scheduled-tick doorbell commissioning this work ends with an explicit instruction, twice:

> `python3 -m background.delivery_lane --landed pick-up-the-relaunched-undecomposed-floor-leg`
> … it is the ONLY way this lane can see your work moving. Skip it and the claim is swept back
> into the pool in 100 minutes however much you landed.

**`pick-up-the-relaunched-undecomposed-floor-leg` is claimed nowhere.** It is absent from
`.delivery_lane_claims.json`, absent from `.seat_work_in_hand.json` (which is `{}`), and a grep of
the whole tree returns no occurrence of the string outside the doorbell itself. Asked directly:

    pick-up-the-relaunched-undecomposed-floor-leg
      -> 'it is NOT CLAIMED -- nothing holds a deadline for it, so there is nothing to inform'

So the instructed command binds nothing and exits non-zero, and the turn that spends the 2h25m
measurement is logged `LANDED NOTHING` and has the item re-offered — the failure the instruction is
quoted above trying to prevent, caused by following it literally.

**The live claim is `the-baseline-was-beaten-in-a-world-that-no-longer-exists`.** It is what holds
the paths (`tools/generate_value_arms_data.py`, `tools/run_value_cycle_ab.py`,
`site/data/value_arms.json`), it is the claim every 2026-09-03 seat finding and pre-registration —
including this one, in its own header — is filed under, and it is the id the landing must bind:

    python3 -m background.delivery_lane --landed the-baseline-was-beaten-in-a-world-that-no-longer-exists

Do **not** mint the doorbell's id to make the instruction true. The work is already claimed, and a
second id over one subject is `SEAT_FINDING_A_SECOND_DRAW_RE_OFFERED_A_RECONCILIATION_ALREADY_
LANDED_UNDER_A_DIFFERENT_CLAIM_ID_2026-09-03.md` — the defect, not the repair.

*One trap when checking this by hand: `refusal_reason` is a post-hoc explainer for a refusal that
already fired, not a predictor. Called speculatively on a healthy id it falls through its three
diagnosable causes and returns the residual string `the claims store refused the write`, which
reads as a fourth refusal and is not one. That is what it returns for the live id here — meaning
bindable, not broken.*

### CORRECTION — bind to the doorbell's id. The block above is refuted on its own central fact.

*Measured 2026-09-03 17:40 BST, by the turn that picks the leg up. This supersedes the block above
in full; where the two conflict, this one is the measurement.*

The block above says `pick-up-the-relaunched-undecomposed-floor-leg` is "claimed nowhere", "absent
from `.delivery_lane_claims.json`", and that "a grep of the whole tree returns no occurrence of the
string outside the doorbell itself". All three are false at the moment a turn acts on them:

    $ cat docs/observability/.delivery_lane_claims.json
    {"pick-up-the-relaunched-undecomposed-floor-leg": {
       "claimed_at": 1788453389.855696,          # 2026-09-03 17:36:29 BST
       "note": "The undecomposed floor leg is RUNNING as se-floor-all-20260903c.service ...",
       "paths": []}}

It is the **only** entry in that store. And it is not merely claimed — it has already had work bound
to it, which settles the bindability question the block above answers by inference:

    $ docs/observability/.delivery_lane_claims.draws.json
    "pick-up-the-relaunched-undecomposed-floor-leg": {
      "first_drawn_at": 1788449732.25,   # 16:55 BST
      "last_landing_at": 1788451990.0,   # 17:13 BST -- a landing that BOUND two paths
      "last_landing_paths": [ ...THE_TURN_RESET_DELETED..., ...THIS PRE-REGISTRATION... ]}

**The block above was landed by the very commit that proves it wrong.** Its own filename is in
`last_landing_paths` for the id it calls unclaimed, bound 22 minutes before it was written.

Meanwhile `the-baseline-was-beaten-in-a-world-that-no-longer-exists` — the id it directs the landing
to — is **not in the claims store at all**. It appears only in the *draws* ledger, which is a history
of past draws and landings, not a register of what is held. Binding to it is what would have exited
non-zero and logged `LANDED NOTHING`: the block above prescribes the exact failure it was written to
prevent, with the ids transposed.

**The operative command is the doorbell's, unmodified:**

    python3 -m background.delivery_lane --landed pick-up-the-relaunched-undecomposed-floor-leg

No id is being minted by this — the executor claimed it at turn start, 89 seconds after the block
above was filed. That is the whole mechanism of the error and it is not carelessness: **a claim
store is a live ledger, and a reading of it goes stale exactly the way a green test does.** The
block above was measured correctly at 17:35 and was false at 17:36:29 without anything being wrong
with the measurement. A pre-registration may fix a *prediction* in advance; it may not fix an
observation of mutable state in advance, and the two are different kinds of sentence sharing one
document. Filed as `SEAT_FINDING_A_PREREGISTRATION_FIXED_AN_OBSERVATION_OF_MUTABLE_STATE_AND_IT_WAS_
FALSE_BEFORE_THE_TURN_READ_IT_2026-09-03.md`.

**Check the store, do not quote this paragraph either.** It carries the same expiry as the one it
corrects — `cat docs/observability/.delivery_lane_claims.json` costs nothing and is the only thing
that answers the question at the instant you need it answered.

### Then

Grade P4, P6 and P7 here against the landed artefact; update the `/capabilities/` headline to the
live-world pair and bound, **or state plainly that the floor still contains the contrast** — P7
predicts it does; and grade P5's substantive clause on the digests, not on the `producing_commit`
proxy §4 of the sibling pre-registration already flagged as the worse test.

---

## §3 SUPERSEDED — the unit is `d`, and the ETA above is calibrated on a CRASH

*Delivery seat, 2026-09-03 18:45 BST, claim `pick-up-the-relaunched-undecomposed-floor-leg`.
Measured from the running unit's own journal, not assumed. The §3 table above names
`se-floor-all-20260903c`, which **failed** at 17:41 after 1h34m with exit 1 and wrote nothing; its
worktree was reaped out from under it and it died on a relative-path write. §3 is kept because a
superseded instruction beside its correction is the record; it is not actionable.*

### The leg that is actually running

| | |
|---|---|
| unit | `se-floor-all-20260903d.service` — **LAUNCH 4** |
| started | 2026-09-03 17:45:25 BST, pid 3730923, ppid 382 (detached under user systemd) |
| worktree | `/var/tmp/se-floorrun-20260903d` at commit `1d821e12b` — **`git worktree list` confirms `locked` at 18:42** |
| `--out` | `/var/tmp/se-floor-artefacts/value_cycle_ab_s1_noise_floor_20260903.json` — outside every worktree |

### The ETA is ~20:05 BST, not ~19:20 — and the difference is what launches a fifth run

The doorbell commissioning this turn implies completion around 19:20 BST, which is 1h35m after
launch. **That is launch 3's time-to-CRASH, not any leg's time-to-COMPLETE.** Calibrating a deadline
on a failed run's duration is the phantom-outage shape §3 already recorded once through a stale unit
name, arriving a second time through a stale clock: a seat that checks at 19:20, finds no artefact
and concludes the leg died would launch the fifth run this claim explicitly forbids — and would kill
a healthy 2h20m measurement to do it.

Measured instead, from the journal of the unit that is running:

* **The leg is 9 full-window passes, not 3.** `run_value_cycle_ab.py:3229` loops `for seed in seeds`
  over the three noise-floor seeds, and each iteration calls `run_value_cycle_ab(level_arm=True)`,
  which runs three arms — control, value, level. 3 seeds x 3 arms = 9.
* **Cadence, from `=== SURVIVED full window` timestamps:** 18:06:26, 18:21:20, 18:34:01 — so
  ~16, ~15 and ~13 minutes per pass, and the first pass began at 17:50:26 after ~5 minutes of data
  loading. Seed 1's three arms took 17:50:26 -> 18:34:01, **43m35s per seed**.
* **Therefore:** 3 seeds x ~43.5 min + ~5 min load = **~2h16m, finishing ~20:01–20:10 BST.**

This agrees with the ~2h24m-per-floor-leg figure in the 2026-08-29 log that §3 of the sibling
pre-registration already cites, and disagrees only with the doorbell.

**Do not read an absent artefact as failure before ~20:15 BST.** The one question that settles it
costs nothing and does not depend on any clock in this document:

    systemctl --user is-active se-floor-all-20260903d

`active` means running. Only `failed`/`inactive` with no artefact at `--out` is a dead leg, and even
then the journal states the cause. **Do not launch a fifth run** on the strength of a timestamp.

### Memory is the binding constraint while this runs — do not start a suite beside it

At 18:36 BST `background.resource_headroom.sample()` returned **7,927.8 MB available** against the
unit's **6.5 GB peak** (`systemctl show ... Memory: 4.4G (peak: 6.5G)`). An earlier leg of this same
measurement was **OOM-killed** (`ExecMainStatus=9`). A full pytest run beside it is what turns a
2h16m measurement into a fourth lost artefact, and the loss is silent — an OOM-killed leg writes
nothing, which is indistinguishable from still-running. **Keep this turn to reads until the artefact
lands.**

### The grading procedure, ready to run

Every guard in `_current_world_bound` was confirmed armed at 18:38 by reading the module, and
`CURRENT_WORLD_NOISE_FLOOR_PATH` already points at
`docs/observability/value_cycle_ab_s1_noise_floor_20260903.json` — so step (c) remains a file copy,
not a code change. Copy the artefact there first, then grade with the real functions rather than by
eye. **Print the three identity fields before any figure**: the `only` leg on disk carries the same
digits, so a grader who opens the wrong file gets the right number.

    import json, sys
    from pathlib import Path
    import tools.generate_value_arms_data as gva
    from simulation.departure_level_anchor import world_level_identity

    floor = json.loads(Path("docs/observability/"
                            "value_cycle_ab_s1_noise_floor_20260903.json").read_text())
    three = json.loads(gva.CURRENT_WORLD_THREE_ARM_PATH.read_text())
    live  = world_level_identity()["digest"]

    # IDENTITY FIRST -- mode must be 'all', generated_at after 17:45 BST, digest 39a192ce04c1eda8
    print((floor.get("redraw_scope") or {}).get("mode"), floor.get("generated_at"),
          (floor.get("world_identity") or {}).get("digest"))

    # AND REFUSE ON THOSE THREE FIELDS -- printing them and trusting the reader is not a control.
    assert (floor.get("redraw_scope") or {}).get("mode") == "all"
    assert (floor.get("world_identity") or {}).get("digest") == "39a192ce04c1eda8"
    assert floor.get("generated_at", "") >= "2026-09-03T16:45:00Z"   # launch 4, 17:45:25 BST

    spreads = gva._seed_spreads(floor, three)          # per-contrast, DERIVED from seed rows
    print(gva._spread_for(spreads, gva.PAGE_FIGURE_CONTRAST))   # P9: ~991.4551, band 942-1041
    print(gva._current_world_bound(floor, three, live))
    print(gva._current_world_contrast(three, None, floor)["resolved"])   # P10: expected True

**Those three assertions are not belt-and-braces, and this was measured rather than supposed.** Run
without them against `value_cycle_ab_s1_noise_floor_only_20260903.json` — the wrong leg, sitting on
disk right now — the grading above reports **P4, P6, P8 and P9 all CONFIRMED** on entirely plausible
digits, because that leg carries the same numbers. Only P10 comes back refused, and it refuses with
`resolved=None`, which is the *plumbing-failure* signal rather than a world result, so even the one
true negative reads as the wrong kind of problem. A grader that prints the identity fields and
leaves a human to check them is fail-open in the flattering direction: it produces four confirmed
predictions from an artefact it should never have opened.

With the assertions in, the two artefacts on disk are refused for two *different* reasons, which is
what keeps each check from being an equivalence the other covers for:

| subject on disk | mode | world | refused on |
|---|---|---|---|
| `..._noise_floor_only_20260903.json` | `only` | live | **the mode** — sole witness for the leg guard |
| `..._noise_floor.json` (2026-08-31) | `all` | `None` | **the world** — sole witness for the world guard |

That is the same two-guard, sole-witness structure `_current_world_bound` already uses on the same
two files, which is the point: **the grader must refuse exactly what the page refuses**, or the
grade and the publication disagree about what the subject was.

Then grade, and **grade each prediction against the quantity it actually names**:

| | predicted | read from | note |
|---|---|---|---|
| **P4** | `selection_gbp_spread.stdev` > 3776.27 | published scalar | |
| **P6** | same stdev in 5,600–6,250; range ~10,983.77 | published scalar | blind, ±5% as filed |
| **P7** | `selection_distinguishable_from_zero` is `false` | producer key, about `selection_gbp` | **its supporting arithmetic is wrong** — see below |
| **P8** | seed rows reproduce the `only` leg exactly | seed rows | retrodiction, determinism check ONLY |
| **P9** | `value_advantage_gbp` seed stdev = 991.4551 ±5% | **derived**, not published | blind |
| **P10** | `_current_world_contrast(...)["resolved"]` is `True` | the page's own function | `None` = plumbing refusal, NOT a world result |

**P7 and P10 predict opposite outcomes about the page, and P10 is the one keyed to the page's own
quantity.** P7 divides `value_advantage_gbp` (£2,335.87) by the floor's published
`selection_gbp_spread` (~£5,923) to get 0.39x and reads it as "comfortably inside". Those two figures
count different things: `_current_world_bound` bounds the page on `value_advantage_gbp`'s **own**
spread across the seed rows, which is ~£991.46 on the live-world `only` leg — **5.97x apart**, and in
the direction that flips the verdict. `_current_world_bound`'s docstring names this exact
substitution as the thing it was written to stop. Fully worked in
`SEAT_PREREGISTRATION_P7_IS_GRADED_ON_A_QUANTITY_THAT_DOES_NOT_BOUND_THE_PAGE_2026-09-03.md`, which
files P9 and P10 to replace it. So act (d) is most likely **"update the headline to the live-world
pair and bound"**, not "state plainly that the floor still contains the contrast" — but that is
P10's prediction and not a licence: read it off the artefact.

**If P10 confirms, the headline may say the figure clears its own draw noise and nothing more.**
`_resolvable` is a one-sigma test on three seeds, and the floor's own `value_advantage_gbp` mean is
£1,030.10 rather than £0, so the floor is not a clean null. The advantage also collapsed from
£12,071 to £2,336 between worlds. A resolved verdict says the figure clears its noise; it does not
say the figure is large, durable, or the one published on 2026-08-31.
