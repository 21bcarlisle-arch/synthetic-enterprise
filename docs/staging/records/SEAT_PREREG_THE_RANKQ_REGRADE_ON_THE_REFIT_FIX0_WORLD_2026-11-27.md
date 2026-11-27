**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: the rankq re-grade on the refit fix-0 world (27 Nov 2026)

**Filed before the run exists.** At filing time, `/var/tmp/se-fix0-anchor-refit-landed.sha` did not exist (a bare
`ls`), so the held continuation `the-rankq-regrade-launches-on-the-refit-fix-0-world` cannot have launched. No refit-world
output was opened. The priors below come from the **void** s.12g files in `/var/tmp/vtn-out/{twin,A,cut,rankq}/`, read
as evidence only, never graded. Readers: `/var/tmp/vtn-driver/s12g-refit-prereg/{auc,offered,cutdefect}.py`, run with `-I` from `/tmp`.
The prior is the decomposition in
`docs/staging/SEAT_FINDING_AN_OFFERED_LEAVER_IS_ANSWERED_ON_A_DIE_THE_FLOOR_DID_NOT_REDRAW_2026-11-25.md` §1. On the
world's stated probabilities, a retention offer loses money here: about 97% of the discount goes to households that
would have stayed anyway.

**What stands unrevised.** That finding's R1 to R3 (§4), and R1a to R1c of the K8 end-of-fix page §7 (`3e032230b`). This
record adds the three things neither of them holds: the belief's AUC, the cut's net, and the list of what this run
re-reads. It changes none of them.

## For the director, in plain English

The re-run tests whether a supplier that chooses its retention offers household by household beats one that follows a
flat rule, now that offers are answered on the right dice. My prediction is that it **neither wins nor loses by a
margin the run can see**. The flat rule's apparent win came from the wiring fault. Once the fault is gone, an offer
mostly gives money to people who were staying anyway, and both suppliers do that. I also predict that the belief
about who will leave looks *better* on the fixed run. The fault had been keeping some of the leavers the belief had
flagged on the books, so they never counted as leavers.

## 1. The belief's AUC (desk renewal-churn belief against who actually left)

**The quantity.** `desk_belief_by_arm.value_arm` in the run's control file, restricted to rows with `desk_asked`. AUC is
P(a leaver's `desk_churn_belief` > a stayer's), with ties counted as 0.5. It is reported per seed and as the mean of
the two seeds. "Left" is the run's kept outcome (`left`).

**Prior, on the void harness (both seeds):**

| Config | Value-arm asked AUC | Leavers / stayers | Offered renewals kept on a roll above the offered P(stay) |
|---|---|---|---|
| twin | 0.190 / 0.243 | 36/352, 41/348 | 52 of 211 |
| rankq | 0.653 / 0.681 | 49/326, 52/327 | 23 of 77 |

**Why the fix should move it.** Those off-roll keeps were leavers that the fault turned into stayers. Each one is
an offered household. On rankq, offered households sit at the **0.77** mean percentile of the stayers' beliefs
(`offered.py`). Each leaver restored there raises the AUC. On the twin, offered households sit at the **0.37** percentile,
so restoring them lifts its AUC a little, from a low base. Arithmetic on the prior: rankq goes to ≈ (50 × 0.667 + 11 × 0.77) / 61 ≈ 0.69.
The twin goes to ≈ (38 × 0.217 + 26 × 0.37) / 64 ≈ 0.28. The refit (fewer leavers after 2024, and 2021 Q4 moved onto the
default route) changes who leaves in about 15% of the decisions. That widens the range. It does not set a direction.

| | Measure | Predicted | Wrong if |
|---|---|---|---|
| **Q1** | rankq value-arm asked desk-belief AUC, mean of seeds | **0.69 (0.60 to 0.77)** | Below 0.60: the corrected belief's ranking on 61118 was partly the fault's, and the belief is re-read before any lever |
| Q2 | twin value-arm asked desk-belief AUC, mean of seeds | **0.28 (0.18 to 0.40)** | Above 0.45: the "live belief ranks leavers backwards" reading (0.333, the triage row) was mostly the fault, and that row is re-opened against this run |
| Q3 | rankq value-arm leavers among asked rows, per seed | **55 to 75** (void: 49, 52) | Under 50: the fault did not hold back the leavers this record says it did |

## 2. The per-customer arm at the 0.12 cut, minus the flat twin

