**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the renewal arm prices no gas)

# RESULT — the billing-account filter tripled the arm's decisions, and the method still cannot be told from chance

The prediction is `SEAT_PREREG_WHAT_THE_BILLING_ACCOUNT_RECORD_FILTER_MUST_MOVE_2026-09-07.md`,
written while the run was running and before any of these numbers existed. This document confronts
it. It sits **beside**
`SEAT_RESULT_ADMITTING_GAS_MOVED_THE_REFUSAL_AND_BOUGHT_ZERO_DECISIONS_BECAUSE_THE_ARM_ASKS_FOR_THE_GAS_LEGS_BOOK_UNDER_THE_WRONG_ID_2026-09-07.md`
and does not replace it, as that document asked: it holds a wrong prediction of mine next to its
result and is worth more intact.

## The pair

Same world (`world_identity.digest = 39a192ce04c1eda8`), same seed, same `--level-arm` three-arm
shape, same 2,039 offered renewals. One variable: `observed_account_state` matches a settled row to
the account by `_billing_account_id(...)` instead of by string equality.

| value-arm funnel stage | BEFORE (gas admitted) | AFTER (billing-account filter) | Δ |
|---|---|---|---|
| `acquisition_term` | 252 | 252 | 0 |
| `not_the_arms_commodity` | 0 | 0 | 0 |
| `product_not_upliftable` | 1,508 | 1,508 | 0 |
| **`no_observed_history`** | **179** | **0** | **−179** |
| `declined` | 6 | 63 | +57 |
| **`priced`** | **94** | **216** | **+122** |
| **accounts priced** | **66** | **100** | **+34** |

`122 + 57 = 179`. Every renewal that could not find its book now finds it, and every one of them
lands in a decision — 122 priced, 57 declined for want of a lawful margin. A decline is a decision
the arm made, not a refusal to look. Nothing else in the funnel moves by one.

## The predictions, in order

**1. `no_observed_history` falls from 179 toward 0 — "it should not reach 0 exactly."** It fell to
179 → **0, exactly**, and the caveat was wrong. The reasoning behind it was sound: a gas leg whose
first settled row lands inside the term being renewed has no prior book under any id. This world
simply contains none — every gas leg that reaches the stage settled at least once inside the
observation window before its renewal. The prediction was right and its hedge was not, and the hedge
is the part worth keeping: it is a real refusal shape that a different draw will produce.

**2. `priced` rises from 94 and `accounts_priced` rises from 66. "This is the claim."** 94 → **216**
and 66 → **100**. The claim holds. The alternative it was written against — that the 158 at
`product_not_upliftable` was the whole story and the gas legs sit on products no arm can price —
is refuted: `product_not_upliftable` did not move at all.

**3. `decisions_scored` rises from 54 and the accounts behind it from 38.** 54 → **170** and
38 → **72**. Three times the decisions on not quite twice the accounts, which is the dual-fuel book
appearing: an account that was one decision is now two.

**4. `detectable_excess` moves and I could not sign its direction.** It **fell**, 0.090496 →
0.050063 — and the reason is the denominator, not the arm. `detectable_excess` is the half-width of
the null interval, and the null spread narrows as the decision count rises: `null_sd` 0.046536 →
0.025664 on n = 54 → 170. This is the ceiling on what any signal could show at this sample size
getting *tighter*, which is the sample doing its job. Not signing the direction was right; the
reason it moved is not a reason either sign was available.

**5. `observed_share_of_what_was_detectable` is the one to distrust.** 0.5830 → **0.7517**. Both
numerator and denominator moved, in opposite directions — `observed_excess` fell 0.052760 →
0.037630 while the half-width fell further. **The rise is arithmetic, not skill, and it must not be
published as the arm improving.** The prereg said to distrust it and it is exactly as untrustworthy
as advertised; a figure that rises because its denominator shrank is the ratio-without-a-quantity
shape this project keeps paying for.

