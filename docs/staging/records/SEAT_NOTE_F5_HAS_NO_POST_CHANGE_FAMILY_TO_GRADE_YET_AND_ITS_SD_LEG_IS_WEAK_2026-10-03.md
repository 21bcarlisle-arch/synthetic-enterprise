# Note: F5 has no post-change family to grade yet, and its sd leg is weak at six seeds

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` ·
**Claim:** `flow-f5-grade-seasonal-dates-on-the-first-post-change-family`

Written 2026-10-03 04:20 BST. It concerns F5 of
`SEAT_RESULT_SAME_DAY_RENEWALS_DO_NOT_COVARY_SO_FLOW_IS_NOT_A_VARIANCE_CAUSE_AND_FIVE_TO_NINE_ACCOUNTS_SET_THE_SD_2026-10-03.md`.

## F5 cannot be graded yet: no family exists

b35e8cfa4 (acquisition days follow the DESNZ months) was committed at 04:09:18, about three minutes
before this item was drawn. No value-arm artefact anywhere on disk was drawn by a commit that
contains it. These are the families that exist or are running:

- `se-ab6-out/run{P1,P2,X1,B6}` and `se-depthwidth-out/depth_*`: a322166cc.
- `width125_61003_61004` is running now in `se-width125-a322166cc`, so it is pre-change.
- The queued payment-history P/C legs (`se-pc-out`) are pinned to c2ba8649c and e0370bf94, so they
  are pre-change too.

The item says not to launch a family for this alone, so none was launched. The claim is released.
The grading is handed on as `flow-f5-grade-when-a-post-change-family-exists`.

## The grader is ready and refuses what it cannot grade

`/var/tmp/se-flow/f5_grade.py ART.json ...` reuses `run.py`'s anniversary key and permutation null
(2,000 draws, seed 7). It refuses in two cases: when any artefact's `producing_commit` does not
contain b35e8cfa4, and when there are fewer than six seeds. Each refusal names its reason. It prints
three figures, each against its permutation null: D_account, sd(S)/sqrt(ΣV_i) and D_date. It gives a
HELD/REFUTED verdict on each F5 leg. Checked against today's artefacts:

- It refuses the ab6 family (a322166cc) and a two-seed file.
- With `--allow-pre-change` it reproduces ab6: D_account 1.022, D_date 0.993, sd ratio 1.011. The
  ratio's null band is 0.50-1.46. Both legs read HELD.
- The REFUTED branch can be taken. depth-2019's D_date of 0.737 falls outside its null band
  (0.76-1.23) and reads REFUTED. That dip is the C5/C5_2 successor pair, not batching.

## F5's sd leg is weaker than it reads

sd(S)/sqrt(ΣV) = sqrt(D_account). At six seeds the null band for D_account is 0.25-2.1, so the
band for the sd ratio is about 0.5-1.46. The sd leg would only fail if batched dates had inflated
the sd by more than about 45%. F5's own words were "will not reduce the residual's sd by more than
10%", and the leg cannot resolve that. I should have seen this when it was written: F2's grading
already found the same blindness in D_account. **D_date is the leg that can fail** (null band about
±0.1). Read F5 as graded on D_date, and treat the sd leg as a coarse check only. Comparing sd(S)
before and after the change is not a dates test either. The founders are the same households on new
dates, so their V_i change with the price path at the new renewal dates. Two six-seed sds differ by
about ±30% from seed noise alone.

## Redrawn three minutes later, still no family (04:18 BST)

The continuation `flow-f5-grade-when-a-post-change-family-exists` was drawn at 04:18, three minutes
after this note landed. I checked again, with the same answer. Every value-arm JSON written since
04:09 with a `producing_commit` (the shared tree, `/var/tmp`) was drawn before the change. The only
`run_value_cycle_ab` process running is width125, which is pre-change. The claim is released.

**No continuation is re-issued.** A continuation has no "when X exists" trigger, so it would be
redrawn on every tick until someone launched a family for some other reason. Each of those draws
would be a turn spent finding this answer again. The obligation is written beside F5 in the result
file instead, with the one command that grades it. That is where whoever lands the next post-change
family will read the pre-registration.

