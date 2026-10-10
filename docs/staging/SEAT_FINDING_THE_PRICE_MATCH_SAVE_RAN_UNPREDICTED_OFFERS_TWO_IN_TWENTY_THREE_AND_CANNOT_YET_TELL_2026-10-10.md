**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`

# The price-match save ran without predictions, offered 2 of 23 held invitations, and on net we cannot yet tell

*Worker, 2026-10-10 ~12:40. Direction item `the-reactive-save-on-the-loss-notice-is-live-in-the-run`.
Read-only on `/var/tmp/save_live/` and `/var/tmp/se-save-live`. The interactive session is still
working in that worktree (it was appending tests and running `suite.sh` while I read it), so this
finding grades the pair. It does not land the switch, and it does not touch that tree.*

## (a) The predictions were never filed, and now they cannot be

The focus item asked for predictions before `/var/tmp/save_live/compare.json` was written. Nobody
filed any: there were none in the staging root, none in the worktree, and none on origin.
`compare.json` was written at **10:03**. This tick was drawn after 12:20. **Anything I wrote now
would be a postdiction, so I have not written one.** The off arm's total net (GBP 407,560) and the
on arm's result were both known before this sentence was written.

This leg of the item's DONE is spent for this pair. Only a fresh pair, with its predictions filed
first, can satisfy it.

## (b) What the pair shows (both arms at HEAD `7b3950cd7`, production book, to 2025-06-07)

| | off | on |
|---|---|---|
| total net, GBP | 407,559.58 | 409,142.02 |
| on − off | | **+1,582.44** |
| renewal departures | 107 | 107 |
| loss notices answered | – | 105 |
| invitations held (from 18 Jul 2022) | – | 23 |
| **offers made** | – | **2** |
| saved | – | 1 |
| stayer price moves (11,612 terms) | – | **0** |
| offers to known-vulnerable | – | 0 |
| vulnerable leavers not offered | – | 4 |
| vulnerable twin shortfalls | – | 0 |

**The paired interval.** The arm output carries no per-household net, so I cannot bootstrap over
households. I can bound it exactly anyway. The two arms differ only on the two offered households,
because there were no stayer moves and departures are equal. Each household is decided on the
world's same roll, `saved_on_loss_notice(roll, p_offer, p_save)`, which returns true iff
`p_offer < roll <= p_save`:

- `PROS-2022-0400`, electricity, 2023-12-21: P(stay) 0.6685 → 0.7686, so it is saved with
  probability **0.100**. This is the one the run saved, and it carries the whole +1,582.
- `SYN-2016-030`, gas, 2025-01-23: P(stay) 0.2710 → 0.2741, so it is saved with probability
  **0.003**. It was not saved.

Over the world's roll, on − off is therefore 0 with probability ≈ 0.90 and about +1,580 with
probability ≈ 0.10. Its expectation is **≈ +GBP 160 over 9.5 years on a GBP 407,560 book**. The 95%
interval runs [0, ~1,580] and includes zero. **Result: cannot yet tell.** The realised +1,582 is a
lucky one-in-ten draw, and it should not be read as the save's effect.

**Stayers: graded, and they hold.** No stayer's price moved in either direction across 11,612
account terms. No known-vulnerable household was offered less than its twin.

## Why the switch is nearly inert: the renewal sits under the company's own cost floor

The price match returns None unless `max(cost_floor, default × (1 − gap)) < renewal`. Of the 23
held invitations, the gap was published on all 23. In **21 of 23 the company's own renewal unit rate
is BELOW the cost floor** passed in, which is `company_fwd + locked_policy + locked_network`
(`simulation/run_phase2b.py`, the price-match inputs block). Examples:

| term start | renewal | floor | default × (1 − gap) |
|---|---|---|---|
| 2024-01-18 | 247.0 | 253.3 | 260.2 |
| 2024-07-20 | 196.3 | 201.8 | 215.3 |
| 2024-12-10 | 215.7 | 228.3 | 223.4 |
| 2025-03-21 | 612.0 | 700.2 | 233.0 |

On every row but the 612.0 outlier, where it is 14% above, the floor sits a steady 2–6% above the
renewal. That steadiness is odd against how a renewal
desk works. **I have not established which explanation is true.** The ones the evidence allows are:

1. the floor and the renewal price are struck at different moments or on different forwards;
2. one of them is on a different basis (losses, VAT, or a hedge cost that one includes and the
   other does not);
3. the company really is renewing these households below cost.

Under (1) or (2) the switch is being refused by a definitional mismatch, not by the market. Under
(3) the finding is the renewal pricing, not the save. Either way, the save as sized cannot fire on
most of the book. **The next run should not be redone with predictions until that is settled.**
A one-variable test settles it: print `renewal_pricing_engine._cost_floor` and the price-match
floor for the same term, side by side.

## What this leaves for the item's DONE

- `activated.value` true on origin with price-match sizing: **not landed by me**. The interactive
  session has the switch, the sizing and the research doc in hand.
- The pair on origin beside its predictions: **impossible for this pair** (see (a)).
- Stayer moves graded: **done above (0)**.
- Net: **cannot yet tell**, with an expected effect of about GBP 160 against an interval that
  includes zero.
