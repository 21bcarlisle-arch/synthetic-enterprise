**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted` — direction item `the-first-run-with-split-campaign-homes-names-its-book-shift`
**Knowledge:** `how-many-synthetic-households` -- which fuel arrangement the campaign's won homes carry on the published runs

# The 19 Oct run's campaign book is always dual, and a prediction for the first run that splits it

*Delivery seat, 2026-10-19 ~09:30Z. Written before any run at or after `30246d6f0` exists.* The 19 Oct
publish is `8b6fea024` (run started 03:30Z), and `30246d6f0` landed at 08:40Z. The sim-runner's last
success is also `8b6fea024`. Per the item, no run was launched for this.

## 1. What is read, said before it is counted

**The instrument the item names does not exist.** `book_identity` (`tools/run_value_cycle_ab.floor_book_identity`)
carries store digests and seed reconciliation, with no fuel field. The run output has no fuel-share key either.
So the reading here is taken from the run output's own `per_customer_lifetime`, one row per supply point:
- A **route** is the id family: `PROS-*` is the campaign (the comment above `tools/run_value_cycle_ab.py`'s route map), `SYN-*` the
  curriculum draw (founders and trickle), `C<n>` the roster, and `OCC-*` a successor occupant.
- A **home** is the id with a trailing `g` dropped.
- A home's **fuel** is read from each row's `commodity`, not from the `g`. A split gas home carries
  the home's own id with no `g` (`30246d6f0`), so reading fuel off the suffix counts a gas-only home
  as electricity-only. My first pass did exactly that: it read the founders at 100% dual of gas homes
  with 0 gas-only, when they are 94.8% with 9 gas-only.
- **Dual of gas homes** is the measure `30246d6f0` and `world_claims` use: dual homes / (dual +
  gas-only). This counts **every home that ever held supply in the run**, not the book at the end.

```
python3 - <<'EOF'   # from the repo root, with the run output's path as RUN
import json, collections; RUN = "docs/reports/run_output_<sha>_<ts>.json"
p = json.load(open(RUN))["per_customer_lifetime"]; homes = collections.defaultdict(set)
for k, v in p.items():
    if k.startswith("PROS-"): homes[k[:-1] if k.endswith("g") else k].add(v["commodity"])
