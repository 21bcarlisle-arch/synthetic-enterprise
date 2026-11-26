**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# An offered leaver is answered on a die the floor did not re-draw. The rankq −£2.45 is that, not the ranking

*The answer to the 25 Nov 12:31 ruling, s.3 (`docs/staging/advisor/done/DIRECTOR_RULING_K8_FOR_WORLD_MODELS_FORWARD_BANDS_YES_AND_STEP_BACK_ON_THE_RETENTION_RESULT_2026-11-25.md`).
Pre-registered before reading: `docs/staging/records/SEAT_PREREG_THE_RANKQ_GAP_DECOMPOSED_BY_RENEWAL_AND_ERA_2026-11-25.md`.
The knowledge page (K8) is `docs/market_research/what_happens_at_the_end_of_a_fix_and_whether_the_world_does_it_2026-11-25.md`.
No run was launched. Readers: `/var/tmp/vtn-driver/s12g-decomp/{decomp,twin_only,defect_share}.py`, over the s.12g
records in `/var/tmp/vtn-out/{twin,rankq}/`.*

## For the director, in plain English

You were right to doubt it. In the world as we built it, a retention offer should lose money. Most people at the
end of a fix stay anyway, and a 3–8% discount changes the minds of about one leaver in twenty. The discount
paid to the stayers costs about eight times what the few extra stayers bring in. So the supplier that offers less
should earn more. That is what reality says too: inert customers mostly stay, and better offers move very few of
them.

The run said the opposite because of a wiring fault in how we test, not in the market. To measure noise, the test
harness re-rolls each household's renewal dice. The retention offer was still reading the *original* dice. So
any household that was leaving, once offered a discount, got a fresh coin toss and stayed about 60% of the time
instead of about 5%. Offers looked roughly twelve times more effective than the world says they are, so the arm that
made more offers "won". Thirty-four household-runs kept this way, most of whom then stayed to 2025, account
for −£3.33 of the arm's −£3.43 per household-year.

It is fixed and has a test. The −£2.45 is void, not a finding. So are the other graded comparisons run on the
same harness where both arms make retention offers (the s.12g family: twin, cut, A, rankq; and today's A4 EP1
grade, `20b14f3ed`). They need re-grading on the fixed code before anyone reads them.

## 1. The decomposition (the ruling's first ask)

On the world's stated probabilities, per offered renewal (both seeds; the desk's term margin, as no realised
per-renewal margin exists):

| Era | Twin offers | P(stay anyway) | World uplift | Mean discount | Discount to stayers | Margin the offer kept |
|---|---|---|---|---|---|---|
| pre-cap | 192 | 0.60 | +0.019 | £20 | £2,351 | £237 |
| cap era before 2021 | 13 | 0.35 | +0.018 | £33 | £178 | £67 |
| 2021–23 | 4 | 0.58 | +0.012 | £51 | £116 | £4 |
| 2024–25 | 2 | 0.03 | 0.000 | £68 | £4 | £0 |
| **all** | **211** | | | | **£2,649** | **£308** |

Net: −£2,342 for the twin (−£0.21/hh-yr) and −£899 for rankq (−£0.08/hh-yr). On the world's stated physics,
**rankq's fewer offers are worth +£0.13/hh-yr to it**, the sign the director expected. The 2021–23 era, where an
offer could have been dearer than the default, holds 4–6 offers per run and cannot move anything.

What happened instead. The whole gap sits on households the twin offered and rankq did not (TWIN_ONLY, −£30.3k
whole-advantage). Of those, 94 ended with the same tenure in both runs and differ by +£629, in rankq's favour, as the
table predicts. 31 were kept longer by the twin: 2,489 more bills, −£38.7k. The worst ten carry 82% of the
gap. Each looks like SYN-2016-241: offered at its first renewal (31 May 2017), P(stay) 0.777 → 0.790 at the
offer, roll **0.946**, renewed under the twin. Under rankq it was not offered and left. It then rode the default
for 36 monthly decisions and stayed to 2025. That is worth £3,652.

**The "default margin on un-offered stayers" line** is real and is the cause of the scale: a household kept in 2017
pays default margin for eight years (`what_a_kept_household_is_worth_beyond_one_term_2026-11-24.md`). It
multiplies whatever the offer keeps. It does not decide the sign.

## 2. The cause

