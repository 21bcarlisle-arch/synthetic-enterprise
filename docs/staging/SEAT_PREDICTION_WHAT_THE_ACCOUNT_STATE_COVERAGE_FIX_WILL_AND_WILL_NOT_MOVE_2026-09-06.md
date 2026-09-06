**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# PREDICTION — what the account-state coverage fix will and will not move on R1's ceiling

**Written 2026-09-06 22:31 UTC, BEFORE the re-measure.** The run that answers it
(`python3 -m simulation.run_phase2b`, launched 22:26) was still executing when this file was
written. Filed here rather than in the finding so that the finding cannot be read as a prediction
made after its own answer.

Lane 0 direction: *"Populate the pair fields on every household so R1's pair rung can carry a
three-way split ... perceived_bill_saving_gbp, portfolio_premium_pct and mean_recent_margin_rate
are the fields that collapse 164 households to 69. At full coverage a three-way split gets ~55 per
fold and ~14 per cell."*

## State established before the run

The working tree already carried the coverage mechanism, uncommitted and **never once executed** —
`simulation/run_phase2b.py`, `simulation/svt_rates.py` and both copies of
`company/*/renewal_rate_chain.py` are additive over HEAD (symbol sets diffed; no HEAD symbol is
deleted by any of them). Every run output on disk, including the newest
(`run_output_cc8caa857_20260906T195137Z.json`), was produced by the PRE-fix code: its
`account_state_log` carries `mean_recent_margin_rate` for **0** households and
`svt_rate_gbp_per_mwh` for **0** of its 449 gas rows.

So the numbers in `docs/observability/r1_inference_ceiling.json` and in A49's own origin note are
both readings of a book the fix has not touched.

## The prediction

1. `svt_rate_gbp_per_mwh` rises from 146 households toward 164 — the gas-only accounts gain the
   field, because the per-fuel dispatch now reads the gas cap the regulation commons has carried
   since W3_1b.
2. `mean_recent_margin_rate` and `portfolio_premium_pct` rise from 149 toward 164 — short of 164
   only by accounts with no completed prior term of that commodity, which is an honest absence and
   not the accounting accident being fixed.
3. **The headline pair rung does NOT reach full coverage, and the direction's premise is wrong on
   one of its three fields.** `perceived_bill_saving_gbp` is `decision_only` in the instrument's
   own scope table — a renewal-window quantity, and most of this book is on indexed products that
   never renew. Its 69 households are the truth about the field. If the reported winner still
   involves it, the three-way split still refuses for coverage, and the refusal is correct.
   Manufacturing a value for an account that never renewed would invent the coverage rather than
   record it — the instrument says so in `OBSERVABLE_FIELD_SCOPE` and it is right.
4. Where the magnitude actually moves is the **whole-book pair rung** (account-state fields only,
   all 164 households), which already carries an unrefused honest point estimate and now gets two
   fields at full coverage plus a per-fuel spread instead of an electricity-only one.

I do not predict which way (4) comes out. If the whole-book rung's selection-corrected verdict
still reads `cannot tell`, that is the answer and it goes on the page.

## How it is refuted

Re-run `tools/r1_inference_ceiling.py` against the post-fix run output. (2) refuted if either field
stays at 149. (3) refuted if the pair rung's `honest_point_estimate` stops refusing without
`perceived_bill_saving_gbp` having gained households.
