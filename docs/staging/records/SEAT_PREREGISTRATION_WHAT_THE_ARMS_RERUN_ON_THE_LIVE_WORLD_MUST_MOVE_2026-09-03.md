**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# What the three-arm re-run on the live world must move

*Delivery seat, 2026-09-03, lane-0, claim `the-baseline-was-beaten-in-a-world-that-no-longer-exists`.
Filed BEFORE any arm is re-run. §1 is measured and is not a prediction. §2 is the prediction, and it
is filed while the published figures are still the 2026-08-31 ones, so nothing here is written with
the answer in hand.*

---

## 1. The size of the world change, measured — act (a)

The published contrast under `/capabilities/` comes from `value_cycle_ab_s1_three_arm.json`
(`generated_at` 2026-08-31T03:47:57Z, producing commit `fe4df178b`) and
`value_cycle_ab_s1_noise_floor.json` (07:05:53Z, `4240e1478`). `simulation/departure_level_anchor.py`
has been re-fitted twice since — `a621edb15` and `712ae5323`, plus the second-pass values at HEAD.

One variable, one capture. `c6_second_pass_departure_factors.json` (133 renewal + 1,313 SVT rows,
executed under the live block) scored twice: once under the anchor table the arms ran on, once under
the table live today. The SVT contribution is anchor-invariant — `level_anchor` multiplies only
`bill_shock_base`, `price_response` and `dissatisfaction_response`, which the SVT route builds at
0.0 — so it is held identical on both sides and the renewal leg is the entire difference. The
arithmetic is `tools.fit_year_level_anchor._sum_probability`, the same function the fit itself
solves against, so this is not a reimplementation.

| year | accts | ren | svt | arms anchor | live anchor | ×    | arms % | live % | Δpp    | published % |
|------|-------|-----|-----|-------------|-------------|------|--------|--------|--------|-------------|
| 2016 | 3     | 1   | 2   | 4.5973      | 4.2599      | 0.93 | 5.748  | 5.351  | −0.397 | 17.60 *(partial)* |
| 2017 | 58    | 20  | 118 | 4.2569      | 7.3726      | 1.73 | 10.693 | 14.000 | **+3.307** | 14.00 |
| 2018 | 50    | 17  | 143 | 3.3458      | 2.9453      | 0.88 | 21.099 | 20.000 | −1.099 | 20.00 |
| 2019 | 41    | 13  | 113 | 3.2281      | 6.6373      | 2.06 | 16.400 | 21.300 | **+4.900** | 21.30 |
| 2020 | 46    | 13  | 135 | 4.4257      | 6.3593      | 1.44 | 20.148 | 22.973 | **+2.825** | 23.00 |
| 2021 | 51    | 20  | 150 | 3.2199      | 5.6413      | 1.75 | 14.390 | 18.531 | **+4.140** | 18.40 |
| 2022 | 51    | 0   | 197 | 1.5241      | 1.0000      | 0.66 | 2.500  | 2.500  | ±0.000 | 4.30 |
| 2023 | 53    | 19  | 193 | 2.0915      | 2.0332      | 0.97 | 12.557 | 12.400 | −0.157 | 12.50 |
| 2024 | 57    | 16  | 170 | 3.0208      | 4.2599      | 1.41 | 13.486 | 15.960 | **+2.474** | 16.10 |
| 2025 | 52    | 14  | 92  | 2.1186      | 4.2599      | 2.01 | 9.779  | 14.952 | +5.174 | 17.90 *(partial)* |

**Over the eight full years: mean whole-book expected departure 13.909% → 15.958%, mean move
+2.049pp. Expected departures 55.7 → 63.8, a rise of 14.6%, on 407 account-years.**

2022 is flat because it has zero renewal decisions — the anchor multiplies nothing there, which is
what `NO_LEVEL_CORRECTION` records.

### The drawn instruction's premise is refuted, and it is the same error as last time

Act (c) of the draw states: *"The world got **easier** to hold — fewer departures on the renewal
route than the old anchor produced — so there is less book to re-win and the per-customer arm has a
smaller surface to act on. Write down before the run whether you expect the advantage to shrink."*

**The world got HARDER to hold. Five of the eight full years' anchors rose, by up to 2.06×, and
expected departures rose 14.6%.** The premise is not marginally wrong; it has the sign backwards.

This is the identical error `simulation/departure_level_anchor.py` already records against the
previous pass's drawn instruction — *"The drawn instruction for this pass asserted the opposite
('this move lowers churn toward the record') and told the seat to invert the detector; that premise
was read off the RENEWAL-ROUTE table, which is 7-of-7 out and high, and the whole book is the
comparable quantity."* The draw's phrase *"on the renewal route"* names the same non-comparable
column. The whole book is the quantity, and it moved the other way.

