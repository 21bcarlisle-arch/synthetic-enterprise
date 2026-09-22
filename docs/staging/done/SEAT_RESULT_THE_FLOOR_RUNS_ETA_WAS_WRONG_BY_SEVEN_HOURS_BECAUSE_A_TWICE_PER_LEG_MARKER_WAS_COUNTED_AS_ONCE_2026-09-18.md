**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** value_arms_floor_family

# RESULT — the next12 ETA was wrong by 7h33m, and a completed run of the same instrument was sitting in the same directory the whole time

**Filed:** 2026-09-18 00:20, with `/var/tmp/value_cycle_ab_s1_noise_floor_next12_20260917.json`
still non-existent. **Claim id:** `next12-twelve-seed-family-read-alone-tests-the-single-arm-sign`

Corrects, beside the claim, the ETA in
`PREREG_THE_NEXT12_FAMILY_IS_STAMPED_A_SALVAGE_COMMIT_AND_SHARES_AN_INSTRUMENT_WITH_THE_AUC_THREE_2026-09-17.md`
(landed `d9ce63a45`), which this seat wrote. Findings 1 and 2 of that prereg, and every prediction
in it, are **untouched** — the defect is confined to its progress arithmetic.

---

## The correction

| | claimed | measured |
|---|---|---|
| per arm-leg | 13.0 min | **25.54 min** |
| arm-legs done at 23:51 | 17 | **8 complete, 9th running** |
| seeds done at 23:51 | ~5.7 of 12 | **~2.9 of 12** |
| ETA | **03:58** | **2026-09-18 11:31:24** |

**Short by 7h33m24s.** The drawn item's own "~4h left at 23:43" carries the same error.

## What went wrong — a marker counted before it was defined

The run prints no per-seed progress line, so progress has to be inferred from incidental markers.
Four are available, and they do **not** all mean the same thing:

| marker | occurrences per arm-leg |
|---|---|
| `=== Phase 2b — Gas Dual Fuel` | 1 |
| `=== SURVIVED full window` | 1 (on completion) |
| `Cache hit: 168,026 SSP records` | 1 |
| `Starting treasury:` | **2** — one per commodity pass |

The prereg counted **17 "arm-legs"** at 23:51. There were 17 *`Starting treasury` lines*, which is
8.5 arm-legs. Dividing 219.7 elapsed minutes by 17 gave 12.9 ≈ the "13.0 min per arm-leg" on file;
every figure downstream inherits the factor of two. The arithmetic was internally consistent and
the input was a quantity nobody had defined.

This is `CLAUDE.md`'s *"before measuring a thing, say what it is"* at its cheapest and most literal:
one sentence naming what one occurrence of the marker meant would have caught it.

## The ruler that was already available

`/var/tmp/floor_auc_20260917.log` — the **completed** 3-seed AUC floor, which the prereg's own
Finding 2 had already established runs *byte-identical* value-arm code to next12 — is a calibrated
ruler for exactly this, and it finished before next12 started:

```
floor_auc_20260917.log   3 seeds, COMPLETE, 16:21:50 -> 20:11:44  (3:49:54)
  === Phase 2b                9      === SURVIVED full window   9
  Cache hit: 168,026          9      Starting treasury:        18   <-- 2x
```

9 arm-legs for 3 seeds confirms **3 arm-legs per seed** (`run_value_cycle_ab(level_arm=True)` calls
`run_phase4c` three times: control, value, level — `tools/run_value_cycle_ab.py:4410`), and
18 vs 9 is the doubling, measured rather than argued.

**It reconciles to the second, which is why I trust it.** 13794 s / 3 seeds = 4598 s per seed. At
00:06:29 next12 had run 14081 s = **3.06 seeds / 9.19 arm-legs** — and the log showed exactly 9
`SURVIVED` with a 10th leg running. A second, independent check: at 00:01:35 next12's log was
84,098,316 bytes against auc3's *final* 83,758,576 for its 3 seeds — just past three seeds, agreeing
with the clock.

12 × 4598 s = 15:19:36 from the 20:11:48 `exec` → **2026-09-18 11:31:24**.

*This is a projection from one completed run of the same instrument, not a guarantee: it assumes the
machine stays as loaded as it was for auc3. It is stated as a projection because an ETA presented as
a fact is what this finding is about.*

## The disposition — a second claim, minted from the refuted ETA, is being worked right now

The drawn item's duplicate-work check named two rivals
(`the-page-prices-a-sign-off-a-spliced-family-...`, `the-publisher-is-wedged-behind-origin-...`) and
asserted each "already holds `site/data/value_arms.json`". **Both claims are wrong**: the first holds
`"paths": []`, and the second holds four paths, none of them `site/data/value_arms.json`
(`background/origin_reconcile.py` and three test/doc paths). Neither is this work. That re-measures
and confirms the prereg's refutation of the same note.

The real duplicate is a **third** claim the check did not name, because it was minted 53 s *after*
this one:

```
next12-twelve-seed-family-read-alone-tests-the-single-arm-sign   claimed_at 1789686370.50  (23:46:10)
read-the-next12-twelve-alone-once-the-0358-run-settles           claimed_at 1789686423.92  (23:47:03)
```

It is the same work — its dispatch text says *"Copy `…next12…json` into `docs/observability/` and
read it as its own TWELVE-seed family"* — and **its id and its text both encode the refuted ETA**:
*"13.0 min per arm-leg, ETA near 03:58; do not draw this before then, the file will not exist."*
A live worker (PID 520483) was drawn on it at 00:02 and cannot do it; the file is 11 hours away.

**Disposition taken: `--release read-the-next12-twelve-alone-once-the-0358-run-settles`.** Both
items instruct the holder to release the other, which is a symmetric race, so the tie is broken on
the only asymmetric fact available: **`claimed_at` — the older claim survives.** This one is older
by 53 s and is the one carrying the landed prereg. Reversible: the work is re-mintable and the
surviving claim names it here.

**The ETA is load-bearing beyond the claim.** Because "03:58" is baked into the rival's id and
dispatch text, the scheduler will keep offering this work from ~04:00 — and each such draw is a
whole invocation that opens a directory, finds no file, and stops. That is the cost this document
exists to stop, and it is why the correction was worth a turn on its own.

## What this turn does not settle

Part 1 itself: the twelve seeds. Unchanged and unchangeable tonight — no judgement substitutes for
them, and nothing here touches the filed prediction about the sign.

## Predictions

1. `/var/tmp/value_cycle_ab_s1_noise_floor_next12_20260917.json` appears between **10:45 and 12:15
   on 2026-09-18**. *If it lands before 09:30 or after 13:30, the auc3 ruler does not transfer and
   the cause is machine load, not seed count — say so rather than widening the window afterwards.*
2. The delivered artefact carries **12** seed rows, and its log ends with **36** `=== Phase 2b` and
   **72** `Starting treasury` lines. *A count of 36 against 72 is the doubling confirmed on the
   delivered family; anything else refutes the marker table above.*
3. I am **not** predicting its selection mean, sem or sign. The sign is the thing under test.
