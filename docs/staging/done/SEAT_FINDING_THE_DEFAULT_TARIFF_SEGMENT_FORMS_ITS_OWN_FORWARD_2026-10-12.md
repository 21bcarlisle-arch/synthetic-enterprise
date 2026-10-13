**Severity:** LATENT · **Lane:** W4_the_wall · **Epoch:** unassigned · **Atom:** `unminted`
**What:** a world-only number reached two supplier decisions (hedge sizing, mover offer cost) · claim `four-principles-the-default-tariff-segment-forms-its-own-forward`
**Status:** pre-registered 2026-10-12 before the arms launched (14:48Z): first committed `70862ebbe` at 14:47Z, which never reached origin because the merge-gate refused a base advance; re-landed byte-identical as `02ff661bd`. Graded below the same day

# The default-tariff segment forms its own forward

**Fate (2026-10-13, clear-the-decks):** DONE -- 5187cb21a svt_product now asks the forward door and is controlled; the hedge's agreed-price open question this doc raised is independently resolved by 61c122683. Minor residue (move-with-us SVT cost untested, since move-with-us is off; a NAMED_DEBTS architecture row not yet built) is explicitly handed to other work, not orphaned here.

## What the drawn item said, and what was true of it

The item cites `tools/seam_value_flow.py`, a finding
`SEAT_FINDING_THE_DEFAULT_TARIFF_SEGMENT_HANDS_THE_COMPANY_THE_WORLDS_FORWARD_2026-10-12.md`, and a
done-means of deleting a `NAMED_DEBTS` row from
`tests/architecture/test_a_supplier_input_is_never_built_from_a_world_only_source.py`. **None of the
three exists** on origin/main, in the shared tree, in any worktree or in any git ref (checked
2026-10-12). They were held by the parent claim `four-principles-a-typed-seam-record-for-run-loop-inputs`,
which never landed them. So that part of done-means cannot be met here. What *can* be checked is the
defect, and it is real: `simulation/svt_product.build_svt_schedule` wrote
`company_forward_price_gbp_per_mwh = sim_fwd` on every segment.

## Which readers a default-tariff segment actually enters (traced in `simulation/run_phase2b.py`)

| Reader the item named | Does an SVT segment reach it? | Why |
|---|---|---|
| renewal-cut margin, save offer (`_price_match_inputs`, `expected_margin`) | **no** | inside `if term_index >= 1 and commodity == _decision_leg and not _indexed_tariff`, and `_indexed_tariff` includes `svt` |
| acquisition gate (`decide_acquisition`, replacement path) | **no** | same branch |
| hedge desk: `decide_term_hedge` (VaR sizing), electricity and gas | **yes** | the `else:` arm after `deemed`/`flex` takes `svt`; gas `elif` takes everything but `pass_through` |
| hedge desk: `open_term_hedge` agreed price | **yes** | same arm; feeds `hedge_pnl_gbp`, a reporting decomposition that no book total sums |
| move-with-us offer `cost_per_mwh` | **yes** | runs for every tariff type on the decision leg |
| basis-risk log `tariff_error_pct` | yes (reporting) | read 0.0 for every SVT segment; it will now report the real gap |

So the item's list of four was half right. The book can move through two routes only: the **hedge
fraction** (the world's settlement prices the hedged share at the world's forward and the naked share
at spot, plus capital cost) and **move-with-us** take-up.

## The hedge's agreed price: the company's belief or the market's forward?

**Decision: the company's own estimate, the same as every fixed term today.** `HedgeDesk.open_term_hedge`
documents its agreed price as "the forward the company locked at tariff signing … company-observable";
the fixed electricity and gas paths both pass `company_fwd`. Giving the SVT segment the market's
forward while fixed terms book their own belief would make one desk book two products by two rules.
That would be the inconsistency this item exists to remove.

**The other reading is better, and it is a separate question, filed here and not built.** A real forward
trades at the market's quote, which a supplier can see. Its *belief* drives the tariff and the sizing,
not the price it pays the counterparty. On that reading the agreed price should be the market's
forward on **both** products, and `sim_fwd` (PIT-safe, built from records before the date) is the
world's market forward, so it is an observable and not world-only truth. This touches only the
reporting decomposition (`hedge_pnl_gbp`), not the book, so it does not block this change. It is recorded
below as an open item.

## Inputs printed before predicting (both forwards at real segment starts)

company / world ratio, electricity: 2017-01 1.32 · 2019-04 0.91 · 2021-10 1.56 · 2022-04 1.11 ·
2022-10 1.36 · 2023-01 1.24 · 2023-07 0.91 · 2024-04 1.09 · 2025-01 1.31. Gas: 1.30 · 0.85 · 1.42 ·
1.04 · 1.15 · 1.37 · 0.86 · 0.85 · 1.29. The company's estimate is usually above the world's, most of
all in winter and in rising markets.

