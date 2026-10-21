**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used` · **Claim:** `flip-the-read-instruction-on-with-its-visit-cost` (Lane 0 delivery)
**Knowledge:** read-access-and-theft-duties

# The read instruction is on in the standing policy and charges 469 visits, not 582, and no value arm can see the cost

Landed with the flip. `DecisionPolicy.instruct_reads_in_billing_run` is now True. In the same change,
each visit the billing run sends is charged £3 (an area round) to account 6100, and £17.50 (an
appointment) is published beside it as the bound. Knowledge first: `read_access_and_theft_duties.md`
§2.9, which names the §2.6 GAP (round or appointment at the 11th estimate).

## Correction to the finding that asked for this

`SEAT_FINDING_THE_READ_INSTRUCTION_PERFORMS_21B4_FOR_NO_MONEY_AT_NO_ACCESS_SO_FLIP_IT_ONLY_WITH_THE_VISIT_COST_2026-10-21.md`
priced 582 visits: £1,746–£10,185. **582 counts instructions, not visits.**
- `monthly_bill_assembly` sends a visit only when the period's ordinary read has not already come
  in. On the 8927e9345 `register` arm, 113 of the 582 had their own read arrive first. Those are the
  "113 no-access visits record outcome actual" that the finding left open.
- So 469 visits went out, which is also the decomposition's 469, the finding's other open item.
- The bound is therefore **£1,407 charged, £8,207.50 at the upper bound**, over ten years. Measured
  on that arm's bills: this change's first draft, which counted every instruction, gave £1,746;
  at no access every visit sent reads nothing, and `outcome == "no_read"` counts 469.
- Bills now carry `read_instruction_visit_sent`. A run output from before this change has no such
  key, so `read_duty_summary` publishes `visits: None`, with its reason, rather than 582.

## The value arms: none needs re-taking for this line, and that is a blindness, not a pass

The item asked for a list, before landing, of the value arms graded against a published run's
margin (`tests/tools/test_generate_value_arms_data.py`), on the premise that the cost moves opex.

- **Every value-cycle arm grades `total_net_gbp` on the settled-realised clock.** This covers the
  control, value and level arms, the SVT arms and the three-arm book. `tools/run_value_cycle_ab.py`
  sums `net_margin_gbp` from the world's settled records, which is gross − capital − bad debt. It
  reads nothing from the ledger. The visit cost posts to the ledger (`read_visit_cost_event`,
  account 6100), so it moves `operating_net_margin_gbp` on the dashboard and annual report and **no
  arm**. This is true of every account-6100 cost, cost-to-serve included (page §6, code gap 6a).
- **The flip itself moves no settled money at the standing (`register`) end.** The 8927e9345 arms
  found every run-output key equal apart from the `read_instruction_*` keys.
- **The published arms are already withheld as not-current.** `site/data/value_arms.json`'s
  `current_world.code_since_the_run` refuses on 131 unexempted substrate paths since 45122d156. My
  paths join a refusal that already stands, so no exemption was written: one could not change the
  verdict.

## Not established

- Whether the value arms *should* see account-6100 costs. Comparing arms on a clock that omits
  operating cost is fine while both arms carry the same cost. A policy whose cost differs between
  arms, as this one would between `off` and `on`, is invisible to them. This is a question about
  what the arms measure. It needs no new number.
- The access rate (`q6_read_visit_access_failure_rate`): still null, still a practitioner question.
