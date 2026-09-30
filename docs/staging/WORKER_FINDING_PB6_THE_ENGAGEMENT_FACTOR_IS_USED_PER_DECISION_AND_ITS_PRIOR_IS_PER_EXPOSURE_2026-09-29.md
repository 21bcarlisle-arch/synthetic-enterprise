> **DISPOSITION 2026-09-30 (worker tick): held open on ONE sub-item.** Everything else here has landed
> (single roll `19a58b44d`, prior centred at 1.0 `f9b04ddc7`, null arm graded `46b78123f`). What keeps this
> in staging is the practitioner question (NTFY `EntQKsMePM5C`, no reply on record): whether some of CIM's
> channel ratio belongs per decision. A reply releases it by moving the prior's centre in
> `enriched_churn_estimate.py`. PB6 itself is parked; see its store record 11.

**Severity:** LATENT · **Lane:** W4_the_wall · **Epoch:** 3 · **Atom:** `PB6_the_engagement_observable_crosses_the_seam`

# PB6 after EH-2: the factor is used per decision, its prior is per exposure, and the world decides one renewal twice

**2026-09-29.** This is the next step `726502fa7` named: settle whether the engagement rate is per
renewal decision or per unit of exposure, before any remedy on either side of the wall.

## The definition, settled

**The factor is a per-decision quantity because that is where it is used.** It multiplies
`company_est_pre`, the probability that this account leaves AT THIS RENEWAL. That estimate decides
whether a retention offer is made (see EH-4). So the evidence for it has to be per decision, and the
ledger already counts closed fixed-renewal decisions. **The ledger's denominator is right. No
company-side remedy to the likelihood is owed.**

**The prior is the wrong quantity for that use.** CIM w6 reports households that switched in the
last six months. That is a rate per household-time, and it breaks into two factors:

    CIM channel ratio  =  (decisions reached, relative)  x  (departure per decision, relative)

Nothing published separates those two factors. So 0.585 is a prior on the product, applied as
though it were the second factor alone. **That is a named gap, not a constant to re-pick.** Per the
knowledge-first rule, the code must carry it explicitly. Today the docstring names only the
arrears-overlap gap. It does not name this one.

## Measured: in this world, the whole ratio is in the first factor

Two rolls answer "is this household active at this renewal":

- `renewals.build_renewal_schedule` (and the gas leg in `run_phase2b`) rolls
  `rolls_active_renewal(start, f"{household}_{k}", active_renewal_probability_for_customer(h))`.
  That is the archetype x the **channel multiplier**, and it decides fixed term vs SVT stint.
- The departure branch (`run_phase2b` ~2359) rolls
  `rolls_active_renewal(start, f"{billing_account}_{term_index}", active_renewal_probability(level))`.
  That is the **archetype alone**, and it decides uncapped churn vs `PASSIVE_CHURN_CAP`.

The seed string is the same. C1b's comment states `len(terms)` and `term_index` are one index, and
`billing_account` is `household_of(cid)`. **I have not re-verified that on a live schedule.** Given
that, it is one uniform read against two thresholds. Conditional on reaching a fixed term
(`U < p·m`), the departure branch is active iff `U < p`:

    20,000 synthetic households x renewals k=1..5, HEAD world
    prepayment       m=0.589  reached 0.210 of rolls  active|reached 1.000
    direct_debit     m=1.064  reached 0.370           active|reached 0.940
    standard_credit  m=1.083  reached 0.373           active|reached 0.926

For any channel with `m <= 1`, every decision reached is uncapped. For `m > 1`, the band
`[p, p·m)` reaches a fixed term and is then charged the passive cap. **So per decision, this world
makes a prepayment household slightly MORE likely to leave than a direct-debit one.** The channel
effect lives entirely in how many decisions a household reaches. That is EH-2 prediction 3 from the
other side: the decision counts ran 20 / 10 / 2, ordered exactly as the plant.

What follows for the company's reading: with enough evidence, a correct per-decision learner
converges at or above 1.0 for prepayment in this world. The 0.585 prior pulls it the other way.
EH-2's null and head arms both read about 0.53, dragged there by the prior on 10-20 decisions.

## Two defects, one on each side, and neither is the EH-1 rule

