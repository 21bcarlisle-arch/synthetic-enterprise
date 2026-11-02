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
