**Severity:** LATENT · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality` · **Twin:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# Pre-registration: billed-minus-used per account on run_output_6af7fd0bfd (2026-11-19)

Written before `tools/couple_w2_36_d48.py` was run on `docs/reports/run_output_6af7fd0bfd_20261118T070221Z.json`.
What I already know: on the 8a300fa561 book, actual, smart and prepayment bills equal metered use exactly
(D48 finding, 2026-11-18). Estimated account-months net to +0.06 kWh signed. Annual billed/metered is
negative at the book's ends (2016 gas −5.1%, 2025 electricity −3.3%), because open estimate runs straddle them.
The door carried W2_36 = 0.2735 from the 2026-11-08 run on af31e73fa7.

- **Q1, sign.** The mean signed billed-minus-used per account is **negative**: the supplier under-bills on net.
  The open estimate runs at the book's end are a lagging, pre-crisis-low estimate, set against winters
  that read high. Size: |mean| < 2% of the mean per-account use.
- **Q2, size.** The mean |billed − used| per account (the truth's MAE about zero) is between 50 and 400 kWh.
  Gas is larger than electricity.
- **Q3, gap.** The gap is in [0.15, 0.45], and gas is lower than electricity. For gas, the no-skill share
  is a poor fit to the seasonal residual, so the true-ups carry more information.
- **Q4.** Every residual sits on accounts with estimated bills. `n_accounts_with_residual` ≤
  `n_accounts_with_estimated_bills`.

The result is recorded beside these in the W2_36 commit and in the D48 finding.

## Result (appended after the run, same day)

Run: `python3 -m tools.couple_w2_36_d48 --book .../run_output_6af7fd0bfd_20261118T070221Z.json`. n = 1,306 accounts
(722 electricity, 584 gas).

- **Q1. Sign refuted, size held.** The pooled mean signed figure is **+3.8 kWh** per account (+0.017% of use). The
  fuels split. Electricity is **+30.9** (+0.25%), so it is over-billed. Gas is **−29.8** (−0.09%), so it is under-billed.
  My pooled-negative story was right for gas only.
- **Q2. Size refuted, ordering held.** The mean |billed − used| is **455 kWh**, above my 400 ceiling. Gas is 786 and
  electricity 189.
- **Q3. Held.** The gap is **0.290** [0.243, 0.342]. Gas is 0.255 [0.216, 0.296] and electricity 0.407 [0.268, 0.538].
- **Q4. Held.** 729 accounts carry a residual over 0.01 kWh, out of 1,026 with estimated bills.

Compared with the 2026-11-08 reading on af31e73fa7 (0.2735): the two figures come from different books and
different commits, so I cannot attribute the move.