1. **WORLD (sim lane, fidelity): one event answered twice.** A household's engagement at a renewal
   has one answer, and today it has two that disagree in the `[p, p·m)` band. The single-roll
   repair (the departure branch reads `active_renewal_probability_for_customer`) makes every
   resi decision reached active. That leaves `PASSIVE_CHURN_CAP` reachable only for non-resi, and
   it exposes the larger gap under it: **an SVT stint has no departure path at all.** A real SVT
   household can switch at any time, with no exit fee. That is where most 2016-2020 switching
   happened, and it is also where CIM's per-exposure rate lives. Repairing the double roll without
   an SVT departure hazard would remove the only churn that passive households face. So the two
   are one sim-lane build, not two. It is a level change to the world's churn, and it is justified
   on fidelity, blind to company results.
2. **COMPANY (declared gap): the prior's quantity.** The CIM ratio is a per-exposure marginal
   applied per decision. Nothing publishes the split. The honest shape is a prior on the
   per-decision factor, centred where the evidence puts it (unknown, so 1.0) with CIM's spread as
   its width. It must not be a re-picked point. That also moves EH-4 (offers withheld from
   prepayment) in the mission's direction. It changes company behaviour, so it lands together with
   the world repair, not before it. Otherwise the company is tuned against a world known to be
   wrong.

## The practitioner question (sent to the director on NTFY)

"When a prepayment customer comes to the end of a fixed deal, are they less likely to switch than a
direct-debit one? Or is their lower switching all in never getting to a fixed deal, sitting on the
default tariff?" No published source separates these. If the answer is "less likely at the
decision too", then some of CIM's ratio belongs in the per-decision factor, and the prior should
keep part of it.

## Next

The world repair in (1) is the next build on this row, in the sim lane, with the practitioner answer
setting how the company prior in (2) is centred. PB6 stays at L2 in build.

## Correction and the world repair (2026-09-29, later, worker tick)

**Corrected beside the claim: an SVT stint DOES have a departure path.** Defect 1 above says "an
SVT stint has no departure path at all" and that the double-roll repair must land with a new SVT
departure hazard. That is false at HEAD. C1b's `inertia_hazard_for_term` (`run_phase2b`, the
"AN ACCOUNT ON THE STANDARD VARIABLE PRODUCT CAN NOW LEAVE" block) rolls a departure on every SVT
segment of the decision leg, and the knowledge map's route attribution has it carrying 70-87% of
the world's departures. What SVT has no path for is a *renewal decision*, which is correct. So the
world repair is the single roll alone, and it removes no churn route from any household.

**The seed alignment, verified on the live roster** (the check this finding said it had not run).
All 212 resi electricity terms that are fixed at k >= 1 had a schedule roll of active on
`{household}_{k}`, so `term_index` is the schedule index there. The departure roll then said
passive on 15 of them: 14 direct debit, 1 standard credit, 0 prepayment. That matches the
synthetic 0.94 / 0.93 / 1.00 above.

**Landed:** `household_segments.active_renewal_probability_at_a_decision(customer_id, segment)`.
It returns archetype x channel for resi, the same probability the schedule builders roll, and the
archetype alone for non-resi. The departure branch now asks it. Every resi decision reached is
active, and `PASSIVE_CHURN_CAP` stays reachable for SME renewals, which have no SVT to roll to.
Controls: `tests/simulation/test_a_renewal_is_decided_once.py`, 4 tests, 3 mutations each red.

**What this moves, downstream:** about 7% of reached resi renewal decisions lose the 0.10 passive
cap, so the renewal route's departures rise for direct debit and standard credit. The per-year
level anchor (`simulation/departure_level_anchor.py`) was fitted on captures of the old route, so
it will now read slightly high. Per the knowledge map it is a clamp owed retirement anyway. It is
not re-fitted here. The EH-2 arms were run on the pre-repair world, so they are stale. The next
step on this row is to re-run them on the repaired world. Prediction, filed now: the null arm's
prepayment factor still reads below 1.0, because the prior dominates at n~20 and nothing here
changes the prior. The planted arm still does not recover 0.307, because the plant still acts on
decisions reached and not on departure per decision. Company prior (2) still waits on the
practitioner answer.

## Re-run on the repaired world: queued (2026-09-29 21:27Z, worker tick)

