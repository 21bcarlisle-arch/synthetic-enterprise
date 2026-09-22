**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The declined renewals now have a roster, and the block stops blaming churn for the arm's own refusals

**Claim:** `the-selection-leg-is-negative-and-nobody-has-asked-which-customers-it-loses-on`
**Pre-registered in:** `PREREG_THE_DECLINED_RENEWALS_ARE_NAMEABLE_ONLY_FROM_A_LOG_NO_ARTEFACT_KEEPS_2026-09-18.md`
**Drawn parts:** ONE — blocked, evidence below · TWO — already in force, confirmed · THREE — unblocked, not delivered

---

## The headline

Two changes to `tools/run_value_cycle_ab.py`:

1. **`decision_population` no longer asserts a mechanism its own numbers contradict.** It publishes
   a `reconciliation` block splitting the priced-denominator gap into the smaller arm's own
   refusals and everything else, and the three prose fields are now **derived from that split**
   rather than asserting one of its terms.
2. **A new `declined_renewals` block names every renewal the value arm refused**, joined to the
   level arm's own decision on that exact renewal.

## What was wrong, and it was wrong on every run ever recorded

`decision_population` published, unconditionally:

> `the_mechanism`: *"Sequential A/B roster divergence... `churn_roster_diff` names the accounts."*
> `why_this_is_not_a_defect`: *"Equalising the denominators would mean pricing renewals for
> customers who had already left, which is not a world any supplier operates in."*

On `s1_three_arm` the value arm priced 215 and declined **65**; the level arm priced 281 and
declined **0**. The gap is 66 and **65 of it is the value arm's own refusal of renewals both arms
reached**. Those customers had not left. The block asserted churn and carried no number that could
contradict it — and `level_vs_selection` took the licence that prose granted, differencing an
advantage over 215 renewals against one over 281 and publishing the residual as the worth of the
choosing.

The mechanism is one bound wide, in `company/pricing/value_based_renewal.py`: `VALUE_BASED`
**filters** candidate margins through the lawful ceiling *and* the churn support bound and raises
`MarginDecisionUnavailable` when none survives; `FLAT_AT_LEVEL` **clamps** to the lawful ceiling and
applies no support bound at all. A clamp always yields a price; a filter can yield nothing.

**Credit where it is due: the diagnosis above is the prior turn's, not mine.** It is in
`WORKER_RESULT_THE_SELECTION_LEG_DIFFERENCES_TWO_ARMS_OVER_DIFFERENT_PRICED_POPULATIONS_...`
(shared tree `96ec173c0`). What this turn adds is the repair to the artefact, the roster that makes
the customers nameable, and one correction to that finding.

## The correction, and it changes the sequencing advice

The prior finding recommends this emission and argues it is safe to land now:

> *"it is a change to `tools/run_value_cycle_ab.py`, not to the pricing arm — so it does not split
> the family and can land while next12 is in flight."*

**Refuted by this repo's own predicate.** `tools/fold_noise_floor_family.py:365`:

```python
_VALUE_ARM_PATHS = ("simulation/", "company/", "saas/", "tools/run_value_cycle_ab.py")
```

The runner **is** the fourth watched path, so this commit does make `_value_arm_pairing` report
`same_value_arm: False` between a family drawn before it and one drawn after.

**It costs nothing here, and I said so before landing rather than after.** `next12` is pinned at
`7da627b90`, which already differs from the eighteen's arm in 18 simulation files; it is unpoolable
already and the drawn item's own instruction is to read it **alone**. A family of one cannot be
split.

**But the predicate now has a false-positive class it did not have, and that is the finding.**
`_VALUE_ARM_PATHS` is a *file-set* proxy for a *semantic* question — "were these rows priced by the
same instrument?" It cannot tell the instrument from its instrumentation: this commit, which cannot
move a single price, reads identically to a change to `decide_margin`, which moves all of them. The
one control that just caught the real £671 step will now fire on reporting-only commits, and a
control that cries wolf is how the next real step gets waved through.

**Deliberately not fixed in this turn.** Narrowing a predicate in the same breath as the change that
tripped it is the asymmetric narrowing this project has a rule against — the false positive gets a
comment and the false negative never does. The honest fix is a second path list (the report
assembly) excluded from the arm question, and it should be taken by someone who is not the author of
the commit that wants it.

## What the two blocks now publish

`reconciliation` carries `gap`, `explained_by_declines`, `explained_by_roster_or_stage_divergence`,
`declines_share_of_the_gap` and `declines_are_the_larger_half` — three integers a reader can check
the composed sentence against, which is exactly what nobody could do before.

`declined_renewals` carries one row per decline: account, commodity, term start, the arm's reason,
the rate left untouched, and — where the join hits — the level arm's chosen margin, uplift, current
rate, offered rate and rate increase on that same renewal.