**Consequence for the trap detector.** The draw says *"a result that moves the advantage the
flattering way, unpredicted, is a defect in the re-run and not a win."* That detector was armed
against a shrinking surface. On the measured direction the surface GREW, so an advantage that grows
is the mechanically expected result and not a flattering surprise. The detector is therefore
**inverted below, in §2, before the run, with the reason stated** — which is what the anchor file
says was correctly *refused* last time when the evidence pointed the other way. It is inverted here
because the measurement supports it, not because the instruction said so.

### Act (a)'s stated stopping rule does not apply

The draw offers an early exit: if the years moved by less than the seed spread, publish a provenance
line and do not re-run. That comparison cannot be taken literally — the spreads are in £
(`stdev_gbp` 2291.07 on `value_advantage_gbp`) and the world move is in percentage points, and
dividing one by the other is not a quantity. Taken on its evident intent — is the world change small
against this instrument's own noise? — the answer is still no: a 14.6% change in the number of
departures is a change in the *surface the arm acts on*, not a wobble in the figure measured on it.
**It matters. Act (b) applies.**

---

## 2. The prediction, filed before the run

### P1 — every arm's absolute net margin FALLS

More departures means less book retained means less margin, for all three arms alike. The anchor's
own one-variable pair recorded net margin −4.4% and gross −3.8% for a single re-fit pass; this is
two passes and a larger move.

> **Predicted:** `control_arm.total_net_gbp`, `value_arm` and `level_arm` all fall from their
> 2026-08-31 values (145,881.43 / 157,952.50 / 155,378.13), each by **3–12%**.
> **Refuted if:** any arm's realised net margin rises.

### P2 — the value arm's ADVANTAGE over the control GROWS

This is the prediction that matters and it is in the flattering direction. The reason is mechanical:
the advantage is earned on renewals the flat rule loses and the per-customer arm holds. A book that
sheds 14.6% more households offers proportionally more such decisions, so the surface the advantage
is earned on grew with the churn.

> **Predicted:** `level_vs_selection.value_advantage_gbp` rises from **£12,071.08** to roughly
> **£13,000–£14,500** — central estimate **+15%**, tracking the departure rise, wide band because
> the cascade is not linear.
> **Refuted if:** it falls below £12,071.08, or rises above £16,000 (a rise much larger than the
> surface change would mean something other than the anchor moved it).

**This is a prediction of a flattering movement, and it is filed as one deliberately.** If the
advantage instead *shrinks*, P2 is refuted and the draw's premise was accidentally right about the
outcome while wrong about the mechanism — which would need its own explanation, not a shrug.

### P3 — the selection leg is STILL indistinguishable from zero

The floor is set by how many decisions the arm actually *prices*, not by how many households leave:
the decomposition establishes that every priced decision belongs to the hand-authored static roster
(10 independent draws, 20 priced decisions), and that drawn households' renewals stop at
`product_not_upliftable`. The anchor changes departures, not the priced roster.

> **Predicted:** `priced_decisions` stays in **15–25**; `selection_gbp` remains smaller than its own
> seed spread, so the page still says the instrument cannot resolve it.
> **Refuted if:** the re-run resolves the selection leg — which would be a finding about the
> decomposition, since nothing in the anchor should have changed the priced count.

### P4 — the noise floor WIDENS

More churn means a larger cascade behind each elasticity draw, and the decomposition already
attributes ~100% of the floor's variance to the priced side.

> **Predicted:** `selection_gbp_spread.stdev` rises from **3776.27**.
> **Refuted if:** it falls, which would mean the harder world is *quieter*, and the decomposition's
> attribution of the variance to the priced side needs re-reading.

### P5 — a constraint on the run itself, not an outcome

All four legs (three-arm, floor `all`, floor `only`, floor `except`) must come from ONE session on
one tree, as `tools/run_arms_rerun_detached.sh` does, and be written to NEW stamped paths. Grading
a new contrast against the old floor is the defect `c30b98048` was filed for.

> **Refuted if:** the artefacts that end up published carry more than one `producing_commit`, or if
> any existing artefact is overwritten in place.

---

## 3. What this turn did and did not do

**Did:** the §1 measurement; the missing control (below); the page's vintage line.

**Did NOT:** run the arms. Two reasons, both recorded so the next turn does not re-derive them.
(i) The four legs cost ~8 hours — 45 min for the three-arm leg and ~2h24 for each of three floor
legs, from the 2026-08-29 log — which no bounded tick can hold. (ii) At 10:30 a second seat
(pid 2917963) was already running this same Lane 0 item in an isolated worktree, and a full pytest
suite was at 67% CPU. Launching a duplicate 8-hour run on one box would contend with both and
duplicate whatever that seat lands.