The three arms are queued as ONE serial job, `longjob-pb6-eh2-rerun-repaired-world`, in a worktree
pinned at `b50a03519` (`/var/tmp/se-pb6-eh2r-b50a03519`, contains `19a58b44d`). The order is null,
then planted, then head, and the output goes to `/var/tmp/pb6_eh2r/<arm>.json`. It waits on pid
1592398, the ab5 leg `longjob-ab5-runa2c`, so it never shares the box with that leg's 10.2 GiB peak.
The declared peak is 6500 MB per arm, taken from the 6.1 GiB `run_phase2b` cycle seen at 19:07Z.
Expect the result about 1h10m after the leg finishes, plus roughly 3 x 30 min.

The predictions are the ones filed above, before this launch, and are not restated with any change:
null prepayment factor < 1.0, and planted does not recover 0.307. Grading them is the next step.

## Re-run on the repaired world: null graded, planted and head pre-registered (2026-09-30 00:40Z, seat)

The job's pinned worktree is at `b50a03519` plus one `fork_salvage` commit (`e0a72b11c`, 00:29Z)
that holds only the run's own `docs/observability/` outputs, so the code the arms run is
`b50a03519` and contains the repair `19a58b44d`.

**Null arm (finished 00:21Z): identical to its pre-repair twin in every number.** 20 prepayment
decisions, 4 lost against 6.91, factor **0.537**. Direct debit 29 of 60, standard credit 2 of 5,
book 42 of 91. That is the expected result, not a failure to run the repair: in the null world every
channel multiplier is 1.0, so the band `[p, p·m)` the repair acts on is empty and the two rolls
already agreed. The null arm is the repair's placebo, and it reads as one. **Filed prediction
(null prepayment factor < 1.0): HELD, at 0.537.**

**Pre-registered now, while planted is 20 minutes in and head has not started.** The same
reasoning, applied to the other two worlds: the repair only moves decisions for channels with
m > 1. In planted, that is direct debit (1.110) and standard credit (1.129), not prepayment (0.307).
In head, it is direct debit (1.064) and standard credit (1.083), not prepayment (0.589).

- P1. **Prepayment decisions and losses do not change in either arm**: planted 2 decisions, 0 lost;
  head 10 decisions, 1 lost.
- P2. **Direct-debit losses rise, or hold, in both arms** (pre-repair: planted 32 of 72, head 30 of
  67). A decision in the band loses the 0.10 cap. About 6-10% of reached decisions sit in the band,
  so I expect +1 to +4 losses, and the direct-debit decision count may fall by the same amount
  because a leaver reaches no later renewal.
- P3. **The prepayment factor moves only through the book's ratio**, and moves DOWN, because book
  losses rise while prepayment's do not. Planted reads in [0.55, 0.584]; head in [0.49, 0.530].
  **Filed prediction (planted does not recover 0.307): expected to HOLD.**
- P4. If P1 fails, meaning prepayment counts move, then either the repair reaches prepayment by a
  route I have not traced, or the world diverges downstream of changed departures. That would be
  the more important result.

## Re-run on the repaired world: all three arms graded (2026-09-30 01:25Z, seat)

Same columns as the first EH-2 table. Each row is one full-window `run_phase2b.main()` at
`b50a03519` (repair `19a58b44d` in), graded at 2026. The pre-repair twin from `/var/tmp/pb6_eh2/`
is on the line below each row.

| arm | world PPM multiplier | PPM decisions | PPM lost / predicted pre-factor | ratio | w | **factor** | pre-EH-1 raw rule, same counts |
|---|---:|---:|---:|---:|---:|---:|---:|
| null, repaired | 1.000 | 20 | 4 / 6.91 | 0.474 | 0.411 | **0.537** | 0.427 |
| null, pre-repair | 1.000 | 20 | 4 / 6.91 | 0.474 | 0.411 | 0.537 | 0.427 |
| planted, repaired | 0.307 | 2 | 0 / 0.38 | 0.596 | 0.036 | **0.585** | 0.562 |
| planted, pre-repair | 0.307 | 2 | 0 / 0.38 | 0.549 | 0.036 | 0.584 | 0.562 |
| head, repaired | 0.589 | 10 | 1 / 2.51 | 0.387 | 0.200 | **0.539** | 0.459 |
| head, pre-repair | 0.589 | 10 | 1 / 2.56 | 0.358 | 0.202 | 0.530 | 0.457 |