**There is no pounds figure in it, and that is the second pre-registered prediction holding.** The
entry carries `chosen_margin_gbp_per_mwh`, a **rate**, and no term volume. A pounds total formed here
would be a rate times a volume the block does not hold, or times a per-renewal average taken over
the *other* population — this project's own divide-two-different-things defect wearing a
decomposition's clothes. `money_unavailable_because` names what would close it: settled term volume
on the chain's entry, after which the sum over `renewals` is the **exact** structural offset
currently sitting inside `selection_gbp` with a negative sign. That replaces the prior finding's
£3,900 order-of-magnitude bound, which was explicitly an average over a population the declines are
not drawn from.

## The controls, and the mutations that prove they fire

Seven controls in `tests/tools/test_run_value_cycle_ab.py`. `decision_population` had **no test of
any kind** before this commit. Keyed to the property, not to today's answer: **nothing pins 64, 65
or 67**, and a run whose declines legitimately fall to zero passes all of them.

| mutation | what it simulates | fired |
|---|---|---|
| `residual = 0` | a split that does not reconcile to its own gap | ✅ `..._SUM_to_the_gap...` |
| `declines_are_the_larger_half = True` | a composer that says one thing on every input | ✅ `..._BOTH_mechanisms_are_reachable...` **and** `..._RETRACTS...` |
| join keyed on `customer_id` alone | a 2021 decline matched to a 2023 price | ✅ `..._keyed_to_the_RENEWAL...` |
| missing log reads as an empty roster | FAIL-OPEN: "no declines" ≡ "never recorded" | ✅ `..._REFUSES_rather_than_reporting_an_empty_roster` |
| absent level arm reports `0` joins not `None` | FAIL-SILENT: no level arm ≡ level arm priced none | ✅ `..._says_so_rather_than_reporting_zero_joins` |

The partition control asserts `declines_are_the_larger_half` **True and False over the whole
partition in one control**, rather than a leg per branch — a composer that only ever took one branch
would pass every per-branch leg.

### One mutation appeared not to fire, and it was neither a missing test nor an equivalence

M4 (fail-open) initially read green. The cause was **broken simulation**: my `-k` filter did not
select the test that grades it. Re-run with the correct selection it fails on
`assert (True is False)`. Recording it because "the mutation did not fire" has two flattering
readings and this was the third one.

## Corrections to my own work in this turn, kept beside the claim

- My first version of the retraction control banned the substring `"already left"` on the declines
  branch. It red the **honest** implementation, because the retraction deliberately quotes the
  sentence it withdraws — a wrong claim kept beside its correction is the evidence the correction
  happened. Worse, it would have passed a block that simply reworded the same defence. Re-keyed to
  whether the gap is **defended**, and the comment in the test says why.
- My test helper `_arm` silently shadowed an existing module-level `_arm` in the same file and red
  **24 unrelated controls**. I nearly attributed those to the pre-existing red register. Renamed;
  200/200 pass.

## Parts ONE and TWO of the drawn item

**ONE — blocked, and not guessed at.** `/var/tmp/value_cycle_ab_s1_noise_floor_next12_20260917.json`
does not exist. PID 3819244 is still running (413 CPU-min at 02:06 UTC). ETA **2026-09-18 11:31:24**,
~8.5h after this turn. Its mean, sem and sems-from-zero are **not reported here**. The instruction to
read it alone before folding stands and is untouched.

**TWO — already in force, and I re-checked rather than trusting the prior claim.** The page states
plainly that the discrimination reading comes from a different family than the advantage:
`site/data/value_arms.json` carries *"measured over a DIFFERENT family from the one the advantage
above is bounded over (the 3-seed AUC-carrying floor of 2026-09-17), so it bounds nothing on this
page"*, with the null (0.3870–0.6130, p=0.231) and `demonstrated: false`. The other half — compute
the AUC for the eighteen — is **not reachable**: `seeds_carrying_an_auc: 0`, the rows predate the
field, and the floor discards the per-seed `result` after writing its row, so there is no
re-derivation from disk at any sample size.

**THREE — unblocked, not delivered, and I will not claim otherwise.** The roster exists only once a
run executes this code. No run has. What this turn delivers is that the next run of any kind
produces the named customers, and that the artefact stops telling its reader a mechanism that is
false for 96% of the gap. **"Name the customers" is still owed and is now one run away instead of
unreachable.**

## What a control cannot yet see

The two remaining repairs are unenforced and deliberately sequenced after `next12`:

1. **The support bound on `FLAT_AT_LEVEL`**, which makes the priced populations equal by
   construction — and moves the published **+£19,277 at 63 sems**, so it is a director-visible
   headline change and not a side effect of a finding.
2. **`value_arm.priced == level_arm.priced` as a control**, which reds today, correctly, and must
   land *with* that fix rather than before it.
3. **Term volume on the chain's entry**, which turns this roster's bound into the exact figure.
