**Knowledge:** acquisition-and-retention-economics

# A retention gate set by volume on the desk's own ranked beliefs (24 Nov 2026)

**Origin.** `docs/staging/records/SEAT_PREREG_WHAT_THE_SUPPLIER_DOES_ON_EACH_S12G_OUTCOME_2026-11-23.md`,
STRADDLE branch, taken when s.12g graded STRADDLE (`docs/design/THE_VALUE_TEST_REDESIGN.md` §12g, "s.12g
graded"). This page comes before the switch (K8). The switch is built only in the pinned test tree
`/var/tmp/value-test-cut012`. It is not on origin.

## What the gate is

At a renewal, the desk offers a retention cut when its own churn belief for that renewal is at or above the
belief that ranks the top share `q` of its beliefs at renewals in the 12 months before the day. Two decisions
that the 0.12 level fused are pulled apart here:
- **whom to offer**, which is the belief's ranking (A's conditioned belief), and
- **how many to offer**, which is `q`.

## What a real supplier could observe (the epistemic wall)

Every input is the supplier's own record:
- the churn belief it formed at each past renewal, and the dates of those renewals;
- the share of renewals it chose to make an offer at.

No world-side quantity enters. The window holds beliefs, not outcomes, so the gate needs no label and no
look-ahead: a renewal's belief joins the window after its own gate has been set.

## What is established and what is not

| Quantity | Status | Value carried |
|---|---|---|
| A retention offer at fixed-term end is lawful, and whom to approach is the supplier's discretion | Established. Knowledge map row *Retention offers (SLC 22B)*: under BAT's market-wide derogation, discretion survives over whom to approach, when and through which channel | n/a |
| The share of renewals a GB supplier makes a retention offer at | **NOT ESTABLISHED.** No published series gives it. The same row's gap says how deep real retention offers are is not published either | `None` as a domain value |
| `q` in this test | **Not a domain value.** It is a volume control copied from the comparator: the flat-rules twin's value-arm offers over its value-arm renewals the desk was asked about on book 61118, pooled over churn seeds 13131/14141 = **215/777 = 0.2767** | Test-only |
| The 12-month look-back | Set by the pre-registration's own wording ("the previous 12 months' renewals"). Not a domain value | Test-only |
| The 20-belief minimum before the gate ranks (until then it falls back to the standing gate at 0.30) | A design choice of the test, not a domain value. A quantile of a handful of renewals is not a volume | Test-only |
| The cut's size once the gate passes | Unchanged: the churn-belief tiers, and the lowest tier's share where the belief is under the lowest tier. This is the 0.12 cut's own rule, so the gate is the only variable | n/a |

## What the gate can and cannot show

- **Against the twin (P1's measure).** If rank-at-q beats flat rules with an interval that excludes zero, A's
  ranking adds value at the twin's volume, and no fitted level is needed.
- **Against the cut.** The single variable is the fitted 0.12 level replaced by the volume match.
- **Bound, measured before the run.** On 61118 the cut already offered at 218 of 774 value-arm asked
  renewals (28.2%), against the twin's 27.7%. The rank gate offers at the gate's own share, and the value test
  still refuses after the gate, so the realised share will sit below `q`. That is the rule as registered,
  not a choice made here.

## Where it would live if it ever left the test tree

`company/interfaces/growth_desk.py`, beside `retention_tier_share`, as a default-off policy field. Moving it
to origin is not proposed: the 24 Oct ruling (levers after the basics) and the open row
`the-live-renewal-belief-ranks-leavers-backwards` both stand.