Book (repaired): null 42 lost of 91 against 32.13 predicted; planted 42 of 84 against **28.50**
(was 26.23); head 40 of 87 against **28.54** (was 26.96). Direct debit: planted 32 of 72 against
25.95 (was 23.69), factor 0.914 (was 0.925); head 30 of 67 against 23.85 (was 22.25), factor 0.957
(was 0.967).

**Not one world outcome changed, in any arm.** In all three, `decisions_by_method` and
`losses_by_method` are identical to the pre-repair twin, year by year, and so are the churn lines in
the run logs once the probabilities are stripped. The repair did move probabilities: in the
retention log, 10 of 101 lines in planted and 7 of 104 in head have a different `p_retain`.
SYN-2016-030 in 2019 fell from 0.41 to 0.14. But every roll landed on the same side as before. On a
deterministic book of this size, the ~7% band is about four decisions, and all of them fell the
same way.

**What moved is the company's expectation, and it moved through `active_renewal`.** In the band,
`RenewalObservation.active_renewal` used to read passive and now reads active. `churn_desk` sends a
passive roller to the SVT-inertia formula and an active one to the full enriched model. So the
company's pre-factor belief on those decisions rose, and the book's predicted losses rose by about
2.3 in planted and 1.6 in head, with no loss added. Book O/E fell, and each channel's ratio is taken
against book O/E. That is why prepayment's ratio ROSE: in planted from 0.549 to 0.596, and in head
from 0.358 to 0.387. Head's prepayment prediction also fell a little (2.56 to 2.51) with its band
empty. The likely route is the company's year-level pressure multiplier, which learns from the same
book O/E. **I have not traced that.**

### Graded

