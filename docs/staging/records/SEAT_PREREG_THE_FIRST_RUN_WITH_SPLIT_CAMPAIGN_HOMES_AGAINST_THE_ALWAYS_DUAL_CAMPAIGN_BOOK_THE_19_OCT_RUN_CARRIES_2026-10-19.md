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