`tools/run_value_cycle_ab.noise_floor(redraw_key="churn_roll")` re-draws the roll with `setattr` on
`simulation.customer_events.churn_roll_for_renewal`. `simulation/retention_offer.py` imported that function **by
name**, so `answer_retention_offer` read the un-patched roll while the household's full-rate decision read the
patched one. A leaver on the redrawn die (`roll > P(stay)`) was then "held" whenever the *original* roll was low.
Measured: 52 of the twin's 211 offers and 23 of rankq's 77 renewed on a roll above even the offered P(stay); of the
88 offered renewals above it, 52 renewed (0.59, about the mean P(stay)). Un-offered renewals agree with their roll
in 99% of cases, so the recorded roll is the one the full-rate decision used.

Two `run_phase2b` sites had the same by-name binding: the save-on-loss answer at a scaled response, and
move-with-us's next roll. All three now read the module at call time. An un-patched run is byte-identical, because
the attribute is the same function. Control:
`tests/simulation/test_an_offer_is_answered_on_the_roll_the_floor_redrew.py`. It covers the three-way partition
on a patched roll, plus an AST leg refusing any top-level by-name import of the roll in `simulation/`. Both legs
were red with the old import restored.

**Not yet re-asked:** which earlier floor runs with `redraw_key="churn_roll"` made offers or saves. The elasticity
key is unaffected. Every value-cycle grade since `churn_roll` became the key (10 Sep) is suspect where offers differ
between arms.

## 3. The thesis, restated (the ruling's third ask; M2, M3, the 13 Nov utility ruling)

The thesis is **not** "the per-customer arm makes more money". It is that a per-customer method finds the
households where a different offer *creates* value, with both sides of the share counted, and that a flat rule cannot.

- **What a money result can tell:** whether the supplier's share rose. Nothing more.
- **What it cannot tell:** whether value was created. A discount to a household that would have stayed is a
  transfer to the household, and it shows as a loss. A default margin on an inert household is a transfer to the
  supplier, and it shows as a gain. A retention discount that keeps a household on a deal that suits it, at a cost to
  serve below what it would pay elsewhere, is creation. Money alone cannot separate the three.
- **What measure would:** per household, the household's weighted gain (money, cash flow, certainty, control,
  time, carbon, above the floor) plus the supplier's margin, with transfers shown beside it and not netted in.
  Here, the twin's extra offers were, on the world's real physics, about 97% transfer to stayers. The ~2% that
  changed a decision kept a household paying the default, which is mostly a transfer the other way. Neither arm
  created measurable value through this lever. That is the expected answer for a blanket discount, and the reason
  Ascarza says to target by uplift.

## 4. The next run, only if still needed (the ruling's fourth ask). Predictions filed now

Before any re-run, the world's 2021–23 leave rate should be looked at (knowledge page §3, reading 2). It rises when
the record says switching collapsed. That is a world-fidelity question, decided blind to company results.

If the director wants the s.12g question asked again: **re-grade rankq against twin on the fixed code**. Same seeds
and books, about 11 h. It settles whether, with offers answered on the real die, offering less makes the supplier
more money.
- **R1.** The rankq − twin whole advantage is ≥ 0: point +£0.13/hh-yr (−£1.0 to +£1.5), the sign set by the offer
  table in §1.
- **R2.** Offered renewals kept on a roll above the offered P(stay): **0** in both arms (the control's property).
- **R3.** The control arm moves by less than £0.3/hh-yr between runs. Today's −£0.97 is partly this defect, through
  the control arm's own "current"-policy offers (8 of 30 off-roll).

It answers a money question only. The thesis question (§3) needs the utility measure, and no current run produces it
for retention.

**By regime (26 Nov ruling, "watch out for weird energy crisis years").** Pre-registered in the knowledge page §7
before any build or run: the thesis result rests on regimes 1 (pre-cap) and 2 (cap era), read separately. Those are
the two where the world's leave rate passes the check against the record. Regimes 3 (crisis) and 4 (after 2024) are
reported beside them and never pooled in. R1 becomes R1a–R1c there. The re-grade runs after fix 0 and the regime-4
anchor refit, on one capture → refit → capture.

## Correction beside a claim

The direction item named the ruling's question keys as `b455c078aa40`, `30860a9d6e96` and `e500f915012f`. The
register's own keys for this ruling are `bf3bddc83e5e`, `53c2cb2a27d5` and `6949a76857a7`. Those are the ones closed.

NEXT: none -- the re-grade waits on the director's word (s.4); the 2021-23 world leave rate is a fidelity item