- **Filed, null prepayment factor < 1.0: HELD** (0.537, byte-identical to pre-repair; the band is
  empty when every multiplier is 1.0, so the null arm is the repair's placebo).
- **Filed, planted does not recover 0.307: HELD** (0.585, which is the prior of 0.585; w = 0.036 on
  2 decisions). **EH-2 still answers FAIL on the repaired world.**
- P1, prepayment counts unchanged in both arms: **HELD** (2/0 and 10/1).
- P2, direct-debit losses rise by +1 to +4: **REFUTED, kept beside the claim.** They rose by 0. I
  priced the band's decisions as losses in expectation and forgot that, on one deterministic book,
  four decisions can all land on the retain side of the roll. That is what happened.
- P3, prepayment factor moves only through the book, and moves DOWN: **REFUTED on direction.** I
  assumed the book would move through its losses. It moved through its EXPECTATION, via the
  company reading the flipped `active_renewal`, so the factor went UP: planted +0.001, head +0.009.
  "Only through the book" held.
- P4 did not fire.

### What this means for PB6

The repair was a fidelity fix and it was right to make. But on this book it moves the engagement
reading by less than 0.01. It does not touch the structural reason EH-2 fails: the channel effect
lands on how many decisions a household reaches (20 / 10 / 2 again), and the ledger learns per
decision. Nothing inside the simulation can now move PB6 toward L3 on this book size. The recovery
needs PB1-scale decision counts (reason (b) of the first EH-2 finding). The prior's centring (per
decision, 1.0 with CIM's spread, or keeping part of 0.585) waits on the practitioner answer to NTFY
`EntQKsMePM5C`, which has not arrived. **PB6 stays at L2.** The next build on this row is the
company-side declared gap in defect (2): the engagement prior's docstring and reading name the
per-exposure vs per-decision gap. `decabc703` has already named it in code. So what is owed is the
centring, and it waits on the answer. This row has no drawable build until then.

Raw artefacts: `/var/tmp/pb6_eh2r/<arm>.json` and `.log`, not committed. Re-running
`tools/_pb6_engagement_recovery_arm.py` at `b50a03519` reproduces them.
## Grading the re-run: null read, and a prediction filed before planted and head (2026-09-30 00:40Z, worker tick)

**Null arm (`/var/tmp/pb6_eh2r/null.json`, pinned at `b50a03519`): identical to its pre-repair twin,
every figure.** PPM 20 decisions, 4 lost / 6.91, factor 0.537; DD 29/60, 1.005; SC 2/5, 1.097. The
two 95k-line run logs differ only in a cache line and a dict print order. **This is an equivalence,
not a repair that failed to reach.** The null arm sets every channel multiplier to 1.0, so
`archetype x channel == archetype` and the band `[p, p·m)` the repair closes is empty. On the null
world the two rolls already agreed. The filed prediction (null prepayment factor < 1.0) **HELD, but
vacuously**: this arm is the same run as before and adds no evidence. Why prepayment still reads 4
lost / 6.91 predicted when the world's truth is 1.0 is the open question from the first EH-2 table,
unchanged.

**Filed now, before planted and head finish.** For prepayment, `m < 1` in both arms, so every
decision reached was already active (1.000 above), and none sits in the band. The repair can move
only direct debit and standard credit.

3. Prepayment decisions and losses are unchanged: planted 2 / 0, head 10 / 1. The exception is a
   cascade, where a DD departure changes the later book, and that would show as other counts moving too.
4. Direct debit losses in head are at least 30 of 67, and the DD factor is at least 0.967, because
   the band's decisions lose the 0.10 cap.
5. So the head prepayment factor reads AT OR BELOW 0.530. Its likelihood is channel O/E over BOOK
   O/E, and the book's O/E rises with DD's. The repair therefore moves the company's prepayment
   reading further from 1.0, not closer.

## Graded: all three arms on the repaired world (2026-09-30 01:25Z, worker tick)

*(The heading above says 00:40Z. The clock read 00:35Z. The predictions landed in `7f3022e66` at
00:35:12Z, before planted finished at 00:50Z and head at 01:19Z.)*

Same columns as the first EH-2 table, each arm beside its pre-repair twin in `/var/tmp/pb6_eh2/`:

| arm | world | world PPM multiplier | PPM decisions | PPM lost / predicted pre-factor | ratio | w | **factor** | pre-EH-1 raw rule | DD lost / decisions | DD factor |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| null | pre-repair `ad3e03018` | 1.000 | 20 | 4 / 6.91 | 0.474 | 0.411 | **0.537** | 0.427 | 29 / 60 | 1.005 |
| null | repaired `b50a03519` | 1.000 | 20 | 4 / 6.91 | 0.474 | 0.411 | **0.537** | 0.427 | 29 / 60 | 1.005 |
| planted | pre-repair | 0.307 | 2 | 0 / 0.38 | 0.549 | 0.036 | **0.584** | 0.562 | 32 / 72 | 0.925 |
| planted | repaired | 0.307 | 2 | 0 / 0.38 | 0.596 | 0.036 | **0.585** | 0.562 | 32 / 72 | 0.914 |
| head | pre-repair | 0.589 | 10 | 1 / 2.56 | 0.358 | 0.202 | **0.530** | 0.457 | 30 / 67 | 0.967 |
| head | repaired | 0.589 | 10 | 1 / 2.51 | 0.387 | 0.200 | **0.539** | 0.459 | 30 / 67 | 0.957 |

**No realised count moved in any arm.** Decisions and losses by method and year are identical to the
pre-repair twins in all three. The repair changed no departure in books of 84 to 91 decisions: the
band decisions it uncapped did not roll between the 0.10 cap and their uncapped probability. The
"departures rise for DD and SC" expected in the correction above was not seen at this book size.

**What moved is the company's expectation, and why.** `run_phase2b` hands the departure branch's
`active_renewal` into `RenewalObservation`. `churn_desk` sends a resi account with
`active_renewal=False` to the passive (SVT-roller) estimator. Before the repair, a band decision was
a household on a fixed renewal, which the supplier can see, and it was estimated as a passive roller
off a coin the supplier cannot see. After the repair, a resi decision's `active_renewal` is exactly
"reached a fixed term", which is observable. So the repair also closes a small leak across the
wall. That is where the rise in DD predicted-pre-factor losses comes from (planted 23.69 -> 25.95,
head 22.25 -> 23.85) with the same losses: DD's O/E falls, the book's O/E falls with it, and
prepayment's channel-over-book ratio rises.

Graded against what was filed:

1. **Null prepayment factor < 1.0: HELD, vacuously.** It is the same run (m = 1 empties the band).
2. **Planted does not recover 0.307: HELD.** It reads 0.585, the prior. EH-2 still answers FAIL on
   the repaired world, for the reason in the first table: the plant acts on decisions reached (20 / 10 / 2),
   not on departure per decision.
3. **Prepayment counts unchanged: HELD** (2 / 0 and 10 / 1).
4. **DD losses at least 30 and DD factor at least 0.967: losses HELD at exactly 30, factor
   REFUTED** (0.957). The mechanism I named, more losses, did not happen. The factor fell because
   expected losses rose.
5. **Head prepayment factor at or below 0.530: REFUTED** (0.539). This is the same wrong mechanism as
   in 4, and it moved the other way: book O/E fell, not rose.

**I cannot yet say** why head's prepayment predicted-pre-factor moved (2.56 -> 2.51) when no
prepayment decision sits in the band. Planted's did not (0.3794 both). The candidate is company
state carried from the DD band decisions, which now take the active estimator and its retention
offer. That is a cascade through the company's own book, not a world outcome. The effect is
0.05 of a loss.

**What this settles for PB6.** The repaired world does not change EH-2's answer. It moves prepayment
by at most 0.009 in any arm. The company prior's centring (defect 2 above) is still the open step,
and it still waits on the practitioner answer (NTFY `EntQKsMePM5C`, no reply on record at this
time). PB6 stays L2. The artefacts are in `/var/tmp/pb6_eh2r/` and are not committed, so re-running
`tools/_pb6_engagement_recovery_arm.py` at `b50a03519` is the reproduction.

## Defect (2) enacted: the prior re-centred at 1.0 as a declared gap (2026-09-30 04:05Z, worker tick)

DIRECTION `PB6_the_engagement_observable_crosses_the_seam` said not to wait for NTFY `EntQKsMePM5C`
any longer. No reply is on record.

**What changed.** In `company/crm/enriched_churn_estimate.payment_method_engagement_reading`, the
prior is now **1.0 for every channel**. Its docstring names the gap and the practitioner question
that would move the centre. The **width is unchanged**: `_CIM_ENGAGEMENT_PRIOR_LOG_VARIANCE` is
still CIM's spread across channels (0.080 in log space), and it is now derived through
`payment_method_engagement_factor`, so the published table and the width cannot drift apart.
`payment_method_engagement_factor` is still Ofgem's per-exposure reading, but it is no longer the
centre. The ledger's blend takes the prior as a parameter and is correct for any centre. It was not
touched.

**Before and after, printed at real inputs.** These are the three repaired-world arms' own
counts, from `/var/tmp/pb6_eh2r/<arm>.json`. The ratio and the weight are unchanged, and only the
centre differs. This is a counterfactual on the same counts, not a re-run: the re-centred prior
also changes which retention offers are made, so a re-run's counts can differ.

| arm | channel | n | lost / pre-expected | ratio | w | before (prior = CIM point) | after (prior 1.0) |
|---|---|---:|---:|---:|---:|---:|---:|
| null | prepayment | 20 | 4 / 6.91 | 0.474 | 0.411 | 0.537 | **0.736** |
| null | direct debit | 60 | 29 / 22.75 | 0.975 | 0.628 | 1.005 | **0.984** |
| planted | prepayment | 2 | 0 / 0.38 | 0.596 | 0.036 | 0.585 | **0.982** |
| planted | direct debit | 72 | 32 / 25.95 | 0.838 | 0.626 | 0.914 | **0.895** |
| head | prepayment | 10 | 1 / 2.51 | 0.387 | 0.200 | 0.539 | **0.827** |
| head | direct debit | 67 | 30 / 23.85 | 0.898 | 0.613 | 0.957 | **0.936** |

Direct debit moves by about 0.02. Prepayment moves most where the book is thinnest, which is what a
prior carrying no information should do. EH-2's planted arm now reads 0.982 instead of 0.585. It is
still not 0.307, because two decisions cannot recover anything, but it no longer reads as though
it had recovered the published point.

**Controls.** `test_the_prior_is_centred_on_no_effect_and_only_the_book_moves_it_off` is new, and
it reds when the old centre is restored (mutation run). At a centre of 1.0 the double-count blend
`prior x ratio**w` and the correct `prior x (ratio/prior)**w` are **the same function**, so that
defect is an equivalence through the public reading. Its control now asks the ledger directly at
CIM's point, where it can still fail. `test_the_desk_books_the_channel_it_priced_with` had needed the
prior alone to put prepayment below one. It now gets a closed 2018 book first, and it still reds
when the desk books the priced belief as the pre-factor belief (mutation run). The seam test
`test_the_companys_churn_belief_actually_moves_with_the_observable` asked the prior, outside a
scope, for 0.75x. It was re-keyed to a book in which prepayment leaves at a third of the rate.

**Prediction for the null arm, filed before it runs.** The world's truth in this arm is 1.0.
(a) The prepayment factor reads above 0.537, the pre-re-centring value, and within 0.70-0.95. The
prior no longer drags it down, but 4 lost against 6.91 predicted is still evidence below 1. (b) The
direct-debit factor reads within 0.03 of 0.984. (c) Prepayment decision count stays within ±3 of 20.
The re-centring can move retention offers, but it cannot move which renewals a household reaches.

**Queued.** Unit `longjob-pb6-null-arm-recentred-prior` waits on the whole ab5 lineage script (pid
2141363, both legs), then calls `launch_long_job --peak-mb 6500`. That launch does its own
co-residency check and refuses by name if ab6 is resident. The worktree is
`/var/tmp/se-pb6-recentre-a5ed0d0e2`, at HEAD `a5ed0d0e2` plus this commit's diff (patch sha256
`bb7984cc…`). Output goes to `/var/tmp/pb6_recentre/null.json`, and the waiter's log is
`/var/tmp/pb6_recentre/wait.log`. Grading it against (a)-(c) is the next step on this row. After
that, the row returns to its Expert Hour.

