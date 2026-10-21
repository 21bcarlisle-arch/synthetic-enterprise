**Severity:** RECORDED · **Lane:** C_customer_ops · **Atom:** `C34_next_best_action_is_one_decision_across_debt_retention_upsell_and_carbon_judged_by_clv`

# Result: crediting the standing charge's opex allowance in the term contribution

Grades `SEAT_PREREG_CREDITING_THE_STANDING_CHARGE_OPEX_IN_THE_TERM_CONTRIBUTION_2026-10-20.md`
(landed `ec7fd9942`).

## How it is graded, fixed before either arm ran (21 Oct 2026, 02:45 BST)

The two arms first launched at 22:31 on 20 Oct were held behind a landing and never started. No
status, log or output existed at 02:15. They were relaunched as the long job
`scopex-opex-credit-arms` and queued behind the three read-instruction arms. This section was
written while they were still queued.

- **Arms.** Worktree `/var/tmp/se-scopex/wt` at `ec7fd9942`. Probe `/var/tmp/se-scopex/probe.py`.
  Both arms run `CURRENT_POLICY` with `next_best_action_decides_at_renewal=True` over the full
  window. `credit` is the code as landed. `nocredit` patches `standing_charge_opex_per_year` to 0,
  and that is the only change.
- **Two additions to the probe before launch**, because the probe as first written could not
  grade P1 or P4b.
  - It now records every leg the desk held (`observe_roll` / `observe_riding_leg`, kept only when
    the desk's leg count grew). That is the same population as the baseline's 487 held legs.
  - Each guard reading now carries `acq_cost_saved`. The guard reading carries no segment, but
    `replacement_cost_avoided_gbp` is above zero only for resi and returns 0.0 for SME and I&C.
    So a reading with `acq` > 0 is resi.
- **P1, P2, P3.** Read from the `credit` arm's legs and renewal log, the same way
  `/var/tmp/se-med391-out/analyse.py` read the baseline. A household decision state is keyed on
  account, start and fuels.
- **P4.** The baseline is the `nocredit` arm, not the 768f41ed1 probe. That probe counted no
  retention offers, and the `nocredit` arm differs from `credit` in one variable only. P4 holds if
  credit offers ≥ nocredit offers.
- **P4b.** Among guard readings with a sized cut (cost > 0) and `acq` > 0 (resi), it holds if the share
  where value > cost is 100% on `credit`. The `nocredit` share is reported beside it.
- **P5.** Book net, `total_net`, credit against nocredit. It holds if |Δ| < 1% and the move, if
  any, is downward.
- **P6.** Per-leg median by renewal year, on the `credit` arm. It holds if 2023 has the highest
  median, and 2020 the lowest of 2017–2021.

## Grades

Owed. Filled from the two arms when the job completes.