**Correction beside the item's wording.** The held launch runs **rankq against the twin**. Rankq has the 0.12 cut
**off** (`retention_rank_at_share = 215/777`). So the 0.12 cut figure the item asks for (s.12g's P1, cut − twin) is
**not produced** by this run unless the launcher adds a `cut` configuration on the same base. It is predicted here
anyway, so that if it is added, its number already exists before the launch. If it is not added, P1 stays void and
unread.

**The quantity.** P1's own measure: on book 61118, churn pair 13131/14141, per household: (cut run, value arm minus flat
book) minus (twin run, value arm minus flat book). It is in £ per household-year over the twin's control-arm
household-years, averaged over the two seeds, with a 95% interval from 2,000 household resamples (seed 20261117), by
`grade_new_book.py`'s method.

**Why this number.** On the void harness, P1 read −£0.140 (−£1.389 to +£1.025). The fault lifted both arms by
nearly the same amount: cut had **57** of 215 offered renewals kept off-roll, and the twin **52** of 211 (`cutdefect.py`).
At equal volume, removing the fault takes away cut's 5 extra keeps. The finding's −£3.33 over 34 household-runs puts
each keep at about £0.1/hh-yr, so P1 moves by about −£0.5. Against that, cut offers to higher-belief households (A's
ranking, AUC ≈ 0.63 asked). Fewer of its discounts go to stayers, but at an uplift near 0.02 that is worth about
£0.02/hh-yr. The refit's lower after-2024 leave rate makes every offer worth less, for both arms alike.

| | Measure | Predicted | Sign | Rule (P1's own, unchanged) |
|---|---|---|---|---|
| **N1** | cut − twin, advantage over the flat book, on the refit fix-0 world | **−£0.50 (−£1.90 to +£0.90)** | **negative point, interval straddles zero** | Held only ABOVE (lower bound > 0). Refuted when the point is below zero. Otherwise "cannot tell" |

N1 is predicted to be **refuted by P1's own rule** (point below zero) and to **STRADDLE** by its interval. Both labels
are published side by side, as s.12g's reader did.

**The run's own headline (rankq − twin)** stays the finding's R1, as filed: +£0.13 (−£1.0 to +£1.5), with R1a to R1c by
regime. This record does not file a second number for it.

## 3. Which voided comparisons this one run re-reads

The void set is s.12g's family on the old harness: twin, cut, A, rankq, plus EP1 A4 at `20b14f3ed`. The refit world has a
different departure level, so its `world_identity.digest` will differ from the void files' `cdba75ebb9197b33`. **No void
file can serve as a comparator** for a refit-world file ("two that do not are different worlds"). A comparison is
re-read only if both of its sides are re-run on the refit base.

| Void comparison | Re-read by this run? |
|---|---|
| rankq − twin (rankq R1, finding R1 to R3, K8 R1a to R1c) | **Yes**, provided the launch runs **both** `twin` and `rankq` on the refit base. A rankq-only launch graded against the void twin file is refused by this record |
| cut − twin (s.12g P1), cut − A (P3, P3b) | **No**, unless a `cut` configuration (and `A`, for P3) is added on the same base. N1 above is filed for that case |
| A − twin (s.12g P2), rankq − A (rankq R3), rankq − cut (rankq R4) | **No**. They need A and cut on the refit base |
| EP1 A4 (`20b14f3ed`, ep1 − A on the dated rate) | **No**. It is held on this run's output as `ep1-a4-regrade-on-the-fixed-dice-is-queued`, and its own pre-registration is a separate record |
| Twin's and rankq's desk-belief AUC (Q1 to Q3) | **Yes**, from the same two configurations' control files |

## 4. What the reader does

1. Check the run's `producing_commit` is the sha in `/var/tmp/se-fix0-anchor-refit-landed.sha` (or a descendant named in
   the launch). Check that both configurations carry the same `world_identity.digest`, and that it is not `cdba75ebb9197b33`.
2. Publish Q1 to Q3, then the finding's R1 to R3 and the K8 page's R1a to R1c, then N1 if a cut configuration ran. All
   unrevised, quoting the grader's output.
3. Grade this record: one line per prediction, `held` or `missed`, and quote the miss.

**If the launch came first.** If the launch's start time is earlier than this record's commit on origin, this record
is graded **void, filed late**. The miss is written here and nothing is predicted after it.

**Reverse:** nothing to reverse. This is a record. It changes no code and launches nothing.