## Graded: the null arm under the re-centred prior (2026-09-30 06:20Z, worker tick)

`/var/tmp/pb6_recentre/null.json`. The run tree's `company/` diff against `a5ed0d0e2` is
byte-identical to `f9b04ddc7`'s (sha256 `d26737b2…` both). The later auto-salvage commit in that
worktree holds only run outputs.

| channel | n | lost / pre-expected | ratio | w | **factor** | counterfactual above |
|---|---:|---:|---:|---:|---:|---:|
| prepayment | 20 | 4 / 6.83 | 0.475 | 0.407 | **0.739** | 0.736 |
| direct debit | 60 | 29 / 22.52 | 0.975 | 0.624 | **0.984** | 0.984 |
| standard credit | 5 | 2 / 1.23 | 1.278 | 0.113 | **1.028** | — |

(a) Prepayment above 0.537 and within 0.70-0.95: **HELD** (0.739). (b) Direct debit within 0.03
of 0.984: **HELD** (0.984). (c) Prepayment decisions within ±3 of 20: **HELD** (20). The realised
losses are the same as in the pre-re-centring run, 4 of 20 and 29 of 60. What moved is pre-expected
prepayment losses, 6.91 to 6.83. That is the re-centred prior changing retention offers, the effect
(c)'s reasoning allowed for. The counterfactual printed before the run was within 0.003.

