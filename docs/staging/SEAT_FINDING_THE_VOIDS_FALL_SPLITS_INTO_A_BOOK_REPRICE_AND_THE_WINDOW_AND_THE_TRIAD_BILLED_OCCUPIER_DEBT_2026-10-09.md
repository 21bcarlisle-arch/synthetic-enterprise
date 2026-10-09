**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_40_voids_tied_to_move_outs` · **Claim:** `the-voids-effect-is-split-and-the-atom-carries-its-gaps` (Lane 0)

# The void's fall in net splits into a book-wide reprice and the later window; the triad was billing the named household for occupier debt

*Seat finding, 2026-10-09. Drawn item `the-voids-effect-is-split-and-the-atom-carries-its-gaps`.
Subject: 5531ef8a6 (B7 slice 6, voids by vacated tenure), whose GBP 910 fall in net margin came
from four changes at once and was not attributed.*

## 1. The four-way split

**Measure.** `simulation.run_phase2b.main(report_end="2019-12-31")`: 80 founders, the run's own
seed, moves on, `total_net`. Each lever turned OFF reverts that one piece to its pre-void
behaviour. The lever patch is env-gated and was never landed. Driver and per-account dumps:
`/tmp/voids_split2/` (`drive.py`, `*.json`; the patch is `/tmp/voids_split/levers.patch`).

**Predictions, filed 2026-10-08 23:59 before any run** (`/tmp/voids_split/PREDICTIONS.md`, copied
unchanged; scratch worktree at origin c38c97622):

| Lever | Predicted effect of the lever ON | Measured (all-on minus that lever off) | Verdict |
|---|---|---|---|
| ENERGY: void rows have 0 kWh and carry only the owner's standing charge | raises net by GBP 300 to 1,500 | **-377.16** | **refuted on sign** (see below) |
| WINDOW: the unnamed window starts at void end | lowers net by GBP 800 to 2,000 | **-405.45** (first draft said -405.44: a slip, corrected from the raw lines in §5) | sign right; **refuted on size** (half the floor) |
| HAZARD: the incoming household's move hazard starts at void end | below GBP 100, probably 0 | **0.00** | held |
| PAYMENT: the void charge is kept out of the triad's monthly amount | below GBP 200 | **0.00** | held |
| Interaction residual (all-on minus base minus the four drop-ones) | below GBP 200 | **-12.39** (first draft -12.40) | held |
| The whole fall | "the WINDOW, partly offset by ENERGY" | ENERGY and WINDOW are about equal and **same sign** | **refuted** |

**Not blind.** That prior invocation saw two numbers at c38c97622 before the re-run that produced
these figures: base 44,478.34 and WINDOW-off 44,092.93. The predictions above were filed before
both.

**The base moved, and each arm is differenced only within its own base.** Read from the scratch
worktrees' HEADs and their `run_phase2b.py` diffs, both byte-identical to
`/tmp/voids_split/levers.patch`: `/tmp/voids_split` ran at **c38c97622** (all-off 44,478.34),
`/tmp/voids_split2` at **5ed687b3d** (all-off 44,331.98). The all-off rows differ by GBP 146.36,
which is the trunk moving between the two, not the void; no single in this table is taken across
bases. The four drop-one arms above are all 5ed687b3d's. These runs are at origin 5ed687b3d (2026-10-09 02:30). There the total fall
is **GBP 795.00** (base 44,331.98, all-on 43,536.98), not 5531ef8a6's 910. The split is of the
795. The 910 was not re-measured at 5531ef8a6.

**Why ENERGY's sign was wrong, measured per account.** Removing void energy changes 97 accounts,
not only the 20 move-in legs:

| ENERGY ON minus OFF | net | revenue | occupier debt | wholesale |
|---|---|---|---|---|
| the 20 move-in legs | **+234.69** | -416.31 | -428.82 | -123.93 |
| the other accounts | **-611.85** | -624.57 | 0.00 | -0.06 |

On the legs themselves the prediction's mechanism holds: a void day stops being an occupier-debt
day whose energy cost is lost, so net rises (+235, just under the predicted floor). The other
accounts lose GBP 612, all of it revenue, with no change in volume or wholesale. That is a price
effect. The one route I found from a leg's settled margin to another account's price is the
portfolio-margin feed (`_portfolio_margins.settled`, read by every later renewal). A leg's term
that loses less teaches the book a lower premium. **This route is inferred from the code; no arm
isolated it.** If it is the route, then most of the void's effect on net is the company
repricing everyone else off the void legs. Whether a void leg should teach the book's premium at
all is a question for the debt line's re-grade. I have not changed it.

WINDOW's -405 sits entirely on the legs: occupier debt rises by GBP 450.81 because the window that
nobody pays now runs from void end.

## 2. The triad question: yes, it did, and it is fixed here

**Question** (5531ef8a6's open check). Does the payment triad's monthly amount feed
change-of-tenancy occupier debt into the named household's payments, against B7 slice 5's
exclusion?

**Read at origin 91a798172: yes.** `_held["amount_gbp"]` added each row's `revenue_gbp` minus
only the void charge. It ran BEFORE the branch that books an unnamed-window row's revenue as
`occupier_debt_gbp`. So `_post_month_bill` (`record_period`) asked the incoming named household,
keyed on its own account, to pay for energy used before anyone was named. Three places read that
event: the W2_11 payment truth, the CX desk, and `WorldDebtBook` (the SLC 14 debt objection reads
it as who owes). The arrears engine already excludes it (`simulation/arrears_engine.py`,
`occupier_share`). The triad was the one place that did not.

**Fix.** The month accumulation now runs after both branches and subtracts
`void_owner_charge_gbp` and `occupier_debt_gbp`. Control:
`test_the_payment_triad_asks_the_named_household_only_for_its_own_months_share` in
`tests/simulation/test_a_vacated_home_stands_void_for_its_tenure.py`. It carries a partition
control: at least one posted month must hold more than GBP 1 of occupier debt, so the control
cannot pass vacuously. With the occupier subtraction removed it goes red (`6.78 != 0.0`).

**Prediction for the fix's effect on net, filed before its run returned:** exactly GBP 0.00
change in `total_net` at 2019. Reason: the PAYMENT lever runs through the same accumulator to the
same `record_period` and moved net by 0.00, so nothing in run_phase2b's net reads the triad's
amount before 2019. If it moves, the triad reaches net by a route the PAYMENT arm did not
exercise.

**Measured:** see §4. **The prediction held.**

## 2a. OCCPAY, graded on each base that has the arms

OCCPAY is the lever form of the triad fix (subtract the row's occupier debt from the triad's month).
No prediction was filed for it as a lever; §2's 0.00 prediction is the one that grades it.

- **5ed687b3d:** the OCCPAY arm (`onOCC`) and the four single-lever-ON arms (`onE`, `onW`, `onH`,
  `onP`) wrote no RESULT line: each log ends after the first-term lookback line, so the second
  batch died before settling. **Ungradable here.**
- **c38c97622:** the only arm with OCCPAY on is all-four-plus-OCCPAY (43,683.63); no all-four arm
  without it ran on that base. So OCCPAY cannot be differenced on its own base. **Ungradable
  here.** What c38c97622 does give: E+H+P from all-off = -385.41 (44,092.93 - 44,478.34), against
  5ed687b3d's -389.55 for the same three levers. All levers plus OCCPAY from all-off = -794.71,
  against 5ed687b3d's -795.00 without OCCPAY. That fits OCCPAY being about zero, but it is not a
  measurement of it.
- **91a798172 (§4):** origin against origin plus the fix, which is OCCPAY landed. **0.00 on
  `total_net`.** This is the one clean grade.

## 3. The atom

`W2_40_voids_tied_to_move_outs` is minted at L1 (target L3) on `docs/design/maturity_map.yaml`,
with these GAPs:
- **The owner-void GAP:** `q1_void_months_owner` is null, because no published owner-occupier
  void length exists.
- **The void-use GAP:** a void's own kWh is unpublished, so 0 kWh and a standing-charge floor are
  used.
- **The gas owner-as-consumer GAP:** gas voids follow electricity.

## 4. Triad fix, measured

Two runs at origin 91a798172, launched as one detached chain (`longjob-voids-triad-fix-price`),
origin against origin plus the fix:
- `total_net` is **43,536.98 in both** (change 0.00, as predicted). Occupier debt (3,112.21),
  void charge (39.78), bad debt and revenue are also unchanged. The all-on figure equals
  5ed687b3d's to the penny.
- The fix did act. Of 5,249 posted months, **77 changed, on exactly the 20 move-in legs**, by a
  total of **GBP 3,112.21**. That is the run's whole occupier debt, moved off the named
  households' payment events.

So the defect was live in what the named household is asked to pay, in what the company's payment
belief observes, and in what the world's debt book records. Up to 2019 it did not reach net.
Where it could reach net is the debt objection at renewal (`WorldDebtBook`) and the payment belief
in later years. Neither was measured here. The re-grade of debt results should read them after
this fix, not before.

## 5. The raw evidence (copied from /tmp, which is lost on reboot)

**Disposition of the triad fix:** it does not change net to 2019 (0.00). It does change what the
named household is asked to pay: 77 posted months on the 20 move-in legs, GBP 3,112.21. It is
**landed** with this finding, because it is a correctness fix to the payment events, not a lever on
net. The fix copy measured in `/tmp/voids_split3` (`/home/rich/wt-voids-split3`) is the one landed
here. Its comparison arm (`/var/tmp/se-voids3-origin`) was origin 91a798172 with no simulation
change. No commit between 91a798172 and this landing's base touches `simulation/run_phase2b.py` or
the void test.

**`/tmp/voids_split/PREDICTIONS.md`, verbatim (filed 2026-10-08 23:59:50, before any run):**

```
Filed 2026-10-08 before any one-variable run (scratch worktree /home/rich/wt-voids-split @ origin c38c97622).
Measure: run_phase2b.main(report_end="2019-12-31"), 80 founders, run seed, moves on; total_net.
Each lever OFF reverts that one piece to pre-void behaviour.
P-ENERGY (void rows: 0 kWh, standing charge only, owner's): RAISES net margin by GBP 300-1,500.
  Reason: before the void those days were occupier-debt rows, net = -(energy costs); now net = -capital only.
P-WINDOW (unnamed window starts at void end, not the move date): LOWERS net margin by GBP 800-2,000.
  Reason: ~350 leg-days of the named occupant's paid supply become occupier debt.
P-HAZARD (incoming household's move hazard starts at void end): |delta| < GBP 100, probably 0.
P-PAYMENT (void charge kept out of the triad's monthly amount): |delta| < GBP 200.
Interaction residual (all-on minus baseline minus the four singles): |r| < GBP 200.
Sign of the whole: the GBP 910 fall is the WINDOW, partly offset by ENERGY.
```

`/tmp/voids_split2/PREDICTIONS.md` (02:32:54) copies those unchanged and declares what was seen
before the re-run: c38c97622's all-off 44,478.34, WINDOW-off 44,092.93, and all-on with OCCPAY
43,683.63.

**RESULT lines, verbatim.** Lever flags: 1 = the piece is as landed in 5531ef8a6. OCCPAY 1 = the
triad fix.

c38c97622 (`/tmp/voids_split`, 2026-10-09 00:04 to 00:12). `offE`, `offH`, `offP`, `onE`, `onW`
and `fullOCC` died before a RESULT line:
```
base.log  RESULT {"ENERGY": "0", "WINDOW": "0", "HAZARD": "0", "PAYMENT": "0", "OCCPAY": "0", "total_net": 44478.34, "occupier": 3096.95, "void": 0.0, "bad_debt": 5019.63, "revenue": 240568.68, "move_ins": 20, "n_records": 155862, "secs": 416}
offW.log  RESULT {"ENERGY": "1", "WINDOW": "0", "HAZARD": "1", "PAYMENT": "1", "OCCPAY": "0", "total_net": 44092.93, "occupier": 2676.52, "void": 39.78, "bad_debt": 5006.1, "revenue": 239523.81, "move_ins": 20, "n_records": 155862, "secs": 420}
on.log    RESULT {"ENERGY": "1", "WINDOW": "1", "HAZARD": "1", "PAYMENT": "1", "OCCPAY": "1", "total_net": 43683.63, "occupier": 3132.89, "void": 39.78, "bad_debt": 4997.75, "revenue": 239562.52, "move_ins": 20, "n_records": 155862, "secs": 295}
```

5ed687b3d (`/tmp/voids_split2`, 2026-10-09 02:33 to 02:41). The second batch (`onE`, `onW`, `onH`,
`onP`, `onOCC`) died before a RESULT line:
```
base.log  RESULT {"ENERGY": "0", "WINDOW": "0", "HAZARD": "0", "PAYMENT": "0", "OCCPAY": "0", "total_net": 44331.98, "occupier": 3077.68, "void": 0.0, "bad_debt": 4985.11, "revenue": 238931.76, "n_records": 155862, "secs": 517}
on.log    RESULT {"ENERGY": "1", "WINDOW": "1", "HAZARD": "1", "PAYMENT": "1", "OCCPAY": "0", "total_net": 43536.98, "occupier": 3112.21, "void": 39.78, "bad_debt": 4963.29, "revenue": 237927.86, "n_records": 155862, "secs": 513}
offE.log  RESULT {"ENERGY": "0", "WINDOW": "1", "HAZARD": "1", "PAYMENT": "1", "OCCPAY": "0", "total_net": 43914.14, "occupier": 3541.03, "void": 0.0, "bad_debt": 4976.59, "revenue": 238968.74, "n_records": 155862, "secs": 517}
offW.log  RESULT {"ENERGY": "1", "WINDOW": "0", "HAZARD": "1", "PAYMENT": "1", "OCCPAY": "0", "total_net": 43942.43, "occupier": 2661.4, "void": 39.78, "bad_debt": 4971.57, "revenue": 237890.77, "n_records": 155862, "secs": 517}
offH.log  RESULT {"ENERGY": "1", "WINDOW": "1", "HAZARD": "0", "PAYMENT": "1", "OCCPAY": "0", "total_net": 43536.98, "occupier": 3112.21, "void": 39.78, "bad_debt": 4963.29, "revenue": 237927.86, "n_records": 155862, "secs": 521}
offP.log  RESULT {"ENERGY": "1", "WINDOW": "1", "HAZARD": "1", "PAYMENT": "0", "OCCPAY": "0", "total_net": 43536.98, "occupier": 3112.21, "void": 39.78, "bad_debt": 4963.29, "revenue": 237927.86, "n_records": 155862, "secs": 519}
```

91a798172 (`/tmp/voids_split3/RESULTS.txt`, 2026-10-09 05:14). `origin` is unpatched origin and
`triadfix` is origin plus §2's fix. No lever patch was applied in either; the flags are the
driver's defaults:
```
origin    RESULT {"ENERGY": "1", "WINDOW": "1", "HAZARD": "1", "PAYMENT": "1", "OCCPAY": "0", "total_net": 43536.98, "occupier": 3112.21, "void": 39.78, "bad_debt": 4963.29, "revenue": 237927.86, "n_records": 155862, "secs": 366}
triadfix  RESULT {"ENERGY": "1", "WINDOW": "1", "HAZARD": "1", "PAYMENT": "1", "OCCPAY": "0", "total_net": 43536.98, "occupier": 3112.21, "void": 39.78, "bad_debt": 4963.29, "revenue": 237927.86, "n_records": 155862, "secs": 363}
```

**What stays open:** the 910 at 5531ef8a6 itself was never re-measured. The book-reprice route in
§1 (`_portfolio_margins.settled`) is inferred, not isolated. The debt line's re-grade should read
the WorldDebtBook and payment-belief effects of the triad fix after 2019.