## Pre-registration (written before either arm ran)

Run: `/var/tmp/se-svt-fwd/arm.py`, 40 founders, budget 0, default book, one seed. Arm `head` makes the
door return its fallback (bit-for-bit HEAD); arm `own` uses the company's estimate. One variable.

- **P1.** Every SVT segment asks the door. Fewer than 1% of asks fall back to `sim_fwd`, because both
  records start before 2016.
- **P2.** On SVT segments the median company/world ratio is above 1.0, between 1.05 and 1.35.
- **P3.** The mean decided hedge fraction on SVT segments is not lower in `own` than in `head`
  (VaR's unhedged allowance falls as the forward rises). It may be equal if quarterly tenors sit at
  the floor.
- **P4.** Renewal, save and acquisition counts are identical across arms unless move-with-us follows
  differ. If the follows are identical, any difference in renewal or save counts is a defect in this
  trace.
- **P5.** `total_net_gbp` moves by less than 1% of its own magnitude. Sign predicted: **up**, on the
  thesis that more hedging into the 2021–22 rise outweighs 2023's fall. Low confidence; F11 says to err
  against the thesis, so a fall is the outcome I would believe first.

## Result (graded 2026-10-12; arms `head` and `own`, 40 founders, budget 0, default book)

A first launch crashed in world build in both arms (`DwellingNotDrawn` for SYN-2016-012). That was a harness
defect: `arm.py` imported `simulation.svt_product` before `m_scale` patched the founder count, so
customers were built for the curriculum's 400 and dwellings for 40. The fix was to patch first. No
segment was reached, and the predictions above were not edited.

| | Predicted | Measured | Verdict |
|---|---|---|---|
| P1 | every segment asks; <1% fall back | 1,500 asks in each arm, **0** fallbacks | **held** |
| P2 | median company/world 1.05–1.35 | **1.090** (electricity 1.100, gas 1.062) | **held** |
| P3 | mean SVT hedge fraction not lower | 646 SVT hedge decisions: **0.8542 → 0.8562** | **held** (small: most quarterly tenors sit near the 0.85 floor) |
| P4 | renewal/save/acquisition unchanged unless follows differ | move-with-us is **off** in this policy (0 rows, so that route went untested). Every `(customer, date, event_type, occasion)` is **identical** (25 renewed, 6 churned). **But** 8 of 31 events carry different rates. | **half wrong, see below** |
| P5 | \|Δnet\| < 1%, sign up | `total_net` 31,448.84 → **31,459.77 (+£10.93, +0.035%)**; bad debt and settled rows identical | **held** (sign held; F11 said to doubt it, and it held anyway at this size) |

**Where P4 was wrong, and what the trace missed.** The table above says the renewal cut cannot be
*reached* from an SVT segment, and that is still true. What it missed is a second-order path: the
company's **portfolio learning premium** (`dynamic_pricing_log`, `margin_feedback_log`) learns from the
realised margins of *every* term it holds, SVT segments included. The SVT segments now hedge slightly
more, so they realise slightly different margins. The company then learns a different premium and
strikes fixed renewals elsewhere in the book differently: 64 `unit_rate_after` moves, −£0.60 to
+£0.47/MWh; 46 contracted rates move, ±£3.1/MWh. No renewal decision flipped on this seed. This path
is legitimate: the company learning from its own results is exactly what should happen. It is noted so
that "an SVT segment cannot touch the renewal cut" is not repeated as true.

**Book diff.** Net +£10.93; enterprise value 17,446.04 → 17,461.46; hedging value-add
−51,768.84 → −51,747.80. On one seed and 40 founders this is a fidelity correction with a
near-zero book effect. It is not a lever, and it is not presented as value created.

## Disposition and what stays open

- **Built** in the same claim: `simulation/svt_product.py` asks the door; control
  `tests/simulation/test_the_default_tariff_segment_carries_the_companys_own_forward.py` (three
  mutations, each red).
- **Not met, and why:** the item's done-means names a `NAMED_DEBTS` row in
  `tests/architecture/test_a_supplier_input_is_never_built_from_a_world_only_source.py`. That control,
  and `tools/seam_value_flow.py` which would feed it, are not in the tree, so there is no row to delete.
  Whoever lands that control should leave `svt_product` off its debt list.
- **Open (filed, not built):** the hedge's agreed price on *both* products is the company's belief.
  A real forward trades at the market's quote. It touches only the `hedge_pnl_gbp` decomposition, and
  it is one question for both products, not a per-product patch.
- **Untested route:** the move-with-us offer cost now carries the company's forward too. It is off in
  the current policy, so this run could not see it.
