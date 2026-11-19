**Severity:** LATENT · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality` · **Twin:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# Pre-registration: where the fuel-split signed residual sits, on run_output_6af7fd0bfd (2026-11-19)

Written before splitting. Reads only `docs/reports/run_output_6af7fd0bfd_20261118T070221Z.json` through
`tools.couple_w2_36_d48.account_errors`. What I already know: the per-account truth t_a (billed − used over the
whole book) nets to +30.9 kWh electricity and −29.8 kWh gas (SEAT_PREREG_W2_36_D48_BILLED_MINUS_USED_ON_6AF7FD0BFD
Q1). Closed runs true up exactly (2026-11-08 reading), so the residual lives on an account's LAST estimate run:
either OPEN at the book's end, or CLOSED ON AN ESTIMATED FINAL bill. Each account has at most one such run.

**What the split is.** Each account is put in exactly one kind: `open` (open_estimated_kwh > 0), `closed_final`
(closed_on_estimated_final_kwh > 0) or `none`. The month is the calendar month of the account's last bill's
`period_end`, which is where that run ends. The signed sum of t_a is reported per fuel × kind, and per fuel ×
end-month for the two run kinds.

- **P1.** `none` accounts carry |Σt| < 1 kWh per fuel (a check of the known mechanism, not a finding).
- **P2.** The fuel signs survive inside the `open` kind: electricity open runs net positive, gas open runs net
  negative. (If they do not, the sign split is a mix of kinds, not a fuel effect.)
- **P3, the discriminating one.** If the gas profile is over-seasonal (the D48 candidate), a gas run ending in
  Dec–Feb is over-billed (Σt > 0) and one ending in Jun–Aug is under-billed (Σt < 0). The opposite pattern says
  under-seasonal. I predict over-seasonal.
- **P4.** `closed_final` runs end across many months and net closer to zero per estimated kWh than `open` runs,
  whose end months are bunched at the book's end.

The result is appended below, same day.

## Result (appended after the run, same day)

n = 1,306 accounts (722 electricity, 584 gas). Sign convention: t > 0 means over-billed. I decomposed each account's
t into what the company KNOWS, b = −true_up from its reads, and the UNKNOWN last run, t − b. 95% intervals are an
account bootstrap (4,000 resamples).

- **P1. Refuted as written, and my premise was wrong.** `none` accounts carry Σt = +13,193 kWh for electricity and
  −28,158 kWh for gas. But on every one of them t equals b exactly. That energy is closed-run true-ups the company
  holds. `total_consumption_kwh` does not include a catch-up's kWh, so the runner's "billed" leaves it out.
  "Closed runs true up exactly" means belief equals truth there, not that t = 0.
- **The headline fuel split is not distinguishable from zero.** The mean unknown per account is **+22.9 kWh
  [−13.6, +75.7]** for electricity and **−30.0 [−64.8, +5.3]** for gas. The mean known per account is +8.1 and
  +0.2. The +30.9 / −29.8 sign split in the prior record is mostly unknown last-run energy, and at this n neither
  sign is established. This is a correction beside that record's Q1: the split it reported is a point estimate,
  not a fuel effect.
- **P2. Refuted.** Inside `open` (every open run ends 2025-06), the unknown part is −0.9% of run kWh for
  electricity [−5.0%, +3.1%] and **−4.0% for gas [−6.5%, −1.7%]**. Both are negative, so the open runs do not carry
  the fuel split.
- **P3. Held, for gas.** Gas runs closed on an estimated final bill ending Dec–May are over-billed by **+3.6%
  [+0.8%, +6.3%]**. Those ending Jun–Nov are under-billed by **−6.3% [−10.3%, −2.6%]**. Over-billing into winter
  and under-billing into summer and autumn is the over-seasonal profile signature. The gas open runs end in June
  and are under-billed by −4.0%, which fits the same pattern. Electricity shows no seasonal sign: +6.1%
  [−5.1%, +17.8%] against +2.4% [−0.4%, +6.3%].
- **P4. Held for gas** (closed_final −0.5% against open −4.0%). **Not established for electricity**: the
  intervals overlap.

**What this does and does not say.** The one effect that clears its bound is seasonal and gas-only. Its sign
matches an estimate profile with too much winter weight. The same sign would also come from a book whose winters
ran milder than the profile's normal year. That is a weather explanation, and this split cannot tell the two
apart. The next one-variable test is to compare the estimator's gas monthly shape with the published Xoserve
ALP/DAF shape for the same LDZ and year, apart from weather. Electricity's positive tilt is not established, so
no mechanism is claimed for it.

The script was a read-only split over `account_errors` and is not kept: no consumer needs it yet.

Separately: the shared tree still holds an untracked older draft of `tools/couple_w2_36_d48.py`, which differs
from origin. This turn runs in an isolated worktree and does not touch the shared tree. Whoever holds that tree
should remove the draft so its checkout can advance.
