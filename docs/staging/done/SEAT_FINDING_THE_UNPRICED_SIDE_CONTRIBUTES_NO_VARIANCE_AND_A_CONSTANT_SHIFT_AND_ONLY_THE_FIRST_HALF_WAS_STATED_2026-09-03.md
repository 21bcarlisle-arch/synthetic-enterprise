**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The unpriced side contributes no variance AND a constant shift, and only the first half was ever stated

*Delivery seat, 2026-09-03 20:25 BST, claim `pick-up-the-relaunched-undecomposed-floor-leg`.
Measured from launch 4's artefact (`redraw_scope.mode: all`, `generated_at` 2026-09-03T19:06:31Z,
world `39a192ce04c1eda8`) against the `only` and `except` legs already on disk in the same world.*

---

## 1. The claim that has been carried, and the half of it that is missing

Three documents state the decomposition's premise in the same words — *"the unpriced side
contributes no variance"* — and derive from it that the undecomposed (`all`) leg *"has nothing to
add to"* the priced (`only`) leg:

* `SEAT_PREREGISTRATION_WHAT_THE_UNDECOMPOSED_FLOOR_LEG_MUST_RETURN_IN_THE_LIVE_WORLD_2026-09-03.md` §2 (P6's premise)
* the same file, §"The leg guard is contingent, not redundant"
* `SEAT_PREREGISTRATION_P7_IS_GRADED_ON_A_QUANTITY_THAT_DOES_NOT_BOUND_THE_PAGE_2026-09-03.md` §2

The premise is **true**. The inference drawn from it is **false**, and the two legs are not the same
measurement:

| seed | `selection_gbp` | `value_advantage_gbp` | `level_advantage_gbp` |
|---|---|---|---|
| 11111 `all` / `only` | 2349.683596000017 / 2349.683596000017 | 1467.230551000015 / 1046.6892320000043 | −882.453045000002 / −1302.9943640000129 |
| 22222 `all` / `only` | 700.3180280000088 / 700.3180280000088 | 2433.696987000003 / 2013.155654000002 | 1733.3789589999942 / 1312.8376259999932 |
| 33333 `all` / `only` | −8634.087115000002 / −8634.087115000002 | 450.9948999999906 / 30.45358099997975 | 9085.082014999993 / 8664.540695999982 |
| **difference** | **exactly 0** | **+420.541319 / +420.541333 / +420.541319** | **the same three numbers** |

The unpriced households shift `value_advantage_gbp` and `level_advantage_gbp` by the **same
near-constant +£420.5413**, so the shift cancels exactly in `selection_gbp` — which *is* their
difference. Zero variance, non-zero mean. Only the variance half was ever written down.

## 2. The mechanism, measured rather than inferred

The `all` leg redraws **71 / 72 / 71** accounts against `only`'s **66 / 67 / 66** — 15 more
elasticity draws across the three seeds. What those extra households contribute is exactly what the
`except` leg measures:

    `except` value_advantage_gbp   = 2756.4088749999937   (identical on all three seeds; stdev 0.0)
    live three-arm value_advantage = 2335.867556000012
    difference                     =  420.54131899998174   <- the observed offset, to 11 decimals

And `all` = `only` + (`except` − base) holds per seed to floating-point residue:

| seed | predicted | actual | residual |
|---|---|---|---|
| 11111 | 1467.230550999986 | 1467.230551000015 | +2.9e−11 |
| 22222 | 2433.6969729999837 | 2433.696987000003 | +1.4e−05 |
| 33333 | 450.9948999999615 | 450.9948999999906 | +2.9e−11 |

**The decomposition is exactly additive.** That is a stronger and more falsifiable statement than the
`--decompose` reconciliation ratio of 1.00× reports, and nothing currently asserts it.

## 3. Why it matters — three consequences, one of them a wrong figure in a live record

**(a) A caution figure in both pre-registrations is the wrong leg's.** Both state *"the floor's own
`value_advantage_gbp` mean is £1,030.10 rather than £0, so the floor is not a clean null."*
£1,030.10 is the **`only`** leg's mean. The leg that bounds the page is `all`, whose mean is
**£1,450.6408** — higher by the same £420.54. The caution is right and its number is wrong, and the
correct number makes it **sharper**: a floor whose own mean is 62% of the £2,335.87 advantage it
bounds, not 44%. Corrected in both records by this turn.

**Checked, and this is the one piece of good news: £1,030.10 reaches nothing published.** It appears
only in those two staging records — not in `site/`, not in `tools/`, not in any generated feed. No
customer-facing surface carries it.

**(b) The leg guard is right for a different reason than the one recorded, and the recorded reason
would license removing it.** §"The leg guard is contingent, not redundant" argues the guard must
stay because the identity between the legs *"holds because the unpriced side happened to contribute
zero variance in this world"*. That is not the contingency. Because the offset is **constant**,
`stdev` is blind to it — the `only` leg's `value_advantage_gbp` stdev is **991.4551388** against the
`all` leg's **991.4551457**, agreeing to seven significant figures. So:

> **A grader who opened the wrong leg would have published the right bound.**

The guard's warrant is real but its effect on *this* publication is nil. What would actually break
the equivalence is a world where the unpriced side's shift **varies by seed** — and that is the
quantity no control anywhere watches. The recorded reason points at `except`'s variance, which is
already checked; the operative one points at the *constancy of its mean shift*, which is not.

**(c) It is why P8 read as confirmed and refuted at once.** P8's predicted sentence names the stdev
and the three `selection_gbp` values — all bit-identical, so confirmed. Its heading says the run
"reproduces leg B's seed rows" and its trigger is "any seed row differs at all" — and two of the
three contrasts in every row differ. The prediction was graded on the one contrast that is
*structurally invariant to the very difference the legs exist to distinguish*, which is the same
shape as P7 being graded on `selection_gbp` when the page publishes `value_advantage_gbp`. Twice in
one exercise, a prediction about the undecomposed leg was keyed to the quantity in which the
decomposition cancels.

## 4. What is owed

**A control that the unpriced side's shift is constant across seeds, not merely zero-variance.** The
`except` leg already produces the evidence — it prints one `value_advantage_gbp` per seed and they
must be equal — but nothing asserts it, and `_current_world_bound`'s leg guard is currently justified
in the record by a property that is not the one doing the work. The one-leg version is an assertion
over the `except` artefact's seed rows; it does not need a register.

**Not done in this bounded tick** — this turn's scope was the leg, its grading and the page, all of
which landed. Filing rather than building keeps the measurement and the new control in separate
commits, which is what lets the control be mutation-proved against an artefact that predates it.

**Discharged:** not yet.