**The next turn's first act is to check whether that seat landed the re-run before starting one.**
If it did not, the launch is
`systemd-run --user --unit=arms-rerun-20260903 tools/run_arms_rerun_detached.sh` with the stamp
changed — never a bare background job, which dies with the tick's cgroup.

---

## 4. Grading, 2026-09-03 — three-arm leg in, floor legs still running

*Appended by the next turn of the same claim. The three-arm leg landed as `416e829c7`
(`value_cycle_ab_s1_three_arm_20260903.json`, `generated_at` 2026-09-03T10:17:07Z, producing commit
`ace28fa44`, `world_identity.digest` `39a192ce04c1eda8`). §2 above is untouched — the predictions
are graded beside themselves, not revised.*

### The measurement

| quantity | old, 2026-08-31 | new, 2026-09-03 | move |
|---|---|---|---|
| `control_arm.total_net_gbp` | 145,881.43 | 138,152.77 | **−5.30%** |
| `value_arm.total_net_gbp` | 157,952.50 | 140,488.64 | **−11.06%** |
| `level_arm.total_net_gbp` | 155,378.13 | 138,311.98 | **−10.98%** |
| `value_advantage_gbp` | 12,071.08 | **2,335.87** | **−80.65%** |
| `level_advantage_gbp` | 9,496.70 | **159.21** | **−98.32%** |
| `selection_gbp` | 2,574.37 | 2,176.66 | −15.45% |
| `level_share_of_advantage` | 78.67% | 6.82% | |
| `level_gbp_per_mwh` | 54.25 | 48.25 | −11.06% |
| renewals offered (value arm) | 1,953 | 2,009 | +2.87% |
| **priced decisions (value arm)** | **120** | **104** | **−13.33%** |
| priced share of renewals | 6.14% | 5.18% | |

### P1 — CONFIRMED

Predicted: all three arms' net margin falls, each by 3–12%. Realised: −5.30%, −11.06%, −10.98%.
All three fell; all three inside the band. Refutation condition (any arm rising) did not fire.

### P2 — REFUTED, and in the UNFLATTERING direction

Predicted `value_advantage_gbp` rises 12,071.08 → **13,000–14,500**. Realised **2,335.87**, a fall of
80.65%. The stated refutation condition — *"refuted if it falls below £12,071.08"* — fired.

**The mechanism was wrong, and the specific error is nameable.** P2 reasoned that the advantage is
earned on renewals the flat rule loses and the per-customer arm holds, so a book shedding 14.6% more
households offers proportionally more such decisions. Departures did rise and renewals offered did
rise (+2.87%) — but **the quantity the arm's advantage is actually earned on is priced decisions,
and those FELL 120 → 104 (−13.33%)**. Renewals offered is not the surface; priced is. P2 differenced
the wrong denominator, which is this project's recurring shape (*"before dividing two numbers, say
out loud what each one counts"*) appearing once more, in the prediction rather than in the result.

Note also what P2 got right and could not use: the draw's own premise ("the world got easier, so the
advantage shrinks") reached the correct DIRECTION through a mechanism §1 measured as false. §1's
refutation of the draw stands — the world got harder, +2.049pp mean, expected departures +14.6% —
and P2's inference from that correct measurement was still wrong. **A correct measurement does not
make the next inference from it correct**, and this is the cleanest example of that the record holds.

### P3 — CONFIRMED on the leg that is in; the priced-count clause is PENDING

`selection_gbp` 2,574.37 → 2,176.66. It remains far smaller than the old floor's own ±3,776.27
spread. `priced_decisions` in the three-arm run is 104, but P3's 15–25 band was written about the
DECOMPOSITION's book (20 priced of 1,369), which is a different and smaller book than the three-arm
run's (104 priced of 2,009) — that non-comparability is the `withdrawn_claim` the feed already
carries. **The clause is gradeable only against the re-run decomposition, which is still running.**

### P4 — PENDING. P5 — PENDING, with one clause already at risk

The three floor legs are in flight as transient units `se-noise-floor-20260903`,
`se-floor-only-20260903`, `se-floor-except-20260903` (started 10:18/10:23Z, ~2h24 each).

P5's substantive clause — one world on both sides — is testable and is the one that matters:
`world_identity.digest` must read `39a192ce04c1eda8` on all four legs. **P5's literal clause ("more
than one `producing_commit`") is already at risk and should be graded honestly rather than
generously**: the three-arm leg bound its modules at 09:43Z and the floor legs at 10:18/10:23Z, so
they are near-certainly different commits. If the digests match, the legs are one world and the
comparison is sound; the commit clause was a proxy for that test and a worse one. Say which test was
passed, not that "P5 passed".

