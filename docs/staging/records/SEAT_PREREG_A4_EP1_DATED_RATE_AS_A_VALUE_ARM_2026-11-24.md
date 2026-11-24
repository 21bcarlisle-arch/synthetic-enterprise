**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `EP1` · **Claim:** `a4-ep1-dated-rate-graded-as-a-value-arm`

# Pre-registration: EP1's dated discount rate, graded as a value arm (A4), 24 Nov 2026

**Filed before the result exists.** When this was written, `/var/tmp/vtn-out/ep1/` held no run and the
configuration had never run on any book. This is step A4 of
`SEAT_RECORD_THE_DEFAULT_OFF_SWITCHES_AND_THE_ORDER_THEY_FLIP_IN_2026-11-24.md`. The standing switch
`EP1_DATED_DISCOUNT_RATE_IN_THE_STANDING_POLICY` stays `False`. Nothing on origin changes.

## 1. What is run

- **One configuration, `ep1`.** A's switches are set on both policies (`renewal_belief_by_ending_term=True`,
  `retention_cut_at_the_flips=False`). On top of them, `renewal_discount_rate_dated=True` is set **on
  `VALUE_ARM_POLICY` only**. The control arm therefore runs exactly A's code path.
- **The comparator is A, already on disk** (`/var/tmp/vtn-out/A/`, s.12g, run 24 Nov). So `ep1 − A` is a
  one-variable difference: the dated rate in the value arm, and nothing else.
- **Book, pair and shape.** Book 61118, churn pair 13131/14141, the s.12g driver shape.
  - Driver: `/var/tmp/vte-driver/driver_ep1.py` (sha256 `181120bce22e…`), derived from
    `/var/tmp/vtn-driver/driver_rankq.py` (`16f15aa39689…`).
  - Grader: `/var/tmp/vte-driver/grade_ep1.py` (`0f1156fe156c…`). Its `load`/`hh`/`comb`/`diff` are copied
    unchanged from `grade_rankq.py`: the household unit, 2,000 household resamples, seed 20261117, and the
    twin's control-arm household-years as the divisor.
- **The tree.** `/var/tmp/value-test-ep1`, a detached worktree at `870201d1e7`, plus `rankq.patch` (the
  rankq tree, byte-identical: `0cc0a709…`), plus the decision path of `63f7faeba`:
  - `clv_three_horizon.discount_rate_at`;
  - the `discount_rate` pass-through in `value_based_renewal` and `renewal_rate_chain`;
  - the policy field, hand-placed because `decision_policy.py` has drifted. `CURRENT_POLICY` there does
    not read the switch.

  The pin is `/var/tmp/vte-driver/ep1.patch.sha256` (`1ca5b5b0…`), and the driver refuses any other diff.
- **No rankq arm was already armed**, so there was nothing to ride. The rankq reader
  (`s12g-rankq-is-graded-when-it-ends`) is still LIVE, and its next arm (A2 or A3) is its own.
- **An in-run shadow measurement.** For each value-arm renewal that starts on or after 1 Oct 2023, the
  driver also calls `renewal_margin_uplift` at the flat 0.10 and logs both chosen margins. The shadow
  result is never returned to the chain. That gives the price count exactly, without a second run.
- **The box.** It is launched through `launch_long_job`. Its wrapper waits for B11 M7's readout
  (`/var/tmp/b11m7/readout.json`) and then for no land10, seed_family or census unit to be live. That
  puts it sixth in `SEAT_RECORD_POST_RANKQ_BOX_ORDER_2026-11-24.md`. It refuses after 96 h of waiting.
  Its last run took about 14 h at a peak of 11.8 GB (rankq).

## 2. Mechanism, from the code (before any number)

The arm maximises `p·c(m)·A(r) − (1−p)·D − stock_loss(p) − carrying(r, revenue)`
(`value_based_renewal.expected_value_gbp`, `decide_margin`):

- the annuity `A(r)` falls by about 10% at 12.3%;
- `D` (the departure cost) and the stock loss are not discounted;
- the carrying cost of late payment rises with `r` and with revenue.

The commit `63f7faeba` already measured one consequence on its probe: **the margin did not move**
(74.0 at both rates). Where `D = 0` and there is no carrying cost, `r` only scales the objective. Where
it does bite, every term that grows heavier penalises a lower `p` or a higher revenue. So **a move can
only be downward.**

## 3. Predictions

- **V1 (validity).** The control arm is byte-identical to A's: 0 households' net moves, and the
  control decisions are equal on both seeds.
- **V2 (validity).** Every value-arm renewal and scored decision dated before 2023-10-01 is identical to
  A's.
- **If V1 or V2 fails,** the run is **VOID** as a one-variable arm, and nothing below is graded.
- **P1 (prices).** Take the value-arm renewals priced on or after 1 Oct 2023 and also priced at 0.10.
  - The share whose chosen margin moves is **at most 0.25**. Point guess: under 0.10.
  - **None moves up.**
  - REFUTED by a share above 0.25 or by any upward move. An empty shadow log also refutes P1, because
    then the switch never reached a decision.
- **P2 (the gap, primary).** `ep1 − A`, whole advantage over the flat book, in GBP per household-year:
  - **|point| ≤ 0.50, and the 95% interval spans zero** (STRADDLE).
  - The sign is **predicted negative, with low confidence**. Lower margins in a window that ends in
    June 2025 give up margin before the retention they buy can pay back.
  - The mechanical part (moved price × MWh × months left, before any dice diverge) is predicted under
    **£0.10/hh-yr**. Most of any spread will come from a moved household's later dice, which are worth up
    to ±£3,000 per household (see the movers in `grade_rankq.out`).

## 4. What each outcome changes

- **STRADDLE (predicted).** On one book, the dated rate makes no decision difference that can be
  resolved. The value arm then takes the dated rate **on knowledge grounds** in the next value-test
  configuration: it is Ofgem's sourced 12.3% from period 11a, and 0.10 is not sourced for post-Oct-2023
  terms. That is recorded as one change, and A2 or A3 is not re-based on it mid-flight. The standing
  switch stays off, because on CURRENT it moves no flat-rules decision.
- **ABOVE.** The same as STRADDLE, and this record is the value arm's evidence for it.
- **BELOW.** The dated rate costs the value arm money inside the window. It stays off in the arms, and
  a finding is filed on whether the loss is horizon truncation (terms that run past June 2025) or
  mis-pricing.
- **P1 REFUTED, with an upward move.** The mechanism in §2 is wrong. A defect finding goes on
  `decide_margin` before any arm takes the switch.

## 5. Reverse

- `systemctl --user stop longjob-a4-ep1-dated-rate-value-arm`
- `rm -r /var/tmp/vtn-out/ep1`
- `git worktree remove /var/tmp/value-test-ep1`
- revert this file.