d = sum(f == {"electricity", "gas"} for f in homes.values()); g = sum(f == {"gas"} for f in homes.values())
print(len(homes), d, g, round(d / (d + g), 3), round(d / len(homes), 3))
EOF
```

## 2. Result on the published runs

| run | route | points | homes | dual | elec-only | gas-only | dual of gas homes | dual of homes |
|---|---|---|---|---|---|---|---|---|
| 19 Oct, `8b6fea024` | campaign `PROS-` | 386 | 214 | 172 | 42 | **0** | **100.0%** | 80.4% |
| | founders `SYN-` | 383 | 220 | 163 | 48 | 9 | 94.8% | 74.1% |
| | successors `OCC-` | 181 | 107 | 74 | 31 | 2 | 97.4% | 69.2% |
| 13 Oct, `2248e3baf` | campaign `PROS-` | 392 | 217 | 175 | 42 | **0** | **100.0%** | 80.6% |
| | founders `SYN-` | 379 | 379 | 0 | 272 | 107 | 0.0% | 0.0% |

**So the shift from 13 to 19 Oct is the founders (0% to 74% dual), not the campaign.** The campaign
was already dual on every gas home on both runs. That matches `30246d6f0`'s 8-seed figure (100.0%, dual of homes
81.7%). On the 19 Oct run, 172 of the 413 dual homes (42%) are campaign homes, and none of them could
have been split.

## 3. What this means for the readings on the 19 Oct run

The two dual-fuel preregs graded on this run, and the per-household NBA count, read a book where
**every campaign gas home is dual.** At `P(dual | gas)` 0.906, about 16 of the 172 would have been
split homes: about 8 gas-only and 8 electricity-only. The number of dual households would then be about 397,
not 413: **about 4% fewer.** The notes beside those readings point here:
- the 27.8D offset prereg (`SEAT_PREREG_HOW_MANY_DUAL_HOUSEHOLDS_…_2026-10-18.md`);
- the B11/C35/C34 prereg (`SEAT_PREREG_B11_C35_C34_…_2026-10-18.md`);
- the per-leg finding (`WORKER_FINDING_THE_COMPANY_DECIDES_A_DUAL_HOUSEHOLD_PER_LEG_…_2026-10-18.md`).

These are level readings, and a 4% change in the dual population moves none of their predicted bands
by itself. The note is there so that no later run's dual-household count is differenced against them
as if only the company had changed.

## 4. Pre-registration: the first published run whose sha descends from `30246d6f0`

Same instrument (§1). The first run is the one whose `producing_commit.commit` has `30246d6f0` as an ancestor
(`git merge-base --is-ancestor 30246d6f0 <sha>`).

- **S1. Campaign dual of gas homes: 0.81–0.96 (point 0.906).** This is `30246d6f0`'s 8-seed band. Below 1.0 at
  all is the main claim: **if it reads 1.000 again, the coin did not reach the published run.**
- **S2. Campaign gas-only homes: at least 1, point about 8 (half the split gas homes).** At 0, a split
  home cannot be gas-only on this route, whatever S1 reads.
- **S3. Campaign dual of homes: 0.68–0.80 (point 0.74; commit 74.0%).**
- **S4. Campaign points per home falls from 1.80 to 1.70–1.78.** One account per split home, not two.
- **S5. Founders hold: dual of gas homes 0.85–0.98, dual of homes 0.68–0.80.** Their coin is unchanged.
- **S6. Dual households across all routes fall by 2–8% against 413**, unless a population commit
  between `8b6fea024` and that sha changes home counts. In that case, compare shares only, and say so.

Grade below this line. Do not edit the predictions above.

**Not gradable yet. Checked by a worker tick at 2026-10-19 09:57Z.** The newest publish on origin is still
`2a195224b` (git=`8b6fea024`), and `8b6fea024` does not descend from `30246d6f0`. No sim run is in
flight. `sim-runner` has deferred every cycle since about 08:00Z to the budget-pay arm long jobs
(`longjob-budgetpay-arm-off` and then `longjob-budgetpay-arm-on-pennyfix2`, the second started 09:30Z).
A run takes about 5.5 h from launch to publish (the 19 Oct one started at 03:30Z and published at 09:15Z),
so the first gradable run cannot land before about 15:30Z. Nothing was graded on an older run. The
hand-off is re-issued as `grade-the-first-split-campaign-run-when-it-publishes`, with a draw embargo.

## 5. Grade: all six hold, on the `ad8afadc5` run (delivery seat, 2026-10-19 ~16:00Z)

**Which run, and why not a published one.** `run_output_ad8afadc5_20261019T132751Z.json` in the
shared tree started at 13:27Z and completed at 15:03Z (5,743 s, peak 4,065 MB). Its
`producing_commit.commit` is `ad8afadc5`, and `git merge-base --is-ancestor 30246d6f0 ad8afadc5`
is true. **It has not published, and it will not this week.** The publisher held it: "HOLD (weekly
publish window): this week's figures reached origin 2026-10-19T09:15Z; the next publish opens Mon
2026-10-26 04:00 GMT" (`sim-runner-log.md`, 15:03Z). So no published run will exist to grade for a
week. This is the first completed production run on the split coin, which is the question the item
asked. Waiting a week would only re-read the same coin on a later sha. The grade is on that run,
and is labelled unpublished. It was read with §1's instrument, fuel from `commodity`, against
the 19 Oct publish run `8b6fea024` from the same file family.

| | prediction | `ad8afadc5` | `8b6fea024` | verdict |
|---|---|---|---|---|
| S1 campaign dual of gas homes | 0.81–0.96 (0.906) | **0.946** | 1.000 | holds: the coin reached the run |
| S2 campaign gas-only homes | ≥ 1, about 8 | **9** | 0 | holds |
| S3 campaign dual of homes | 0.68–0.80 (0.74) | **0.734** | 0.804 | holds |
| S4 campaign points per home | 1.70–1.78 | **1.734** (371 / 214) | 1.804 | holds |
| S5 founders dual of gas / of homes | 0.85–0.98 / 0.68–0.80 | **0.948 / 0.741** | same | holds, unchanged as predicted |
| S6 dual households, all routes | −2% to −8% against 413 | **395, −4.4%** | 413 | holds |

**S6 is a like-for-like count, not only a share.** Homes across all routes are 550 on both runs,
and campaign homes are 214 on both. The campaign won the same homes, and only their fuel
arrangement changed: 15 dual homes became 9 gas-only and 6 more electricity-only, and the book
lost 15 supply points (386 to 371). Successors moved 74 to 71 dual, following the homes they
replace. So §3's "about 4% fewer dual households" is now measured, at 4.4%.

**What this licenses.** Readings taken on the 19 Oct publish (`8b6fea024`) and on the next publish
differ in the dual population by 18 households from this source alone. §3's notes stand as
written. The 26 Oct publish will carry this run or a later one. Either way it descends from
`30246d6f0`, so this grade is what it should reproduce at seed 20260724, unless a population
commit lands first.
