**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [ADVISOR-CHASE] Nine breaches stand between the site and current; clear them or name them today (2026-11-02, 14:35)

**Type:** CHASE, through the advisor channel, on `DIRECTOR_STEER_THE_VALUE_TEST_MUST_BE_ABLE_TO_ANSWER_AND_THE_SITE_MUST_BE_CURRENT_2026-11-02.md` (now in done/). The director's words, from chat on Mon 2 Nov:

- 07:29 GMT: "Yes. And please make sure the website is up to date"

## Where it stands at 14:32

Today's work moved this well:
- the over-ceiling refusal was a grader defect, now fixed;
- the census false positive is fixed;
- the dropped SLC 22C statements are fixed;
- the banner now explains the pause in plain words;
- the 85b044be54 book was graded against both pre-registrations.

Your 14:16 answer is accepted: the pages cannot be rebuilt on 4ae8da9b0f, because today's gate refuses that book.

**What stops the site being current now is small.** At 7c34f48a64 the gate refuses on nine breaches:

| Invariant | Breaches |
| --- | --- |
| E7 meter billed on two registers | 2 |
| Read monotonic | 2 |
| ToU bands sum to the total | 2 |
| Estimate follows the latest actual reads | 3 |

The site is still on 26 Oct, eight days stale.

## Ask, today

1. **Trace and fix each of the nine.** Several already have a known cause from today's Economy 7 work (11:37, 13:10, 13:20). Fix those first.
2. **Name what you cannot fix today.** If a breach is traced, its cause is understood, and it is confined to a few named accounts, record it as a **named, dated exception** under the correctness ruling's own rule, rather than leave the whole site a further week stale. Each exception needs:
   - its accounts;
   - its cause;
   - why it does not move a published figure materially;
   - the commit that will retire it.

   An untraced breach is never excepted.
3. **Then publish the first book that passes.** If the book needs a re-run to carry the fixes, start it at once. Say in Done when the site will be current. If it cannot be current today, say so plainly and give the earliest realistic time.

## Done (2026-11-02, delivery seat)

- **The nine are cleared.** The publisher graded the 65bbdc6787 book (run finished 15:48Z, 1,293 accounts) with
  all nine at 0: 1b709ac0e9 and 8cf2ecb744 did what they said. The 7c34f48a64 marker is superseded by it.
- **One row new to the refusal list.** The refusal string, from `docs/reports/domain_invariants.json` and the
  banner commit 8e769778d3: "domain-invariant breaches at git=65bbdc6787 that no exception covers:
  INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS 18 (no exception)". The 8cf2ecb744 prediction ("estimate-after-actual
  3 -> at most 1") was wrong: 18, because the same fix gave those accounts correct per-register reads for the row
  to grade against.
- **Traced to one cause, on four accounts**: PROS-2017-0336 (12), SYN-2016-565 (4), SYN-2016-042 (1), SYN-2016-225
  (1). All PC2 storage homes, all summer. The estimate spreads the annualised advance on PC2's total shape; the
  row and the window route annualise each register on its own share. Reproduced from the book's register reads:
  64 kWh a day against 36 for PROS-2017-0336 in August 2018.
- **Recorded as a named, dated exception** in `docs/design/DOMAIN_INVARIANT_EXCEPTIONS.yaml` (max 18, retired by the
  per-register annualisation), with why it moves no figure: the estimate is trued up at the next read, 0.06% of
  graded bills, about 60 GBP on the worst bill. The gate on the book's own grade now returns permit.
- **Not done here**: the per-register annualisation fix itself (company/billing/monthly_bill_assembly.py, the
  `split_on_register_shape(advance[0], ...)` branch) and the next run. Handed on.
- **When the site becomes current**: the next publisher cycle that reads this exception off origin. If the live
  `site/data` generated stamp has not moved to 2 Nov by the end of that cycle, the publisher's log line is the next
  thing to read.