## What did not happen, and it is the headline

`observed_inside_the_null_interval` is **`true` in both runs**. Concordance 0.5378 sits inside
[0.4498, 0.5499]; `p_two_sided` moved 0.26035 → 0.14285. The arm now makes three times as many
decisions on a book it can actually see, and **this run still does not distinguish the method from
chance in either direction.** It moved toward separation and did not reach it.

That is the honest reading and it is not a disappointment: the defect being fixed was the arm
pricing half its book blind, and the fix is proved by the funnel, not by the concordance. The
concordance says what it has always said here — there are too few decisions to tell. There are now
170 instead of 54, which is the first thing that has ever moved that denominator.

## The pounds are NOT read as one-variable, as the prereg required

`realised_delta.net_margin_gbp` 7,155 → 19,655 and `enterprise_value_gbp` 4,078 → 18,605. **These
are not attributable to the filter.** Adding priced renewals changes churn rolls, so the two runs'
rosters diverge after the first gas renewal the arm prices differently. The artefact's own
`churn_roster_diff` puts realised coverage at 4 accounts only in the value arm and 1 only in the
control arm in both runs. A pounds delta across a diverged roster is not a one-variable quantity and
this document does not treat it as one.

## The artefact's own provenance stamp is one commit short, and the funnel is what closes it

`value_cycle_ab_leg_id_fixed_2026-09-07.json` stamps
`producing_commit.commit = 08ec389fbf0da2ffb8fd5eb9f223aedce0380ac5`. **The fix is not in that
commit.** `27c7672f7` landed at 02:50:50Z; the run bound its modules at 02:46:54Z, four minutes
earlier, from a working tree that held the fix uncommitted. The stamp resolves at process start and
records the last COMMIT, so by construction it cannot attest to working-tree bytes that are ahead
of it.

The funnel is what closes the gap, and it closes it completely. At `08ec389fb` the filter is
provably still `if r.get("customer_id") == account_id` — checked at that revision, not inferred —
and that filter cannot return `no_observed_history = 0` for a book whose gas legs are stamped with
the supply point. A run genuinely executing `08ec389fb`'s bytes would have reproduced 179. It
returned 0. The fix was in the run.

**Recorded because the next reader will hit it.** An A/B artefact's `producing_commit` is not
evidence of what code ran when the run is launched from a dirty tree — and launching from a dirty
tree is normal here, because the measurement is what decides whether the change is worth committing.
The stamp bounds the run from below and nothing more.

## Artefacts

- `docs/observability/value_cycle_ab_gas_admitted_2026-09-07.json` — BEFORE, commit `d1aebbd79`
- `docs/observability/value_cycle_ab_leg_id_fixed_2026-09-07.json` — AFTER, stamped `08ec389fb`, fix uncommitted in tree (above)

Both stamp `world_identity.digest = 39a192ce04c1eda8`.

## What this discharges, and what it does not

**Discharges** `SEAT_RESULT_ADMITTING_GAS_MOVED_THE_REFUSAL_AND_BOUGHT_ZERO_DECISIONS...`. That
document named one owed thing — "what is owed next, and it is one filter" — and required it be
measured one-variable rather than landed on a unit test. The filter is landed (`27c7672f7`) with its
class control, and the measurement is above. Archived to `docs/staging/done/`.

**Does not discharge writer 3.**
`SEAT_FINDING_THE_SAME_ID_MISMATCH_IS_LIVE_AT_WRITER_3_SO_NO_GAS_RENEWAL_IS_EVER_REPRICED_FOR_UNPROFITABILITY_2026-09-07.md`
is the same defect at `company/crm/customer_profitability.py:156`, still `== cid`, verified live at
HEAD in this turn. It is LATENT and correctly so. Its BEFORE is now
`value_cycle_ab_leg_id_fixed_2026-09-07.json`, which is what that finding asked for.