### The bound that must NOT be quoted until the floor legs land

£2,335.87 sits about 1.02× the OLD floor's ±£2,291.07 on `value_advantage_gbp`, where £12,071 sat at
5.27×. **That ratio must not be published, or used to decide "resolved", because it prices a new
world's figure against an old world's bound — the exact defect `c30b98048` was filed for and the one
act (b) exists to prevent.** It is written here only to record that the question is now live, and it
is answered by the new floor or not at all.

---

## 5. 2026-09-03, later — the current-world figure is now ON the page, unbounded and labelled so

*Appended by the next turn of the same claim. §2 is still untouched; P4 and P5 are still pending and
are graded when the floor legs land, not before.*

### What changed

The live-world three-arm run was landed on 2026-09-03 and **the page did not read it**. So the
repository held the one figure measured in the world that is live and published only the 2026-08-31
ones, under a "READ THIS AS HISTORY" headline. Withholding is not the correction; dating is.

`/capabilities/` now leads with the mixed-world verdict, then the current figure and its refusal,
then the superseded run kept with its own date:

> THE FIGURE BELOW AND THE BOUND ON IT WERE MEASURED IN DIFFERENT WORLDS. The runs behind it are
> dated 2026-08-31. […] **IN THE WORLD AS IT IS NOW, the same comparison gives £2,336, measured
> 2026-09-03T10:17:07Z. THIS PAGE STATES NO VERDICT ON THAT FIGURE**: every bound it holds was
> measured in the superseded world […] It is published unbounded and labelled unbounded rather than
> withheld, and the older figures below are kept with their own date beside it. Running the same
> book through the per-customer decision engine earned £12,071 MORE than flat rules […]

`current_world` in the feed carries every figure, its world digest, its producing commit, and
`resolved: None` — never `False`, because "not measured" and "measured and did not clear" are
different states and only the first is true.

### The £2,336 / £2,291 ratio is refused in code, not in prose

§4 recorded that the new contrast sits about 1.02× the OLD floor and that the ratio must not be
published. That was a note to the reader; it is now a control. `_current_world_contrast` reads the
floor for its world and its date and **never for a number**, and the door rung greps the rendered
text after the figure for a `Nx` multiple and reds on one. A page that printed it would look more
rigorous and be less true, which is why it is asserted rather than left to review.

### A defect found in the process, and it was one branch from being published

Wiring the live-world run into the page exposed that `_world_provenance`'s mixed verdict — the whole
point of which is *"when one leg IS the live world, 'read this as history' is false about that leg"*
— was implemented for only one of the two ways a page can be mixed. A live leg beside an
**unstamped** one took the early return, which sets no `one_world_across_every_figure` key, and
`_world_clause` read the absent key with `is False` and fell through to the history sentence. It had
never fired because until today every artefact predated the stamp. Filed as
`SEAT_FINDING_THE_MIXED_WORLD_VERDICT_HAS_NO_BRANCH_FOR_A_LIVE_LEG_BESIDE_AN_UNSTAMPED_ONE_2026-09-03.md`
and repaired by making the existing verdict reachable, not by writing a second sentence.

### Mutation record — six run and reverted, under `python3 -B`

| mutation | red |
|---|---|
| drop `_current_world_clause` from the headline | door rung |
| unstamped branch stops naming the mixed verdict | `..._a_live_leg_beside_an_UNSTAMPED_one...` |
| mixed verdict becomes a constant `False` | `..._a_run_that_cannot_name_its_world...` |
| `resolved` reports `False` instead of `None` | door rung |
| current-world block skips the world-digest check | `..._refuses_a_run_that_names_another_world` |
| `why_no_bound` drops the world it would have come from | same |

Two of these first SURVIVED and were established as a tautology and an equivalence rather than
assumed to be either. The mixed-verdict mutation survived because the only rung watching it read the
same feed key it asserted, so both moved together; the digest mutation survived because the artefact
on disk genuinely IS the live world, so removing the check changes nothing for that subject. Each
now has a sole-witness subject that no other rung can satisfy.

### What is still owed, and it is the whole of P4 and P5's substantive clause

The floor legs. `only` and `except` have been running since 10:23Z; the `all` leg was **OOM-killed at
11:27Z with `ExecMainStatus=9` and wrote nothing**, and is re-queued as `se-noise-floor-all-20260903b`
behind the other two. Until all three land with `world_identity.digest` `39a192ce04c1eda8`, the page
states no verdict on the current figure — which is the correct verdict and not a gap in the leg.

**P4 and P5 remain ungraded. Nothing in this turn touched them, and the ratio that would settle
"resolved" is exactly the one now refused in code.**