What this leaves: the world's truth in this arm is 1.0 and the company reads 0.739. That is the
prior's pull, gone, and 4 losses against 6.83 expected on 20 decisions, still there. Sampling at
this book size (w 0.41) is the whole of the remaining gap. The rule cannot be graded any finer
than this until the book is at PB1's population scale.

## Two more, found while grading (2026-09-30, same tick)

**A HEAD red `f9b04ddc7` left in a sibling file.** `tests/tools/test_the_payment_observable_reaches_a_live_decision.py`
asserted that the live decision reads prepayment below 0.75 x direct debit. That held only because
of CIM's point prior. `tools/run_live_decisions._retention_ev` runs with no scope and no renewal
year, so at a centre of 1.0 both channels read 0.1326, even inside a book. The gate's stem
selection never ran it. It is now re-keyed to the property it was written for: the method reaches
the belief call (a pass-through spy, which reds when the call drops the method). **Declared gap:**
the live path reads no book, so after the re-centring the payment method moves no live decision.
That is correct with no evidence behind it. It stops being correct once the live path can read the
run's end-of-run ledger, and nothing does that yet.

**EH-5 remedied.** `LiveSimInterface.get_payment_method` fell to direct debit on any exception.
This world models no CRM miss, so the fallback could catch only a caller passing no id. It booked
that as a direct-debit renewal. Its control never reached it: `None` on the electricity leg draws as
direct debit by chance. Only the gas leg reached the except arm. The seam now refuses a non-string
or empty id by name, and lets any world failure surface. Controls: both fuels are refused, and every
id shape the book carries still resolves. Restoring the silent fallback reds two tests (mutation run).
