**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `B10_competitor_switching_response`

# Pre-registration: what the chase-off run must show, written before it finishes

**Written 2026-08-28, while the run is executing.** The chase-off A/B was launched at 11:17 UTC and
takes ~35 minutes. This document is filed now so the prediction cannot be fitted to the answer.

## The reversal being explained

The three-arm A/B was re-run at 10:47 on the current world. Against the 07:36 artefact:

| | 07:36 | 10:47 | delta | churned |
|---|---|---|---|---|
| control (flat rules) | £153,244.79 | £159,423.50 | **+£6,178.71** | 36 → **35** |
| value arm (per-customer) | £157,913.20 | £154,699.49 | **−£3,213.71** | 39 → **46** |
| level arm (flat @ £44.50) | £158,484.58 | £164,326.41 | **+£5,841.83** | 38 → **38** |
| selection | −£571.38 | −£9,626.92 | −£9,055.55 | |

Two things happened between those runs and I could not separate them from the P&L alone:

- **The chase** — `5f50408c6`, 08:25, gave the market the ability to defend against a company that
  undercuts it.
- **A clock repair** — another lane's *uncommitted* `simulation/settlement_clocks.py` re-derives
  `total_net_gbp` after the bad-debt and debt-recovery mutations, and their own note puts the
  discrepancy it fixes at £39,962.17. `total_net_gbp` is the field every number above is read from.

## The discriminator is the churn roster, and it is already visible

**A monetary re-derivation cannot change who churned.** The clock repair re-computes a scalar from
rows; it does not move an account from stayed to left. So the churn column separates the two causes
without waiting for anything:

- **Control −1 and level +0.** Essentially unmoved, as a clock repair predicts and as a defending
  rival also predicts for these two arms — the control prices at £2.00 of margin and the level arm at
  £44.50 flat, and neither is the arm that prices *individual* customers high.
- **Value arm +7 churned accounts, 39 → 46.** Nothing about re-deriving a monetary total can do
  this.

And the money moves the same way: control and level both rose by ~£6k — a common tide consistent
with the clock repair lifting every arm — while the value arm alone fell. Its −£9,392 change in
advantage is roughly the common tide it did not receive plus its own loss.

**So the reading I hold before the answer is: the clock repair explains the common ~£6k level shift
across all three arms, and the chase explains the value arm's seven extra churned accounts and its
loss relative to that tide.** That is an inference from two artefacts, not a measurement.

## What the chase-off run must show if that reading is right

Run: the identical three-arm A/B on the identical tree, with `chase_per_quarter: 0.0` supplied
through a scratch curriculum file (the committed `docs/design/COMPETITOR_AGGRESSION.yaml` is
untouched — the wrapper points `competitor_reference.AGGRESSION_PATH` at a scratch copy, so exactly
one input differs).

**Predictions, in falsifiable order:**

1. **The value arm's churned-account count falls back toward 39** — the single most direct
   consequence. If it stays at 46, the chase is not what churned those seven accounts and my reading
   is wrong.
2. **The control arm's net margin stays near £159,423** — it is post-clock-repair either way, and the
   chase should barely touch an arm pricing at £2.00 of margin. If the control moves materially,
   something other than the two named causes is in play and neither explanation stands.
3. **The value arm's advantage returns to positive**, near the +£4,668 of the 07:36 run once the
   common tide is accounted for. This is the weakest of the three: it is a difference of
   differences on a 210-account book, and it can fail while (1) holds.
4. **The level arm barely moves.** It prices flat, so a rival that follows a company *down* has
   almost nothing to respond to.

**What would refute the whole reading:** the value arm's churn unchanged at 46 with chase off. That
would mean the seven accounts left for a reason neither candidate names, and both explanations go
back in the box.

## What this is NOT

Not a claim that the defence leg is worth having, and not B10 at L3. It is one comparison on one
book with no seed replication. What it can do that yesterday's instrument could not is resolve
anything at all: **the churn roster is a set of accounts, not a rate on 17 binary decisions**, and
the P&L is continuous. That is the whole reason this reading exists where the 2026-08-28 ladder
comparison returned nothing.

## Still live
