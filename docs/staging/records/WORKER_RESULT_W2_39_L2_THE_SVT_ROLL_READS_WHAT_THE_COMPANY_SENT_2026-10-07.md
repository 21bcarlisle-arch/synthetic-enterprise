# W2_39 L2: the SVT roll reads what the company sent

*Worker, 2026-10-07. Claim `w2-39-the-svt-roll-reaches-the-contact-response`.*

## What was built

- **The seam.** `SimInterface.send_contact(account_id, sent_on, instrument)`: COMPANY -> WORLD. The
  only reply is whether the contact went. The stub and an unconnected live seam both say it did not,
  with a reason.
- **The world's record.** `contact_response.ContactsReceived`, one per run. Only the seam writes
  to it, and only the SVT roll reads it. An instrument with no sourced woken share is refused when
  it is sent.
- **The roll.** In `run_phase2b`'s SVT branch, when a contact reached the household inside the
  segment, the departure probability becomes `svt_departure_after_contact(p_drift, churn_if_choosing_off_svt(...))`.
  It is rolled on the same draw. `svt_cause_on_the_coupled_roll` files a drift departure as
  `svt_inertia`, exactly as before, and a woken leaver as `price_position`. Each row carries
  `contact_instrument` (the company's own send) and `sim_p_depart_uncontacted` (ground truth: the
  counterfactual an uplift estimate is graded against).
- **The sender.** `DecisionPolicy.svt_contact_instrument` is the flat rule: every SVT account, at
  each segment's start. It is `None` on every standing policy. It is the baseline C34's per-account
  decision has to beat.

## The §5 question, before any constant

What a woken household weighs is the default it is on, set against `_price_differential_vs_market`,
the one reference every renewal uses. That reference is never the market's cheapest fix. So from
2016 to 2019 the loss is understated, in the company's favour. This is named in the research doc
§5, not patched with a second "market". No constant was added.

## Numbers (pre-registered first)

Same book, 2016-01 to 2017-12. Predicted: about +3 pp per contacted segment for `collective_switch`
and about +0.7 pp for `cmoc_letter`.

| arm | segments | drift departures | woken leavers | mean woken churn | added per segment |
|---|---|---|---|---|---|
| none | 274 | 14 | 0 | — | 0 |
| collective_switch | 245 | 14 | 7 | 0.233 | +4.6 pp |
| cmoc_letter | 271 | 14 | 1 | 0.237 | +0.9 pp |

Both predictions came in low. I assumed a woken chooser churned near the parity column (0.17), but
its premium is not at parity. In all 245 paired segments the roll and the uncontacted probability
are identical to the no-contact arm's.

## Controls

- `tests/simulation/test_a_run_reaches_the_svt_contact_response.py`: two runs to 2017-02-28, 2 passed.
  Mutation: delete the run loop's `send_contact` call. Result: red, `assert ([])` on the contacted set, 1 failed.
- `tests/simulation/test_contact_response.py`, +4 tests. Mutations: the segment window, the
  middle-band cause and the dropped `receive` each red. `roll <= p_uncontacted` stays green, an
  equivalence on a continuous draw.
- `tests/company/policy/test_policy_field_consumption.py` declares the field `run_argument`.

## Not L3

- The fixed-term roll does not yet read a contact.
- No per-account sender exists (C34).
- The reference is the default, not the best fix.
- No source here splits each trial's switchers into external and internal.
