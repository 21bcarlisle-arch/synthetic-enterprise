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

## The second launch died queued too; relaunched 21 Oct 05:36Z

At 05:35Z `scopex-opex-credit-arms` did not exist either: there was no process, no `longjob-*`
unit, no `.launch_records.json` row and no `credit`/`nocredit` output. It went the same way as the
first launch. The launcher was still queued for memory, so it had no unit of its own, and it died
with the tick's cgroup. The relaunch went in at **05:36Z**. It runs as a driver unit in its own
cgroup, `relaunch-driver-scopex-1021.service` (`/var/tmp/se-relaunch-1021/driver2.sh scopex`), and
writes a QUEUED line to `/var/tmp/se-relaunch-1021/scopex.log` every 5 min while
`longjob-per-customer-switch-arms-8fbb641d8` is active. After that it launches
`scopex-opex-credit-arms-ec7fd9942`: `run_both.sh` in the same locked worktree, at a 7,000 MB
peak, with the artefact `/var/tmp/se-scopex/nocredit.json`, which is written last. When the follow ends,
the driver hands off the grade as the continuation `grade-the-opex-credit-arms-ec7fd9942`, at that
point because a continuation lives only 6h. The arms, the probe and the grading above are unchanged.

## The third launch ran, and both arms died on import in 15 s; relaunched 21 Oct 15:18Z

The job ran this time (14:52Z, `Result=success`, 15 s) but wrote no artefact. Both `credit.log` and
`nocredit.log` say `ModuleNotFoundError: No module named 'company'`. The cause is the probe, not
the code under test. A script's `sys.path[0]` is its own directory (`/var/tmp/se-scopex`), not the
cwd that `run_both.sh` changes into, and the launch sets no `PYTHONPATH`. The retnet probe already
carries the same fix. The probe now puts the cwd (the locked worktree at `ec7fd9942`) at the front
of `sys.path`, and nothing else changes. The arms, the patch and the grading above are unchanged.
The failed logs and status are kept beside it as `*.failed-1021*`. The import path was checked in
the worktree before the relaunch.

The relaunch is `relaunch-driver-scopex-1021.service` again, now running `driver3.sh`. That is
`driver2.sh` with the continuation id changed to `grade-the-opex-credit-arms-ec7fd9942-r2`, because
releasing this draw retires a continuation filed under its own id. At 15:18Z it is queued in
`longjob-scopex-opex-credit-arms-ec7fd9942-queued` behind a landing. Its log is
`/var/tmp/longjob-scopex-opex-credit-arms-ec7fd9942-queued.log`. The retnet driver still waits on
this unit, so it stays behind it.

## Grades

Graded 21 Oct 2026 from `/var/tmp/se-scopex/{credit,nocredit}.json`. Both arms are stamped
`ec7fd9942b68`, the job's `status` reads `done`, and nocredit finished at 19:23 local.
`python3 /var/tmp/se-scopex/grade.py` printed the figures below.

**The control is clean.** The `nocredit` arm reproduces the 768f41ed1 baseline exactly: 487 held
legs, a median of −£2.89 a month, 85.0% negative, and 4 rows advised. So the patch is the only
variable between the arms.

| | credit | nocredit | Predicted | Grade |
|---|---|---|---|---|
| P1 median leg £/mo | **+1.54** (493 legs) | −2.89 (487) | +0.50 to +2.50 | **holds** |
| P1 share negative | **26.4%** | 85.0% | 15–40% | **holds** |
| P2 median household £/mo | **+2.29** (325 states, 16.6% negative) | −3.66 (321, 85.0%) | +1.00 to +3.50 | **holds** |
| P3 advised | **4 / 975 = 0.41%** | 4 / 963 = 0.42% | ≤ 2% | **holds** |
| P4 retention offers | **95** (£2,642.77) | 7 (£781.50) | credit ≥ nocredit | **holds** |
| P4b resi sized cuts offered | **233 / 233 = 100%** (value − cost min +£11.70, median +£25.03) | 47 / 243 = 19.3% | 100% on credit | **holds** |
| P5 book net | **£444,034.64** | £442,032.15 | \|Δ\| < 1%, falling | **magnitude holds, direction REFUTED**: +£2,002.49 = **+0.453%** |
| P6 by renewal year | 2023 **+9.30** highest; 2020 **−0.02**, lowest of 2017–21 (17: +1.25, 18: +1.23, 19: +1.61, 21: +2.09) | 2023 +4.27; 2020 −3.66 | 2023 top, 2020 bottom | **holds** |

Every guard reading with a sized cut carried `acq` > 0 in both arms. No SME or I&C cut was sized,
so P4b's resi filter excluded nothing.

### What it settles

- **The median renewal's −£3.91 was an artefact of how it was built, not a property of the book.**
  With the standing charge's nil-consumption opex credited, the median household decision state
  is **+£2.29 a month** and 16.6% are negative, against −£3.66 and 85.0% on the same code without
  the credit. The C34 concern's sentence "our side of almost every renewal is below zero before
  any advice is costed" rested on that figure. It is corrected beside the claim in
  `docs/direction/DIRECTION.yaml`.
- **C34 still advises almost nobody (0.41%), and the credit is not why.** P3 reasoned this before
  either arm ran: every stated effect gives up at least £2 a month, which is at or above the
  median contribution even after the credit. A positive contribution removes one reason to
  advise nobody and supplies none to advise.
- **As P4b predicted, the retention guard no longer refuses anything for resi on the default
  policy.** It sized 233 resi cuts and offered all 233. The closest case still cleared by £11.70.
  Offers rose from 7 to 95 and their cost from £782 to £2,643, while departures moved from 236 to
  235. So about 88 more offers bought, at most, one more stay. This is the measured form of
  `SEAT_FINDING_THE_RETENTION_GUARD_WEIGHS_THE_SPREAD_OVER_WHOLESALE_AS_THE_VALUE_IT_PROTECTS_2026-10-20.md`:
  the guard has no weight for the chance that the offer changes the outcome. That finding's note
  is updated with this count.

### P5, refuted: what the prediction said and what happened

The prediction said book net would fall, if it moved at all, because more discounts are given.
Discounts did rise by £1,861. But gross rose by £6,004.83 (£1,334,743.75 → £1,340,748.58), so net
rose by £2,002.49. One departure fewer and six more held legs both point the same way: some
discounts kept or extended a supply that otherwise ended. **I cannot yet say** how the £6.0k
splits between the one account that stayed and longer terms on accounts that left later. The probe
saved churn counts, not the roster. One seed, one book; a 0.45% move sits inside what a single
departure can carry. The written prediction stays as it was, refuted on direction and right on
magnitude.

### What would change this

Nothing here touches the C34 switch's grade, which is still off by default. The next lever is the
missing outcome weight in the retention guard (C29's `retention_weighs_engagement`, or B8's
measured uplift). Turning it on is a policy change and needs its own pre-registered run.
